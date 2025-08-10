#!/usr/bin/env python3
"""
Analyze and prioritize the most critical broken imports.
Focus on core modules that affect system functionality.
"""

import ast
import json
import os
from collections import Counter, defaultdict
from pathlib import Path


class CriticalImportAnalyzer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.broken_imports_by_module = defaultdict(list)
        self.module_importance = {}
        self.import_frequency = Counter()

        # Define critical modules by priority
        self.critical_modules = {
            "consciousness": 10,  # Core AGI functionality
            "memory": 10,  # Core memory system
            "api": 9,  # API endpoints
            "orchestration": 9,  # System orchestration
            "core": 8,  # Core utilities
            "bio": 7,  # Bio-inspired systems
            "symbolic": 7,  # Symbolic processing
            "features": 6,  # Feature modules
            "creativity": 5,  # Creative systems
            "tools": 4,  # Development tools
            "tests": 3,  # Test files
            "benchmarks": 2,  # Benchmarks
            "scripts": 1,  # Scripts
        }

    def analyze(self):
        """Analyze all Python files for broken imports."""
        print("Analyzing broken imports across the codebase...")

        # First pass: collect all broken imports
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            module_path = self._get_module_path(py_file)
            broken = self._analyze_file(py_file)

            if broken:
                self.broken_imports_by_module[module_path].extend(broken)

                # Track import frequency
                for imp in broken:
                    self.import_frequency[imp["import_statement"]] += 1

        # Calculate module importance scores
        self._calculate_importance_scores()

        # Generate report
        self._generate_report()

    def _get_module_path(self, file_path: Path) -> str:
        """Get the module category from file path."""
        parts = file_path.relative_to(self.root_path).parts
        if parts:
            return parts[0]
        return "root"

    def _analyze_file(self, file_path: Path) -> list:
        """Analyze a single file for broken imports."""
        broken_imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    # Check for incomplete imports
                    if not node.names or (
                        len(node.names) == 1 and not node.names[0].name
                    ):
                        broken_imports.append(
                            {
                                "file": str(file_path.relative_to(self.root_path)),
                                "line": node.lineno,
                                "import_statement": f"from {node.module} import",
                                "type": "incomplete",
                            }
                        )

                # Check for other patterns
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        # Check if it's trying to import a local module that might not exist
                        if "." in alias.name and not alias.name.startswith(
                            ("numpy", "pandas", "torch")
                        ):
                            broken_imports.append(
                                {
                                    "file": str(file_path.relative_to(self.root_path)),
                                    "line": node.lineno,
                                    "import_statement": f"import {alias.name}",
                                    "type": "possibly_broken",
                                }
                            )

        except SyntaxError:
            # File has syntax errors
            pass
        except Exception:
            pass

        return broken_imports

    def _calculate_importance_scores(self):
        """Calculate importance scores for each module."""
        for module, broken_list in self.broken_imports_by_module.items():
            base_priority = self.critical_modules.get(module, 0)

            # Factor in number of broken imports
            broken_count = len(broken_list)

            # Factor in how many other files import from this module
            import_refs = sum(
                1
                for imp in broken_list
                if any(
                    critical in imp["import_statement"]
                    for critical in ["core", "memory", "consciousness", "api"]
                )
            )

            # Calculate score
            score = (base_priority * 100) + (broken_count * 10) + (import_refs * 5)
            self.module_importance[module] = {
                "score": score,
                "priority": base_priority,
                "broken_count": broken_count,
                "critical_imports": import_refs,
            }

    def _generate_report(self):
        """Generate analysis report."""
        # Sort modules by importance
        sorted_modules = sorted(
            self.module_importance.items(), key=lambda x: x[1]["score"], reverse=True
        )

        report = {
            "summary": {
                "total_broken": sum(
                    len(imports) for imports in self.broken_imports_by_module.values()
                ),
                "affected_modules": len(self.broken_imports_by_module),
                "most_common_broken": self.import_frequency.most_common(10),
            },
            "critical_modules": [],
        }

        # Focus on top critical modules
        for module, info in sorted_modules[:10]:
            module_data = {
                "module": module,
                "importance_score": info["score"],
                "broken_imports": len(self.broken_imports_by_module[module]),
                "examples": self.broken_imports_by_module[module][
                    :5
                ],  # First 5 examples
                "fix_priority": (
                    "HIGH"
                    if info["priority"] >= 8
                    else "MEDIUM" if info["priority"] >= 5 else "LOW"
                ),
            }
            report["critical_modules"].append(module_data)

        # Save report
        output_path = (
            self.root_path
            / "scripts"
            / "import_migration"
            / "critical_imports_analysis.json"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 80)
        print("CRITICAL BROKEN IMPORTS ANALYSIS")
        print("=" * 80)
        print(f"\nTotal broken imports: {report['summary']['total_broken']}")
        print(f"Affected modules: {report['summary']['affected_modules']}")

        print("\n🎯 TOP PRIORITY MODULES TO FIX:")
        for module_data in report["critical_modules"][:5]:
            print(
                f"\n{module_data['module'].upper()} (Priority: {module_data['fix_priority']})"
            )
            print(f"  - Importance Score: {module_data['importance_score']}")
            print(f"  - Broken Imports: {module_data['broken_imports']}")
            print(
                f"  - Example: {module_data['examples'][0]['import_statement'] if module_data['examples'] else 'N/A'}"
            )

        print(f"\nDetailed report saved to: {output_path}")

        # Generate fix scripts for top modules
        self._generate_fix_scripts(sorted_modules[:5])

    def _generate_fix_scripts(self, top_modules):
        """Generate targeted fix scripts for critical modules."""
        print("\n📝 Generating fix scripts for critical modules...")

        for module, info in top_modules:
            if info["broken_count"] == 0:
                continue

            script_content = f'''#!/usr/bin/env python3
"""
Fix broken imports in {module} module.
Generated by critical import analyzer.
"""

import ast
import os
from pathlib import Path

def fix_{module}_imports():
    """Fix imports specific to {module} module."""

    fixes = {{
        # Add specific fixes here based on common patterns
        'from dataclasses import': 'from dataclasses import dataclass, field',
        'from typing import': 'from typing import Dict, List, Any, Optional',
        'from pathlib import': 'from pathlib import Path',
    }}

    # Common import completions for {module}
'''

            if module == "consciousness":
                script_content += """    consciousness_fixes = {
        'from consciousness.core import': 'from consciousness.core import ConsciousnessCore',
        'from consciousness.stream import': 'from consciousness.stream import StreamProcessor',
    }
    fixes.update(consciousness_fixes)
"""
            elif module == "memory":
                script_content += """    memory_fixes = {
        'from memory.systems import': 'from memory.systems import MemorySystem',
        'from memory.fold import': 'from memory.fold import FoldEngine',
    }
    fixes.update(memory_fixes)
"""

            script_content += f"""
    root = Path('.')
    fixed_count = 0

    for py_file in root.glob('{module}/**/*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            for broken, fixed in fixes.items():
                if broken in content and fixed not in content:
                    content = content.replace(broken, fixed)

            if content != original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_count += 1
                print(f"Fixed: {{py_file}}")

        except Exception as e:
            print(f"Error fixing {{py_file}}: {{e}}")

    print(f"\\nFixed {{fixed_count}} files in {module}")

if __name__ == "__main__":
    fix_{module}_imports()
"""

            # Save fix script
            script_path = self.root_path / "scripts" / f"fix_{module}_imports.py"
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)

            print(f"  Created: fix_{module}_imports.py")

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_dirs = {
            "__pycache__",
            ".git",
            "venv",
            ".venv",
            "env",
            "build",
            "dist",
            "node_modules",
            ".pytest_cache",
        }

        return any(part in skip_dirs for part in path.parts)


def main():
    root_path = Path(".").resolve()
    analyzer = CriticalImportAnalyzer(root_path)
    analyzer.analyze()


if __name__ == "__main__":
    main()
