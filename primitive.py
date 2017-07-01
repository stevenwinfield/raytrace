"""
primitive.

Defines the Primitive class - a base class for all renderable objects -
and some primitives that derive from it.
"""

from random import random
import math
from abc import ABCMeta, abstractmethod

from .vector import Vector
from .constants import INFINITY, INTERSECTION_TOLERANCE


class Primitive(metaclass=ABCMeta):
    """Abstract base class for all renderable objects."""

    _clone_attributes = ("material", "shader")

    material = None
    shader = None

    def __init__(self, material, shader):
        self.material = material
        self.shader = shader
        self._cached_bounding_box = None

    def clone_attributes(self):
        attrs = ()
        for cls in type(self).__mro__:
            if hasattr(cls, "_clone_attributes"):
                attrs += cls._clone_attributes
        return attrs

    def clone(self, **replacements):
        """Return a clone of self, optionally with changes."""
        attrs = self.clone_attributes()
        values = {attr: getattr(self, attr) for attr in attrs}
        values.update(replacements)
        return type(self)(**values)

    def bounding_box(self):
        if not self._cached_bounding_box:
            self._cached_bounding_box = self._bounding_box()
        return self._cached_bounding_box

    @abstractmethod
    def _bounding_box(self):
        """Return an AxisAlignedBox that bounds this primitive."""

    def intersection(self, ray, compute_normal=True):
        distance, normal = self._intersection(ray, compute_normal)
        return distance, normal

    @abstractmethod
    def _intersection(self, ray, compute_normal=True):
        """Compute the intersection of the given ray with this primitive.

        Return the distance along the ray that first intersects with
        this primitive, or None if there is no intersection.
        If compute_normal is True then also return the normal vector at
        the point of intersection.

        Note that the normal may have either a positive or a negative
        projection along the ray's direction, i.e. intersections can occur
        both on the "inside" and "outside" of a primitive.

        A ray intersecting a primitive from the outside will have a negative
        projection: ray.direction @ normal < 0
        """

    def __str__(self):
        values = ", ".join("{}={}".format(key, getattr(self, key))
                           for key in sorted(self.clone_attributes()))
        return "{}({})".format(type(self).__name__, values)


class AxisAlignedBox(Primitive):
    """A box whose axes are aligned with the Cartesian coordinate system.

    Defined by xmin, xmax, ymin, yman, zmin, zmax.
    """

    _clone_attributes = ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax")

    def __init__(self, xmin, xmax, ymin, ymax, zmin, zmax,
                 material=None, shader=None):
        super(AxisAlignedBox, self).__init__(material, shader)
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax

        self.min = Vector(xmin, ymin, zmin)
        self.max = Vector(xmax, ymax, zmax)

    def _bounding_box(self):
        """Return the bounding box of an AxisAlignedBox: itself."""
        return self

    _tests = [(0, 1, 2, Vector(1.0, 0.0, 0.0)),
              (1, 2, 0, Vector(0.0, 1.0, 0.0)),
              (2, 0, 1, Vector(0.0, 0.0, 1.0))]

    def _intersection(self, ray, compute_normal=True):
        """Compute the intersection of a ray with an AxisAlignedBox."""
        min_intersection_distance = INFINITY
        min_normal = None

        # Iterate over pairs of parallel planes
        for index, other1, other2, normal in self._tests:
            # if the ray direction is || to these planes there will be no
            # intersection
            if ray.direction[index] == 0.0:
                continue

            # Iterate over the two planes in this pair
            for plane_distance, this_normal in ((self.min[index], -normal),
                                                (self.max[index], normal)):
                intersection_distance = ((plane_distance - ray.source[index]) /
                                         ray.direction[index])
                # if the intersection is within range...
                if ray.min_distance < intersection_distance < ray.max_distance:
                    # ... see if the intersection point is bounded by the
                    # two planes normal to direction "other1"
                    intersection1 = (ray.source[other1] +
                                     intersection_distance *
                                     ray.direction[other1])

                    if self.min[other1] <= intersection1 <= self.max[other1]:

                        # ... and if that test passes then repeat with
                        # direction "other2"...
                        intersection2 = (ray.source[other2] +
                                         intersection_distance *
                                         ray.direction[other2])
                        if (self.min[other2]
                            <= intersection2
                            <= self.max[other2]
                            # ... then we have an intersection.
                            # If this is the closest one so far then record it.
                            and intersection_distance
                                < min_intersection_distance):
                            min_intersection_distance = intersection_distance
                            min_normal = this_normal

            return min_intersection_distance, min_normal

    def combine(self, other):
        """Return the AxisAlignedBox that contains self and other."""
        return AxisAlignedBox(min(self.xmin, other.xmin),
                              max(self.xmax, other.xmax),
                              min(self.ymin, other.ymin),
                              max(self.ymax, other.ymax),
                              min(self.zmin, other.zmin),
                              max(self.zmax, other.zmax))

    def overlap(self, other):
        """Return the AxisAlignedBox that is the overlap of self and other.

        If there is no overlap then None is returned.
        """
        xmin = max(self.xmin, other.xmin)
        xmax = min(self.xmax, other.xmax)
        if xmax < xmin:
            return None
        ymin = max(self.ymin, other.ymin)
        ymax = min(self.ymax, other.ymax)
        if ymax < ymin:
            return None
        zmin = max(self.zmin, other.zmin)
        zmax = min(self.zmax, other.zmax)
        if zmax < zmin:
            return None

        return AxisAlignedBox(xmin, xmax, ymin, ymax, zmin, zmax)

    def volume(self):
        """Return the volume of this AxisAlignedBox"""
        return ((self.xmax - self.xmin) *
                (self.ymax - self.ymin) *
                (self.zmax - self.zmin))

    @classmethod
    def infinite(cls):
        """Return an infinite AxisAlignedBox."""
        return cls(-INFINITY, INFINITY,
                   -INFINITY, INFINITY,
                   -INFINITY, INFINITY)


class Sphere(Primitive):
    """A sphere.

    Defined by its centre (a vector) and its radius.
    """

    _clone_attributes = ("centre", "radius")

    def __init__(self, centre, radius, material=None, shader=None):
        """Initialise this sphere."""
        super(Sphere, self).__init__(material, shader)
        self.centre = centre
        self.radius = radius
        self._radius2 = self.radius * self.radius

    def _bounding_box(self):
        """Return a bounding box for this sphere."""
        return AxisAlignedBox(self.centre.x - self.radius,
                              self.centre.x + self.radius,
                              self.centre.y - self.radius,
                              self.centre.y + self.radius,
                              self.centre.z - self.radius,
                              self.centre.z + self.radius)

    def _intersection(self, ray, compute_normal=True):
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

            visible1 = ray.min_distance < distance1 < ray.max_distance
            visible2 = ray.min_distance < distance2 < ray.max_distance

            if visible1:
                if visible2:
                    intersection_distance = min(distance1, distance2)
                else:
                    intersection_distance = distance1
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
        else:
            normal = None

        return intersection_distance, normal


class FuzzySphere(Sphere):
    """A Sphere with a rough surface."""

    # TODO does this work with clone attributes?
    def _intersection(self, ray, compute_normal=True):
        """Compute the intersection between the ray and this sphere.

        Adds some randomness to the normal of a regular sphere.
        """
        intersection_distance, normal = (super(FuzzySphere, self)
                                         .intersection(ray, compute_normal))
        if compute_normal and normal is not None:
            normal += (Vector(random(), random(), random()) * 0.1).normalized()
        return intersection_distance, normal


class Plane(Primitive):

    _clone_attributes = ("point", "normal")

    def __init__(self, point, normal, material=None, shader=None):
        super(Plane, self).__init__(material, shader)
        self.point = point
        self.normal = normal.normalized()
        self._signed_distance = self.point @ self.normal

    def _bounding_box(self):
        """There is no finite bounding box for a plane."""
        return AxisAlignedBox.infinite()

    def _intersection(self, ray, compute_normal=True):
        proj = ray.direction @ self.normal
        if abs(proj) < INTERSECTION_TOLERANCE:  # TODO: almost_zero() ?
            distance = None
        else:
            distance = ((self._signed_distance - ray.source @ self.normal)
                        / proj)
            if not (ray.min_distance < distance < ray.max_distance):
                distance = None

        return distance, self.normal


class InfiniteCylinder(Primitive):

    _clone_attributes = ("axis_point", "axis_direction", "radius")

    def __init__(self, axis_point, axis_direction, radius, material=None,
                 shader=None):
        super(InfiniteCylinder, self).__init__(material, shader)
        self.axis_point = axis_point
        self.axis_direction = axis_direction.normalized()
        self.radius = radius
        self._radius2 = radius * radius

    def _bounding_box(self):
        return AxisAlignedBox.infinite()

    def _intersection(self, ray, compute_normal=True):

        d = ray.direction.project_out(self.axis_direction)
        a = d.norm2()
        if a == 0.0:
            return None, None

        diff = (ray.source - self.axis_point).project_out(self.axis_direction)

        b_2 = d @ diff
        c = diff.norm2() - self._radius2
        discriminant = b_2 * b_2 - a * c

        if discriminant < 0.0:
            return None, None

        lambda1 = (math.sqrt(discriminant) - b_2) / a
        lambda2 = (-math.sqrt(discriminant) - b_2) / a

        # Find the closest intersection, if any, that is between the ray's
        # min and max distances
        if lambda1 < lambda2 and ray.min_distance < lambda1 < ray.max_distance:
            distance = lambda1
        elif ray.min_distance < lambda2 < ray.max_distance:
            distance = lambda2
        else:
            return None, None

        if compute_normal:
            normal = (diff + distance * d).normalized()
        else:
            normal = None

        return distance, normal


class Cylinder(Primitive):

    _clone_attributes = ("axis_start", "axis_end", "radius")

    def __init__(self, axis_start, axis_end, radius, material=None,
                 shader=None):
        super(Cylinder, self).__init__(material, shader)
        self.axis_start = axis_start
        self.axis_end = axis_end
        self.axis_direction = (axis_end - axis_start).normalized()
        self.length = (axis_end - axis_start).norm()
        self.radius = radius
        self._radius2 = radius * radius

    def _bounding_box(self):
        start_box = AxisAlignedBox(self.axis_start.x - self.radius,
                                   self.axis_start.x + self.radius,
                                   self.axis_start.y - self.radius,
                                   self.axis_start.y + self.radius,
                                   self.axis_start.z - self.radius,
                                   self.axis_start.z + self.radius)

        end_box = AxisAlignedBox(self.axis_end.x - self.radius,
                                 self.axis_end.x + self.radius,
                                 self.axis_end.y - self.radius,
                                 self.axis_end.y + self.radius,
                                 self.axis_end.z - self.radius,
                                 self.axis_end.z + self.radius)

        return start_box.combine(end_box)

    def _intersection(self, ray, compute_normal=True):

        d = ray.direction.project_out(self.axis_direction)
        a = d.norm2()
        if a == 0.0:
            return None, None

        diff = (ray.source - self.axis_start).project_out(self.axis_direction)

        b_2 = d @ diff
        c = diff.norm2() - self._radius2
        discriminant = b_2 * b_2 - a * c

        if discriminant < 0.0:
            return None, None

        lambda1 = (math.sqrt(discriminant) - b_2) / a
        lambda2 = (-math.sqrt(discriminant) - b_2) / a

        lambda_min, lambda_max = ((lambda1, lambda2) if lambda1 < lambda2 else
                                  (lambda2, lambda1))

        # Find the closest intersection, if any, that is between the ray's
        # min and max distances
        distance = None
        if ray.min_distance < lambda_min < ray.max_distance:
            distance = lambda_min
            intersection_point = ray.point(distance)
            along_axis = ((intersection_point - self.axis_start)
                          @ self.axis_direction)
            if not (0.0 <= along_axis <= self.length):
                distance = None

        if (distance is None and
            ray.min_distance < lambda_max < ray.max_distance):
            distance = lambda_max
            intersection_point = ray.point(distance)
            along_axis = ((intersection_point - self.axis_start)
                          @ self.axis_direction)
            if not (0.0 <= along_axis <= self.length):
                distance = None

        if distance is None:
            return None, None

        if compute_normal:
            normal = (diff + distance * d).normalized()
        else:
            normal = None

        return distance, normal
