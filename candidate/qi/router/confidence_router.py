from __future__ import annotations

import argparse
import json
import os
from typing import Any
import streamlit as st

STATE = os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
CAL_PATH = os.path.join(STATE, "calibration.json")

DEFAULT = {
    "fast": {"gen_tokens": 256, "retrieval": False, "passes": 1, "temperature": 0.5},
    "normal": {"gen_tokens": 512, "retrieval": True, "passes": 1, "temperature": 0.7},
    "deliberate": {
        "gen_tokens": 768,
        "retrieval": True,
        "passes": 2,
        "temperature": 0.6,
    },
    "handoff": {
        "gen_tokens": 128,
        "retrieval": True,
        "passes": 1,
        "temperature": 0.3,
        "handoff": True,
    },
}


class ConfidenceRouter:
    def __init__(self, conf_thresholds=(0.8, 0.6, 0.4)):
        self.t_fast, self.t_norm, self.t_delib = conf_thresholds
        self.cal = self._load_calibration()

    def _load_calibration(self):
        try:
            return json.load(open(CAL_PATH))
        except Exception:
            return {}

    def decide(self, *, calibrated_conf: float, last_path: str | None = None) -> dict[str, Any]:
        """
        Hysteresis: avoid flapping between adjacent paths by requiring a margin.
        """
        margin = 0.03
        if calibrated_conf >= self.t_fast:
            path = "fast"
        elif calibrated_conf >= self.t_norm:
            path = "normal"
        elif calibrated_conf >= self.t_delib:
            path = "deliberate"
        else:
            path = "handoff"

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
    print(
        json.dumps(
            ConfidenceRouter().decide(calibrated_conf=args.conf, last_path=args.last_path),
            indent=2,
        )
    )
