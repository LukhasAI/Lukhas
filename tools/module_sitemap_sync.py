#!/usr/bin/env python3
"""
LUKHAS - Module Sitemap Sync (T4/0.01%)

Purpose
-------
Idempotently scan all modules under a root (default: Lukhas/), ensure each has a normalized
layout and metadata, and emit human & machine artifacts. Designed to be SAFE-by-default:
- Dry-run by default (no writes) unless --write or --fix passed
- Never deletes; only creates or merges
- Produces diff-style markdown + JSON summary for auditing

What it enforces (aligned with artifacts/module_sitemap.md Draft v3):
- Per-module structure (created if missing when --write):
    <root>/<module>/
      module.json                    # normalized manifest (renamed from directory_index.json)
      schema/module_schema.json      # per-module schema/config descriptor (not global JSON-Schema)
      docs/                          # docs; creates README.md stub if missing
      tests/                         # tests; creates README.md stub if missing
      config/                        # configs; creates README.md stub if missing

- Metadata enrichment (added if missing, never overwriting explicit existing values):
    module.json:
      name, description, version
      lane (L0-L5)
      matriz_contract (path)
      owner {team, codeowners}
      tags []
      # Enrichments (0.01% additions)
      module_id (stable)
      matriz_ready (bool)
      tier (alias of lane for readability)
      provenance {git_sha?, created_at, updated_at}
      imports_validated (bool)
      dependencies [], contracts []

Outputs:
- artifacts/module_sitemap.sync.json        # machine summary (per-module status)
- artifacts/module_sitemap.diff.md          # human diff-style report
- (does NOT modify artifacts/where_is_which.*; separate tools manage those)

Usage:
    # See what would change (default)
    python3 tools/module_sitemap_sync.py

    # Apply changes (create/merge manifests & folders)
    python3 tools/module_sitemap_sync.py --write

    # Strict validation (non-zero exit if any module missing required bits)
    python3 tools/module_sitemap_sync.py --validate

    # Custom root
    python3 tools/module_sitemap_sync.py --root Lukhas

Exit codes:
  0: OK
  1: Validation failures (when --validate), or unexpected error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------- Defaults / Constants ----------

DEFAULT_ROOT = "Lukhas"
ARTIFACTS_DIR = Path("artifacts")
DIFF_MD = ARTIFACTS_DIR / "module_sitemap.diff.md"
SYNC_JSON = ARTIFACTS_DIR / "module_sitemap.sync.json"

REQUIRED_DIRS = ["docs", "tests", "config", "schema"]
MANIFEST_FILENAME = "module.json"                 # formerly directory_index.json
MODULE_SCHEMA_FILENAME = "module_schema.json"     # per-module descriptor (NOT JSON-Schema meta)
README_STUB = "# Placeholder\n\nThis stub is created by module_sitemap_sync.py. Replace with real content."

LANES = ["L0", "L1", "L2", "L3", "L4", "L5"]

# Attempt to detect MATRIZ contract naming convention
def _guess_matriz_contract(mod_dir: Path) -> str | None:
    # Look for matrix_<module>.json, or matrix.json
    mname = f"matrix_{mod_dir.name}.json"
    cand = mod_dir / mname
    if cand.exists():
        return mname
    cand2 = mod_dir / "matrix.json"
    if cand2.exists():
        return "matrix.json"
    # Fallback: any matrix_*.json
    for p in mod_dir.glob("matrix_*.json"):
        return p.name
    return None

def _stable_module_id(module_name: str, root: Path) -> str:
    h = hashlib.sha256()
    h.update(module_name.encode("utf-8"))
    h.update(str(root.resolve()).encode("utf-8"))
    return f"mod-{h.hexdigest()[:16]}"

def _utc_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _load_json(p: Path) -> Dict[str, Any] | None:
    try:
        if not p.exists():
            return None
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _dump_json(p: Path, obj: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=False)
        f.write("\n")

def _ensure_dirs(mod_dir: Path, write: bool, diffs: List[str]) -> Dict[str, bool]:
    created = {}
    for d in REQUIRED_DIRS:
        path = mod_dir / d
        if not path.exists():
            created[d] = True
            diffs.append(f"  - create dir: {path.as_posix()}")
            if write:
                path.mkdir(parents=True, exist_ok=True)
                # Drop a README stub if docs/tests/config (schema usually gets JSON)
                if d in ("docs", "tests", "config") and not (path / "README.md").exists():
                    (path / "README.md").write_text(README_STUB, encoding="utf-8")
        else:
            created[d] = False
    return created

def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Shallow merge: preserve values in a; fill missing from b. Never delete keys.
    """
    out = dict(a) if a else {}
    for k, v in b.items():
        if k not in out or out[k] in (None, "", [], {}):
            out[k] = v
    return out

def _manifest_defaults(module_name: str, mod_dir: Path, root: Path) -> Dict[str, Any]:
    matriz_contract = _guess_matriz_contract(mod_dir)
    lane_guess = "L2"  # neutral default
    return {
        "name": module_name,
        "description": "",
        "version": "0.1.0",
        "lane": lane_guess,
        "tier": lane_guess,  # readability alias
        "matriz_contract": matriz_contract or "",
        "owner": {"team": "", "codeowners": []},
        "tags": [],
        # 0.01% enrichments
        "module_id": _stable_module_id(module_name, root),
        "matriz_ready": bool(matriz_contract),
        "provenance": {
            "created_at": _utc_ts(),
            "updated_at": _utc_ts()
        },
        "imports_validated": False,
        "dependencies": [],
        "contracts": [matriz_contract] if matriz_contract else []
    }

def _module_schema_defaults(module_name: str) -> Dict[str, Any]:
    """
    Per-module descriptor with light, human-friendly fields.
    Not a global JSON-Schema draft; think of it as module-local schema/config index.
    """
    return {
        "module": module_name,
        "schema_version": "1.0.0",
        "layout": {
            "code_layout": "package-root",
            "paths": {
                "code": ".",
                "config": "config/",
                "tests": "tests/",
                "docs": "docs/",
                "assets": "assets/"
            }
        },
        "runtime": {
            "language": "python",
            "entrypoints": []
        },
        "observability": {
            "required_spans": [],
            "otel_semconv_version": "1.37.0"
        }
    }

def _normalize_module(mod_dir: Path, root: Path, write: bool) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Returns (ok, status_dict, diffs[])
    """
    diffs: List[str] = []
    status: Dict[str, Any] = {"module": mod_dir.name, "path": mod_dir.as_posix()}
    # Skip non-directories or hidden/system folders
    if not mod_dir.is_dir():
        status["skipped"] = "not-a-directory"
        return True, status, diffs
    if mod_dir.name.startswith("."):
        status["skipped"] = "hidden"
        return True, status, diffs

    # Ensure required dirs
    created_map = _ensure_dirs(mod_dir, write, diffs)
    status["created_dirs"] = created_map

    # MANIFEST
    manifest_path = mod_dir / MANIFEST_FILENAME
    legacy_path = mod_dir / "directory_index.json"
    existing = _load_json(manifest_path) or _load_json(legacy_path) or {}

    defaults = _manifest_defaults(mod_dir.name, mod_dir, root)
    merged = _merge(existing, defaults)

    # Light validation
    problems = []
    if merged.get("lane") not in LANES:
        problems.append(f"invalid lane '{merged.get('lane')}', expected one of {LANES}")
    if not merged.get("name"):
        problems.append("missing name")
    if "owner" in merged and not isinstance(merged["owner"].get("codeowners", []), list):
        problems.append("owner.codeowners must be array")

    status["manifest_before"] = existing
    status["manifest_after"] = merged
    status["manifest_path"] = manifest_path.as_posix()
    status["manifest_renamed"] = False

    if legacy_path.exists() and not manifest_path.exists():
        diffs.append(f"  - rename: {legacy_path.name} → {MANIFEST_FILENAME}")
        status["manifest_renamed"] = True
        if write:
            # Write merged manifest at new path; keep legacy until sunset window, but we prefer to move.
            _dump_json(manifest_path, merged)
    else:
        # Write merged manifest if we're allowed AND something changed or it doesn't exist
        if write and (not manifest_path.exists() or merged != existing):
            action = "create" if not manifest_path.exists() else "update"
            diffs.append(f"  - {action} manifest: {manifest_path.as_posix()}")
            _dump_json(manifest_path, merged)

    # MODULE SCHEMA (per-module descriptor)
    schema_path = mod_dir / "schema" / MODULE_SCHEMA_FILENAME
    schema_existing = _load_json(schema_path) or {}
    schema_merged = _merge(schema_existing, _module_schema_defaults(mod_dir.name))

    status["module_schema_before"] = schema_existing
    status["module_schema_after"] = schema_merged
    status["module_schema_path"] = schema_path.as_posix()

    if write and (not schema_path.exists() or schema_merged != schema_existing):
        action = "create" if not schema_path.exists() else "update"
        diffs.append(f"  - {action} schema: {schema_path.as_posix()}")
        _dump_json(schema_path, schema_merged)

    # Stubs if newly created dirs
    for d in ("docs", "tests", "config"):
        rp = mod_dir / d / "README.md"
        if (mod_dir / d).exists() and not rp.exists() and write:
            diffs.append(f"  - stub README: {rp.as_posix()}")
            rp.write_text(README_STUB, encoding="utf-8")

    # Final status flags
    status["problems"] = problems
    status["ok"] = len(problems) == 0
    return status["ok"], status, diffs


def run(root: Path, write: bool, validate_only: bool) -> int:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    modules_root = root
    if not modules_root.exists():
        print(f"[ERROR] Root '{modules_root}' does not exist.", file=sys.stderr)
        return 1

    all_status: List[Dict[str, Any]] = []
    all_diffs: List[str] = []
    failures = 0

    # Treat each immediate child of root as a module directory
    for mod_dir in sorted([p for p in modules_root.iterdir() if p.is_dir() and not p.name.startswith(".")]):
        _ok, status, diffs = _normalize_module(mod_dir, root, write=write and not validate_only)
        all_status.append(status)
        if diffs:
            all_diffs.append(f"- **{mod_dir.name}**")
            all_diffs.extend(diffs)
        if not status.get("ok", False):
            failures += 1

    # Write artifacts
    _dump_json(SYNC_JSON, {"root": str(root), "generated_at": _utc_ts(), "modules": all_status})
    DIFF_MD.write_text(
        "# Module Sitemap Sync - Diff Report\n\n"
        f"- root: `{root.as_posix()}`\n"
        f"- generated_at: `{_utc_ts()}`\n\n"
        + ("\n".join(all_diffs) if all_diffs else "_No changes_\n"),
        encoding="utf-8"
    )

    # Validation mode: fail if any problems
    if validate_only and failures:
        print(f"[FAIL] {failures} module(s) failed validation. See {SYNC_JSON} and {DIFF_MD}.", file=sys.stderr)
        return 1

    # Normal mode: report summary
    changed = "yes" if all_diffs else "no"
    print(f"[OK] sitemap sync complete | changed: {changed} | problems: {failures} | root: {root.as_posix()}")
    print(f"     artifacts: {SYNC_JSON} , {DIFF_MD}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Sync per-module layout + manifest; emit artifacts.")
    ap.add_argument("--root", default=DEFAULT_ROOT, help="Modules root (default: Lukhas)")
    ap.add_argument("--write", action="store_true", help="Apply fixes (create/merge manifests & folders)")
    ap.add_argument("--fix", action="store_true", help="Alias for --write")
    ap.add_argument("--validate", action="store_true", help="Validate only (non-zero on problems)")
    args = ap.parse_args()

    root = Path(args.root)
    write = args.write or args.fix
    validate_only = args.validate

    try:
        rc = run(root=root, write=write, validate_only=validate_only)
    except KeyboardInterrupt:
        print("[INTERRUPTED] sitemap sync aborted", file=sys.stderr)
        rc = 1
    sys.exit(rc)


if __name__ == "__main__":
    main()
