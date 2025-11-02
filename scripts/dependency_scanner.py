#!/usr/bin/env python3
"""
LUKHAS Dependency Scanner
Scans actual Python imports to build real dependency matrix
"""

import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set


class DependencyScanner:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.dependencies = defaultdict(set)
        self.module_files = defaultdict(list)

    def scan_file(self, file_path: Path) -> Set[str]:
        """Extract imports from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            return imports
        except Exception as e:
            logger.debug(f"Expected optional failure: {e}")
            return set()

    def scan_module(self, module_path: Path, module_name: str):
        """Scan all Python files in a module"""
        if not module_path.exists():
            return

        for py_file in module_path.glob("**/*.py"):
            if "__pycache__" in str(py_file):
                continue

            self.module_files[module_name].append(str(py_file))
            imports = self.scan_file(py_file)

            # Filter to lukhas/candidate imports
            lukhas_imports = {imp for imp in imports if imp in ['lukhas', 'candidate', 'MATRIZ']}
            self.dependencies[module_name].update(lukhas_imports)

    def scan_all_modules(self):
        """Scan lukhas and candidate modules"""
        # Scan lukhas modules
        lukhas_path = self.root_path / "lukhas"
        if lukhas_path.exists():
            for module_dir in lukhas_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    module_name = f"lukhas.{module_dir.name}"
                    self.scan_module(module_dir, module_name)

        # Scan candidate modules
        candidate_path = self.root_path / "candidate"
        if candidate_path.exists():
            for module_dir in candidate_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('.'):
                    module_name = f"candidate.{module_dir.name}"
                    self.scan_module(module_dir, module_name)

    def generate_matrix(self) -> Dict:
        """Generate dependency matrix JSON"""
        matrix = {
            "metadata": {
                "schema_version": "1.2.0",
                "generated_at": "2025-09-20T23:20:00Z",
                "analysis_type": "actual_import_scanning",
                "total_modules": len(self.dependencies),
                "scan_method": "AST_python_import_analysis"
            },
            "module_dependency_matrix": {},
            "statistics": {
                "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
                "lukhas_modules": len([m for m in self.dependencies.keys() if m.startswith('lukhas.')]),
                "candidate_modules": len([m for m in self.dependencies.keys() if m.startswith('candidate.')]),
                "file_count": {module: len(files) for module, files in self.module_files.items()}
            }
        }

        for module, deps in self.dependencies.items():
            matrix["module_dependency_matrix"][module] = {
                "internal_dependencies": list(deps),
                "file_count": len(self.module_files[module]),
                "sample_files": self.module_files[module][:3]  # First 3 files as samples
            }

        return matrix


if __name__ == "__main__":
    scanner = DependencyScanner("/Users/agi_dev/LOCAL-REPOS/Lukhas")
    scanner.scan_all_modules()
    matrix = scanner.generate_matrix()

    print(json.dumps(matrix, indent=2))
