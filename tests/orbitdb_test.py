from svarog_ctl import orbitdb
from svarog_ctl import tle
import pytest

def test_db_stats():

    db = orbitdb.OrbitDatabase()

    # Nothing is loaded by default
    assert db.count() == 0

    # There's close to 2600 sats listed for now, but the number may fluctuate over
    # time. Let's make the test robust.
    db.refresh_urls()
    assert db.count() > 2500

def test_load_db():

    db = orbitdb.OrbitDatabase()
    db.refresh_urls()

    tle1 = db.get_name("NOAA 18")
    tle2 = db.get_norad(28654)

    assert tle1 is not None
    assert isinstance(tle1, tle.Tle)
    assert tle1.name == "NOAA 18"
    assert tle1.norad == 28654

    assert tle2 is not None
    assert isinstance(tle2, tle.Tle)
    assert tle2.name == "NOAA 18"
    assert tle2.norad == 28654

    with pytest.raises(KeyError):
        db.get_name("nonexistent")

    with pytest.raises(KeyError):
        db.get_norad(1234567)

    pred = db.get_predictor("NOAA 18")
    assert pred

    assert db.get_name_by_norad(28654) == "NOAA 18"

def test_add_custom():

    LINE1 = "1 44427U 98067QM  21192.54020985  .00022355  00000-0  19763-3 0  9995"
    LINE2 = "2 44427  51.6376 177.8799 0003618 359.5888  93.1405 15.68562202115256"
    NAME = "KRAKSAT"

    db = orbitdb.OrbitDatabase()

    # Make sure there's no entry for KRAKSAT
    with pytest.raises(KeyError):
        db.get_name("KRAKSAT")
    with pytest.raises(KeyError):
        db.get_norad(44427)
    with pytest.raises(KeyError):
        db.get_name_by_norad(44427)

    # Now add a custom TLE
    db.add_tle(LINE1, LINE2, NAME)

    tle1 = db.get_name(NAME)
    tle2 = db.get_norad(44427)

    assert tle1 is not None
    assert tle2 is not None
    assert isinstance(tle1, tle.Tle)
    assert isinstance(tle2, tle.Tle)

    assert db.get_name_by_norad(44427) == "KRAKSAT"
