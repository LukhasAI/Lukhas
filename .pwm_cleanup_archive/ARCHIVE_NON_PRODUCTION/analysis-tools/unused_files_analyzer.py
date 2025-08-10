#!/usr/bin/env python3
"""
Unused Files Analyzer

Analyzes the codebase to identify files that are not imported or referenced anywhere.
"""

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set


class UnusedFilesAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.python_files: Set[Path] = set()
        self.imports_graph: Dict[str, Set[str]] = {}
        self.file_references: Dict[str, Set[str]] = {}
        self.excluded_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "venv",
            "env",
            ".venv",
            "dist",
            "build",
            "htmlcov",
            ".mypy_cache",
            ".ruff_cache",
        }
        self.excluded_patterns = {
            "test_",
            "_test.py",
            "conftest.py",
            "setup.py",
            "__main__.py",
            "example_",
            "demo_",
            "sample_",
        }

    def analyze(self) -> Dict[str, any]:
        """Main analysis method"""
        print("🔍 Collecting Python files...")
        self._collect_python_files()

        print("📊 Analyzing imports and references...")
        self._analyze_imports()

        print("🔗 Building connectivity graph...")
        connectivity = self._analyze_connectivity()

        print("🚫 Identifying unused files...")
        unused_files = self._identify_unused_files()

        return {
            "total_files": len(self.python_files),
            "unused_files": unused_files,
            "connectivity": connectivity,
            "import_statistics": self._get_import_statistics(),
        }

    def _collect_python_files(self):
        """Collect all Python files in the repository"""
        for root, dirs, files in os.walk(self.root_path):
            # Remove excluded directories from dirs to prevent walking into them
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            root_path = Path(root)

            for file in files:
                if file.endswith(".py"):
                    file_path = root_path / file
                    # Skip excluded patterns
                    if not any(pattern in file for pattern in self.excluded_patterns):
                        self.python_files.add(file_path)

    def _analyze_imports(self):
        """Analyze imports in all Python files"""
        for file_path in self.python_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find imports
                try:
                    tree = ast.parse(content)
                    imports = self._extract_imports(tree, file_path)
                    self.imports_graph[str(file_path)] = imports
                except SyntaxError:
                    # Fallback to regex for files with syntax errors
                    imports = self._extract_imports_regex(content, file_path)
                    self.imports_graph[str(file_path)] = imports

                # Also look for string references to files
                references = self._extract_file_references(content)
                self.file_references[str(file_path)] = references

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

    def _extract_imports(self, tree: ast.AST, file_path: Path) -> Set[str]:
        """Extract imports from AST"""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_file = self._resolve_import(alias.name, file_path)
                    if imported_file:
                        imports.add(imported_file)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_file = self._resolve_import(node.module, file_path)
                    if imported_file:
                        imports.add(imported_file)

        return imports

    def _extract_imports_regex(self, content: str, file_path: Path) -> Set[str]:
        """Fallback import extraction using regex"""
        imports = set()

        # Match import statements
        import_patterns = [
            r"^\s*import\s+(\S+)",
            r"^\s*from\s+(\S+)\s+import",
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                module = match.group(1)
                imported_file = self._resolve_import(module, file_path)
                if imported_file:
                    imports.add(imported_file)

        return imports

    def _resolve_import(self, module_name: str, from_file: Path) -> str:
        """Resolve an import to a file path"""
        # Handle relative imports
        if module_name.startswith("."):
            level = len(module_name) - len(module_name.lstrip("."))
            module_parts = module_name.lstrip(".").split(".")

            current_dir = from_file.parent
            for _ in range(level - 1):
                current_dir = current_dir.parent

            if module_parts[0]:
                potential_path = current_dir / "/".join(module_parts)
            else:
                potential_path = current_dir
        else:
            # Absolute import
            module_parts = module_name.split(".")
            potential_path = self.root_path / "/".join(module_parts)

        # Check for .py file
        py_file = potential_path.with_suffix(".py")
        if py_file in self.python_files:
            return str(py_file)

        # Check for __init__.py in directory
        init_file = potential_path / "__init__.py"
        if init_file in self.python_files:
            return str(init_file)

        return None

    def _extract_file_references(self, content: str) -> Set[str]:
        """Extract file references from strings in code"""
        references = set()

        # Look for string literals that might be file paths
        string_pattern = r'["\']([^"\']+\.py)["\']'
        for match in re.finditer(string_pattern, content):
            potential_file = match.group(1)
            # Try to resolve the path
            for py_file in self.python_files:
                if potential_file in str(py_file):
                    references.add(str(py_file))

        return references

    def _identify_unused_files(self) -> List[Dict[str, any]]:
        """Identify files that are never imported or referenced"""
        # Collect all imported/referenced files
        used_files = set()

        for imports in self.imports_graph.values():
            used_files.update(imports)

        for refs in self.file_references.values():
            used_files.update(refs)

        # Entry points that shouldn't be considered unused
        entry_points = {
            "main.py",
            "app.py",
            "run.py",
            "manage.py",
            "cli.py",
            "server.py",
            "api.py",
            "wsgi.py",
        }

        unused_files = []
        for file_path in self.python_files:
            file_str = str(file_path)
            file_name = file_path.name

            # Skip if it's an entry point
            if file_name in entry_points:
                continue

            # Skip if it's used
            if file_str in used_files:
                continue

            # Calculate file info
            rel_path = file_path.relative_to(self.root_path)
            size = file_path.stat().st_size

            unused_files.append(
                {
                    "path": str(rel_path),
                    "size_bytes": size,
                    "size_human": self._format_size(size),
                    "directory": str(rel_path.parent),
                }
            )

        # Sort by directory and then by name
        unused_files.sort(key=lambda x: x["path"])

        return unused_files

    def _analyze_connectivity(self) -> Dict[str, any]:
        """Analyze system connectivity"""
        # Identify key system hubs
        hub_patterns = [
            "*hub.py",
            "*_hub.py",
            "*orchestrator*.py",
            "*bridge*.py",
            "*coordinator*.py",
            "*manager*.py",
            "*engine*.py",
        ]

        hubs = []
        for file_path in self.python_files:
            for pattern in hub_patterns:
                if file_path.match(pattern):
                    rel_path = file_path.relative_to(self.root_path)

                    # Count incoming and outgoing connections
                    file_str = str(file_path)
                    incoming = sum(
                        1
                        for imports in self.imports_graph.values()
                        if file_str in imports
                    )
                    outgoing = len(self.imports_graph.get(file_str, set()))

                    hubs.append(
                        {
                            "path": str(rel_path),
                            "type": self._identify_hub_type(file_path.name),
                            "incoming_connections": incoming,
                            "outgoing_connections": outgoing,
                            "total_connections": incoming + outgoing,
                        }
                    )

        # Sort by total connections
        hubs.sort(key=lambda x: x["total_connections"], reverse=True)

        # Identify isolated components (files with no connections)
        isolated = []
        for file_path in self.python_files:
            file_str = str(file_path)
            incoming = sum(
                1 for imports in self.imports_graph.values() if file_str in imports
            )
            outgoing = len(self.imports_graph.get(file_str, set()))

            if incoming == 0 and outgoing == 0:
                rel_path = file_path.relative_to(self.root_path)
                isolated.append(str(rel_path))

        return {
            "key_hubs": hubs[:20],  # Top 20 most connected
            "isolated_files": isolated,
            "total_connections": sum(
                len(imports) for imports in self.imports_graph.values()
            ),
            "average_connections": (
                sum(len(imports) for imports in self.imports_graph.values())
                / len(self.python_files)
                if self.python_files
                else 0
            ),
        }

    def _identify_hub_type(self, filename: str) -> str:
        """Identify the type of hub based on filename"""
        if "orchestrator" in filename:
            return "orchestrator"
        elif "hub" in filename:
            return "hub"
        elif "bridge" in filename:
            return "bridge"
        elif "coordinator" in filename:
            return "coordinator"
        elif "manager" in filename:
            return "manager"
        elif "engine" in filename:
            return "engine"
        else:
            return "other"

    def _get_import_statistics(self) -> Dict[str, any]:
        """Get statistics about imports"""
        all_imports = []
        for imports in self.imports_graph.values():
            all_imports.extend(imports)

        # Count module imports
        module_counts = {}
        for imp in all_imports:
            module = Path(imp).parts[0] if Path(imp).parts else "root"
            module_counts[module] = module_counts.get(module, 0) + 1

        # Sort by count
        sorted_modules = sorted(module_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_imports": len(all_imports),
            "unique_imports": len(set(all_imports)),
            "most_imported_modules": sorted_modules[:10],
            "files_with_no_imports": sum(
                1 for imports in self.imports_graph.values() if not imports
            ),
        }

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    # Get repository root
    repo_root = Path(__file__).parent.parent

    analyzer = UnusedFilesAnalyzer(repo_root)
    results = analyzer.analyze()

    # Save results
    output_file = repo_root / "analysis-tools" / "unused_files_report.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("📋 UNUSED FILES ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Python files analyzed: {results['total_files']}")
    print(f"Unused files found: {len(results['unused_files'])}")
    print(
        f"Isolated files (no connections): {len(results['connectivity']['isolated_files'])}"
    )
    print(f"Total connections: {results['connectivity']['total_connections']}")
    print(
        f"Average connections per file: {results['connectivity']['average_connections']:.2f}"
    )

    print("\n🚫 TOP UNUSED FILES:")
    for file in results["unused_files"][:10]:
        print(f"  - {file['path']} ({file['size_human']})")

    print("\n🔗 TOP CONNECTED HUBS:")
    for hub in results["connectivity"]["key_hubs"][:10]:
        print(
            f"  - {hub['path']} ({hub['type']}) - {hub['total_connections']} connections"
        )

    print(f"\n✅ Full report saved to: {output_file}")


if __name__ == "__main__":
    main()
