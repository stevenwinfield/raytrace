"""
linalg.

Linear Algebra.
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

    def refracted(self, normal, ior):
        """Return self after refraction.

        Uses the given unit normal and index of refraction.
        """
        # ior = sin i / sin r

    def project_out(self, other, normalized=False):
        """Return self with any component along other removed.

        If other is known to be normalized, pass normalized=True.
        """
        unit = other if normalized else other.normalized()
        return self - (self @ unit) * unit

    def __getstate__(self):
        return (self.x, self.y, self.z)

    def __setstate__(self, state):
        self.x, self.y, self.z = state


class Matrix:

    def __init__(self, values=None):
        """Initialise from a list of 3-item lists (the rows)"""
        self.x = values or [[0.0, 0.0, 0.0] for _ in range(3)]

    def det(self):
        """Return the determinant of this matrix"""
        return (self.x[0][0] * (self.x[1][1] * self.x[2][2] - self.x[1][2] * self.x[2][1]) -
                self.x[0][1] * (self.x[1][0] * self.x[2][2] - self.x[1][2] * self.x[2][0]) +
                self.x[0][2] * (self.x[1][0] * self.x[2][1] - self.x[1][1] * self.x[2][0]))

    def is_singular(self):
        """Return True if this matrix is singular."""
        return self.det() == 0.0

    def t(self):
        """Return the transpose of self."""
        return type(self)(self.x[0][0], self.x[1][0], self.x[2][0], 
                          self.x[0][1], self.x[1][1], self.x[2][1],
                          self.x[0][2], self,x[1][2], self.x[2][2])

    def __matmul__(self, other):
        if isinstance(other, Vector):
            result = Vector()
            for j in range(3):
                for i in range(3):
                    result[i] += self.x[i][j] * other[j]
        elif isinstance(other, Matrix):
            result = Matrix()
            for k in range(3):
                for j in range(3):
                    for i in range(3):
                        result[i][j] += self.x[i][k] * other.x[k][j]
        else:
            return NotImplemented

        return result
