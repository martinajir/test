#!/usr/bin/env python3
"""Simple script that divides two numbers."""

import sys


def divide(a, b):
    """Return the quotient of a and b.

    Raises:
        ZeroDivisionError: If b is 0.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def main():
    if len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    try:
        result = divide(a, b)
    except ZeroDivisionError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"The quotient of {a} and {b} is {result}")


if __name__ == "__main__":
    main()
