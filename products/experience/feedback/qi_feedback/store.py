# path: qi/feedback/store.py
from __future__ import annotations

# Use native file operations
import builtins
import fcntl  # For file locking
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any
from datetime import timezone
import streamlit as st
from consciousness.qi import qi

_ORIG_OPEN = builtins.open

# Storage paths
STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state", timezone))
FEEDBACK_DIR = os.path.join(STATE, "feedback")
FEEDBACK_FILE = os.path.join(FEEDBACK_DIR, "feedback.jsonl")
CLUSTERS_FILE = os.path.join(FEEDBACK_DIR, "clusters.json")
DIGESTS_DIR = os.path.join(FEEDBACK_DIR, "digests")

# Create directories
os.makedirs(FEEDBACK_DIR, exist_ok=True)
os.makedirs(DIGESTS_DIR, exist_ok=True)


class FeedbackStore:
    """JSONL storage with HMAC redaction and Merkle tree generation."""

    def __init__(self):
        self.feedback_file = FEEDBACK_FILE
        self.clusters_file = CLUSTERS_FILE
        self.digests_dir = DIGESTS_DIR
        self._hmac_key = self._derive_hmac_key()

    def _derive_hmac_key(self) -> bytes:
        """Derive weekly HMAC key using HKDF-like derivation."""
        # Get week number for key rotation
        week_num = datetime.now(timezone.utc).isocalendar()[1]
        year = datetime.now(timezone.utc).year

        # Base secret from environment or generate
        base_secret = os.environ.get("FEEDBACK_HMAC_SECRET", "lukhas-feedback-v1")

        # Derive weekly key
        key_material = f"{base_secret}:{year}:week{week_num}".encode()
        return hashlib.sha3_256(key_material).digest()

    def hmac_id(self, value: str) -> str:
        """Generate HMAC SHA3-512 of value."""
        h = hmac.new(self._hmac_key, value.encode(), hashlib.sha3_512)
        return f"hmac_sha3_512:{h.hexdigest(}"

    def append_feedback(self, feedback_data: dict[str, Any]) -> str:
        """Append feedback to JSONL with fsync."""
        # Apply HMAC redaction
        if "user_id" in feedback_data:
            feedback_data["user_hash"] = self.hmac_id(feedback_data.pop("user_id"))
        if "session_id" in feedback_data:
            feedback_data["session_hash"] = self.hmac_id(feedback_data.pop("session_id"))
        if "note" in feedback_data.get("feedback", {}):
            note = feedback_data["feedback"].pop("note")
            feedback_data["feedback"]["note_hash"] = self.hmac_id(note) if note else None

        # Write with lock and fsync
        with _ORIG_OPEN(self.feedback_file, "a", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(feedback_data, f, separators=(",", ":"))
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return feedback_data.get("fc_id", "unknown")

    def read_feedback(
        self,
        limit: int | None = None,
        task_filter: str | None = None,
        jurisdiction_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Read feedback from jsonl_with optional filters."""
        if not os.path.exists(self.feedback_file):
            return []

        feedback = []
        with _ORIG_OPEN(self.feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    fc = json.loads(line)

                    # Apply filters
                    if task_filter and fc.get("context", {}).get("task") != task_filter:
                        continue
                    if jurisdiction_filter and fc.get("context", {}).get("jurisdiction") != jurisdiction_filter:
                        continue

                    feedback.append(fc)

                    if limit and len(feedback) >= limit:
                        break
                except json.JSONDecodeError:
                    continue

        # Return in reverse chronological order
        return list(reversed(feedback))

    def write_clusters(self, clusters: list[dict[str, Any]]):
        """Write clusters to JSON file."""
        with _ORIG_OPEN(self.clusters_file, "w", encoding="utf-8") as f:
            json.dump({"clusters": clusters, "generated_at": time.time()}, f, indent=2)

    def read_clusters(self) -> list[dict[str, Any]]:
        """Read clusters from json_file."""
        if not os.path.exists(self.clusters_file):
            return []

        with _ORIG_OPEN(self.clusters_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("clusters", [])

    def build_merkle_tree(self, records: list[dict[str, Any]]) -> str:
        """Build Merkle tree from records and return root hash."""
        if not records:
            return hashlib.sha3_512(b"empty").hexdigest()

        # Leaf hashes
        hashes = []
        for record in records:
            # Canonical JSON for consistent hashing
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
            leaf_hash = hashlib.sha3_512(canonical.encode()).hexdigest()
            hashes.append(leaf_hash)

        # Build tree bottom-up
        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i + 1]
                else:
                    combined = hashes[i] + hashes[i]  # Duplicate last if odd
                parent_hash = hashlib.sha3_512(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            hashes = next_level

        return hashes[0]

    def generate_weekly_digest(self) -> dict[str, Any]:
        """Generate weekly Merkle digest with signature."""
        # Get current week
        now = datetime.now(timezone.utc)
        year, week, _ = now.isocalendar()
        week_str = f"{year}-W{week:02d}"

        # Read all feedback for this week
        week_start = now - timedelta(days=now.weekday())
        week_feedback = []

        with _ORIG_OPEN(self.feedback_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    fc = json.loads(line)
                    fc_time = datetime.fromisoformat(fc.get("ts", "").replace("Z", ""))
                    if fc_time >= week_start:
                        week_feedback.append(fc)
                except (json.JSONDecodeError, ValueError):
                    continue

        # Build Merkle tree
        merkle_root = self.build_merkle_tree(week_feedback)

        # Create digest
        digest = {
            "week": week_str,
            "file": self.feedback_file,
            "merkle_root": merkle_root,
            "n_records": len(week_feedback),
            "generated_at": now.isoformat() + "Z",
            "alg": "merkle_sha3_512",
            "signer": "development",  # Will be replaced with PQC signer
        }

        # Save digest
        digest_file = os.path.join(self.digests_dir, f"{week_str}.json")
        with _ORIG_OPEN(digest_file, "w", encoding="utf-8") as f:
            json.dump(digest, f, indent=2)

        return digest


# Singleton instance
_store = None


def get_store() -> FeedbackStore:
    """Get singleton store instance."""
    global _store
    if _store is None:
        _store = FeedbackStore()
    return _store
