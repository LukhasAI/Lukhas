import json
import os
import threading
from pathlib import Path
from typing import Any, Optional
import streamlit as st

_AUDIT_LOCK = threading.Lock()
_AUDIT_DIR = Path(os.getenv("LUKHAS_AUDIT_DIR", ".lukhas_audit"))
_AUDIT_FILE = _AUDIT_DIR / "audit.jsonl"
_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
_AUDIT_FILE.touch(exist_ok=True)


def audit_log_write(bundle: dict[str, Any]) -> None:
    """
    Append a single audit bundle as one JSON line.
    Bundle must include a unique 'audit_id'.
    """
    if "audit_id" not in bundle:
        raise ValueError("audit bundle missing 'audit_id'")
    # Redact anything dangerous; keep it server-safe
    bundle = _redact(bundle)
    line = json.dumps(bundle, ensure_ascii=False)
    with _AUDIT_LOCK, _AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def audit_log_read(audit_id: str) -> Optional[dict[str, Any]]:
    """
    Scan JSONL for the most recent bundle with matching audit_id.
    """
    with _AUDIT_LOCK, _AUDIT_FILE.open("r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            try:
                obj = json.loads(line)
                if obj.get("audit_id") == audit_id:
                    return obj
            except Exception:
                continue
    return None


REDACT_KEYS = {"api_key", "token", "authorization", "email", "phone", "pii"}


def _redact(obj):
    # Shallow redaction for known keys; extend as needed
    if isinstance(obj, dict):
        return {k: ("[REDACTED]" if k.lower() in REDACT_KEYS else _redact(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj
