---
danger_level: low
goal: Produce a dry-run plan to flatten under Lukhas/<module> without moving files
module: unknown
name: flat-root-dry-run
type: documentation
---
## Prompt
Using **artifacts/flat_inventory.json** (or matriz_* equivalents if present), build a plan that moves each module to:
- `Lukhas/<module>/`
Select primary source when duplicates exist (prefer candidate/* if more recently modified, else Lukhas/*).
Co-locate contract to: `Lukhas/<module>/matrix_<module>.json`

Emit:
- artifacts/lukhas_flat.plan.jsonl (one JSON per module: {module,before_paths,primary,contracts,target})
- artifacts/lukhas_flat_dry_run.md (table)
Open a Draft PR titled: `feat(lukhas): flat root consolidation — dry run`

## Shell
```bash
python3 - <<'PY'
import json, pathlib, os, time
root = pathlib.Path('.')
inv = json.loads((root/'artifacts/flat_inventory.json').read_text())
plan = []
now = time.time()
for m,paths in inv['modules'].items():
    # naive pick: path with highest mtime
    def mtime(p):
        try:
            return max((root/p).stat().st_mtime, max((f.stat().st_mtime for f in (root/p).rglob('*') if f.is_file()), default=0))
        except: return 0
    primary = sorted(paths, key=lambda p: mtime(p), reverse=True)[0]
    contracts = [c['path'] for c in inv.get('contracts',[]) if c['module']==m]
    plan.append({'module':m, 'before_paths':paths, 'primary':primary, 'contracts':contracts, 'target':f'Lukhas/{m}/'})
out = root/'artifacts'/'lukhas_flat.plan.jsonl'
with open(out,'w') as f:
    for row in plan: f.write(json.dumps(row)+'\n')
# md table
md = ["# Dry Run — Lukhas Flat Plan","","| Module | Before Paths | Primary | Contracts | Target |","|---|---|---|---|---|"]
for r in plan:
    md.append(f"| `{r['module']}` | {', '.join(r['before_paths'])} | `{r['primary']}` | {', '.join(r['contracts']) or '—'} | `{r['target']}` |")
(root/'artifacts'/'lukhas_flat_dry_run.md').write_text("\n".join(md)+"\n")
print("WROTE artifacts/lukhas_flat.plan.jsonl and lukhas_flat_dry_run.md")
PY
```

## Acceptance

* `artifacts/lukhas_flat.plan.jsonl` + `artifacts/lukhas_flat_dry_run.md` exist