#!/usr/bin/env python3
"""
🧹 LUKHAS Security Backup Cleanup
=================================
Consolidates and cleans up security backup directories created during
the automated security fixing process.

Keeps the important requirements.txt backups and removes redundant
individual file backups.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path


def main():
    """Clean up security backup directories"""
    print("🧹 LUKHAS Security Backup Cleanup")
    print("=" * 40)

    # Find all security backup directories
    backup_dirs = [d for d in os.listdir(".") if d.startswith(".security_backup_20250822_")]
    backup_dirs.sort()

    print(f"📊 Found {len(backup_dirs)} security backup directories")

    if not backup_dirs:
        print("✅ No security backup directories to clean up")
        return

    # Create consolidated backup directory
    consolidated_dir = f".security_backup_consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(consolidated_dir, exist_ok=True)

    requirements_backups = []
    individual_backups = []

    # Categorize backups
    for backup_dir in backup_dirs:
        backup_path = Path(backup_dir)
        if not backup_path.exists():
            continue

        files = list(backup_path.glob("*"))

        # Check if this contains requirements.txt files
        has_requirements = any("requirements.txt" in f.name for f in files)

        if has_requirements:
            requirements_backups.append(backup_dir)
            print(f"📋 Requirements backup: {backup_dir}")
        else:
            individual_backups.append(backup_dir)

    print(f"\n📋 Requirements backups: {len(requirements_backups)}")
    print(f"📄 Individual file backups: {len(individual_backups)}")

    # Preserve important requirements backups
    if requirements_backups:
        print("\n💾 Consolidating requirements backups...")

        # Keep the first and last requirements backup
        important_backups = [requirements_backups[0]]
        if len(requirements_backups) > 1:
            important_backups.append(requirements_backups[-1])

        for backup_dir in important_backups:
            dest_dir = Path(consolidated_dir) / backup_dir
            dest_dir.mkdir(exist_ok=True)

            # Copy files
            for file_path in Path(backup_dir).glob("*"):
                if file_path.is_file():
                    shutil.copy2(file_path, dest_dir / file_path.name)
                    print(f"  📋 Preserved: {backup_dir}/{file_path.name}")

    # Remove all backup directories
    print(f"\n🗑️  Removing {len(backup_dirs)} backup directories...")
    removed_count = 0
    for backup_dir in backup_dirs:
        try:
            shutil.rmtree(backup_dir)
            removed_count += 1
            print(f"  ✅ Removed: {backup_dir}")
        except Exception as e:
            print(f"  ❌ Failed to remove {backup_dir}: {e}")

    print("\n📊 Cleanup Summary:")
    print(f"  🗑️  Removed directories: {removed_count}")
    print(f"  💾 Preserved backups: {consolidated_dir}")
    print(f"  📋 Important files preserved: {len(requirements_backups)} * 3} requirements.txt files")

    # Show space saved
    if removed_count > 0:
        print("\n💾 Space cleanup completed!")
        print(f"  📁 Consolidated backup location: {consolidated_dir}")
        print(f"  🧹 Removed {removed_count} redundant backup directories")

    # Create cleanup report
    report_file = f"security_backup_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        f.write("Security Backup Cleanup Report\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"Original backup directories: {len(backup_dirs)}\n")
        f.write(f"Requirements backups found: {len(requirements_backups)}\n")
        f.write(f"Individual file backups: {len(individual_backups)}\n")
        f.write(f"Directories removed: {removed_count}\n")
        f.write(f"Consolidated backup: {consolidated_dir}\n\n")
        f.write("Preserved files:\n")
        for backup_dir in requirements_backups[:2]:  # First and last
            f.write(f"  - {backup_dir}/ (requirements.txt files)\n")

    print(f"📄 Cleanup report saved: {report_file}")


if __name__ == "__main__":
    main()