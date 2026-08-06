#!/usr/bin/env python3
"""Simple script that adds two numbers together."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def divide(a, b):
    """Return the quotient of a and b."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def main():
    if len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    print(f"The sum of {a} and {b} is {add(a, b)}")

    try:
        print(f"The division of {a} by {b} is {divide(a, b)}")
    except ZeroDivisionError as e:
        print(f"Cannot compute division: {e}")


if __name__ == "__main__":
    main()
