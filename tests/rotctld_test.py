import pytest
from svarog_ctl.rotcltd import Rotctld
import unittest

class PassesTest(unittest.TestCase):

    def setUp(self):
        # TODO: need to start rotctld in the background with Dummy rotator
        pass

    def tearDown(self):
        # TODO: kill the rotctld running in the background.
        pass

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
