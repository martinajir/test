"""Simple script that adds two numbers together."""


def add(a, b):
    """Return the sum of a and b."""
    return a + b


if __name__ == "__main__":
    num1 = 3
    num2 = 5
    result = add(num1, num2)
    print(f"{num1} + {num2} = {result}")
