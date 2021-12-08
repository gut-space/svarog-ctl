import pytest
import subprocess
from svarog_ctl.rotcltd import Rotctld
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

        self.rotctld_proc.send_signal(15) #sigterm
        out, err = self.rotctld_proc.communicate(timeout=3) # try to kill it and wait 3 seconds.

    def test_ctor(self):

        # Valid instantiation, should not throw.
        r = Rotctld("127.0.0.2", 3456)

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
        self.assertEqual(m, "Dummy rotator") # make sure the rotctld reports the rotator type as dummy.
                                             # That's because we started it with -m 1 (1 is a dummy rotator)

        print(f"returned model: [{m}]")
