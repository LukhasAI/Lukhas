#!/usr/bin/env python3
"""
Targeted Timezone Import Fixer
==============================
Future-proof addition of missing timezone imports for consciousness modules
that need UTC datetime functionality.
"""
import ast
import re
from pathlib import Path


class TargetedTimezoneFixer:
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0

    def needs_timezone_import(self, content: str) -> bool:
        """Check if file uses timezone but doesn't import it"""
        # Check for timezone usage patterns
        usage_patterns = [
            r"timezone\.utc",
            r"datetime\.now\(timezone\.utc\)",
            r"\.isoformat\(\)",  # Often used with UTC
        ]

        has_usage = any(re.search(pattern, content) for pattern in usage_patterns)

        if not has_usage:
            return False

        # Check for existing timezone imports
        import_patterns = [
            r"from datetime import.*timezone",
            r"import datetime.*timezone",
            r"from datetime import datetime, timezone"
        ]

        has_import = any(re.search(pattern, content) for pattern in import_patterns)

        return not has_import

    def get_import_insertion_point(self, lines: list[str]) -> int:
        """Find the best place to insert datetime import"""
        # Look for existing datetime imports first
        for i, line in enumerate(lines):
            if re.match(r"from datetime import", line.strip()):
                # Add timezone to existing datetime import
                return -1  # Special flag for modification

        # Find standard insertion point after other imports
        last_import_idx = -1
        in_docstring = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track docstrings
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            # Skip comments and shebangs
            if stripped.startswith("#"):
                continue

            # Track imports
            if (stripped.startswith("import ") or
                (stripped.startswith("from ") and " import " in stripped)):
                last_import_idx = i
            elif stripped and not stripped.startswith("#"):
                # Found first non-import line
                break

        return last_import_idx + 1 if last_import_idx >= 0 else 0

    def add_timezone_import(self, content: str) -> str:
        """Add timezone import safely"""
        lines = content.split("\n")

        # Check for existing datetime import to extend
        for i, line in enumerate(lines):
            if re.match(r"from datetime import datetime(?!.*timezone)", line.strip()):
                # Extend existing import
                lines[i] = line.rstrip() + ", timezone"
                self.fixes_applied += 1
                return "\n".join(lines)

        # Add new import
        insert_idx = self.get_import_insertion_point(lines)
        if insert_idx >= 0:
            lines.insert(insert_idx, "from datetime import timezone")
            self.fixes_applied += 1

        return "\n".join(lines)

    def validate_syntax(self, content: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False

    def fix_file(self, file_path: Path) -> bool:
        """Fix a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            if not self.needs_timezone_import(original_content):
                return False

            fixed_content = self.add_timezone_import(original_content)

            # Validate before writing
            if self.validate_syntax(fixed_content):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                return True
            else:
                print(f"⚠️ Syntax validation failed: {file_path}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

        return False

    def process_consciousness_modules(self):
        """Process key consciousness modules that need timezone"""
        target_files = [
            "candidate/consciousness/awareness/awareness_tracker.py",
            "candidate/consciousness/reasoning/reasoning_diagnostics.py",
            "candidate/consciousness/perception/symbolic_nervous_system.py",
            "candidate/consciousness/dream/core/dream_engine.py",
            "candidate/memory/causal/causal_reasoning.py",
            "candidate/bridge/openai/openai_adapter.py",
            "candidate/governance/ethics/drift_detector.py",
            "lukhas/core/glyph.py"
        ]

        print("🔧 TARGETED TIMEZONE IMPORT FIXER")
        print("=" * 50)

        fixed_count = 0

        for file_path_str in target_files:
            file_path = Path(file_path_str)

            if file_path.exists():
                if self.fix_file(file_path):
                    print(f"✅ Fixed: {file_path}")
                    fixed_count += 1
                else:
                    print(f"⏭️ Skipped: {file_path}")
            else:
                print(f"❓ Not found: {file_path}")

        print("\n🎯 TIMEZONE FIXES COMPLETE!")
        print(f"✅ Files fixed: {fixed_count}")
        print(f"🔧 Total fixes applied: {self.fixes_applied}")


def main():
    fixer = TargetedTimezoneFixer()
    fixer.process_consciousness_modules()


if __name__ == "__main__":
    main()
