#!/usr/bin/env python3
"""
LUKHAS  Class Registry Generator
Creates a comprehensive registry of all classes in the codebase
"""

import ast
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class ClassRegistryGenerator:

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.registry = defaultdict(dict)
        self.inheritance_map = defaultdict(list)
        self.module_classes = defaultdict(list)

    def generate_registry(self) -> dict[str, Any]:
        """Generate comprehensive class registry"""
        print(" Generating class registry...")

        # Get all Python files
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        print(f" Scanning {total_files} Python files for classes...")

        class_count = 0
        for i, file_path in enumerate(python_files):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{total_files} files...")

            # Skip archive directories
            if any(
                skip in str(file_path)
                for skip in ["._cleanup_archive", "__pycache__", ".git"]
            ):
                continue

            classes_found = self._extract_classes(file_path)
            class_count += classes_found

        print(f" Found {class_count} classes")
        return self._create_report()

    def _extract_classes(self, file_path: Path) -> int:
        """Extract class information from a file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            relative_path = file_path.relative_to(self.root_path)
            module_name = str(relative_path).replace("/", ".").replace(".py", "")

            class_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node, file_path, module_name)

                    # Organize by module
                    module_parts = str(relative_path).split("/")
                    top_module = module_parts[0] if module_parts else "root"

                    self.registry[top_module][node.name] = class_info
                    self.module_classes[module_name].append(node.name)

                    # Track inheritance
                    for base in class_info["base_classes"]:
                        self.inheritance_map[base].append(
                            {"class": node.name, "module": module_name}
                        )

                    class_count += 1

            return class_count

        except Exception:
            return 0

    def _analyze_class(
        self, node: ast.ClassDef, file_path: Path, module_name: str
    ) -> dict[str, Any]:
        """Analyze a class node and extract information"""
        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(f"{base.value.id}.{base.attr}")

        # Extract methods
        methods = []
        properties = []
        class_methods = []
        static_methods = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Check decorators
                decorators = [
                    d.id for d in item.decorator_list if isinstance(d, ast.Name)
                ]

                if "property" in decorators:
                    properties.append(item.name)
                elif "classmethod" in decorators:
                    class_methods.append(item.name)
                elif "staticmethod" in decorators:
                    static_methods.append(item.name)
                else:
                    methods.append(item.name)

        # Extract docstring
        docstring = ast.get_docstring(node)

        return {
            "file": str(file_path.relative_to(self.root_path)),
            "module": module_name,
            "line": node.lineno,
            "type": "class",
            "base_classes": base_classes,
            "methods": methods,
            "properties": properties,
            "class_methods": class_methods,
            "static_methods": static_methods,
            "has_init": "__init__" in methods,
            "docstring": (
                docstring[:100] + "..."
                if docstring and len(docstring) > 100
                else docstring
            ),
        }

    def _create_report(self) -> dict[str, Any]:
        """Create the final registry report"""
        # Calculate statistics
        total_classes = sum(len(classes) for classes in self.registry.values())
        modules_with_classes = len([m for m in self.registry if self.registry[m]])

        # Find most inherited classes
        most_inherited = sorted(
            [(base, len(children)) for base, children in self.inheritance_map.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Find largest classes (by method count)
        largest_classes = []
        for module, classes in self.registry.items():
            for class_name, _info in classes.items():
                # SYNTAX_ERROR_FIXED:                 method_count =
                # len(info['methods']) + len(info['properties']) + " +
                # "len(info['class_methods']) + len(info['static_methods'])
                largest_classes.append((class_name, module, method_count))
        largest_classes.sort(key=lambda x: x[2], reverse=True)

        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_classes": total_classes,
                "modules_with_classes": modules_with_classes,
                "total_modules": len(self.module_classes),
                "most_inherited_bases": most_inherited[:5],
                "largest_classes": [(c[0], c[1], c[2]) for c in largest_classes[:10]],
            },
            "registry": dict(self.registry),
            "inheritance_map": dict(self.inheritance_map),
            "module_index": dict(self.module_classes),
        }

        return report

    def generate_markdown_docs(self, registry: dict[str, Any]) -> str:
        """Generate markdown documentation from registry"""
        lines = ["# LUKHAS  Class Registry\n"]
        lines.append(f"Generated: {registry['timestamp']}\n")
        lines.append(f"Total Classes: {registry['summary']['total_classes']}\n")

        # Table of contents
        lines.append("#)  #  Table of Contents\n"
        for module in sorted(registry["registry"].keys()):
            if registry["registry"][module]:
                lines.append(f"- [{module}](")
        lines.append("")

        # Module sections
        for module in sorted(registry["registry"].keys()):
            classes = registry["registry"][module]
            if not classes:
                continue

            lines.append(f"#")

            for class_name in sorted(classes.keys()):
                info = classes[class_name]
                lines.append(f"##")
                lines.append(f"- **File**: `{info['file']}`")
                lines.append(f"- **Line**: {info['line']}")

                if info["base_classes"]:
                    lines.append(f"- **Inherits**: {', '.join(info['base_classes'])}")

                if info["docstring"]:
                    lines.append(f"- **Description**: {info['docstring']}")

                if info["methods"]:
                    lines.append(f"- **Methods**: {', '.join(info['methods'][:5])}")
                    if len(info["methods"]) > 5:
                        lines.append(f"  (and {len(info['methods']) - 5} more)")

                lines.append("")

        return "\n".join(lines)


def main():
    generator = ClassRegistryGenerator()
    registry = generator.generate_registry()

    # Save JSON registry
    json_path = Path("docs/registries/class_registry.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w") as f:
        json.dump(registry, f, indent=2)

    # Save markdown documentation
    markdown = generator.generate_markdown_docs(registry)
    md_path = Path("docs/registries/CLASS_REGISTRY.md")

    with open(md_path, "w") as f:
        f.write(markdown)

    # Print summary
    print("\n CLASS REGISTRY SUMMARY:")
    print(f"   Total classes: {registry['summary']['total_classes']}")
    print(f"   Modules with classes: {registry['summary']['modules_with_classes']}")

    print("\n Most Inherited Base Classes:")
    for base, count in registry["summary"]["most_inherited_bases"]:
        print(f"   {base}: {count} subclasses")

    print("\n Largest Classes (by method count):")
    for class_name, module, count in registry["summary"]["largest_classes"][:5]:
        print(f"   {class_name} ({module}): {count} methods")

    print("\n Registry saved to:")
    print(f"   JSON: {json_path}")
    print(f"   Markdown: {md_path}")


if __name__ == "__main__":
    main()
