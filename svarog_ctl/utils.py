"""
A collection of random utility functions.
"""

def coords(lat: float, lon: float, alt: float = None ) -> str:
    """Turn longitude, latitude into a printable string."""
    txt = f"{abs(lat):2.4f}{'N' if lat>0 else 'S'} "
    txt += f"{abs(lon):2.4f}{'E' if lon>0 else 'W'}"
    if alt:
        txt += f" {alt:2.0f}m"
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
    # First we need to get rid of the protocol part
    safe = url[url.find("//")+2:]
    safe = safe_filename(safe, "-")

    return safe.lower()
