#!/usr/bin/env python3
"""
LUKHAS Manifest Validator (minimal / fast)
- Validates one manifest or scans repo for **/module.manifest.json
- Uses schemas/module.manifest.schema.json
- Adds a few pragmatic semantic checks (paths exist, module name matches dir)
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    import jsonschema
except Exception as e:
    print("❌ Missing dependency: jsonschema\n   pip install jsonschema", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "module.manifest.schema.json"

def load_schema(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)

def iter_manifests(start: Path) -> list[Path]:
    return sorted(start.rglob("module.manifest.json"))

def semantic_checks(manifest_path: Path, data: dict) -> list[str]:
    errs = []
    # 1) Module name should match directory name (best-effort)
    mod = data.get("module", "")
    leaf = manifest_path.parent.name
    if "." in mod:
        expected_leaf = mod.split(".")[-1].replace("_", "-").replace(".", "-")
        # allow small variations: underscore/dash differences are common
        norm = lambda s: s.lower().replace("_", "").replace("-", "")
        if norm(leaf) != norm(expected_leaf):
            errs.append(f"module '{mod}' does not seem to match directory '{leaf}'")

    # 2) Layout paths should exist if declared
    paths = (data.get("layout") or {}).get("paths") or {}
    for k, v in paths.items():
        p = (manifest_path.parent / v).resolve()
        if not p.exists():
            errs.append(f"layout.paths.{k} points to missing path: {v}")

    # 3) If runtime.language == python ⇒ entrypoints non-empty (schema already enforces; double-check)
    rt = data.get("runtime") or {}
    if rt.get("language") == "python" and not (rt.get("entrypoints") or []):
        errs.append("runtime.language=python but runtime.entrypoints is empty")

    # 4) If tokenization.enabled ⇒ asset_id/proof_uri present (schema enforces; double-check)
    tok = data.get("tokenization") or {}
    if tok.get("enabled"):
        for k in ("asset_id", "proof_uri"):
            if not tok.get(k):
                errs.append(f"tokenization.enabled=true but '{k}' is missing")

    return errs

def validate_file(schema: dict, manifest_path: Path) -> tuple[bool, list[str]]:
    try:
        with manifest_path.open() as f:
            data = json.load(f)
        jsonschema.validate(instance=data, schema=schema)
        sem = semantic_checks(manifest_path, data)
        if sem:
            return False, sem
        return True, []
    except jsonschema.ValidationError as e:
        return False, [f"schema: {e.message}"]
    except json.decoder.JSONDecodeError as e:
        return False, [f"json: {e}"]
    except Exception as e:
        return False, [f"unexpected: {e}"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="Path to a module.manifest.json")
    ap.add_argument("--all", action="store_true", help="Validate all manifests")
    args = ap.parse_args()

    if not SCHEMA.exists():
        print(f"❌ Schema not found: {SCHEMA}", file=sys.stderr)
        sys.exit(2)

    schema = load_schema(SCHEMA)

    targets: list[Path]
    if args.all or not args.path:
        targets = iter_manifests(ROOT)
        if args.path:
            p = Path(args.path).resolve()
            if p.is_dir():
                targets = iter_manifests(p)
            elif p.is_file():
                targets = [p]
    else:
        targets = [Path(args.path).resolve()]

    if not targets:
        print("⚠️  No manifests found.")
        sys.exit(0)

    print("🔍 LUKHAS Manifest Validator")
    print(f"Schema: {SCHEMA}")
    print("-" * 60)

    ok = 0
    failures: list[tuple[Path, list[str]]] = []
    for m in targets:
        valid, errs = validate_file(schema, m)
        try:
            rel_path = m.relative_to(ROOT)
        except ValueError:
            rel_path = m

        if valid:
            print(f"✅ {rel_path}")
            ok += 1
        else:
            print(f"❌ {rel_path}")
            for e in errs:
                print(f"   - {e}")
            failures.append((m, errs))

    print("\n📊 Summary:", f"{ok}/{len(targets)} valid")
    if failures:
        print(f"❌ {len(failures)} invalid manifest(s)")
        sys.exit(1)
    print("✅ All good!")
    sys.exit(0)

if __name__ == "__main__":
    main()