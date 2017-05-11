"""
ray.py

Defines the Ray class
"""


class Ray:
    """
    A ray (of light, for example).

    Defined by x = source + distance * direction

    where:
    source is a vector, giving the position of the ray's source
    direction is a unit vector pointing in the direction of the ray's motion
    distance is a positive scalar giving the distance between the source and
        the resultant point.
    """

    def __init__(self, source, direction, normalize=False):
        self.source = source
        self.direction = direction.normalized() if normalize else direction

    def point(self, distance):
        """ Return a point on this ray a given distance from its source """
        return self.source + distance * self.direction

    def points(self, start, end, step=1.0):
        distance = start
        current = self.point(start)
        delta = step * self.direction
        while True:
            yield current
            distance += step
            if distance >= end:
                break
            current = current + delta  # construct a new vector

    def __repr__(self):
        return "{}(source={}, direction={})".format(type(self).__name__,
                                               self.source, self.direction)
