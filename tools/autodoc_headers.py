#!/usr/bin/env python3
"""
Auto-Documentation Header Generator for LUKHAS AI
Scans lukhas/accepted/ modules and adds 3-line docstring headers
Constellation Framework: ⚛️🧠🛡️
"""

import ast
import os
from pathlib import Path


class DocHeaderGenerator:
    """Generates documentation headers for Python modules"""

    def __init__(self, base_path: str = "lukhas/accepted"):
        self.base_path = Path(base_path)
        self.report = {
            "processed": [],
            "skipped": [],
            "errors": [],
            "stats": {
                "total_files": 0,
                "documented": 0,
                "undocumented": 0,
                "headers_added": 0,
            },
        }

    def scan_modules(self) -> list[Path]:
        """Scan for Python modules in accepted/"""
        modules = []
        for py_file in self.base_path.rglob("*.py"):
            # Skip test files and __pycache__
            if "__pycache__" not in str(py_file) and not py_file.name.startswith("test_"):
                modules.append(py_file)
        return sorted(modules)

    def has_docstring(self, file_path: Path) -> bool:
        """Check if module already has a docstring"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST to check for module docstring
            tree = ast.parse(content)

            # Module docstring is the first statement if it's a string
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, (ast.Str, ast.Constant)):
                    return True

            # Also check for triple quotes at the beginning
            if content.lstrip().startswith('"""') or content.lstrip().startswith("'''"):
                return True

        except Exception as e:
            self.report["errors"].append(f"{file_path}: {e}")
            return True  # Assume documented on error to be safe

        return False

    def extract_module_info(self, file_path: Path) -> dict[str, any]:
        """Extract key information from module"""
        info = {
            "path": file_path,
            "name": file_path.stem,
            "package": file_path.parent.name,
            "classes": [],
            "functions": [],
            "imports": [],
            "purpose": "Module implementation",  # Default
            "triad_component": self._get_triad_component(file_path),
        }

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Extract classes
                if isinstance(node, ast.ClassDef):
                    info["classes"].append(node.name)

                # Extract top-level functions
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions
                    if not any(
                        isinstance(p, ast.ClassDef) for p in ast.walk(tree) if hasattr(p, "body") and node in p.body
                    ):
                        info["functions"].append(node.name)

                # Extract imports to understand dependencies
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    info["imports"].append(node.module.split(".")[0])

            # Deduplicate imports
            info["imports"] = list(set(info["imports"]))

            # Infer purpose from content
            info["purpose"] = self._infer_purpose(info)

        except Exception as e:
            self.report["errors"].append(f"{file_path}: {e}")

        return info

    def _get_triad_component(self, file_path: Path) -> str:
        """Map file path to Trinity component"""
        path_str = str(file_path).lower()

        if any(term in path_str for term in ["identity", "auth", "lid", "lambda"]):
            return "⚛️"
        elif any(term in path_str for term in ["consent", "lukhas.governance", "guardian", "ethics", "policy"]):
            return "🛡️"
        elif any(term in path_str for term in ["consciousness", "brain", "lukhas.memory", "context"]):
            return "🧠"
        else:
            # Default based on parent directory
            if "bio" in path_str:
                return "🧠"
            elif "core" in path_str:
                return "⚛️"
            else:
                return "🧠"

    def _infer_purpose(self, info: dict) -> str:
        """Infer module purpose from its contents"""
        name = info["name"].lower()
        classes = [c.lower() for c in info["classes"]]
        [f.lower() for f in info["functions"]]

        # Check for common patterns
        if "adapter" in name:
            return "Service adapter implementation"
        elif "interface" in name:
            return "Interface definitions"
        elif "config" in name:
            return "Configuration management"
        elif "test" in name:
            return "Test utilities"
        elif "__init__" in name:
            if info["classes"] or info["functions"]:
                return "Package exports and initialization"
            else:
                return "Package marker"
        elif "base" in name or "abstract" in any(classes):
            return "Base classes and abstractions"
        elif "manager" in name or "manager" in classes:
            return "Resource management"
        elif "service" in name or "service" in classes:
            return "Service implementation"
        elif "model" in name:
            return "Data models"
        elif "util" in name or "helper" in name:
            return "Utility functions"
        elif any(term in name for term in ["colony", "swarm", "cluster"]):
            return "Distributed processing"
        else:
            # Generic based on contents
            if info["classes"] and not info["functions"]:
                return "Class definitions"
            elif info["functions"] and not info["classes"]:
                return "Function library"
            elif info["classes"] and info["functions"]:
                return "Mixed implementation"
            else:
                return "Module implementation"

    def generate_header(self, info: dict) -> str:
        """Generate a 3-line docstring header"""
        # Line 1: Module name and package
        line1 = f"{info['package'].title()}.{info['name']} - {info['purpose']}"

        # Line 2: Key exports
        exports = []
        if info["classes"]:
            exports.append(f"{len(info['classes'])} classes")
        if info["functions"]:
            exports.append(f"{len(info['functions'])} functions")
        if not exports:
            exports.append("Package module")
        line2 = f"Provides: {', '.join(exports)}"

        # Line 3: Trinity component
        line3 = f"Trinity: {info['triad_component']} Component"

        # Format as docstring
        header = f'"""\n{line1}\n{line2}\n{line3}\n"""\n\n'

        return header

    def add_header_to_file(self, file_path: Path, header: str) -> bool:
        """Add header to file if not present"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for shebang
            lines = content.split("\n")

            if lines and lines[0].startswith("#!"):
                # Insert after shebang
                new_content = lines[0] + "\n" + header + "\n".join(lines[1:])
            else:
                # Insert at beginning
                new_content = header + content

            # Write back (in dry-run mode, would skip this)
            if os.getenv("AUTODOC_DRY_RUN", "").lower() != "true":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

            return True

        except Exception as e:
            self.report["errors"].append(f"Failed to add header to {file_path}: {e}")
            return False

    def process_all(self, dry_run: bool = True) -> dict:
        """Process all modules and generate headers"""
        if dry_run:
            os.environ["AUTODOC_DRY_RUN"] = "true"

        modules = self.scan_modules()
        self.report["stats"]["total_files"] = len(modules)

        for module_path in modules:
            # Check if already documented
            if self.has_docstring(module_path):
                self.report["skipped"].append(str(module_path))
                self.report["stats"]["documented"] += 1
                continue

            # Extract info and generate header
            info = self.extract_module_info(module_path)
            header = self.generate_header(info)

            # Add header (or simulate in dry-run)
            if dry_run:
                self.report["processed"].append({"path": str(module_path), "header": header, "info": info})
            else:
                if self.add_header_to_file(module_path, header):
                    self.report["processed"].append(str(module_path))
                    self.report["stats"]["headers_added"] += 1

            self.report["stats"]["undocumented"] += 1

        return self.report

    def generate_report(self, output_path: str = "docs/AUDIT/DOCS_TODO.md"):
        """Generate documentation report"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write("#  LUKHAS AI Documentation Status Report\n\n")
            f.write("## Summary\n\n")
            f.write(f"- **Total Modules**: {self.report['stats']['total_files']}\n")
            f.write(f"- **Documented**: {self.report['stats']['documented']}\n")
            f.write(f"- **Undocumented**: {self.report['stats']['undocumented']}\n")
            f.write(f"- **Headers Added**: {self.report['stats']['headers_added']}\n\n")

            if self.report["processed"]:
                f.write("## Modules Needing Documentation\n\n")

                # In dry-run mode, show what would be added
                if isinstance(self.report["processed"][0], dict):
                    for item in self.report["processed"]:
                        f.write(f"### `{item['path']}`\n\n")
                        f.write("Suggested header:\n```python\n")
                        f.write(item["header"])
                        f.write("```\n\n")

                        if item["info"]["classes"]:
                            f.write(f"**Classes**: {', '.join(item['info']['classes'])}\n\n")
                        if item["info"]["functions"]:
                            f.write(f"**Functions**: {', '.join(item['info']['functions'])}\n\n")
                else:
                    for path in self.report["processed"]:
                        f.write(f"- `{path}`\n")

            if self.report["errors"]:
                f.write("\n## Errors\n\n")
                for error in self.report["errors"]:
                    f.write(f"- {error}\n")

        print(f"Documentation report generated: {output_path}")
        return output_path


def main():
    """Main entry point for auto-documentation"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-generate documentation headers")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing files")
    parser.add_argument("--path", default="lukhas/accepted", help="Base path to scan")
    parser.add_argument("--report", default="docs/AUDIT/DOCS_TODO.md", help="Report output path")

    args = parser.parse_args()

    generator = DocHeaderGenerator(args.path)
    report = generator.process_all(dry_run=args.dry_run)
    report_path = generator.generate_report(args.report)

    # Print summary
    print("\n" + "=" * 60)
    print("📝 AUTO-DOCUMENTATION COMPLETE")
    print("=" * 60)
    print(f"Total modules: {report['stats']['total_files']}")
    print(f"Already documented: {report['stats']['documented']}")
    print(f"Need documentation: {report['stats']['undocumented']}")

    if args.dry_run:
        print("\n⚠️ DRY RUN - No files were modified")
        print(f"Review report at: {report_path}")
    else:
        print(f"\n✅ Added {report['stats']['headers_added']} headers")

    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    exit(main())
