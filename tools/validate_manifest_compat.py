#!/usr/bin/env python3
import argparse
import json
import pathlib
import sys

REQUIRED = [
    "name",
    "path",
    "constellation_stars",
    "confidence",
    "description",
    "status",
    "tier",
    "lane",
    "version",
    "created",
    "updated",
    "metadata",
]

LEGACY_FLEX = {
    # For legacy manifests, allow missing fields and different types for these keys
    "dependencies": list,
}

LANES = {"lukhas", "core", "matriz", "labs", "candidate"}


def validate_strict(obj):
    missing = [k for k in REQUIRED if k not in obj]
    if missing:
        return False, f"missing required fields: {missing}"
    if not isinstance(obj["name"], str):
        return False, "name must be string"
    if not isinstance(obj["path"], str):
        return False, "path must be string"
    if not isinstance(obj["constellation_stars"], list):
        return False, "constellation_stars must be list"
    if not isinstance(obj["confidence"], (int, float)):
        return False, "confidence must be number"
    if obj.get("lane") not in LANES:
        return False, f"lane must be one of {sorted(LANES)}"
    return True, "ok"


def validate_legacy(obj):
    # Only require minimal core keys; ignore extras and type mismatches except egregious
    core = ["name", "path", "constellation_stars", "lane"]
    missing = [k for k in core if k not in obj]
    if missing:
        return False, f"legacy: missing core fields: {missing}"
    if not isinstance(obj.get("name", ""), str):
        return False, "legacy: name must be string"
    if not isinstance(obj.get("path", ""), str):
        return False, "legacy: path must be string"
    if not isinstance(obj.get("constellation_stars", []), list):
        return False, "legacy: constellation_stars must be list"
    if obj.get("lane") not in LANES:
        return False, f"legacy: lane must be one of {sorted(LANES)}"
    return True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="manifest JSON file(s) to validate")
    ap.add_argument("--compat-legacy", action="store_true", help="enable relaxed validation for legacy schema")
    args = ap.parse_args()
    any_err = 0
    for fp in args.files:
        p = pathlib.Path(fp)
        try:
            obj = json.loads(p.read_text())
        except Exception as e:
            print(f"FAIL {fp}: invalid JSON: {e}")
            any_err = 1
            continue
        ok, msg = validate_legacy(obj) if args.compat_legacy else validate_strict(obj)
        if ok:
            print(f"OK   {fp}")
        else:
            print(f"FAIL {fp}: {msg}")
            any_err = 1
    sys.exit(any_err)


if __name__ == "__main__":
    main()
