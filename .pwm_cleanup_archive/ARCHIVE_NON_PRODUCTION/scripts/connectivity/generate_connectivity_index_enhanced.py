#!/usr/bin/env python3
"""
Enhanced Connectivity Index Generator
Analyzes code dependencies and generates comprehensive connectivity reports
with missed opportunities detection and architectural insights
"""

import ast
import concurrent.futures
import json
import logging
import os
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    name: str
    kind: str  # class/function/dataclass/constant/type_alias
    file_path: str
    line_number: int = 0
    used: bool = False
    used_by: Set[str] = field(default_factory=set)
    imports: Set[str] = field(default_factory=set)  # What this symbol imports
    docstring: Optional[str] = None
    complexity: int = 0  # Cyclomatic complexity for functions


@dataclass
class ModuleMetrics:
    total_symbols: int = 0
    used_symbols: int = 0
    unused_symbols: int = 0
    import_count: int = 0
    export_count: int = 0
    connectivity_score: float = 0.0
    cohesion_score: float = 0.0
    coupling_score: float = 0.0


@dataclass
class MissedOpportunity:
    type: str  # "unused_export", "circular_dependency", "god_module", "isolated_module"
    description: str
    affected_files: List[str]
    severity: str  # "low", "medium", "high"
    suggestion: str


class EnhancedConnectivityAnalyzer:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.all_definitions: Dict[str, Dict[str, SymbolInfo]] = {}
        self.all_imports: Dict[Tuple[str, str], Set[str]] = {}
        self.module_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.missed_opportunities: List[MissedOpportunity] = []

    def analyze_directory(self, target_dir: str) -> Dict[str, Any]:
        """Main entry point for analyzing a directory"""
        target_path = Path(target_dir).resolve()
        logger.info(f"Analyzing directory: {target_path}")

        # Collect all Python files
        python_files = list(target_path.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")

        # Parallel processing for better performance
        with concurrent.futures.ProcessPoolExecutor() as executor:
            # Collect definitions in parallel
            future_to_file = {
                executor.submit(self._collect_file_definitions, f): f
                for f in python_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    module_name, definitions = future.result()
                    if module_name and definitions:
                        self.all_definitions[module_name] = definitions
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

        # Collect imports (sequential due to shared state)
        self._collect_all_imports(python_files)

        # Analyze connectivity
        self._analyze_dependencies()

        # Detect missed opportunities
        self._detect_missed_opportunities()

        # Generate comprehensive report
        return self._generate_report(target_path)

    def _collect_file_definitions(
        self, file_path: Path
    ) -> Tuple[str, Dict[str, SymbolInfo]]:
        """Collect all definitions from a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            module_name = self._get_module_name(file_path)
            definitions = {}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    kind = self._get_class_kind(node)
                    info = SymbolInfo(
                        name=node.name,
                        kind=kind,
                        file_path=str(file_path.relative_to(self.repo_root)),
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                    )
                    definitions[node.name] = info

                elif isinstance(node, ast.FunctionDef):
                    info = SymbolInfo(
                        name=node.name,
                        kind="function",
                        file_path=str(file_path.relative_to(self.repo_root)),
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                        complexity=self._calculate_complexity(node),
                    )
                    definitions[node.name] = info

                elif isinstance(node, ast.AnnAssign) and isinstance(
                    node.target, ast.Name
                ):
                    # Type aliases and constants
                    info = SymbolInfo(
                        name=node.target.id,
                        kind="type_alias" if "Type" in ast.dump(node) else "constant",
                        file_path=str(file_path.relative_to(self.repo_root)),
                        line_number=node.lineno,
                    )
                    definitions[node.target.id] = info

            return module_name, definitions

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None, {}

    def _get_class_kind(self, node: ast.ClassDef) -> str:
        """Determine the kind of class (regular, dataclass, enum, etc.)"""
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        if "dataclass" in decorators:
            return "dataclass"
        elif any("enum" in d.lower() for d in decorators if d):
            return "enum"
        elif any(
            base.id == "Protocol" if isinstance(base, ast.Name) else False
            for base in node.bases
        ):
            return "protocol"
        else:
            return "class"

    def _get_decorator_name(self, decorator) -> Optional[str]:
        """Extract decorator name from AST node"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return None

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name"""
        try:
            relative = file_path.relative_to(self.repo_root)
            parts = list(relative.parts[:-1]) + [relative.stem]
            return ".".join(parts)
        except ValueError:
            return str(file_path.stem)

    def _collect_all_imports(self, python_files: List[Path]):
        """Collect all imports from Python files"""
        for file_path in python_files:
            self._collect_file_imports(file_path)

    def _collect_file_imports(self, file_path: Path):
        """Collect imports from a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=str(file_path))
            current_module = self._get_module_name(file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = self._resolve_import(node, current_module)
                    if module:
                        for alias in node.names:
                            if alias.name != "*":
                                key = (module, alias.name)
                                self.all_imports.setdefault(key, set()).add(
                                    str(file_path.relative_to(self.repo_root))
                                )
                                # Track module-level dependencies
                                self.module_dependencies[current_module].add(module)
                                self.reverse_dependencies[module].add(current_module)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.module_dependencies[current_module].add(alias.name)

        except Exception as e:
            logger.error(f"Error collecting imports from {file_path}: {e}")

    def _resolve_import(
        self, node: ast.ImportFrom, current_module: str
    ) -> Optional[str]:
        """Resolve relative imports to absolute module names"""
        if node.level == 0:
            return node.module

        # Handle relative imports
        parts = current_module.split(".")
        if node.level <= len(parts):
            base = parts[: -node.level]
            if node.module:
                return ".".join(base + [node.module])
            else:
                return ".".join(base)

        return None

    def _analyze_dependencies(self):
        """Analyze which symbols are actually used"""
        for (module, symbol), used_by in self.all_imports.items():
            if (
                module in self.all_definitions
                and symbol in self.all_definitions[module]
            ):
                self.all_definitions[module][symbol].used = True
                self.all_definitions[module][symbol].used_by = used_by

    def _detect_missed_opportunities(self):
        """Detect architectural issues and missed opportunities"""

        # 1. Detect unused exports
        for module, definitions in self.all_definitions.items():
            unused = [
                d
                for d in definitions.values()
                if not d.used and not d.name.startswith("_")
            ]
            if len(unused) > 5:  # Threshold for concern
                self.missed_opportunities.append(
                    MissedOpportunity(
                        type="unused_exports",
                        description=f"Module {module} has {len(unused)} unused public symbols",
                        affected_files=[module],
                        severity="medium" if len(unused) < 10 else "high",
                        suggestion=f"Consider making these symbols private or removing them: {', '.join(s.name for s in unused[:5])}...",
                    )
                )

        # 2. Detect circular dependencies
        visited = set()
        for module in self.module_dependencies:
            if module not in visited:
                cycle = self._find_cycle(module, [module], visited)
                if cycle:
                    self.missed_opportunities.append(
                        MissedOpportunity(
                            type="circular_dependency",
                            description=f"Circular dependency detected: {' -> '.join(cycle)}",
                            affected_files=cycle,
                            severity="high",
                            suggestion="Refactor to break the circular dependency, possibly by introducing an abstraction",
                        )
                    )

        # 3. Detect god modules (too many dependencies)
        for module, deps in self.module_dependencies.items():
            if len(deps) > 20:  # Threshold
                self.missed_opportunities.append(
                    MissedOpportunity(
                        type="god_module",
                        description=f"Module {module} has too many dependencies ({len(deps)})",
                        affected_files=[module],
                        severity="high",
                        suggestion="Consider breaking this module into smaller, more focused modules",
                    )
                )

        # 4. Detect isolated modules (no imports or exports)
        for module in self.all_definitions:
            if (
                module not in self.module_dependencies
                or not self.module_dependencies[module]
            ) and (
                module not in self.reverse_dependencies
                or not self.reverse_dependencies[module]
            ):
                self.missed_opportunities.append(
                    MissedOpportunity(
                        type="isolated_module",
                        description=f"Module {module} is isolated (no imports or exports)",
                        affected_files=[module],
                        severity="low",
                        suggestion="Consider if this module should be integrated with others or removed",
                    )
                )

    def _find_cycle(
        self, start: str, path: List[str], visited: Set[str]
    ) -> Optional[List[str]]:
        """Find circular dependencies using DFS"""
        if start in visited:
            return None

        for dep in self.module_dependencies.get(start, []):
            if dep in path:
                # Found a cycle
                cycle_start = path.index(dep)
                return path[cycle_start:] + [dep]

            cycle = self._find_cycle(dep, path + [dep], visited)
            if cycle:
                return cycle

        visited.add(start)
        return None

    def _calculate_metrics(self, module: str) -> ModuleMetrics:
        """Calculate metrics for a module"""
        metrics = ModuleMetrics()

        if module in self.all_definitions:
            definitions = self.all_definitions[module]
            metrics.total_symbols = len(definitions)
            metrics.used_symbols = sum(1 for d in definitions.values() if d.used)
            metrics.unused_symbols = metrics.total_symbols - metrics.used_symbols

        metrics.import_count = len(self.module_dependencies.get(module, []))
        metrics.export_count = len(self.reverse_dependencies.get(module, []))

        # Connectivity score: ratio of used symbols to total
        if metrics.total_symbols > 0:
            metrics.connectivity_score = metrics.used_symbols / metrics.total_symbols

        # Cohesion score: how well the module's symbols work together
        # (simplified: based on internal vs external usage)
        if metrics.total_symbols > 0:
            internal_refs = sum(
                1
                for d in definitions.values()
                if any(module in str(u) for u in d.used_by)
            )
            metrics.cohesion_score = internal_refs / metrics.total_symbols

        # Coupling score: dependency ratio
        total_modules = len(self.all_definitions)
        if total_modules > 1:
            metrics.coupling_score = metrics.import_count / (total_modules - 1)

        return metrics

    def _generate_report(self, target_path: Path) -> Dict[str, Any]:
        """Generate comprehensive connectivity report"""
        report = {
            "directory": str(target_path.relative_to(self.repo_root)),
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_modules": len(self.all_definitions),
                "total_symbols": sum(len(d) for d in self.all_definitions.values()),
                "total_dependencies": sum(
                    len(d) for d in self.module_dependencies.values()
                ),
                "missed_opportunities": len(self.missed_opportunities),
            },
            "modules": {},
            "missed_opportunities": [asdict(mo) for mo in self.missed_opportunities],
            "dependency_graph": {
                "nodes": list(self.all_definitions.keys()),
                "edges": [
                    {"from": src, "to": dst}
                    for src, dsts in self.module_dependencies.items()
                    for dst in dsts
                ],
            },
        }

        # Add detailed module information
        for module in self.all_definitions:
            metrics = self._calculate_metrics(module)
            module_info = {"metrics": asdict(metrics), "symbols": []}

            for symbol in self.all_definitions[module].values():
                symbol_dict = {
                    "name": symbol.name,
                    "kind": symbol.kind,
                    "line": symbol.line_number,
                    "used": symbol.used,
                    "used_by": sorted(symbol.used_by),
                    "complexity": (
                        symbol.complexity if symbol.kind == "function" else None
                    ),
                    "has_docstring": bool(symbol.docstring),
                }
                module_info["symbols"].append(symbol_dict)

            report["modules"][module] = module_info

        return report


def write_enhanced_reports(report: Dict[str, Any], output_dir: str):
    """Write enhanced connectivity reports"""
    output_path = Path(output_dir)

    # Write JSON report
    json_path = output_path / "CONNECTIVITY_INDEX.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write detailed Markdown report
    md_path = output_path / "CONNECTIVITY_INDEX.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Connectivity Index for {report['directory']}\n\n")
        f.write(f"Generated: {report['timestamp']}\n\n")

        # Summary section
        f.write("## Summary\n\n")
        summary = report["summary"]
        f.write(f"- **Total Modules:** {summary['total_modules']}\n")
        f.write(f"- **Total Symbols:** {summary['total_symbols']}\n")
        f.write(f"- **Total Dependencies:** {summary['total_dependencies']}\n")
        f.write(f"- **Missed Opportunities:** {summary['missed_opportunities']}\n\n")

        # Missed opportunities section
        if report["missed_opportunities"]:
            f.write("## 🔍 Missed Opportunities\n\n")
            for mo in report["missed_opportunities"]:
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    mo["severity"], "⚪"
                )
                f.write(f"### {emoji} {mo['type'].replace('_', ' ').title()}\n")
                f.write(f"**Description:** {mo['description']}\n")
                f.write(f"**Affected Files:** {', '.join(mo['affected_files'])}\n")
                f.write(f"**Suggestion:** {mo['suggestion']}\n\n")

        # Module details
        f.write("## Module Details\n\n")
        for module, info in report["modules"].items():
            metrics = info["metrics"]
            f.write(f"### {module}\n\n")
            f.write("**Metrics:**\n")
            f.write(f"- Connectivity Score: {metrics['connectivity_score']:.2%}\n")
            f.write(f"- Cohesion Score: {metrics['cohesion_score']:.2%}\n")
            f.write(f"- Coupling Score: {metrics['coupling_score']:.2%}\n")
            f.write(
                f"- Used/Total Symbols: {metrics['used_symbols']}/{metrics['total_symbols']}\n\n"
            )

            if info["symbols"]:
                f.write("**Symbols:**\n\n")
                f.write("| Name | Kind | Used | Complexity | Documented |\n")
                f.write("| --- | --- | --- | --- | --- |\n")
                for sym in info["symbols"]:
                    complexity = sym["complexity"] if sym["complexity"] else "N/A"
                    documented = "✅" if sym["has_docstring"] else "❌"
                    f.write(
                        f"| {sym['name']} | {sym['kind']} | {sym['used']} | {complexity} | {documented} |\n"
                    )
                f.write("\n")

    # Write visualization HTML (optional)
    html_path = output_path / "CONNECTIVITY_VISUALIZATION.html"
    write_visualization(report, html_path)

    logger.info(f"Reports generated at {output_path}")


def write_visualization(report: Dict[str, Any], html_path: Path):
    """Generate an interactive visualization of the connectivity graph"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Connectivity Visualization - {report['directory']}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .node {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        .tooltip {{ position: absolute; padding: 10px; background: rgba(0,0,0,0.8); color: white; border-radius: 5px; }}
        #graph {{ width: 100%; height: 600px; border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <h1>Connectivity Visualization: {report['directory']}</h1>
    <div id="graph"></div>
    <script>
        const data = {json.dumps(report['dependency_graph'])};
        // D3.js visualization code would go here
        console.log('Dependency graph data:', data);
    </script>
</body>
</html>
"""
    with open(html_path, "w") as f:
        f.write(html_content)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Connectivity Index Generator - Analyze code dependencies and architecture"
    )
    parser.add_argument("target", help="Target directory to analyze")
    parser.add_argument(
        "--repo-root",
        default=os.getcwd(),
        help="Repository root (default: current directory)",
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Enable parallel processing"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Create analyzer and run analysis
    analyzer = EnhancedConnectivityAnalyzer(args.repo_root)
    report = analyzer.analyze_directory(args.target)

    # Write reports
    write_enhanced_reports(report, args.target)

    # Print summary
    print("\n✨ Connectivity Analysis Complete!")
    print(
        f"📊 Analyzed: {report['summary']['total_modules']} modules, {report['summary']['total_symbols']} symbols"
    )
    print(
        f"🔍 Found: {report['summary']['missed_opportunities']} improvement opportunities"
    )
    print(f"📁 Reports saved to: {args.target}")


if __name__ == "__main__":
    main()
