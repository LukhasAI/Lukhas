import json
import pkgutil
import sys

failed = {}
# Probe all `lukhas.<module>` and a few known submodules from artifacts
candidates = set()
for m in pkgutil.iter_modules():
    # focus on your top-level modules found by the probe
    if m.name in {"qi","core","consciousness","api","identity","bridge","utils","vivox"}:
        candidates.add(m.name)
for m in sorted(candidates):
    try:
        __import__(f"lukhas.{m}")
    except Exception as e:
        failed[f"lukhas.{m}"] = repr(e)
print(json.dumps(failed, indent=2))
sys.exit(1 if failed else 0)
