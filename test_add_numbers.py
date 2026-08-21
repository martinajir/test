#!/usr/bin/env python3
"""Unit tests for add_numbers.py."""

import unittest

from add_numbers import add


class TestAdd(unittest.TestCase):
    def test_add_positive_numbers(self):
        self.assertEqual(add(2, 3), 5)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-2, -3), -5)

    def test_add_mixed_sign_numbers(self):
        self.assertEqual(add(-2, 3), 1)

    def test_add_floats(self):
        self.assertAlmostEqual(add(1.5, 2.25), 3.75)

    def test_add_zero(self):
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(5, 0), 5)


if __name__ == "__main__":
    unittest.main()
