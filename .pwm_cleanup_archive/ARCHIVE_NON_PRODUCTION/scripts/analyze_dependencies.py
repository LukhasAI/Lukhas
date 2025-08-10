#!/usr/bin/env python3
"""
Analyze module dependencies and generate dependency report.
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

try:
    import matplotlib.pyplot as plt
    import networkx as nx

    HAS_GRAPH_LIBS = True
except ImportError:
    HAS_GRAPH_LIBS = False


def extract_imports(filepath: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    imports = []

    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def categorize_import(import_name: str, internal_modules: Set[str]) -> str:
    """Categorize an import as internal, external, or standard library."""
    # Standard library modules (common ones)
    stdlib = {
        "os",
        "sys",
        "json",
        "datetime",
        "time",
        "random",
        "math",
        "collections",
        "itertools",
        "functools",
        "typing",
        "pathlib",
        "re",
        "ast",
        "logging",
        "traceback",
        "copy",
        "pickle",
        "subprocess",
        "threading",
        "asyncio",
        "unittest",
        "abc",
    }

    base_module = import_name.split(".")[0]

    if base_module in stdlib:
        return "stdlib"
    elif base_module in internal_modules:
        return "internal"
    elif import_name.startswith("."):
        return "relative"
    else:
        return "external"


def analyze_module_dependencies(base_path: Path) -> Dict[str, Dict]:
    """Analyze dependencies for all modules."""
    # Get all module directories
    modules = {
        d.name: d
        for d in base_path.iterdir()
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name not in ["scripts", "tests", "docs", "examples"]
    }

    internal_modules = set(modules.keys())
    dependency_graph = defaultdict(lambda: {"imports": set(), "imported_by": set()})
    module_stats = {}

    for module_name, module_path in modules.items():
        print(f"Analyzing {module_name}...")

        py_files = list(module_path.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]

        imports_by_category = defaultdict(set)
        file_count = len(py_files)

        for py_file in py_files:
            imports = extract_imports(py_file)

            for imp in imports:
                category = categorize_import(imp, internal_modules)
                imports_by_category[category].add(imp)

                # Track internal dependencies
                if category == "internal":
                    imported_module = imp.split(".")[0]
                    dependency_graph[module_name]["imports"].add(imported_module)
                    dependency_graph[imported_module]["imported_by"].add(module_name)

        module_stats[module_name] = {
            "file_count": file_count,
            "internal_deps": sorted(imports_by_category["internal"]),
            "external_deps": sorted(imports_by_category["external"]),
            "stdlib_deps": sorted(imports_by_category["stdlib"]),
            "relative_imports": len(imports_by_category["relative"]),
        }

    return module_stats, dict(dependency_graph)


def generate_dependency_report(module_stats: Dict, dependency_graph: Dict) -> str:
    """Generate a markdown report of module dependencies."""
    report = """# Module Dependency Analysis Report

## Summary
This report analyzes the dependencies between modules in the LUKHAS system.

## Module Statistics

| Module | Files | Internal Deps | External Deps | Stdlib Deps |
|--------|-------|---------------|---------------|-------------|
"""

    for module, stats in sorted(module_stats.items()):
        internal = len([d for d in stats["internal_deps"] if "." not in d])
        external = len(stats["external_deps"])
        stdlib = len(stats["stdlib_deps"])

        report += f"| {module} | {stats['file_count']} | {internal} | {external} | {stdlib} |\n"

    report += "\n## Dependency Graph\n\n"
    report += "### Most Connected Modules\n"

    # Calculate connectivity
    connectivity = []
    for module, deps in dependency_graph.items():
        total_connections = len(deps["imports"]) + len(deps["imported_by"])
        connectivity.append(
            (module, total_connections, len(deps["imports"]), len(deps["imported_by"]))
        )

    connectivity.sort(key=lambda x: x[1], reverse=True)

    report += "| Module | Total Connections | Imports | Imported By |\n"
    report += "|--------|------------------|---------|-------------|\n"

    for module, total, imports, imported_by in connectivity[:10]:
        report += f"| {module} | {total} | {imports} | {imported_by} |\n"

    report += "\n### Detailed Dependencies\n\n"

    for module in sorted(dependency_graph.keys()):
        deps = dependency_graph[module]
        if deps["imports"] or deps["imported_by"]:
            report += f"#### {module}\n"

            if deps["imports"]:
                report += f"- **Imports**: {', '.join(sorted(deps['imports']))}\n"

            if deps["imported_by"]:
                report += (
                    f"- **Imported by**: {', '.join(sorted(deps['imported_by']))}\n"
                )

            report += "\n"

    # Add external dependencies section
    report += "## External Dependencies\n\n"

    all_external = set()
    for stats in module_stats.values():
        all_external.update(stats["external_deps"])

    if all_external:
        report += "### All External Packages Used\n"
        for pkg in sorted(all_external):
            base_pkg = pkg.split(".")[0]
            report += f"- `{base_pkg}`\n"

    return report


def visualize_dependencies(dependency_graph: Dict, output_path: Path):
    """Create a visual graph of module dependencies."""
    if not HAS_GRAPH_LIBS:
        return

    G = nx.DiGraph()

    # Add nodes and edges
    for module, deps in dependency_graph.items():
        G.add_node(module)
        for imported in deps["imports"]:
            G.add_edge(module, imported)

    # Calculate layout
    pos = nx.spring_layout(G, k=2, iterations=50)

    # Create figure
    plt.figure(figsize=(12, 8))

    # Draw nodes
    node_sizes = [300 * (1 + G.degree(node)) for node in G.nodes()]
    nx.draw_networkx_nodes(
        G, pos, node_size=node_sizes, node_color="lightblue", alpha=0.7
    )

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color="gray", alpha=0.5, arrows=True)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Module Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze module dependencies")
    parser.add_argument("--path", type=str, default=".", help="Base path")
    parser.add_argument(
        "--output", type=str, default="dependency_report.md", help="Output report file"
    )
    parser.add_argument(
        "--graph", action="store_true", help="Generate dependency graph visualization"
    )
    args = parser.parse_args()

    base_path = Path(args.path).resolve()
    print(f"Analyzing dependencies in: {base_path}")
    print("-" * 80)

    # Analyze dependencies
    module_stats, dependency_graph = analyze_module_dependencies(base_path)

    # Generate report
    report = generate_dependency_report(module_stats, dependency_graph)

    # Save report
    output_path = base_path / args.output
    output_path.write_text(report)
    print(f"\n✅ Dependency report saved to: {output_path}")

    # Generate visualization if requested
    if args.graph:
        try:
            graph_path = base_path / "dependency_graph.png"
            visualize_dependencies(dependency_graph, graph_path)
            print(f"✅ Dependency graph saved to: {graph_path}")
        except ImportError:
            print("⚠️  matplotlib/networkx not installed, skipping graph generation")

    # Print summary
    print("\n" + "=" * 80)
    print("Summary:")
    print(f"- Analyzed {len(module_stats)} modules")
    print(
        f"- Found {sum(len(d['imports']) for d in dependency_graph.values())} dependencies"
    )

    # Find potential issues
    circular_deps = []
    for module, deps in dependency_graph.items():
        for imported in deps["imports"]:
            if module in dependency_graph.get(imported, {}).get("imports", []):
                circular_deps.append((module, imported))

    if circular_deps:
        print(f"\n⚠️  Found {len(circular_deps)} potential circular dependencies:")
        for a, b in circular_deps[:5]:
            print(f"  - {a} <-> {b}")


if __name__ == "__main__":
    main()
