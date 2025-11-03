import json
import os
from datetime import datetime, timezone
from pathlib import Path

# Simple witness chain anchoring mechanism
ANCHOR_LOG = Path(os.environ.get("LUKHAS_BLOCKCHAIN_ANCHOR", "anchor_log.json", timezone))


def anchor_hash(data_hash: str) -> str:
    """Anchor a data hash to the witness chain (simulated blockchain)."""
    tx = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_hash": data_hash,
    }
    anchors = json.loads(ANCHOR_LOG.read_text()) if ANCHOR_LOG.exists() else []
    anchors.append(tx)
    ANCHOR_LOG.write_text(json.dumps(anchors, indent=2))
    return tx["timestamp"]
