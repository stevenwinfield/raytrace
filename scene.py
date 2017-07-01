"""
scene.

Defines the Scene class.
"""

from functools import lru_cache, partial

from .constants import INFINITY, INTERSECTION_TOLERANCE
from .ray import Ray


class ObjectGroup:
    """A group of objects and/or other ObjectGroups.

    Used to hold objects in a graph for more efficient intersection tests.
    """

    def __init__(self, *objects):
        """Initialise an ObjectGroup with zero or more objects/groups."""
        self.objects = set()
        self._bounding_box = None
        for object_ in objects:
            self.add_object(object_)

    def add_object(self, object_):
        """Add an object to this ObjectGroup."""
        self.objects.add(object_)
        if self._bounding_box is None:
            self._bounding_box = object_.bounding_box()
        else:
            self._bounding_box = self._bounding_box.combine(
                                    object_.bounding_box())

    def bounding_box(self):
        """Return this group's bounding box."""
        return self._bounding_box

    def intersection(self, ray, compute_normal=True, source_object=None):
        """Perform an intersection test with this group.

        If an intersection is detected then recurse into child groups as
        necessary.

        Returns object, distance, normal - or None, None, None.
        """
        distance, normal = self._bounding_box.intersection(ray, False)
        if distance is None:
            return None, None, None

        min_distance = INFINITY
        min_obj = None
        min_normal = None

        for child in self.objects:
            if isinstance(child, ObjectGroup):
                obj, distance, normal = child.intersection(ray, compute_normal,
                                                           source_object)
            else:
                distance, normal = child.intersection(ray, compute_normal)
                obj = child
            if distance is not None and distance < min_distance:
                min_distance = distance
                min_obj = obj
                min_normal = normal

        if min_distance == INFINITY:
            min_distance = None

        return min_obj, min_distance, min_normal

    def print(self, indent=0):
        """Pretty-print this ObjectGroup."""
        print(" " * indent, "Object Group", self._bounding_box.volume())
        indent += 4
        for obj in self.objects:
            if isinstance(obj, ObjectGroup):
                obj.print(indent)
            else:
                print(" " * indent, type(obj).__name__,
                      obj.bounding_box().volume())


class Scene:
    """Scene class."""

    intersect_tolerance = INTERSECTION_TOLERANCE

    def __init__(self):
        """Initialise a Scene."""
        self.lights = set()
        self.objects = set()
        self.tree = None

    def intersection_old(self, ray, compute_normal=True, source_object=None):
        """Compute the intersection of this ray with all objects in the scene.

        Returns the object, +ve distance along the ray, and normal of the
        point of nearest intersection.
        source_object, if given, is the source of the ray. Used to test
        for self-intersections with low distances, caused by roundoff errors.
        """
        if self.tree is None:
            self._compute_tree()
            self.tree.print()

        return self.tree.intersection(ray, compute_normal, source_object)

    def intersection(self, ray, compute_normal=True):
        """Compute the intersection of this ray with all objects in the scene.

        Returns the object, +ve distance along the ray, and normal of the
        point of nearest intersection.
        """
        min_distance = INFINITY
        min_normal = None
        min_obj = None
        for obj in self.objects:
            distance, normal = obj.intersection(ray, compute_normal)
            if (distance is not None and distance < min_distance):
                min_distance = distance
                min_normal = normal
                min_obj = obj

        if min_distance == INFINITY:  # No intersections
            min_distance = None

        return min_obj, min_distance, min_normal

    @lru_cache(maxsize=128)
    def is_obscured(self, source, destination):  # FIXME
        """Return True if a ray from source cannot be seen from destination."""
        diff = destination - source
        ray = Ray(source, diff)
        _, distance, _ = self.intersection(ray, compute_normal=False)
        return (distance - diff.norm()) < self.intersect_tolerance

    def _compute_tree(self):
        """Create a tree of objects for more efficient intersection tests."""
        # No point making a tree for less than two objects
        if len(self.objects) < 2:
            return
        # Make a copy of our objects set - we will mutate this, not the
        # original

        objects = set(self.objects)

        # 1. pop a random element from objects
        # 2. find the element from the remaining objects that will give the
        #    minimum volume bounding box if combined in a group.
        # 3. remove that object, combine the two into a group, add back to
        #    objects
        # 4. if there is still more that one object then go to 1.

        def combined_volume(box1, obj2):
            box2 = obj2.bounding_box()
            return box1.combine(box2).volume()

        while len(objects) > 1:
            obj = objects.pop()
            best = min(objects, key=partial(combined_volume,
                                            obj.bounding_box()))
            objects.remove(best)
            objects.add(ObjectGroup(obj, best))

        self.tree = objects.pop()
