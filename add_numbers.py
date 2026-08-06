#!/usr/bin/env python3
"""Simple script that adds or divides two numbers."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def divide(a, b):
    """Return the result of dividing a by b."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def main():
    if len(sys.argv) == 4:
        a, op, b = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    elif len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
        op = "+"
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))
        op = input("Enter an operation (+ or /): ").strip() or "+"

    if op == "/":
        try:
            print(f"{a} divided by {b} is {divide(a, b)}")
        except ZeroDivisionError as exc:
            print(f"Error: {exc}")
    else:
        print(f"The sum of {a} and {b} is {add(a, b)}")


if __name__ == "__main__":
    main()
