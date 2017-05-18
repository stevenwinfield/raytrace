"""
camera.

Defines the Camera classes.

Cameras are positioned and oriented, then are responsible for yielding
rays which should be traced.
"""


from abc import ABCMeta, abstractmethod
from ray import Ray

class Camera(metaclass=ABCMeta):
    """Camera abstract base class."""

    @abstractmethod
    def rays(self, image_width, image_height):
        """Yield (x, y, ray) tuples."""

class Orthographic(Camera):
    """A Camera with orthographic projection"""
    def __init__(self, position, up, forward, width, height):
        self.position = position
        self.up = up.normalized()
        self.forward = forward.normalized()
        self.width = width
        self.height = height
        self.right = forward.cross(up)

    def rays(self, image_width, image_height):

        pixel_width = self.width / image_width
        pixel_height = self.height / image_height
        bottom_left = (self.position
                       - self.right * self.width / 2.0
                       - self.up * self.height / 2.0
                       + self.right * pixel_width / 2.0
                       + self.up * pixel_height / 2.0)
        for x in range(image_width):
            for y in range(image_height):
                yield (x, y, Ray(bottom_left
                                 + x * pixel_width * self.right
                                 + y * pixel_height * self.up,
                                 self.forward))
