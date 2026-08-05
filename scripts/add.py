#!/usr/bin/env python3
"""Simple script to add, subtract, multiply, or divide two numbers."""
import sys


def add(a, b):
    return a + b


def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


OPERATIONS = {
    "+": add,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": divide,
}


def main():
    if len(sys.argv) == 4 and sys.argv[2] in OPERATIONS:
        a, op, b = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
    elif len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
        op = "+"
    else:
        a = float(input("Enter first number: "))
        op = input("Enter operation (+, -, *, /) [default +]: ").strip() or "+"
        b = float(input("Enter second number: "))

    if op not in OPERATIONS:
        print(f"Unknown operation: {op}", file=sys.stderr)
        sys.exit(1)

    try:
        result = OPERATIONS[op](a, b)
    except ZeroDivisionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if result == int(result):
        result = int(result)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
