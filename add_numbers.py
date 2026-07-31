"""A simple script that adds two numbers together."""


def add(a, b):
    """Return the sum of a and b."""
    return a + b


if __name__ == "__main__":
    x = float(input("Enter the first number: "))
    y = float(input("Enter the second number: "))
    print(f"The sum is: {add(x, y)}")
