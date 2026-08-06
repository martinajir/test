#!/usr/bin/env python3
"""Simple script that adds or divides two numbers."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def divide(a, b):
    """Return the quotient of a and b.

    Raises:
        ValueError: if b is zero, since division by zero is undefined.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


OPERATIONS = {
    "add": (add, "sum"),
    "divide": (divide, "quotient"),
}


def main():
    args = sys.argv[1:]

    if args and args[0] in OPERATIONS:
        operation = args[0]
        args = args[1:]
    else:
        operation = "add"

    func, noun = OPERATIONS[operation]

    if len(args) == 2:
        a, b = float(args[0]), float(args[1])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    try:
        result = func(a, b)
    except ValueError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"The {noun} of {a} and {b} is {result}")


if __name__ == "__main__":
    main()
