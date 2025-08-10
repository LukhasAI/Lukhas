#!/usr/bin/env python3
"""
Module Connectivity Visualizer for LUKHAS Codebase
Shows import relationships and module dependencies after consolidation.
"""

import ast
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx


class ConnectivityVisualizer:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.module_graph = nx.DiGraph()
        self.module_imports = defaultdict(set)
        self.module_sizes = {}
        self.module_categories = {}

        # Define module categories and colors
        self.category_colors = {
            "consciousness": "#FF6B6B",  # Red
            "memory": "#4ECDC4",  # Teal
            "orchestration": "#45B7D1",  # Blue
            "api": "#96CEB4",  # Green
            "core": "#FECA57",  # Yellow
            "bio": "#9C88FF",  # Purple
            "symbolic": "#FD79A8",  # Pink
            "features": "#A29BFE",  # Light Purple
            "creativity": "#74B9FF",  # Light Blue
            "identity": "#FF4757",  # Bright Red (Safety Layer!)
            "dream": "#C44569",  # Deep Pink (Important!)
            "dreams": "#C44569",  # Deep Pink
            "colony": "#F8B500",  # Orange
            "swarm": "#F97F51",  # Coral
            "event_bus": "#25CCF7",  # Bright Blue
            "quantum": "#8B78E6",  # Deep Purple
            "emotion": "#EE5A6F",  # Rose
            "ethics": "#00D2D3",  # Turquoise
            "reasoning": "#55A3FF",  # Sky Blue
            "learning": "#05C46B",  # Emerald
            "voice": "#FFC048",  # Amber
            "bridge": "#FDA7DF",  # Lavender
            "dashboard": "#12CBC4",  # Teal Green
            "tools": "#81ECEC",  # Cyan
            "tests": "#DFE6E9",  # Gray
            "benchmarks": "#B2BEC3",  # Dark Gray
            "scripts": "#636E72",  # Darker Gray
        }

    def analyze_codebase(self):
        """Analyze the entire codebase for module dependencies."""
        print("🔍 Analyzing module connectivity...")

        py_files = list(self.root_path.rglob("*.py"))
        total_files = len(py_files)

        for i, py_file in enumerate(py_files):
            if i % 100 == 0:
                print(f"  Processing file {i}/{total_files}...")

            if self._should_skip(py_file):
                continue

            self._analyze_file(py_file)

        print(f"✅ Analyzed {total_files} Python files")

    def _analyze_file(self, file_path: Path):
        """Analyze a single file for imports and connections."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Get module name
            module_path = file_path.relative_to(self.root_path)
            module_name = self._get_module_name(module_path)

            # Track file size
            self.module_sizes[module_name] = self.module_sizes.get(
                module_name, 0
            ) + len(content)

            # Categorize module
            category = module_path.parts[0] if module_path.parts else "root"
            self.module_categories[module_name] = category

            # Parse imports
            try:
                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for imported_module in imports:
                    if self._is_internal_import(imported_module):
                        self.module_imports[module_name].add(imported_module)
                        self.module_graph.add_edge(module_name, imported_module)

            except SyntaxError:
                pass  # Skip files with syntax errors

        except Exception:
            pass  # Skip problematic files

    def _extract_imports(self, tree: ast.AST) -> set:
        """Extract all imports from an AST."""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        return imports

    def _is_internal_import(self, module_name: str) -> bool:
        """Check if an import is internal to the project."""
        internal_modules = {
            "consciousness",
            "memory",
            "orchestration",
            "api",
            "core",
            "bio",
            "symbolic",
            "features",
            "creativity",
            "tools",
            "tests",
            "benchmarks",
            "scripts",
            "trace",
            "integration",
            "identity",
            "dream",
            "dreams",
            "colony",
            "swarm",
            "event_bus",
            "baggage",
            "quantum",
            "emotion",
            "ethics",
            "reasoning",
            "learning",
            "voice",
            "bridge",
            "dashboard",
        }

        return module_name in internal_modules

    def _get_module_name(self, module_path: Path) -> str:
        """Get module name from path."""
        parts = module_path.parts
        if parts:
            return parts[0]
        return "root"

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = {"__pycache__", ".git", "venv", ".venv", "build", "dist"}
        return any(pattern in str(path) for pattern in skip_patterns)

    def generate_report(self):
        """Generate connectivity report."""
        print("\n📊 Generating connectivity report...")

        # Calculate metrics
        total_modules = len(self.module_imports)
        total_connections = sum(
            len(imports) for imports in self.module_imports.values()
        )

        # Find most connected modules
        in_degree = dict(self.module_graph.in_degree())
        out_degree = dict(self.module_graph.out_degree())

        most_imported = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:10]
        most_importing = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        # Find circular dependencies
        try:
            cycles = list(nx.simple_cycles(self.module_graph))
            circular_deps = [cycle for cycle in cycles if len(cycle) > 1]
        except:
            circular_deps = []

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_modules": total_modules,
                "total_connections": total_connections,
                "average_imports_per_module": total_connections / max(1, total_modules),
                "circular_dependencies": len(circular_deps),
            },
            "most_imported_modules": most_imported,
            "most_importing_modules": most_importing,
            "circular_dependencies": circular_deps[:10],  # Top 10
            "module_categories": Counter(self.module_categories.values()),
        }

        # Save report
        report_path = self.root_path / "scripts" / "connectivity_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        print("\n🌐 CONNECTIVITY SUMMARY")
        print(f"{'='*50}")
        print(f"Total modules: {total_modules}")
        print(f"Total connections: {total_connections}")
        print(
            f"Average imports per module: {report['summary']['average_imports_per_module']:.2f}"
        )
        print(f"Circular dependencies: {len(circular_deps)}")

        print("\n🎯 Most imported modules:")
        for module, count in most_imported[:5]:
            print(f"  - {module}: {count} imports")

        print("\n📦 Most importing modules:")
        for module, count in most_importing[:5]:
            print(f"  - {module}: {count} imports")

        if circular_deps:
            print("\n⚠️  Circular dependencies found:")
            for cycle in circular_deps[:3]:
                print(f"  - {' -> '.join(cycle)} -> {cycle[0]}")

    def visualize_graph(self):
        """Create visual representation of module connectivity."""
        print("\n🎨 Creating connectivity visualization...")

        # Create figure
        plt.figure(figsize=(20, 16))

        # Filter to major modules only
        major_modules = [
            node
            for node in self.module_graph.nodes()
            if self.module_graph.degree(node) > 2
        ]

        subgraph = self.module_graph.subgraph(major_modules)

        # Layout
        pos = nx.spring_layout(subgraph, k=3, iterations=50)

        # Draw nodes
        for category, color in self.category_colors.items():
            nodes = [
                n for n in subgraph.nodes() if self.module_categories.get(n) == category
            ]
            if nodes:
                sizes = [min(self.module_graph.degree(n) * 100, 3000) for n in nodes]
                nx.draw_networkx_nodes(
                    subgraph,
                    pos,
                    nodelist=nodes,
                    node_color=color,
                    node_size=sizes,
                    alpha=0.8,
                    label=category,
                )

        # Draw edges with varying thickness
        edge_weights = []
        for u, v in subgraph.edges():
            weight = 1 + len([e for e in self.module_graph.edges() if e == (u, v)])
            edge_weights.append(weight)

        nx.draw_networkx_edges(
            subgraph,
            pos,
            width=edge_weights,
            alpha=0.3,
            edge_color="gray",
            arrows=True,
            arrowsize=10,
        )

        # Draw labels for highly connected nodes
        important_nodes = {
            n: n for n in subgraph.nodes() if self.module_graph.degree(n) > 5
        }
        nx.draw_networkx_labels(subgraph, pos, important_nodes, font_size=10)

        # Add legend
        patches = [
            mpatches.Patch(color=color, label=category)
            for category, color in self.category_colors.items()
            if any(self.module_categories.get(n) == category for n in subgraph.nodes())
        ]
        plt.legend(handles=patches, loc="upper left", bbox_to_anchor=(1, 1))

        plt.title(
            "LUKHAS Module Connectivity Graph\n(After Consolidation)", fontsize=16
        )
        plt.axis("off")
        plt.tight_layout()

        # Save visualization
        output_path = self.root_path / "visualizations" / "connectivity_graph.png"
        output_path.parent.mkdir(exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Visualization saved to: {output_path}")

        # Also create a simplified view
        self._create_simplified_view()

    def _create_simplified_view(self):
        """Create a simplified category-level view."""
        plt.figure(figsize=(12, 10))

        # Create category graph
        category_graph = nx.DiGraph()
        category_connections = defaultdict(lambda: defaultdict(int))

        for source, targets in self.module_imports.items():
            source_cat = self.module_categories.get(source, "unknown")
            for target in targets:
                target_cat = self.module_categories.get(target, "unknown")
                if source_cat != target_cat:
                    category_connections[source_cat][target_cat] += 1

        # Add edges with weights
        for source, targets in category_connections.items():
            for target, weight in targets.items():
                category_graph.add_edge(source, target, weight=weight)

        # Layout
        pos = nx.circular_layout(category_graph)

        # Draw nodes
        node_sizes = [
            len([m for m in self.module_categories.values() if m == cat]) * 200
            for cat in category_graph.nodes()
        ]
        node_colors = [
            self.category_colors.get(cat, "#95A5A6") for cat in category_graph.nodes()
        ]

        nx.draw_networkx_nodes(
            category_graph, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8
        )

        # Draw edges with weights
        edges = category_graph.edges()
        weights = [category_graph[u][v]["weight"] for u, v in edges]
        nx.draw_networkx_edges(
            category_graph,
            pos,
            width=[w / 10 for w in weights],
            alpha=0.5,
            edge_color="gray",
            arrows=True,
            arrowsize=20,
            connectionstyle="arc3,rad=0.1",
        )

        # Draw labels
        nx.draw_networkx_labels(category_graph, pos, font_size=12, font_weight="bold")

        # Add edge labels
        edge_labels = {
            (u, v): f"{w}"
            for (u, v), w in nx.get_edge_attributes(category_graph, "weight").items()
        }
        nx.draw_networkx_edge_labels(category_graph, pos, edge_labels, font_size=8)

        plt.title("LUKHAS Module Category Dependencies\n(Simplified View)", fontsize=16)
        plt.axis("off")
        plt.tight_layout()

        # Save
        output_path = self.root_path / "visualizations" / "connectivity_simplified.png"
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Simplified view saved to: {output_path}")


def main():
    root_path = Path(".").resolve()
    visualizer = ConnectivityVisualizer(root_path)

    # Analyze codebase
    visualizer.analyze_codebase()

    # Generate report
    visualizer.generate_report()

    # Create visualizations
    try:
        visualizer.visualize_graph()
    except Exception as e:
        print(f"⚠️  Could not create visualization: {e}")
        print("Make sure matplotlib is installed: pip install matplotlib networkx")


if __name__ == "__main__":
    main()
