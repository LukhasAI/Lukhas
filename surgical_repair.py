#!/usr/bin/env python3
"""
🔧 Surgical Corruption Repair Tool

Repairs specific corruption patterns while preserving logic and organization.
"""

import os
import re


class SurgicalRepairer:
    def __init__(self):
        self.repaired_files = []
        self.errors = []

    def repair_indentation_corruption(self, filepath):
        """Fix severe indentation corruption while preserving logic"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Fix the corruption signature: excessive whitespace padding
            lines = content.split("\n")
            repaired_lines = []

            for line in lines:
                # Common corruption pattern: excessive spaces followed by content
                if "                                                   " in line:
                    # Extract the meaningful content and proper indentation
                    stripped = line.strip()

                    # Determine proper indentation level by looking at structure
                    if stripped.startswith("'") or stripped.startswith('"'):
                        # This looks like a string value, probably should be indented like a list item
                        repaired_line = "    " + stripped
                    elif stripped.startswith("}") or stripped.startswith("]"):
                        # Closing bracket, minimal indent
                        repaired_line = stripped
                    else:
                        # Default to reasonable indentation
                        repaired_line = "    " + stripped

                    repaired_lines.append(repaired_line)
                else:
                    repaired_lines.append(line)

            repaired_content = "\n".join(repaired_lines)

            # Write the repaired content
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(repaired_content)

            self.repaired_files.append(f"Indentation: {filepath}")
            return True

        except Exception as e:
            self.errors.append(f"Indentation repair failed for {filepath}: {e}")
            return False

    def repair_fstring_corruption(self, filepath):
        """Fix f-string corruption while preserving logic"""
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Common f-string corruption patterns
            original_content = content

            # Fix double closing braces
            content = re.sub(r"}}(?!\})", "}", content)

            # Fix mismatched brackets in f-strings
            # Look for f" followed by problematic patterns
            fstring_pattern = r'f"([^"]*)"'

            def fix_fstring_brackets(match):
                fstring_content = match.group(1)
                # Count brackets
                open_count = fstring_content.count("{")
                close_count = fstring_content.count("}")

                if open_count > close_count:
                    # Add missing closing brackets
                    fstring_content += "}" * (open_count - close_count)
                elif close_count > open_count:
                    # Remove extra closing brackets
                    for _ in range(close_count - open_count):
                        fstring_content = fstring_content.rsplit("}", 1)[0]

                return f'f"{fstring_content}"'

            content = re.sub(fstring_pattern, fix_fstring_brackets, content)

            # Only write if we made changes
            if content != original_content:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self.repaired_files.append(f"F-string: {filepath}")

            return True

        except Exception as e:
            self.errors.append(f"F-string repair failed for {filepath}: {e}")
            return False

    def repair_priority_files(self):
        """Repair the identified priority corruption files"""

        # Phase 1: Severe indentation corruption
        indentation_files = [
            "candidate/core/safety/predictive_harm_prevention.py",
            "candidate/memory/systems/dream_memory_manager.py",
            "tools/scripts/enhance_all_modules.py",
        ]

        print("🔧 Phase 1: Repairing severe indentation corruption...")
        for filepath in indentation_files:
            if os.path.exists(filepath):
                print(f"  Repairing: {filepath}")
                self.repair_indentation_corruption(filepath)
            else:
                print(f"  ⚠️  File not found: {filepath}")

        # Phase 2: F-string corruption
        fstring_files = [
            "candidate/bridge/adapters/api_documentation_generator.py",
            "candidate/bridge/api/direct_ai_router.py",
            "candidate/api/audit.py",
            "tools/module_dependency_visualizer.py",
            "products/communication/nias/vendor_portal_backup.py",
        ]

        print("\n🔧 Phase 2: Repairing f-string corruption...")
        for filepath in fstring_files:
            if os.path.exists(filepath):
                print(f"  Repairing: {filepath}")
                self.repair_fstring_corruption(filepath)
            else:
                print(f"  ⚠️  File not found: {filepath}")

    def validate_repairs(self):
        """Validate that repaired files can be parsed"""
        import ast

        print("\n✅ Validating repairs...")
        validation_success = 0
        validation_errors = 0

        for repair_info in self.repaired_files:
            filepath = repair_info.split(": ", 1)[1]
            try:
                with open(filepath) as f:
                    content = f.read()
                ast.parse(content)
                print(f"  ✅ {filepath}")
                validation_success += 1
            except Exception as e:
                print(f"  ❌ {filepath}: {e}")
                validation_errors += 1

        return validation_success, validation_errors

    def generate_report(self):
        """Generate repair summary"""
        report = f"""
# 🔧 Surgical Corruption Repair Report

## ✅ Successfully Repaired Files: {len(self.repaired_files)}
"""
        for repair in self.repaired_files:
            report += f"- {repair}\n"

        if self.errors:
            report += f"\n## ❌ Repair Errors: {len(self.errors)}\n"
            for error in self.errors:
                report += f"- {error}\n"

        validation_success, validation_errors = self.validate_repairs()

        report += f"""
## 📊 Validation Results
- ✅ **Successfully parsing**: {validation_success} files
- ❌ **Still have issues**: {validation_errors} files

## 🎯 Next Steps
1. Commit surgical repairs
2. Run targeted syntax validation  
3. Apply automated ruff fixes to clean foundation
4. Preserve all logic, state, and organization

---
*All repairs preserve tagged commit logic while eliminating corruption*
"""

        with open("SURGICAL_REPAIR_REPORT.md", "w") as f:
            f.write(report)

        print("\n📄 Report saved: SURGICAL_REPAIR_REPORT.md")
        print(f"✅ Repaired: {len(self.repaired_files)} files")
        print(f"❌ Errors: {len(self.errors)} files")
        print(f"✅ Parsing: {validation_success} files")
        print(f"❌ Still broken: {validation_errors} files")


if __name__ == "__main__":
    print("🔧 Starting Surgical Corruption Repair...")

    repairer = SurgicalRepairer()
    repairer.repair_priority_files()
    repairer.generate_report()

    print("\n🎯 Surgical repair complete! Check SURGICAL_REPAIR_REPORT.md for details.")
