#!/usr/bin/env python3
"""Simple script that adds, multiplies, or divides two numbers together."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def divide(a, b):
    """Return the quotient of a and b."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


OPERATIONS = {
    "add": add,
    "multiply": multiply,
    "divide": divide,
}

VERBS = {
    "add": "sum",
    "multiply": "product",
    "divide": "quotient",
}


def main():
    args = sys.argv[1:]

    operation = "add"
    if args and args[-1] in OPERATIONS:
        operation = args[-1]
        args = args[:-1]

    if len(args) == 2:
        a, b = float(args[0]), float(args[1])
    else:
        a = float(input("Enter the first number: "))
        b = float(input("Enter the second number: "))
        choice = input("Choose operation (add/multiply/divide) [add]: ").strip().lower()
        if choice in OPERATIONS:
            operation = choice

    try:
        result = OPERATIONS[operation](a, b)
    except ZeroDivisionError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"The {VERBS[operation]} of {a} and {b} is {result}")


if __name__ == "__main__":
    main()
