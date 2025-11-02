#!/usr/bin/env python3
import gzip, json, hashlib, hmac, os, time
from pathlib import Path
from typing import Any

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def write_snapshot(memory_state: Any, out_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    p = Path(out_path)
    payload = json.dumps(memory_state, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    gz = gzip.compress(payload)
    sha = hashlib.sha256(gz).hexdigest()
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError(f"Missing signing key: {key_env}")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    p.with_suffix(".gz").write_bytes(gz)
    meta = {"sha256": sha, "sig": sig, "timestamp": now_iso()}
    p.with_suffix(".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return meta

def verify_snapshot(gz_path: str, key_env: str = "WAVEC_SIGN_KEY"):
    gz = Path(gz_path).read_bytes()
    sha = hashlib.sha256(gz).hexdigest()
    meta_p = Path(gz_path).with_suffix(".meta.json")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    if meta["sha256"] != sha:
        raise RuntimeError("Snapshot SHA mismatch")
    key = os.environ.get(key_env)
    if not key:
        raise RuntimeError("Missing signing key")
    sig = hmac.new(key.encode("utf-8"), gz, hashlib.sha256).hexdigest()
    if sig != meta["sig"]:
        raise RuntimeError("Signature mismatch")
    return True
