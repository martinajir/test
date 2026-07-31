"""Simple script that adds and multiplies two numbers."""


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def multiply(a, b):
    """Return the product of a and b."""
    return a * b


def main():
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print(f"The sum of {a} and {b} is {add(a, b)}")
    print(f"The product of {a} and {b} is {multiply(a, b)}")


if __name__ == "__main__":
    main()
