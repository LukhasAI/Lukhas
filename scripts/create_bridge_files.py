#!/usr/bin/env python3
"""
Create actual bridge .py files for all 786 bridge gaps.
This implements @codex's feedback: create explicit bridge modules (e.g., consciousness/dream/expand/mesh.py)
that delegate to labs.* modules, supporting both import styles:
  - from consciousness.dream.expand import mesh  (attribute-style)
  - import consciousness.dream.expand.mesh       (submodule-style)
"""
import subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path(".")
LABS_DIR = ROOT / "labs"

def get_bridge_gaps():
    """Run find_bridge_gaps.py and parse output to get modules needing bridges."""
    result = subprocess.run(
        ["python3", "scripts/find_bridge_gaps.py"],
        capture_output=True,
        text=True
    )

    gaps_by_dir = defaultdict(list)
    current_dir = None

    for line in result.stdout.splitlines():
        if "/ needs these modules:" in line:
            # Extract directory path from line like "./consciousness/dream/expand/ needs these modules:"
            current_dir = line.split("/")[0].strip(".")
            if not current_dir:
                # Handle root-level directories
                parts = line.split("/")
                if len(parts) > 1:
                    current_dir = parts[0].strip()
        elif line.strip().startswith("- "):
            module = line.strip()[2:].strip()
            if current_dir:
                gaps_by_dir[current_dir].append(module)

    return gaps_by_dir

def create_bridge_file(bridge_dir: Path, module_name: str, labs_module_path: str, dry_run=False):
    """
    Create a bridge .py file that re-exports from labs.*.

    Args:
        bridge_dir: Directory where bridge file should be created (e.g., consciousness/dream/expand)
        module_name: Name of module (e.g., "mesh")
        labs_module_path: Full labs import path (e.g., "labs.consciousness.dream.expand.mesh")
        dry_run: If True, only print what would be created
    """
    bridge_file = bridge_dir / f"{module_name}.py"

    # Generate bridge file content
    content = f'''"""Bridge module for {bridge_dir}.{module_name} → {labs_module_path}"""
from __future__ import annotations

from {labs_module_path} import *  # noqa: F401, F403
'''

    if dry_run:
        print(f"[DRY RUN] Would create: {bridge_file}")
        print(f"  Content: {content[:100]}...")
        return None

    # Create directory if needed
    bridge_dir.mkdir(parents=True, exist_ok=True)

    # Write bridge file
    bridge_file.write_text(content, encoding="utf-8")
    print(f"✅ Created: {bridge_file}")
    return bridge_file

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Don't actually create files")
    parser.add_argument("--limit", type=int, help="Limit number of files created")
    args = parser.parse_args()

    print("🔍 Finding bridge gaps...")
    gaps_by_dir = get_bridge_gaps()

    total_modules = sum(len(m) for m in gaps_by_dir.values())
    print(f"📊 Found gaps in {len(gaps_by_dir)} directories")
    print(f"📦 Total modules: {total_modules}")
    print()

    files_created = []
    count = 0

    for dir_path, modules in sorted(gaps_by_dir.items()):
        # Parse directory path
        dir_path = dir_path.lstrip("./")
        bridge_dir = ROOT / dir_path if dir_path else ROOT

        print(f"\n📁 Processing {bridge_dir}/ ({len(modules)} modules)")

        for module_name in sorted(modules):
            # Construct labs module path
            if dir_path:
                labs_module_path = f"labs.{dir_path.replace('/', '.')}.{module_name}"
            else:
                labs_module_path = f"labs.{module_name}"

            # Verify labs module exists
            labs_file = LABS_DIR / dir_path / f"{module_name}.py" if dir_path else LABS_DIR / f"{module_name}.py"
            if not labs_file.exists():
                print(f"  ⚠️  Skipping {module_name} (labs file not found: {labs_file})")
                continue

            bridge_file = create_bridge_file(bridge_dir, module_name, labs_module_path, args.dry_run)
            if bridge_file:
                files_created.append(str(bridge_file))

            count += 1
            if args.limit and count >= args.limit:
                break

        if args.limit and count >= args.limit:
            break

    print()
    print(f"✅ Created {len(files_created)} bridge files")

    # Write summary
    if not args.dry_run and files_created:
        summary_file = ROOT / "release_artifacts" / "repo_audit_v2" / "bridge_files_created.txt"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with summary_file.open("w") as f:
            f.write("# Bridge Files Created\n\n")
            f.write(f"**Total:** {len(files_created)} files\n\n")
            for file_path in files_created:
                f.write(f"{file_path}\n")

        print(f"📝 Summary written to {summary_file}")

if __name__ == "__main__":
    main()
