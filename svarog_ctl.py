"""
This is the main runner script for svarog_ctl.
"""

import sys
sys.path.append('.')

from svarog_ctl.orbitdb import *
from orbit_predictor.locations import Location
from dateutil import tz
import datetime as dt

db = OrbitDatabase()
pred = db.get_predictor('NOAA 18')

OBSERVER_NAME = 'Gdansk'
OBSERVER_LAT = 53.35 # deg
OBSERVER_LON = 18.53 # deg
OBSERVER_ALT = 120 # masl

# test data
when = dt.datetime.utcnow()
when = dt.datetime(2021, 6, 20, 15, 8, 25, 0)

loc = Location(OBSERVER_NAME, OBSERVER_LAT, OBSERVER_LON, OBSERVER_ALT)
pass_ = pred.get_next_pass(loc, when_utc=when)

local_tz = True

target_tz = tz.tzutc() if not local_tz else tz.tzlocal()

print("AOS:", str(pass_.aos.astimezone(target_tz)))
print("LOS:", str(pass_.los.astimezone(target_tz)))
print("Duration:", str(datetime.timedelta(seconds=pass_.duration_s)))
print("Max elevation:", "%.2f" % (pass_.max_elevation_deg,), "deg",
      str(pass_.max_elevation_date.astimezone(target_tz)))
print("Off nadir", "%.2f" % (pass_.off_nadir_deg,), "deg")

t = pass_.aos

date_series: List[datetime.datetime] = []
az_series: List[float] = []
el_series: List[float] = []

def get_pass(pred: CartesianPredictor, loc: Location, aos: datetime, los: datetime):

    pos_list = []

    t = aos
    while t < pass_.los:
        t += datetime.timedelta(seconds=30)
        pos = pred.get_position(t)
        az, el = loc.get_azimuth_elev_deg(pos)

        pos_list.append([t, az, el])

    return pos_list

positions = get_pass(pred, loc, pass_.aos, pass_.los)

for x in positions:
    print("Date %s, az=%3d deg el=%2d" % (x[0], x[1], x[2]))
