#!/usr/bin/env python3
"""
🔄 QUANTUM TO QI MIGRATION SCRIPT
Complete systematic migration from quantum naming to qi naming conventions

LUKHAS AI Agent Army - Trinity Framework Migration
⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import re
from pathlib import Path


class QIToQIMigrator:
    """Migrates all quantum references to qi following strict naming conventions"""

    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.file_renames: list[tuple[Path, Path]] = []
        self.class_renames: list[tuple[Path, str, str]] = []
        self.content_updates: list[Path] = []

        # Naming patterns to migrate
        self.file_patterns = [
            (r'quantum_(.+\.py)$', r'qi_\1'),
            (r'(.+)_quantum_(.+\.py)$', r'\1_qi_\2'),
            (r'quantum_(.+\.json)$', r'qi_\1'),
            (r'(.+)_quantum_(.+\.json)$', r'\1_qi_\2'),
            (r'quantum_(.+\.yaml)$', r'qi_\1'),
            (r'(.+)_quantum_(.+\.yaml)$', r'\1_qi_\2'),
        ]

        self.content_patterns = [
            (r'\bquantum_(\w+)', r'qi_\1'),
            (r'\bQuantum([A-Z]\w*)', r'QI\1'),
            (r'quantum\.', r'qi.'),
            (r'from quantum ', r'from qi '),
            (r'import quantum', r'import qi'),
        ]

        # Files to preserve (never rename)
        self.preserve_files = {
            'post_quantum',
            'quantum_safe',
            'post_quantum_cryptography'
        }

    def should_preserve_file(self, filepath: Path) -> bool:
        """Check if file should be preserved from renaming"""
        filename = filepath.name.lower()
        return any(preserve in filename for preserve in self.preserve_files)

    def find_quantum_files(self) -> list[Path]:
        """Find all files containing quantum in their names"""
        quantum_files = []

        # Python files
        for pattern in ['**/quantum_*.py', '**/*_quantum_*.py', '**/quantum*.py']:
            for filepath in self.root.glob(pattern):
                if not self.should_preserve_file(filepath):
                    quantum_files.append(filepath)

        # JSON files
        for pattern in ['**/quantum_*.json', '**/*_quantum_*.json', '**/quantum*.json']:
            for filepath in self.root.glob(pattern):
                if not self.should_preserve_file(filepath):
                    quantum_files.append(filepath)

        # HTML files (test reports)
        for pattern in ['**/*quantum*.html']:
            for filepath in self.root.glob(pattern):
                quantum_files.append(filepath)

        return sorted(set(quantum_files))

    def find_quantum_classes(self) -> list[tuple[Path, str]]:
        """Find all class definitions with Quantum in their names"""
        quantum_classes = []

        for py_file in self.root.glob('**/*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                # Find class definitions
                class_matches = re.finditer(r'class\s+(Quantum\w+)', content)
                for match in class_matches:
                    class_name = match.group(1)
                    if class_name != 'Quantum':  # Preserve base 'Quantum' class if exists
                        quantum_classes.append((py_file, class_name))
            except (UnicodeDecodeError, PermissionError):
                continue

        return quantum_classes

    def find_files_with_quantum_references(self) -> list[Path]:
        """Find all files that reference quantum in content"""
        files_with_refs = []

        for py_file in self.root.glob('**/*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                if re.search(r'\bquantum_\w+|\bQuantum[A-Z]\w*|from quantum|import quantum|\bquantum\.', content):
                    files_with_refs.append(py_file)
            except (UnicodeDecodeError, PermissionError):
                continue

        return files_with_refs

    def generate_file_renames(self) -> None:
        """Generate all file rename operations"""
        quantum_files = self.find_quantum_files()

        for old_path in quantum_files:
            new_name = old_path.name

            # Apply file patterns
            for pattern, replacement in self.file_patterns:
                new_name = re.sub(pattern, replacement, new_name)

            if new_name != old_path.name:
                new_path = old_path.parent / new_name
                self.file_renames.append((old_path, new_path))

    def generate_class_renames(self) -> None:
        """Generate all class rename operations"""
        quantum_classes = self.find_quantum_classes()

        for filepath, old_class in quantum_classes:
            # Convert Quantum* to QI*
            if old_class.startswith('Quantum'):
                new_class = 'QI' + old_class[7:]  # Remove 'Quantum' and add 'QI'
                self.class_renames.append((filepath, old_class, new_class))

    def generate_content_updates(self) -> None:
        """Generate all content update operations"""
        self.content_updates = self.find_files_with_quantum_references()

    def preview_migration(self) -> None:
        """Show preview of all migration operations"""
        print("🔄 QUANTUM TO QI MIGRATION PREVIEW")
        print("=" * 60)

        # Generate all operations
        self.generate_file_renames()
        self.generate_class_renames()
        self.generate_content_updates()

        # Show file renames
        if self.file_renames:
            print("\n📁 FILE RENAME PREVIEW")
            print("=" * 60)
            for src, dst in self.file_renames[:10]:  # Show first 10
                print(f"📁 {src.name}")
                print(f"   → {dst.name}")
                print(f"   Path: {src.parent}")
                print()

            if len(self.file_renames) > 10:
                print(f"... and {len(self.file_renames) - 10} more files")

        print(f"📊 Total files to rename: {len(self.file_renames)}")

        # Show class renames
        if self.class_renames:
            print("\n🧠 QUANTUM CLASS MIGRATION PREVIEW")
            print("=" * 60)
            for filepath, old_class, new_class in self.class_renames:
                print(f"📄 {filepath.name}")
                print(f"   class {old_class}")
                print(f"   → class {new_class}")
                print(f"   File: {filepath}")
                print()

        print(f"📊 Total classes to rename: {len(self.class_renames)}")

        # Show content updates
        if self.content_updates:
            print("\n📝 CONTENT REFERENCE UPDATES PREVIEW")
            print("=" * 60)
            for filepath in self.content_updates[:10]:  # Show first 10
                print(f"📄 {filepath.name}")
                for pattern, replacement in self.content_patterns[:2]:
                    print(f"   {pattern} → {replacement}")
                print()

            if len(self.content_updates) > 10:
                print(f"... and {len(self.content_updates) - 10} more files")

        print(f"📊 Total files with content updates needed: {len(self.content_updates)}")

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

    def execute_migration(self) -> None:
        """Execute the actual migration"""
        print("🚀 EXECUTING QUANTUM → QI MIGRATION")
        print("=" * 60)

        # Generate all operations first
        self.generate_file_renames()
        self.generate_class_renames()
        self.generate_content_updates()

        executed_operations = 0
        errors = []

        # 1. Execute file renames
        print("🔄 Renaming files...")
        for src, dst in self.file_renames:
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
        for filepath, old_class, new_class in self.class_renames:
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
        for filepath in self.content_updates:
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
        print("3. git add . && git commit -m '🔄 Complete Quantum → QI migration'")

    def validate_migration(self) -> None:
        """Validate migration was successful"""
        print("🔍 VALIDATING MIGRATION SUCCESS")
        print("=" * 40)

        # Check for remaining quantum files
        remaining_quantum_files = self.find_quantum_files()
        preserved_files = [f for f in remaining_quantum_files if self.should_preserve_file(f)]
        unexpected_files = [f for f in remaining_quantum_files if not self.should_preserve_file(f)]

        print(f"✅ Preserved files (expected): {len(preserved_files)}")
        print(f"⚠️  Unexpected quantum files: {len(unexpected_files)}")

        if unexpected_files:
            print("   Unexpected files:")
            for f in unexpected_files:
                print(f"     {f}")

        # Check for remaining quantum classes
        remaining_classes = self.find_quantum_classes()
        print(f"⚠️  Remaining Quantum classes: {len(remaining_classes)}")

        if remaining_classes:
            print("   Remaining classes:")
            for filepath, class_name in remaining_classes:
                print(f"     {class_name} in {filepath}")

        # Success metrics
        success_rate = (len(self.file_renames) - len(unexpected_files)) / max(len(self.file_renames), 1) * 100
        print(f"📊 File migration success rate: {success_rate:.1f}%")


def main():
    """Main entry point"""
    import sys

    migrator = QIToQIMigrator()

    if '--execute' in sys.argv:
        print("⚠️  WARNING: This will modify files!")
        response = input("Are you sure you want to execute the migration? (y/N): ")
        if response.lower() == 'y':
            migrator.execute_migration()
        else:
            print("❌ Migration cancelled")
    elif '--validate' in sys.argv:
        migrator.validate_migration()
    else:
        # Default: preview mode
        migrator.preview_migration()


if __name__ == "__main__":
    main()
