#!/usr/bin/env python3
"""
Analyze lukhas_import_ledger.ndjson to generate migration scorecard.
Ranks top legacy imports and recommends canonical targets.
"""
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter

LEDGER = Path("artifacts/lukhas_import_ledger.ndjson")
REPORT = Path("artifacts/IMPORT_MIGRATION_REPORT.md")

def read_ledger():
    if not LEDGER.exists():
        print(f"no ledger at {LEDGER}", file=sys.stderr)
        sys.exit(1)
    for line in LEDGER.read_text().splitlines():
        if not line.strip():
            continue
        try:
            yield json.loads(line)
        except Exception:
            continue

def main():
    alias_counts = Counter()
    target_counts = Counter()
    misses = Counter()
    pairs = defaultdict(Counter)  # lukhas.mod -> {real.mod: count}

    for ev in read_ledger():
        if ev.get("event") == "alias":
            l = ev.get("lukhas")
            r = ev.get("real")
            if l and r:
                alias_counts[l] += 1
                target_counts[r] += 1
                pairs[l][r] += 1
        elif ev.get("event") == "miss":
            l = ev.get("lukhas")
            if l:
                misses[l] += 1

    top_legacy = alias_counts.most_common(30)
    total_alias = sum(alias_counts.values())
    total_miss = sum(misses.values())

    # Pick a canonical target per lukhas.* (plurality vote)
    recommended = {}
    for l, _ in top_legacy:
        if pairs[l]:
            best = pairs[l].most_common(1)[0][0]
            recommended[l] = best

    # Emit report
    lines = []
    lines.append("# IMPORT MIGRATION REPORT\n")
    lines.append(f"- Total alias hits: **{total_alias}**")
    lines.append(f"- Total misses: **{total_miss}**\n")
    if top_legacy:
        lines.append("## Top legacy imports\n")
        lines.append("| rank | lukhas.* | hits | recommended canonical |")
        lines.append("|---:|---|---:|---|")
        for i, (l, n) in enumerate(top_legacy, 1):
            lines.append(f"| {i} | `{l}` | {n} | `{recommended.get(l, '—')}` |")
        lines.append("")
    if misses:
        lines.append("## Misses (need real modules or xfail)\n")
        for l, n in misses.most_common(20):
            lines.append(f"- `{l}` — {n} misses")
        lines.append("")
    REPORT.write_text("\n".join(lines))
    print(f"✅ Wrote {REPORT}")

if __name__ == "__main__":
    main()
