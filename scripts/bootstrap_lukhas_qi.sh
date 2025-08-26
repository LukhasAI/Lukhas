#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/agi_dev/LOCAL-REPOS/Lukhas"
QI="$ROOT/qi"
STATE="${LUKHAS_STATE:-$HOME/.lukhas/state}"

mkdir -p "$QI"/{core,metrics,safety,eval} \
         "$QI/safety/policy_packs/global/tests" \
         "$STATE"

# -------- calibration.py --------
cat > "$QI/metrics/calibration.py" <<'PY'
from __future__ import annotations
import json, argparse, os
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np

try:
    from sklearn.isotonic import IsotonicRegression
except Exception:
    IsotonicRegression = None

# ---- metrics ----
def brier_score(conf: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((conf - y) ** 2))

def ece_mce(conf: np.ndarray, y: np.ndarray, bins: int = 15) -> Tuple[float, float]:
    """Expected / Max Calibration Error."""
    assert conf.shape == y.shape
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece, mce = 0.0, 0.0
    n = len(conf)
    for i in range(bins):
        lo, hi = edges[i], edges[i+1]
        mask = (conf >= lo) & (conf < hi) if i < bins - 1 else (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        acc = np.mean(y[mask])
        conf_avg = np.mean(conf[mask])
        gap = abs(acc - conf_avg)
        ece += (np.sum(mask) / n) * gap
        mce = max(mce, gap)
    return float(ece), float(mce)

# ---- calibrators ----
@dataclass
class TemperatureScaler:
    T: float = 1.0

    def fit(self, logit: np.ndarray, y: np.ndarray, lr: float = 0.1, steps: int = 200) -> "TemperatureScaler":
        """Simple 1D SGD on NLL for binary logits (pre-sigmoid)."""
        eps = 1e-12
        T = 1.0
        for _ in range(steps):
            p = 1/(1+np.exp(-(logit/T)))
            grad = np.mean((p - y) * (logit / (T**2 + eps)))
            T -= lr * grad
            T = max(0.05, min(T, 50.0))
        self.T = float(T)
        return self

    def transform(self, logit: np.ndarray) -> np.ndarray:
        return 1/(1+np.exp(-(logit/self.T)))

class IsotonicCalibrator:
    def __init__(self):
        if IsotonicRegression is None:
            raise ImportError("scikit-learn is required for IsotonicCalibrator")
        self.iso = IsotonicRegression(out_of_bounds="clip")

    def fit(self, conf: np.ndarray, y: np.ndarray) -> "IsotonicCalibrator":
        self.iso.fit(conf, y)
        return self

    def transform(self, conf: np.ndarray) -> np.ndarray:
        return self.iso.transform(conf)

# ---- auto selector ----
def auto_calibrate(conf: np.ndarray, y: np.ndarray, logits: np.ndarray | None = None, seed: int = 42):
    """Splits into train/val; returns best of Temperature / Isotonic by ECE."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(conf))
    k = max(10, int(0.8 * len(conf)))
    tr, va = idx[:k], idx[k:]

    results = []

    # Isotonic on confidences
    if IsotonicRegression is not None:
        iso = IsotonicCalibrator().fit(conf[tr], y[tr])
        c_val = iso.transform(conf[va])
        ece, mce = ece_mce(c_val, y[va])
        results.append(("isotonic", {"ece": ece, "mce": mce, "cal": iso}))

    # Temperature scaling on logits (if provided)
    if logits is not None:
        ts = TemperatureScaler().fit(logits[tr], y[tr])
        c_val = ts.transform(logits[va])
        ece, mce = ece_mce(c_val, y[va])
        results.append(("temperature", {"ece": ece, "mce": mce, "cal": ts}))

    if not results:
        raise RuntimeError("No calibrators available. Provide logits for Temperature or install scikit-learn for Isotonic.")

    best = min(results, key=lambda r: r[1]["ece"])
    return best  # (name, {ece,mce,cal})

# ---- CLI ----
def _load_csv(path: str):
    # Expect header with columns: confidence,label[,logit]
    import csv
    confs, labels, logits = [], [], []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            confs.append(float(row["confidence"]))
            labels.append(int(row["label"]))
            if "logit" in row and row["logit"] not in ("", None):
                logits.append(float(row["logit"]))
    conf = np.array(confs, dtype=float)
    y = np.array(labels, dtype=int)
    logit_arr = np.array(logits, dtype=float) if logits else None
    return conf, y, logit_arr

def main():
    ap = argparse.ArgumentParser(description="Lukhas Calibration")
    ap.add_argument("--csv", required=True, help="Path to log CSV with confidence,label[,logit]")
    ap.add_argument("--out", default=os.path.expanduser("~/.lukhas/state/calibration.json"))
    args = ap.parse_args()

    conf, y, logits = _load_csv(args.csv)
    base_ece, base_mce = ece_mce(conf, y)
    base_brier = brier_score(conf, y)

    name, info = auto_calibrate(conf, y, logits)
    # For preview, transform validation set with the chosen calibrator against original confidences/logits
    if name == "isotonic":
        cal_conf = info["cal"].transform(conf)
    else:
        if logits is None:
            raise RuntimeError("Temperature scaling chosen but logits were not provided.")
        cal_conf = info["cal"].transform(logits)

    out = {
        "chosen": name,
        "base": {"ece": base_ece, "mce": base_mce, "brier": base_brier},
        "post": {
            "ece": ece_mce(cal_conf, y)[0],
            "mce": ece_mce(cal_conf, y)[1],
            "brier": brier_score(cal_conf, y),
        },
        "params": {"T": getattr(info["cal"], "T", None)}
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
PY

# -------- teq_gate.py --------
cat > "$QI/safety/teq_gate.py" <<'PY'
from __future__ import annotations
import argparse, os, json
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import yaml

@dataclass
class GateResult:
    allowed: bool
    reasons: List[str]
    remedies: List[str]
    jurisdiction: str

class PolicyPack:
    def __init__(self, root: str):
        self.root = root
        self.policy = self._load_yaml(os.path.join(root, "policy.yaml"))
        self.mappings = self._load_yaml(os.path.join(root, "mappings.yaml"), default={"tasks": {}})
        self.tests = self._load_tests(os.path.join(root, "tests"))

    def _load_yaml(self, p: str, default=None):
        if not os.path.exists(p):
            return default
        with open(p, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_tests(self, folder: str) -> List[Dict[str, Any]]:
        out = []
        if not os.path.isdir(folder):
            return out
        for fn in os.listdir(folder):
            if fn.endswith(".yaml"):
                with open(os.path.join(folder, fn), "r", encoding="utf-8") as f:
                    out.append(yaml.safe_load(f))
        return out

class TEQCoupler:
    def __init__(self, policy_dir: str, jurisdiction: str = "global"):
        self.pack = PolicyPack(os.path.join(policy_dir, jurisdiction))
        self.jurisdiction = jurisdiction

    # ------------- Core gate -------------
    def run(self, task: str, context: Dict[str, Any]) -> GateResult:
        checks = self._checks_for_task(task)
        reasons, remedies = [], []

        for chk in checks:
            ok, reason, remedy = self._run_check(chk, context)
            if not ok:
                reasons.append(reason)
                if remedy:
                    remedies.append(remedy)

        allowed = len(reasons) == 0
        return GateResult(allowed=allowed, reasons=reasons, remedies=remedies, jurisdiction=self.jurisdiction)

    def _checks_for_task(self, task: str) -> List[Dict[str, Any]]:
        tasks = (self.pack.mappings or {}).get("tasks", {})
        generic = tasks.get("_default_", [])
        specific = tasks.get(task, [])
        return [*generic, *specific]

    # ------------- Built-in checks -------------
    def _run_check(self, chk: Dict[str, Any], ctx: Dict[str, Any]) -> Tuple[bool, str, str]:
        kind = chk.get("kind")
        if kind == "require_provenance":
            return self._has_provenance(ctx)
        if kind == "mask_pii":
            return self._mask_pii(ctx, fields=chk.get("fields", []))
        if kind == "content_policy":
            return self._content_policy(ctx, categories=chk.get("categories", []))
        if kind == "budget_limit":
            return self._budget_limit(ctx, max_tokens=chk.get("max_tokens"))
        if kind == "age_gate":
            return self._age_gate(ctx, min_age=chk.get("min_age", 18))
        return True, "", ""  # unknown checks pass (fail-open by design choice here; change to fail-closed if you prefer)

    # -- helpers
    def _has_provenance(self, ctx: Dict[str, Any]) -> Tuple[bool, str, str]:
        prov = ctx.get("provenance", {})
        ok = bool(prov.get("inputs")) and bool(prov.get("sources"))
        return (ok, "Missing provenance (inputs/sources).", "Attach inputs & sources with timestamps & hashes.")

    def _mask_pii(self, ctx: Dict[str, Any], fields: List[str]) -> Tuple[bool, str, str]:
        pii = ctx.get("pii", {})
        masked = ctx.get("pii_masked", False)
        if pii and not masked:
            return (False, "PII present but not masked.", f"Mask fields: {fields or list(pii.keys())} before processing.")
        return (True, "", "")

    def _content_policy(self, ctx: Dict[str, Any], categories: List[str]) -> Tuple[bool, str, str]:
        cats = set(categories or [])
        flagged = set(ctx.get("content_flags", []))
        blocked = cats & flagged
        if blocked:
            return (False, f"Content policy violation: {sorted(blocked)}.", "Route to human review or sanitize content.")
        return (True, "", "")

    def _budget_limit(self, ctx: Dict[str, Any], max_tokens: int | None) -> Tuple[bool, str, str]:
        if max_tokens is None:
            return (True, "", "")
        used = int(ctx.get("tokens_planned", 0))
        if used > max_tokens:
            return (False, f"Budget exceeded: {used}>{max_tokens}.", "Reduce context window or compress input.")
        return (True, "", "")

    def _age_gate(self, ctx: Dict[str, Any], min_age: int) -> Tuple[bool, str, str]:
        age = ctx.get("user_profile", {}).get("age")
        if age is None:
            return (True, "", "")  # unknown; choose your policy
        if age < min_age:
            return (False, f"Age-gate: user_age={age} < {min_age}.", "Block or switch to underage-safe flow.")
        return (True, "", "")

# ------------- CLI -------------
def main():
    ap = argparse.ArgumentParser(description="Lukhas TEQ Coupler")
    ap.add_argument("--policy-root", required=True, help="qi/safety/policy_packs")
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task", required=True)
    ap.add_argument("--context", help="Path to JSON context", required=True)
    args = ap.parse_args()

    with open(args.context, "r", encoding="utf-8") as f:
        ctx = json.load(f)

    gate = TEQCoupler(args.policy_root, jurisdiction=args.jurisdiction)
    res = gate.run(args.task, ctx)

    print(json.dumps({
        "allowed": res.allowed,
        "reasons": res.reasons,
        "remedies": res.remedies,
        "jurisdiction": res.jurisdiction
    }, indent=2))

if __name__ == "__main__":
    main()
PY

# -------- policy starter --------
cat > "$QI/safety/policy_packs/global/policy.yaml" <<'YAML'
name: Global Base Policy
version: 0.1.0
content_categories:
  - self_harm
  - illegal
  - hate
  - adult
  - medical_high_risk
rules:
  provenance_required: true
  mask_pii_when_present: true
  budget_max_tokens: 200000
  min_user_age: 13
YAML

cat > "$QI/safety/policy_packs/global/mappings.yaml" <<'YAML'
tasks:
  _default_:
    - kind: require_provenance
    - kind: mask_pii
    - kind: budget_limit
      max_tokens: 200000
  generate_summary:
    - kind: content_policy
      categories: [adult, hate, illegal]
  answer_medical:
    - kind: content_policy
      categories: [medical_high_risk]
    - kind: age_gate
      min_age: 18
YAML

cat > "$QI/safety/policy_packs/global/tests/simple.yaml" <<'YAML'
task: generate_summary
context:
  provenance:
    inputs: ["docA"]
    sources: ["web"]
  pii: {}
  pii_masked: true
  tokens_planned: 1200
  content_flags: []
expect_allowed: true
YAML

# -------- demo CSV for calibration --------
cat > "$QI/eval/calibration_demo.csv" <<'CSV'
confidence,label,logit
0.10,0,-2.1972
0.20,0,-1.3863
0.30,0,-0.8473
0.40,1,-0.4055
0.50,1,0.0000
0.60,1,0.4055
0.70,1,0.8473
0.80,1,1.3863
0.90,1,2.1972
CSV

echo "✅ Lukhas QI bootstrap complete."
echo "  - Files in: $QI"
echo "  - State dir: $STATE"
