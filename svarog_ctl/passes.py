from datetime import datetime, timedelta
from orbit_predictor.predictors.base import CartesianPredictor
from orbit_predictor.locations import Location
from enum import Enum

class PassAlgo(Enum):
    TIME_TICKS = 1,
    DISTANCE = 2
    MAX_STEPS = 3

def get_pass(pred: CartesianPredictor, loc: Location, aos: datetime, los: datetime,
             algo: PassAlgo, delta: float, smooth: bool = False):
    """Returns position list for specified satellite (identified by predictor) for
       specified location, between AOS (start time) and LOS (end time). algo
       specifies the algorithm for picking the intermediate steps. delta is
       a parameter that is algorithm dependent. smooth parameter determines if
       the locations should be averaged. If set to False, the antenna will point
       exactly at the current sat location. Effectively, the antenna will
       always be lagging behind. When set to True, it will take the current
       and next point and will average them. As a result, the antenna will be
       roughly 50% of the time ahead of the sat and 50% lagging behind.

       TIME_TICKS - antenna is moved every delta seconds
       DISTANCE - antenna is moved if its pointing deviates from the sat position
                  by more than delta degrees (not implemented yet)
       MAX_STEPS - conducts the whole fly over with exactly delta number of steps
                   (not implemented yet)

       TIME_TICKS is the most basic algorithm and easiest to implement and understand.
       However, its flaw comes from varying radial velocity of a passing sat. When
       it's low over the horizon, the angular movement is very slow, so frequent
       rotator movements are not necessary. However, when the sat get closer to
       the zenith, its angular velocity increases greatly, so frequent rotator
       adjustments would be useful. The delta parameter is interpreted as seconds.

       DISTANCE - this algorithm attempts to address the problem described above
       by deciding to conduct the next move depending on how far the antenna and
       sat position differ. Tuning this parameter requires a knowledge of the
       antenna characteristics. If its very narrow, then you'd want to make many
       small adjustments. For wider beam antennas, fewer larger adjustments may
       be better. The delta parameter is interpreted as angular degrees.

       MAX_STEPS - this is another possible approach that splits the total pass
       into specified number of equal steps. It's somewhat similar to TIME_TICKS,
       but may possibly be a bit better in treating very long and very brief
       passes more uniformly. The delta parameter is interpreted as number of steps.
       Highly experimental."""

    pos_list = []

    if algo == PassAlgo.TIME_TICKS:
        d = timedelta(seconds = delta)
    elif algo == PassAlgo.MAX_STEPS:
        d = (los - aos) / delta
    elif algo == PassAlgo.DISTANCE:
        raise NotImplementedError

    t = aos
    while t < los:
        t += d
        if t>los: # Make sure we don't do anything stupid, like tracking below horizon
            t = los
        pos = pred.get_position(t)
        az, el = loc.get_azimuth_elev_deg(pos)

        pos_list.append([t, az, el])

    return pos_list
