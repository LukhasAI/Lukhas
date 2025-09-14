#!/usr/bin/env python3
"""
LUKHAS Module Dependency Visualizer

Creates visual dependency graphs and architecture diagrams for LUKHAS modules.
    Generates interactive HTML visualizations and static diagrams.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

import json
from pathlib import Path
from typing import Optional

import yaml


class DependencyVisualizer:
        """Creates visual dependency graphs"""

    def __init__(self, schemas_dir: Path):
        self.schemas_dir = Path(schemas_dir)
        self.modules = {}
        self.dependencies = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load module schemas"""
        schema_files = list(self.schemas_dir.glob("*.yaml"))
        schema_files = [f for f in schema_files if f.name != "module_schema_template.yaml"]

        for schema_file in schema_files:
            try:
                with open(schema_file) as f:
                    schema = yaml.safe_load(f)

                identity = schema.get("identity", {})
                module_name = identity.get("name", "")

                if module_name:
                    self.modules[module_name] = {
                        "name": module_name,
                        "layer": identity.get("layer", "unknown"),
                        "tier": identity.get("tier", 5),
                        "status": identity.get("status", "active"),
                        "owner": schema.get("ownership", {}).get("owner", "@unknown"),
                    }

                    deps = schema.get("dependencies", {}).get("internal", {}).get("requires", [])
                    self.dependencies[module_name] = deps

            except Exception as e:
                print(f"Warning: Could not load {schema_file.name}: {e}")

    def generate_dot_graph(self, output_file: Path, focus_module: Optional[str] = None) -> None:
        """Generate Graphviz DOT file"""
        dot_content = ["digraph LUKHAS_Modules {"]
        dot_content.append("  rankdir=TB;")
        dot_content.append("  node [shape=box, style=rounded];")
        dot_content.append("  edge [color=gray];")
        dot_content.append("")

        # Color scheme by layer

        # Color scheme by tier
        tier_colors = {
            1: "#FF4757",  # Critical - Red
            2: "#FFA502",  # High - Orange
            3: "#2ED573",  # Medium - Green
            4: "#70A1FF",  # Low - Blue
            5: "#A4B0BE",  # Minimal - Gray
        }

        # Add nodes with styling
        modules_to_show = set()
        if focus_module and focus_module in self.modules:
            # Show focus module and its dependencies/dependents
            modules_to_show.add(focus_module)
            modules_to_show.update(self.dependencies.get(focus_module, []))

            # Add dependents
            for mod, deps in self.dependencies.items():
                if focus_module in deps:
                    modules_to_show.add(mod)
        else:
            modules_to_show = set(self.modules.keys())

        # Add subgraphs by lane
        lanes = {}
        for module_name in modules_to_show:
            if module_name in self.modules:
                lane = module_name.split(".")[0] if "." in module_name else "root"
                if lane not in lanes:
                    lanes[lane] = []
                lanes[lane].append(module_name)

        for lane, modules in lanes.items():
            dot_content.append(f"  subgraph cluster_{lane} {{}}")
            dot_content.append(f'    label="{lane.upper()}";')
            dot_content.append("    style=dashed;")
            dot_content.append("    color=lightgray;")

            for module_name in modules:
                if module_name in self.modules:
                    module = self.modules[module_name]

                    # Determine node color
                    color = tier_colors.get(module["tier"], "#A4B0BE")

                    # Node styling
                    label = module_name.split(".")[-1] if "." in module_name else module_name
                    dot_content.append(f'    "{module_name}" [')
                    dot_content.append(f'      label="{label}\\nT{module["tier"]}"')
                    dot_content.append(f'      fillcolor="{color}"')
                    dot_content.append('      style="rounded,filled"')

                    if module_name == focus_module:
                        dot_content.append("      penwidth=3")
                        dot_content.append("      color=red")

                    dot_content.append("    ];")

            dot_content.append("  }")
            dot_content.append("")

        # Add dependency edges
        for module, deps in self.dependencies.items():
            if module in modules_to_show:
                for dep in deps:
                    if dep in modules_to_show:
                        # Style edge based on cross-lane dependencies
                        module_lane = module.split(".")[0] if "." in module else "root"
                        dep_lane = dep.split(".")[0] if "." in dep else "root"

                        edge_style = ""
                        if module_lane != dep_lane:
                            edge_style = " [color=red, penwidth=2]"  # Cross-lane dependency

                        dot_content.append(f'  "{dep}" -> "{module}"{edge_style};')

        # Add legend
        dot_content.append("  // Legend")
        dot_content.append("  subgraph cluster_legend {")
        dot_content.append('    label="Legend";')
        dot_content.append("    style=dashed;")
        dot_content.append("    color=black;")

        for tier, color in tier_colors.items():
            dot_content.append(f'    "tier{tier}" [label="Tier {tier}" fillcolor="{color}" style="rounded,filled"];')

        dot_content.append("  }")
        dot_content.append("}")

        # Write to file
        with open(output_file, "w") as f:
            f.write("\\n".join(dot_content))

        print(f"Generated DOT file: {output_file}")

    def generate_mermaid_diagram(self, output_file: Path, focus_module: Optional[str] = None) -> None:
        """Generate Mermaid diagram"""
        mermaid_content = ["graph TD"]
        mermaid_content.append("")

        # Determine modules to show
        modules_to_show = set()
        if focus_module and focus_module in self.modules:
            modules_to_show.add(focus_module)
            modules_to_show.update(self.dependencies.get(focus_module, []))

            for mod, deps in self.dependencies.items():
                if focus_module in deps:
                    modules_to_show.add(mod)
        else:
            # Limit to critical modules for readability
            modules_to_show = {
                name
                for name, info in self.modules.items()
                if info["tier"] <= 2  # Only tier 1-2 modules
            }

        # Create node definitions
        for module_name in modules_to_show:
            if module_name in self.modules:
                module = self.modules[module_name]
                safe_name = module_name.replace(".", "_").replace("-", "_")
                display_name = module_name.split(".")[-1] if "." in module_name else module_name

                # Node styling based on tier
                if module["tier"] == 1:
                    style = ":::critical"
                elif module["tier"] == 2:
                    style = ":::high"
                else:
                    style = ":::normal"

                mermaid_content.append(f'  {safe_name}["{display_name}<br/>T{module["tier"]}"] {style}')

        mermaid_content.append("")

        # Add dependencies
        for module, deps in self.dependencies.items():
            if module in modules_to_show:
                safe_module = module.replace(".", "_").replace("-", "_")

                for dep in deps:
                    if dep in modules_to_show:
                        safe_dep = dep.replace(".", "_").replace("-", "_")

                        # Check for cross-lane dependencies
                        module_lane = module.split(".")[0] if "." in module else "root"
                        dep_lane = dep.split(".")[0] if "." in dep else "root"

                        if module_lane != dep_lane:
                            mermaid_content.append(f"  {safe_dep} -.->|cross-lane| {safe_module}")
                        else:
                            mermaid_content.append(f"  {safe_dep} --> {safe_module}")

        # Add styling
        mermaid_content.extend(
            [
                "",
                "  classDef critical fill:#ff4757,stroke:#333,stroke-width:2px,color:#fff",
                "  classDef high fill:#ffa502,stroke:#333,stroke-width:2px,color:#fff",
                "  classDef normal fill:#2ed573,stroke:#333,stroke-width:2px,color:#fff",
            ]
        )

        with open(output_file, "w") as f:
            f.write("\\n".join(mermaid_content))

        print(f"Generated Mermaid diagram: {output_file}")

    def generate_html_interactive(self, output_file: Path) -> None:
        """Generate interactive HTML visualization using vis.js"""

        # Prepare data for vis.js
        nodes = []
        edges = []

        # Color mapping
        layer_colors = {
            "foundational": "#FF6B6B",
            "infrastructure": "#4ECDC4",
            "application": "#45B7D1",
            "interface": "#96CEB4",
        }

        # Create nodes
        for module_name, module in self.modules.items():
            color = layer_colors.get(module["layer"], "#A4B0BE")

            nodes.append(
                {
                    "id": module_name,
                    "label": module_name.split(".")[-1] if "." in module_name else module_name,
                    "title": f"{module_name}\\nLayer: {module['layer']}\\nTier: {module['tier']}\\nOwner: {module['owner']}",
                    "color": color,
                    "size": 30 - (module["tier"] * 5),  # Larger for lower tier numbers
                    "font": {"size": 12},
                }
            )

        # Create edges
        edge_id = 0
        for module, deps in self.dependencies.items():
            if module in self.modules:
                for dep in deps:
                    if dep in self.modules:
                        # Check for cross-lane
                        module_lane = module.split(".")[0] if "." in module else "root"
                        dep_lane = dep.split(".")[0] if "." in dep else "root"

                        edge_color = "#ff4757" if module_lane != dep_lane else "#777777"
                        edge_width = 3 if module_lane != dep_lane else 1

                        edges.append(
                            {
                                "id": edge_id,
                                "from": dep,
                                "to": module,
                                "arrows": "to",
                                "color": edge_color,
                                "width": edge_width,
                                "title": f"{dep} → {module}" + (" (cross-lane)" if module_lane != dep_lane else ""),
                            }
                        )
                        edge_id += 1

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LUKHAS Module Dependencies</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        #network { height: 800px; border: 1px solid #ccc; }
        .controls { margin: 20px 0; }
        .legend { margin: 20px 0; display: flex; gap: 20px; }
        .legend-item { display: flex; align-items: center; gap: 5px; }
        .color-box { width: 20px; height: 20px; border: 1px solid #333; }
        .stats { background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>🏗️ LUKHAS Module Dependencies</h1>

    <div class="stats">
        <strong>System Overview:</strong><br/>
        Total Modules: {len(nodes)} |
        Total Dependencies: {len(edges)} |
        Generated: {json.dumps(str(datetime.now()))}
    </div>

    <div class="legend">
        <div class="legend-item">
            <div class="color-box" style="background: #FF6B6B;"></div>
            <span>Foundational</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #4ECDC4;"></div>
            <span>Infrastructure</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #45B7D1;"></div>
            <span>Application</span>
        </div>
        <div class="legend-item">
            <div class="color-box" style="background: #96CEB4;"></div>
            <span>Interface</span>
        </div>
    </div>

    <div class="controls">
        <button onclick="fitNetwork()">Fit All</button>
        <button onclick="togglePhysics()">Toggle Physics</button>
        <button onclick="exportImage()">Export PNG</button>
    </div>

    <div id="network"></div>

    <script>
        const nodes = new vis.DataSet({json.dumps(nodes, indent=2)});
        const edges = new vis.DataSet({json.dumps(edges, indent=2)});

        const data = { nodes: nodes, edges: edges };

        const options = {{
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                stabilization: { iterations: 100 }
            },
            nodes: {{
                shape: 'box',
                margin: 10,
                widthConstraint: { minimum: 100, maximum: 200 },
                heightConstraint: { minimum: 50 }
            },
            edges: {{
                smooth: { type: 'dynamic' },
                arrows: { to: { scaleFactor: 0.5 } }
            },
            interaction: {{
                hover: true,
                selectConnectedEdges: true,
                tooltipDelay: 200
            },
            layout: {{
                improvedLayout: true,
                hierarchical: {{
                    enabled: false,
                    sortMethod: 'directed',
                    direction: 'UD'
                }
            }
        };

        const container = document.getElementById('network');
        const network = new vis.Network(container, data, options);

        let physicsEnabled = true;

        function fitNetwork() {{
            network.fit();
        }

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            network.setOptions({ physics: { enabled: physicsEnabled } });
        }

        function exportImage() {{
            const canvas = document.querySelector('#network canvas');
            const link = document.createElement('a');
            link.download = 'lukhas-dependencies.png';
            link.href = canvas.toDataURL();
            link.click();
        }

        // Event handlers
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                console.log('Selected module:', nodeId);
                // Could highlight dependencies here
            }
        });

        network.on('stabilizationProgress', function(params) {{
            console.log('Stabilization progress:', Math.round(params.iterations/params.total * 100) + '%');
        });

        network.on('stabilizationIterationsDone', function() {{
            console.log('Network stabilized');
        });
    </script>
</body>
</html>"""

        with open(output_file, "w") as f:
            f.write(html_template)

        print(f"Generated interactive HTML: {output_file}")

    def generate_architecture_summary(self, output_file: Path) -> None:
        """Generate architecture summary report"""
        from collections import defaultdict
        from datetime import datetime

        # Analyze architecture
        layer_stats = defaultdict(int)
        tier_stats = defaultdict(int)
        lane_stats = defaultdict(int)

        for module in self.modules.values():
            layer_stats[module["layer"]] += 1
            tier_stats[module["tier"]] += 1

            lane = module["name"].split(".")[0] if "." in module["name"] else "root"
            lane_stats[lane] += 1

        # Calculate coupling metrics
        total_deps = sum(len(deps) for deps in self.dependencies.values())
        avg_deps = total_deps / len(self.modules) if self.modules else 0

        # Find highly coupled modules
        highly_coupled = sorted(
            [(module, len(deps)) for module, deps in self.dependencies.items() if len(deps) > avg_deps * 1.5],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Cross-lane dependencies
        cross_lane_deps = []
        for module, deps in self.dependencies.items():
            module_lane = module.split(".")[0] if "." in module else "root"
            for dep in deps:
                dep_lane = dep.split(".")[0] if "." in dep else "root"
                if module_lane != dep_lane:
                    cross_lane_deps.append((dep, module))

        # Generate report
        report = f"""# LUKHAS Architecture Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Overview
- **Total Modules**: {len(self.modules)}
- **Total Dependencies**: {total_deps}
- **Average Dependencies per Module**: {avg_deps:.2f}
- **Cross-Lane Dependencies**: {len(cross_lane_deps)}

## Distribution by Layer
"""

        for layer, count in sorted(layer_stats.items()):
            percentage = (count / len(self.modules)) * 100
            report += f"- **{layer.title()}**: {count} modules ({percentage:.1f}%)\\n"

        report += "\\n## Distribution by Tier\\n"
        for tier, count in sorted(tier_stats.items()):
            percentage = (count / len(self.modules)) * 100
            report += f"- **Tier {tier}**: {count} modules ({percentage:.1f}%)\\n"

        report += "\\n## Distribution by Lane\\n"
        for lane, count in sorted(lane_stats.items()):
            percentage = (count / len(self.modules)) * 100
            report += f"- **{lane}**: {count} modules ({percentage:.1f}%)\\n"

        if highly_coupled:
            report += "\\n## Highly Coupled Modules (Top 10)\\n"
            for module, dep_count in highly_coupled:
                report += f"- **{module}**: {dep_count} dependencies\\n"

        if cross_lane_deps:
            report += f"\\n## Cross-Lane Dependencies ({len(cross_lane_deps)})\\n"
            for dep, module in cross_lane_deps[:20]:  # Show first 20
                report += f"- {dep} → {module}\\n"

            if len(cross_lane_deps) > 20:
                report += f"... and {len(cross_lane_deps) - 20} more\\n"

        report += """
## Recommendations
1. **Reduce Cross-Lane Dependencies**: Consider refactoring to minimize dependencies between lanes
2. **Monitor Highly Coupled Modules**: Review modules with excessive dependencies
    3. **Layer Violations**: Ensure higher layers don't depend on lower layers inappropriately
4. **Module Consolidation**: Consider merging small, tightly coupled modules
"""

        with open(output_file, "w") as f:
            f.write(report)

        print(f"Generated architecture summary: {output_file}")


def main():
        """CLI interface for dependency visualization"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Module Dependency Visualizer")
    parser.add_argument("--schemas-dir", default="modules", help="Module schemas directory")
    parser.add_argument("--output-dir", default="docs/architecture", help="Output directory")
    parser.add_argument(
        "--format", choices=["dot", "mermaid", "html", "summary", "all"], default="all", help="Output format"
    )
    parser.add_argument("--focus", help="Focus on specific module")

    args = parser.parse_args()

    print("🚀 LUKHAS Module Dependency Visualizer")
    print("-" * 40)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize visualizer
    visualizer = DependencyVisualizer(Path(args.schemas_dir))

    if args.format in ["dot", "all"]:
        dot_file = output_dir / f"dependencies{'_' + args.focus if args.focus else ''}.dot"
        visualizer.generate_dot_graph(dot_file, args.focus)

    if args.format in ["mermaid", "all"]:
        mermaid_file = output_dir / f"dependencies{'_' + args.focus if args.focus else ''}.md"
        visualizer.generate_mermaid_diagram(mermaid_file, args.focus)

    if args.format in ["html", "all"]:
        html_file = output_dir / "dependencies_interactive.html"
        visualizer.generate_html_interactive(html_file)

    if args.format in ["summary", "all"]:
        summary_file = output_dir / "architecture_summary.md"
        visualizer.generate_architecture_summary(summary_file)

    print(f"\\n✅ Visualization files generated in {output_dir}")


if __name__ == "__main__":
    from datetime import datetime

    main()
