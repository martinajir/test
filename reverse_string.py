#!/usr/bin/env python3
"""A simple script that reverses a string."""

import sys


def reverse_string(text: str) -> str:
    """Return the reverse of the given string."""
    return text[::-1]


def main() -> None:
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = input("Enter a string to reverse: ")

    print(reverse_string(text))


if __name__ == "__main__":
    main()
