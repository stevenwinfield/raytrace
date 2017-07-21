"""
camera.

Defines the Camera classes.

Cameras are positioned and oriented, then are responsible for yielding
rays which should be traced.
"""


from abc import ABCMeta, abstractmethod
from math import pi, sin, cos
from random import shuffle

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

    @abstractmethod
    def __getstate__(self):
        """Used to implement pickling."""

    @abstractmethod
    def __setstate__(self):
        """Used to implement pickling."""

    def ray_count(self, image_width, image_height,
                  xmin=0, xmax=None, ymin=0, ymax=None):
        """Return the number of rays that will be yielded."""
        return (len(coordinate_range(xmin, xmax, image_width)) *
                len(coordinate_range(ymin, ymax, image_height)))

class Shuffler(Camera):
    def __init__(self, camera):
        self.camera = camera
    def __getstate__(self):
        return (self.camera,)
    def __setstate__(self, state):
        self.camera, = state
    def ray_count(self, image_width, image_height,
                  xmin=0, xmax=None, ymin=0, ymax=None):
        return self.camera.ray_count(image_width, image_height,
                                     xmin, xmax, ymin, ymax)
    def rays(self, image_width, image_height,
             xmin=0, xmax=None, ymin=0, ymax=None):
        rays = list(self.camera.rays(image_width, image_height, xmin, xmax, ymin, ymax))
        shuffle(rays)
        return iter(rays)

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

    def __getstate__(self):
        return (self.position, self.forward, self.up, self.width, self.height,
                self.right)

    def __setstate__(self, state):
        (self.position, self.forward, self.up, self.width, self.height,
         self.right) = state

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

    def __getstate__(self):
        return (self.eye, self.up, self.forward, self.fov_width,
                self.fov_height, self.fov_distance, self.right)

    def __setstate__(self, state):
        (self.eye, self.up, self.forward, self.fov_width,
         self.fov_height, self.fov_distance, self.right) = state

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

    def __getstate__(self):
        return (self.eye, self.forward, self.up, self.right)

    def __setstate__(self, state):
        self.eye, self.forward, self.up, self.right = state

    def rays(self, image_width, image_height=None,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield the rays for an equirectangular camera."""
        # In spherical polar coordinates, phi sweeps from zero (along the
        # +x axis), through pi/2 (+y), pi (-x) 3pi/2 (-y), finishing at 2pi
        # (+x again).
        # theta sweeps from zero (+z axis) through pi/2 (xy plane) to pi
        # (-z axis)

        # if we imagine that +x is along the "right" direction, +y is in the
        # "forward" dirction, and (therefore) +z is in the "up" direction,
        # and we would like the "forward" direction to be in the centre of the
        # image, then we must instead sweep phi from 3pi/2 down to -pi/2,
        # and theta from pi to zero.

        image_height = image_height or image_width / 2

        phi0 = 3.0 * pi / 2.0
        dphi = -2.0 * pi / image_width
        theta0 = pi
        dtheta = -pi / image_height

        for y in coordinate_range(ymin, ymax, image_height):
            theta = theta0 + (y + 0.5) * dtheta
            sin_theta = sin(theta)
            cos_theta = cos(theta)
            for x in coordinate_range(xmin, xmax, image_width):
                phi = phi0 + (x + 0.5) * dphi
                sin_phi = sin(phi)
                cos_phi = cos(phi)
                # shoot rays from 'eye' to
                # (cos(phi)sin(theta), sin(phi)sin(theta), cos(theta))
                direction = (cos_phi * sin_theta * self.right +
                             sin_phi * sin_theta * self.forward +
                             cos_theta * self.up)
                yield (x, y, Ray(self.eye, direction))


class StereoEquirectangular(Camera):
    """A Camera that uses the equirectangular projection and renders a
    stereoscopic image.

    It renders a full 360 degree image of the scene, twice, where each pixel
    is rendered as if the virtual head is looking straight at it.

    The top half of the resultant image is for the left eye, the bottom half
    for the right.
    """

    def __init__(self, centre, up, forward, eye_separation):
        """Initialise a StereoEquirectangular camera."""
        self.centre = centre
        self.forward = forward.normalized()
        # Ensure "up" is _|_ to "forward"
        self.up = (up - (up @ self.forward) * self.forward).normalized()
        self.eye_separation = eye_separation
        self.right = self.forward.cross(self.up)

    def __getstate__(self):
        return (self.centre, self.forward, self.up, self.eye_separation,
                self.right)

    def __setstate__(self, state):
        (self.centre, self.forward, self.up, self.eye_separation,
         self.right) = state

    def rays(self, image_width, image_height=None,
             xmin=0, xmax=None, ymin=0, ymax=None):
        """Yield the rays for an equirectangular camera."""
        # As with the Equirectangular camera, we sweep phi from 3pi/2 to -pi/2
        # and theta from pi to zero, but now the source of each ray is
        # different.
        # The sources all lie on a circle, centred on 'centre', in the
        # (forward, right) plane of radius eye_separation / 2
        # When phi = pi / 2 (i.e. we are looking forward) the left eye will be
        # at pi, while the right eye will be at 0

        image_height = image_height or image_width
        two_pi = 2.0 * pi
        half_pi = pi / 2.0

        phi0 = 3.0 * half_pi
        dphi = -two_pi / image_width
        theta0 = pi
        dtheta = -two_pi / image_height
        radius = self.eye_separation / 2.0

        for y in coordinate_range(ymin, ymax, image_height):
            is_left_eye = 2 * y > image_height

            theta = theta0 + (y + 0.5) * dtheta
            if is_left_eye:
                theta -= pi

            sin_theta = sin(theta)
            cos_theta = cos(theta)

            for x in coordinate_range(xmin, xmax, image_width):
                phi = phi0 + (x + 0.5) * dphi
                sin_phi = sin(phi)
                cos_phi = cos(phi)

                phi_eye = phi + (half_pi if is_left_eye else -half_pi)
                sin_phi_eye = sin(phi_eye)
                cos_phi_eye = cos(phi_eye)

                eye_pos = (self.centre +
                           radius * (cos_phi_eye * self.right +
                                     sin_phi_eye * self.forward))

                direction = (cos_phi * sin_theta * self.right +
                             sin_phi * sin_theta * self.forward +
                             cos_theta * self.up)

                yield (x, y, Ray(eye_pos, direction))
