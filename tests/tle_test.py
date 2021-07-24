from svarog_ctl.tle import Tle
import pytest
import unittest

NAME='NOAA 15'
LINE1='1 25338U 98030A   19351.71640046 +.00000015 +00000-0 +24973-4 0  9993'
LINE2='2 25338 098.7340 012.5392 0011411 075.8229 284.4218 14.25943731122932'

class TleTest(unittest.TestCase):

    def test_tle_bad_init(self):

        with pytest.raises(TypeError):
            # without any strings
            Tle()

        with pytest.raises(TypeError):
            # with just one line
            Tle(LINE1)

        with pytest.raises(TypeError):
            Tle(LINE1, LINE2, NAME, "unsubstantiated nonsense")

    def test_tle2lines(self):

        x = Tle(LINE1, LINE2)
        self.assertEqual(x.name, "")
        self.assertEqual(x.line1, LINE1)
        self.assertEqual(x.line2, LINE2)

    def test_tle3lines(self):

        x = Tle(LINE1, LINE2, NAME)
        self.assertEqual(x.name, NAME)
        self.assertEqual(x.line1, LINE1)
        self.assertEqual(x.line2, LINE2)

    def test_tle_parse(self):
        x = Tle(LINE1, LINE2, NAME)
        self.assertEqual(x.norad, 25338)

    def test_tle_repr(self):
        """Make sure there's an easy way to print the Tle"""
        x = Tle(LINE1, LINE2, NAME)

        exp = NAME + '\n' + LINE1 + '\n' + LINE2
        self.assertEqual(x.__str__(), exp)
        self.assertEqual(repr(x), exp)

    def test_tle_parsing(self):
        x = Tle(LINE1, LINE2, NAME)

        self.assertEqual(x.get_id(), 25338)
        self.assertEqual(x.get_name(), "NOAA 15")
