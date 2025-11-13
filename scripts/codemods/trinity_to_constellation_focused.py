#!/usr/bin/env python3
"""
Focused Trinity to Constellation migration script
Targets specific files with Trinity references for careful replacement
"""
import os
import re
import shutil
import sys
from pathlib import Path


def get_trinity_python_files():
    """Get Python files that still contain Trinity references"""
    trinity_files = []
    base_dir = Path(".")

    # Target specific directories to avoid .venv and binary files
    target_dirs = ["candidate", "lukhas", "modulation", "mcp-lukhas-sse"]

    for target_dir in target_dirs:
        if (base_dir / target_dir).exists():
            for py_file in (base_dir / target_dir).rglob("*.py"):
                if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                try:
                    with open(py_file, encoding='utf-8') as f:
                        content = f.read()
                        if "Trinity" in content:
                            trinity_files.append(py_file)
                except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                    continue

    return trinity_files

def safe_replace_trinity_terms(content: str) -> str:
    """Safely replace Trinity terms with Constellation equivalents"""

    # Class and type names
    patterns = [
        (r'\bTrinityComponent\b', 'ConstellationComponent'),
        (r'\bTrinityInteraction\b', 'ConstellationInteraction'),
        (r'\bTrinityHealthStatus\b', 'ConstellationHealthStatus'),
        (r'\bTrinityReport\b', 'ConstellationReport'),
        (r'\bTrinityFrameworkMonitor\b', 'ConstellationFrameworkMonitor'),

        # Method and variable names
        (r'\btrinty_interactions\b', 'constellation_interactions'),
        (r'\btrinty_components\b', 'constellation_components'),
        (r'\btrinty_component\b', 'constellation_component'),
        (r'\btrinty_impact\b', 'constellation_impact'),
        (r'\btrinity_framework_monitor\b', 'constellation_framework_monitor'),

        # Method names with underscores
        (r'\b_trinity_(\w+)', r'_constellation_\1'),
        (r'\brecord_trinity_interaction\b', 'record_constellation_interaction'),
        (r'\bget_trinity_(\w+)', r'get_constellation_\1'),

        # Documentation and comments
        (r'\bTrinity Framework\b', 'Constellation Framework'),
        (r'\bTrinity component\b', 'Constellation component'),
        (r'\bTrinity monitoring\b', 'Constellation monitoring'),
    ]

    result = content
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result

def process_file(file_path):
    """Process a single file for Trinity to Constellation migration"""
    try:
        # Create backup
        backup_path = f"{file_path}.trinity_backup"
        shutil.copy2(file_path, backup_path)

        # Read content
        with open(file_path, encoding='utf-8') as f:
            content = f.read()

        # Apply transformations
        new_content = safe_replace_trinity_terms(content)

        # Only write if content changed
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            # Remove backup if no changes
            os.remove(backup_path)
            return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    """Main migration function"""
    print("🔄 Starting focused Trinity to Constellation migration...")

    trinity_files = get_trinity_python_files()
    print(f"📝 Found {len(trinity_files)} Python files with Trinity references")

    if not trinity_files:
        print("✅ No Trinity references found in Python files!")
        return 0

    updated_count = 0
    for file_path in trinity_files:
        if process_file(file_path):
            updated_count += 1

    print(f"🎯 Migration complete: {updated_count}/{len(trinity_files)} files updated")

    if updated_count > 0:
        print("\n📋 Next steps:")
        print("1. Test the system to ensure no broken imports")
        print("2. Update any remaining Trinity references in documentation")
        print("3. Remove .trinity_backup files when satisfied")

    return 0

if __name__ == "__main__":
    sys.exit(main())
