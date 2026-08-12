#!/usr/bin/env python3
"""Simple script to divide two numbers."""

import sys


def divide(numerator: float, denominator: float) -> float:
    """Divide numerator by denominator, raising a clear error on division by zero."""
    if denominator == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return numerator / denominator


def main() -> None:
    if len(sys.argv) == 3:
        try:
            numerator = float(sys.argv[1])
            denominator = float(sys.argv[2])
        except ValueError:
            print("Error: both arguments must be numbers.")
            sys.exit(1)
    else:
        try:
            numerator = float(input("Enter the numerator: "))
            denominator = float(input("Enter the denominator: "))
        except ValueError:
            print("Error: please enter valid numbers.")
            sys.exit(1)

    try:
        result = divide(numerator, denominator)
    except ZeroDivisionError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"{numerator} / {denominator} = {result}")


if __name__ == "__main__":
    main()
