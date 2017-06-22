"""
camera.

Defines the Camera classes.

Cameras are positioned and oriented, then are responsible for yielding
rays which should be traced.
"""


from abc import ABCMeta, abstractmethod
from math import pi, sin, cos

from .ray import Ray


def coordinate_range(min_value, max_value, size):
    """Construct the range of values that will be iterated over."""
    return range(min_value, size if max_value is None else (max_value + 1))


class Camera(metaclass=ABCMeta):
    """Camera abstract base class."""

    @abstractmethod
    def rays(self, image_width, image_height,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield (x, y, ray) tuples.

        If (x/y)(min/max) are specified, they are inclusive bounds
        of the rays to be yielded.
        """

    def ray_count(self, image_width, image_height,
                  xmin=0, xmax=None, ymin=0, ymax=None):
        """Return the number of rays that will be yielded."""
        return (len(coordinate_range(xmin, xmax, image_width)) *
                len(coordinate_range(ymin, ymax, image_height)))


class Orthographic(Camera):
    """A Camera with orthographic projection."""

    def __init__(self, position, up, forward, width, height):
        """Initialise an Orthographic camera."""
        self.position = position
        self.forward = forward.normalized()
        # Ensure "up" is _|_ to "forward"
        self.up = (up - (up @ self.forward) * self.forward).normalized()
        self.width = width
        self.height = height
        self.right = forward.cross(up).normalized()

    def rays(self, image_width, image_height,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield the rays from an Orthographic camera.

        All rays are parallel to the forward direction.
        """
        pixel_width = self.width / image_width
        pixel_height = self.height / image_height
        bottom_left = (self.position
                       - self.right * self.width / 2.0
                       - self.up * self.height / 2.0
                       + self.right * pixel_width / 2.0
                       + self.up * pixel_height / 2.0)
        for y in coordinate_range(ymin, ymax, image_height):
            for x in coordinate_range(xmin, xmax, image_width):
                yield (x, y, Ray(bottom_left
                                 + x * pixel_width * self.right
                                 + y * pixel_height * self.up,
                                 self.forward))


class Perspective(Camera):
    """A Camera that casts its rays from an eye point."""

    def __init__(self, eye, up, forward, fov_width, fov_height, fov_distance):
        """Initialise a Perspective camera."""
        self.eye = eye
        self.up = up.normalized()
        self.forward = forward.normalized()
        self.fov_width = fov_width
        self.fov_height = fov_height
        self.fov_distance = fov_distance
        self.right = forward.cross(up).normalized()

    def rays(self, image_width, image_height,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield the rays for a Perspective camera."""
        pixel_width = self.fov_width / image_width
        pixel_height = self.fov_height / image_height
        bottom_left = (self.fov_distance * self.forward
                       - self.right * self.fov_width / 2.0
                       - self.up * self.fov_height / 2.0
                       + self.right * pixel_width / 2.0
                       + self.up * pixel_height / 2.0)
        for y in coordinate_range(ymin, ymax, image_height):
            for x in coordinate_range(xmin, xmax, image_width):
                direction = (bottom_left
                             + x * pixel_width * self.right
                             + y * pixel_height * self.up)
                yield (x, y, Ray(self.eye, direction))


class Equirectangular(Camera):
    """A Camera that uses the equirectangular projection.

    It renders a full 360 degree image of the scene, suitable for viewing
    with VR headsets.
    """

    def __init__(self, eye, up, forward):
        """Initialise an Equirectangular camera."""
        self.eye = eye
        self.forward = forward.normalized()
        # Ensure "up" is _|_ to "forward"
        self.up = (up - (up @ self.forward) * self.forward).normalized()
        self.right = self.forward.cross(self.up)

    def rays(self, image_width, image_height=None,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield the rays for an equirectangular camera."""
        image_height = image_height or image_width / 2
        dphi = 2.0 * pi / image_width
        dtheta = pi / image_height
        left = -self.right
        back = -self.forward
        down = -self.up
        for y in coordinate_range(ymin, ymax, image_height):
            theta = (image_height / 2 - y + 0.5) * dtheta
            sin_theta = sin(theta)
            cos_theta = cos(theta)
            for x in coordinate_range(xmin, xmax, image_width):
                phi = (x + 0.5) * dphi
                sin_phi = sin(phi)
                cos_phi = cos(phi)
                # shoot rays from 'eye' to
                # (cos(phi)sin(theta), sin(phi)sin(theta), cos(theta))
                direction = (cos_phi * sin_theta * back +
                             sin_phi * sin_theta * left +
                             cos_theta * down)
                yield (x, y, Ray(self.eye, direction))
