#!/usr/bin/env python3
"""
LUKHAS Naming Convention Application Tool
Applies industry-standard naming while preserving LUKHAS's unique concepts and personality
"""
import json
import re
import shutil
from pathlib import Path

import streamlit as st

from consciousness.qi import qi


class LukhasNamingApplicator:
    def __init__(self):
        self.report_path = Path("docs/reports/analysis/LUKHAS_NAMING_REFINEMENTS.json")
        self.backup_dir = Path(".naming_backup")
        self.dry_run = True  # Safety first

        # Load the refinement report
        with open(self.report_path) as f:
            self.report = json.load(f)

        # LUKHAS concepts to preserve
        self.preserve_concepts = set(self.report["naming_guidelines"]["concepts_to_preserve"])

        # Track changes for summary
        self.changes_applied = {
            "classes": 0,
            "functions": 0,
            "files": 0,
            "imports_updated": 0,
        }

    def apply_refinements(self, dry_run: bool = True):
        """Apply naming refinements to the codebase"""
        self.dry_run = dry_run

        print("🧬 LUKHAS Naming Convention Application")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if dry_run else 'APPLYING CHANGES'}")
        print(f"Total refinements to apply: {self.report['summary']['total_refinements']}")
        print(f"Preserving {len(self.preserve_concepts)} LUKHAS concepts")

        if not dry_run:
            # Create backup
            self._create_backup()

        # Apply refinements by category
        self._apply_class_refinements()
        self._apply_function_refinements()
        self._apply_file_refinements()

        # Update imports
        self._update_imports()

        # Print summary
        self._print_summary()

    def _create_backup(self):
        """Create backup of files to be modified"""
        print("\n📦 Creating backup...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        self.backup_dir.mkdir()

        # Collect all files that will be modified
        files_to_backup = set()

        for refinement in self.report["refinements"]["classes"]:
            files_to_backup.add(refinement["file"])

        for refinement in self.report["refinements"]["functions"]:
            files_to_backup.add(refinement["file"])

        for refinement in self.report["refinements"]["files"]:
            files_to_backup.add(refinement["path"])

        # Backup files
        for file_path in files_to_backup:
            src = Path(file_path)
            if src.exists():
                dst = self.backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        print(f"   Backed up {len(files_to_backup)} files to {self.backup_dir}")

    def _apply_class_refinements(self):
        """Apply class name refinements"""
        print("\n🏗️  Refining class names...")

        # Group refinements by file
        refinements_by_file = {}
        for refinement in self.report["refinements"]["classes"]:
            file_path = refinement["file"]
            if file_path not in refinements_by_file:
                refinements_by_file[file_path] = []
            refinements_by_file[file_path].append(refinement)

        for file_path, refinements in refinements_by_file.items():
            self._apply_refinements_to_file(file_path, refinements, "class")

    def _apply_function_refinements(self):
        """Apply function name refinements"""
        print("\n🔧 Refining function names...")

        # Group refinements by file
        refinements_by_file = {}
        for refinement in self.report["refinements"]["functions"]:
            file_path = refinement["file"]
            if file_path not in refinements_by_file:
                refinements_by_file[file_path] = []
            refinements_by_file[file_path].append(refinement)

        for file_path, refinements in refinements_by_file.items():
            self._apply_refinements_to_file(file_path, refinements, "function")

    def _apply_file_refinements(self):
        """Apply file name refinements"""
        print("\n📄 Refining file names...")

        for refinement in self.report["refinements"]["files"]:
            old_path = Path(refinement["path"])
            new_name = refinement["refined"]
            new_path = old_path.parent / new_name

            if self.dry_run:
                print(f"   Would rename: {old_path} → {new_path}")
            else:
                if old_path.exists():
                    old_path.rename(new_path)
                    self.changes_applied["files"] += 1
                    print(f"   ✓ Renamed: {old_path} → {new_path}")

    def _apply_refinements_to_file(self, file_path: str, refinements: list[dict], refinement_type: str):
        """Apply refinements to a single file"""
        file_path = Path(file_path)

        if not file_path.exists():
            return

        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Sort refinements by line number (reverse order to maintain positions)
            refinements.sort(key=lambda x: x["line"], reverse=True)

            # Apply each refinement
            for refinement in refinements:
                old_name = refinement["original"]
                new_name = refinement["refined"]

                # Skip if preserving a concept
                if any(concept in old_name.lower() for concept in self.preserve_concepts):
                    if not any(concept in new_name.lower() for concept in self.preserve_concepts):
                        print(f"   ⚠️  Skipping {old_name} → {new_name} (would lose LUKHAS concept)")
                        continue

                # Apply the refinement
                if refinement_type == "class":
                    # Replace class definition and all references
                    pattern = rf"\b{re.escape(old_name)}\b"
                    content = re.sub(pattern, new_name, content)

                elif refinement_type == "function":
                    # Replace function definition and calls
                    # Be careful with method calls (obj.method)
                    pattern = rf"(?<!\.)\b{re.escape(old_name)}\b"
                    content = re.sub(pattern, new_name, content)

                if content != original_content:
                    self.changes_applied[f"{refinement_type}es"] += 1

            # Write changes
            if content != original_content:
                if self.dry_run:
                    print(f"   Would modify: {file_path}")
                else:
                    file_path.write_text(content, encoding="utf-8")
                    print(f"   ✓ Modified: {file_path}")

        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")

    def _update_imports(self):
        """Update import statements for renamed modules"""
        print("\n📦 Updating imports...")

        # Build mapping of old to new module names
        module_renames = {}
        for refinement in self.report["refinements"]["files"]:
            old_name = refinement["original"].replace(".py", "")
            new_name = refinement["refined"].replace(".py", "")
            if old_name != new_name:
                module_renames[old_name] = new_name

        if not module_renames:
            print("   No import updates needed")
            return

        # Find all Python files
        python_files = list(Path(".").rglob("*.py"))

        for file_path in python_files:
            # Skip files in virtual environments and cache
            if any(skip in str(file_path) for skip in [".venv", "__pycache__", ".git"]):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content

                # Update imports
                for old_module, new_module in module_renames.items():
                    # from module import ...
                    content = re.sub(
                        rf"from\s+(\S+\.)?{re.escape(old_module)}\s+import",
                        rf"from \1{new_module} import",
                        content,
                    )
                    # import module
                    content = re.sub(
                        rf"import\s+(\S+\.)?{re.escape(old_module)}",
                        rf"import \1{new_module}",
                        content,
                    )

                if content != original_content:
                    if self.dry_run:
                        print(f"   Would update imports in: {file_path}")
                    else:
                        file_path.write_text(content, encoding="utf-8")
                        self.changes_applied["imports_updated"] += 1

            except Exception:
                pass

    def _print_summary(self):
        """Print summary of changes"""
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")

        if self.dry_run:
            print("\n🔍 DRY RUN COMPLETE - No changes were made")
            print("\nChanges that would be applied:")
        else:
            print("\n✅ CHANGES APPLIED:")

        print(f"   Classes refined: {self.changes_applied['classes']}")
        print(f"   Functions refined: {self.changes_applied['functions']}")
        print(f"   Files renamed: {self.changes_applied['files']}")
        print(f"   Import statements updated: {self.changes_applied['imports_updated']}")

        print(f"\n🧬 LUKHAS concepts preserved: {len(self.preserve_concepts)}")
        print("   Examples: memory_fold, dream_recall, qi_state, bio_symbolic")

        if not self.dry_run:
            print(f"\n📦 Backup created at: {self.backup_dir}")
            print("\n⚠️  IMPORTANT: Run tests to ensure nothing is broken!")


def main():
    applicator = LukhasNamingApplicator()

    # First, do a dry run
    print("🚀 Starting LUKHAS naming convention application...\n")
    applicator.apply_refinements(dry_run=True)

    # Ask user to confirm
    print("\n" + "=" * 60)
    response = input("\n❓ Apply these changes? (yes/no): ").lower().strip()

    if response == "yes":
        print("\n🔧 Applying changes...\n")
        applicator.apply_refinements(dry_run=False)

        print("\n✨ LUKHAS naming conventions applied!")
        print("   Industry standards: ✓")
        print("   LUKHAS personality: ✓")
        print("   Original concepts: ✓")

        print("\n📋 Next steps:")
        print("   1. Run tests: pytest tests/")
        print("   2. Check functionality: python main.py")
        print("   3. If issues, restore from backup")
    else:
        print("\n❌ Changes cancelled")


if __name__ == "__main__":
    main()
