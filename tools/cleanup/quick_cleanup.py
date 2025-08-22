#!/usr/bin/env python3
"""
Quick Cleanup Script for LUKHAS
====================================
Focuses on main module duplicates and conflicts.
"""

import shutil
from pathlib import Path
from typing import List


def find_backup_directories() -> List[Path]:
    """Find all backup directories that can be archived"""
    backups = []

    patterns = [
        "*_backup_*",
        ".hygiene_backup_*",
        ".identity_backup_*",
        ".event_bus_backup_*",
        "._cleanup_archive",
    ]

    for pattern in patterns:
        backups.extend(Path(".").glob(pattern))

    return backups


def find_duplicate_modules() -> dict:
    """Find modules that exist in multiple places"""
    duplicates = {}

    # Common duplicate patterns
    module_patterns = [
        ("identity", ["identity", "governance/identity", "identity_enhanced"]),
        ("memory", ["memory", "consciousness/memory", "memory/systems"]),
        ("emotion", ["emotion", "consciousness/emotion", "bio/emotion"]),
        ("dream", ["dream", "consciousness/dream", "creativity/dream"]),
        ("quantum", ["quantum", "qim", "quantum_computing"]),
    ]

    for module_name, locations in module_patterns:
        existing = []
        for loc in locations:
            path = Path(loc)
            if path.exists():
                existing.append(str(path))

        if len(existing) > 1:
            duplicates[module_name] = existing

    return duplicates


def cleanup_imports() -> int:
    """Clean up broken imports in Python files"""
    fixed = 0

    # Common import fixes
    replacements = [
        ("from identity.interface", "from lukhas.governance.identity.interface"),
        ("from identity.core", "from lukhas.governance.identity.core"),
        ("from identity.auth", "from lukhas.governance.identity.auth"),
        ("import identity.", "import lukhas.governance.identity."),
    ]

    # Only fix in main modules, not backups
    main_modules = [
        "core",
        "consciousness",
        "governance",
        "orchestration",
        "bridge",
        "api",
    ]

    for module in main_modules:
        if not Path(module).exists():
            continue

        for py_file in Path(module).rglob("*.py"):
            try:
                content = py_file.read_text()
                original = content

                for old, new in replacements:
                    content = content.replace(old, new)

                if content != original:
                    py_file.write_text(content)
                    fixed += 1
                    print(f"  Fixed imports in: {py_file}")

            except Exception as e:
                print(f"  Error fixing {py_file}: {e}")

    return fixed


def archive_backups(backups: List[Path]) -> int:
    """Archive backup directories"""
    archive_dir = Path("archive/backups")
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived = 0
    for backup in backups:
        if backup.exists():
            dest = archive_dir / backup.name
            try:
                shutil.move(str(backup), str(dest))
                print(f"  Archived: {backup} -> {dest}")
                archived += 1
            except Exception as e:
                print(f"  Failed to archive {backup}: {e}")

    return archived


def consolidate_duplicates(duplicates: dict) -> dict:
    """Suggest consolidation for duplicate modules"""
    suggestions = {}

    for module_name, locations in duplicates.items():
        # Determine primary location
        if f"governance/{module_name}" in locations:
            primary = f"governance/{module_name}"
        elif module_name in locations:
            primary = module_name
        else:
            primary = locations[0]

        suggestions[module_name] = {
            "primary": primary,
            "duplicates": [loc for loc in locations if loc != primary],
            "action": f"Consolidate into {primary}",
        }

    return suggestions


def main():
    """Run quick cleanup"""
    print("🧹 LUKHAS  Quick Cleanup")
    print("=" * 60)

    # Find backups
    print("\n📦 Finding backup directories...")
    backups = find_backup_directories()
    print(f"  Found {len(backups)} backup directories")

    # Find duplicates
    print("\n🔍 Finding duplicate modules...")
    duplicates = find_duplicate_modules()
    print(f"  Found {len(duplicates)} modules with duplicates")

    # Fix imports
    print("\n🔧 Fixing imports...")
    fixed = cleanup_imports()
    print(f"  Fixed {fixed} import statements")

    # Archive backups
    if backups:
        print("\n📁 Archiving backups...")
        archived = archive_backups(backups)
        print(f"  Archived {archived} directories")

    # Suggest consolidations
    if duplicates:
        print("\n💡 Consolidation Suggestions:")
        suggestions = consolidate_duplicates(duplicates)
        for module_name, info in suggestions.items():
            print(f"\n  {module_name}:")
            print(f"    Primary: {info['primary']}")
            print(f"    Duplicates: {', '.join(info['duplicates'])}")
            print(f"    Action: {info['action']}")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Cleanup Complete!")
    print(f"  • Fixed {fixed} imports")
    print(f"  • Archived {len(backups)} backup directories")
    print(f"  • Identified {len(duplicates)} modules for consolidation")

    # Create cleanup report
    report = {
        "timestamp": str(Path.cwd()),
        "backups_archived": len(backups),
        "imports_fixed": fixed,
        "duplicates_found": duplicates,
        "suggestions": suggestions if duplicates else {},
    }

    report_path = Path("docs/reports/cleanup_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_path}")


if __name__ == "__main__":
    main()
