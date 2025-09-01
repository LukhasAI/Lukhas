#!/usr/bin/env python3
"""
🔍  Duplicate Code Analysis
=============================
Identifies duplicate functionality across LUKHAS  modules.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DuplicateAnalyzer:
    """Analyzes code for duplicate functionality"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.function_signatures: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.class_signatures: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.similar_functions: list[dict] = []
        self.duplicate_imports: dict[str, list[str]] = defaultdict(list)
        self.common_patterns: dict[str, list[str]] = defaultdict(list)

    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file for duplicates"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            rel_path = str(file_path.relative_to(self.root_path))

            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self._get_function_signature(node)
                    self.function_signatures[sig].append((rel_path, node.name))

                    # Check for common patterns
                    self._check_common_patterns(node, rel_path)

                elif isinstance(node, ast.ClassDef):
                    sig = self._get_class_signature(node)
                    self.class_signatures[sig].append((rel_path, node.name))

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    self._analyze_imports(node, rel_path)

        except Exception:
            pass  # Skip files with syntax errors

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Generate a signature for function comparison"""
        # Get parameter names (not default values)
        params = []
        for arg in node.args.args:
            params.append(arg.arg)

        # Get return type if specified
        returns = ast.unparse(node.returns) if node.returns else "None"

        # Create signature
        sig_parts = [
            f"def {node.name}",
            f"params:{','.join(params)}",
            f"returns:{returns}",
            f"decorators:{len(node.decorator_list)}",
        ]

        return "|".join(sig_parts)

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Generate a signature for class comparison"""
        # Get base classes
        bases = [ast.unparse(base) for base in node.bases]

        # Get method names
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)

        sig_parts = [
            f"class {node.name}",
            f"bases:{','.join(bases)}",
            f"methods:{','.join(sorted(methods))}",
        ]

        return "|".join(sig_parts)

    def _check_common_patterns(self, node: ast.FunctionDef, file_path: str) -> None:
        """Check for common code patterns"""
        # Pattern 1: Logger initialization
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "logger" for target in n.targets
            ):
                self.common_patterns["logger_init"].append(f"{file_path}::{node.name}")

        # Pattern 2: Configuration loading
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if hasattr(n.func, "id") and "config" in n.func.id.lower():
                    self.common_patterns["config_loading"].append(f"{file_path}::{node.name}")

        # Pattern 3: Error handling patterns
        try_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.Try))
        if try_count > 2:
            self.common_patterns["heavy_error_handling"].append(f"{file_path}::{node.name}")

    def _analyze_imports(self, node, file_path: str) -> None:
        """Track import patterns"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self.duplicate_imports[alias.name].append(file_path)
        elif isinstance(node, ast.ImportFrom) and node.module:
            self.duplicate_imports[node.module].append(file_path)

    def find_duplicates(self) -> dict:
        """Find all types of duplicates"""
        duplicates = {
            "duplicate_functions": [],
            "similar_classes": [],
            "common_imports": [],
            "repeated_patterns": dict(self.common_patterns),
            "consolidation_opportunities": [],
        }

        # Find duplicate functions
        for sig, locations in self.function_signatures.items():
            if len(locations) > 1:
                duplicates["duplicate_functions"].append(
                    {"signature": sig, "locations": locations, "count": len(locations)}
                )

        # Find similar classes
        for sig, locations in self.class_signatures.items():
            if len(locations) > 1:
                duplicates["similar_classes"].append(
                    {"signature": sig, "locations": locations, "count": len(locations)}
                )

        # Find common imports
        for module, files in self.duplicate_imports.items():
            if len(files) > 10:  # Used in many files:
                duplicates["common_imports"].append(
                    {
                        "module": module,
                        "used_in": len(files),
                        "files": files[:5],  # Sample
                    }
                )

        # Identify consolidation opportunities
        duplicates["consolidation_opportunities"] = self._identify_consolidation_opportunities()

        return duplicates

    def _identify_consolidation_opportunities(self) -> list[dict]:
        """Identify specific consolidation opportunities"""
        opportunities = []

        # 1. Logger initialization
        if len(self.common_patterns["logger_init"]) > 5:
            opportunities.append(
                {
                    "type": "logger_initialization",
                    "description": "Create common logger factory",
                    "affected_files": len({f.split("::")[0] for f in self.common_patterns["logger_init"]}),
                    "priority": "high",
                }
            )

        # 2. Config loading
        if len(self.common_patterns["config_loading"]) > 3:
            opportunities.append(
                {
                    "type": "configuration_management",
                    "description": "Create centralized config loader",
                    "affected_files": len({f.split("::")[0] for f in self.common_patterns["config_loading"]}),
                    "priority": "high",
                }
            )

        # 3. Guardian client initialization
        guardian_imports = list(self.duplicate_imports.get("governance", []))
        if len(guardian_imports) > 5:
            opportunities.append(
                {
                    "type": "guardian_client",
                    "description": "Create singleton Guardian client",
                    "affected_files": len(guardian_imports),
                    "priority": "medium",
                }
            )

        # 4. GLYPH token handling
        glyph_functions = [f for f in self.function_signatures if "glyph" in f.lower()]
        if len(glyph_functions) > 10:
            opportunities.append(
                {
                    "type": "glyph_utilities",
                    "description": "Consolidate GLYPH token utilities",
                    "affected_functions": len(glyph_functions),
                    "priority": "high",
                }
            )

        return opportunities

    def analyze_directory(self, directory: Path) -> None:
        """Analyze all Python files in directory"""
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "venv",
            ".venv",
            "archive",
            "._cleanup_archive",
        }

        for py_file in directory.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue

            self.analyze_file(py_file)


def generate_consolidation_plan(duplicates: dict) -> list[dict]:
    """Generate a concrete consolidation plan"""
    plan = []

    # 1. Create common utilities module
    if duplicates["consolidation_opportunities"]:
        plan.append(
            {
                "action": "create_common_utilities",
                "description": "Create core/common/utils.py with shared utilities",
                "includes": [
                    "Logger factory",
                    "Config loader",
                    "Error handlers",
                    "Retry decorators",
                ],
            }
        )

    # 2. Consolidate duplicate functions
    if duplicates["duplicate_functions"]:
        # Group by functionality
        func_groups = defaultdict(list)
        for dup in duplicates["duplicate_functions"]:
            func_name = dup["locations"][0][1]
            func_groups[func_name].append(dup)

        plan.append(
            {
                "action": "consolidate_functions",
                "description": "Move duplicate functions to appropriate shared modules",
                "targets": list(func_groups.keys())[:10],  # Top 10
            }
        )

    # 3. Create base classes
    if duplicates["similar_classes"]:
        plan.append(
            {
                "action": "create_base_classes",
                "description": "Extract common functionality into base classes",
                "candidates": [
                    "BaseModule",
                    "BaseProcessor",
                    "BaseValidator",
                    "BaseMemoryHandler",
                ],
            }
        )

    # 4. Standardize imports
    if duplicates["common_imports"]:
        plan.append(
            {
                "action": "standardize_imports",
                "description": "Create common import modules",
                "modules": [
                    "core.imports.ai_libs",
                    "core.imports.data_libs",
                    "core.imports.system_libs",
                ],
            }
        )

    return plan


def main():
    """Main analysis function"""
    print("🔍  Duplicate Code Analysis")
    print("=" * 60)

    analyzer = DuplicateAnalyzer(PROJECT_ROOT)

    # Analyze active modules
    print("\n📂 Analyzing codebase for duplicates...")
    modules = [
        "api",
        "consciousness",
        "core",
        "governance",
        "memory",
        "orchestration",
        "reasoning",
        "identity",
        "quantum",
        "bio",
        "creativity",
        "emotion",
        "bridge",
        "security",
        "vivox",
    ]

    for module in modules:
        module_path = PROJECT_ROOT / module
        if module_path.exists():
            print(f"   Analyzing {module}...")
            analyzer.analyze_directory(module_path)

    # Find duplicates
    print("\n🔎 Finding duplicates...")
    duplicates = analyzer.find_duplicates()

    # Display results
    print("\n📊 Duplicate Analysis Results:")
    print(f"   Duplicate functions: {len(duplicates['duplicate_functions'])}")
    print(f"   Similar classes: {len(duplicates['similar_classes'])}")
    print(f"   Common imports: {len(duplicates['common_imports'])}")
    print(f"   Repeated patterns: {sum(len(v) for v in duplicates['repeated_patterns'].values())}")

    # Show top duplicates
    if duplicates["duplicate_functions"]:
        print("\n🔄 Top Duplicate Functions:")
        for dup in duplicates["duplicate_functions"][:5]:
            func_name = dup["locations"][0][1]
            print(f"   • {func_name} - found in {dup['count']} files")
            for file, _name in dup["locations"][:3]:
                print(f"      - {file}")

    # Show consolidation opportunities
    if duplicates["consolidation_opportunities"]:
        print("\n💡 Consolidation Opportunities:")
        for opp in duplicates["consolidation_opportunities"]:
            print(f"   • {opp['type']}: {opp['description']}")
            print(f"     Priority: {opp['priority']}, Affected: {opp.get('affected_files', 'N/A')} files")

    # Generate consolidation plan
    plan = generate_consolidation_plan(duplicates)
    print("\n📋 Consolidation Plan:")
    for i, step in enumerate(plan, 1):
        print(f"\n   Step {i}: {step['action']}")
        print(f"   {step['description']}")
        if "includes" in step:
            for item in step["includes"]:
                print(f"      - {item}")

    # Save detailed report
    report_path = PROJECT_ROOT / "docs" / "reports" / "analysis" / "_DUPLICATE_ANALYSIS_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(
            {
                "duplicates": duplicates,
                "consolidation_plan": plan,
                "summary": {
                    "total_functions_analyzed": sum(len(v) for v in analyzer.function_signatures.values()),
                    "total_classes_analyzed": sum(len(v) for v in analyzer.class_signatures.values()),
                    "duplicate_functions": len(duplicates["duplicate_functions"]),
                    "similar_classes": len(duplicates["similar_classes"]),
                    "consolidation_opportunities": len(duplicates["consolidation_opportunities"]),
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Detailed report saved to: {report_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
