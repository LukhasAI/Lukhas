# path: qi/safety/teq_coupler.py
from __future__ import annotations

# safe I/O
import builtins
import json
import os
from typing import Any

_ORIG_OPEN = builtins.open

from qi.metrics.calibration import apply_calibration, load_params
from qi.safety.constants import MAX_THRESHOLD_SHIFT

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
COUPLER_STATE = os.path.join(STATE, "teq_coupler.json")

def _write_json(p: str, obj: Any):
    tmp=p+".tmp"
    with _ORIG_OPEN(tmp,"w",encoding="utf-8") as f: json.dump(obj, f, indent=2)
    os.replace(tmp,p)

def _pick_temperature(task: str | None, params) -> float:
    if not params: return 1.0
    if task and params.per_task_temperature and task in params.per_task_temperature:
        return float(params.per_task_temperature[task])
    return float(params.temperature or 1.0)

def calibrated_gate(confidence: float, *, base_threshold: float, max_shift: float = MAX_THRESHOLD_SHIFT, task: str | None = None) -> dict[str, Any]:
    """
    Uses per-task temperature if available; falls back to global.
    Respects feedback-driven threshold adjustments (bounded to ±0.05).
    Returns a dict safe to embed in receipts.
    """
    params = load_params()
    T = _pick_temperature(task, params)
    # temporarily override temperature for apply_calibration
    if params:
        params.temperature = T
    c_hat = apply_calibration(confidence, params)

    # Get feedback-driven threshold adjustment if available
    feedback_shift = 0.0
    try:
        # Check if there are active proposals for this task
        proposals_file = os.path.join(STATE, "proposals", "active_adjustments.json")
        if os.path.exists(proposals_file):
            with _ORIG_OPEN(proposals_file, "r") as f:
                adjustments = json.load(f)
                if task and task in adjustments:
                    feedback_shift = adjustments[task].get("threshold_delta", 0.0)
    except:
        pass

    # Combine temperature-based and feedback-based shifts (bounded)
    temp_shift = 0.0
    if T > 1.0:   # under-confident → lower threshold slightly
        temp_shift = -min(max_shift/2, (T-1.0)*0.025)
    elif T < 1.0: # over-confident → raise slightly
        temp_shift =  min(max_shift/2, (1.0-T)*0.025)

    # Total shift bounded to max_shift (0.05)
    total_shift = max(-max_shift, min(max_shift, temp_shift + feedback_shift))

    eff = max(0.0, min(1.0, base_threshold + total_shift))
    decision = "allow" if c_hat >= eff else "block"
    # Determine calibration source (task-specific or global)
    calibration_source = "global"
    if task and params and params.per_task_temperature and task in params.per_task_temperature:
        # Check if task has enough samples for reliable calibration
        # This would ideally check actual sample count, but we use temperature as proxy
        calibration_source = "task"

    return {
        "raw_conf": float(confidence),
        "calibrated_conf": float(c_hat),
        "decision": decision,
        "threshold_base": float(base_threshold),
        "threshold_shift": float(total_shift),
        "threshold_eff": float(eff),
        "temperature": float(T),
        "task": task or None,
        "source": (params.source if params else None),
        "calibration_source": calibration_source,
        "feedback_shift": float(feedback_shift) if feedback_shift else None
    }

def emit_calibrated_receipt(**kwargs):
    """
    Emit a receipt with calibration metadata.

    Usage:
        gate_result = calibrated_gate(0.72, base_threshold=0.75, task="generate_summary")
        emit_calibrated_receipt(
            artifact_sha="abc123",
            run_id="run_456",
            task="generate_summary",
            started_at=time.time()-1,
            ended_at=time.time(),
            calibration_result=gate_result,
            # ... other receipt params
        )
    """
    # Extract calibration result if provided
    cal_result = kwargs.pop("calibration_result", None)

    # Set defaults for required parameters if not provided
    kwargs.setdefault("artifact_mime", "application/json")
    kwargs.setdefault("artifact_size", None)
    kwargs.setdefault("storage_url", None)

    # Build metrics dict from calibration data
    metrics = kwargs.get("metrics", {})
    if cal_result:
        metrics.update({
            "confidence": cal_result.get("raw_conf"),
            "calibrated_confidence": cal_result.get("calibrated_conf"),
            "temperature": cal_result.get("temperature"),
            "decision": cal_result.get("decision"),
            "threshold_eff": cal_result.get("threshold_eff"),
            "calibration_source": cal_result.get("source")
        })
        kwargs["metrics"] = metrics

        # Add to risk flags if blocked
        if cal_result.get("decision") == "block":
            risk_flags = kwargs.get("risk_flags", [])
            risk_flags.append("calibration_blocked")
            kwargs["risk_flags"] = risk_flags

    # Import and use receipts hub
    try:
        from qi.provenance.receipts_hub import emit_receipt
        return emit_receipt(**kwargs)
    except ImportError:
        # Fallback - just return the kwargs for testing
        return {"error": "receipts_hub not available", "kwargs": kwargs}

# ------------- CLI -------------
def main():
    import argparse
    import json as _json
    ap = argparse.ArgumentParser(description="TEQ Coupler preview")
    ap.add_argument("--conf", type=float, required=True, help="raw confidence [0,1]")
    ap.add_argument("--base-threshold", type=float, required=True)
    ap.add_argument("--max-shift", type=float, default=0.1)
    ap.add_argument("--task", type=str, help="task name for per-task calibration")
    args = ap.parse_args()
    result = calibrated_gate(args.conf, base_threshold=args.base_threshold, max_shift=args.max_shift, task=args.task)
    print(_json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
