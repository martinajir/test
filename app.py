#!/usr/bin/env python3
"""A simple Flask web server for the test repo.

Routes:
  /            Home page with links to available endpoints
  /joke        Returns a random pirate joke (GET)
  /add         Adds two numbers passed as query params `a` and `b` (GET)
  /healthz     Basic health check
"""

import random

from flask import Flask, jsonify, request

from add_numbers import add

app = Flask(__name__)

JOKES_FILE = "pirate-jokes.txt"


def load_jokes():
    """Parse pirate-jokes.txt into a list of joke strings."""
    jokes = []
    with open(JOKES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and line[0].isdigit() and "." in line:
                # Strip the leading "N. " numbering.
                jokes.append(line.split(".", 1)[1].strip())
    return jokes


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Ahoy! Welcome to the simple web server.",
            "endpoints": {
                "/joke": "Get a random pirate joke",
                "/add?a=<num>&b=<num>": "Add two numbers",
                "/healthz": "Health check",
            },
        }
    )


@app.route("/joke")
def joke():
    jokes = load_jokes()
    if not jokes:
        return jsonify({"error": "No jokes found"}), 404
    return jsonify({"joke": random.choice(jokes)})


@app.route("/add")
def add_route():
    a = request.args.get("a")
    b = request.args.get("b")
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b' query params"}), 400
    try:
        a, b = float(a), float(b)
    except ValueError:
        return jsonify({"error": "'a' and 'b' must be numbers"}), 400
    return jsonify({"a": a, "b": b, "sum": add(a, b)})


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
