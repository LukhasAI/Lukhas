#!/usr/bin/env python3
"""
🔄 LUKHAS Quantum → QI Complete Migration Script
Systematic migration of all quantum references to QI following naming conventions:
- Files: quantum_*.py → qi_*.py or *_qi_*.py
- Classes: Quantum* → QI*
- Exceptions: post_quantum files are allowed to keep quantum naming
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class QuantumToQIMigrator:
    """Complete migration from quantum to QI naming conventions"""

    def __init__(self, base_path: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas"):
        self.base_path = Path(base_path)
        self.migration_log = []
        self.file_renames = []
        self.class_renames = []
        self.content_updates = []

    def log_action(self, action: str, details: str):
        """Log migration action"""
        self.migration_log.append(f"{action}: {details}")
        print(f"📝 {action}: {details}")

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped from migration"""
        # Skip post_quantum files
        if "post_quantum" in str(file_path):
            return True

        # Skip certain directories
        skip_dirs = {".git", ".venv", "__pycache__", "node_modules"}
        for skip_dir in skip_dirs:
            if skip_dir in file_path.parts:
                return True

        return False

    def find_quantum_files(self) -> List[Path]:
        """Find all files with 'quantum' in name that need renaming"""
        quantum_files = []

        for file_path in self.base_path.rglob("*quantum*"):
            if self.should_skip_file(file_path):
                continue

            if file_path.is_file():
                quantum_files.append(file_path)

        return quantum_files

    def generate_qi_filename(self, quantum_file: Path) -> str:
        """Generate new QI filename following naming conventions"""
        name = quantum_file.name
        stem = quantum_file.stem
        suffix = quantum_file.suffix

        # Pattern: quantum_*.py → qi_*.py
        if name.startswith("quantum_"):
            new_name = name.replace("quantum_", "qi_", 1)

        # Pattern: *_quantum_*.py → *_qi_*.py
        elif "_quantum_" in name:
            new_name = name.replace("_quantum_", "_qi_")

        # Pattern: *quantum*.py → *qi*.py
        elif "quantum" in stem:
            new_name = name.replace("quantum", "qi")

        else:
            # Fallback: add qi_ prefix
            new_name = f"qi_{name}"

        return new_name

    def find_quantum_classes(self) -> List[Tuple[Path, str, str]]:
        """Find all Quantum classes that need renaming to QI"""
        quantum_classes = []

        for py_file in self.base_path.rglob("*.py"):
            if self.should_skip_file(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Find class definitions with Quantum in name
                class_pattern = r'class\s+(\w*Quantum\w*)'
                matches = re.findall(class_pattern, content)

                for class_name in matches:
                    # Generate QI class name
                    qi_class_name = class_name.replace("Quantum", "QI")
                    quantum_classes.append((py_file, class_name, qi_class_name))

            except Exception as e:
                self.log_action("ERROR", f"Failed to read {py_file}: {e}")

        return quantum_classes

    def preview_file_migrations(self):
        """Preview file rename operations"""
        print("\n🔍 QUANTUM FILE MIGRATION PREVIEW")
        print("=" * 60)

        quantum_files = self.find_quantum_files()

        for quantum_file in quantum_files:
            new_name = self.generate_qi_filename(quantum_file)
            new_path = quantum_file.parent / new_name

            print(f"📁 {quantum_file.name}")
            print(f"   → {new_name}")
            print(f"   Path: {quantum_file.parent}")
            print()

            self.file_renames.append((quantum_file, new_path))

        print(f"📊 Total files to rename: {len(quantum_files)}")

    def preview_class_migrations(self):
        """Preview class rename operations"""
        print("\n🧠 QUANTUM CLASS MIGRATION PREVIEW")
        print("=" * 60)

        quantum_classes = self.find_quantum_classes()

        for file_path, old_class, new_class in quantum_classes:
            print(f"📄 {file_path.name}")
            print(f"   class {old_class}")
            print(f"   → class {new_class}")
            print(f"   File: {file_path}")
            print()

            self.class_renames.append((file_path, old_class, new_class))

        print(f"📊 Total classes to rename: {len(quantum_classes)}")

    def preview_content_updates(self):
        """Preview content reference updates"""
        print("\n📝 CONTENT REFERENCE UPDATES PREVIEW")
        print("=" * 60)

        # Common quantum references to update
        reference_patterns = [
            (r'\bquantum_(\w+)', r'qi_\1'),  # quantum_coordinator → qi_coordinator
            (r'\bQuantum([A-Z]\w*)', r'QI\1'),  # QuantumProcessor → QIProcessor
            (r'quantum\.', r'qi.'),  # quantum.module → qi.module
            (r'from quantum ', r'from qi '),  # from quantum import → from qi import
            (r'import quantum', r'import qi'),  # import quantum → import qi
        ]

        affected_files = []

        for py_file in self.base_path.rglob("*.py"):
            if self.should_skip_file(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                updates_needed = []
                for pattern, replacement in reference_patterns:
                    if re.search(pattern, content):
                        updates_needed.append((pattern, replacement))

                if updates_needed:
                    affected_files.append((py_file, updates_needed))

            except Exception as e:
                continue

        for file_path, updates in affected_files[:10]:  # Show first 10
            print(f"📄 {file_path.name}")
            for pattern, replacement in updates:
                print(f"   {pattern} → {replacement}")
            print()

        print(f"📊 Total files with content updates needed: {len(affected_files)}")
        self.content_updates = affected_files

    def generate_migration_plan(self):
        """Generate complete migration plan"""
        print("🎯 QUANTUM → QI MIGRATION PLAN")
        print("=" * 80)

        # Preview all migrations
        self.preview_file_migrations()
        self.preview_class_migrations()
        self.preview_content_updates()

        # Generate summary
        print("\n📊 MIGRATION SUMMARY")
        print("=" * 40)
        print(f"📁 Files to rename: {len(self.file_renames)}")
        print(f"🧠 Classes to rename: {len(self.class_renames)}")
        print(f"📝 Files needing content updates: {len(self.content_updates)}")

        total_operations = len(self.file_renames) + len(self.class_renames) + len(self.content_updates)
        print(f"🎯 Total operations: {total_operations}")

        # Generate migration commands
        print("\n💻 MIGRATION EXECUTION COMMANDS")
        print("=" * 40)
        print("# 1. Backup current state")
        print("git add . && git commit -m '🔄 Pre-migration backup'")
        print()
        print("# 2. Execute migration")
        print("python quantum_to_qi_migrator.py --execute")
        print()
        print("# 3. Verify migration")
        print("python systematic_module_hunter.py")
        print()
        print("# 4. Commit changes")
        print("git add . && git commit -m '🔄 Complete Quantum → QI migration'")

    def execute_migration(self):
        """Execute the actual migration (placeholder)"""
            print("🚀 EXECUTING QUANTUM → QI MIGRATION")
            print("=" * 60)

            executed_operations = 0
            errors = []

            # 1. Execute file renames
            print("🔄 Renaming files...")
            for src, dst in file_renames:
                try:
                    if src.exists():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        src.rename(dst)
                        executed_operations += 1
                        print(f"✅ Renamed: {src.name} → {dst.name}")
                    else:
                        print(f"⚠️  File not found: {src}")
                except Exception as e:
                    error_msg = f"❌ Failed to rename {src} → {dst}: {e}"
                    print(error_msg)
                    errors.append(error_msg)

            # 2. Execute class renames (content updates)
            print("\n🧠 Updating class names...")
            for filepath, old_class, new_class in class_renames:
                try:
                    if filepath.exists():
                        content = filepath.read_text()
                        # Replace class definitions
                        content = re.sub(rf'\bclass {re.escape(old_class)}\b', f'class {new_class}', content)
                        # Replace class references (not inside strings)
                        content = re.sub(rf'\b{re.escape(old_class)}\b', new_class, content)
                        filepath.write_text(content)
                        executed_operations += 1
                        print(f"✅ Updated class: {old_class} → {new_class}")
                    else:
                        print(f"⚠️  File not found: {filepath}")
                except Exception as e:
                    error_msg = f"❌ Failed to update class {old_class} in {filepath}: {e}"
                    print(error_msg)
                    errors.append(error_msg)

            # 3. Execute content reference updates
            print("\n📝 Updating content references...")
            for filepath in content_updates:
                try:
                    if filepath.exists():
                        content = filepath.read_text()
                        original_content = content

                        # Apply all patterns
                        for pattern, replacement in self.content_patterns:
                            content = re.sub(pattern, replacement, content)

                        if content != original_content:
                            filepath.write_text(content)
                            executed_operations += 1
                            print(f"✅ Updated references in: {filepath.name}")
                        else:
                            print(f"ℹ️  No changes needed in: {filepath.name}")
                    else:
                        print(f"⚠️  File not found: {filepath}")
                except Exception as e:
                    error_msg = f"❌ Failed to update content in {filepath}: {e}"
                    print(error_msg)
                    errors.append(error_msg)

            print("\n📊 MIGRATION COMPLETE")
            print("=" * 60)
            print(f"✅ Total operations executed: {executed_operations}")
            print(f"❌ Total errors: {len(errors)}")

            if errors:
                print("\n🚨 ERRORS ENCOUNTERED:")
                for error in errors:
                    print(f"  {error}")

            print("\n🔍 RECOMMENDED NEXT STEPS:")
            print("1. Run systematic_module_hunter.py to verify migration")
            print("2. Run tests to ensure functionality")
            print("3. git add . && git commit -m '🔄 Complete Quantum → QI migration'")    def validate_migration(self):
        """Validate migration was successful"""
        quantum_files = self.find_quantum_files()
        quantum_classes = self.find_quantum_classes()

        print(f"✅ Remaining quantum files: {len(quantum_files)}")
        print(f"✅ Remaining quantum classes: {len(quantum_classes)}")

        if len(quantum_files) == 0 and len(quantum_classes) == 0:
            print("🎉 MIGRATION COMPLETE - No quantum references remaining!")
        else:
            print("⚠️  Migration incomplete - quantum references still exist")

def main():
    """Main migration function"""
    import sys

    migrator = QuantumToQIMigrator()

    if "--execute" in sys.argv:
        migrator.execute_migration()
    elif "--validate" in sys.argv:
        migrator.validate_migration()
    else:
        migrator.generate_migration_plan()

if __name__ == "__main__":
    main()
