from __future__ import annotations
from typing import Dict, Any
class ConfidenceRouter:
    def decide(self, *, calibrated_conf: float) -> Dict[str, Any]:
        if calibrated_conf >= 0.8:   return {"path":"fast","gen_tokens":256,"retrieval":False}
        if calibrated_conf >= 0.6:   return {"path":"normal","gen_tokens":512,"retrieval":True}
        if calibrated_conf >= 0.4:   return {"path":"deliberate","gen_tokens":768,"retrieval":True,"double_pass":True}
        return {"path":"human_loop","gen_tokens":128,"retrieval":True,"handoff":True}
if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--conf", type=float, required=True)
    args = ap.parse_args()
    print(json.dumps(ConfidenceRouter().decide(calibrated_conf=args.conf), indent=2))
