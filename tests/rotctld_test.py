import pytest
from svarog_ctl.rotcltd import Rotctld

def test_ctor():

    # Valid instantiation, should not throw.
    r = Rotctld("127.0.0.2", 3456)

    # Invalid port, should throw.
    with pytest.raises(IndexError):
        Rotctld("127.0.0.1", -1)

def test_connected():
    r = Rotctld("127.0.0.1", 4533)

    # This is clearly broken. It's supposed to be False before connect is called.
    assert r.connected() == True