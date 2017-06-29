"""
csg.

Constructive Solid Geometry.
"""

from .primitive import Primitive
from .constants import INFINITY, INTERSECTION_TOLERANCE


class Intersection(Primitive):
    """An Intersection of two other objects.

    The inside of the Intersection is the region of space that lies
    inside both child objects.

    The inside of a child object is the region of space that the object's
    surface normals point away from.
    """

    def __init__(self, object1, object2, material=None, shader=None):
        """Initialise this Intersection with two objects."""
        super(Intersection, self).__init__(material, shader)
        self.object1 = object1
        self.object2 = object2

    def _intersection(self, ray, compute_normal=True):
        """Compute the intersection of the ray with this Intersection."""
        # When a ray comes in from infinity, the surface of this Intersection
        # object will be the second of the two child objects.
        #
        # But when a ray's source is nearby it may already be inside one of
        # the child objects.
        #
        # So we must shoot a ray in the opposite direction to test whether this
        # is the case.

        back_ray = -ray

        d1_fwd, n1_fwd = self.object1.intersection(ray, True)
        d1_back, n1_back = self.object1.intersection(back_ray, True)

        inside1 = ((d1_fwd is not None and
                    ray.min_distance < d1_fwd < ray.max_distance and
                    n1_fwd @ ray.direction > 0.0) or
                   (d1_back is not None and
                    back_ray.min_distance < d1_back < back_ray.max_distance and
                    n1_back @ ray.direction < 0.0))

        d2_fwd, n2_fwd = self.object2.intersection(ray, True)
        d2_back, n2_back = self.object2.intersection(back_ray, True)

        inside2 = ((d2_fwd is not None and
                    ray.min_distance < d2_fwd < ray.max_distance and
                    n2_fwd @ ray.direction > 0.0) or
                   (d2_back is not None and
                    back_ray.min_distance < d2_back < back_ray.max_distance and
                    n2_back @ ray.direction < 0.0))

        if (d1_fwd or INFINITY) < (d2_fwd or INFINITY):
            first_intersection = (d1_fwd, n1_fwd)
            second_intersection = (d2_fwd, n2_fwd)
        else:
            first_intersection = (d2_fwd, n2_fwd)
            second_intersection = (d1_fwd, n1_fwd)

        # The ray's source can be outside both, just inside 1 or 2, or inside
        # both.

        if inside1:
            if inside2:
                # We're inside both here, so return the first forward
                # intersection with either 1 or 2.
                return first_intersection
            else:
                # We're inside 1, so return the forward intersection with 2
                # (which will be None if there isn't one)
                return d2_fwd, n2_fwd

        elif inside2:
            # We're inside 2, so return the forward intersection with 1 (which
            # will be None if there isn't one)
            return d1_fwd, n1_fwd

        # We're outside. The forward ray must intersect both 1 and 2,
        # and the intersection's surface will be at the second of those.
        elif d1_fwd is None or d2_fwd is None:
            return None, None

        else:
            return second_intersection

    def _bounding_box(self):
        box1 = self.object1.bounding_box()
        box2 = self.object2.bounding_box()
        return box1.overlap(box2)


class Inverse(Primitive):
    """The inverse of another object.

    Its geometry is the same, but its normals point in the opposide direction.
    """

    def __init__(self, object_):
        """Initialise this Inverse with an object."""
        self.object = object_

    @property
    def material(self):
        """Proxy the 'material' property to the child object."""
        return self.object.material

    @property
    def shader(self):
        """Proxy the 'shader' property to the child object."""
        return self.object.shader

    def _bounding_box(self):
        """Proxy the '_bounding_box' method to the child object."""
        return self.object.bounding_box()

    def _intersection(self, ray, compute_normal=True):
        """Flip the surface normal at the point of intersection."""
        result = self.object.intersection(ray, compute_normal)
        return result[0], -result[1] if result[1] is not None else None


def Difference(object1, object2, material=None, shader=None):
    """Return the difference of two objects.

    The second object is subtracted from the first, i.e. the part of the
    second object that was inside the first is outside the Difference.
    """
    return Intersection(object1, Inverse(object2), material=material,
                        shader=shader)
