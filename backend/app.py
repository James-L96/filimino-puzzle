from flask import Flask, jsonify, request
from flask_cors import CORS

import generator as puzzle_generator
import solver

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

_puzzle_cache = {}


@app.route("/api/puzzle", methods=["GET"])
def get_puzzle():
    """Generate (or return cached) Fillomino puzzle.

    Query params: size (4-20, default 8), difficulty (easy/medium/hard,
    default medium), refresh=true to force a fresh puzzle.
    """
    size = request.args.get("size", default=8, type=int)
    difficulty = request.args.get("difficulty", default="medium")
    refresh = request.args.get("refresh", default="false").lower() in ("1", "true", "yes")

    key = (size, difficulty)
    if refresh or key not in _puzzle_cache:
        try:
            _puzzle_cache[key] = puzzle_generator.generate_puzzle(size, difficulty)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    puzzle = dict(_puzzle_cache[key])
    puzzle.pop("solution", None)
    return jsonify(puzzle), 200


@app.route("/api/check", methods=["POST"])
def check_solution():
    """Validate a fully filled grid. Body: {rows, cols, values (flat list)}."""
    data = request.get_json(silent=True) or {}
    rows, cols, values = data.get("rows"), data.get("cols"), data.get("values")

    if not isinstance(rows, int) or not isinstance(cols, int):
        return jsonify({"error": "Expected integer fields 'rows' and 'cols'"}), 400
    if not isinstance(values, list) or len(values) != rows * cols:
        return jsonify({"error": f"'values' must be a flat list of length {rows * cols}"}), 400

    solved = solver.is_valid_complete(values, rows, cols)
    return jsonify({"solved": solved}), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
