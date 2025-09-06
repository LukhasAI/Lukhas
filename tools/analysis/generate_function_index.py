#!/usr/bin/env python3
"""
LUKHAS  Function Index Generator
Creates a comprehensive index of all functions in the codebase
"""

import ast
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class FunctionIndexGenerator:
    def __init__(self, root_path: str = ".", timezone):
        self.root_path = Path(root_path).resolve()
        self.index = defaultdict(dict)
        self.decorator_usage = defaultdict(list)
        self.lukhas_functions = []

    def generate_index(self) -> dict[str, Any]:
        """Generate comprehensive function index"""
        print("🔍 Generating function index...")

        # Get all Python files
        python_files = list(self.root_path.rglob("*.py"))
        total_files = len(python_files)
        print(f"📁 Scanning {total_files} Python files for functions...")

        function_count = 0
        for i, file_path in enumerate(python_files):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{total_files} files...")

            # Skip archive directories
            if any(skip in str(file_path) for skip in ["._cleanup_archive", "__pycache__", ".git"]):
                continue

            functions_found = self._extract_functions(file_path)
            function_count += functions_found

        print(f"✅ Found {function_count} functions")
        return self._create_report()

    def _extract_functions(self, file_path: Path) -> int:
        """Extract function information from a file"""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))

            relative_path = file_path.relative_to(self.root_path)
            module_name = str(relative_path).replace("/", ".").replace(".py", "")

            function_count = 0

            # Extract module-level functions
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node, file_path, module_name)

                    # Organize by module
                    module_parts = str(relative_path).split("/")
                    top_module = module_parts[0] if module_parts else "root"

                    self.index[top_module][node.name] = func_info

                    # Track LUKHAS-specific functions
                    if self._is_lukhas_function(node.name, func_info):
                        self.lukhas_functions.append(
                            {
                                "name": node.name,
                                "module": module_name,
                                "info": func_info,
                            }
                        )

                    function_count += 1

            return function_count

        except Exception:
            return 0

    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, module_name: str) -> dict[str, Any]:
        """Analyze a function node and extract information"""
        # Extract parameters
        params = []
        defaults = []

        for arg in node.args.args:
            params.append(arg.arg)

        # Extract default values (simplified)
        for default in node.args.defaults:
            if isinstance(default, ast.Constant):
                defaults.append(str(default.value))
            else:
                defaults.append("...")

        # Extract decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
                self.decorator_usage[decorator.id].append({"function": node.name, "module": module_name})
            elif isinstance(decorator, ast.Attribute):
                decorator_name = (
                    f"{decorator.value.id if isinstance(decorator.value, ast.Name) else '...'}.{decorator.attr}"
                )
                decorators.append(decorator_name)

        # Extract return type if available
        return_type = None
        if node.returns:
            return_type = self._get_annotation_string(node.returns)

        # Extract docstring
        docstring = ast.get_docstring(node)

        # Check if it's async
        is_async = isinstance(node, ast.AsyncFunctionDef)

        # Simple complexity metric (number of nodes in function body)
        complexity = sum(1 for _ in ast.walk(node))

        return {
            "file": str(file_path.relative_to(self.root_path)),
            "module": module_name,
            "line": node.lineno,
            "type": "async_function" if is_async else "function",
            "params": params,
            "defaults": defaults,
            "decorators": decorators,
            "returns": return_type,
            "complexity": complexity,
            "docstring": (docstring[:100] + "..." if docstring and len(docstring) > 100 else docstring),
        }

    def _get_annotation_string(self, annotation) -> str:
        """Convert annotation AST to string"""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            return f"{self._get_annotation_string(annotation.value)}[...]"
        else:
            return "Any"

    def _is_lukhas_function(self, name: str, info: dict[str, Any]) -> bool:
        """Check if function is LUKHAS-specific"""
        lukhas_keywords = [
            "fold",
            "drift",
            "resonance",
            "oscillation",
            "glyph",
            "quantum",
            "consciousness",
            "dream",
            "emotion",
            "bio",
            "symbolic",
            "trace",
            "mutation",
            "helix",
            "crista",
        ]

        # Check function name
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in lukhas_keywords):
            return True

        # Check docstring
        if info["docstring"]:
            doc_lower = info["docstring"].lower()
            if any(keyword in doc_lower for keyword in lukhas_keywords):
                return True

        return False

    def _create_report(self) -> dict[str, Any]:
        """Create the final index report"""
        # Calculate statistics
        total_functions = sum(len(funcs) for funcs in self.index.values())
        modules_with_functions = len([m for m in self.index if self.index[m]])

        # Find most used decorators
        decorator_stats = sorted(
            [(dec, len(uses)) for dec, uses in self.decorator_usage.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Find most complex functions
        complex_functions = []
        for module, functions in self.index.items():
            for func_name, info in functions.items():
                complex_functions.append((func_name, module, info["complexity"], len(info["params"])))
        complex_functions.sort(key=lambda x: x[2], reverse=True)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "summary": {
                "total_functions": total_functions,
                "modules_with_functions": modules_with_functions,
                "lukhas_specific_functions": len(self.lukhas_functions),
                "most_used_decorators": decorator_stats,
                "most_complex_functions": [(f[0], f[1], f[2]) for f in complex_functions[:10]],
            },
            "index": dict(self.index),
            "decorator_usage": dict(self.decorator_usage),
            "lukhas_functions": self.lukhas_functions[:50],  # First 50 LUKHAS functions
        }

        return report

    def generate_api_docs(self, index: dict[str, Any]) -> str:
        """Generate API documentation from index"""
        lines = ["# LUKHAS  Function API Reference\n"]
        lines.append(f"Generated: {index['timestamp']}\n")
        lines.append(f"Total Functions: {index['summary']['total_functions']}\n")

        # LUKHAS-specific functions section
        if index["lukhas_functions"]:
            lines.append("## LUKHAS-Specific Functions\n")
            lines.append("Functions implementing core LUKHAS concepts:\n")

            for func_data in index["lukhas_functions"][:20]:
                func = func_data["info"]
                lines.append(f"### `{func_data['name']}`")
                lines.append(f"- **Module**: `{func_data['module']}`")
                lines.append(f"- **File**: `{func['file']}:{func['line']}`")

                if func["params"]:
                    lines.append(f"- **Parameters**: {', '.join(func['params'])}")

                if func["returns"]:
                    lines.append(f"- **Returns**: `{func['returns']}`")

                if func["docstring"]:
                    lines.append(f"- **Description**: {func['docstring']}")

                lines.append("")

        # Module sections
        lines.append("## Functions by Module\n")

        for module in sorted(index["index"].keys()):
            functions = index["index"][module]
            if not functions:
                continue

            lines.append(f"### {module}\n")

            # Group by functionality
            for func_name in sorted(functions.keys())[:20]:  # Limit to 20 per module
                info = functions[func_name]

                # Function signature
                params_str = ", ".join(info["params"]) if info["params"] else ""
                return_str = f" -> {info['returns']}" if info["returns"] else ""

                lines.append(f"- `{func_name}({params_str}){return_str}`")

                if info["decorators"]:
                    lines.append(f"  - Decorators: {', '.join(info['decorators'])}")

                if info["docstring"]:
                    lines.append(f"  - {info['docstring']}")

            if len(functions) > 20:
                lines.append(f"  - ... and {len(functions) - 20} more functions")

            lines.append("")

        return "\n".join(lines)


def main():
    generator = FunctionIndexGenerator()
    index = generator.generate_index()

    # Save JSON index
    json_path = Path("docs/registries/function_index.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w") as f:
        json.dump(index, f, indent=2)

    # Save API documentation
    api_docs = generator.generate_api_docs(index)
    api_path = Path("docs/registries/FUNCTION_API.md")

    with open(api_path, "w") as f:
        f.write(api_docs)

    # Print summary
    print("\n📊 FUNCTION INDEX SUMMARY:")
    print(f"   Total functions: {index['summary']['total_functions']}")
    print(f"   LUKHAS-specific: {index['summary']['lukhas_specific_functions']}")

    print("\n🎯 Most Used Decorators:")
    for decorator, count in index["summary"]["most_used_decorators"][:5]:
        print(f"   @{decorator}: {count} uses")

    print("\n🔧 Most Complex Functions:")
    for func_name, module, complexity in index["summary"]["most_complex_functions"][:5]:
        print(f"   {func_name} ({module}): complexity {complexity}")

    print("\n📄 Index saved to:")
    print(f"   JSON: {json_path}")
    print(f"   API Docs: {api_path}")


if __name__ == "__main__":
    main()
