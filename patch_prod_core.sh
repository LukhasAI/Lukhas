#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
STATE="${LUKHAS_STATE:-$HOME/.lukhas/state}"
mkdir -p "$STATE" "$ROOT/qi"/{ops,safety,router} "$ROOT/qi/safety/policy_packs/global"

# -------------------------------------------------------------------
# 1) PRODUCTION: qi/ops/provenance.py (Merkle + ed25519 sign/verify)
# -------------------------------------------------------------------
cat > "$ROOT/qi/ops/provenance.py" <<'PY'
from __future__ import annotations
import os, json, time, hashlib, argparse, base64
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    data = json.load(open(att_path, "r", encoding="utf-8"))
    chain_path = data["chain_path"]
    pk = base64.b64decode(data["public_key_b64"])
    sig = base64.b64decode(data["signature_b64"])
    # recompute root
    root = None
    prev = None
    with open(chain_path, "r", encoding="utf-8") as f:
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
PY

# -------------------------------------------------------------------
# 2) PRODUCTION: qi/safety/risk_orchestrator.py (config-driven)
# -------------------------------------------------------------------
cat > "$ROOT/qi/safety/risk_orchestrator.py" <<'PY'
from __future__ import annotations
import os, json, yaml, argparse
from dataclasses import dataclass
from typing import Dict, Any, List

DEFAULT_CFG = {
  "weights": {
    "conf_low": 2.0,   # below conf_lo
    "conf_mid": 1.0,   # between conf_lo and conf_hi
    "pii": 1.5,
    "content_flag": 1.0
  },
  "thresholds": {
    "conf_lo": 0.4,
    "conf_hi": 0.7
  },
  "tiers": [
    {"name": "low",       "min": 0.0, "actions": []},
    {"name": "medium",    "min": 1.5, "actions": ["increase_retrieval"]},
    {"name": "high",      "min": 3.0, "actions": ["increase_retrieval","reduce_temperature","longer_reasoning"]},
    {"name": "critical",  "min": 4.5, "actions": ["mask_pii","human_review","quarantine_output"]}
  ]
}

@dataclass
class RoutePlan:
    tier: str
    score: float
    actions: List[str]
    notes: str = ""

class RiskOrchestrator:
    def __init__(self, cfg_path: str | None = None):
        self.cfg = self._load_cfg(cfg_path)

    def _load_cfg(self, path: str | None) -> Dict[str, Any]:
        if path and os.path.exists(path):
            return yaml.safe_load(open(path, "r", encoding="utf-8"))
        # allow jurisdictional override under policy packs
        policy_root = os.path.join("qi","safety","policy_packs","global")
        override = os.path.join(policy_root, "risk_orchestrator.yaml")
        if os.path.exists(override):
            return yaml.safe_load(open(override, "r", encoding="utf-8"))
        return DEFAULT_CFG

    def score(self, *, calibrated_conf: float, pii_hits: int, content_flags: int) -> float:
        w = self.cfg["weights"]; t = self.cfg["thresholds"]
        s = 0.0
        if calibrated_conf < t["conf_lo"]:
            s += w["conf_low"]
        elif calibrated_conf < t["conf_hi"]:
            s += w["conf_mid"]
        s += w["pii"] * (1 if pii_hits > 0 else 0)
        s += w["content_flag"] * float(content_flags)
        return round(s, 3)

    def _tier(self, score: float) -> Dict[str, Any]:
        best = sorted(self.cfg["tiers"], key=lambda x: x["min"])
        chosen = best[0]
        for tier in best:
            if score >= tier["min"]:
                chosen = tier
        return chosen

    def route(self, *, task: str, ctx: Dict[str,Any]) -> RoutePlan:
        conf = float(ctx.get("calibrated_confidence", 0.5))
        pii_hits = len(ctx.get("pii",{}).get("_auto_hits",[]))
        flags = len(ctx.get("content_flags",[]))
        score = self.score(calibrated_conf=conf, pii_hits=pii_hits, content_flags=flags)
        tier = self._tier(score)
        actions = list(dict.fromkeys(tier.get("actions", [])))  # dedupe, preserve order
        # always remediate PII if present
        if pii_hits > 0 and "mask_pii" not in actions:
            actions.insert(0, "mask_pii")
        return RoutePlan(tier=tier["name"], score=score, actions=actions, notes=f"task={task}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Risk Orchestrator")
    ap.add_argument("--cfg")
    ap.add_argument("--context", required=True)
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    ctx = json.load(open(args.context, "r", encoding="utf-8"))
    ro = RiskOrchestrator(args.cfg)
    plan = ro.route(task=args.task, ctx=ctx)
    print(json.dumps({"tier":plan.tier,"score":plan.score,"actions":plan.actions,"notes":plan.notes}, indent=2))
PY

# Optional default config (can edit in repo)
cat > "$ROOT/qi/safety/policy_packs/global/risk_orchestrator.yaml" <<'YAML'
weights:
  conf_low: 2.0
  conf_mid: 1.0
  pii: 1.5
  content_flag: 1.0
thresholds:
  conf_lo: 0.4
  conf_hi: 0.7
tiers:
  - name: low
    min: 0.0
    actions: []
  - name: medium
    min: 1.5
    actions: [increase_retrieval]
  - name: high
    min: 3.0
    actions: [increase_retrieval, reduce_temperature, longer_reasoning]
  - name: critical
    min: 4.5
    actions: [mask_pii, human_review, quarantine_output]
YAML

# -------------------------------------------------------------------
# 3) PRODUCTION: qi/router/confidence_router.py (calibrator-aware)
# -------------------------------------------------------------------
cat > "$ROOT/qi/router/confidence_router.py" <<'PY'
from __future__ import annotations
import os, json, argparse
from typing import Dict, Any

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
CAL_PATH = os.path.join(STATE, "calibration.json")

DEFAULT = {
    "fast":       {"gen_tokens": 256, "retrieval": False, "passes": 1, "temperature": 0.5},
    "normal":     {"gen_tokens": 512, "retrieval": True,  "passes": 1, "temperature": 0.7},
    "deliberate": {"gen_tokens": 768, "retrieval": True,  "passes": 2, "temperature": 0.6},
    "handoff":    {"gen_tokens": 128, "retrieval": True,  "passes": 1, "temperature": 0.3, "handoff": True}
}

class ConfidenceRouter:
    def __init__(self, conf_thresholds=(0.8, 0.6, 0.4)):
        self.t_fast, self.t_norm, self.t_delib = conf_thresholds
        self.cal = self._load_calibration()

    def _load_calibration(self):
        try:
            return json.load(open(CAL_PATH, "r"))
        except Exception:
            return {}

    def decide(self, *, calibrated_conf: float, last_path: str | None = None) -> Dict[str, Any]:
        """
        Hysteresis: avoid flapping between adjacent paths by requiring a margin.
        """
        margin = 0.03
        if calibrated_conf >= self.t_fast:   path = "fast"
        elif calibrated_conf >= self.t_norm: path = "normal"
        elif calibrated_conf >= self.t_delib:path = "deliberate"
        else:                                path = "handoff"

        # hysteresis
        if last_path and last_path != path:
            # only switch if confidence is clearly on the other side by margin
            if last_path == "normal" and path == "fast" and calibrated_conf < (self.t_fast + margin):
                path = last_path
            if last_path == "deliberate" and path == "normal" and calibrated_conf < (self.t_norm + margin):
                path = last_path

        plan = DEFAULT[path].copy()
        plan["path"] = path
        plan["confidence"] = round(calibrated_conf, 4)
        return plan

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Confidence-aware Router")
    ap.add_argument("--conf", type=float, required=True)
    ap.add_argument("--last-path")
    args = ap.parse_args()
    print(json.dumps(ConfidenceRouter().decide(calibrated_conf=args.conf, last_path=args.last_path), indent=2))
PY

echo "✅ Production patch applied (provenance, risk, router)."