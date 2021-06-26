"""
Class representing TLE
"""

class tle():
    """
    TLE class represents a TLE, Two Line Element that describes an Earth orbit.
    See https://en.wikipedia.org/wiki/Two-line_element_set
    """
    def __init__(self, line1: str, line2: str, line0: str = ""):
        self.set_line1(line1)
        self.set_line2(line2)
        self.name = line0

    def set_line1(self, line: str) -> str:
        """Sets the first line out of two"""
        # @todo: Add sanity checks for line 1
        tokens = line.split()
        if len(tokens) != 9:
            raise Exception("First line of TLE (%s) malformed. Expected 9 values" % line)
        if tokens[0] != '1':
            raise Exception("First line of TLE (%s) malformed. Expected '1'" % line)

        self.norad = int(''.join(ch for ch in tokens[1] if ch.isdigit()))

        self.line1 = line

    def set_line2(self, line: str) -> str:
        """Sets the second line out of two"""
        # @todo: Add sanity checks for line 2
        self.line2 = line

    # @todo: add __str__ printer for TLE
