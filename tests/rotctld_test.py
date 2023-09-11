import pytest
import subprocess
from svarog_ctl.rotctld import Rotctld
import unittest
import time


class RotctldTest(unittest.TestCase):

    rotctld_proc = None

    def setUp(self):
        # Start the rotctld with dummy rotor type 1 (-m 1) and run in verbose (-v) mode
        CMD = 'rotctld -m 1 -t 45033 -v'
        self.rotctld_proc = subprocess.Popen(CMD.split(' '))
        time.sleep(1)

    def tearDown(self):

        self.rotctld_proc.send_signal(15)  # sigterm
        out, err = self.rotctld_proc.communicate(timeout=3)  # try to kill it and wait 3 seconds.

    def test_ctor(self):

        # Valid instantiation, should not throw.
        Rotctld("127.0.0.2", 3456)

        # Invalid port, should throw.
        with pytest.raises(IndexError):
            Rotctld("127.0.0.1", -1)

    def test_connected(self):
        r = Rotctld("127.0.0.1", 4533)

        # This is clearly broken. It's supposed to be False before connect is called.
        self.assertFalse(r.connected())

    def test_connect(self):
        r = Rotctld("127.0.0.1", 45033)
        m = r.connect()
        self.assertEqual(m, "Dummy rotator")  # make sure the rotctld reports the rotator type as dummy.
        # That's because we started it with -m 1 (1 is a dummy rotator)

        print(f"returned model: [{m}]")

    def test_norm_azimuth(self):
        """Tests if azimuth is normalized to -180..180 range."""
        r = Rotctld("127.0.0.1", 45033)

        for x in range(-200, 200, 10):
            norm = r.norm_az(x)
            self.assertTrue(norm >= -180.0 and norm <= 180)

    def test_norm_elevation(self):
        """Tests if elevation is normalized to 0..90 range."""
        r = Rotctld("127.0.0.1", 45033)

        for x in range(-200, 200, 10):
            norm = r.norm_el(x)
            self.assertTrue(norm >= 0 and norm <= 90)

    def test_capabilities(self):
        """Check if capabilities are returned. This test is only so-so, as the capabilities returned are
           as plain text. There's no easy way to interpret this, so we chose a random properties returned,
           check that they're in the returned text. There's a lot more returned there."""
        r = Rotctld("127.0.0.1", 45033)
        r.connect()
        caps = r.capabilities()
        r.close()

        self.assertTrue(len(caps))

        # strings we expect to see in the the response.
        exp = ["Caps dump for model:	1",
               "Model name:		Dummy",
               "Rot type:		Az-El"]

        for e in exp:
            self.assertTrue(caps.find(e) != -1)
