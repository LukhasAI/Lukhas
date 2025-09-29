---
name: flat-root-execute
goal: Move code+contracts into Lukhas/<module>/ preserving git history
danger_level: medium
---

## Prompt
Apply `artifacts/lukhas_flat.plan.jsonl`:
- For each row, `git mv` primary path to `Lukhas/<module>/` (create if missing)
- Move first/primary contract to `Lukhas/<module>/matrix_<module>.json` (log duplicates to artifacts/contract_dupes.md, don't delete)
- Leave legacy dirs in place if they still contain other modules (no mass deletion)
- Write `artifacts/split_sources.md` if module had multiple before_paths

## Shell
```bash
set -euo pipefail
python3 - <<'PY'
import json, pathlib, subprocess, os, shutil
root = pathlib.Path('.')
plan = [json.loads(l) for l in (root/'artifacts/lukhas_flat.plan.jsonl').read_text().splitlines() if l.strip()]
dupes = []
splits = []
for r in plan:
    m, primary, target = r['module'], pathlib.Path(r['primary']), pathlib.Path(r['target'])
    target.mkdir(parents=True, exist_ok=True)
    if str(primary)!=str(target):
        subprocess.check_call(['git','mv',str(primary),str(target)])
    # contracts
    cs = r.get('contracts',[])
    if cs:
        main = cs[0]
        dest = target/(f"matrix_{m}.json")
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.check_call(['git','mv', main, str(dest)])
        if len(cs)>1: dupes.append({'module':m,'others':cs[1:]})
    if len(r['before_paths'])>1:
        splits.append({'module':m,'before_paths':r['before_paths']})
art = root/'artifacts'
if dupes:
    (art/'contract_dupes.md').write_text("\n".join([f"- {d['module']}: {', '.join(d['others'])}" for d in dupes])+"\n")
if splits:
    (art/'split_sources.md').write_text("\n".join([f"- {s['module']}: {', '.join(s['before_paths'])}" for s in splits])+"\n")
print("APPLIED: moves and primary contract colocation")
PY
```

## Acceptance

* All planned targets exist under `Lukhas/<module>/`
* Contracts present (or dupes logged)