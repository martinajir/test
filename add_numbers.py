#!/usr/bin/env python3
"""Simple script that adds two numbers together."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def main():
    if len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    print(f"The sum of {a} and {b} is {add(a, b)}")
    print(f"The product of {a} and {b} is {multiply(a, b)}")


if __name__ == "__main__":
    main()
