from vector import Vector
from ray import Ray


x = Vector(1.0, 2.0, 3.0)
y = Vector(4.0, 3.2, 1.2)

z = x.normalized()

"""
# Vector ops
print(x + y)
print(x - y)
print(x @ y)
print(2.0 * x)
print(y * 3.0)
print(x.norm2())
print(x.norm())
print(z.norm())
print(z)
print(-z)
"""

# Ray tests

eye = Vector(0.0, 0.0, -5.0)
forward = Vector(0.0, 0.0, 1.0)

r = Ray(eye, forward)
print(list(r.points(3.0, 10.0)))
