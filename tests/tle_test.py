from svarog_ctl.tle import Tle
import pytest

NAME='NOAA-15'
LINE1='1 25338U 98030A   19351.71640046 +.00000015 +00000-0 +24973-4 0  9993'
LINE2='2 25338 098.7340 012.5392 0011411 075.8229 284.4218 14.25943731122932'

def test_tle_bad_init():

    with pytest.raises(TypeError):
        # without any strings
        Tle()

    with pytest.raises(TypeError):
        # with just one line
        Tle(LINE1)

    with pytest.raises(TypeError):
        Tle(NAME,
            LINE1,
            LINE2,
            "unsubstantiated nonsense")

def test_tle2lines():

    x = Tle(LINE1, LINE2)
    assert x.name == ""
    assert x.line1 == LINE1
    assert x.line2 == LINE2

def test_tle3lines():

    x = Tle(LINE1, LINE2, NAME)
    assert x.name == NAME
    assert x.line1 == LINE1
    assert x.line2 == LINE2

def test_tle_parse():
    x = Tle(LINE1, LINE2, NAME)
    assert x.norad == 25338

def test_tle_repr():
    """Make sure there's an easy way to print the Tle"""
    x = Tle(LINE1, LINE2, NAME)

    exp = NAME + '\n' + LINE1 + '\n' + LINE2
    assert x.__str__() == exp
    assert repr(x) == exp
