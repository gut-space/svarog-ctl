"""
A collection of random utility functions.
"""

def coords(lon: float, lat: float):
    """Turn longitude, latitude into a printable string."""
    txt = "%2.4f%s" % (lat, "N" if lat else "S")

    txt += " %2.4f" % lon
    if lon > 0:
        txt += "E"
    else:
        txt += "W"
    return txt

def is_safe_filename_character(char: str) -> bool:
    """checks if a char is safe to use in a filename"""
    return char.isalpha() or char.isdigit() or char in ('.', '-', '_')

def safe_filename(filename: str, replacement: str="_") -> str:
    """Turns a string into a name that can be safely used as a filename."""
    chars = [c if is_safe_filename_character(c) else replacement for c in filename]
    return "".join(chars).rstrip()

def url_to_filename(url: str) -> str:
    """Returns a filename based on URL"""
    # First we need to get rid of the
    safe = url[url.find("//")+2:]
    safe = safe_filename(safe, "-")

    return safe
