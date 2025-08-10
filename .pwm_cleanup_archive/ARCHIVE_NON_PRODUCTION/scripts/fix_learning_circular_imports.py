#!/usr/bin/env python3
"""
Fix the incorrect learning circular imports.
Core should not depend on learning - it's a violation of architectural hierarchy.
"""

import re
from pathlib import Path


class LearningCircularFixer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.fixes_applied = 0

    def fix_core_learning_import(self):
        """Fix core importing from learning - this is architecturally wrong."""
        print("🔧 Fixing core → learning dependency (incorrect hierarchy)...")

        # Fix api_controllers.py
        api_controllers = self.root_path / "core" / "api_controllers.py"
        if api_controllers.exists():
            self._fix_file(api_controllers)

    def _fix_file(self, file_path: Path):
        """Fix imports in api_controllers.py"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original = content

            # Move learning import to lazy import or remove if not used
            if "from learning.learning_service import LearningService" in content:
                print(f"  Found learning import in {file_path.name}")

                # Check if LearningService is actually used
                if "LearningService" in content.replace(
                    "from learning.learning_service import LearningService", ""
                ):
                    # It's used - convert to lazy import
                    content = content.replace(
                        "from learning.learning_service import LearningService",
                        "# from learning.learning_service import LearningService  # Moved to lazy import",
                    )

                    # Add lazy import function
                    lazy_import = '''
def _get_learning_service():
    """Lazy import to avoid circular dependency - core should not depend on learning."""
    from learning.learning_service import LearningService
    return LearningService

'''
                    # Insert after imports section
                    lines = content.split("\n")
                    import_end = 0
                    for i, line in enumerate(lines):
                        if (
                            line.strip()
                            and not line.strip().startswith(("import ", "from ", "#"))
                            and not line.startswith("def ")
                        ):
                            import_end = i
                            break

                    lines.insert(import_end, lazy_import)
                    content = "\n".join(lines)

                    # Replace LearningService usage
                    content = re.sub(
                        r"\bLearningService\b", "_get_learning_service()", content
                    )

                    print("    ✓ Converted to lazy import")
                else:
                    # Not used - just remove it
                    content = content.replace(
                        "from learning.learning_service import LearningService\n", ""
                    )
                    content = content.replace(
                        "from learning.learning_service import LearningService", ""
                    )
                    print("    ✓ Removed unused import")

                self.fixes_applied += 1

            if content != original:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"    ✗ Error: {e}")

    def check_other_violations(self):
        """Check for other architectural violations."""
        print("\n🔍 Checking for other architectural violations...")

        violations = []

        # Core should not import from these high-level modules
        high_level_modules = [
            "learning",
            "api",
            "features",
            "creativity",
            "consciousness",
        ]

        for py_file in (self.root_path / "core").rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                for module in high_level_modules:
                    if f"from {module}" in content or f"import {module}" in content:
                        # Skip if it's in TYPE_CHECKING
                        if "TYPE_CHECKING" in content:
                            # Check if import is in TYPE_CHECKING block
                            lines = content.split("\n")
                            in_type_checking = False
                            for line in lines:
                                if "if TYPE_CHECKING:" in line:
                                    in_type_checking = True
                                elif in_type_checking and (
                                    line.strip() and not line.startswith(" ")
                                ):
                                    in_type_checking = False
                                elif in_type_checking and module in line:
                                    continue  # It's OK, skip this violation

                        violations.append(
                            {
                                "file": py_file.relative_to(self.root_path),
                                "imports": module,
                                "severity": (
                                    "high"
                                    if module in ["api", "learning"]
                                    else "medium"
                                ),
                            }
                        )

            except Exception:
                pass

        if violations:
            print(f"\n⚠️  Found {len(violations)} architectural violations:")
            for v in violations[:10]:  # Show first 10
                print(
                    f"  - {v['file']}: imports from {v['imports']} (severity: {v['severity']})"
                )
        else:
            print("  ✅ No architectural violations found in core module")

        return violations


def main():
    root_path = Path(".").resolve()
    fixer = LearningCircularFixer(root_path)

    # Fix the specific core → learning import
    fixer.fix_core_learning_import()

    # Check for other violations
    violations = fixer.check_other_violations()

    print(f"\n✅ Applied {fixer.fixes_applied} fixes")

    if violations:
        print("\n💡 Recommendations:")
        print("1. Move shared interfaces to core/interfaces/")
        print("2. Use dependency injection instead of direct imports")
        print("3. Consider if core really needs these high-level dependencies")


if __name__ == "__main__":
    main()
