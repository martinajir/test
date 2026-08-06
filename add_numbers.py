#!/usr/bin/env python3
"""Simple script that adds or multiplies two numbers together."""

import sys


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


OPERATIONS = {
    "add": add,
    "multiply": multiply,
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
        choice = input("Choose operation (add/multiply) [add]: ").strip().lower()
        if choice in OPERATIONS:
            operation = choice

    result = OPERATIONS[operation](a, b)
    verb = "sum" if operation == "add" else "product"
    print(f"The {verb} of {a} and {b} is {result}")


if __name__ == "__main__":
    main()
