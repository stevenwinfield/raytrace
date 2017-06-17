"""
utility.

Commonly used utility functions.
"""


def clamp(value, min_value, max_value):
    """Return value clamped to the range [min_value, max_value]."""
    return max(min(value, max_value), min_value)


def approx_eq(x, y, rel_tol=1e-6, abs_tol=None):
    """Return True if x ~= y else False.

    A relative tolerance is used by default. An absolute tolerance will
    override this.
    """
    diff = x - y
    if abs_tol is not None:
        return diff < abs_tol
    elif x != 0.0 and abs(diff / x) < rel_tol:
        return True
    elif y != 0.0 and abs(diff / y) < rel_tol:
        return True
    else:
        return x == y == 0.0
