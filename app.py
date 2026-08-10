#!/usr/bin/env python3
"""A simple Flask web server for the test repo.

Exposes a few small endpoints that reuse the existing scratch-space
content in this repository (adding numbers, pirate jokes).
"""

import random

from flask import Flask, jsonify, request

from add_numbers import add

app = Flask(__name__)

JOKES_FILE = "pirate-jokes.txt"


def load_jokes():
    """Parse numbered jokes out of pirate-jokes.txt."""
    jokes = []
    with open(JOKES_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and line[0].isdigit() and "." in line:
                jokes.append(line.split(".", 1)[1].strip())
    return jokes


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Welcome to the test repo web server!",
            "endpoints": {
                "GET /": "This message",
                "GET /add?a=<num>&b=<num>": "Add two numbers",
                "GET /joke": "Get a random pirate joke",
                "GET /health": "Health check",
            },
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/add")
def add_route():
    try:
        a = float(request.args.get("a", ""))
        b = float(request.args.get("b", ""))
    except (TypeError, ValueError):
        return jsonify({"error": "Provide numeric query params 'a' and 'b'"}), 400
    return jsonify({"a": a, "b": b, "sum": add(a, b)})


@app.route("/joke")
def joke_route():
    jokes = load_jokes()
    if not jokes:
        return jsonify({"error": "No jokes found"}), 404
    return jsonify({"joke": random.choice(jokes)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
