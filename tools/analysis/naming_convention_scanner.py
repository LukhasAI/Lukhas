#!/usr/bin/env python3
"""
LUKHAS  Naming Convention Scanner
Identifies classes, functions, and files that don't follow naming conventions
"""

import ast
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class NamingConventionScanner:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.violations = {"classes": [], "functions": [], "files": [], "modules": []}
        self.lukhas_terms = {
            "memory_fold",
            "dream_resonance",
            "qi_consciousness",
            "bio_oscillation",
            "symbolic_mutation",
            "emotional_drift",
            "trace_trail",
            "glyph_tokens",
            "crista",
            "helix",
            "resonance",
            "oscillation",
            "fold",
            "drift",
        }

    def scan_codebase(self) -> dict[str, Any]:
        """Scan entire codebase for naming violations"""
        print("🔍 Scanning for naming convention violations...")

        # Get all Python files
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        print(f"📁 Scanning {total_files} Python files...")

        for i, file_path in enumerate(python_files):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{total_files} files...")

            # Skip archive directories
            if any(skip in str(file_path) for skip in ["._cleanup_archive", "__pycache__", ".git"]):
                continue

            self._check_file_naming(file_path)
            self._scan_file_contents(file_path)

        return self._generate_report()

    def _check_file_naming(self, file_path: Path):
        """Check if file name follows conventions"""
        file_name = file_path.name

        # Check for special characters
        if re.search(r"[^a-zA-Z0-9_.]", file_name):
            self.violations["files"].append(
                {
                    "path": str(file_path.relative_to(self.root_path)),
                    "name": file_name,
                    "issue": "Contains special characters",
                    "suggestion": self._suggest_file_name(file_name),
                }
            )

        # Check for PascalCase in file names (should be snake_case)
        elif file_name != "__init__.py" and re.search(r"[A-Z]", file_name.replace(".py", "")):
            self.violations["files"].append(
                {
                    "path": str(file_path.relative_to(self.root_path)),
                    "name": file_name,
                    "issue": "Not in snake_case",
                    "suggestion": self._to_snake_case(file_name.replace(".py", "")) + ".py",
                }
            )

    def _scan_file_contents(self, file_path: Path):
        """Scan file contents for class and function naming violations"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class_name(node, file_path)
                elif isinstance(node, ast.FunctionDef):
                    self._check_function_name(node, file_path)

        except Exception:
            # Ignore files with syntax errors
            pass

    def _check_class_name(self, node: ast.ClassDef, file_path: Path):
        """Check if class name follows PascalCase"""
        class_name = node.name

        # Check for snake_case classes (should be PascalCase)
        if "_" in class_name or class_name[0].islower():
            self.violations["classes"].append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": node.lineno,
                    "name": class_name,
                    "issue": "Not in PascalCase",
                    "suggestion": self._to_pascal_case(class_name),
                }
            )

        # Check for special characters
        elif re.search(r"[^a-zA-Z0-9]", class_name):
            clean_name = re.sub(r"[^a-zA-Z0-9]", "", class_name)
            self.violations["classes"].append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": node.lineno,
                    "name": class_name,
                    "issue": "Contains special characters",
                    "suggestion": self._to_pascal_case(clean_name),
                }
            )

    def _check_function_name(self, node: ast.FunctionDef, file_path: Path):
        """Check if function name follows snake_case"""
        func_name = node.name

        # Skip dunder methods
        if func_name.startswith("__") and func_name.endswith("__"):
            return

        # Check for PascalCase functions (should be snake_case)
        if re.search(r"[A-Z]", func_name):
            self.violations["functions"].append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": node.lineno,
                    "name": func_name,
                    "issue": "Not in snake_case",
                    "suggestion": self._to_snake_case(func_name),
                }
            )

        # Check for special characters
        elif re.search(r"[^a-z0-9_]", func_name):
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", func_name)
            self.violations["functions"].append(
                {
                    "file": str(file_path.relative_to(self.root_path)),
                    "line": node.lineno,
                    "name": func_name,
                    "issue": "Contains special characters",
                    "suggestion": self._to_snake_case(clean_name),
                }
            )

    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case while preserving LUKHAS terms"""
        # Replace special characters
        name = name.replace("Λ", "lambda").replace("λ", "lambda")

        # Convert PascalCase to snake_case
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # Preserve LUKHAS terms
        for term in self.lukhas_terms:
            if term in result:
                result = result.replace(term.replace("_", ""), term)

        return result

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase"""
        # Handle special characters
        name = name.replace("Λ", "Lambda").replace("λ", "Lambda")

        # Convert snake_case to PascalCase
        parts = name.split("_")
        return "".join(word.capitalize() for word in parts if word)

    def _suggest_file_name(self, file_name: str) -> str:
        """Suggest a compliant file name"""
        # Remove .py extension
        base_name = file_name.replace(".py", "")

        # Convert to snake_case
        suggestion = self._to_snake_case(base_name)

        return suggestion + ".py"

    def _generate_report(self) -> dict[str, Any]:
        """Generate comprehensive naming convention report"""
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_violations": sum(len(v) for v in self.violations.values()),
                "class_violations": len(self.violations["classes"]),
                "function_violations": len(self.violations["functions"]),
                "file_violations": len(self.violations["files"]),
                "module_violations": len(self.violations["modules"]),
            },
            "violations": self.violations,
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if self.violations["files"]:
            recommendations.append(f"Rename {len(self.violations['files'])} files to snake_case format")

        if self.violations["classes"]:
            recommendations.append(f"Update {len(self.violations['classes'])} class names to PascalCase")

        if self.violations["functions"]:
            recommendations.append(f"Convert {len(self.violations['functions'])} function names to snake_case")

        recommendations.append("Use the safe_rename.py tool to automatically fix naming violations")

        return recommendations


def main():
    scanner = NamingConventionScanner()
    report = scanner.scan_codebase()

    # Save report
    output_path = Path("docs/reports/analysis/NAMING_CONVENTION_VIOLATIONS.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 NAMING CONVENTION SUMMARY:")
    print(f"   Total violations: {report['summary']['total_violations']}")
    print(f"   Class violations: {report['summary']['class_violations']}")
    print(f"   Function violations: {report['summary']['function_violations']}")
    print(f"   File violations: {report['summary']['file_violations']}")

    # Show examples
    if report["violations"]["files"]:
        print("\n📁 FILE NAMING VIOLATIONS (first 5):")
        for violation in report["violations"]["files"][:5]:
            print(f"   {violation['name']} → {violation['suggestion']}")

    if report["violations"]["classes"]:
        print("\n🏛️ CLASS NAMING VIOLATIONS (first 5):")
        for violation in report["violations"]["classes"][:5]:
            print(f"   {violation['name']} → {violation['suggestion']}")
            print(f"      in {violation['file']}:{violation['line']}")

    if report["violations"]["functions"]:
        print("\n🔧 FUNCTION NAMING VIOLATIONS (first 5):")
        for violation in report["violations"]["functions"][:5]:
            print(f"   {violation['name']} → {violation['suggestion']}")
            print(f"      in {violation['file']}:{violation['line']}")

    print(f"\n📄 Full report saved to: {output_path}")


if __name__ == "__main__":
    main()
