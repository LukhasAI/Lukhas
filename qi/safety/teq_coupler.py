    """
    Uses per-task temperature if available; falls back to global.
    Respects feedback-driven threshold adjustments (bounded to ±0.05).
    Returns a dict safe to embed in receipts.
    """

from __future__ import annotations
import builtins
import json
import os
from typing import Any
from qi.metrics.calibration import apply_calibration, load_params
from qi.safety.constants import MAX_THRESHOLD_SHIFT
    try:
    try:
        from qi.provenance.receipts_hub import emit_receipt
    import argparse
    import json as _json

_ORIG_OPEN = builtins.open
STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
COUPLER_STATE = os.path.join(STATE, "teq_coupler.json")
def _write_json(p: str, obj: Any):
    tmp = p + ".tmp"
    with _ORIG_OPEN(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, p)
def _pick_temperature(task: str | None, params) -> float:
    if not params:
        return 1.0
    if task and params.per_task_temperature and task in params.per_task_temperature:
        return float(params.per_task_temperature[task])
    return float(params.temperature or 1.0)
def calibrated_gate(
    confidence: float,
    *,
    base_threshold: float,
    max_shift: float = MAX_THRESHOLD_SHIFT,
    task: str | None = None,
) -> dict[str, Any]:


        return emit_receipt(**kwargs)
    except ImportError:
        # Fallback - just return the kwargs for testing
        return {"error": "receipts_hub not available", "kwargs": kwargs}


# ------------- CLI -------------
def main():

    ap = argparse.ArgumentParser(description="TEQ Coupler preview")
    ap.add_argument("--conf", type=float, required=True, help="raw confidence [0,1]")
    ap.add_argument("--base-threshold", type=float, required=True)
    ap.add_argument("--max-shift", type=float, default=0.1)
    ap.add_argument("--task", type=str, help="task name for per-task calibration")
    args = ap.parse_args()
    result = calibrated_gate(
        args.conf,
        base_threshold=args.base_threshold,
        max_shift=args.max_shift,
        task=args.task,
    )
    print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
