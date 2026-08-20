#!/usr/bin/env python3
"""Check whether a piece of text is a palindrome."""

import sys


def is_palindrome(text):
    """Return True when text reads the same forwards and backwards."""
    normalized = "".join(character.lower() for character in text if character.isalnum())
    return normalized == normalized[::-1]


def main():
    """Read text from the command line and report whether it is a palindrome."""
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Enter text: ")
    result = "is" if is_palindrome(text) else "is not"
    print(f'"{text}" {result} a palindrome.')


if __name__ == "__main__":
    main()
