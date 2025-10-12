"""
Mock dream_log module
Temporary implementation - see MOCK_TRANSPARENCY_LOG.md
"""

import logging
from datetime import datetime, timezone


class DreamLog:
    """Mock DreamLog class"""

    def __init__(self, log_path=None):
        self.log_path = log_path
        self.logger = logging.getLogger("dream_log")
        self.entries = []

    def log_dream(self, dream_id, content, metadata=None):
        """Mock log_dream method"""
        entry = {
            "id": dream_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
            "metadata": metadata or {},
        }
        self.entries.append(entry)
        self.logger.info(f"Dream logged: {dream_id}")
        return entry

    def get_recent_dreams(self, count=10):
        """Mock get_recent_dreams method"""
        return self.entries[-count:]


# Global instance
dream_logger = DreamLog()
