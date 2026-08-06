#!/usr/bin/env python3
"""Simple script that divides two numbers."""

import sys


def divide(a, b):
    """Return the quotient of a divided by b."""
    return a / b


def main():
    try:
        if len(sys.argv) == 3:
            a, b = float(sys.argv[1]), float(sys.argv[2])
        else:
            a = float(input("Enter the first number: "))
            b = float(input("Enter the second number: "))
    except ValueError:
        print("Error: please provide valid numbers.")
        sys.exit(1)

    try:
        result = divide(a, b)
    except ZeroDivisionError:
        print("Error: cannot divide by zero.")
        sys.exit(1)

    print(f"{a} divided by {b} is {result}")


if __name__ == "__main__":
    main()
