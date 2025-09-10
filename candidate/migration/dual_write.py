from typing import Any, Optional

from lukhas.dna.interfaces import DNAWriteReceipt, HelixMemory
from lukhas.flags import is_enabled
from lukhas.migration.legacy_store import LegacyStore


def write_memory_dual(
    *,
    legacy: LegacyStore,
    dna: HelixMemory,
    key: str,
    value: Any,
    version: int,
    strength: float = 0.5,
    meta: Optional[dict] = None,
) -> dict[str, Any]:
    """
    Single entrypoint for writes during migration.
    - If FLAG_DNA_DUAL_WRITE=false: write legacy only
    - If true: write legacy + DNA (idempotent on version)
    Returns a dict summary for audit.
    """
    meta = meta or {}
    wrote_legacy = legacy.write(key, value, version=version, strength=strength, meta=meta)
    dna_receipt: Optional[DNAWriteReceipt] = None
    if is_enabled("dna_dual_write"):
        dna_receipt = dna.write(key, value, version=version, strength=strength, meta=meta)
    return {
        "legacy_upserted": wrote_legacy,
        "dna": (dna_receipt.__dict__ if dna_receipt else None),
    }