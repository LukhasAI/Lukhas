#!/usr/bin/env python3
"""
Fix imports after directory consolidation
Updates imports from moved directories to their new locations
"""

import re
from pathlib import Path


class ImportFixer:
    def __init__(self):
        self.replacements = {
            # Core module moves
            r"from core\.common\.": "from core.utils.",
            r"from core\.common import": "from core.utils import",
            r"from core\.tracing\.": "from core.utils.",
            r"from core\.tracing import": "from core.utils import",
            r"from core\.user_interaction\.": "from core.utils.",
            r"from core\.user_interaction import": "from core.utils import",
            r"from core\.grow\.": "from core.utils.",
            r"from core\.grow import": "from core.utils import",
            r"from core\.adaptive_ai\.": "from core.agi.adaptive.",
            r"from core\.adaptive_ai import": "from core.agi.adaptive import",
            # Bio module moves
            r"from bio\.processing\.": "from bio.core.",
            r"from bio\.processing import": "from bio.core import",
            r"from bio\.endocrine\.": "from bio.core.",
            r"from bio\.endocrine import": "from bio.core import",
            r"from bio\.integration\.": "from bio.core.",
            r"from bio\.integration import": "from bio.core import",
            r"from bio\.orchestration\.": "from bio.core.",
            r"from bio\.orchestration import": "from bio.core import",
            # Special case for endocrine_integration which wasn't moved
            r"from bio\.endocrine_integration import": "from bio.endocrine_integration import",
        }

        self.files_to_fix = []
        self.fixed_count = 0

    def find_files_to_fix(self, root_path: str):
        """Find Python files that need import fixes"""
        root = Path(root_path)

        # Skip archived directories
        skip_dirs = {
            "ARCHIVE_NON_PRODUCTION",
            "ARCHIVE_DISCONNECTED",
            ".git",
            "__pycache__",
        }

        for py_file in root.rglob("*.py"):
            # Skip files in archive directories
            if any(skip_dir in str(py_file) for skip_dir in skip_dirs):
                continue

            # Check if file contains imports to fix
            try:
                content = py_file.read_text()
                for pattern in self.replacements:
                    if re.search(pattern, content):
                        self.files_to_fix.append(py_file)
                        break
            except Exception as e:
                print(f"Error reading {py_file}: {e}")

    def fix_imports(self):
        """Fix imports in all identified files"""
        for file_path in self.files_to_fix:
            try:
                content = file_path.read_text()
                original_content = content

                # Apply all replacements
                for pattern, replacement in self.replacements.items():
                    content = re.sub(pattern, replacement, content)

                # Only write if changes were made
                if content != original_content:
                    file_path.write_text(content)
                    self.fixed_count += 1
                    print(f"Fixed imports in: {file_path}")

            except Exception as e:
                print(f"Error fixing {file_path}: {e}")

    def run(self, root_path: str = "."):
        """Run the import fixer"""
        print("🔍 Finding files with imports to fix...")
        self.find_files_to_fix(root_path)

        print(f"\nFound {len(self.files_to_fix)} files to check")

        if self.files_to_fix:
            print("\n🔧 Fixing imports...")
            self.fix_imports()
            print(f"\n✅ Fixed imports in {self.fixed_count} files")
        else:
            print("\n✅ No imports need fixing")

        # Report on specific files that might need manual attention
        special_cases = [
            "orchestration/core_modules/orchestration_service.py",
            "reasoning/scaffold_modules_reasoning_engine.py",
            "bridge/integration_bridge.py",
        ]

        print("\n⚠️  Files that may need manual review:")
        for case in special_cases:
            if Path(case).exists():
                print(f"  - {case}")


def main():
    fixer = ImportFixer()
    fixer.run()

    print("\n📝 Next steps:")
    print("1. Review the changed files")
    print("2. Run any tests to ensure imports work correctly")
    print("3. Check for any circular import issues")


if __name__ == "__main__":
    main()
