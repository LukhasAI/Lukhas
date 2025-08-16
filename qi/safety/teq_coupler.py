# path: qi/safety/teq_coupler.py
from __future__ import annotations
import os, json
from typing import Dict, Any, Optional

# safe I/O
import builtins
_ORIG_OPEN = builtins.open

from qi.metrics.calibration import load_params, apply_calibration

STATE = os.path.expanduser(os.environ.get("LUKHAS_STATE", "~/.lukhas/state"))
COUPLER_STATE = os.path.join(STATE, "teq_coupler.json")

def _write_json(p: str, obj: Any):
    tmp=p+".tmp"
    with _ORIG_OPEN(tmp,"w",encoding="utf-8") as f: json.dump(obj, f, indent=2)
    os.replace(tmp,p)

def calibrated_gate(confidence: float, *, base_threshold: float, max_shift: float = 0.1) -> Dict[str, Any]:
    """
    Applies temperature scaling to a raw confidence score and nudges the TEQ threshold within ±max_shift.
    Returns the calibrated confidence, new effective threshold, and decision hint.
    """
    params = load_params()
    c_hat = apply_calibration(confidence, params)
    # threshold nudging: if model is under-confident (T>1), slightly lower threshold; if over-confident, raise it
    T = (params.temperature if params else 1.0)
    shift = 0.0
    if T > 1.0:  # under-confident → lower threshold a bit
        shift = -min(max_shift, (T-1.0)*0.05)
    elif T < 1.0: # over-confident → raise threshold a bit
        shift = min(max_shift, (1.0-T)*0.05)
    eff = max(0.0, min(1.0, base_threshold + shift))
    decision = "allow" if c_hat >= eff else "block"
    state = {"threshold_base": base_threshold, "threshold_shift": shift, "threshold_eff": eff, "temperature": T}
    _write_json(COUPLER_STATE, state)
    return {"calibrated_conf": c_hat, "decision": decision, **state}

# ------------- CLI -------------
def main():
    import argparse, json as _json
    ap = argparse.ArgumentParser(description="TEQ Coupler preview")
    ap.add_argument("--conf", type=float, required=True, help="raw confidence [0,1]")
    ap.add_argument("--base-threshold", type=float, required=True)
    ap.add_argument("--max-shift", type=float, default=0.1)
    args = ap.parse_args()
    print(_json.dumps(calibrated_gate(args.conf, base_threshold=args.base_threshold, max_shift=args.max_shift), indent=2))

if __name__ == "__main__":
    main()