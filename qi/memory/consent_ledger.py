from __future__ import annotations
import os, json, time, argparse
from typing import Dict, Any
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
LEDGER=os.path.join(STATE,"consent_ledger.jsonl")
def record(user_id: str, purpose: str, fields: list[str], duration_days: int, meta: Dict[str,Any]|None=None):
    rec={"ts":time.time(),"user":user_id,"purpose":purpose,"fields":fields,"duration_days":duration_days,"meta":meta or {}}
    with open(LEDGER,"a",encoding="utf-8") as f: f.write(json.dumps(rec)+"\n")
    return rec
def forget(user_id: str):
    # stub: real impl would trigger targeted purges/GC
    record(user_id, "forget", [], 0, {"action":"erase"})
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--user", required=True)
    ap.add_argument("--purpose", required=True)
    ap.add_argument("--fields", nargs="+", default=[])
    ap.add_argument("--days", type=int, default=365)
    args=ap.parse_args()
    print(record(args.user,args.purpose,args.fields,args.days))
