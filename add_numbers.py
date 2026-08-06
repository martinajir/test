#!/usr/bin/env python3
"""Simple script that adds or divides two numbers."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def divide(a, b):
    """Return the quotient of a divided by b.

    Raises:
        ZeroDivisionError: if b is 0.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


def main():
    args = sys.argv[1:]

    operation = "add"
    if args and args[0] in ("add", "divide"):
        operation = args[0]
        args = args[1:]

    if len(args) == 2:
        a, b = float(args[0]), float(args[1])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))

    if operation == "divide":
        try:
            print(f"{a} divided by {b} is {divide(a, b)}")
        except ZeroDivisionError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        print(f"The sum of {a} and {b} is {add(a, b)}")


if __name__ == "__main__":
    main()
