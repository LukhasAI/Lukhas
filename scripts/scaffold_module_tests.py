#!/usr/bin/env python3
"""T4/0.01% Module Test Scaffolder
Deterministic, idempotent, append-only ledger, dry-run by default.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(".")
LEDGER = ROOT / "manifests/.ledger/test_scaffold.ndjson"
TPL_DIR = ROOT / "templates/tests"

# Default footprint (fast to run)
REQUIRED = [
    "tests/conftest.py",
    "tests/test_smoke.py",
    "tests/test_unit.py",
    # Uncomment if you want a placeholder integration test by default:
    # "tests/test_integration.py",
]


def load_manifest(p: Path) -> dict:
    """Load module.manifest.json with safe defaults."""
    try:
        d = json.loads(p.read_text())
    except Exception as e:
        print(f"⚠️  Failed to parse {p}: {e}")
        return {}
    d.setdefault("module", p.parent.name)
    return d


def render(template: str, ctx: dict) -> str:
    """Very simple mustache-ish replacer for {{key}}."""

    def sub(m):
        return str(ctx.get(m.group(1).strip(), ""))

    return re.sub(r"{{\s*([^}]+)\s*}}", sub, template)


def write_if_missing(dst: Path, content: str, apply: bool) -> bool:
    """Write file only if it doesn't exist. Return True if created."""
    if dst.exists():
        return False
    if not apply:
        print(f"  ~ would create {dst}")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")
    return True


def append_ledger(rec: dict):
    """Append record to test scaffold ledger (NDJSON)."""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Scaffold per-module tests (dry-run by default)"
    )
    ap.add_argument(
        "--module",
        help="module folder name or path (repeat to run multiple)",
        action="append",
    )
    ap.add_argument(
        "--apply", action="store_true", help="write files to disk"
    )
    ap.add_argument(
        "--with-integration",
        action="store_true",
        help="also create tests/test_integration.py",
    )
    ap.add_argument(
        "--verbose", "-v", action="store_true", help="verbose output"
    )
    args = ap.parse_args()

    required = REQUIRED.copy()
    if args.with_integration and "tests/test_integration.py" not in required:
        required.append("tests/test_integration.py")

    # Determine targets
    targets = []
    if args.module:
        for m in args.module:
            mdir = ROOT / m
            if not mdir.exists():
                # Try finding by name
                manifests = list(ROOT.rglob(f"{m}/module.manifest.json"))
                if manifests:
                    mdir = manifests[0].parent
                else:
                    print(f"❌ Module not found: {m}")
                    continue
            targets.append(mdir)
    else:
        # All modules with manifests
        targets = sorted([p.parent for p in ROOT.rglob("module.manifest.json")])

    print(f"{'🔧 DRY-RUN' if not args.apply else '✅ APPLY'} mode")
    print(f"Found {len(targets)} module(s) to process\n")

    total_created = 0
    for mdir in sorted(set(targets)):
        mf = mdir / "module.manifest.json"
        if not mf.exists():
            if args.verbose:
                print(f"! skipping {mdir}: no module.manifest.json")
            continue

        manifest = load_manifest(mf)
        if not manifest:
            continue

        module_name = manifest.get("module", mdir.name)
        ctx = {"module_fqn": module_name}

        created = []
        for rel in required:
            tpl_path = TPL_DIR / Path(rel).name
            if not tpl_path.exists():
                if args.verbose:
                    print(f"  ⚠️  Template missing: {tpl_path}")
                continue

            tpl = tpl_path.read_text(encoding="utf-8")
            out = render(tpl, ctx)

            if write_if_missing(mdir / rel, out, args.apply):
                created.append(rel)
                total_created += 1

        if created:
            if args.apply:
                append_ledger(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "module": module_name,
                        "created": created,
                    }
                )
            status = "✅" if args.apply else "~"
            print(f"{status} {mdir.name}: created {len(created)} test files")
            if args.verbose:
                for f in created:
                    print(f"    + {f}")
        else:
            if args.verbose:
                print(f"= {mdir.name}: tests footprint OK")

    print(f"\n{'Would create' if not args.apply else 'Created'} {total_created} files")
    if not args.apply:
        print("💡 Run with --apply to write files")
    return 0


if __name__ == "__main__":
    exit(main())
