# path: qi/metrics/calibration.py
from __future__ import annotations

# safe I/O
import builtins
import glob
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

_ORIG_OPEN = builtins.open

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
CAL_DIR = os.path.join(STATE, "calibration")
os.makedirs(CAL_DIR, exist_ok=True)
PARAMS_PATH = os.path.join(CAL_DIR, "calibration_params.json")

EVALDIR = os.environ.get("LUKHAS_EVAL_DIR", "./eval_runs")
RECDIR = os.path.join(STATE, "provenance", "exec_receipts")


@dataclass
class CalibParams:
    fitted_at: float
    source: str  # "eval"|"receipts"
    bins: list[dict[str, float]]  # global reliability
    ece: float  # global ECE
    temperature: float  # global temperature
    min_conf_clip: float
    max_conf_clip: float
    # NEW:
    per_task_temperature: dict[str, float] = None  # e.g. {"generate_summary": 1.12, ...}
    per_task_ece: dict[str, float] = None  # e.g. {"generate_summary": 0.041, ...}
    per_task_bins: dict[str, list[dict[str, float]]] = None  # (optional; keep last fitted)


def _read_json(p: str) -> dict:
    with _ORIG_OPEN(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(p: str, obj: Any):
    tmp = p + ".tmp"
    with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, p)


def _collect_eval() -> list[tuple[float, int, str]]:
    """Return list of (confidence, correct, task) from eval runs if available.
    For now assumes each task has 'score' in [0,1] and pass/fail."""
    files = sorted(glob.glob(os.path.join(EVALDIR, "eval_*.json")))
    out = []
    for fp in files[-10:]:  # last 10 evals
        try:
            ev = _read_json(fp)
            for r in ev.get("results", []):
                conf = float(r.get("score", 0.0))
                corr = 1 if bool(r.get("pass", False)) else 0
                task = str(r.get("task_id") or r.get("desc") or "unknown")
                out.append((conf, corr, task))
        except Exception:
            continue
    return out


def _collect_receipts() -> list[tuple[float, int, str]]:
    """Fallback: infer confidence from runtime metadata; requires your pipeline to log a 'confidence' field & correctness."""
    paths = sorted(glob.glob(os.path.join(RECDIR, "*.json")))
    out = []
    for p in paths[-1000:]:
        try:
            r = _read_json(p)
            conf = float((r.get("metrics") or {}).get("confidence", 0.0))
            corr = (r.get("metrics") or {}).get("correct", None)
            if corr is None:
                continue
            task = ((r.get("activity") or {}).get("type")) or "unknown"
            out.append((conf, 1 if corr else 0, str(task)))
        except Exception:
            continue
    return out


def reliability_diagram(samples: list[tuple[float, int, str]], bins: int = 10, task: str | None = None):
    if task is not None:
        samples = [s for s in samples if s[2] == task]
    buckets = [{"lower": i / bins, "upper": (i + 1) / bins, "count": 0, "acc": 0.0, "conf": 0.0} for i in range(bins)]
    for conf, corr, _t in samples:
        c = min(max(conf, 0.0), 1.0)
        idx = min(int(c * bins), bins - 1)
        b = buckets[idx]
        b["count"] += 1
        b["acc"] += corr
        b["conf"] += c
    diag = []
    for b in buckets:
        if b["count"] == 0:
            diag.append({"lower": b["lower"], "upper": b["upper"], "acc": None, "conf": None, "count": 0})
        else:
            diag.append(
                {
                    "lower": b["lower"],
                    "upper": b["upper"],
                    "acc": b["acc"] / b["count"],
                    "conf": b["conf"] / b["count"],
                    "count": b["count"],
                }
            )
    return diag


def expected_calibration_error(diag) -> float:
    total = sum(b["count"] for b in diag)
    if total == 0:
        return 0.0
    e = 0.0
    for b in diag:
        if b["count"] == 0:
            continue
        gap = abs((b["acc"] or 0.0) - (b["conf"] or 0.0))
        e += (b["count"] / total) * gap
    return float(round(e, 6))


def fit_temperature(samples: list[tuple[float, int, str]], weights: dict[str, float] | None = None) -> float:
    """Simple 1D temperature on confidence → minimize logloss (Newton steps) with optional per-task weights."""
    if not samples:
        return 1.0
    # Apply weights if provided
    weighted_pairs = []
    for c, y, t in samples:
        w = 1.0
        if weights and t in weights:
            w = weights[t]
        weighted_pairs.append((c, y, w))

    T = 1.0
    for _ in range(50):
        grad = 0.0
        hess = 0.0
        for conf, corr, weight in weighted_pairs:
            c = min(max(conf, 1e-6), 1 - 1e-6)
            z = math.log(c / (1.0 - c))
            zT = z / T
            p = 1.0 / (1.0 + math.exp(-zT))
            grad += weight * (p - corr) * (-z) / (T * T)
            hess += weight * p * (1 - p) * (z * z) / (T**4)
        if abs(hess) < 1e-9:
            break
        step = grad / hess
        T = max(0.2, min(5.0, T - step))
        if abs(step) < 1e-6:
            break
    return float(round(T, 6))


def fit_and_save(source_preference: str = "eval", feedback_weights: dict[str, float] | None = None) -> CalibParams:
    samples = _collect_eval() if source_preference == "eval" else _collect_receipts()
    if not samples:
        # fallback to the other source
        samples = _collect_receipts() if source_preference == "eval" else _collect_eval()
        src = "receipts" if source_preference == "eval" else "eval"
    else:
        src = source_preference

    # Get feedback weights if not provided
    if feedback_weights is None:
        try:
            from qi.feedback.triage import get_triage

            triage = get_triage()
            clusters = triage.store.read_clusters()
            feedback_weights = triage.compute_task_weights(clusters)
        except Exception as e:
            feedback_weights = {}

    # global (with weights)
    diag = reliability_diagram(samples)
    ece = expected_calibration_error(diag)
    T_global = fit_temperature(samples, weights=feedback_weights)

    # per-task
    per_task_temperature = {}
    per_task_ece = {}
    per_task_bins = {}
    tasks = sorted({t for _c, _y, t in samples})
    for t in tasks:
        d = reliability_diagram(samples, task=t)
        n_samples = sum(b["count"] for b in d)

        # Cold-start: if samples < N_min (e.g., 50) → ignore weight
        if n_samples < 50:
            task_weights = None
        else:
            task_weights = {t: feedback_weights.get(t, 1.0)} if feedback_weights else None

        if n_samples < 20:  # skip tiny data
            continue
        per_task_bins[t] = d
        per_task_ece[t] = expected_calibration_error(d)
        per_task_temperature[t] = fit_temperature([s for s in samples if s[2] == t], weights=task_weights)

    params = CalibParams(
        fitted_at=time.time(),
        source=src,
        bins=diag,
        ece=ece,
        temperature=T_global,
        min_conf_clip=0.02,
        max_conf_clip=0.98,
        per_task_temperature=per_task_temperature or {},
        per_task_ece=per_task_ece or {},
        per_task_bins=per_task_bins or {},
    )
    _write_json(PARAMS_PATH, asdict(params))
    return params


def load_params() -> CalibParams | None:
    if not os.path.exists(PARAMS_PATH):
        return None
    j = _read_json(PARAMS_PATH)
    return CalibParams(**j)


def apply_calibration(conf: float, params: CalibParams | None = None) -> float:
    p = params or load_params()
    if p is None:
        return conf
    c = min(max(conf, p.min_conf_clip), p.max_conf_clip)
    # temperature scaling with pre-logit / post-sigmoid
    z = math.log(c / (1.0 - c))
    zT = z / (p.temperature if p.temperature else 1.0)
    out = 1.0 / (1.0 + math.exp(-zT))
    return float(max(0.0, min(1.0, out)))


def reliability_svg(task: str | None = None, width=640, height=320) -> str:
    """Render reliability diagram + ECE/Temp as SVG using current params (or latest fit)."""
    p = load_params()
    if not p:
        return f"<svg width='{width}' height='{height}' xmlns='http://www.w3.org/2000/svg'><text x='12' y='24' fill='#e7eaf0' font-family='monospace'>No calibration params found.</text></svg>"
    # choose bins & stats
    bins = (p.per_task_bins or {}).get(task) if task else p.bins
    ece = (p.per_task_ece or {}).get(task) if task else p.ece
    T = (p.per_task_temperature or {}).get(task) if task else p.temperature
    if not bins:
        bins = p.bins
        ece = p.ece
        T = p.temperature

    pad = 40
    W = width
    H = height
    # axes
    lines = [
        f"<rect width='{W}' height='{H}' fill='#0f1115'/>",
        f"<line x1='{pad}' y1='{H-pad}' x2='{W-pad}' y2='{H-pad}' stroke='#444'/>",
        f"<line x1='{pad}' y1='{H-pad}' x2='{pad}' y2='{pad}' stroke='#444'/>",
        f"<text x='{pad}' y='{pad-12}' fill='#9aa5b1' font-size='12' font-family='monospace'>ECE={ece:.4f}  T={T:.3f}  {('task='+task) if task else 'global'}</text>",
    ]
    # y-scale 0..1
    # draw ideal diagonal
    lines.append(
        f"<line x1='{pad}' y1='{H-pad}' x2='{W-pad}' y2='{pad}' stroke='#2a74ff' stroke-dasharray='4 3' opacity='0.6'/>"
    )

    # draw bars: predicted conf vs empirical acc for each bin
    n = len(bins)
    innerW = W - 2 * pad
    barW = innerW / n
    for i, b in enumerate(bins):
        if b["count"] == 0:
            continue
        cx = pad + i * barW + barW / 2
        # predicted confidence as x position (midpoint) vs y height? We'll render two lines per bin:
        # vertical tick at bin center up to predicted acc and empirical acc.
        conf = b["conf"] or 0.0
        acc = b["acc"] or 0.0

        # convert to y
        def Y(v):
            return H - pad - v * (H - 2 * pad)

        x = cx
        # conf marker
        lines.append(f"<circle cx='{x-6}' cy='{Y(conf)}' r='3' fill='#9aa5b1'/>")
        # acc marker
        lines.append(f"<circle cx='{x+6}' cy='{Y(acc)}' r='3' fill='#3ddc97'/>")
        # bin boundary
        if i > 0:
            xb = pad + i * barW
            lines.append(f"<line x1='{xb}' y1='{H-pad}' x2='{xb}' y2='{H-pad+4}' stroke='#555'/>")
        # label each 2 bins
        if i % 2 == 0:
            pct = int(b["upper"] * 100)
            lines.append(
                f"<text x='{cx-8}' y='{H-pad+14}' fill='#777' font-size='10' font-family='monospace'>{pct}%</text>"
            )
    return (
        f"<svg width='{W}' height='{H}' viewBox='0 0 {W} {H}' xmlns='http://www.w3.org/2000/svg'>{''.join(lines)}</svg>"
    )


# ------------- CLI -------------
def main():
    import argparse

    ap = argparse.ArgumentParser(description="Lukhas Uncertainty & Calibration Engine")
    ap.add_argument("--fit", action="store_true", help="Fit and save params (from eval by default)")
    ap.add_argument("--source", default="eval", choices=["eval", "receipts"])
    ap.add_argument("--show", action="store_true", help="Print current params")
    ap.add_argument("--demo", action="store_true", help="Demo: fit + print ECE")
    args = ap.parse_args()

    if args.fit or args.demo:
        p = fit_and_save(args.source)
        print(json.dumps(asdict(p), indent=2))
        if not args.demo:
            return
    if args.show:
        p = load_params()
        print(json.dumps(asdict(p) if p else {"note": "no params"}, indent=2))


if __name__ == "__main__":
    main()
