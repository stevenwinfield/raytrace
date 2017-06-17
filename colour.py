"""
colour.

Defines the colour class and some named colours.
"""


class Colour:
    """A Colour, stored as RGB values >= 0.0."""

    def __init__(self, red=0.0, green=0.0, blue=0.0):
        """Initialise a Colour."""
        self.red = red
        self.green = green
        self.blue = blue

    def _get_red(self):
        return self._red

    def _set_red(self, value):
        self._red = max(0.0, value)

    red = property(_get_red, _set_red)

    def _get_green(self):
        return self._green

    def _set_green(self, value):
        self._green = max(0.0, value)

    green = property(_get_green, _set_green)

    def _get_blue(self):
        return self._blue

    def _set_blue(self, value):
        self._blue = max(0.0, value)

    blue = property(_get_blue, _set_blue)

    def __add__(self, other):
        """Add colours."""
        return Colour(self.red + other.red,
                      self.green + other.green,
                      self.blue + other.blue)

    def __iadd__(self, other):
        """Add a colour in-place."""
        self.red += other.red
        self.green += other.green
        self.blue += other.blue
        return self

    def __mul__(self, other):
        """Multiply a colour by a number or colour."""
        if isinstance(other, Colour):
            return Colour(self.red * other.red,
                          self.green * other.green,
                          self.blue * other.blue)
        else:
            return Colour(self.red * other,
                          self.green * other,
                          self.blue * other)

    def __rmul__(self, other):
        """Multiply a number by a colour."""
        return self * other

    def __imul__(self, other):
        """In-place multiply a colour by a number or colour."""
        if isinstance(other, Colour):
            self.red *= other.red
            self.green *= other.green
            self.blue *= other.blue
        else:
            self.red *= other
            self.green *= other
            self.blue *= other
        return self

    def clamp(self, min_value=0.0, max_value=0.0):
        """Modify self to contain values clamped to [min_value, max_value]."""
        self.red = max(min(self.red, max_value), min_value)
        self.green = max(min(self.green, max_value), min_value)
        self.blue = max(min(self.blue, max_value), min_value)

    def clone(self, red=None, green=None, blue=None):
        """Return a clone of self, with the given modifications."""
        return Colour(red or self.red, green or self.green, blue or self.blue)

    def clamped(self, min_value=0.0, max_value=1.0):
        """Return a clone of self after clamping."""
        clone = self.clone()
        clone.clamp(min_value, max_value)
        return clone

    def rgb(self, multiplier=255):
        """Return this colour's RGB value.

        i.e. 0xRRGGBB
        """
        r = max(min(int(self.red * multiplier), 255), 0)
        g = max(min(int(self.green * multiplier), 255), 0)
        b = max(min(int(self.blue * multiplier), 255), 0)
        return (r << 16) + (g << 8) + b


RED = Colour(red=1.0)
GREEN = Colour(green=1.0)
BLUE = Colour(blue=1.0)
YELLOW = Colour(red=1.0, green=1.0)
CYAN = Colour(green=1.0, blue=1.0)
MAGENTA = Colour(red=1.0, blue=1.0)
WHITE = Colour(red=1.0, green=1.0, blue=1.0)
BLACK = Colour()
