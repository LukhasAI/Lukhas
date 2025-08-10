#!/usr/bin/env python3
"""
Fix the most critical circular imports by restructuring imports.
Focus on consciousness, memory, core, and orchestration modules.
"""

import re
from pathlib import Path


class CriticalCircularFixer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.fixes_applied = 0

        # Define specific fixes for known circular dependencies
        self.circular_fixes = {
            # consciousness → creativity → consciousness
            ("creativity/advanced_haiku_generator.py", "consciousness"): {
                "action": "lazy_import",
                "reason": "Break consciousness-creativity cycle",
            },
            ("creativity/dream/dream_data_sources.py", "consciousness"): {
                "action": "lazy_import",
                "reason": "Break consciousness-creativity cycle",
            },
            # core → consciousness → core
            ("core/api_controllers.py", "consciousness"): {
                "action": "type_checking_only",
                "reason": "Break core-consciousness cycle",
            },
            ("core/bio_symbolic_swarm_hub.py", "consciousness"): {
                "action": "type_checking_only",
                "reason": "Break core-consciousness cycle",
            },
            # memory → consciousness → memory
            ("memory/systems/memory_learning/memory_manager.py", "consciousness"): {
                "action": "remove_import",
                "reason": "Memory should not depend on consciousness",
            },
            # consciousness → orchestration → consciousness
            (
                "consciousness/systems/cognitive_systems/voice_personality.py",
                "orchestration",
            ): {
                "action": "lazy_import",
                "reason": "Break consciousness-orchestration cycle",
            },
        }

    def fix_circular_imports(self):
        """Apply fixes to break circular imports."""
        print("🔧 Fixing critical circular imports...")

        for (file_path, module), fix_info in self.circular_fixes.items():
            full_path = self.root_path / file_path

            if not full_path.exists():
                print(f"  ⚠️  File not found: {file_path}")
                continue

            print(f"\n  Processing: {file_path}")
            print(f"    Action: {fix_info['action']} - {fix_info['reason']}")

            if fix_info["action"] == "lazy_import":
                self._apply_lazy_import(full_path, module)
            elif fix_info["action"] == "type_checking_only":
                self._apply_type_checking_import(full_path, module)
            elif fix_info["action"] == "remove_import":
                self._remove_import(full_path, module)

    def _apply_lazy_import(self, file_path: Path, module: str):
        """Convert import to lazy import."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            modified = False
            new_lines = []
            imports_to_lazy = []

            for line in lines:
                # Find imports from the problematic module
                import_match = re.match(rf"from {module}(\.\w+)* import (.+)", line)
                if import_match:
                    imports = import_match.group(2)
                    full_module = module + (import_match.group(1) or "")

                    # Comment out the original import
                    new_lines.append(
                        f"# {line}  # Moved to lazy import to break circular dependency"
                    )
                    imports_to_lazy.append((full_module, imports))
                    modified = True
                else:
                    new_lines.append(line)

            if modified and imports_to_lazy:
                # Find first function or class definition
                insert_pos = len(new_lines)
                for i, line in enumerate(new_lines):
                    if line.strip().startswith(("def ", "class ", "async def ")):
                        insert_pos = i
                        break

                # Create lazy import functions
                lazy_code = []
                for full_module, imports in imports_to_lazy:
                    func_name = f'_get_{full_module.replace(".", "_")}_imports'
                    lazy_code.append(
                        f'\ndef {func_name}():\n    """Lazy import to avoid circular dependency."""\n    from {full_module} import {imports}\n    return locals()\n'
                    )

                # Insert lazy import code before first function/class
                new_lines.insert(insert_pos, "\n".join(lazy_code))

                # Write back
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                print("    ✓ Applied lazy import fix")
                self.fixes_applied += 1

        except Exception as e:
            print(f"    ✗ Error: {e}")

    def _apply_type_checking_import(self, file_path: Path, module: str):
        """Move import to TYPE_CHECKING block."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            modified = False
            new_lines = []
            type_checking_imports = []
            has_type_checking = False

            # Check if TYPE_CHECKING is already imported
            for line in lines:
                if "from typing import" in line and "TYPE_CHECKING" in line:
                    has_type_checking = True
                    break

            i = 0
            while i < len(lines):
                line = lines[i]

                # Find imports from the problematic module
                if re.match(rf"from {module}(\.\w+)* import", line) or re.match(
                    rf"import {module}", line
                ):
                    # Move to TYPE_CHECKING
                    type_checking_imports.append(line)
                    new_lines.append(f"# {line}  # Moved to TYPE_CHECKING")
                    modified = True
                else:
                    new_lines.append(line)
                i += 1

            if modified and type_checking_imports:
                # Find where to insert TYPE_CHECKING block
                import_end = 0
                for i, line in enumerate(new_lines):
                    if line.strip() and not line.strip().startswith(
                        ("import ", "from ", "#")
                    ):
                        import_end = i
                        break

                # Add TYPE_CHECKING import if needed
                if not has_type_checking:
                    # Find existing typing import
                    typing_line = -1
                    for i, line in enumerate(new_lines[:import_end]):
                        if "from typing import" in line:
                            typing_line = i
                            break

                    if typing_line >= 0:
                        # Add TYPE_CHECKING to existing typing import
                        new_lines[typing_line] = (
                            new_lines[typing_line].rstrip() + ", TYPE_CHECKING"
                        )
                    else:
                        # Add new typing import
                        new_lines.insert(
                            import_end, "from typing import TYPE_CHECKING\n"
                        )
                        import_end += 1

                # Add TYPE_CHECKING block
                type_checking_block = [
                    "",
                    "if TYPE_CHECKING:",
                ]
                for imp in type_checking_imports:
                    type_checking_block.append(f"    {imp}")
                type_checking_block.append("")

                new_lines[import_end:import_end] = type_checking_block

                # Write back
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                print("    ✓ Applied TYPE_CHECKING import fix")
                self.fixes_applied += 1

        except Exception as e:
            print(f"    ✗ Error: {e}")

    def _remove_import(self, file_path: Path, module: str):
        """Remove the import entirely."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            new_lines = []
            modified = False

            for line in lines:
                if re.match(rf"from {module}(\.\w+)* import", line) or re.match(
                    rf"import {module}", line
                ):
                    new_lines.append(
                        f"# {line}  # Removed to break circular dependency"
                    )
                    modified = True
                else:
                    new_lines.append(line)

            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines))

                print("    ✓ Removed import")
                self.fixes_applied += 1

        except Exception as e:
            print(f"    ✗ Error: {e}")

    def fix_additional_patterns(self):
        """Fix additional common circular import patterns."""
        print("\n\n🔍 Scanning for additional circular import patterns...")

        # Pattern 1: Features importing from API (API should be top-level)
        self._fix_pattern("features", "api", action="remove")

        # Pattern 2: Core importing from high-level modules
        for high_level in ["orchestration", "consciousness", "features", "api"]:
            self._fix_pattern("core", high_level, action="type_checking")

        # Pattern 3: Memory importing from high-level modules
        for high_level in ["consciousness", "orchestration", "api"]:
            self._fix_pattern("memory", high_level, action="remove")

    def _fix_pattern(self, from_module: str, to_module: str, action: str):
        """Fix a specific import pattern."""
        module_path = self.root_path / from_module
        if not module_path.exists():
            return

        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check if file imports from the problematic module
                if f"from {to_module}" in content or f"import {to_module}" in content:
                    print(
                        f"\n  Found {from_module} → {to_module} in {py_file.relative_to(self.root_path)}"
                    )

                    if action == "remove":
                        self._remove_import(py_file, to_module)
                    elif action == "type_checking":
                        self._apply_type_checking_import(py_file, to_module)
                    elif action == "lazy":
                        self._apply_lazy_import(py_file, to_module)

            except Exception:
                pass


def main():
    root_path = Path(".").resolve()
    fixer = CriticalCircularFixer(root_path)

    # Fix known critical circular imports
    fixer.fix_circular_imports()

    # Fix additional patterns
    fixer.fix_additional_patterns()

    print(f"\n\n✅ Total fixes applied: {fixer.fixes_applied}")
    print("\n💡 Next steps:")
    print("1. Run tests to ensure functionality")
    print("2. Review modified files for any issues")
    print("3. Consider refactoring to prevent future circular imports")


if __name__ == "__main__":
    main()
