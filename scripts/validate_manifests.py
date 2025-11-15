#!/usr/bin/env python3
"""
Validate all module.manifest.json files against schema.
Usage:
  python scripts/validate_manifests.py --schema schemas/matriz_module_compliance.schema.json [--root .] [--warn-only]
"""
import argparse
import json
import pathlib
import sys

from jsonschema import Draft7Validator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--warn-only", action="store_true")
    args = ap.parse_args()

    with open(args.schema, encoding="utf-8") as f:
        schema = json.load(f)
    validator = Draft7Validator(schema)

    root = pathlib.Path(args.root)
    files = list(root.rglob("module.manifest.json"))
    failures = 0

    for f in sorted(files):
        with open(f, encoding="utf-8") as file:
            data = json.load(file)
        errs = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errs:
            failures += 1
            print(f"[FAIL] {f}")
            for e in errs[:10]:
                loc = "$." + ".".join([str(p) for p in e.path])
                print("  -", e.message, " @ ", loc)
        else:
            print(f"[OK]   {f}")

    print(f"\nChecked {len(files)} files; failures: {failures}")
    if failures and not args.warn_only:
        sys.exit(1)

if __name__ == "__main__":
    main()
