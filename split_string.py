#!/usr/bin/env python3
"""A simple script that splits a string by a delimiter."""

import sys


def split_string(text: str, delimiter: str = " ") -> list[str]:
    """Return the given string split by the delimiter."""
    return text.split(delimiter)


def main() -> None:
    if len(sys.argv) > 2:
        text = sys.argv[1]
        delimiter = sys.argv[2]
    elif len(sys.argv) > 1:
        text = sys.argv[1]
        delimiter = " "
    else:
        text = input("Enter a string to split: ")
        delimiter = input("Enter a delimiter (default is space): ") or " "

    print(split_string(text, delimiter))


if __name__ == "__main__":
    main()
