import unittest

from add_numbers import add


class AddTests(unittest.TestCase):
    def test_adds_integers(self):
        self.assertEqual(add(2, 3), 5)

    def test_adds_floating_point_numbers(self):
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)

    def test_adds_negative_numbers(self):
        self.assertEqual(add(-4, -6), -10)

    def test_concatenates_strings(self):
        self.assertEqual(add("copilot", " test"), "copilot test")


if __name__ == "__main__":
    unittest.main()
