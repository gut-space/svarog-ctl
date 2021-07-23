"""
Class representing TLE
"""

class Tle():
    """
    TLE class represents a TLE, Two Line Element that describes an Earth orbit.
    See https://en.wikipedia.org/wiki/Two-line_element_set
    """
    def __init__(self, line1: str, line2: str, line0: str = ""):
        self.set_line1(line1)
        self.set_line2(line2)
        self.name = line0

        self.parse(line1, line2)

    def parse(self, line1: str, line2: str):
        """Parses the TLE lines"""
        x1 = line1.split() # not used yet
        x2 = line2.split()
        self.id = int(x2[1])

        if x1[0] != '1':
            raise ValueError("First line of TLE (%s) malformed. Expected to start with '1'" % line1)
        if x2[0] != '2':
            raise ValueError("Second line of TLE (%s) malformed. Expected to start with '2'" % line1)

        # many more fields to parse here

    def get_id(self) -> int:
        """Returns NORAD ID of the satellite"""
        return self.id

    def get_name(self) -> str:
        """Returns a satellite name"""
        return self.name

    def set_line1(self, line: str) -> str:
        """Sets the first line out of two"""
        # @todo: Add sanity checks for line 1
        tokens = line.split()
        if len(tokens) != 9:
            raise ValueError("First line of TLE (%s) malformed. Expected 9 values" % line)
        if tokens[0] != '1':
            raise ValueError("First line of TLE (%s) malformed. Expected '1'" % line)

        self.norad = int(''.join(ch for ch in tokens[1] if ch.isdigit()))

        self.line1 = line

    def set_line2(self, line: str) -> str:
        """Sets the second line out of two"""
        # @todo: Add sanity checks for line 2
        self.line2 = line

    def __str__(self) -> str:
        if self.name:
            return self.name + '\n' + self.line1 + '\n' + self.line2
        return self.line1 + '\n' + self.line2

    def __repr__(self) -> str:
        return self.__str__()
