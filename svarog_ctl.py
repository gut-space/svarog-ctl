"""
This is the main runner script for svarog_ctl.
"""

import time

import argparse
import sys
import logging
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from dateutil import tz
from orbit_predictor.predictors.base import CartesianPredictor
from orbit_predictor.locations import Location
from orbit_predictor.sources import get_predictor_from_tle_lines
from svarog_ctl import orbitdb, utils, passes, rotctld

def get_pass(pred: CartesianPredictor, loc: Location, aos: datetime, los: datetime):
    """Returns position list for specified satellite (identified by predictor) for
       specified location, between AOS (start time) and LOS (end time).
       For the time being we're using time ticks algorithm with 30 seconds interval
       and no smoothing."""

    return passes.get_pass(pred, loc, aos, los, passes.PassAlgo.TIME_TICKS, 5)

def get_fake_pass(steps: int, start_az: int, end_az: int):
    """Returns fake positions list. Useful for testing. The timing is always now..now+2 minutes.

       Parameters
       ==========
       steps - how many steps
       start_az - starting azimuth
       end_az - ending azimuth"""
    pos = []
    delta = (end_az - start_az) / (steps-1)
    for x in range(steps):
        pos.append([datetime.now() + timedelta(seconds=x), start_az + delta*x, 5.0])

    pos.append([datetime.now() + timedelta(seconds=120), 0, 0])

    return pos

def log_details(loc: Location, args: argparse.Namespace, when: datetime, pass_,
               timezone: tz.tz):
    """Print the details of parameters used. Mostly for developer's convenience."""
    logging.info("Observer location: %s", utils.coords(loc.latitude_deg, loc.longitude_deg))
    logging.info("After time: %s", when)
    logging.info("AOS: %s", str(pass_.aos.astimezone(timezone)))
    logging.info("Max elevation: %.1f deg at %s", pass_.max_elevation_deg,
        str(pass_.max_elevation_date.astimezone(timezone)))
    logging.info("LOS: %s", str(pass_.los.astimezone(timezone)))
    logging.info("Duration: %s", str(timedelta(seconds=pass_.duration_s)))

    logging.debug(args)

def print_pos(positions: list):
    """Prints the positions list. Useful for debugging."""
    print(f"---positions has {len(positions)} entries")
    for x in positions:
        print(f"{x[0]}: az={x[1]:3.1f},el={x[2]:03.1f}")

def rewind_positions(positions: list) -> list:
    """This function rewinds (shifts positions) in time in a way that the pass will start now.
       This is useful for testing, because usually the sat pass is in the future and we want to run
       the experiments or tests now. Looking at it from a different perspective, this is a good
       way to test future pass in advance (or replay old pass).

       Parameters
       ==========
       positions - list of positions (tuples of 3 elements: timestamp, azimuth, elevation)
       returns - modified list of positions (tuples of 3 elements: timestamp, azimuth, elevation)"""

    delta = positions[0][0] - datetime.now()
    return list(map(lambda x: [x[0]-delta,x[1],x[2]], positions))

def track_positions(positions: list, rotctld: rotctld.Rotctld, delta: int):
    """This function sends commands to the rotator and tracks its position.

       Parameters
       ==========
       positions - list of positions (tuples of 3 elements: timestamp, azimuth, elevation)
       rotctld - an instance of open connection to the rotator
       delta - step time in seconds (the loop will get the rotator position every delta seconds)

       returns a list of actual rotator positions over time (list of tuple with 3 elements: timestamp, azimuth, elevation)
    """

    actual = [] # actual rotator positions

    timeout = positions[-1][0] # The last entry specifies last position and also when to stop movement

    # get the first command
    index = 0
    pos = positions[index]

    while datetime.now() < timeout:
        actual_az, actual_el = rotctld.get_pos()
        actual.append([datetime.now(), actual_az, actual_el])
        logging.debug(f"{datetime.now()}: az={actual_az}, el={actual_el}, the next command @ {pos[0]} (in {pos[0]-datetime.now()})")

        if pos[0] <= datetime.now():

            # normalize azimuth to -180;180, as this is what most rotctl rotators require.
            if pos[1]>180.0:
                pos[1] = pos[1] - 360.0

            # Ok, it's time to execute the next command
            logging.info(f"{datetime.now()}: sending command to move to az={pos[1]:.1f}, el={pos[2]:.1f}")

            status, resp = rotctld.set_pos(pos[1], pos[2])
            if not status:
                logging.warning(f"set_pos command failed. response={resp}")
            index = index + 1
            # If we gotten to the end of the list of commands, we're done here.
            if index>len(positions):
                return actual
            pos = positions[index]

        time.sleep(delta)

    return actual

def plot_charts(intended: list, actual: list):
    """To be implemented: generate charts based on two series of data:
       1. the intended antenna position over time (commands we're sending),
       2. the actual antenna position (as checked using get_pos command)."""
    pass

def main():
    """Example usage: get predictor for NOAA-18, define (hardcoded) observer,
       call get_pass (which will return a list of az,el positions over time),
       then print it."""

    parser = argparse.ArgumentParser(description="svarog-ctl: tracks satellite pass with rotator")
    parser.add_argument('--tle1', type=str, help="First line of the orbital data in TLE format")
    parser.add_argument('--tle2', type=str, help="Second line of the orbital data in TLE format")
    parser.add_argument('--sat', type=str,
        help="Name of the satellite (if local catalog is available)")
    parser.add_argument('--satid', type=int,
        help="Norad ID of the satellite (if local catalog is available)")

    parser.add_argument("--lat", type=float, required=True,
        help="Specify the latitude of the observer in degrees, positive is northern hemisphere"
             " (e.g. 53.3 represents 53.3N for Gdansk)")
    parser.add_argument("--lon", type=float, required=True,
        help="Specify the longitude of the observer in degrees, positive is easter hemisphere "
             "(e.g. 18.5 represents 18.5E for Gdansk)")
    parser.add_argument("--alt", default=0, type=int, required=False,
        help="Observer's altitude, in meters above sea level")

    parser.add_argument("--time", default=str(datetime.utcnow()), type=str,
        help="Specify the timestamp before the pass in UTC.")

    parser.add_argument("--host", default="127.0.0.1", type=str,
        help="Specify how to connect (which hostname to use) to a running rotctld.")
    parser.add_argument("--port", default=4533, type=int,
        help="Specify which port to connect to")

    parser.add_argument("--now", default=False, type=bool,
        help="Don't wait for the actual pass, start now (useful for testing only)")

    args = parser.parse_args()

    # Sanity checks
    if (args.tle1 and not args.tle2) or (not args.tle1 and args.tle2):
        print("ERROR: You must either specify both TLE lines or none.")
        sys.exit(1)

    if (not args.tle1 and not args.sat and not args.satid):
        print("ERROR: You need to identify the satellite somehow. 3 options are supported:")
        print("ERROR: - provide TLE parameters on your own (use --tle1 and --tle2 options)")
        print("ERROR: - specify the satellite name, e.g. --sat 'NOAA 18'")
        print("ERROR: - specify the NORAD ID of the satellite, e.g. --satid 28654")
        sys.exit(1)


    # First step is to get the orbit predictor. There are two options here.
    name = None
    if args.tle1:
        # If TLE is specified explicitly, we don't need to load any databases, just use
        # the TLE as is.
        name = "CUSTOM"
        tle_lines = (args.tle1, args.tle2)
        pred = get_predictor_from_tle_lines(tle_lines)
    else:
        # If sat was referenced by name or Norad ID, we need to load the database and
        # see if we can find the sat.
        db = orbitdb.OrbitDatabase()
        db.refresh_urls()

        if args.satid is not None:
            tle = db.get_norad(args.satid)
            name = tle.get_name()
        elif args.sat is not None:
            name = args.sat
        logging.debug(f"Looking for satellite {name}")
        pred = db.get_predictor(name)

    when = dateparser.parse(args.time)

    loc = Location('Observer', args.lat, args.lon, args.alt)

    pass_ = pred.get_next_pass(loc, when_utc=when)

    local_tz = True
    target_tz = tz.tzutc() if not local_tz else tz.tzlocal()

    log_details(loc, args, when, pass_, target_tz)

    positions = get_pass(pred, loc, pass_.aos, pass_.los)

    # Uncomment this for azimuth debugging
    # positions = get_fake_pass(10, 30, -30) # generate from 3 to 200 degrees, in 10 steps
    # print_pos(positions)

    # If specified, rewind in time so the positions start immediately.
    if (args.now):
        positions = rewind_positions(positions)

    print_pos(positions)

    logging.info(f"Connecting to {args.host}, port {args.port}")

    rotctld = rotctld.Rotctld(args.host, args.port, 1)
    rotctld.connect()

    antenna_pos = track_positions(positions, rotctld, 3)

    plot_charts(positions, antenna_pos)

    rotctld.close()

if __name__ == "__main__":
    main()
