"""
environment.

Inquiries about the environment we're running in.
"""

import platform


def is_cpython():
    """Return True if the interpreter is CPython."""
    return platform.python_implementation().lower() == "cpython"


def is_pypy():
    """Return True if the interpreter is PyPy."""
    return platform.python_implementation().lower() == "pypy"
