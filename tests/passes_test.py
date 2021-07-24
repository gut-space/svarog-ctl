from svarog_ctl import orbitdb, passes, tle
from orbit_predictor.locations import Location
from orbit_predictor.sources import get_predictor_from_tle_lines
from datetime import datetime, timedelta
from dateutil import parser
import unittest

NAME='KRAKSAT'
NORAD=44427
LINE1='1 44427U 98067QM  21192.54020985  .00022355  00000-0  19763-3 0  9995'
LINE2='2 44427  51.6376 177.8799 0003618 359.5888  93.1405 15.68562202115256'

OBSERVER_NAME = 'Gdansk'
OBSERVER_LAT = 53.35 # deg
OBSERVER_LON = 18.53 # deg
OBSERVER_ALT = 120 # masl

# A nice timestamp that will produce reasonably high pass.
DATE = datetime(2021, 7, 14, 18, 44, 0)

class PassesTest(unittest.TestCase):

    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)

    def setUp(self):
        self._tle = tle.Tle(LINE1, LINE2, NAME)

        self._db = orbitdb.OrbitDatabase()
        self._db.add_tle(LINE1, LINE2, NAME)

        self._pred = get_predictor_from_tle_lines((LINE1, LINE2))

        self._loc = Location(OBSERVER_NAME, OBSERVER_LAT, OBSERVER_LON, OBSERVER_ALT)

    def tearDown(self):
        pass

    def test_passes_max_ticks(self):

        next_pass = self._pred.get_next_pass(self._loc, when_utc=DATE)

        aos = next_pass.aos
        los = next_pass.los

        # We want to get pass details between AOS and LOS, we want to use the time ticks
        # algorithm (position every 30 seconds), we don't want any smoothing
        x = passes.get_pass(self._pred, self._loc, aos, los, passes.PassAlgo.TIME_TICKS, 30)

        # These are expected locations for TIME TICKS, 30 seconds, no smoothing
        exp = [
            [ '2021-07-14 18:48:46.673549', 246.9, 2.0 ],
            [ '2021-07-14 18:49:16.673549', 245.8, 4.2 ],
            [ '2021-07-14 18:49:46.673549', 244.5, 6.7 ],
            [ '2021-07-14 18:50:16.673549', 242.6, 9.7 ],
            [ '2021-07-14 18:50:46.673549', 240.1, 13.4 ],
            [ '2021-07-14 18:51:16.673549', 236.4, 18.1 ],
            [ '2021-07-14 18:51:46.673549', 230.4, 24.5 ],
            [ '2021-07-14 18:52:16.673549', 220.0, 33.1 ],
            [ '2021-07-14 18:52:46.673549', 199.5, 43.5 ],
            [ '2021-07-14 18:53:16.673549', 163.5, 48.7 ],
            [ '2021-07-14 18:53:46.673549', 129.4, 42.0 ],
            [ '2021-07-14 18:54:16.673549', 111.0, 31.7 ],
            [ '2021-07-14 18:54:46.673549', 101.5, 23.5 ],
            [ '2021-07-14 18:55:16.673549', 96.0, 17.4 ],
            [ '2021-07-14 18:55:46.673549', 92.5, 12.9 ],
            [ '2021-07-14 18:56:16.673549', 90.1, 9.3 ],
            [ '2021-07-14 18:56:46.673549', 88.3, 6.4 ],
            [ '2021-07-14 18:57:16.673549', 87.0, 3.9 ],
            [ '2021-07-14 18:57:46.673549', 86.0, 1.8 ],
            [ '2021-07-14 18:58:13.892806', 85.3, 0.0 ]
        ]

        prev = None
        for pos in x:

            current = pos[0]

            # First step is to verify the time interval is indeed 30 seconds.
            if prev is not None:
                delta = current - prev
                if pos != x[-1]:
                    # all samples except the last one must be exactly 30 seconds apart
                    assert delta.seconds == 30
                else:
                    # it's ok if the last one (at LOS) is shorter.
                    assert delta.seconds <= 30
            prev = pos[0]

            # Second step is to verify that the timestamps looks reasonable,
            # the azimuth is between 0 and 360 and elevation is between 0 and 90.
            self.assertGreaterEqual(current, aos)
            self.assertLessEqual(current, los)
            self.assertLess(pos[1], 360)
            self.assertGreaterEqual(pos[1], 0)
            self.assertLessEqual(pos[2], 90)
            self.assertGreaterEqual(pos[2], 0)

        # Third step is to verify against the precalculated values.
        # The value of this step is not too high, as the same code was used
        # to generate that reference data. However, it's still useful to
        # detect regressions.
        self.assertEqual(len(exp), len(x))

        # Check that each sample matches expectation
        for i in range(len(exp)):
            exp_data = exp[i]
            data = x[i]

            # For some reason on some systems the data varies a bit. As such we're using
            # epsilons of 10 seconds and 0.5 degrees
            self.assertAlmostEqual(parser.parse(exp_data[0]), data[0], delta=timedelta(seconds=5))
            self.assertAlmostEqual(exp_data[1], data[1], delta = 0.5)     # azimuth
            self.assertAlmostEqual(exp_data[2], data[2], delta = 0.5)     # elevation


    def test_distance(self):

        exp = [
            # az1, el1, az2, el2, expected distance
            [10, 0, 20, 0, 10],
            [0, 10, 0, 20, 10],
            [350, 0, 10, 0, 20],
            [ 0, 0, 10, 10, 14.10604]
        ]

        for e in exp:
            dist = passes.distance(e[0], e[1], e[2], e[3])
            self.assertAlmostEqual(dist, e[4], delta = 0.00001)
