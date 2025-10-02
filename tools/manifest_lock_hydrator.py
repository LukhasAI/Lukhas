#!/usr/bin/env python3
"""
LUKHAS Manifest Lock Hydrator
Generates module.manifest.lock.json for each manifest with:
- Resolved module path (absolute from repo root)
- SHA256 hashes of manifest + all .py/.json/.yaml files in module
- Git commit SHA
- Timestamp
- Normalized entrypoints, lanes, status, owner, SLOs
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".venv", "artifacts", "node_modules", ".git", "__pycache__"}


def sha256_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def collect_module_files(module_dir: Path) -> list[Path]:
    """Collect all .py, .json, .yaml files in module directory."""
    files = []
    for pattern in ["**/*.py", "**/*.json", "**/*.yaml", "**/*.yml"]:
        for f in module_dir.glob(pattern):
            # Skip files in excluded directories
            if any(part in SKIP_DIRS for part in f.parts):
                continue
            if f.is_file():
                files.append(f)
    return sorted(files)


def generate_lockfile(manifest_path: Path) -> dict:
    """Generate lockfile data for a manifest."""
    module_dir = manifest_path.parent

    # Load manifest
    with manifest_path.open() as f:
        manifest_data = json.load(f)

    # Compute module path relative to repo root
    try:
        rel_path = module_dir.relative_to(ROOT)
        module_path = str(rel_path)
    except ValueError:
        module_path = str(module_dir)

    # Compute hashes
    file_hashes = {}

    # Hash the manifest itself
    file_hashes["module.manifest.json"] = sha256_file(manifest_path)

    # Hash all module files
    for f in collect_module_files(module_dir):
        try:
            rel_to_module = f.relative_to(module_dir)
            file_hashes[str(rel_to_module)] = sha256_file(f)
        except ValueError:
            continue

    # Get git commit
    git_commit = get_git_commit()

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Normalize key fields from manifest
    lockfile_data = {
        "module": manifest_data.get("module", ""),
        "module_path": module_path,
        "schema_version": manifest_data.get("schema_version", "1.0.0"),
        "status": manifest_data.get("metadata", {}).get("status", "unknown"),
        "owner": {
            "team": manifest_data.get("ownership", {}).get("team", ""),
            "codeowners": manifest_data.get("ownership", {}).get("codeowners", []),
        },
        "runtime": {
            "language": manifest_data.get("runtime", {}).get("language", ""),
            "entrypoints": sorted(manifest_data.get("runtime", {}).get("entrypoints", [])),
        },
        "matrix": {
            "lane": manifest_data.get("matrix", {}).get("lane", ""),
            "gates_profile": manifest_data.get("matrix", {}).get("gates_profile", ""),
        },
        "slos": {
            "availability": manifest_data.get("performance", {}).get("sla", {}).get("availability"),
            "latency_p95_ms": manifest_data.get("performance", {}).get("sla", {}).get("latency_p95_ms"),
            "latency_p99_ms": manifest_data.get("performance", {}).get("sla", {}).get("latency_p99_ms"),
        },
        "hashes": dict(sorted(file_hashes.items())),
        "git_commit": git_commit,
        "generated_at": timestamp,
    }

    return lockfile_data


def iter_manifests(start: Path) -> list[Path]:
    """Find all module.manifest.json files, skipping excluded directories."""
    manifests = []
    for manifest in start.rglob("module.manifest.json"):
        # Skip if in excluded directories
        if any(part in SKIP_DIRS for part in manifest.parts):
            continue
        manifests.append(manifest)
    return sorted(manifests)


def main():
    ap = argparse.ArgumentParser(description="Generate lockfiles for LUKHAS manifests")
    ap.add_argument("path", nargs="?", help="Path to a module directory or manifest file")
    ap.add_argument("--all", action="store_true", help="Process all manifests in repository")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be generated without writing")
    args = ap.parse_args()

    targets: list[Path]
    if args.all or not args.path:
        targets = iter_manifests(ROOT)
    else:
        p = Path(args.path).resolve()
        if p.is_dir():
            manifest = p / "module.manifest.json"
            if not manifest.exists():
                print(f"❌ No manifest found in {p}", file=sys.stderr)
                sys.exit(1)
            targets = [manifest]
        elif p.name == "module.manifest.json":
            targets = [p]
        else:
            print(f"❌ Invalid path: {args.path}", file=sys.stderr)
            sys.exit(1)

    if not targets:
        print("⚠️  No manifests found.")
        sys.exit(0)

    print("🔒 LUKHAS Manifest Lock Hydrator")
    print(f"Repository: {ROOT}")
    print(f"Git commit: {get_git_commit()}")
    print("-" * 60)

    generated = 0
    errors = []

    for manifest_path in targets:
        try:
            rel_path = manifest_path.relative_to(ROOT)
        except ValueError:
            rel_path = manifest_path

        try:
            lockfile_data = generate_lockfile(manifest_path)
            lockfile_path = manifest_path.parent / "module.manifest.lock.json"

            if args.dry_run:
                print(f"🔍 {rel_path}")
                print(f"   → Would generate: {lockfile_path.relative_to(ROOT)}")
                print(f"   → Files hashed: {len(lockfile_data['hashes'])}")
            else:
                # Write lockfile with sorted keys for deterministic output
                with lockfile_path.open("w") as f:
                    json.dump(lockfile_data, f, indent=2, sort_keys=True)
                print(f"✅ {rel_path}")
                print(f"   → {lockfile_path.relative_to(ROOT)} ({len(lockfile_data['hashes'])} files hashed)")

            generated += 1

        except Exception as e:
            print(f"❌ {rel_path}")
            print(f"   Error: {e}")
            errors.append((rel_path, str(e)))

    print("\n📊 Summary:")
    print(f"   Processed: {generated}/{len(targets)} manifests")
    if errors:
        print(f"   ❌ Errors: {len(errors)}")
        for path, err in errors:
            print(f"      - {path}: {err}")
        sys.exit(1)
    else:
        print("   ✅ All lockfiles generated successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
