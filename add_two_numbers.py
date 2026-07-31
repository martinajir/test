"""Simple script that adds two numbers together."""


def add(a, b):
    """Return the sum of a and b."""
    return a + b


def main():
    a = float(input("Enter first number: "))
    b = float(input("Enter second number: "))
    print(f"The sum of {a} and {b} is {add(a, b)}")


if __name__ == "__main__":
    main()
