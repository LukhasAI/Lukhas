# path: qi/metrics/calibration.py
from __future__ import annotations
import os, json, math, glob, time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple

# safe I/O
import builtins
_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
CAL_DIR = os.path.join(STATE, "calibration"); os.makedirs(CAL_DIR, exist_ok=True)
PARAMS_PATH = os.path.join(CAL_DIR, "calibration_params.json")

EVALDIR = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs")
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")

@dataclass
class CalibParams:
    fitted_at: float
    source: str           # "eval"|"receipts"
    bins: List[Dict[str, float]]  # reliability diagram
    ece: float
    temperature: float    # temperature scaling for logits/confidence
    min_conf_clip: float
    max_conf_clip: float

def _read_json(p: str) -> dict:
    with _ORIG_OPEN(p, "r", encoding="utf-8") as f: return json.load(f)

def _write_json(p: str, obj: Any):
    tmp = p + ".tmp"
    with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f: json.dump(obj, f, indent=2)
    os.replace(tmp, p)

def _collect_eval() -> List[Tuple[float, int]]:
    """Return list of (confidence, correct) from eval runs if available.
       For now assumes each task has 'score' in [0,1] and pass/fail."""
    files = sorted(glob.glob(os.path.join(EVALDIR, "eval_*.json")))
    out=[]
    for fp in files[-10:]:  # last 10 evals
        try:
            ev = _read_json(fp)
            for r in ev.get("results", []):
                conf = float(r.get("score", 0.0))
                correct = 1 if bool(r.get("pass", False)) else 0
                out.append((conf, correct))
        except Exception:
            continue
    return out

def _collect_receipts() -> List[Tuple[float, int]]:
    """Fallback: infer confidence from runtime metadata; requires your pipeline to log a 'confidence' field & correctness."""
    paths = sorted(glob.glob(os.path.join(RECDIR, "*.json")))
    out=[]
    for p in paths[-1000:]:
        try:
            r = _read_json(p)
            conf = float((r.get("metrics") or {}).get("confidence", 0.0))
            corr = (r.get("metrics") or {}).get("correct", None)
            if corr is None: continue
            out.append((conf, 1 if corr else 0))
        except Exception:
            continue
    return out

def reliability_diagram(samples: List[Tuple[float,int]], bins: int = 10):
    buckets = [ {"lower":i/bins, "upper":(i+1)/bins, "count":0, "acc":0.0, "conf":0.0 } for i in range(bins) ]
    for conf, corr in samples:
        c = min(max(conf, 0.0), 1.0)
        idx = min(int(c * bins), bins-1)
        b = buckets[idx]
        b["count"] += 1
        b["acc"] += corr
        b["conf"] += c
    # finalize
    diag=[]
    for b in buckets:
        if b["count"] == 0:
            diag.append({"lower":b["lower"], "upper":b["upper"], "acc": None, "conf": None, "count": 0})
        else:
            diag.append({"lower":b["lower"], "upper":b["upper"], "acc": b["acc"]/b["count"], "conf": b["conf"]/b["count"], "count": b["count"]})
    return diag

def expected_calibration_error(diag) -> float:
    total = sum(b["count"] for b in diag)
    if total == 0: return 0.0
    e = 0.0
    for b in diag:
        if b["count"] == 0: continue
        gap = abs((b["acc"] or 0.0) - (b["conf"] or 0.0))
        e += (b["count"]/total) * gap
    return float(round(e, 6))

def fit_temperature(samples: List[Tuple[float,int]]) -> float:
    """Simple 1D temperature on confidence → minimize logloss (Newton steps)."""
    if not samples: return 1.0
    T = 1.0
    for _ in range(50):
        grad = 0.0
        hess = 0.0
        for conf, corr in samples:
            c = min(max(conf, 1e-6), 1-1e-6)
            # inverse link approx: z = logit(c) = ln(c/(1-c))
            z = math.log(c/(1.0-c))
            zT = z / T
            p = 1.0/(1.0+math.exp(-zT))
            # dL/dT = (p - y)*(-z)/T^2
            grad += (p - corr) * (-z) / (T*T)
            # crude hessian approx
            hess += p*(1-p) * (z*z) / (T**4)
        if abs(hess) < 1e-9: break
        step = grad / hess
        T -= step
        T = max(0.2, min(5.0, T))
        if abs(step) < 1e-6: break
    return float(round(T, 6))

def fit_and_save(source_preference: str = "eval") -> CalibParams:
    samples = _collect_eval() if source_preference == "eval" else _collect_receipts()
    if not samples:
        # fallback to the other source
        samples = _collect_receipts() if source_preference == "eval" else _collect_eval()
        src = "receipts" if source_preference == "eval" else "eval"
    else:
        src = source_preference

    diag = reliability_diagram(samples)
    ece = expected_calibration_error(diag)
    T = fit_temperature(samples)
    params = CalibParams(
        fitted_at=time.time(), source=src, bins=diag, ece=ece,
        temperature=T, min_conf_clip=0.02, max_conf_clip=0.98
    )
    _write_json(PARAMS_PATH, asdict(params))
    return params

def load_params() -> Optional[CalibParams]:
    if not os.path.exists(PARAMS_PATH): return None
    j = _read_json(PARAMS_PATH)
    return CalibParams(**j)

def apply_calibration(conf: float, params: Optional[CalibParams] = None) -> float:
    p = params or load_params()
    if p is None: return conf
    c = min(max(conf, p.min_conf_clip), p.max_conf_clip)
    # temperature scaling with pre-logit / post-sigmoid
    z = math.log(c/(1.0-c))
    zT = z / (p.temperature if p.temperature else 1.0)
    out = 1.0/(1.0+math.exp(-zT))
    return float(max(0.0, min(1.0, out)))

# ------------- CLI -------------
def main():
    import argparse
    ap = argparse.ArgumentParser(description="Lukhas Uncertainty & Calibration Engine")
    ap.add_argument("--fit", action="store_true", help="Fit and save params (from eval by default)")
    ap.add_argument("--source", default="eval", choices=["eval","receipts"])
    ap.add_argument("--show", action="store_true", help="Print current params")
    ap.add_argument("--demo", action="store_true", help="Demo: fit + print ECE")
    args = ap.parse_args()

    if args.fit or args.demo:
        p = fit_and_save(args.source)
        print(json.dumps(asdict(p), indent=2))
        if not args.demo: return
    if args.show:
        p = load_params()
        print(json.dumps(asdict(p) if p else {"note":"no params"}, indent=2))

if __name__ == "__main__":
    main()