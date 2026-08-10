#!/usr/bin/env python3
"""A simple Flask web server for the test repo.

Exposes:
- GET  /            Homepage with links to available endpoints.
- GET  /add?a=1&b=2 Adds two numbers using the logic from add_numbers.py.
- GET  /joke        Returns a random pirate joke from pirate-jokes.txt.
"""

import random
from pathlib import Path

from flask import Flask, jsonify, request

from add_numbers import add

app = Flask(__name__)

JOKES_FILE = Path(__file__).parent / "pirate-jokes.txt"


def load_jokes():
    """Parse numbered joke lines out of pirate-jokes.txt."""
    jokes = []
    for line in JOKES_FILE.read_text().splitlines():
        line = line.strip()
        if line and line[0].isdigit() and "." in line:
            jokes.append(line.split(".", 1)[1].strip())
    return jokes


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the simple test web server!",
        "endpoints": {
            "/add?a=<number>&b=<number>": "Add two numbers together",
            "/joke": "Get a random pirate joke",
        },
    })


@app.route("/add")
def add_route():
    try:
        a = float(request.args.get("a", ""))
        b = float(request.args.get("b", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "Please provide numeric query params 'a' and 'b'"}), 400
    return jsonify({"a": a, "b": b, "sum": add(a, b)})


@app.route("/joke")
def joke_route():
    jokes = load_jokes()
    if not jokes:
        return jsonify({"error": "No jokes found"}), 404
    return jsonify({"joke": random.choice(jokes)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
