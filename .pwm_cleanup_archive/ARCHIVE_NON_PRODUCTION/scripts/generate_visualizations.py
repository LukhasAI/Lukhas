#!/usr/bin/env python3
"""
Generate comprehensive dependency visualizations for the codebase
"""

import ast
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Set

import community as community_louvain
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DependencyVisualizer:
    """Generate various dependency visualizations for the codebase"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.output_dir = (
            root_path / "visualizations" / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Module colors for consistency
        self.module_colors = {
            "bio": "#2ecc71",  # Green - biological systems
            "core": "#e74c3c",  # Red - core infrastructure
            "memory": "#3498db",  # Blue - memory systems
            "quantum": "#9b59b6",  # Purple - quantum systems
            "orchestration": "#f39c12",  # Orange - orchestration
            "consciousness": "#1abc9c",  # Turquoise - consciousness
            "creativity": "#e91e63",  # Pink - creativity
            "ethics": "#34495e",  # Dark gray - ethics
            "identity": "#16a085",  # Dark turquoise - identity
            "learning": "#f1c40f",  # Yellow - learning
            "bridge": "#795548",  # Brown - bridge systems
            "reasoning": "#607d8b",  # Blue gray - reasoning
            "emotion": "#ff5722",  # Deep orange - emotion
            "features": "#8bc34a",  # Light green - features
            "interfaces": "#00bcd4",  # Cyan - interfaces
            "dashboard": "#673ab7",  # Deep purple - dashboard
            "symbolic": "#ff9800",  # Amber - symbolic
        }

    def generate_all_visualizations(self):
        """Generate all visualization types"""
        logger.info(f"Generating visualizations in {self.output_dir}")

        # Load dependency data
        dependency_graph = self._build_dependency_graph()

        if dependency_graph.number_of_nodes() == 0:
            logger.warning("No dependencies found to visualize")
            return

        # Generate various visualizations
        self._generate_full_dependency_graph(dependency_graph)
        self._generate_module_hierarchy(dependency_graph)
        self._generate_circular_dependencies(dependency_graph)
        self._generate_community_structure(dependency_graph)
        self._generate_complexity_heatmap(dependency_graph)
        self._generate_module_coupling_matrix(dependency_graph)
        self._generate_layered_architecture(dependency_graph)

        # Generate HTML index
        self._generate_index_html()

        logger.info(f"✓ Visualizations complete! View them in {self.output_dir}")

    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build dependency graph from Python files"""
        graph = nx.DiGraph()

        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_path(py_file):
                continue

            module_name = self._path_to_module(py_file)
            imports = self._extract_imports(py_file)

            # Add node with metadata
            graph.add_node(
                module_name,
                file_path=str(py_file),
                size=py_file.stat().st_size,
                module_type=self._get_module_type(py_file),
            )

            # Add edges for imports
            for imported in imports:
                if imported.startswith("."):
                    # Relative import
                    base = ".".join(module_name.split(".")[:-1])
                    if imported == ".":
                        imported = base
                    else:
                        imported = base + imported

                graph.add_edge(module_name, imported)

        return graph

    def _extract_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from a Python file"""
        imports = set()

        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)

        except Exception as e:
            logger.debug(f"Error parsing {file_path}: {e}")

        return imports

    def _generate_full_dependency_graph(self, graph: nx.DiGraph):
        """Generate full dependency graph visualization"""
        plt.figure(figsize=(24, 18))

        # Filter to only internal modules
        internal_nodes = [
            n
            for n in graph.nodes()
            if any(n.startswith(m) for m in self.module_colors.keys())
        ]
        subgraph = graph.subgraph(internal_nodes)

        # Use spring layout for better visualization
        pos = nx.spring_layout(subgraph, k=3, iterations=50)

        # Draw nodes colored by module
        for module_prefix, color in self.module_colors.items():
            nodes = [n for n in subgraph.nodes() if n.startswith(module_prefix)]
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=nodes,
                node_color=color,
                node_size=100,
                alpha=0.8,
            )

        # Draw edges with transparency
        nx.draw_networkx_edges(
            subgraph, pos, alpha=0.2, arrows=True, arrowsize=10, edge_color="gray"
        )

        # Add legend
        patches = [
            mpatches.Patch(color=color, label=module)
            for module, color in self.module_colors.items()
        ]
        plt.legend(handles=patches, loc="upper left", bbox_to_anchor=(1, 1))

        plt.title("Full Dependency Graph", fontsize=20)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "full_dependency_graph.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_module_hierarchy(self, graph: nx.DiGraph):
        """Generate module hierarchy visualization"""
        plt.figure(figsize=(20, 16))

        # Create hierarchy
        hierarchy = nx.DiGraph()

        for node in graph.nodes():
            parts = node.split(".")
            for i in range(len(parts)):
                parent = ".".join(parts[:i]) if i > 0 else "root"
                child = ".".join(parts[: i + 1])
                hierarchy.add_edge(parent, child)

        # Use hierarchical layout
        pos = self._hierarchical_layout(hierarchy, "root")

        # Draw nodes
        for node in hierarchy.nodes():
            if node == "root":
                continue

            depth = len(node.split("."))
            color = self._get_node_color(node)
            size = 300 / depth  # Smaller nodes for deeper levels

            nx.draw_networkx_nodes(
                hierarchy,
                pos,
                nodelist=[node],
                node_color=color,
                node_size=size,
                alpha=0.8,
            )

        # Draw edges
        nx.draw_networkx_edges(hierarchy, pos, alpha=0.3, edge_color="gray")

        # Add labels for top-level modules
        top_level = [n for n in hierarchy.nodes() if n != "root" and "." not in n]
        labels = {n: n for n in top_level}
        nx.draw_networkx_labels(hierarchy, pos, labels, font_size=10)

        plt.title("Module Hierarchy", fontsize=20)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "module_hierarchy.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_circular_dependencies(self, graph: nx.DiGraph):
        """Visualize circular dependencies"""
        plt.figure(figsize=(16, 12))

        # Find all cycles
        cycles = list(nx.simple_cycles(graph))

        if not cycles:
            plt.text(
                0.5,
                0.5,
                "No circular dependencies found!",
                ha="center",
                va="center",
                fontsize=20,
                color="green",
            )
        else:
            # Create subgraph with only nodes involved in cycles
            cycle_nodes = set()
            for cycle in cycles:
                cycle_nodes.update(cycle)

            cycle_graph = graph.subgraph(cycle_nodes)

            # Use circular layout
            pos = nx.circular_layout(cycle_graph)

            # Draw nodes
            for node in cycle_graph.nodes():
                color = self._get_node_color(node)
                nx.draw_networkx_nodes(
                    cycle_graph,
                    pos,
                    nodelist=[node],
                    node_color=color,
                    node_size=300,
                    alpha=0.8,
                )

            # Draw edges, highlighting cycles
            all_edges = list(cycle_graph.edges())
            cycle_edges = []
            for cycle in cycles:
                for i in range(len(cycle)):
                    edge = (cycle[i], cycle[(i + 1) % len(cycle)])
                    if edge in all_edges:
                        cycle_edges.append(edge)

            # Draw regular edges
            regular_edges = [e for e in all_edges if e not in cycle_edges]
            nx.draw_networkx_edges(
                cycle_graph, pos, edgelist=regular_edges, alpha=0.3, edge_color="gray"
            )

            # Draw cycle edges in red
            nx.draw_networkx_edges(
                cycle_graph,
                pos,
                edgelist=cycle_edges,
                alpha=0.8,
                edge_color="red",
                width=2,
            )

            # Add labels
            labels = {n: n.split(".")[-1] for n in cycle_graph.nodes()}
            nx.draw_networkx_labels(cycle_graph, pos, labels, font_size=8)

        plt.title(f"Circular Dependencies ({len(cycles)} cycles found)", fontsize=20)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "circular_dependencies.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_community_structure(self, graph: nx.DiGraph):
        """Generate community detection visualization"""
        plt.figure(figsize=(20, 16))

        # Convert to undirected for community detection
        undirected = graph.to_undirected()

        # Filter to internal modules only
        internal_nodes = [
            n
            for n in undirected.nodes()
            if any(n.startswith(m) for m in self.module_colors.keys())
        ]
        subgraph = undirected.subgraph(internal_nodes)

        # Detect communities
        partition = community_louvain.best_partition(subgraph)

        # Use spring layout
        pos = nx.spring_layout(subgraph, k=2, iterations=50)

        # Draw nodes colored by community
        cmap = plt.cm.tab20
        for com in set(partition.values()):
            nodes = [n for n in partition.keys() if partition[n] == com]
            nx.draw_networkx_nodes(
                subgraph,
                pos,
                nodelist=nodes,
                node_color=[cmap(com % 20)] * len(nodes),
                node_size=100,
                alpha=0.8,
            )

        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, alpha=0.1, edge_color="gray")

        # Add community labels
        com_centers = {}
        for node, com in partition.items():
            if com not in com_centers:
                com_centers[com] = []
            com_centers[com].append(pos[node])

        # Calculate center of each community
        for com, positions in com_centers.items():
            center = np.mean(positions, axis=0)
            plt.text(
                center[0],
                center[1],
                f"C{com}",
                fontsize=16,
                ha="center",
                va="center",
                bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
            )

        plt.title("Community Structure (Louvain Algorithm)", fontsize=20)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "community_structure.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_complexity_heatmap(self, graph: nx.DiGraph):
        """Generate complexity heatmap based on connections"""
        # Get top-level modules
        modules = list(self.module_colors.keys())

        # Calculate complexity matrix
        matrix = np.zeros((len(modules), len(modules)))

        for i, mod1 in enumerate(modules):
            for j, mod2 in enumerate(modules):
                # Count connections between modules
                connections = 0
                for node1 in graph.nodes():
                    if node1.startswith(mod1):
                        for node2 in graph.successors(node1):
                            if node2.startswith(mod2):
                                connections += 1
                matrix[i, j] = connections

        # Create heatmap
        plt.figure(figsize=(12, 10))
        im = plt.imshow(matrix, cmap="YlOrRd", aspect="auto")

        # Set ticks and labels
        plt.xticks(range(len(modules)), modules, rotation=45, ha="right")
        plt.yticks(range(len(modules)), modules)

        # Add colorbar
        plt.colorbar(im, label="Number of Dependencies")

        # Add values to cells
        for i in range(len(modules)):
            for j in range(len(modules)):
                text = plt.text(
                    j,
                    i,
                    int(matrix[i, j]),
                    ha="center",
                    va="center",
                    color="white" if matrix[i, j] > matrix.max() / 2 else "black",
                )

        plt.title("Module Dependency Heatmap", fontsize=16)
        plt.xlabel("Target Module")
        plt.ylabel("Source Module")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "complexity_heatmap.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_module_coupling_matrix(self, graph: nx.DiGraph):
        """Generate module coupling visualization"""
        # Calculate coupling metrics
        modules = list(self.module_colors.keys())
        coupling_data = []

        for module in modules:
            module_nodes = [n for n in graph.nodes() if n.startswith(module)]

            if not module_nodes:
                continue

            # Calculate metrics
            internal_edges = 0
            external_edges = 0

            for node in module_nodes:
                for target in graph.successors(node):
                    if target.startswith(module):
                        internal_edges += 1
                    else:
                        external_edges += 1

            total_edges = internal_edges + external_edges
            cohesion = internal_edges / total_edges if total_edges > 0 else 0
            coupling = external_edges / total_edges if total_edges > 0 else 0

            coupling_data.append(
                {
                    "module": module,
                    "nodes": len(module_nodes),
                    "cohesion": cohesion,
                    "coupling": coupling,
                    "internal_edges": internal_edges,
                    "external_edges": external_edges,
                }
            )

        # Create bar chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        modules = [d["module"] for d in coupling_data]
        cohesion = [d["cohesion"] for d in coupling_data]
        coupling = [d["coupling"] for d in coupling_data]

        # Cohesion chart
        bars1 = ax1.bar(modules, cohesion, color="green", alpha=0.7)
        ax1.set_ylabel("Cohesion Score")
        ax1.set_title("Module Cohesion (Internal Dependencies)")
        ax1.set_ylim(0, 1)

        # Coupling chart
        bars2 = ax2.bar(modules, coupling, color="red", alpha=0.7)
        ax2.set_ylabel("Coupling Score")
        ax2.set_title("Module Coupling (External Dependencies)")
        ax2.set_ylim(0, 1)
        ax2.set_xticks(range(len(modules)))
        ax2.set_xticklabels(modules, rotation=45, ha="right")

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "module_coupling_analysis.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def _generate_layered_architecture(self, graph: nx.DiGraph):
        """Generate layered architecture view"""
        plt.figure(figsize=(16, 20))

        # Define architectural layers
        layers = {
            "interfaces": ["interfaces", "dashboard", "bridge"],
            "application": ["orchestration", "reasoning", "creativity"],
            "domain": ["consciousness", "emotion", "learning", "ethics"],
            "infrastructure": ["core", "memory", "identity"],
            "foundation": ["bio", "quantum", "symbolic"],
        }

        # Create layered graph
        layer_graph = nx.DiGraph()
        node_layers = {}

        for layer_name, modules in layers.items():
            for module in modules:
                module_nodes = [n for n in graph.nodes() if n.split(".")[0] == module]
                for node in module_nodes:
                    layer_graph.add_node(node)
                    node_layers[node] = layer_name

        # Add edges from original graph
        for edge in graph.edges():
            if edge[0] in layer_graph and edge[1] in layer_graph:
                layer_graph.add_edge(edge[0], edge[1])

        # Calculate positions
        pos = {}
        layer_y = {
            "interfaces": 4,
            "application": 3,
            "domain": 2,
            "infrastructure": 1,
            "foundation": 0,
        }

        for layer_name, y in layer_y.items():
            nodes_in_layer = [n for n, l in node_layers.items() if l == layer_name]
            for i, node in enumerate(nodes_in_layer):
                x = i * 0.5 - len(nodes_in_layer) * 0.25
                pos[node] = (x, y)

        # Draw nodes by layer
        for layer_name, y in layer_y.items():
            nodes = [n for n, l in node_layers.items() if l == layer_name]
            colors = [self._get_node_color(n) for n in nodes]
            nx.draw_networkx_nodes(
                layer_graph,
                pos,
                nodelist=nodes,
                node_color=colors,
                node_size=50,
                alpha=0.8,
            )

        # Draw edges
        nx.draw_networkx_edges(
            layer_graph, pos, alpha=0.1, edge_color="gray", arrows=True
        )

        # Add layer labels
        for layer_name, y in layer_y.items():
            plt.text(
                -10,
                y,
                layer_name.upper(),
                fontsize=14,
                ha="right",
                va="center",
                weight="bold",
            )

        # Add layer boundaries
        for y in layer_y.values():
            plt.axhline(y - 0.5, color="lightgray", linestyle="--", alpha=0.5)

        plt.title("Layered Architecture View", fontsize=20)
        plt.axis("off")
        plt.xlim(-12, 12)
        plt.ylim(-1, 5)
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "layered_architecture.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def _generate_index_html(self):
        """Generate HTML index for all visualizations"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Codebase Dependency Visualizations</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .visualization {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .visualization h2 {{
            color: #555;
            margin-top: 0;
        }}
        .visualization img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            border: 1px solid #ddd;
        }}
        .description {{
            color: #666;
            margin: 10px 0;
        }}
        .metrics {{
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .timestamp {{
            text-align: center;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <h1>Codebase Dependency Visualizations</h1>
    <p class="timestamp">Generated: {timestamp}</p>

    <div class="visualization">
        <h2>Full Dependency Graph</h2>
        <p class="description">
            Complete view of all module dependencies in the codebase.
            Nodes are colored by their top-level module.
        </p>
        <img src="full_dependency_graph.png" alt="Full Dependency Graph">
    </div>

    <div class="visualization">
        <h2>Module Hierarchy</h2>
        <p class="description">
            Hierarchical view of the module structure, showing the organization
            of packages and submodules.
        </p>
        <img src="module_hierarchy.png" alt="Module Hierarchy">
    </div>

    <div class="visualization">
        <h2>Circular Dependencies</h2>
        <p class="description">
            Visualization of circular dependencies in the codebase.
            Red edges indicate dependency cycles that should be resolved.
        </p>
        <img src="circular_dependencies.png" alt="Circular Dependencies">
    </div>

    <div class="visualization">
        <h2>Community Structure</h2>
        <p class="description">
            Modules grouped by their natural communities using the Louvain algorithm.
            Modules in the same community tend to have strong interconnections.
        </p>
        <img src="community_structure.png" alt="Community Structure">
    </div>

    <div class="visualization">
        <h2>Module Dependency Heatmap</h2>
        <p class="description">
            Heatmap showing the intensity of dependencies between top-level modules.
            Darker colors indicate more dependencies.
        </p>
        <img src="complexity_heatmap.png" alt="Dependency Heatmap">
    </div>

    <div class="visualization">
        <h2>Module Coupling Analysis</h2>
        <p class="description">
            Analysis of module cohesion (internal dependencies) and coupling
            (external dependencies). High cohesion and low coupling indicate good design.
        </p>
        <img src="module_coupling_analysis.png" alt="Module Coupling">
    </div>

    <div class="visualization">
        <h2>Layered Architecture</h2>
        <p class="description">
            Architectural view showing modules organized into logical layers.
            Dependencies should generally flow downward through the layers.
        </p>
        <img src="layered_architecture.png" alt="Layered Architecture">
    </div>
</body>
</html>"""

        with open(self.output_dir / "index.html", "w") as f:
            f.write(html_content)

    def _path_to_module(self, path: Path) -> str:
        """Convert file path to module name"""
        try:
            relative = path.relative_to(self.root_path)
            parts = list(relative.parts[:-1]) + [relative.stem]
            return ".".join(parts)
        except ValueError:
            return path.stem

    def _get_module_type(self, path: Path) -> str:
        """Get the top-level module type"""
        try:
            relative = path.relative_to(self.root_path)
            return relative.parts[0] if relative.parts else "unknown"
        except ValueError:
            return "unknown"

    def _get_node_color(self, node: str) -> str:
        """Get color for a node based on its module"""
        for module, color in self.module_colors.items():
            if node.startswith(module):
                return color
        return "#cccccc"  # Default gray

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_dirs = {
            "__pycache__",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".git",
            "build",
            "dist",
            ".eggs",
            ".pytest_cache",
            ".mypy_cache",
            "visualizations",
            "analysis_output",
        }

        return any(part in skip_dirs for part in path.parts)

    def _hierarchical_layout(self, G, root):
        """Create hierarchical layout for tree"""
        pos = {}

        def _hierarchy_pos(
            G,
            root,
            width=1.0,
            vert_gap=0.2,
            vert_loc=0,
            xcenter=0.5,
            pos=None,
            parent=None,
            parsed=[],
        ):
            if pos is None:
                pos = {root: (xcenter, vert_loc)}
            else:
                pos[root] = (xcenter, vert_loc)

            children = list(G.neighbors(root))
            if parent is not None and parent in children:
                children.remove(parent)

            if len(children) != 0:
                dx = width / len(children)
                nextx = xcenter - width / 2 - dx / 2
                for child in children:
                    nextx += dx
                    pos = _hierarchy_pos(
                        G,
                        child,
                        width=dx,
                        vert_gap=vert_gap,
                        vert_loc=vert_loc - vert_gap,
                        xcenter=nextx,
                        pos=pos,
                        parent=root,
                        parsed=parsed,
                    )
            return pos

        return _hierarchy_pos(G, root)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate dependency visualizations for the codebase"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args()

    root_path = Path(args.path).resolve()
    if not root_path.exists():
        logger.error(f"Path does not exist: {root_path}")
        sys.exit(1)

    visualizer = DependencyVisualizer(root_path)
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
