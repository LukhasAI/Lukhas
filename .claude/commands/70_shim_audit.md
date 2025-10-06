---
danger_level: low
goal: Track and timebox legacy lane shims; fail if new code appears there
module: unknown
name: shim-audit
type: documentation
---
## Prompt
Scan legacy paths for non-shim files. If found, list them and exit nonzero. Otherwise, print OK.

## Shell
```bash
set -euo pipefail
python3 - <<'PY'
import pathlib, sys
bad=[]
for base in ['Lukhas/lukhas','Lukhas/accepted','candidate','LukhasCandidates']:
    p=pathlib.Path(base)
    if not p.exists(): continue
    for f in p.rglob('*'):
        if f.is_file() and f.name not in ('__init__.py','README.md'):
            bad.append(str(f))
if bad:
    print("Non-shim files detected in legacy lanes:")
    print("\n".join(bad))
    sys.exit(1)
print("Legacy lanes clean (shims only)")
PY
```

## Acceptance

* Exits 0 when only shims exist; nonzero if drift