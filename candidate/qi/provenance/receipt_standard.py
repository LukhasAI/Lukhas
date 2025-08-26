# path: qi/provenance/receipt_standard.py
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

# Merkle + Ed25519 (same primitives you already use)
_HAS_PROV = True
try:
    from qi.ops.provenance import attest, merkle_chain  # writes *.jsonl + *.att.json
except Exception:
    _HAS_PROV = False

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _semantic_hash(vector: Optional[List[float]]) -> Optional[str]:
    if not vector:
        return None
    # simple stable hash (don't store vector by default)
    return _sha256(json.dumps([round(x, 6) for x in vector], separators=(",", ":"), ensure_ascii=False).encode())

@dataclass
class ProvEntity:
    id: str                    # "entity:artifact:<sha>"
    type: str                  # e.g., "artifact", "prompt", "model_output"
    digest_sha256: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    storage_url: Optional[str] = None

@dataclass
class ProvAgent:
    id: str                    # "agent:user:<id>", "agent:service:<name>"
    role: str                  # "user"|"service"|"system"
    meta: Dict[str, Any] = None

@dataclass
class ProvActivity:
    id: str                    # "activity:run:<run_id>"
    type: str                  # e.g., "generate_summary"
    started_at: float = 0.0
    ended_at: float = 0.0
    jurisdiction: Optional[str] = None
    context: Optional[str] = None

@dataclass
class Receipt:
    # W3C PROV core (flattened)
    entity: ProvEntity
    activity: ProvActivity
    agents: List[ProvAgent]

    # Policy & compliance replay pointers
    policy_decision_id: Optional[str] = None
    consent_receipt_id: Optional[str] = None
    capability_lease_ids: Optional[List[str]] = None

    # Risk & analytics
    risk_flags: List[str] = None
    embedding_hash: Optional[str] = None  # hash of semantic vector (no raw data)
    latency_ms: Optional[int] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None

    # Calibration & confidence metadata
    metrics: Optional[Dict[str, Any]] = None  # raw_conf, calibrated_conf, temperature, etc.

    # Integrity
    attestation: Optional[Dict[str, Any]] = None
    schema_version: str = "prov-1.0.0"
    created_at: float = 0.0
    id: str = ""  # stable id for sinks

def build_receipt(
    *,
    artifact_sha: str,
    artifact_mime: Optional[str],
    artifact_size: Optional[int],
    storage_url: Optional[str],
    run_id: str,
    task: str,
    started_at: float,
    ended_at: float,
    user_id: Optional[str],
    service_name: str = "lukhas",
    jurisdiction: Optional[str] = None,
    context: Optional[str] = None,
    policy_decision_id: Optional[str] = None,
    consent_receipt_id: Optional[str] = None,
    capability_lease_ids: Optional[List[str]] = None,
    risk_flags: Optional[List[str]] = None,
    tokens_in: Optional[int] = None,
    tokens_out: Optional[int] = None,
    embedding_vector: Optional[List[float]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    extra_steps: Optional[List[Dict[str, Any]]] = None,
) -> Receipt:
    created = time.time()
    entity = ProvEntity(
        id=f"entity:artifact:{artifact_sha}",
        type="artifact",
        digest_sha256=artifact_sha,
        mime_type=artifact_mime,
        size_bytes=artifact_size,
        storage_url=storage_url,
    )
    agents = []
    if user_id:
        agents.append(ProvAgent(id=f"agent:user:{user_id}", role="user", meta={}))
    agents.append(ProvAgent(id=f"agent:service:{service_name}", role="system", meta={}))

    act = ProvActivity(
        id=f"activity:run:{run_id}",
        type=task,
        started_at=started_at,
        ended_at=ended_at,
        jurisdiction=jurisdiction,
        context=context,
    )

    # Stable, privacy-safe receipt id
    rid = _sha256(json.dumps({
        "artifact": artifact_sha,
        "run": run_id,
        "task": task,
        "t": int(created)
    }, sort_keys=True, separators=(",", ":")).encode())

    # Optional signature (Merkle + ed25519)
    att: Optional[Dict[str, Any]] = None
    if _HAS_PROV:
        steps = [
            {"phase":"entity", "sha": artifact_sha, "mime": artifact_mime, "size": artifact_size},
            {"phase":"activity", "run_id": run_id, "task": task, "jurisdiction": jurisdiction, "context": context},
            {"phase":"agents", "agents": [a.id for a in agents]},
        ] + (extra_steps or [])
        ch = merkle_chain(steps)
        at = attest(ch, tag="receipt")
        att = {
            "chain_path": at.chain_path,
            "signature_b64": at.signature_b64,
            "public_key_b64": at.public_key_b64,
            "root_hash": at.root_hash,
        }

    return Receipt(
        entity=entity,
        activity=act,
        agents=agents,
        policy_decision_id=policy_decision_id,
        consent_receipt_id=consent_receipt_id,
        capability_lease_ids=capability_lease_ids or [],
        risk_flags=risk_flags or [],
        embedding_hash=_semantic_hash(embedding_vector),
        latency_ms=int((ended_at - started_at) * 1000) if ended_at and started_at else None,
        tokens_in=tokens_in, tokens_out=tokens_out,
        metrics=metrics,
        attestation=att,
        schema_version="prov-1.0.0",
        created_at=created,
        id=rid,
    )

def to_json(receipt: Receipt) -> Dict[str, Any]:
    d = asdict(receipt)
    # flatten dataclasses
    d["entity"] = asdict(receipt.entity)
    d["activity"] = asdict(receipt.activity)
    d["agents"] = [asdict(a) for a in receipt.agents]
    return d
