#!/usr/bin/env python3
"""Simple script that adds two numbers together."""

import sys


def add_numbers(a, b):
    """Return the sum of two numbers."""
    return a + b


def main():
    if len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))

    print(f"The sum of {a} and {b} is {add_numbers(a, b)}")


if __name__ == "__main__":
    main()
