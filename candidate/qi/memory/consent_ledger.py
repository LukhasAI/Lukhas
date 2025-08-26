# path: qi/memory/consent_ledger.py
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
LEDGER_DIR = os.path.join(STATE, "consent")
RECS = os.path.join(LEDGER_DIR, "consent_ledger.jsonl")
IDX  = os.path.join(LEDGER_DIR, "consent_index.json")  # quick lookups (user->purpose->latest)
os.makedirs(LEDGER_DIR, exist_ok=True)

# Optional fan-out
WEBHOOK_URL = os.environ.get("CONSENT_WEBHOOK_URL")         # e.g., https://audit.yourapp/consent
KAFKA_BROKERS = os.environ.get("CONSENT_KAFKA_BROKERS")     # e.g., localhost:9092
KAFKA_TOPIC   = os.environ.get("CONSENT_KAFKA_TOPIC")       # e.g., lukhas.consent.events

# Reuse Merkle + ed25519 attestation from provenance
_HAS_ATTEST = True
try:
    from qi.ops.provenance import attest, merkle_chain  # pip install pynacl
except Exception:
    _HAS_ATTEST = False

@dataclass
class ConsentEvent:
    ts: float
    user: str
    purpose: str
    kind: str                     # "grant" | "revoke"
    fields: List[str]
    duration_days: int
    meta: Dict[str, Any]
    receipt: Dict[str, Any]       # attestation pointers (chain_path, signature, etc.)
    event_id: str                 # deterministic id (sha256)

def _sha(d: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(",",":")).encode("utf-8")).hexdigest()

def _read_index() -> Dict[str, Dict[str, Dict[str, Any]]]:
    try:
        return json.load(open(IDX, encoding="utf-8"))
    except Exception:
        return {}

def _write_index(ix: Dict[str, Any]) -> None:
    tmp = IDX + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ix, f, indent=2)
    os.replace(tmp, IDX)

def _fanout(evt: ConsentEvent) -> None:
    # Best-effort: webhook then Kafka
    if WEBHOOK_URL:
        try:
            import requests  # pip install requests
            requests.post(WEBHOOK_URL, json=asdict(evt), timeout=2)
        except Exception:
            pass
    if KAFKA_BROKERS and KAFKA_TOPIC:
        try:
            from kafka import KafkaProducer  # pip install kafka-python
            prod = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS.split(","),
                acks="all",
                linger_ms=50,
                value_serializer=lambda d: json.dumps(d).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8"),
            )
            prod.send(KAFKA_TOPIC, key=evt.event_id, value=asdict(evt))
            prod.flush(2.0)
        except Exception:
            pass

def _sign_receipt(grant: Dict[str, Any]) -> Dict[str, Any]:
    if not _HAS_ATTEST:
        return {"note": "attestation disabled (pynacl not installed)"}
    steps = [
        {"phase":"consent","op":grant["kind"],"user":grant["user"],"purpose":grant["purpose"]},
        {"phase":"details","fields":grant["fields"],"duration_days":grant["duration_days"]},
        {"phase":"meta","meta":grant.get("meta",{})}
    ]
    ch = merkle_chain(steps)
    at = attest(ch, tag="consent")
    return {
        "chain_path": at.chain_path,
        "signature_b64": at.signature_b64,
        "public_key_b64": at.public_key_b64,
        "root_hash": at.root_hash
    }

def _append_event(evt: ConsentEvent) -> None:
    with open(RECS, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(evt)) + "\n")

def record(user: str, purpose: str, fields: List[str], duration_days: int, meta: Optional[Dict[str,Any]] = None) -> ConsentEvent:
    now = time.time()
    grant = {"ts": now, "user": user, "purpose": purpose, "kind":"grant",
             "fields": sorted(set(fields)), "duration_days": int(duration_days), "meta": meta or {}}
    receipt = _sign_receipt(grant)
    event_id = _sha({"u":user,"p":purpose,"k":"g","t":int(now)})
    evt = ConsentEvent(ts=now, user=user, purpose=purpose, kind="grant",
                       fields=grant["fields"], duration_days=grant["duration_days"],
                       meta=grant["meta"], receipt=receipt, event_id=event_id)
    _append_event(evt)
    # update index
    ix = _read_index()
    ix.setdefault(user, {}).setdefault(purpose, {})
    ix[user][purpose] = {"ts": now, "fields": evt.fields, "duration_days": evt.duration_days, "meta": evt.meta}
    _write_index(ix)
    _fanout(evt)
    return evt

def revoke(user: str, purpose: Optional[str] = None, reason: Optional[str] = None, meta: Optional[Dict[str,Any]] = None) -> ConsentEvent:
    now = time.time()
    p = purpose or "ALL"
    rec = {"ts": now, "user": user, "purpose": p, "kind":"revoke",
           "fields": [], "duration_days": 0, "meta": {"reason":reason or "", **(meta or {})}}
    receipt = _sign_receipt(rec)
    event_id = _sha({"u":user,"p":p,"k":"r","t":int(now)})
    evt = ConsentEvent(ts=now, user=user, purpose=p, kind="revoke",
                       fields=[], duration_days=0, meta=rec["meta"], receipt=receipt, event_id=event_id)
    _append_event(evt)
    # update index
    ix = _read_index()
    if p == "ALL":
        ix[user] = {}
    else:
        ix.setdefault(user, {}).pop(p, None)
    _write_index(ix)
    _fanout(evt)
    return evt

def is_allowed(user: str, purpose: str, *, require_fields: Optional[List[str]] = None, now: Optional[float] = None, within_days: Optional[int] = None) -> bool:
    """
    Returns True if there is a non-revoked, non-expired consent for user+purpose.
    - require_fields: if set, the granted fields must be a superset.
    - within_days: if set, consent must be newer than now - within_days.
    """
    ix = _read_index()
    ent = ix.get(user, {}).get(purpose)
    if not ent:
        return False
    now = now or time.time()
    ttl = float(ent.get("duration_days", 0)) * 86400
    if ttl <= 0:
        return False
    if (now - float(ent.get("ts", 0))) > ttl:
        return False
    if within_days is not None:
        if (now - float(ent.get("ts", 0))) > (within_days * 86400):
            return False
    if require_fields:
        fields = set(ent.get("fields", []))
        if not set(require_fields).issubset(fields):
            return False
    return True

def list_user(user: str) -> Dict[str, Any]:
    return _read_index().get(user, {})

# ---------------- CLI ----------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas Consent Ledger (signed receipts + fan-out)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("grant")
    p1.add_argument("--user", required=True)
    p1.add_argument("--purpose", required=True)
    p1.add_argument("--fields", nargs="+", default=[])
    p1.add_argument("--days", type=int, default=365)

    p2 = sub.add_parser("revoke")
    p2.add_argument("--user", required=True)
    p2.add_argument("--purpose")
    p2.add_argument("--reason")

    p3 = sub.add_parser("check")
    p3.add_argument("--user", required=True)
    p3.add_argument("--purpose", required=True)
    p3.add_argument("--need-fields", nargs="*")
    p3.add_argument("--within-days", type=int)

    p4 = sub.add_parser("list")
    p4.add_argument("--user", required=True)

    args = ap.parse_args()
    if args.cmd == "grant":
        print(json.dumps(asdict(record(args.user, args.purpose, args.fields, args.days)), indent=2))
    elif args.cmd == "revoke":
        print(json.dumps(asdict(revoke(args.user, args.purpose, args.reason)), indent=2))
    elif args.cmd == "check":
        ok = is_allowed(args.user, args.purpose, require_fields=args.need_fields, within_days=args.within_days)
        print(json.dumps({"allowed": ok}, indent=2))
        raise SystemExit(0 if ok else 2)
    else:
        print(json.dumps(list_user(args.user), indent=2))

if __name__ == "__main__":
    main()
