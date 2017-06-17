"""
light.

Defines the light classes
"""


class Light:
    """Light base class.

    All lights inherit from this.
    """

class Point(Light):

    def __init__(self, position, colour, intensity=1.0):
        self.position = position
        self.colour = colour
        self.intensity = intensity


class Ambient(Light):

    def __init__(self, colour):
        self.colour = colour
