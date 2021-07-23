from svarog_ctl import utils

import unittest


class UtilsTest(unittest.TestCase):


    def test_url_to_filename(self):
        # Tests if URL can be properly converted to a filename
        values = [ ['https://celestrak.com/NORAD/elements/active.txt', 'celestrak.com-NORAD-elements-active.txt'],
                ['ftp://isc.org/foo.txt', 'isc.org-foo.txt'] ]

        for _, row in enumerate(values):
            assert utils.url_to_filename(row[0]) == row[1]

    def test_coords(self):
        test_data = [ [ 54.0, 19.0, None, "54.0000N 19.0000E"],
                    [-54.0, 19.0, None, "54.0000S 19.0000E"],
                    [-54.0,-19.0, None, "54.0000S 19.0000W"],
                    [ 54.0, 19.0, 123,  "54.0000N 19.0000E 123m"] ]

        for case in test_data:
            assert utils.coords(case[0], case[1], case[2]) == case[3]
