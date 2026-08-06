#!/usr/bin/env python3
"""Simple script that adds or divides two numbers together."""

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
    if len(sys.argv) == 4:
        op = sys.argv[1]
        a, b = float(sys.argv[2]), float(sys.argv[3])
    elif len(sys.argv) == 3:
        op = "add"
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        op = input("Enter operation (add/divide): ").strip().lower() or "add"
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    if op in ("divide", "div", "/"):
        try:
            print(f"{a} divided by {b} is {divide(a, b)}")
        except ZeroDivisionError as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print(f"The sum of {a} and {b} is {add(a, b)}")


if __name__ == "__main__":
    main()
