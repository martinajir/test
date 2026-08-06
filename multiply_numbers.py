#!/usr/bin/env python3
"""Simple script that multiplies two numbers together."""

import sys


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


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

    print(f"The product of {a} and {b} is {multiply(a, b)}")


if __name__ == "__main__":
    main()
