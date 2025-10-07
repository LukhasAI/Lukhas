#!/usr/bin/env python3
"""Focus on last-mile collection errors using telemetry + pytest report."""
from __future__ import annotations
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ART = Path("artifacts")
FAILS = ART / "import_failures.ndjson"
COLLECT = ART / "pytest_collection_errors_detailed.json"


def load_ndjson(p: Path):
    """Load NDJSON file into list of dicts."""
    out = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def main():
    """Analyze import failures and pytest errors to suggest bridge targets."""
    fails = load_ndjson(FAILS)
    report = json.loads(COLLECT.read_text()) if COLLECT.exists() else {"detailed_errors": []}

    tb_by_mod = defaultdict(list)
    for it in fails:
        tb_by_mod[it.get("module", "<unknown>")].append(it.get("trace", ""))

    # Mine pytest report for ModuleNotFound / ImportError lines
    mod_counts = Counter()
    sym_counts = Counter()
    for e in report.get("detailed_errors", []):
        err_msg = e.get("full_message", "") or e.get("error_message", "")
        m1 = re.search(r"No module named ['\"]([^'\"]+)['\"]", err_msg)
        if m1:
            mod_counts[m1.group(1)] += 1
        m2 = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", err_msg)
        if m2:
            sym_counts[m2.group(1)] += 1

    print("\n=== HOT MODULES (telemetry+pytest) ===")
    combined = Counter({k: len(v) for k, v in tb_by_mod.items()}) + mod_counts
    for mod, n in combined.most_common(15):
        print(f"{n:>3}  {mod}")

    print("\n=== TOP MISSING SYMBOLS ===")
    for s, c in sym_counts.most_common(15):
        print(f"{c:>3}  {s}")

    # Spit out a todo list for bridges
    todo = []
    for mod, _ in combined.most_common():
        if mod.startswith((
            "lukhas.",
            "candidate.",
            "consciousness.",
            "core.",
            "governance.",
            "memory.",
            "observability.",
            "tools.",
        )):
            todo.append(mod)

    (ART / "phase11_bridge_targets.txt").write_text("\n".join(todo), encoding="utf-8")
    print(f"\n→ wrote suggested targets: {ART/'phase11_bridge_targets.txt'}")
    print(f"   Total targets: {len(todo)}")


if __name__ == "__main__":
    main()
