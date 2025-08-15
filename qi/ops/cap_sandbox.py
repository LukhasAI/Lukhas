from __future__ import annotations
from typing import Dict, Any
class CapabilityError(Exception): pass
class CapSandbox:
    def __init__(self, allow: Dict[str,bool]): self.allow=allow
    def require(self, cap: str):
        if not self.allow.get(cap, False):
            raise CapabilityError(f"Capability '{cap}' not granted")
    def with_net(self): self.require("net")
    def with_fs(self):  self.require("fs")
    def with_api(self, name:str): self.require(f"api:{name}")
if __name__=="__main__":
    import argparse, json
    ap=argparse.ArgumentParser(); ap.add_argument("--net", action="store_true"); args=ap.parse_args()
    cs=CapSandbox({"net":args.net}); 
    try: cs.with_net(); print(json.dumps({"ok":True}))
    except Exception as e: print(json.dumps({"ok":False,"err":str(e)}))
