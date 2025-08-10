#!/usr/bin/env python3
"""
LUKHAS VeriFold Scanner API Server
Simple Flask server to handle verification requests from the PWA scanner
"""

import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from scanner_backend import ScannerBackend

app = Flask(__name__)
CORS(app)  # Enable CORS for PWA requests

# Initialize backend
scanner_backend = ScannerBackend()


@app.route("/")
def index():
    """Serve the PWA"""
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    """Serve static files"""
    # CLAUDE_EDIT_v0.13: Fixed critical path traversal vulnerability
    import os

    # Sanitize the filename to prevent path traversal
    safe_filename = os.path.basename(filename)

    # Define allowed static file extensions
    allowed_extensions = {
        ".html",
        ".css",
        ".js",
        ".json",
        ".png",
        ".jpg",
        ".ico",
        ".svg",
    }

    # Check file extension
    _, ext = os.path.splitext(safe_filename)
    if ext.lower() not in allowed_extensions:
        abort(403)  # Forbidden

    # Ensure the file exists in the current directory only
    safe_path = os.path.join(".", safe_filename)
    if not os.path.exists(safe_path) or not os.path.isfile(safe_path):
        abort(404)  # Not found

    return send_from_directory(".", safe_filename)


@app.route("/api/verify", methods=["POST"])
def verify_qr_data():
    """Main verification endpoint"""
    try:
        data = request.get_json()

        if not data or "payload" not in data:
            return jsonify({"error": "No payload provided", "valid": False}), 400

        qr_data = data["payload"]
        result = scanner_backend.process_qr_data(qr_data)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}", "valid": False}), 500


@app.route("/api/lukhas-id/<lukhas_id>", methods=["GET"])
def verify_lucas_id(lukhas_id):
    """Direct Lukhas ID verification endpoint"""
    try:
        result = scanner_backend.verify_lucas_id(lukhas_id)
        return jsonify(result)
    except Exception as e:
        return (
            jsonify(
                {"error": f"Lukhas ID verification failed: {str(e)}", "valid": False}
            ),
            500,
        )


@app.route("/api/verifold/verify", methods=["POST"])
def verify_symbolic_memory():
    """VeriFold symbolic memory verification endpoint"""
    try:
        data = request.get_json()
        result = scanner_backend.verify_symbolic_memory(data)
        return jsonify(result)
    except Exception as e:
        return (
            jsonify(
                {
                    "error": f"Symbolic memory verification failed: {str(e)}",
                    "valid": False,
                }
            ),
            500,
        )


@app.route("/api/status", methods=["GET"])
def api_status():
    """API health check"""
    return jsonify(
        {
            "status": "online",
            "service": "LUKHAS VeriFold Scanner API",
            "version": "1.0.0",
            "endpoints": {
                "verify": "/api/verify",
                "identity_legacy": "/api/lukhas-id/<id>",
                "symbolic_memory": "/api/verifold/verify",
            },
        }
    )


if __name__ == "__main__":
    print("🧠 Starting LUKHAS VeriFold Scanner API Server...")
    print("📱 PWA available at: http://localhost:5000")
    print("🔗 API endpoints at: http://localhost:5000/api/")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
    )
