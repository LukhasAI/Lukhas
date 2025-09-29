---
name: contracts-colocate
goal: Ensure each module has `matrix_<module>.json` beside it, schema-safe
danger_level: low
---

## Prompt
For each directory `Lukhas/<module>/`, ensure presence of `matrix_<module>.json`. If absent, create a minimal, schema-valid v3 stub with:
- `"module": "<module>"`
- existing defaults; **do not** add fields not in schema.
Run `make validate-matrix-all || true` and log results.

## Shell
```bash
set -euo pipefail
python3 - <<'PY'
import json, pathlib
root = pathlib.Path('.')
created=[]
for d in (root/'Lukhas').iterdir():
    if not d.is_dir(): continue
    f = d/f"matrix_{d.name}.json"
    if not f.exists():
        stub = {
          "schema_version": "3.0.0",
          "module": d.name,
          "identity": {"requires_auth": False},
          "guardian_check": {"enabled": True}
        }
        f.write_text(json.dumps(stub, indent=2))
        created.append(str(f))
pathlib.Path('artifacts/contract_notes.md').write_text("\n".join(["- created "+c for c in created])+"\n")
print("CREATED:", len(created), "stubs")
PY
make validate-matrix-all || true
```

## Acceptance

* Missing contracts stubbed, validation runs