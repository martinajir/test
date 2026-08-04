#!/usr/bin/env python3
"""Detect whether a given string is a palindrome.

A palindrome is a string that reads the same forwards and backwards,
ignoring case, spaces, and punctuation (e.g. "A man, a plan, a canal: Panama").
"""

import argparse
import re
import sys


def is_palindrome(text: str) -> bool:
    """Return True if `text` is a palindrome, ignoring case and non-alphanumeric characters."""
    normalized = re.sub(r"[^A-Za-z0-9]", "", text).lower()
    return normalized == normalized[::-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Check if a string is a palindrome.")
    parser.add_argument("text", nargs="?", help="The string to check.")
    args = parser.parse_args()

    text = args.text if args.text is not None else input("Enter a string: ")

    if is_palindrome(text):
        print(f'"{text}" is a palindrome.')
    else:
        print(f'"{text}" is not a palindrome.')
        sys.exit(1)


if __name__ == "__main__":
    main()
