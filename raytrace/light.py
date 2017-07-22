"""
light.

Defines the light classes
"""

from abc import ABCMeta, abstractmethod

class Light(metaclass=ABCMeta):
    """Light base class.

    All lights inherit from this.
    """

    @abstractmethod
    def __getstate__(self):
        """Used to implement pickling."""

    @abstractmethod
    def __setstate__(self, state):
        """Used to implement pickling."""


class Point(Light):

    def __init__(self, position, colour, intensity=1.0):
        self.position = position
        self.colour = colour
        self.intensity = intensity

    def __getstate__(self):
        return (self.position, self.colour, self.intensity)

    def __setstate__(self, state):
        self.position, self.colour, self.intensity = state


class Ambient(Light):

    def __init__(self, colour):
        self.colour = colour

    def __getstate__(self):
        return (self.colour,)

    def __setstate__(self, state):
        self.colour, = state
