#!/usr/bin/env python3
"""Simple script to multiply two numbers."""

import argparse


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b


def main():
    parser = argparse.ArgumentParser(description="Multiply two numbers.")
    parser.add_argument("a", type=float, help="First number")
    parser.add_argument("b", type=float, help="Second number")
    args = parser.parse_args()

    result = multiply(args.a, args.b)
    print(result)


if __name__ == "__main__":
    main()
