    """
    Creates a signed, append-only receipt and returns:
      { "artifact_sha", "event", "attestation": {chain_path, signature_b64, ...}, "ts" }
    """

from __future__ import annotations
import json
import os
import time
from typing import Any
from qi.ops.provenance import attest, merkle_chain  # requires pynacl

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
RECEIPTS_DIR = os.path.join(STATE, "provenance", "receipts")
os.makedirs(RECEIPTS_DIR, exist_ok=True)
def write_receipt(
    *,
    artifact_sha: str,
    event: str,  # "link_issued" | "download_redirect" | "view_ack"
    user_id: str | None,
    url: str | None,
    client_ip: str | None,
    user_agent: str | None,
    purpose: str | None = None,
    extras: dict[str, Any] | None = None,
    tag: str = "receipt",
) -> dict[str, Any]:

    ts = time.time()
    steps = [
        {
            "phase": "request",
            "ts": ts,
            "artifact_sha": artifact_sha,
            "user_id": user_id,
            "purpose": purpose,
        },
        {"phase": "link", "url": url, "client_ip": client_ip, "user_agent": user_agent},
        {"phase": "outcome", "event": event, "extras": extras or {}},
    ]
    chain = merkle_chain(steps)
    att = attest(chain, tag=tag)  # writes *.jsonl + *.att.json

    out = {
        "artifact_sha": artifact_sha,
        "event": event,
        "ts": ts,
        "attestation": {
            "chain_path": att.chain_path,
            "signature_b64": att.signature_b64,
            "public_key_b64": att.public_key_b64,
            "root_hash": att.root_hash,
        },
    }
    # Also append a flat JSONL record for quick scans
    log_path = os.path.join(RECEIPTS_DIR, f"{artifact_sha[:2]}_{int(ts)}.jsonl")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(out) + "\n")
    return out
