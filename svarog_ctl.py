"""
This is the main runner script for svarog_ctl.
"""

from datetime import datetime, timedelta
from dateutil import parser as dateparser
import logging
from dateutil import tz
from orbit_predictor.predictors.base import CartesianPredictor
from orbit_predictor.locations import Location
from orbit_predictor.sources import get_predictor_from_tle_lines
from svarog_ctl import orbitdb, utils, passes
import argparse
import sys

def get_pass(pred: CartesianPredictor, loc: Location, aos: datetime, los: datetime):
    """Returns position list for specified satellite (identified by predictor) for
       specified location, between AOS (start time) and LOS (end time).
       For the time being we're using time ticks algorithm with 30 seconds interval
       and no smoothing."""

    return passes.get_pass(pred, loc, aos, los, passes.PassAlgo.TIME_TICKS, 30, False)

def logDetails(loc: Location, args: argparse.Namespace, when: datetime):
    logging.info("Observer location: %s" % utils.coords(loc.latitude_deg, loc.longitude_deg))
    logging.info("After time: %s", when)
    logging.debug(args)

def main():
    """Example usage: get predictor for NOAA-18, define (hardcoded) observer,
       call get_pass (which will return a list of az,el positions over time),
       then print it."""

    parser = argparse.ArgumentParser(description="svarog-ctl: tracks satellite pass with rotator")
    parser.add_argument('--tle1', type=str, help="First line of the orbital data in TLE format")
    parser.add_argument('--tle2', type=str, help="Second line of the orbital data in TLE format")
    parser.add_argument('--sat', type=str, help="Name of the satellite (if local catalog is available)")
    parser.add_argument('--satid', type=int, help="Norad ID of the satellite (if local catalog is available)")

    parser.add_argument("--lat", type=float, help="Specify the latitude of the observer in degrees, positive is northern hemisphere (e.g. 53.3 represents 53.3N for Gdansk)")
    parser.add_argument("--lon", type=float, help="Specify the longitude of the observer in degrees, positive is easter hemisphere (e.g. 18.5 represents 18.5E for Gdansk)")
    parser.add_argument("--alt", default=0, type=int, required=False, help="Observer's altitude, in meters above sea level")

    parser.add_argument("--time", default=str(datetime.utcnow()), type=str, help="Specify the timestamp before the pass in UTC.")

    args = parser.parse_args()

    # Sanity checks
    if args.lon is None or args.lat is None:
        print("ERROR: You need to specify both the latitude (--lat) and longitude (--lon) of the observer")
        sys.exit(1)

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
    if (args.tle1):
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
        print("Looking for name: ", name)
        pred = db.get_predictor(name)

    when = dateparser.parse(args.time)

    loc = Location('Observer', args.lat, args.lon, args.alt)

    logDetails(loc, args, when)

    pass_ = pred.get_next_pass(loc, when_utc=when)

    local_tz = True

    target_tz = tz.tzutc() if not local_tz else tz.tzlocal()

    logging.info("AOS: %s", str(pass_.aos.astimezone(target_tz)))
    logging.info("Max elevation: %.2f deg at %s" % (pass_.max_elevation_deg,
        str(pass_.max_elevation_date.astimezone(target_tz))))
    logging.info("LOS: %s", str(pass_.los.astimezone(target_tz)))
    logging.info("Duration: %s", str(timedelta(seconds=pass_.duration_s)))

    positions = get_pass(pred, loc, pass_.aos, pass_.los)

    for x in positions:
        print("Date %s, az=%3.1f deg el=%3.1f" % (x[0], x[1], x[2]))

if __name__ == "__main__":
    main()
