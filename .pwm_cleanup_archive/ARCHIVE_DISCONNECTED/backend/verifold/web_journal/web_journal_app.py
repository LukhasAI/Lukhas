"""
web_journal_app.py

VeriFold Web Journal - Interactive Symbolic Intelligence Interface
Beautiful web interface for viewing probabilistic observation narratives with GPT-4 integration.

Features:
- Scrollable timeline of quantum events
- Interactive emotion-colored glyphs
- Real-time GPT summarization
- Live updates from VeriFold logbook
- Responsive design with quantum-themed UI

Author: LUKHAS AGI Core
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Web framework imports
try:
    from flask import Flask, jsonify, render_template, request, websocket
    from flask_socketio import SocketIO, emit

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print(
        "Warning: Flask not available. Install with: pip install flask flask-socketio"
    )

# Import our journal system
try:
    import sys

    sys.path.append(str(Path(__file__).parent.parent))
    from journal_mode import (
        VeriFoldJournal,
        gpt_summarize,
        replay_chain,
        replay_with_gpt_summary,
    )

    JOURNAL_AVAILABLE = True
except ImportError:
    JOURNAL_AVAILABLE = False
    print(
        "Warning: Could not import journal_mode. Make sure it's in the parent directory."
    )


class VeriFoldWebJournal:
    """
    Web interface for VeriFold symbolic journal with real-time updates.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5001, debug: bool = True):
        """
        Initialize the web journal application.

        Args:
            host (str): Server host address
            port (int): Server port
            debug (bool): Debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug

        # Initialize Flask app if available
        if FLASK_AVAILABLE:
            self.app = Flask(
                __name__, template_folder="templates", static_folder="static"
            )
            self.app.secret_key = os.urandom(24)
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")
            self.setup_routes()
        else:
            self.app = None
            self.socketio = None

        # Initialize journal
        if JOURNAL_AVAILABLE:
            self.journal = VeriFoldJournal()
            self.logbook_path = Path("../verifold_logbook.jsonl")
        else:
            self.journal = None
            self.logbook_path = None

        # Cache for entries
        self.cached_entries = []
        self.last_update = 0

    def setup_routes(self):
        """Set up Flask routes for the web interface."""

        @self.app.route("/")
        def index():
            """Main journal interface."""
            return render_template("journal.html")

        @self.app.route("/api/entries")
        def get_entries():
            """Get journal entries as JSON."""
            entries = self.load_journal_entries()
            return jsonify(
                {
                    "entries": entries,
                    "total": len(entries),
                    "last_update": datetime.now().isoformat(),
                }
            )

        @self.app.route("/api/summary")
        def get_gpt_summary():
            """Get GPT-4 summary of recent entries."""
            limit = request.args.get("limit", 5, type=int)
            summary = self.generate_live_summary(limit)
            return jsonify(
                {"summary": summary, "timestamp": datetime.now().isoformat()}
            )

        @self.app.route("/api/refresh")
        def refresh_entries():
            """Force refresh of journal entries."""
            self.cached_entries = []
            entries = self.load_journal_entries()

            # Emit update to connected clients
            if self.socketio:
                self.socketio.emit(
                    "entries_updated",
                    {"entries": entries, "timestamp": datetime.now().isoformat()},
                )

            return jsonify({"status": "refreshed", "count": len(entries)})

        # WebSocket events
        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection."""
            print("Client connected to VeriFold Web Journal")
            entries = self.load_journal_entries()
            emit(
                "initial_entries",
                {"entries": entries, "timestamp": datetime.now().isoformat()},
            )

        @self.socketio.on("request_summary")
        def handle_summary_request(data):
            """Handle GPT summary request."""
            limit = data.get("limit", 5)
            summary = self.generate_live_summary(limit)
            emit(
                "summary_generated",
                {"summary": summary, "timestamp": datetime.now().isoformat()},
            )

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection."""
            print("Client disconnected from VeriFold Web Journal")

    def load_journal_entries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Load and format journal entries for web display.

        Args:
            limit (int): Maximum number of entries to load

        Returns:
            List[Dict]: Formatted journal entries
        """
        if not JOURNAL_AVAILABLE or not self.logbook_path.exists():
            return self._get_sample_entries()

        try:
            # Load entries from logbook
            with open(self.logbook_path) as f:
                lines = f.readlines()

            # Process recent entries
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            formatted_entries = []

            for i, line in enumerate(recent_lines):
                try:
                    record = json.loads(line.strip())
                    entry = self.journal.generate_journal_entry(record)

                    # Format for web display
                    formatted_entry = {
                        "id": f"entry_{entry.timestamp}_{i}",
                        "timestamp": entry.timestamp,
                        "formatted_time": datetime.fromtimestamp(
                            entry.timestamp
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "title": entry.title,
                        "narrative": entry.narrative,
                        "technical_summary": entry.technical_summary,
                        "emotion_tags": entry.emotion_tags,
                        "symbolic_meaning": entry.symbolic_meaning,
                        "hash_snippet": (
                            entry.related_hashes[0][:16] + "..."
                            if entry.related_hashes
                            else "unknown"
                        ),
                        "verified": record.get("verified", False),
                        "location": record.get("metadata", {}).get(
                            "location", "unknown"
                        ),
                        "measurement_type": record.get("metadata", {}).get(
                            "measurement_type", "unknown"
                        ),
                        "entropy_score": record.get("metadata", {}).get(
                            "entropy_score", 0.0
                        ),
                        "glyph_color": self._get_emotion_color(entry.emotion_tags),
                        "glyph_symbol": self._get_quantum_symbol(
                            record.get("metadata", {}).get(
                                "measurement_type", "unknown"
                            )
                        ),
                    }

                    formatted_entries.append(formatted_entry)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing entry: {e}")
                    continue

            self.cached_entries = formatted_entries
            return formatted_entries

        except (OSError, FileNotFoundError) as e:
            print(f"Error reading logbook: {e}")
            return self._get_sample_entries()

    def _get_sample_entries(self) -> List[Dict[str, Any]]:
        """Generate sample entries for demo purposes."""
        return [
            {
                "id": "sample_1",
                "timestamp": datetime.now().timestamp(),
                "formatted_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": "Quantum Whispers from the Digital Realm",
                "narrative": "In this moment of digital transcendence, the probabilistic observation crystallized into verification. The hash emerged from uncertainty, its signature validated with mathematical precision.",
                "technical_summary": "Hash verification completed successfully using SPHINCS+ post-quantum cryptography.",
                "emotion_tags": ["wonder", "transcendent", "quantum"],
                "symbolic_meaning": "The dance of light revealing hidden polarities",
                "hash_snippet": "demo1234abcd...",
                "verified": True,
                "location": "digital_lab",
                "measurement_type": "demo_measurement",
                "entropy_score": 8.5,
                "glyph_color": "#4CAF50",
                "glyph_symbol": "🌟",
            },
            {
                "id": "sample_2",
                "timestamp": datetime.now().timestamp() - 3600,
                "formatted_time": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "title": "The Measurement That Changed Everything",
                "narrative": "Through profound curiosity, the verification process unveiled truth. The quantum field yielded its secrets, cryptographically sealed and tamper-evident.",
                "technical_summary": "Quantum measurement processed with high entropy score.",
                "emotion_tags": ["curiosity", "profound", "mystery"],
                "symbolic_meaning": "Information transcending space and time",
                "hash_snippet": "demo5678efgh...",
                "verified": False,
                "location": "remote_lab",
                "measurement_type": "bell_state",
                "entropy_score": 7.2,
                "glyph_color": "#FF9800",
                "glyph_symbol": "🔮",
            },
        ]

    def _get_emotion_color(self, emotion_tags: List[str]) -> str:
        """
        Get color code based on emotion tags.

        Args:
            emotion_tags (List[str]): List of emotion tags

        Returns:
            str: Hex color code
        """
        color_map = {
            "wonder": "#9C27B0",  # Purple
            "excitement": "#F44336",  # Red
            "curiosity": "#2196F3",  # Blue
            "focus": "#4CAF50",  # Green
            "uncertainty": "#FF9800",  # Orange
            "transcendent": "#E91E63",  # Pink
            "quantum": "#00BCD4",  # Cyan
            "mystery": "#795548",  # Brown
        }

        # Return color for first recognized emotion, or default
        for tag in emotion_tags:
            if tag in color_map:
                return color_map[tag]

        return "#607D8B"  # Default blue-grey

    def _get_quantum_symbol(self, measurement_type: str) -> str:
        """
        Get quantum symbol based on measurement type.

        Args:
            measurement_type (str): Type of probabilistic observation

        Returns:
            str: Unicode symbol
        """
        symbol_map = {
            "photon_polarization": "💫",
            "electron_spin": "⚛️",
            "bell_state_measurement": "🔗",
            "quantum_teleportation": "🌀",
            "atom_interference": "🌊",
            "demo_measurement": "🌟",
            "unknown": "❓",
        }

        return symbol_map.get(measurement_type, "⚡")

    def generate_live_summary(self, limit: int = 5) -> str:
        """
        Generate live GPT summary of recent entries.

        Args:
            limit (int): Number of recent entries to summarize

        Returns:
            str: GPT-generated summary
        """
        if not JOURNAL_AVAILABLE:
            return "Journal system not available for live summarization."

        try:
            # Get symbolic entries
            symbolic_entries = replay_chain(str(self.logbook_path), limit)

            # Generate GPT summary
            summary = gpt_summarize(symbolic_entries)

            return summary

        except Exception as e:
            return f"Error generating summary: {e}"

    def run(self):
        """Start the web journal server."""
        if not FLASK_AVAILABLE:
            print(
                "❌ Flask not available. Install with: pip install flask flask-socketio"
            )
            return

        print("🌐 Starting VeriFold Web Journal...")
        print(f"📱 Interface: http://{self.host}:{self.port}")
        print(f"🔮 Real-time updates: {'Enabled' if self.socketio else 'Disabled'}")
        print(f"🧠 GPT Integration: {'Available' if JOURNAL_AVAILABLE else 'Limited'}")
        print("=" * 50)

        if self.socketio:
            self.socketio.run(
                self.app, host=self.host, port=self.port, debug=self.debug
            )
        else:
            self.app.run(host=self.host, port=self.port, debug=self.debug)


def main():
    """Main entry point for the web journal."""
    import argparse

    parser = argparse.ArgumentParser(description="VeriFold Web Journal Interface")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=5001, help="Server port")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Create and run web journal
    web_journal = VeriFoldWebJournal(host=args.host, port=args.port, debug=args.debug)

    web_journal.run()


if __name__ == "__main__":
    main()
