"""
Symbolic Entropy Observer for LUKHAS AGI system.

This module provides an observer for the symbolic entropy of the system.
"""

from typing import Dict, List
import json

#LUKHAS_TAG: symbolic_entropy
class SymbolicEntropyObserver:
    """
    The Symbolic Entropy Observer.
    """

    def __init__(self, log_file="symbolic_entropy_log.jsonl"):
        self.log_file = log_file

    def get_latest_entropy_snapshot(self) -> Dict:
        """
        Gets the latest entropy snapshot from the log file.

        Returns:
            A dictionary of the latest entropy snapshot.
        """
        latest_snapshot = {}
        latest_snapshot = {}
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        latest_snapshot = log_entry["entropy_snapshot"]
                    except json.JSONDecodeError:
                        logger.warning(f"Could not decode line in {self.log_file}: {line}")
        except FileNotFoundError:
            logger.warning(f"Log file not found: {self.log_file}")
        return latest_snapshot

    def get_entropy_history(self) -> List[Dict]:
        """
        Gets the entropy history from the log file.

        Returns:
            A list of entropy snapshots.
        """
        history = []
        with open(self.log_file, "r") as f:
            for line in f:
                log_entry = json.loads(line)
                history.append(log_entry["entropy_snapshot"])
        return history
