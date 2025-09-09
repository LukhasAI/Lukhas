#!/usr/bin/env python3
"""Validate example JSON files against the project's pydantic schemas.

Usage: python3 tools/validate_examples.py
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

EXAMPLES = [
    ("examples/job_users.json", "job"),
    ("examples/photon_users.json", "photon"),
    ("examples/widget_presets.json", "widgets"),
]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    failed = False

    # Try a few likely import paths so this script works when run from repo root
    import importlib

    # Prefer the fully-qualified package path that exists in the repo
    MODULE_CANDIDATES = [
        "products.intelligence.lens.api.schemas",
        "lambda_products.lambda_products_pack.lambda_core.Lens.api.schemas",
        "api.schemas",
        "schemas",
    ]

    schemas_mod = None
    for modname in MODULE_CANDIDATES:
        try:
            schemas_mod = importlib.import_module(modname)
            break
        except Exception:
            pass

    if schemas_mod is None:
        # Try adjusting sys.path to include repo root and api dir explicitly
        api_dir = os.path.join(ROOT, "api")
        if api_dir not in sys.path:
            sys.path.insert(0, api_dir)
        try:
            schemas_mod = importlib.import_module("schemas")
        except Exception as exc:
            print("Failed to import schemas from known locations:", exc)
            print("Tried candidates:", MODULE_CANDIDATES)
            sys.exit(2)

    # If the imported module doesn't provide the expected classes, attempt
    # to load the schemas file directly by path to avoid package-name issues.
    need_attrs = ("JobRequest", "PhotonDocument", "WidgetPresetsResponse")
    missing = [a for a in need_attrs if not hasattr(schemas_mod, a)]
    if missing:
        # Try to locate the schemas.py file in expected repo location
        candidate_path = os.path.join(
            ROOT, "lambda_products", "lambda_products_pack", "lambda_core", "Lens", "api", "schemas.py"
        )
        if os.path.exists(candidate_path):
            import importlib.util

            spec = importlib.util.spec_from_file_location("lens_api_schemas", candidate_path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load spec for {candidate_path}")
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            schemas_mod = mod
        else:
            # last-resort: try attributes and let AttributeError surface
            pass

    JobRequest = schemas_mod.JobRequest
    PhotonDocument = schemas_mod.PhotonDocument
    WidgetPresetsResponse = schemas_mod.WidgetPresetsResponse

    for path, kind in EXAMPLES:
        print(f"Validating {path} as {kind}...")
        data = load_json(path)
        try:
            if kind == "job":
                obj = JobRequest(**data)
            elif kind == "photon":
                obj = PhotonDocument(**data)
            elif kind == "widgets":
                obj = WidgetPresetsResponse(**data)
            else:
                raise RuntimeError("unknown kind")
            # Print a concise representation of the validated object
            # Print a concise representation of the validated object.
            printed = None
            if hasattr(obj, "model_dump_json"):
                try:
                    printed = obj.model_dump_json(indent=2)
                except Exception:
                    printed = None
            if printed is None and hasattr(obj, "json"):
                try:
                    printed = obj.json(indent=2)
                except Exception:
                    printed = None
            if printed is None:
                printed = repr(obj)
            print("  OK — validated.\n", printed)
        except Exception as exc:
            failed = True
            print("  VALIDATION FAILED:", exc)

    if failed:
        print("One or more validations failed")
        sys.exit(1)
    print("All example files validated successfully")


if __name__ == "__main__":
    main()