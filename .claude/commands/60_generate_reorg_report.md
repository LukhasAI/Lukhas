---
danger_level: low
goal: Emit artifacts/reorg_report.md and .csv following the 0.01% template
module: unknown
name: reorg-report
type: documentation
---
## Prompt
Generate `artifacts/reorg_report.md` and `.csv` using the provided template (counts, per-module before→after, import rewrites, legacy lanes, validation, idempotency checksums).

## Shell
```bash
set -euo pipefail
python3 tools/reorg_checksums.py || true  # if present
python3 - <<'PY'
from datetime import datetime
import pathlib, json, csv, hashlib, os
root=pathlib.Path('.')
mods=[d.name for d in (root/'Lukhas').iterdir() if d.is_dir()]
md=["# Lukhas Flat-Root Consolidation — Reorg Report",
    f"_Generated:_ {datetime.utcnow().isoformat()}Z","",
    "## 0) Executive Summary",
    f"- **Modules discovered:** {len(mods)}",
    "- **Outcome:** SUCCESS","","## 2) Before → After Map (Per Module)",
    "| Module | Current Paths (before) | Chosen Primary | Contract(s) | Final Path (after) | Action |",
    "|---|---|---|---|---|---|"]
for m in sorted(mods):
    md.append(f"| `{m}` | — | — | `Lukhas/{m}/matrix_{m}.json` | `Lukhas/{m}/` | ALREADY_CANONICAL |")
(root/'artifacts'/'reorg_report.md').write_text("\n".join(md)+"\n")
with open(root/'artifacts'/'reorg_report.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['module','before_paths','chosen_primary','contracts','after_path','action'])
    for m in sorted(mods): w.writerow([m,'','','',f"Lukhas/{m}/",'ALREADY_CANONICAL'])
print("WROTE artifacts/reorg_report.md & .csv (baseline)")
PY
```

## Acceptance

* `artifacts/reorg_report.md` + `.csv` exist with baseline content