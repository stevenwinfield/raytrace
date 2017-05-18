"""
primitives.

Defines the Primitive class - a base class for all renderable objects -
and some primitives that derive from it.
"""


import math
from abc import ABCMeta, abstractmethod


class Primitive(metaclass=ABCMeta):
    """Abstract base class for all renderable objects."""

    @abstractmethod
    def bounding_box(self):
        """Return a Box that bounds this primitive."""

    @abstractmethod
    def intersection(self, ray, compute_normal=True):
        """Compute the intersection of the given ray with this primitive.

        Return the distance along the ray that first intersects with
        this primitive, or None if there is no intersection.
        If compute_normal is True then also return the normal vector at
        the point of intersection.
        """


class AxisAlignedBox(Primitive):
    """A box whose axes are aligned with the Cartesian coordinate system.

    Defined by xmin, xmax, ymin, yman, zmin, zmax.
    """

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax

    def bounding_box(self):
        return self

    def intersection(self, ray):
        pass

class Sphere(Primitive):
    """A sphere.

    Defined by its centre (a vector) and its radius.
    """

    def __init__(self, centre, radius):
        self.centre = centre
        self.radius = radius
        self._radius2 = self.radius * self.radius

    def bounding_box(self):
        pass

    def intersection(self, ray, compute_normal=True):
        """Compute the intersection between the ray and this sphere."""
        diff = self.centre - ray.source
        diff2 = diff.norm2()
        projection = ray.direction @ diff
        projection2 = projection * projection

        discriminant = projection2 - diff2 + self._radius2
        if discriminant < 0.0:
            intersection_distance = None
        else:
            sq_discriminant = math.sqrt(discriminant)
            distance1 = projection + sq_discriminant
            distance2 = projection - sq_discriminant

            visible1 = distance1 >= 0.0
            visible2 = distance2 >= 0.0

            if visible1:
                if visible2:
                    intersection_distance = min(distance1, distance2)
                else:
                    intersection_distance = visible1
            elif visible2:
                intersection_distance = distance2
            else:
                intersection_distance = None

        if compute_normal:
            if intersection_distance is None:
                normal = None
            else:
                normal = ray.point(intersection_distance) - self.centre
                normal.normalize()
            return intersection_distance, normal
        else:
            return intersection_distance
