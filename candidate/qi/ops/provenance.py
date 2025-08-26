from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
PROV_DIR = os.path.join(STATE, "prov"); os.makedirs(PROV_DIR, exist_ok=True)
KEY_DIR  = os.path.join(STATE, "keys"); os.makedirs(KEY_DIR, exist_ok=True)

# -- crypto (ed25519 via stdlib if 3.11+, else pure-Python fallback) --
try:
    # Python 3.11+ has hashlib.ed25519 via 'cryptography' binding only in some builds.
    # We'll try nacl first if available; else fall back to a tiny local impl.
    import nacl.signing as _nacl  # type: ignore
    _HAS_NACL = True
except Exception:
    _HAS_NACL = False

@dataclass
class Attestation:
    chain_path: str
    public_key_b64: str
    signature_b64: str
    root_hash: str

def _sha256_json(v: Any) -> str:
    b = json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",",":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def _file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def _safe_body(d: Dict[str, Any]) -> Dict[str, Any]:
    # Normalize and only keep serializable primitives (plus 'attachments' with file hashes)
    body = {}
    for k, v in d.items():
        if k == "attachments" and isinstance(v, list):
            # turn file paths into hashes
            files_h = []
            for p in v:
                try:
                    files_h.append({"path": os.path.basename(p), "sha256": _file_sha256(p)})
                except Exception:
                    files_h.append({"path": os.path.basename(str(p)), "sha256": None})
            body[k] = files_h
        else:
            try:
                json.dumps(v)
                body[k] = v
            except Exception:
                body[k] = str(v)
    return body

def merkle_chain(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create a simple hash-linked list. Each node: ts, body, prev, hash."""
    prev = None
    out: List[Dict[str, Any]] = []
    for s in steps:
        body = _safe_body(s)
        node = {"ts": round(time.time(), 6), "body": body, "prev": prev}
        # root hash committed over body + prev (if present)
        node["hash"] = _sha256_json({"body": body, "prev": prev})
        prev = node["hash"]
        out.append(node)
    return out

def _key_paths(tag: str) -> tuple[str, str]:
    # one key per tag family (e.g., "prod", "dev", "thesis")
    return (os.path.join(KEY_DIR, f"{tag}.sk"), os.path.join(KEY_DIR, f"{tag}.pk"))

def _ensure_keypair(tag: str) -> tuple[bytes, bytes]:
    sk_path, pk_path = _key_paths(tag)
    if os.path.exists(sk_path) and os.path.exists(pk_path):
        return open(sk_path,"rb").read(), open(pk_path,"rb").read()
    if not _HAS_NACL:
        raise RuntimeError("PyNaCl not available. Install: pip install pynacl")
    sk = _nacl.SigningKey.generate()
    pk = sk.verify_key
    open(sk_path,"wb").write(bytes(sk))
    open(pk_path,"wb").write(bytes(pk))
    return bytes(sk), bytes(pk)

def _load_keypair(tag: str) -> tuple[bytes, bytes]:
    sk_path, pk_path = _key_paths(tag)
    return open(sk_path,"rb").read(), open(pk_path,"rb").read()

def attest(chain: List[Dict[str, Any]], tag: str) -> Attestation:
    # write chain
    chain_path = os.path.join(PROV_DIR, f"{int(time.time())}_{tag}.jsonl")
    with open(chain_path, "w", encoding="utf-8") as f:
        for n in chain:
            f.write(json.dumps(n, ensure_ascii=False)+"\n")

    # sign root (last hash) with ed25519
    root_hash = chain[-1]["hash"] if chain else _sha256_json({"empty": True})
    sk_raw, pk_raw = _ensure_keypair(tag)
    if not _HAS_NACL:
        raise RuntimeError("PyNaCl required for signing.")

    signer = _nacl.SigningKey(sk_raw)
    sig = signer.sign(root_hash.encode("utf-8")).signature
    att = Attestation(
        chain_path=chain_path,
        public_key_b64=base64.b64encode(pk_raw).decode("ascii"),
        signature_b64=base64.b64encode(sig).decode("ascii"),
        root_hash=root_hash,
    )
    # store alongside
    with open(chain_path + ".att.json", "w", encoding="utf-8") as f:
        json.dump(att.__dict__, f, indent=2)
    return att

def verify(att_path: str) -> bool:
    data = json.load(open(att_path, encoding="utf-8"))
    chain_path = data["chain_path"]
    pk = base64.b64decode(data["public_key_b64"])
    sig = base64.b64decode(data["signature_b64"])
    # recompute root
    root = None
    prev = None
    with open(chain_path, encoding="utf-8") as f:
        for line in f:
            n = json.loads(line)
            if n.get("prev") != prev:
                return False
            expected = _sha256_json({"body": n["body"], "prev": n["prev"]})
            if n.get("hash") != expected:
                return False
            prev = n["hash"]; root = prev
    # verify signature
    if not _HAS_NACL:
        raise RuntimeError("PyNaCl required for verification.")
    _nacl.VerifyKey(pk).verify(root.encode("utf-8"), sig)
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Provenance (Merkle + ed25519)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("attest")
    p1.add_argument("--tag", required=True)
    p1.add_argument("--step", action="append", required=True, help="JSON dict per step")
    p2 = sub.add_parser("verify")
    p2.add_argument("--att", required=True, help="Path to *.att.json")
    args = ap.parse_args()

    if args.cmd == "attest":
        steps = [json.loads(s) for s in args.step]
        chain = merkle_chain(steps)
        att = attest(chain, args.tag)
        print(json.dumps(att.__dict__, indent=2))
    else:
        ok = verify(args.att)
        print(json.dumps({"verified": bool(ok)}, indent=2))
