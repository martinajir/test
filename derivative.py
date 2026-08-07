#!/usr/bin/env python3
"""Simple script that computes the numerical derivative of a polynomial at a point.

The polynomial is given as a list of coefficients, highest degree first,
e.g. [1, 0, -3] represents x^2 - 3.
"""

import sys


def evaluate(coefficients, x):
    """Evaluate a polynomial (highest degree first) at x."""
    result = 0.0
    degree = len(coefficients) - 1
    for i, coeff in enumerate(coefficients):
        result += coeff * (x ** (degree - i))
    return result


def derivative(coefficients, x, h=1e-6):
    """Approximate the derivative of the polynomial at x using the
    central difference method: f'(x) ~= (f(x+h) - f(x-h)) / (2h).
    """
    return (evaluate(coefficients, x + h) - evaluate(coefficients, x - h)) / (2 * h)


def parse_coefficients(text):
    return [float(c) for c in text.split(",")]


def main():
    args = sys.argv[1:]

    if len(args) == 2:
        coefficients = parse_coefficients(args[0])
        x = float(args[1])
    else:
        coeff_text = input("Enter polynomial coefficients (comma-separated, highest degree first): ")
        coefficients = parse_coefficients(coeff_text)
        x = float(input("Enter the point x at which to evaluate the derivative: "))

    result = derivative(coefficients, x)
    print(f"The derivative at x={x} is approximately {result}")


if __name__ == "__main__":
    main()
