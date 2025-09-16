"""
Consent History Manager
======================

Immutable symbolic consent trails with time-stamped, hash-locked records.
Integrates with ΛTRACE for comprehensive audit logging.

Features:
- Immutable consent records
- Hash-chain verification
- ΛTRACE integration
- Symbolic representation
- Zero-knowledge proof support (future)
"""

from datetime import datetime, timezone
from typing import Optional
import hashlib


class ConsentHistoryManager:
    """Manage immutable consent history with symbolic trails"""

    def __init__(self, config, trace_logger=None):
        self.config = config
        self.trace_logger = trace_logger
        self.consent_chain = {}
        self.hash_algorithm = "sha256"

    def record_consent_event(self, user_id: str, event_type: str, scope_data: dict, metadata: dict) -> str:
        """Record a consent event in immutable history"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create consent record
        consent_record = {
            "user_id": user_id,
            "event_type": event_type,  # 'granted', 'revoked', 'updated'
            "scope_data": scope_data,
            "timestamp": timestamp,
            "metadata": metadata,
        }

        # Generate hash for chain integrity
        record_hash = self._generate_record_hash(consent_record, user_id)
        consent_record["hash"] = record_hash

        # Add to chain
        if user_id not in self.consent_chain:
            self.consent_chain[user_id] = []

        # Link to previous record
        if self.consent_chain[user_id]:
            consent_record["previous_hash"] = self.consent_chain[user_id][-1]["hash"]

        self.consent_chain[user_id].append(consent_record)

        # Log to ΛTRACE if available
        if self.trace_logger:
            self._log_to_trace(user_id, consent_record)

        return record_hash

    def _log_to_trace(self, user_id: str, record: dict) -> None:
        """Send consent record to ΛTRACE logger"""
        symbolic_data = {
            "hash": record.get("hash"),
            "event_type": record.get("event_type"),
            "scopes": list(record.get("scope_data", {}).keys()),
        }
        # ΛTAG: consent_audit
        # TODO: include previous_hash and metadata in trace context
        self.trace_logger.log_activity(user_id, f"consent_{record.get('event_type')}", symbolic_data)

    def _generate_record_hash(self, record: dict, user_id: str) -> str:
        """Generate cryptographic hash for consent record"""
        # Create deterministic string for hashing
        hash_input = f"{record['timestamp']}|{record['event_type']}|{record['scope_data']!s}|{user_id}"
        record_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        if self.trace_logger:
            symbolic_data = {
                "hash": record_hash,
                "event_type": record.get("event_type"),
                "scopes": list(record.get("scope_data", {}).keys()),
            }
            # ΛTAG: consent_trace
            # TODO: enrich symbolic_data with ΛTIER metadata
            self.trace_logger.log_activity(user_id, f"consent_{record.get('event_type')}", symbolic_data)

        return record_hash

    def verify_consent_chain(self, user_id: str) -> bool:
        """Verify integrity of user's consent chain"""
        if user_id not in self.consent_chain:
            return True  # Empty chain is valid

        chain = self.consent_chain[user_id]
        for i, record in enumerate(chain):
            # Verify hash integrity
            expected_hash = self._generate_record_hash(record, user_id)
            if record["hash"] != expected_hash:
                return False

            # Verify chain linkage
            if i > 0 and record.get("previous_hash") != chain[i - 1]["hash"]:
                return False

        return True

    def get_consent_timeline(self, user_id: str, scope: Optional[str] = None) -> list[dict]:
        """Get chronological consent timeline for user"""
        if user_id not in self.consent_chain:
            return []

        timeline = self.consent_chain[user_id].copy()

        # Filter by scope if specified
        if scope:
            timeline = [r for r in timeline if scope in r.get("scope_data", {})]

        return sorted(timeline, key=lambda x: x["timestamp"])

    def generate_consent_proof(self, user_id: str, scope: str, timestamp: Optional[str] = None) -> dict:
        """Generate cryptographic proof of consent status"""
        import hashlib
        import json
        from datetime import datetime, timezone

        # Basic proof structure (placeholder for full ZK implementation)
        proof_timestamp = timestamp or datetime.now(timezone.utc).isoformat()

        # Create proof components
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        scope_hash = hashlib.sha256(scope.encode()).hexdigest()[:16]
        proof_data = {
            "user_id": user_hash,  # Hashed for privacy
            "scope": scope_hash,  # Hashed for privacy
            "timestamp": proof_timestamp,
            "consent_exists": user_id in self.consent_history,
            "proof_version": "v1.0-basic",
        }

        # Generate proof signature (simplified)
        proof_content = json.dumps(proof_data, sort_keys=True)
        proof_signature = hashlib.sha256(proof_content.encode()).hexdigest()

        return {
            **proof_data,
            "proof_signature": proof_signature,
            "verification": "basic-hash-proof",  # Would be ZK proof in production
        }

    def get_symbolic_consent_history(self, user_id: str) -> str:
        """Generate symbolic representation of consent history"""
        if user_id not in self.consent_chain:
            return "🆕"  # New user symbol

        # Generate symbolic trail based on consent events
        symbols = []
        for record in self.consent_chain[user_id]:
            if record["event_type"] == "granted":
                symbols.append("✅")
            elif record["event_type"] == "revoked":
                symbols.append("❌")
            elif record["event_type"] == "updated":
                symbols.append("🔄")

        return "".join(symbols[-10:])  # Last 10 events
