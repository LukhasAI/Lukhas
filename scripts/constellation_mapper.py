#!/usr/bin/env python3
"""
LUKHAS Constellation Module Mapper
Maps relationships and dependencies between consciousness components
"""

import ast
import json
from datetime import datetime
from pathlib import Path
from typing import Dict

import networkx as nx


class ConstellationMapper:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.consciousness_dir = self.root_path / "candidate" / "consciousness"
        self.contracts_dir = self.root_path / "contracts" / "consciousness"
        self.graph = nx.DiGraph()
        self.component_map = {}

    def extract_imports_from_file(self, file_path: Path) -> set[str]:
        """Extract import dependencies from a Python file"""
        imports = set()
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)

        except Exception:
            pass

        return imports

    def analyze_consciousness_dependencies(self) -> Dict:
        """Analyze dependencies between consciousness components"""
        component_deps = {}

        if not self.consciousness_dir.exists():
            return {"error": "Consciousness directory not found"}

        py_files = list(self.consciousness_dir.rglob("*.py"))

        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue

            # Generate component ID
            rel_path = py_file.relative_to(self.root_path)
            component_id = str(rel_path).replace("/", ".").replace(".py", "")

            # Extract imports
            imports = self.extract_imports_from_file(py_file)

            # Filter for consciousness-related imports
            consciousness_imports = set()
            for imp in imports:
                if "consciousness" in imp or "lukhas" in imp or "candidate" in imp:
                    consciousness_imports.add(imp)

            component_deps[component_id] = {
                "file_path": str(py_file),
                "imports": list(imports),
                "consciousness_imports": list(consciousness_imports),
                "import_count": len(imports),
                "consciousness_import_count": len(consciousness_imports)
            }

            # Add to graph
            self.graph.add_node(component_id,
                               file_path=str(py_file),
                               import_count=len(imports))

            # Add edges for consciousness dependencies
            for dep in consciousness_imports:
                if dep != component_id:  # Avoid self-loops
                    self.graph.add_edge(component_id, dep, relationship="imports")

        return component_deps

    def identify_constellation_clusters(self) -> Dict:
        """Identify clusters/constellations of related components"""
        try:
            # Convert to undirected for clustering
            undirected_graph = self.graph.to_undirected()

            # Find connected components
            clusters = list(nx.connected_components(undirected_graph))

            cluster_analysis = {
                "total_clusters": len(clusters),
                "largest_cluster_size": max(len(c) for c in clusters) if clusters else 0,
                "clusters": []
            }

            for i, cluster in enumerate(clusters, 1):
                cluster_info = {
                    "cluster_id": f"constellation_{i}",
                    "size": len(cluster),
                    "components": list(cluster),
                    "internal_edges": 0,
                    "external_edges": 0
                }

                # Count internal vs external edges
                subgraph = self.graph.subgraph(cluster)
                cluster_info["internal_edges"] = subgraph.number_of_edges()

                for node in cluster:
                    for neighbor in self.graph.neighbors(node):
                        if neighbor not in cluster:
                            cluster_info["external_edges"] += 1

                cluster_analysis["clusters"].append(cluster_info)

            # Sort clusters by size
            cluster_analysis["clusters"].sort(key=lambda x: x["size"], reverse=True)

            return cluster_analysis

        except Exception as e:
            return {"error": f"Clustering failed: {e}"}

    def analyze_component_centrality(self) -> Dict:
        """Analyze which components are most central/important"""
        try:
            centrality_metrics = {}

            if self.graph.number_of_nodes() > 0:
                # Degree centrality
                degree_centrality = nx.degree_centrality(self.graph)

                # In-degree centrality (most depended upon)
                in_degree_centrality = nx.in_degree_centrality(self.graph)

                # Out-degree centrality (depends on most things)
                out_degree_centrality = nx.out_degree_centrality(self.graph)

                # PageRank (overall importance)
                try:
                    pagerank = nx.pagerank(self.graph)
                except Exception:
                    pagerank = {}

                # Combine metrics
                for node in self.graph.nodes():
                    centrality_metrics[node] = {
                        "degree_centrality": degree_centrality.get(node, 0),
                        "in_degree_centrality": in_degree_centrality.get(node, 0),
                        "out_degree_centrality": out_degree_centrality.get(node, 0),
                        "pagerank": pagerank.get(node, 0),
                        "total_connections": self.graph.degree(node)
                    }

            # Sort by PageRank
            sorted_components = sorted(centrality_metrics.items(),
                                     key=lambda x: x[1]["pagerank"], reverse=True)

            return {
                "total_components": len(centrality_metrics),
                "top_central_components": sorted_components[:20],
                "metrics": centrality_metrics
            }

        except Exception as e:
            return {"error": f"Centrality analysis failed: {e}"}

    def identify_architectural_patterns(self, component_deps: Dict) -> Dict:
        """Identify architectural patterns in the consciousness system"""
        patterns = {
            "engine_components": [],
            "bridge_components": [],
            "processing_components": [],
            "dream_components": [],
            "trinity_components": [],
            "high_coupling_components": [],
            "isolated_components": []
        }

        for component_id, info in component_deps.items():
            # Categorize by file path patterns
            if "engine" in component_id:
                patterns["engine_components"].append(component_id)
            elif "bridge" in component_id or "constellation" in component_id:
                patterns["bridge_components"].append(component_id)
            elif "dream" in component_id:
                patterns["dream_components"].append(component_id)
            elif any(t in component_id for t in ["cognitive", "processing", "reflection"]):
                patterns["processing_components"].append(component_id)

            # Identify Constellation Framework components
            trinity_keywords = ["identity", "guardian", "consciousness"]
            if any(keyword in " ".join(info["imports"]) for keyword in trinity_keywords):
                patterns["trinity_components"].append(component_id)

            # High coupling (many dependencies)
            if info["consciousness_import_count"] > 5:
                patterns["high_coupling_components"].append(component_id)

            # Isolated components (few dependencies)
            if info["consciousness_import_count"] == 0:
                patterns["isolated_components"].append(component_id)

        # Add counts (create new dict to avoid iteration issues)
        pattern_counts = {}
        for pattern_name, components in patterns.items():
            pattern_counts[f"{pattern_name}_count"] = len(components)

        patterns.update(pattern_counts)

        return patterns

    def generate_constellation_map(self) -> Dict:
        """Generate complete constellation map of the consciousness system"""
        results = {
            "mapping_timestamp": datetime.now().isoformat(),
            "system_overview": {},
            "component_dependencies": {},
            "constellation_clusters": {},
            "centrality_analysis": {},
            "architectural_patterns": {},
            "graph_statistics": {},
            "recommendations": []
        }

        print("Analyzing consciousness component dependencies...")
        component_deps = self.analyze_consciousness_dependencies()
        if "error" in component_deps:
            results["error"] = component_deps["error"]
            return results

        results["component_dependencies"] = component_deps

        print("Identifying constellation clusters...")
        clusters = self.identify_constellation_clusters()
        results["constellation_clusters"] = clusters

        print("Analyzing component centrality...")
        centrality = self.analyze_component_centrality()
        results["centrality_analysis"] = centrality

        print("Identifying architectural patterns...")
        patterns = self.identify_architectural_patterns(component_deps)
        results["architectural_patterns"] = patterns

        # Graph statistics
        results["graph_statistics"] = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph),
            "number_of_weakly_connected_components": nx.number_weakly_connected_components(self.graph)
        }

        # System overview
        results["system_overview"] = {
            "total_consciousness_files": len(component_deps),
            "components_with_dependencies": len([c for c in component_deps.values() if c["consciousness_import_count"] > 0]),
            "average_dependencies_per_component": sum(c["consciousness_import_count"] for c in component_deps.values()) / len(component_deps) if component_deps else 0,
            "most_connected_component": centrality.get("top_central_components", [{}])[0] if centrality.get("top_central_components") else None
        }

        # Generate recommendations
        if patterns.get("isolated_components_count", 0) > 50:
            results["recommendations"].append("High number of isolated components suggests potential for better integration")

        if results["graph_statistics"]["density"] < 0.1:
            results["recommendations"].append("Low graph density suggests loose coupling - consider architectural bridges")

        if clusters.get("total_clusters", 0) > 10:
            results["recommendations"].append("Multiple clusters detected - consider constellation-based organization")

        return results

    def export_graph_data(self, output_dir: Path) -> Dict:
        """Export graph data for visualization"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Export as GraphML for advanced visualization tools
        graphml_path = output_dir / "consciousness_constellation.graphml"
        nx.write_graphml(self.graph, graphml_path)

        # Export as JSON for web visualization
        graph_data = nx.node_link_data(self.graph)
        json_path = output_dir / "consciousness_constellation.json"
        with open(json_path, 'w') as f:
            json.dump(graph_data, f, indent=2)

        return {
            "graphml_exported": str(graphml_path),
            "json_exported": str(json_path),
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges()
        }


def main():
    mapper = ConstellationMapper(".")

    print("LUKHAS Constellation Module Mapping")
    print("=" * 50)

    results = mapper.generate_constellation_map()

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print("System Overview:")
    print(f"  Total consciousness files: {results['system_overview']['total_consciousness_files']}")
    print(f"  Components with dependencies: {results['system_overview']['components_with_dependencies']}")
    print(f"  Average dependencies per component: {results['system_overview']['average_dependencies_per_component']:.1f}")

    print("\nGraph Statistics:")
    print(f"  Nodes: {results['graph_statistics']['total_nodes']}")
    print(f"  Edges: {results['graph_statistics']['total_edges']}")
    print(f"  Density: {results['graph_statistics']['density']:.3f}")
    print(f"  Connected: {results['graph_statistics']['is_connected']}")

    print("\nConstellation Clusters:")
    if results['constellation_clusters'].get('clusters'):
        print(f"  Total clusters: {results['constellation_clusters']['total_clusters']}")
        print(f"  Largest cluster: {results['constellation_clusters']['largest_cluster_size']} components")

        top_clusters = results['constellation_clusters']['clusters'][:5]
        for i, cluster in enumerate(top_clusters, 1):
            print(f"    Cluster {i}: {cluster['size']} components")

    print("\nArchitectural Patterns:")
    patterns = results['architectural_patterns']
    for pattern_name, count in patterns.items():
        if pattern_name.endswith('_count'):
            clean_name = pattern_name.replace('_count', '').replace('_', ' ').title()
            print(f"  {clean_name}: {count}")

    if results["recommendations"]:
        print("\nRecommendations:")
        for rec in results["recommendations"]:
            print(f"  - {rec}")

    # Export graph data
    print("\nExporting graph data...")
    export_results = mapper.export_graph_data("docs/constellation/")
    print(f"  GraphML: {export_results['graphml_exported']}")
    print(f"  JSON: {export_results['json_exported']}")

    # Save full results
    with open("temp_constellation_mapping_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nFull constellation mapping report saved to: temp_constellation_mapping_report.json")


if __name__ == "__main__":
    main()
