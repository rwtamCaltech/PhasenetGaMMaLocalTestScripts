"""
Basic mathematical calculations utility module.

Resolves: https://github.com/rwtamCaltech/PhasenetGaMMaLocalTestScripts/issues/4
"""

import math


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def subtract(a, b):
    """Return the difference of a minus b."""
    return a - b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def divide(a, b):
    """Return a divided by b.

    Raises ValueError if b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def power(base, exp):
    """Return base raised to the power of exp."""
    return base ** exp


def square_root(n):
    """Return the square root of n.

    Raises ValueError if n is negative.
    """
    if n < 0:
        raise ValueError("Cannot compute square root of a negative number.")
    return math.sqrt(n)


def mean(values):
    """Return the arithmetic mean of a non-empty list of numbers.

    Raises ValueError if values is empty.
    """
    if not values:
        raise ValueError("Cannot compute mean of an empty list.")
    return sum(values) / len(values)


def median(values):
    """Return the median of a non-empty list of numbers.

    Raises ValueError if values is empty.
    """
    if not values:
        raise ValueError("Cannot compute median of an empty list.")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
