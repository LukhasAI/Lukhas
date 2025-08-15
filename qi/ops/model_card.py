from __future__ import annotations
import os, json, argparse
STATE=os.environ.get("LUKHAS_STATE", os.path.expanduser("~/.lukhas/state"))
def load_json(p, default=None):
    try: return json.load(open(p))
    except: return default
def generate(out_md: str):
    cal=load_json(os.path.join(STATE,"calibration.json"),{})
    pol=load_json(os.path.join(STATE,"policy_report.json"),{})
    ceval=load_json(os.path.join(STATE,"eval","ceval.json"),{})
    card={"title":"Lukhas Model & Safety Card","calibration":cal,"policy":pol,"eval":ceval}
    with open(out_md,"w") as f: f.write("# Lukhas Model & Safety Card\n\n```json\n"+json.dumps(card,indent=2)+"\n```\n")
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out-md", required=True)
    args=ap.parse_args(); generate(args.out_md); print(args.out_md)
