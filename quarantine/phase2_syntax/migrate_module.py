#!/usr/bin/env python3
"""
Module Migration Helper for LUKHAS AI
Automates the migration of modules to lukhas/ (accepted)
"""

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Optional


class ModuleMigrator:
    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or Path.cwd()
        self.lukhas_dir = self.root / "lukhas"
        self.candidate_dir = self.root / "candidate"
        self.quarantine_dir = self.root / "quarantine"
        self.archive_dir = self.root / "archive"

    def check_illegal_imports(self, module_path: Path) -> list[str]:
        """Check for imports from non-production lanes"""
        illegal = []
        pattern = re.compile(r"^\s*(?:from|import)\s+(candidate|quarantine|archive)\b")

        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        if pattern.search(line):
                            illegal.append(f"{py_file.relative_to(self.root)}:{line_no}: {line.strip()}")
            except Exception as e:
                print(f"Error reading {py_file}: {e}")

        return illegal

    def find_circular_dependencies(self, module_name: str) -> dict[str, list[str]]:
        """Find circular dependencies with other modules"""
        circular = {}
        module_path = self.root / module_name

        if not module_path.exists():
            return circular

        # Check what this module imports
        other_modules = [
            "core",
            "memory",
            "consciousness",
            "orchestration",
            "governance",
            "identity",
            "bridge",
            "emotion",
        ]
        other_modules.remove(module_name) if module_name in other_modules else None

        for other in other_modules:
            imports = []
            pattern = re.compile(rf"^\s*(?:from\s+{other}|import\s+{other})\b")

            for py_file in module_path.rglob("*.py"):
                try:
                    with open(py_file, encoding="utf-8") as f:
                        for _line_no, line in enumerate(f, 1):
                            if pattern.search(line):
                                imports.append(f"{py_file.relative_to(module_path)}")
                                break
                except:
                    pass

            if imports:
                circular[other] = imports

        return circular

    def check_matriz_compliance(self, module_path: Path) -> bool:
        """Check if module has MATRIZ node emission"""
        matriz_patterns = [
            r"MATRIZ",
            r"matriz_node",
            r"schema_ref.*matriz_node_v1",
            r"validate_node",
        ]

        for py_file in module_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in matriz_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
            except:
                pass

        return False

    def count_tests(self, module_name: str) -> int:
        """Count test files for a module"""
        test_dir = self.root / "tests"
        if not test_dir.exists():
            return 0

        count = 0
        for test_file in test_dir.rglob("*.py"):
            if module_name in test_file.name.lower():
                count += 1

        return count

    def migrate_module(self, module_name: str, fix_imports: bool = True) -> bool:
        """Migrate a module to lukhas/"""
        source = self.root / module_name
        dest = self.lukhas_dir / module_name

        if not source.exists():
            print(f"Error: Module {module_name} not found")
            return False

        if dest.exists():
            print(f"Warning: Destination {dest} already exists")
            response = input("Overwrite? (y/n): ")
            if response.lower() != "y":
                return False
            shutil.rmtree(dest)

        # Copy module
        shutil.copytree(source, dest)
        print(f"Copied {module_name} to lukhas/")

        if fix_imports:
            self.update_imports(dest, module_name)

        # Remove source
        response = input(f"Remove source {source}? (y/n): ")
        if response.lower() == "y":
            shutil.rmtree(source)
            print(f"Removed source {source}")

        return True

    def update_imports(self, module_path: Path, module_name: str):
        """Update imports from 'module' to 'lukhas.module'"""
        count = 0

        # Update imports in all Python files in the repo
        for py_file in self.root.rglob("*.py"):
            if ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                original = content

                # Update various import patterns
                patterns = [
                    (rf"^from {module_name}\b", f"from lukhas.{module_name}"),
                    (rf"^import {module_name}\b", f"import lukhas.{module_name}"),
                    (rf"^from {module_name}\.", f"from lukhas.{module_name}."),
                    (rf"^import {module_name}\.", f"import lukhas.{module_name}."),
                ]

                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

                if content != original:
                    py_file.write_text(content, encoding="utf-8")
                    count += 1

            except Exception as e:
                print(f"Error updating {py_file}: {e}")

        print(f"Updated imports in {count} files")

    def generate_report(self, module_name: str) -> dict:
        """Generate migration readiness report"""
        module_path = self.root / module_name

        if not module_path.exists():
            return {"error": f"Module {module_name} not found"}

        report = {
            "module": module_name,
            "files": len(list(module_path.rglob("*.py"))),
            "illegal_imports": self.check_illegal_imports(module_path),
            "circular_deps": self.find_circular_dependencies(module_name),
            "matriz_compliant": self.check_matriz_compliance(module_path),
            "test_count": self.count_tests(module_name),
            "ready": False,
        }

        # Determine if ready for migration
        report["ready"] = len(report["illegal_imports"]) == 0 and report["test_count"] > 0

        return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_module.py <command> [module_name]")
        print("Commands:")
        print("  check <module>  - Check migration readiness")
        print("  migrate <module> - Migrate module to lukhas/")
        print("  report <module> - Generate detailed report")
        sys.exit(1)

    command = sys.argv[1]
    module_name = sys.argv[2] if len(sys.argv) > 2 else None

    migrator = ModuleMigrator()

    if command == "check" and module_name:
        report = migrator.generate_report(module_name)
        print(json.dumps(report, indent=2))

    elif command == "migrate" and module_name:
        success = migrator.migrate_module(module_name)
        if success:
            print(f"Successfully migrated {module_name}")
        else:
            print(f"Failed to migrate {module_name}")

    elif command == "report" and module_name:
        report = migrator.generate_report(module_name)

        print(f"\n=== Migration Report for {module_name} ===")
        print(f"Files: {report.get('files', 0)}")
        print(f"Tests: {report.get('test_count', 0)}")
        print(f"MATRIZ Compliant: {'Yes' if report.get('matriz_compliant') else 'No'}")
        print(f"Ready for Migration: {'Yes' if report.get('ready') else 'No'}")

        if report.get("illegal_imports"):
            print(f"\nIllegal Imports ({len(report['illegal_imports'])}):")
            for imp in report["illegal_imports"][:5]:
                print(f"  - {imp}")

        if report.get("circular_deps"):
            print("\nCircular Dependencies:")
            for dep, files in report["circular_deps"].items():
                print(f"  {module_name} → {dep}: {len(files)} files")

    else:
        print("Invalid command or missing module name")
        sys.exit(1)


if __name__ == "__main__":
    main()