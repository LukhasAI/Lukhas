#!/usr/bin/env python3
"""
Run pytest collect-only, parse ModuleNotFoundErrors for lukhas.*, cluster them,
and emit a shim manifest for package promotion.

Outputs:
  - artifacts/import_missing.json  (raw occurrences)
  - artifacts/import_clusters.json (dedup + counts)
  - artifacts/lukhas_shim_map.json (package_dir -> [submodules])
"""
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ART = Path("artifacts")
ART.mkdir(exist_ok=True, parents=True)

def run_collect():
    # Collect-only to avoid executing tests; keep stderr merged.
    proc = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True, text=True
    )
    return proc.stdout + "\n" + proc.stderr

MISS_RE = re.compile(r"ModuleNotFoundError: No module named ['\"](lukhas(?:\.[A-Za-z0-9_]+)+)['\"]")

def main():
    out = run_collect()
    misses = MISS_RE.findall(out)

    Path(ART / "import_missing.json").write_text(json.dumps(misses, indent=2, sort_keys=True))
    counts = Counter(misses)
    clusters = [{"module": m, "count": c} for m, c in counts.most_common()]
    Path(ART / "import_clusters.json").write_text(json.dumps(clusters, indent=2))

    # Build package shim map: lukhas.a.b.c -> package dir 'lukhas/a/b' and submodule 'c'
    pkg_map = defaultdict(set)
    for mod in counts:
        parts = mod.split(".")[1:]  # drop 'lukhas'
        if len(parts) >= 2:
            pkg_dir = "lukhas/" + "/".join(parts[:-1])
            leaf = parts[-1]
            pkg_map[pkg_dir].add(leaf)
        else:
            # single-level misses handled by alias hook, but include anyway
            pkg_dir = "lukhas/" + parts[0]
            pkg_map[pkg_dir].add("__init__")

    # keep only hot paths (threshold = 3)
    THRESH = 3
    hot = {}
    for item in clusters:
        m = item["module"]
        c = item["count"]
        if c >= THRESH:
            parts = m.split(".")[1:]
            if len(parts) >= 2:
                pkg_dir = "lukhas/" + "/".join(parts[:-1])
                leaf = parts[-1]
                hot.setdefault(pkg_dir, set()).add(leaf)

    # Convert sets → lists
    pkg_map = {k: sorted(v) for k, v in pkg_map.items()}
    hot = {k: sorted(v) for k, v in hot.items()}

    Path(ART / "lukhas_shim_map.json").write_text(json.dumps(hot or pkg_map, indent=2))
    print(f"✅ Wrote {ART/'import_missing.json'}, {ART/'import_clusters.json'}, {ART/'lukhas_shim_map.json'}")

if __name__ == "__main__":
    sys.exit(main())
