#!/usr/bin/env python3
"""Simple script to add two numbers together."""
import sys


def add(a, b):
    return a + b


def main():
    if len(sys.argv) == 3:
        a, b = float(sys.argv[1]), float(sys.argv[2])
    else:
        a = float(input("Enter first number: "))
        b = float(input("Enter second number: "))

    result = add(a, b)
    if result == int(result):
        result = int(result)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
