from __future__ import annotations
import json, argparse, time
from typing import List, Dict, Any
def build_trace(nodes: List[Dict[str,Any]]) -> Dict[str,Any]:
    return {"ts":time.time(),"nodes":nodes}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--nodes-json", required=True, help='JSON list of {"id","label","inputs","outputs"}')
    args=ap.parse_args()
    print(json.dumps(build_trace(json.loads(args.nodes_json)), indent=2))
