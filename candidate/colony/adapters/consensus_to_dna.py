from typing import Any, Optional

from lukhas.colony.contracts import ConsensusResult
from lukhas.dna.interfaces import DNAWriteReceipt, HelixMemory
from lukhas.flags import is_enabled


def persist_consensus_to_dna(
    dna: HelixMemory,
    c: ConsensusResult,
    *,
    policy: Optional[dict[str, Any]] = None,
) -> DNAWriteReceipt:
    """
    Map a consensus decision into a DNA write with bounded strength, versioning,
    and optional dual-write / encryption guards via feature flags.
    """
    policy = policy or {}

    # Strength: blend consensus confidence and quorum fraction
    quorum_ratio = c.votes_for / max(1, c.votes_total)
    raw_strength = 0.4 + 0.5 * (0.5 * c.confidence + 0.5 * quorum_ratio)
    strength = max(0.1, min(1.0, policy.get("max_strength", 1.0) * raw_strength))

    # Optional privacy: encrypt personal payloads (placeholder toggle)
    value = c.decided_value
    if is_enabled("dna_encrypt_personal") and isinstance(value, dict) and value.get("_personal"):
        value = {"_enc": True, "blob": "[ENCRYPTED]"}

    # Optional dual-write is caller-side by design; we only write to DNA here
    meta = {
        "consensus": {
            "method": c.metadata.get("method", "majority"),
            "confidence": c.confidence,
            "votes_for": c.votes_for,
            "votes_total": c.votes_total,
        }
    }
    return dna.write(c.key, value, version=c.version, strength=strength, meta=meta)