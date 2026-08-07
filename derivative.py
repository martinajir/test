#!/usr/bin/env python3
"""Compute the derivative of a polynomial.

The polynomial is given as a list of coefficients, highest degree first,
e.g. "1,0,-3" represents x^2 - 3.

Two methods are supported:
  - symbolic (default): computes the exact derivative polynomial using the
    power rule, then evaluates it at x. Also prints the derivative
    polynomial itself.
  - numerical: approximates f'(x) using the central difference method:
    f'(x) ~= (f(x+h) - f(x-h)) / (2h)

Both methods support an --order (or interactive prompt) to compute higher
order derivatives (2nd, 3rd, ...).

Examples:
    $ python derivative.py "1,0,-3" 2
    Polynomial: x^2 - 3
    1st derivative: 2x
    f'(2.0) = 4.0

    $ python derivative.py "1,0,-3" 2 --order 2
    Polynomial: x^2 - 3
    2nd derivative: 2
    f''(2.0) = 2.0

    $ python derivative.py "1,0,-3" 2 --method numerical
    f'(2.0) is approximately 4.000000000115023
"""

import argparse
import sys


class DerivativeError(ValueError):
    """Raised when the polynomial or input arguments are invalid."""


def parse_coefficients(text):
    """Parse a comma-separated coefficient string into a list of floats.

    Raises DerivativeError if the input is empty or contains a value that
    cannot be converted to a float.
    """
    if not text or not text.strip():
        raise DerivativeError("Coefficients cannot be empty.")

    parts = [part.strip() for part in text.split(",")]
    try:
        return [float(part) for part in parts]
    except ValueError as exc:
        raise DerivativeError(f"Invalid coefficient in '{text}': {exc}") from exc


def evaluate(coefficients, x):
    """Evaluate a polynomial (highest degree first) at x."""
    result = 0.0
    degree = len(coefficients) - 1
    for i, coeff in enumerate(coefficients):
        result += coeff * (x ** (degree - i))
    return result


def symbolic_derivative(coefficients):
    """Return the coefficients of the exact derivative polynomial.

    Uses the power rule: d/dx[c * x^n] = c*n * x^(n-1).
    The derivative of a constant (or empty polynomial) is [0].
    """
    degree = len(coefficients) - 1
    if degree <= 0:
        return [0.0]

    result = []
    for i, coeff in enumerate(coefficients[:-1]):
        power = degree - i
        result.append(coeff * power)
    return result


def nth_symbolic_derivative(coefficients, order):
    """Apply symbolic_derivative repeatedly to get the nth derivative."""
    if order < 0:
        raise DerivativeError("Order must be a non-negative integer.")

    current = coefficients
    for _ in range(order):
        current = symbolic_derivative(current)
    return current


def numerical_derivative(coefficients, x, order=1, h=1e-4):
    """Approximate the nth derivative at x using repeated central differences."""
    if order < 0:
        raise DerivativeError("Order must be a non-negative integer.")
    if order == 0:
        return evaluate(coefficients, x)
    if order == 1:
        return (evaluate(coefficients, x + h) - evaluate(coefficients, x - h)) / (2 * h)

    # For higher orders, differentiate the lower-order numerical derivative
    # function using the same central difference approach.
    def f(point):
        return numerical_derivative(coefficients, point, order - 1, h)

    return (f(x + h) - f(x - h)) / (2 * h)


def format_polynomial(coefficients):
    """Render a coefficient list as a human-readable polynomial string,
    e.g. [1, 0, -3] -> "x^2 - 3", [0.0] -> "0".
    """
    degree = len(coefficients) - 1
    terms = []
    for i, coeff in enumerate(coefficients):
        power = degree - i
        if coeff == 0:
            continue

        abs_coeff = abs(coeff)
        sign = "-" if coeff < 0 else "+"

        if power == 0:
            term = f"{abs_coeff:g}"
        elif power == 1:
            term = "x" if abs_coeff == 1 else f"{abs_coeff:g}x"
        else:
            term = f"x^{power}" if abs_coeff == 1 else f"{abs_coeff:g}x^{power}"

        terms.append((sign, term))

    if not terms:
        return "0"

    first_sign, first_term = terms[0]
    rendered = f"-{first_term}" if first_sign == "-" else first_term
    for sign, term in terms[1:]:
        rendered += f" {sign} {term}"
    return rendered


def ordinal(n):
    """Return the ordinal string for a positive integer, e.g. 1 -> '1st'."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def prime_marks(order):
    """Return the prime notation for f at a given derivative order, e.g. f''."""
    return "f" + ("'" * order) if order <= 3 else f"f^({order})"


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Compute the derivative of a polynomial at a point.",
    )
    parser.add_argument(
        "coefficients",
        nargs="?",
        help="Comma-separated coefficients, highest degree first (e.g. '1,0,-3').",
    )
    parser.add_argument(
        "x",
        nargs="?",
        type=float,
        help="The point at which to evaluate the derivative.",
    )
    parser.add_argument(
        "--order",
        type=int,
        default=1,
        help="Order of the derivative to compute (default: 1).",
    )
    parser.add_argument(
        "--method",
        choices=["symbolic", "numerical"],
        default="symbolic",
        help=(
            "Computation method: 'symbolic' computes the exact derivative "
            "polynomial via the power rule (default); 'numerical' "
            "approximates it using central differences."
        ),
    )
    return parser.parse_args(argv)


def run(coefficients, x, order=1, method="symbolic"):
    """Compute and return (derivative_coefficients_or_None, value) for the
    requested order and method. derivative_coefficients_or_None is only
    populated for the symbolic method.
    """
    if method == "symbolic":
        deriv_coeffs = nth_symbolic_derivative(coefficients, order)
        value = evaluate(deriv_coeffs, x)
        return deriv_coeffs, value

    value = numerical_derivative(coefficients, x, order)
    return None, value


def main():
    args = parse_args(sys.argv[1:])

    try:
        if args.coefficients is not None and args.x is not None:
            coefficients = parse_coefficients(args.coefficients)
            x = args.x
        else:
            coeff_text = input(
                "Enter polynomial coefficients (comma-separated, highest degree first): "
            )
            coefficients = parse_coefficients(coeff_text)
            x = float(input("Enter the point x at which to evaluate the derivative: "))

        order = args.order
        if order < 0:
            raise DerivativeError("Order must be a non-negative integer.")

        deriv_coeffs, value = run(coefficients, x, order, args.method)
    except DerivativeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"Polynomial: {format_polynomial(coefficients)}")

    if args.method == "symbolic":
        label = "Derivative" if order == 1 else f"{ordinal(order)} derivative"
        print(f"{label}: {format_polynomial(deriv_coeffs)}")
        print(f"{prime_marks(order)}({x}) = {value:g}")
    else:
        print(f"{prime_marks(order)}({x}) is approximately {value}")


if __name__ == "__main__":
    main()
