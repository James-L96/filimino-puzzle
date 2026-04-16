from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/api/click", methods=["POST"])
def handle_click():
    """Handle a click event from the frontend."""
    data = request.get_json(silent=True) or {}
    return jsonify({
        "status": "success",
        "message": "Button was clicked!",
        "received_data": data
    }), 200


@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)