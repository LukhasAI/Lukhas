"""
Dream Recorder for NIAS system.
Provides dream recording and logging functionality.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional


class DreamRecorder:
    """
    Dream recording system for capturing and storing dream data.

    This class provides functionality to record, store, and retrieve
    dream messages and related metadata.
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the dream recorder.

        Args:
            log_file: Optional path to dream log file
        """
        self.log_file = log_file or "dream_log.json"
        self.logger = self._setup_logger()
        self.recorded_dreams = []
        self.session_id = self._generate_session_id()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for dream recording."""
        logger = logging.getLogger("DreamRecorder")
        logger.setLevel(logging.INFO)

        # Create file handler if not already exists
        if not logger.handlers:
            handler = logging.FileHandler("dream_recorder.log")
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

    def record_dream_message(
        self,
        dream_message: dict[str, Any],
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Record a dream message with context.

        Args:
            dream_message: Dictionary containing dream message data
            context: Optional context information

        Returns:
            Recording result
        """
        try:
            # Create dream record
            dream_record = {
                "id": f"dream_{len(self.recorded_dreams)} + 1}",  # noqa: invalid-syntax
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "dream_message": dream_message,
                "context": context or {},
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            }

            # Add to recorded dreams
            self.recorded_dreams.append(dream_record)

            # Log the recording
            self.logger.info(f"Recorded dream message: {dream_record['id']}")

            # Save to file if specified
            if self.log_file:
                self._save_to_file(dream_record)

            return {
                "success": True,
                "dream_id": dream_record["id"],
                "session_id": self.session_id,
                "recorded_at": dream_record["recorded_at"],
            }

        except Exception as e:
            self.logger.error(f"Failed to record dream message: {e!s}")
            return {"success": False, "error": str(e), "dream_id": None}

    def _save_to_file(self, dream_record: dict[str, Any]) -> None:
        """Save dream record to file."""
        try:
            # Load existing records if file exists
            if os.path.exists(self.log_file):
                with open(self.log_file, encoding="utf-8") as f:
                    existing_records = json.load(f)
                    if not isinstance(existing_records, list):
                        existing_records = []
            else:
                existing_records = []

            # Add new record
            existing_records.append(dream_record)

            # Save back to file
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(existing_records, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save dream record to file: {e!s}")

    def get_recorded_dreams(self, session_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get recorded dreams, optionally filtered by session.

        Args:
            session_id: Optional session ID to filter by

        Returns:
            List of dream records
        """
        if session_id:
            return [dream for dream in self.recorded_dreams if dream["session_id"] == session_id]
        else:
            return self.recorded_dreams.copy()

    def search_dreams(self, query: str, search_fields: Optional[list[str]] = None) -> list[dict[str, Any]]:
        """
        Search recorded dreams by query.

        Args:
            query: Search query string
            search_fields: Fields to search in

        Returns:
            List of matching dream records
        """
        search_fields = search_fields or ["dream_message", "context"]
        matching_dreams = []

        for dream in self.recorded_dreams:
            # Convert dream to string for searching
            dream_str = json.dumps(dream, default=str).lower()

            if query.lower() in dream_str:
                matching_dreams.append(dream)

        return matching_dreams

    def get_dream_stats(self) -> dict[str, Any]:
        """
        Get statistics about recorded dreams.

        Returns:
            Dictionary with dream statistics
        """
        if not self.recorded_dreams:
            return {
                "total_dreams": 0,
                "sessions": 0,
                "earliest_dream": None,
                "latest_dream": None,
            }

        # Calculate statistics
        sessions = {dream["session_id"] for dream in self.recorded_dreams}
        timestamps = [dream["timestamp"] for dream in self.recorded_dreams]

        return {
            "total_dreams": len(self.recorded_dreams),
            "sessions": len(sessions),
            "earliest_dream": min(timestamps),
            "latest_dream": max(timestamps),
            "current_session": self.session_id,
            "dreams_in_current_session": len([d for d in self.recorded_dreams if d["session_id"] == self.session_id]),
        }

    def clear_dreams(self, session_id: Optional[str] = None) -> dict[str, Any]:
        """
        Clear recorded dreams, optionally by session.

        Args:
            session_id: Optional session ID to clear

        Returns:
            Clear operation result
        """
        try:
            if session_id:
                # Clear specific session
                original_count = len(self.recorded_dreams)
                self.recorded_dreams = [d for d in self.recorded_dreams if d["session_id"] != session_id]
                cleared_count = original_count - len(self.recorded_dreams)

                self.logger.info(f"Cleared {cleared_count} dreams from session {session_id}")

                return {
                    "success": True,
                    "cleared_count": cleared_count,
                    "session_id": session_id,
                }
            else:
                # Clear all dreams
                cleared_count = len(self.recorded_dreams)
                self.recorded_dreams.clear()

                self.logger.info(f"Cleared all {cleared_count} dreams")

                return {
                    "success": True,
                    "cleared_count": cleared_count,
                    "session_id": None,
                }

        except Exception as e:
            self.logger.error(f"Failed to clear dreams: {e!s}")
            return {"success": False, "error": str(e), "cleared_count": 0}

    def export_dreams(self, output_file: str, format: str = "json") -> dict[str, Any]:
        """
        Export recorded dreams to file.

        Args:
            output_file: Output file path
            format: Export format (json, csv)

        Returns:
            Export result
        """
        try:
            if format.lower() == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(self.recorded_dreams, f, indent=2, ensure_ascii=False)
            elif format.lower() == "csv":
                # Simple CSV export
                import csv

                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    if self.recorded_dreams:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "id",
                                "session_id",
                                "timestamp",
                                "dream_message",
                                "context",
                            ],
                        )
                        writer.writeheader()
                        for dream in self.recorded_dreams:
                            # Flatten dream for CSV
                            row = {
                                "id": dream["id"],
                                "session_id": dream["session_id"],
                                "timestamp": dream["timestamp"],
                                "dream_message": json.dumps(dream["dream_message"]),
                                "context": json.dumps(dream["context"]),
                            }
                            writer.writerow(row)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported format: {format}",
                }

            self.logger.info(f"Exported {len(self.recorded_dreams)} dreams to {output_file}")

            return {
                "success": True,
                "exported_count": len(self.recorded_dreams),
                "output_file": output_file,
                "format": format,
            }

        except Exception as e:
            self.logger.error(f"Failed to export dreams: {e!s}")
            return {"success": False, "error": str(e), "exported_count": 0}


# Global dream recorder instance
_global_recorder = DreamRecorder()


def record_dream_message(dream_message: dict[str, Any], context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Convenience function to record a dream message using the global recorder.

    Args:
        dream_message: Dictionary containing dream message data
        context: Optional context information

    Returns:
        Recording result
    """
    return _global_recorder.record_dream_message(dream_message, context)


def get_dream_recorder() -> DreamRecorder:
    """
    Get the global dream recorder instance.

    Returns:
        Global dream recorder instance
    """
    return _global_recorder


def set_dream_recorder(recorder: DreamRecorder) -> None:
    """
    Set a new global dream recorder instance.

    Args:
        recorder: New dream recorder instance
    """
    global _global_recorder
    _global_recorder = recorder
