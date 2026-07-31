#!/usr/bin/env python3
"""A simple calculator script that performs addition."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def main():
    if len(sys.argv) != 3:
        print("Usage: python calculator.py <num1> <num2>")
        sys.exit(1)

    try:
        num1 = float(sys.argv[1])
        num2 = float(sys.argv[2])
    except ValueError:
        print("Error: please provide valid numbers.")
        sys.exit(1)

    result = add(num1, num2)
    print(f"{num1} + {num2} = {result}")


if __name__ == "__main__":
    main()
