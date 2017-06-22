"""
vector.

Defines the Vector class
"""

import math


class Vector:
    """A 3-dimensional vector."""

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def norm2(self):
        """Return the squared norm of this vector."""
        return self.x * self.x + self.y * self.y + self.z * self.z

    def norm(self):
        """Return the norm of this vector."""
        return math.sqrt(self.norm2())

    def __eq__(self, other):
        return (self.x == other.x and
                self.y == other.y and
                self.z == other.z)

    def __matmul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y + self.z * other.z

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other, self.z * other)

    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self

    def __rmul__(self, other):
        return self * other

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other, self.z / other)

    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        return self

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def normalize(self):
        """Make this vector have unit norm, preserving direction."""
        self /= self.norm()

    def normalized(self):
        """Return a normalized copy of this vector."""
        return self / self.norm()

    def __repr__(self):
        return "{}({}, {}, {})".format(type(self).__name__,
                                       self.x, self.y, self.z)

    def __str__(self):
        return "({0.x}, {0.y}, {0.z})".format(self)

    def cross(self, other):
        return Vector(self.y * other.z - other.y * self.z,
                      self.z * other.x - other.z * self.x,
                      self.x * other.y - other.x * self.y)

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def __getitem__(self, index):
        return self.as_tuple()[index]

    def reflected(self, normal):
        """Return self reflected from a surface with the given unit normal"""
        return self - 2.0 * (self @ normal) * normal
