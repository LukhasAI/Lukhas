#!/usr/bin/env python3
"""
MATRIZ Node Contract v1.0.0 - FROZEN INTERFACE
DO NOT MODIFY - This is the canonical interface for all MATRIZ nodes

Legacy implementations must adapt to this contract via shims.
Any changes require a new major version.

T4-Approved: Simple, typed, minimal contract for production AGI systems.

Golden Fixture Binding (T4):
- Golden input must serialize to MatrizMessage with fields:
  msg_id, ts (ISO-8601), lane, topic, glyph{id,kind,version,tags}, payload, guardian_token.
- Golden output must serialize from MatrizResult with fields:
  ok, reasons, payload, trace, guardian_log.
- topic must be one of ALLOWED_TOPICS and glyph.version must equal CONTRACT_VERSION.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID
from enum import Enum

import json
import hashlib
from typing import Literal, Tuple

CONTRACT_VERSION = "1.0.0"

__version__ = "1.0.0"


class Topic(Enum):
    CONTRADICTION = "contradiction"
    RESOURCE = "resource"
    TREND = "trend"
    BREAKTHROUGH = "breakthrough"


# Frozen ontology of allowed topics for v1.0.0
ALLOWED_TOPICS = {t.value for t in Topic}

# Lane typing (for static analyzers) and runtime constant
LANE = Literal["experimental", "candidate", "prod"]
LANES: Tuple[str, str, str] = ("experimental", "candidate", "prod")


@dataclass(frozen=True)
class GLYPH:
    """
    Immutable symbolic identity for LUKHAS consciousness technology

    Each GLYPH represents a unique symbolic entity in the MATRIZ ecosystem
    with complete provenance and governance tracking.
    """
    id: UUID
    kind: str  # "intent", "memory", "attention", "action", "decision", "awareness"
    version: str = CONTRACT_VERSION
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MatrizMessage:
    """
    Immutable message format for MATRIZ communication

    All communication between MATRIZ nodes uses this canonical format
    ensuring complete auditability and governance.
    """
    msg_id: UUID
    ts: datetime
    lane: LANE  # "experimental", "candidate", "prod"
    glyph: GLYPH
    payload: Dict[str, Any]
    topic: str  # one of ALLOWED_TOPICS
    guardian_token: str = ""  # Guardian system audit token
    idempotency_key: str | None = None  # optional stable idempotency key (defaults to str(msg_id))


@dataclass
class MatrizResult:
    """
    Mutable result structure with complete trace and audit

    Every MATRIZ operation returns this standardized result
    with explainability traces and Guardian audit logs.
    """
    ok: bool
    reasons: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    trace: Dict[str, Any] = field(default_factory=dict)
    guardian_log: List[str] = field(default_factory=list)


# --- Helper utilities (T4 micro-upgrades) ---

def canonical_json(obj: dict) -> str:
    """Deterministic, minimal JSON for hashing and auditing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def message_digest(msg: MatrizMessage) -> str:
    """SHA-256 of canonical MatrizMessage (structure-only; no secrets)."""
    as_dict = {
        "msg_id": str(msg.msg_id),
        "ts": msg.ts.isoformat(),
        "lane": msg.lane,
        "topic": msg.topic,
        "glyph": {
            "id": str(msg.glyph.id),
            "kind": msg.glyph.kind,
            "version": msg.glyph.version,
            "tags": msg.glyph.tags,
        },
        "payload": msg.payload,
        "guardian_token": msg.guardian_token,
        "idempotency_key": msg.idempotency_key or str(msg.msg_id),
    }
    return hashlib.sha256(canonical_json(as_dict).encode("utf-8")).hexdigest()

def is_jsonable(x: Any) -> bool:
    """Return True if x can be json.dumps()'d."""
    try:
        json.dumps(x)
        return True
    except Exception:
        return False

def to_dict(msg: MatrizMessage) -> Dict[str, Any]:
    """Serialize MatrizMessage to a JSON-ready dict."""
    return {
        "msg_id": str(msg.msg_id),
        "ts": msg.ts.isoformat(),
        "lane": msg.lane,
        "topic": msg.topic,
        "glyph": {
            "id": str(msg.glyph.id),
            "kind": msg.glyph.kind,
            "version": msg.glyph.version,
            "tags": msg.glyph.tags,
        },
        "payload": msg.payload,
        "guardian_token": msg.guardian_token,
        "idempotency_key": msg.idempotency_key,
    }

def from_dict(d: Dict[str, Any]) -> MatrizMessage:
    """Strict deserialization with contract enforcement for v1.0.0."""
    # Basic shape checks
    required = ["lane", "topic", "glyph", "payload"]
    for k in required:
        if k not in d:
            raise ValueError(f"Missing field: {k}")

    # Parse/validate IDs and timestamps if present
    msg_id = UUID(d["msg_id"]) if "msg_id" in d else UUID(int=0)
    ts = datetime.fromisoformat(d["ts"]) if "ts" in d else datetime.utcnow()

    lane = d["lane"]
    topic = d["topic"]
    glyph_d = d["glyph"]
    payload = d["payload"]
    guardian_token = d.get("guardian_token", "")

    # Construct GLYPH with version enforcement
    glyph = GLYPH(
        id=UUID(glyph_d["id"]),
        kind=glyph_d["kind"],
        version=glyph_d.get("version", CONTRACT_VERSION),
        tags=glyph_d.get("tags", {}),
    )

    msg = MatrizMessage(
        msg_id=msg_id,
        ts=ts,
        lane=lane,  # type: ignore[arg-type]  # validated below
        glyph=glyph,
        payload=payload,
        topic=topic,
        guardian_token=guardian_token,
        idempotency_key=d.get("idempotency_key"),
    )

    # Enforce contract (topics, lanes, glyph version)
    if not validate_message(msg):
        raise ValueError("Deserialized MatrizMessage failed contract validation")

    return msg


class MatrizNode:
    """
    Base class for all MATRIZ cognitive nodes

    Every cognitive node in the LUKHAS system must inherit from this
    class and implement the handle method.

    Contract Requirements:
    1. Must process input deterministically
    2. Must return complete MatrizResult with trace
    3. Must support Guardian system integration
    4. Must be pure function (no side effects)
    """

    name: str = "abstract-node"
    version: str = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        """
        Process a MATRIZ message and return a result

        Args:
            msg: Immutable MatrizMessage with GLYPH identity

        Returns:
            MatrizResult with payload, trace, and audit information

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError(
            f"Node {self.name} must implement handle() method"
        )


# Contract validation utilities
def validate_glyph(glyph: GLYPH) -> bool:
    """Validate GLYPH structure and required fields"""
    if not isinstance(glyph.id, UUID):
        return False
    if not glyph.kind or not isinstance(glyph.kind, str):
        return False
    if glyph.version != CONTRACT_VERSION:
        return False
    return True


def validate_message(msg: MatrizMessage) -> bool:
    """Validate MatrizMessage structure and contract compliance"""
    if not isinstance(msg.msg_id, UUID):
        return False
    if not isinstance(msg.ts, datetime):
        return False
    if msg.lane not in LANES:
        return False
    if not validate_glyph(msg.glyph):
        return False
    if not msg.topic or not isinstance(msg.topic, str):
        return False
    if msg.topic not in ALLOWED_TOPICS:
        return False
    # Normalize idempotency key
    if msg.idempotency_key is None:
        # ok to be None at construction; normalize callers to use digest or msg_id
        pass
    return True


def validate_result(result: MatrizResult) -> bool:
    """Validate MatrizResult structure and trace requirements"""
    if not isinstance(result.ok, bool):
        return False
    if not isinstance(result.reasons, list):
        return False
    if not isinstance(result.payload, dict):
        return False
    if not isinstance(result.trace, dict):
        return False
    if not (isinstance(result.guardian_log, list) and len(result.guardian_log) >= 1):
        return False
    if not is_jsonable(result.payload):
        return False
    return True


def validate_message_ex(msg: MatrizMessage) -> Tuple[bool, List[str]]:
    """Extended validation that returns (ok, reasons)."""
    reasons: List[str] = []
    if not isinstance(msg.msg_id, UUID): reasons.append("msg_id_type")
    if not isinstance(msg.ts, datetime): reasons.append("ts_type")
    if msg.lane not in LANES: reasons.append("lane_value")
    if not validate_glyph(msg.glyph): reasons.append("glyph_invalid")
    if not msg.topic or not isinstance(msg.topic, str): reasons.append("topic_type")
    elif msg.topic not in ALLOWED_TOPICS: reasons.append("topic_not_allowed")
    return (len(reasons) == 0, reasons)


def mk_guardian_token(node_name: str, lane: str, msg_id: UUID, epoch_ms: int | None = None) -> str:
    """Recommended Guardian token format for searchable audits."""
    if epoch_ms is None:
        epoch_ms = int(datetime.utcnow().timestamp() * 1000)
    return f"lukhas:{lane}:{node_name}:{str(msg_id)[:8]}:{epoch_ms}"


# Export all public interfaces
__all__ = [
    "GLYPH",
    "MatrizMessage",
    "MatrizResult",
    "MatrizNode",
    "validate_glyph",
    "validate_message",
    "validate_result",
    "CONTRACT_VERSION",
    "Topic",
    "ALLOWED_TOPICS",
    "LANE",
    "LANES",
    "canonical_json",
    "message_digest",
    "is_jsonable",
    "validate_message_ex",
    "to_dict",
    "from_dict",
    "mk_guardian_token",
]