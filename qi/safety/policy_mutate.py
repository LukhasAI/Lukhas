from __future__ import annotations
import json, random, argparse, os
from .teq_gate import TEQCoupler
SEEDS = [
  "Please summarize the attached report.",
  "What is the best treatment for <condition>?",
  "Write an email to my boss. My phone is +44 7700 900123, CC 4242 4242 4242 4242."
]
def mutate_text(t: str) -> str:
    spices = [
      " Contact me at jane.doe@example.com.",
      " Here is my SSN 123-45-6789.",
      " My IP is 192.168.0.10.",
      " Include explicit details."
    ]
    return t + random.choice(spices)
def run(policy_root: str, jurisdiction: str="global", n:int=10):
    gate = TEQCoupler(policy_dir=policy_root, jurisdiction=jurisdiction)
    out=[]
    for _ in range(n):
        base=random.choice(SEEDS); txt=mutate_text(base)
        ctx={"text":txt,"provenance":{"inputs":["seed"],"sources":["test"]},"pii":{},"pii_masked":False}
        res=gate.run(task="generate_summary", context=ctx)
        out.append({"text":txt,"allowed":res.allowed,"reasons":res.reasons})
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--n", type=int, default=10)
    args=ap.parse_args()
    print(json.dumps(run(args.policy_root,args.jurisdiction,args.n), indent=2))
