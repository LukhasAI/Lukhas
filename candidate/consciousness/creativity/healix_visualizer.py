"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Visualization Component
File: healix_visualizer.py
Path: core/visualization/healix_visualizer.py
Created: 2025-06-20
Author: lukhas AI Team

TAGS: [CRITICAL, KeyFile, Visualization]
"""

#!/usr/bin/env python3
"""
HealixMapper Visualization & UX Interface
DNA-inspired memory visualization with stunning visual representations
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from golden_healix_mapper import HealixMapper, MemoryStrand, MutationStrategy
from matplotlib.animation import FuncAnimation
from plotly.subplots import make_subplots


class HealixVisualizer:
    """
    Beautiful visualization interface for the HealixMapper
    Creates stunning DNA helix visualizations and interactive UX
    """

    def __init__(self, healix_mapper: HealixMapper):
        self.healix = healix_mapper
        self.colors = {
            "EMOTIONAL": "#FF6B6B",  # Warm red
            "CULTURAL": "#4ECDC4",  # Teal
            "EXPERIENTIAL": "#45B7D1",  # Blue
            "PROCEDURAL": "#96CEB4",  # Green
            "COGNITIVE": "#FFEAA7",  # Yellow
        }
        self.mutation_colors = {
            "POINT": "#FF8C94",
            "INSERTION": "#A8E6CF",
            "DELETION": "#FFB3BA",
            "CROSSOVER": "#B5EAD7",
        }

    async def create_dna_helix_visualization(
        self,
        title: str = "HealixMapper DNA Memory Structure",
        save_path: Optional[str] = None,
    ) -> go.Figure:
        """Create a stunning 3D DNA helix visualization of memories"""

        # Generate helix coordinates
        t = np.linspace(0, 4 * np.pi, 200)
        x1 = np.cos(t)
        y1 = np.sin(t)
        x2 = np.cos(t + np.pi)
        y2 = np.sin(t + np.pi)
        z = np.linspace(0, 10, 200)

        fig = go.Figure()

        # Create the DNA backbone
        fig.add_trace(
            go.Scatter3d(
                x=x1,
                y=y1,
                z=z,
                mode="lines+markers",
                line={"color": "rgba(100, 149, 237, 0.8)", "width": 6},
                marker={"size": 2, "color": "rgba(100, 149, 237, 0.6)"},
                name="DNA Strand 1",
                hoverinfo="skip",
            )
        )

        fig.add_trace(
            go.Scatter3d(
                x=x2,
                y=y2,
                z=z,
                mode="lines+markers",
                line={"color": "rgba(255, 105, 180, 0.8)", "width": 6},
                marker={"size": 2, "color": "rgba(255, 105, 180, 0.6)"},
                name="DNA Strand 2",
                hoverinfo="skip",
            )
        )

        # Add memory representations as bases
        memory_positions = []
        memory_data = []

        for strand_type in MemoryStrand:
            memories = self.healix.strands[strand_type]
            for i, memory in enumerate(memories):
                # Calculate position along helix
                pos_index = len(memory_positions) * 10
                if pos_index < len(t):
                    base_x = (x1[pos_index] + x2[pos_index]) / 2
                    base_y = (y1[pos_index] + y2[pos_index]) / 2
                    base_z = z[pos_index]

                    memory_positions.append([base_x, base_y, base_z])
                    memory_data.append(
                        {
                            "content": memory["data"].get("content", "")[:50] + "...",
                            "strand": strand_type.value,
                            "resonance": memory["resonance"],
                            "mutations": len(memory.get("mutations", [])),
                            "id": memory["id"][:20] + "...",
                        }
                    )

        # Add memory nodes
        if memory_positions:
            positions = np.array(memory_positions)

            fig.add_trace(
                go.Scatter3d(
                    x=positions[:, 0],
                    y=positions[:, 1],
                    z=positions[:, 2],
                    mode="markers",
                    marker={
                        "size": [mem["resonance"] * 15 + 5 for mem in memory_data],
                        "color": [self.colors[mem["strand"]] for mem in memory_data],
                        "opacity": 0.8,
                        "line": {"width": 2, "color": "white"},
                    },
                    text=[
                        f"💭 {mem['content']}<br>🧬 {mem['strand']}<br>⚡ Resonance: {mem['resonance']:.3f}<br>🔬 Mutations: {mem['mutations']}<br>🆔 {mem['id']}"
                        for mem in memory_data
                    ],
                    hovertemplate="%{text}<extra></extra>",
                    name="Memories",
                )
            )

        # Connect the base pairs
        for i in range(0, len(t), 20):
            fig.add_trace(
                go.Scatter3d(
                    x=[x1[i], x2[i]],
                    y=[y1[i], y2[i]],
                    z=[z[i], z[i]],
                    mode="lines",
                    line={"color": "rgba(200, 200, 200, 0.3)", "width": 2},
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # Update layout for stunning visuals
        fig.update_layout(
            title={
                "text": title,
                "x": 0.5,
                "font": {"size": 24, "color": "#2E4057", "family": "Arial Black"},
            },
            scene={
                "xaxis": {"showgrid": False, "showticklabels": False, "title": ""},
                "yaxis": {"showgrid": False, "showticklabels": False, "title": ""},
                "zaxis": {
                    "showgrid": False,
                    "showticklabels": False,
                    "title": "Memory Depth",
                },
                "bgcolor": "rgba(240, 248, 255, 0.1)",
                "camera": {"eye": {"x": 1.5, "y": 1.5, "z": 1.5}},
            },
            paper_bgcolor="white",
            font={"color": "#2E4057"},
            width=1000,
            height=800,
        )

        if save_path:
            fig.write_html(save_path)

        return fig

    async def create_memory_dashboard(self) -> go.Figure:
        """Create a comprehensive memory system dashboard"""

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=3,
            subplot_titles=(
                "Memory Distribution",
                "Resonance Patterns",
                "Mutation Activity",
                "Temporal Patterns",
                "Strand Health",
                "System Overview",
            ),
            specs=[
                [{"type": "pie"}, {"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "radar"}, {"type": "indicator"}],
            ],
        )

        # 1. Memory Distribution (Pie Chart)
        strand_counts = {
            strand.value: len(self.healix.strands[strand]) for strand in MemoryStrand
        }
        non_zero_strands = {k: v for k, v in strand_counts.items() if v > 0}

        if non_zero_strands:
            fig.add_trace(
                go.Pie(
                    labels=list(non_zero_strands.keys()),
                    values=list(non_zero_strands.values()),
                    marker_colors=[self.colors[strand] for strand in non_zero_strands],
                    textinfo="label+percent",
                    hole=0.3,
                ),
                row=1,
                col=1,
            )

        # 2. Resonance Patterns (Scatter)
        all_memories = []
        for strand_type in MemoryStrand:
            for memory in self.healix.strands[strand_type]:
                all_memories.append(
                    {
                        "resonance": memory["resonance"],
                        "strand": strand_type.value,
                        "age_hours": (
                            datetime.utcnow()
                            - datetime.fromisoformat(memory["created"])
                        ).total_seconds()
                        / 3600,
                        "mutations": len(memory.get("mutations", [])),
                    }
                )

        if all_memories:
            for strand in {mem["strand"] for mem in all_memories}:
                strand_mems = [mem for mem in all_memories if mem["strand"] == strand]
                fig.add_trace(
                    go.Scatter(
                        x=[mem["age_hours"] for mem in strand_mems],
                        y=[mem["resonance"] for mem in strand_mems],
                        mode="markers",
                        marker={
                            "size": [mem["mutations"] * 3 + 8 for mem in strand_mems],
                            "color": self.colors[strand],
                            "opacity": 0.7,
                        },
                        name=strand,
                        showlegend=False,
                    ),
                    row=1,
                    col=2,
                )

        # 3. Mutation Activity (Bar Chart)
        mutation_counts = defaultdict(int)
        for strand_type in MemoryStrand:
            for memory in self.healix.strands[strand_type]:
                for mutation in memory.get("mutations", []):
                    mutation_counts[mutation.get("type", "unknown")] += 1

        if mutation_counts:
            fig.add_trace(
                go.Bar(
                    x=list(mutation_counts.keys()),
                    y=list(mutation_counts.values()),
                    marker_color=[
                        self.mutation_colors.get(mut, ")  # 95A5A6"
                        for mut in mutation_counts
                    ],
                    showlegend=False,
                ),
                row=1,
                col=3,
            )

        # 4. Temporal Patterns (Timeline)
        if all_memories:
            fig.add_trace(
                go.Scatter(
                    x=[
                        datetime.fromisoformat(datetime.utcnow().isoformat())
                        - datetime.timedelta(hours=mem["age_hours"])
                        for mem in all_memories
                    ],
                    y=[mem["resonance"] for mem in all_memories],
                    mode="markers+lines",
                    marker={
                        "color": [self.colors[mem["strand"]] for mem in all_memories],
                        "size": 8,
                    },
                    line={"color": "rgba(100, 100, 100, 0.3)"},
                    showlegend=False,
                ),
                row=2,
                col=1,
            )

        # 5. Strand Health (Radar)
        strand_health = {}
        for strand_type in MemoryStrand:
            memories = self.healix.strands[strand_type]
            if memories:
                avg_resonance = sum(mem["resonance"] for mem in memories) / len(
                    memories
                )
                mutation_rate = sum(
                    len(mem.get("mutations", [])) for mem in memories
                ) / len(memories)
                health_score = min(1.0, avg_resonance * (1 + mutation_rate / 10))
                strand_health[strand_type.value] = health_score
            else:
                strand_health[strand_type.value] = 0

        fig.add_trace(
            go.Scatterpolar(
                r=list(strand_health.values()),
                theta=list(strand_health.keys()),
                fill="toself",
                fillcolor="rgba(70, 130, 180, 0.3)",
                line={"color": "rgba(70, 130, 180, 0.8)", "width": 2},
                showlegend=False,
            ),
            row=2,
            col=2,
        )

        # 6. System Overview (Indicator)
        total_memories = sum(
            len(self.healix.strands[strand]) for strand in MemoryStrand
        )
        avg_system_resonance = (
            (
                sum(
                    sum(mem["resonance"] for mem in self.healix.strands[strand])
                    for strand in MemoryStrand
                )
                / total_memories
            )
            if total_memories > 0
            else 0
        )

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=avg_system_resonance,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "System Health"},
                gauge={
                    "axis": {"range": [None, 1]},
                    "bar": {"color": "#1f77b4"},
                    "steps": [
                        {"range": [0, 0.3], "color": "#ffcccc"},
                        {"range": [0.3, 0.7], "color": "#ffffcc"},
                        {"range": [0.7, 1], "color": "#ccffcc"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 0.9,
                    },
                },
            ),
            row=2,
            col=3,
        )

        # Update layout
        fig.update_layout(
            title={
                "text": "🧬 HealixMapper Memory System Dashboard",
                "x": 0.5,
                "font": {"size": 24, "color": "#2E4057"},
            },
            height=800,
            showlegend=True,
            paper_bgcolor="white",
            plot_bgcolor="rgba(240, 248, 255, 0.5)",
        )

        return fig

    async def create_interactive_memory_explorer(self) -> go.Figure:
        """Create an interactive memory exploration interface"""

        fig = go.Figure()

        # Create network-style memory visualization
        all_memories = []
        positions = []

        for strand_type in MemoryStrand:
            memories = self.healix.strands[strand_type]
            for i, memory in enumerate(memories):
                # Create spiral positioning for each strand
                angle = i * 0.5 + list(MemoryStrand).index(strand_type) * (
                    2 * np.pi / len(MemoryStrand)
                )
                radius = memory["resonance"] * 3 + 1

                x = radius * np.cos(angle)
                y = radius * np.sin(angle)

                positions.append([x, y])
                all_memories.append(
                    {"memory": memory, "strand": strand_type, "x": x, "y": y}
                )

        # Add memory nodes
        for mem_info in all_memories:
            memory = mem_info["memory"]
            strand = mem_info["strand"]

            # Create hover text with emoji indicators
            emoji_map = {
                "EMOTIONAL": "❤️",
                "CULTURAL": "🏛️",
                "EXPERIENTIAL": "🌟",
                "PROCEDURAL": "⚙️",
                "COGNITIVE": "🧠",
            }

            hover_text = f"""
            {emoji_map.get(strand.value, '💭')} <b>{strand.value.title()} Memory</b><br>
            📝 {memory['data'].get('content', '')[:100]}...<br>
            ⚡ Resonance: {memory['resonance']:.3f}<br>
            🔬 Mutations: {len(memory.get('mutations', []))}<br>
            📅 Created: {memory['created'][:19]}<br>
            🆔 ID: {memory['id'][:25]}...
            """

            fig.add_trace(
                go.Scatter(
                    x=[mem_info["x"]],
                    y=[mem_info["y"]],
                    mode="markers",
                    marker={
                        "size": memory["resonance"] * 30 + 15,
                        "color": self.colors[strand.value],
                        "opacity": 0.8,
                        "line": {"width": 2, "color": "white"},
                        "symbol": "circle",
                    },
                    text=hover_text,
                    hovertemplate="%{text}<extra></extra>",
                    name=strand.value,
                    showlegend=True,
                )
            )

        # Add connection lines for related memories
        # (Based on content similarity or mutations)

        fig.update_layout(
            title={
                "text": "🔍 Interactive Memory Explorer - DNA Helix View",
                "x": 0.5,
                "font": {"size": 20, "color": "#2E4057"},
            },
            xaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
            yaxis={"showgrid": False, "showticklabels": False, "zeroline": False},
            plot_bgcolor="rgba(240, 248, 255, 0.1)",
            paper_bgcolor="white",
            width=900,
            height=700,
            hovermode="closest",
        )

        return fig

    async def animate_memory_formation(
        self, memory_id: str, save_path: Optional[str] = None
    ):
        """Create an animated visualization of memory formation and evolution"""

        memory = await self.healix.retrieve_memory(memory_id)
        if not memory:
            print(f"Memory {memory_id} not found")
            return

        # Create animation frames showing memory evolution
        fig, ax = plt.subplots(figsize=(12, 8))

        def animate_frame(frame):
            ax.clear()

            # Draw DNA helix background
            t = np.linspace(0, 4 * np.pi, 100)
            x1 = np.cos(t)
            y1 = np.sin(t)
            x2 = np.cos(t + np.pi)
            y2 = np.sin(t + np.pi)

            ax.plot(x1, y1, "b-", alpha=0.3, linewidth=2)
            ax.plot(x2, y2, "r-", alpha=0.3, linewidth=2)

            # Show memory evolution up to current frame
            mutations = memory["mutations"][:frame]

            # Base memory representation
            center_x, center_y = 0, 0
            memory["resonance"] * 1000

            circle = plt.Circle(
                (center_x, center_y),
                0.3,
                color=self.colors.get(memory_id.split("_")[0].upper(), "#95A5A6"),
                alpha=0.7,
            )
            ax.add_patch(circle)

            # Show mutations as growing connections
            for i, mutation in enumerate(mutations):
                angle = i * (2 * np.pi / max(len(mutations), 1))
                mut_x = center_x + 0.5 * np.cos(angle)
                mut_y = center_y + 0.5 * np.sin(angle)

                ax.plot(
                    [center_x, mut_x], [center_y, mut_y], "g-", linewidth=2, alpha=0.6
                )
                ax.scatter(
                    mut_x,
                    mut_y,
                    s=100,
                    c=self.mutation_colors.get(
                        mutation.get("type", "").upper(), "#95A5A6"
                    ),
                    alpha=0.8,
                )

            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect("equal")
            ax.set_title(
                f"Memory Evolution: {memory_id[:30]}...\nFrame {frame}/{len(mutations)+1}",
                fontsize=14,
                fontweight="bold",
            )
            ax.set_facecolor("rgba(240, 248, 255, 0.3)")

        # Create animation
        total_frames = len(memory["mutations"]) + 1
        anim = FuncAnimation(
            fig, animate_frame, frames=total_frames, interval=1000, repeat=True
        )

        if save_path:
            anim.save(save_path, writer="pillow", fps=1)

        plt.show()
        return anim

    async def create_mutation_flow_diagram(self) -> go.Figure:
        """Create a beautiful flow diagram showing mutation patterns"""

        fig = go.Figure()

        # Collect all mutations across all memories
        all_mutations = []
        for strand_type in MemoryStrand:
            for memory in self.healix.strands[strand_type]:
                for mutation in memory.get("mutations", []):
                    all_mutations.append(
                        {
                            "type": mutation.get("type", "unknown"),
                            "timestamp": mutation.get("timestamp", ""),
                            "memory_strand": strand_type.value,
                            "memory_id": memory["id"],
                        }
                    )

        # Create Sankey diagram for mutation flow
        if all_mutations:
            # Count flows between strand types and mutation types
            flows = defaultdict(int)

            for mut in all_mutations:
                flow_key = f"{mut['memory_strand']} → {mut['type']}"
                flows[flow_key] += 1

            # Prepare data for Sankey
            sources = []
            targets = []
            values = []

            strand_names = [strand.value for strand in MemoryStrand]
            mutation_names = list({mut["type"] for mut in all_mutations})
            all_nodes = strand_names + mutation_names

            for flow, count in flows.items():
                source_name, target_name = flow.split(" → ")
                if source_name in all_nodes and target_name in all_nodes:
                    sources.append(all_nodes.index(source_name))
                    targets.append(all_nodes.index(target_name))
                    values.append(count)

            fig.add_trace(
                go.Sankey(
                    node={
                        "pad": 15,
                        "thickness": 20,
                        "line": {"color": "black", "width": 0.5},
                        "label": all_nodes,
                        "color": [
                            (
                                self.colors.get(node, ")  # 95A5A6"
                                if node in strand_names
                                else self.mutation_colors.get(node.upper(), "#95A5A6")
                            )
                            for node in all_nodes
                        ],
                    },
                    link={
                        "source": sources,
                        "target": targets,
                        "value": values,
                        "color": "rgba(100, 150, 200, 0.4)",
                    },
                )
            )

        fig.update_layout(
            title={
                "text": "🔀 Memory Mutation Flow Pattern",
                "x": 0.5,
                "font": {"size": 20, "color": "#2E4057"},
            },
            font_size=12,
            width=1000,
            height=600,
            paper_bgcolor="white",
        )

        return fig


# Demo interface
async def launch_healix_ui():
    """Launch the complete HealixMapper UI experience"""
    print("🚀 Launching HealixMapper Visual Experience...")

    # Initialize systems
    healix = HealixMapper()
    visualizer = HealixVisualizer(healix)

    # Create some sample memories for demonstration
    sample_memories = [
        {
            "memory": {
                "content": "The moment I first understood the beauty of DNA-inspired computing",
                "emotional_weight": 0.95,
                "valence": "positive",
                "metadata": {"breakthrough": True, "inspiration": "nature"},
            },
            "strand": MemoryStrand.COGNITIVE,
            "context": {"research_session": "biomimetic_computing"},
        },
        {
            "memory": {
                "content": "Traditional family stories passed down through generations",
                "cultural_markers": ["storytelling", "heritage", "wisdom"],
                "origin": "grandmother",
                "metadata": {"importance": "high", "preservation": "critical"},
            },
            "strand": MemoryStrand.CULTURAL,
            "context": {"family_gathering": "holiday_tradition"},
        },
        {
            "memory": {
                "content": "The overwhelming joy of seeing a complex system finally work",
                "emotional_weight": 0.9,
                "valence": "positive",
                "context": {"achievement": "system_integration"},
                "metadata": {"milestone": True, "satisfaction": "profound"},
            },
            "strand": MemoryStrand.EMOTIONAL,
            "context": {"project": "healix_completion"},
        },
    ]

    # Add sample memories
    memory_ids = []
    for sample in sample_memories:
        memory_id = await healix.encode_memory(
            sample["memory"], sample["strand"], sample["context"]
        )
        memory_ids.append(memory_id)
        print(f"✅ Added {sample['strand'].value} memory: {memory_id[:30]}...")

    # Add some mutations for demonstration
    if memory_ids:
        await healix.mutate_memory(
            memory_ids[0],
            {"data": {"insight_level": "profound"}, "position": "metadata"},
            MutationStrategy.INSERTION,
        )

        if len(memory_ids) > 1:
            await healix.mutate_memory(
                memory_ids[1],
                {"source_memory_id": memory_ids[0], "fields": ["metadata"]},
                MutationStrategy.CROSSOVER,
            )

    print("\n🎨 Creating visualizations...")

    # Create all visualizations
    print("🧬 Generating 3D DNA Helix...")
    dna_fig = await visualizer.create_dna_helix_visualization()
    dna_fig.write_html(
        "/Users/A_G_I/CodexGPT_Lukhas/golden_transfers/healix_dna_helix.html"
    )

    print("📊 Creating Memory Dashboard...")
    dashboard_fig = await visualizer.create_memory_dashboard()
    dashboard_fig.write_html(
        "/Users/A_G_I/CodexGPT_Lukhas/golden_transfers/healix_dashboard.html"
    )

    print("🔍 Building Interactive Explorer...")
    explorer_fig = await visualizer.create_interactive_memory_explorer()
    explorer_fig.write_html(
        "/Users/A_G_I/CodexGPT_Lukhas/golden_transfers/healix_explorer.html"
    )

    print("🔀 Generating Mutation Flow...")
    flow_fig = await visualizer.create_mutation_flow_diagram()
    flow_fig.write_html(
        "/Users/A_G_I/CodexGPT_Lukhas/golden_transfers/healix_mutations.html"
    )

    print("\n✨ HealixMapper Visual Experience Ready!")
    print("📁 Files created:")
    print("   • healix_dna_helix.html - 3D DNA structure visualization")
    print("   • healix_dashboard.html - System overview dashboard")
    print("   • healix_explorer.html - Interactive memory explorer")
    print("   • healix_mutations.html - Mutation flow patterns")
    print("\n🌟 Open these HTML files in your browser for the full experience!")

    return healix, visualizer


if __name__ == "__main__":
    asyncio.run(launch_healix_ui())
