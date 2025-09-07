#!/usr/bin/env python3
"""
Complete Codebase Hygiene - Remove ALL redundant prefixes
"""

import re
import shutil
from datetime import datetime
from pathlib import Path


def complete_cleanup():
    """Remove all remaining _, lukhas_, and other redundant prefixes"""

    workspace = Path("/Users/agi_dev/LOCAL-REPOS/Lukhas"
    changes = []

    print("🧹 COMPLETE HYGIENE CLEANUP")
    print("=" * 60)

    # Find and rename all _ prefixed files
    print("\n📄 Removing _ prefixes from all files...")
    for py_file in workspace.rglob("_*.py"):
        new_name = py_file.name.replace("_", "").lower()
        new_path = py_file.parent / new_name

        if not new_path.exists():
            print(f"  ✅ {py_file.name} → {new_name}")
            shutil.move(str(py_file), str(new_path))
            changes.append(
                (
                    str(py_file.relative_to(workspace)),
                    str(new_path.relative_to(workspace)),
                )
            )

    # Find and rename any remaining lukhas_ prefixed files
    print("\n📄 Removing lukhas_ prefixes from all files...")
    for py_file in workspace.rglob("lukhas_*.py"):
        new_name = (
            py_file.name.replace("lukhas_", "")
            .replace("LUKHAS_", "")
            .replace("Lukhas_", "")
        )
        new_path = py_file.parent / new_name

        if not new_path.exists():
            print(f"  ✅ {py_file.name} → {new_name}")
            shutil.move(str(py_file), str(new_path))
            changes.append(
                (
                    str(py_file.relative_to(workspace)),
                    str(new_path.relative_to(workspace)),
                )
            )

    # Rename any remaining lukhas directories
    print("\n📁 Removing lukhas prefix from remaining directories...")
    lukhas_dirs = [
        d for d in workspace.iterdir() if d.is_dir() and d.name.startswith("lukhas")
    ]

    for old_dir in lukhas_dirs:
        new_name = old_dir.name.replace("lukhas_", "").replace("lukhas", "system")
        new_path = workspace / new_name

        if not new_path.exists():
            print(f"  ✅ {old_dir.name} → {new_name}")
            shutil.move(str(old_dir), str(new_path))
            changes.append(
                (
                    str(old_dir.relative_to(workspace)),
                    str(new_path.relative_to(workspace)),
                )
            )

    # Special case renames for clarity
    special_renames = {
        "tools/analysis/_current_connectivity_analysis.py": "tools/analysis/connectivity_analysis.py",
        "tools/analysis/_root_directory_audit_fixed.py": "tools/analysis/root_audit_fixed.py",
        "tools/analysis/lambda_id_audit.py": "tools/analysis/lambda_identity_audit.py",
    }

    print("\n📄 Applying special renames for clarity...")
    for old_name, new_name in special_renames.items():
        old_path = workspace / old_name
        new_path = workspace / new_name

        if old_path.exists() and not new_path.exists():
            print(f"  ✅ {old_name} → {new_name}")
            shutil.move(str(old_path), str(new_path))
            changes.append((old_name, new_name))

    # Update all imports
    print("\n🔄 Updating imports...")
    updated_files = 0

    for py_file in workspace.rglob("*.py"):
        if ".hygiene_backup" in str(py_file) or "._cleanup" in str(py_file):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            original = content

            # Update imports for renamed files
            for old, new in changes:
                old_module = old.replace("/", ".").replace(".py", "")
                new_module = new.replace("/", ".").replace(".py", "")

                content = content.replace(f"from {old_module}", f"from {new_module}")
                content = content.replace(
                    f"import {old_module}", f"import {new_module}"
                )

            # Remove lukhas_ prefixes from imports
            content = re.sub(r"from system_(\w+)", r"from \1", content)
            content = re.sub(r"import system_(\w+)", r"import \1", content)

            # Remove _ prefixes from imports
            content = re.sub(
                r"from tools\.analysis\._(\w+)", r"from tools.analysis.\1", content
            )
            content = re.sub(
                r"import tools\.analysis\._(\w+)",
                r"import tools.analysis.\1",
                content,
            )

            if content != original:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)
                updated_files += 1

        except Exception as e:
            print(f"  ⚠️  Error updating {py_file}: {e}")

    print(f"  ✅ Updated imports in {updated_files} files")

    # Final summary
    print("\n" + "=" * 60)
    print("📊 CLEANUP SUMMARY")
    print("=" * 60)
    print(f"Total renames: {len(changes)}")
    print(f"Import updates: {updated_files} files")
    print("\n✅ Complete hygiene cleanup finished!")

    # Save change log
    log_path = workspace / "COMPLETE_HYGIENE_LOG.txt"
    with open(log_path, "w") as f:
        f.write(f"Complete Hygiene Cleanup - {datetime.now(timezone.utc).isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        for old, new in changes:
            f.write(f"{old} → {new}\n")

    print(f"\n📄 Change log saved to: {log_path}")


if __name__ == "__main__":
    complete_cleanup()
