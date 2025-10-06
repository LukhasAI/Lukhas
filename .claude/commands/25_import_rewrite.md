---
danger_level: medium
goal: Normalize imports to `lukhas.<module>`; remove lane prefixes
module: unknown
name: import-rewrite
type: documentation
---
## Prompt
Rewrite repo-wide (excluding `artifacts/`, `.git/`):
- `from lukhas.lukhas.` → `from lukhas.`
- `from lukhas.accepted.` → `from lukhas.`
- `from candidate.` → `from lukhas.`
- `import lukhas.lukhas.` → `import lukhas.`
- `import lukhas.accepted.` → `import lukhas.`
- `import candidate.` → `import lukhas.`

Then run a quick importability check: attempt `importlib.import_module(f"lukhas.{module}")` for all modules in `Lukhas/`.

## Shell
```bash
set -euo pipefail
# rewrite
python3 - <<'PY'
import pathlib, re
root = pathlib.Path('.')
patterns = [
    (r'\bfrom\s+lukhas\.lukhas\.', 'from lukhas.'),
    (r'\bfrom\s+lukhas\.accepted\.', 'from lukhas.'),
    (r'\bfrom\s+candidate\.', 'from lukhas.'),
    (r'\bimport\s+lukhas\.lukhas\.', 'import lukhas.'),
    (r'\bimport\s+lukhas\.accepted\.', 'import lukhas.'),
    (r'\bimport\s+candidate\.', 'import lukhas.')
]
for p in root.rglob('*.py'):
    if str(p).startswith(('artifacts/','.git/')): continue
    s = t = p.read_text(encoding='utf-8', errors='ignore')
    for pat,rep in patterns: t = re.sub(pat, rep, t)
    if t!=s: p.write_text(t, encoding='utf-8')
print("REWRITES APPLIED")

# importability
import importlib, json
mods = [d.name for d in (root/'Lukhas').iterdir() if d.is_dir()]
fail = {}
for m in mods:
    try: importlib.import_module(f"lukhas.{m}")
    except Exception as e: fail[m]=str(e)
pathlib.Path('artifacts/import_failures.json').write_text(json.dumps(fail, indent=2))
print("WROTE artifacts/import_failures.json")
if fail:
    print("WARN: Some modules failed to import; see artifacts/import_failures.json")
PY
```

## Acceptance

* `artifacts/import_failures.json` exists (empty or actionable)