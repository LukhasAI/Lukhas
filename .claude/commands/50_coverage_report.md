---
danger_level: low
goal: Rebuild human-readable coverage & where-is-which deltas
module: unknown
name: coverage-report
type: documentation
---
## Prompt
Recalculate coverage and refresh human mapping (md+csv). Include "Delta" between pre/post move if available.

## Shell
```bash
set -euo pipefail
make coverage-report
python3 - <<'PY'
import pathlib, csv, json
root=pathlib.Path('.')
rows=[]
for d in (root/'Lukhas').iterdir():
    if d.is_dir():
        rows.append([d.name, f"Lukhas/{d.name}/"])
with open(root/'artifacts/where_is_which.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['module','path']); w.writerows(sorted(rows))
with open(root/'artifacts/where_is_which.md','w') as f:
    f.write("| Module | Path |\n|---|---|\n")
    for m,p in sorted(rows): f.write(f"| `{m}` | `{p}` |\n")
print("UPDATED where_is_which.*")
PY
```

## Acceptance

* `where_is_which.*` reflect flat root