"""
test.

Defines and runs tests.
"""

from unittest import TestCase, main

from .vector import Vector

class Test_1_Vector(TestCase):
    """Simple unit tests for the Vector class"""

    def test_equality(self):
        x = Vector(1.0, 2.0, 3.0)
        y = Vector(1.0, 2.0, 3.0)
        z = Vector(2.0, 2.0, 3.0)
        self.assertEqual(x, y)
        self.assertNotEqual(x, z)

    def test_addition(self):
        x = Vector(1.0, 0.0, 0.0)
        y = Vector(0.0, 2.0, 0.0)
        result = Vector(1.0, 2.0, 0.0)
        self.assertEqual(x + y, result)

        x += y
        self.assertEqual(x, result)

    def test_subtraction(self):
        x = Vector(1.0, 0.0, 0.0)
        y = Vector(0.0, 2.0, 0.0)
        result = Vector(1.0, -2.0, 0.0)
        self.assertEqual(x - y, result)

        x -= y
        self.assertEqual(x, result)

    def test_multiplication(self):
        x = Vector(1.0, 2.0, 3.0)
        m = 3.0
        result = Vector(3.0, 6.0, 9.0)
        self.assertEqual(x * m, result)
        self.assertEqual(m * x, result)

        x *= m
        self.assertEqual(x, result)

    def test_division(self):
        x = Vector(1.0, 2.0, 3.0)
        d = 2.0
        result = Vector(0.5, 1.0, 1.5)
        self.assertEqual(x / d, result)

        x /= d
        self.assertEqual(x, result)

    def test_negation(self):
        x = Vector(3.0, 4.0, 12.0)
        result = Vector(-3.0, -4.0, -12.0)
        self.assertEqual(-x, result)

    def test_norm(self):
        x = Vector(3.0, 4.0, 12.0)
        self.assertEqual(x.norm2(), 169.0)
        self.assertEqual(x.norm(), 13.0)

    def test_dot_product(self):
        x = Vector(1.0, 2.0, 3.0)
        y = Vector(2.0, -3.0, 5.0)
        result = 11.0
        self.assertEqual(x @ y, result)
        self.assertEqual(y @ x, result)

    def test_cross_product(self):
        x = Vector(1.0, 0.0, 0.0)
        y = Vector(0.0, 1.0, 0.0)
        result = Vector(0.0, 0.0, 1.0)
        self.assertEqual(x.cross(y), result)
        self.assertEqual(y.cross(x), -result)

    def test_normalize(self):
        x = Vector(2.0, 3.0, 4.0)
        self.assertEqual(x.normalized().norm2(), 1.0)
        x.normalize()
        self.assertEqual(x.norm2(), 1.0)

    def test_reflection(self):
        x = Vector(1.0, 1.0, 0.0)
        n = Vector(1.0, 0.0, 0.0)
        result = Vector(-1.0, 1.0, 0.0)
        self.assertEqual(x.reflected(n), result)


def run():
    """Run the tests."""
    main(verbosity=2)


if __name__ == "__main__":
    run()
