---
danger_level: low
goal: Enumerate modules, lanes, contracts; build dry-run inputs
module: unknown
name: discovery
type: documentation
---
## Prompt (to Claude)
Scan the repo to discover all modules under:
- Lukhas/**
- Lukhas/lukhas/**
- Lukhas/accepted/**
- candidate/**
- LukhasCandidates/**
- any Lucas* legacy roots

Also find all matrix_*.json and map to modules. If these artifacts exist, reuse not overwrite:
- artifacts/matriz_inventory.json
- artifacts/where_is_which.md
- artifacts/where_is_which.csv
- artifacts/matriz_audit.json

Emit or update:
- artifacts/flat_inventory.json
- artifacts/flat_duplicates.md
- artifacts/where_is_which.md (if missing)
- artifacts/where_is_which.csv (if missing)

## Shell (run in repo root)
```bash
mkdir -p artifacts
python3 - <<'PY'
import json, os, pathlib, csv
root = pathlib.Path('.')
mods = {}
contracts = []
for p in root.rglob('matrix_*.json'):
    if str(p).startswith('artifacts/'): continue
    module = p.stem.replace('matrix_','')
    contracts.append({'module':module,'path':str(p)})
for d in ['Lukhas','candidate','LukhasCandidates','Lukhas/lukhas','Lukhas/accepted']:
    dp = root/d
    if not dp.exists(): continue
    for child in dp.iterdir():
        if child.is_dir():
            mods.setdefault(child.name, []).append(str(child))
artifacts = root/'artifacts'
with open(artifacts/'flat_inventory.json','w') as f: json.dump({'modules':mods,'contracts':contracts}, f, indent=2)
# human map
with open(artifacts/'where_is_which.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['module','paths'])
    for m,paths in sorted(mods.items()): w.writerow([m,'|'.join(paths)])
with open(artifacts/'where_is_which.md','w') as f:
    f.write("| Module | Paths |\n|---|---|\n")
    for m,paths in sorted(mods.items()): f.write(f"| `{m}` | {', '.join(paths)} |\n")
PY
```

## Acceptance

* `artifacts/flat_inventory.json` exists with modules+contracts
* `artifacts/where_is_which.{md,csv}` present