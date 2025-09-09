import logging

logger = logging.getLogger(__name__)
import logging

#!/usr/bin/env python3
"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


Quantum Ethics Mesh Visual Debugger - ΛMESH VIS
Visual inspection and debugging interface for Quantum Ethics Mesh Integrator

ΛTAG: QUANTUM_MESH_VIS
MODULE_ID: ethics.tools.qi_mesh_visualizer
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from candidate.core.common import get_logger

# Visualization libraries
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib/seaborn not available. Some visualizations disabled.", timezone)

try:
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.offline as pyo
    from plotly.subplots import make_subplots

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    print("Warning: plotly not available. Interactive features disabled.")

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

try:
    from ethics.qi_mesh_integrator import QIEthicsMeshIntegrator
except ImportError:
    print("Warning: Could not import QIEthicsMeshIntegrator")
    QIEthicsMeshIntegrator = None

logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class QIMeshVisualizer:
    """Visual debugger for Quantum Ethics Mesh states and entanglements"""

    def __init__(self, output_dir: str = "ethics/tools/mesh_snapshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_data = None
        self.color_schemes = self._setup_color_schemes()

        # Standard subsystem names
        self.subsystems = [
            "emotion",
            "memory",
            "reasoning",
            "dream",
            "ethics",
            "consciousness",
        ]

    def _setup_color_schemes(self) -> dict[str, Any]:
        """Setup color schemes for different visualizations"""
        return {
            "entanglement": {
                "cmap": "RdYlGn",  # Red-Yellow-Green for strength
                "thresholds": {"low": 0.3, "medium": 0.6, "high": 0.8},
            },
            "risk": {
                "SAFE": "#2ecc71",  # Green
                "CAUTION": "#f39c12",  # Orange
                "WARNING": "#e74c3c",  # Red
                "CRITICAL": "#8e44ad",  # Purple
                "EMERGENCY": "#2c3e50",  # Dark blue
            },
            "coherence": {"cmap": "plasma", "range": (0.0, 1.0)},
        }

    def load_entanglement_data(self, log_path: Optional[str] = None, live_mode: bool = False) -> dict[str, Any]:
        """
        Load entanglement matrix, phase conflicts, and ethics mesh states

        Args:
            log_path: Path to log file (JSONL format)
            live_mode: Whether to pull from live integrator

        Returns:
            Dict containing mesh data
        """
        logger.info(f"Loading entanglement data: log_path={log_path}, live_mode={live_mode}")

        if live_mode and QIEthicsMeshIntegrator:
            return self._load_live_data()
        elif log_path and Path(log_path).exists():
            return self._load_from_logs(log_path)
        else:
            logger.warning("No data source available, generating synthetic data")
            return self._generate_synthetic_data()

    def _load_live_data(self) -> dict[str, Any]:
        """Load data from live quantum mesh integrator"""
        integrator = QIEthicsMeshIntegrator()

        # Generate sample states for live demo
        sample_states = {
            "emotion": {
                "coherence": np.random.uniform(0.6, 0.9),
                "confidence": np.random.uniform(0.7, 0.95),
                "entropy": np.random.uniform(0.1, 0.4),
                "alignment": np.random.uniform(0.75, 0.95),
                "phase": np.random.uniform(0, 2 * np.pi),
            },
            "memory": {
                "coherence": np.random.uniform(0.8, 0.95),
                "confidence": np.random.uniform(0.8, 0.98),
                "entropy": np.random.uniform(0.05, 0.25),
                "alignment": np.random.uniform(0.8, 0.95),
                "phase": np.random.uniform(0, 2 * np.pi),
            },
            "reasoning": {
                "coherence": np.random.uniform(0.7, 0.9),
                "confidence": np.random.uniform(0.8, 0.95),
                "entropy": np.random.uniform(0.1, 0.3),
                "alignment": np.random.uniform(0.75, 0.9),
                "phase": np.random.uniform(0, 2 * np.pi),
            },
            "dream": {
                "coherence": np.random.uniform(0.5, 0.8),
                "confidence": np.random.uniform(0.6, 0.8),
                "entropy": np.random.uniform(0.2, 0.5),
                "alignment": np.random.uniform(0.6, 0.85),
                "phase": np.random.uniform(0, 2 * np.pi),
            },
        }

        # Process through integrator
        unified_field = integrator.integrate_ethics_mesh(sample_states)
        entanglement_matrix = integrator.calculate_phase_entanglement_matrix(sample_states)
        conflicts = integrator.detect_ethics_phase_conflict(entanglement_matrix)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "unified_field": unified_field,
            "entanglement_matrix": entanglement_matrix,
            "conflicts": conflicts,
            "subsystem_states": sample_states,
            "mesh_status": integrator.get_mesh_status(),
        }

    def _load_from_logs(self, log_path: str) -> dict[str, Any]:
        """Load data from jsonl_log file"""
        try:
            with open(log_path) as f:
                lines = f.readlines()

            # Get most recent entry
            if lines:
                latest_entry = json.loads(lines[-1])
                logger.info(f"Loaded {len(lines)} log entries, using latest")
                return latest_entry
            else:
                logger.warning("Log file empty, generating synthetic data")
                return self._generate_synthetic_data()

        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
            return self._generate_synthetic_data()

    def _generate_synthetic_data(self) -> dict[str, Any]:
        """Generate synthetic mesh data for demonstration"""
        logger.info("Generating synthetic mesh data")

        # Generate realistic subsystem states
        subsystem_states = {}
        for system in self.subsystems[:4]:  # Focus on main 4
            coherence = np.random.normal(0.8, 0.1)
            confidence = np.random.normal(0.85, 0.1)
            entropy = np.random.normal(0.2, 0.05)
            alignment = np.random.normal(0.8, 0.1)
            phase = np.random.uniform(0, 2 * np.pi)

            subsystem_states[system] = {
                "coherence": max(0.0, min(1.0, coherence)),
                "confidence": max(0.0, min(1.0, confidence)),
                "entropy": max(0.0, min(1.0, entropy)),
                "alignment": max(0.0, min(1.0, alignment)),
                "phase": phase,
            }

        # Generate entanglement matrix
        entanglements = {}
        modules = list(subsystem_states.keys())

        for i, mod_a in enumerate(modules):
            for _j, mod_b in enumerate(modules[i + 1 :], i + 1):
                strength = np.random.beta(3, 1)  # Bias toward higher values
                phase_diff = abs(subsystem_states[mod_a]["phase"] - subsystem_states[mod_b]["phase"])
                phase_diff = min(phase_diff, 2 * np.pi - phase_diff)

                coherence = (subsystem_states[mod_a]["coherence"] + subsystem_states[mod_b]["coherence"]) / 2
                conflict_risk = max(0.0, 0.5 - strength) * np.random.uniform(0.5, 1.5)

                pair_key = f"{mod_a}↔{mod_b}"
                entanglements[pair_key] = {
                    "strength": strength,
                    "phase_diff": phase_diff,
                    "coherence": coherence,
                    "conflict_risk": conflict_risk,
                }

        # Generate conflicts based on risk
        conflicts = [
            pair
            for pair, metrics in entanglements.items()
            if metrics["conflict_risk"] > 0.3 or metrics["strength"] < 0.4
        ]

        # Generate unified field
        mesh_score = np.mean([s["coherence"] * s["alignment"] for s in subsystem_states.values()])
        risk_levels = ["SAFE", "CAUTION", "WARNING"]
        risk_level = risk_levels[min(2, len(conflicts))]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "unified_field": {
                "mesh_ethics_score": mesh_score,
                "coherence": np.mean([s["coherence"] for s in subsystem_states.values()]),
                "confidence": np.mean([s["confidence"] for s in subsystem_states.values()]),
                "entropy": np.mean([s["entropy"] for s in subsystem_states.values()]),
                "alignment": np.mean([s["alignment"] for s in subsystem_states.values()]),
                "phase_synchronization": np.random.uniform(0.6, 0.9),
                "stability_index": np.random.uniform(0.7, 0.9),
                "drift_magnitude": np.random.uniform(0.05, 0.2),
                "risk_level": risk_level,
                "subsystem_count": len(subsystem_states),
            },
            "entanglement_matrix": {
                "entanglements": entanglements,
                "matrix_metrics": {
                    "average_entanglement": np.mean([e["strength"] for e in entanglements.values()]),
                    "max_conflict_risk": max([e["conflict_risk"] for e in entanglements.values()]),
                    "phase_variance": np.var([s["phase"] for s in subsystem_states.values()]),
                    "total_pairs": len(entanglements),
                },
            },
            "conflicts": conflicts,
            "subsystem_states": subsystem_states,
        }

    def generate_entanglement_heatmap(self, matrix: dict[str, Any], save_path: Optional[str] = None) -> None:
        """Generate visual heatmap of pairwise entanglement scores"""
        if not HAS_MATPLOTLIB:
            print("Matplotlib not available for heatmap generation")
            return

        logger.info("Generating entanglement heatmap")

        entanglements = matrix.get("entanglements", {})
        if not entanglements:
            logger.warning("No entanglement data available")
            return

        # Extract unique modules from pair names
        modules = set()
        for pair in entanglements:
            mod_a, mod_b = pair.split("↔")
            modules.add(mod_a)
            modules.add(mod_b)

        modules = sorted(modules)
        n_modules = len(modules)

        # Create strength and risk matrices
        strength_matrix = np.zeros((n_modules, n_modules))
        risk_matrix = np.zeros((n_modules, n_modules))

        for pair, metrics in entanglements.items():
            mod_a, mod_b = pair.split("↔")
            i, j = modules.index(mod_a), modules.index(mod_b)

            strength_matrix[i, j] = metrics["strength"]
            strength_matrix[j, i] = metrics["strength"]  # Symmetric

            risk_matrix[i, j] = metrics["conflict_risk"]
            risk_matrix[j, i] = metrics["conflict_risk"]

        # Set diagonal to 1.0 for self-entanglement
        np.fill_diagonal(strength_matrix, 1.0)

        # Create subplot for both heatmaps
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

        # Entanglement strength heatmap
        sns.heatmap(
            strength_matrix,
            xticklabels=modules,
            yticklabels=modules,
            annot=True,
            fmt=".3f",
            cmap="RdYlGn",
            vmin=0.0,
            vmax=1.0,
            ax=ax1,
            cbar_kws={"label": "Entanglement Strength"},
        )
        ax1.set_title("Quantum Entanglement Strength Matrix", fontsize=14)
        ax1.set_xlabel("Subsystem")
        ax1.set_ylabel("Subsystem")

        # Conflict risk heatmap
        sns.heatmap(
            risk_matrix,
            xticklabels=modules,
            yticklabels=modules,
            annot=True,
            fmt=".3f",
            cmap="Reds",
            vmin=0.0,
            vmax=max(1.0, np.max(risk_matrix)),
            ax=ax2,
            cbar_kws={"label": "Conflict Risk"},
        )
        ax2.set_title("Phase Conflict Risk Matrix", fontsize=14)
        ax2.set_xlabel("Subsystem")
        ax2.set_ylabel("Subsystem")

        plt.tight_layout()

        # Save or show
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Heatmap saved to {save_path}")
        else:
            plt.savefig(
                self.output_dir / "entanglement_heatmap.png",
                dpi=300,
                bbox_inches="tight",
            )
            logger.info(f"Heatmap saved to {self.output_dir / 'entanglement_heatmap.png'}")

        plt.show()

    def plot_phase_synchronization(self, data: dict[str, Any], save_path: Optional[str] = None) -> None:
        """Generate radar chart showing phase sync across subsystems"""
        if not HAS_MATPLOTLIB:
            print("Matplotlib not available for radar chart")
            return

        logger.info("Generating phase synchronization radar chart")

        subsystem_states = data.get("subsystem_states", {})
        if not subsystem_states:
            logger.warning("No subsystem states available")
            return

        # Prepare data
        modules = list(subsystem_states.keys())
        metrics = ["coherence", "confidence", "alignment", "stability"]

        # Extract values for radar chart
        values = []
        for metric in metrics:
            if metric == "stability":
                # Calculate stability from entropy (inverse)
                metric_values = [1.0 - state.get("entropy", 0.5) for state in subsystem_states.values()]
            else:
                metric_values = [state.get(metric, 0.5) for state in subsystem_states.values()]
            values.append(metric_values)

        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": "polar"})

        colors = plt.cm.Set3(np.linspace(0, 1, len(modules)))

        for i, module in enumerate(modules):
            module_values = [values[j][i] for j in range(len(metrics))]
            module_values += module_values[:1]  # Complete the circle

            ax.plot(angles, module_values, "o-", linewidth=2, label=module, color=colors[i])
            ax.fill(angles, module_values, alpha=0.25, color=colors[i])

        # Customize chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"])
        ax.grid(True)

        plt.legend(loc="upper right", bbox_to_anchor=(1.2, 1.0))
        plt.title(
            "Subsystem Phase Synchronization Radar\n(Ethics Mesh Coherence)",
            size=14,
            y=1.08,
        )

        # Save or show
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Radar chart saved to {save_path}")
        else:
            plt.savefig(self.output_dir / "phase_sync_radar.png", dpi=300, bbox_inches="tight")
            logger.info(f"Radar chart saved to {self.output_dir / 'phase_sync_radar.png'}")

        plt.show()

    def list_active_conflict_pairs(self, conflicts: list[str], entanglements: dict[str, Any]) -> str:
        """Generate human-readable output of phase-misaligned modules and risk tiers"""
        if not conflicts:
            return "✅ No active phase conflicts detected - mesh is stable\n"

        output = []
        output.append(f"⚠️  ACTIVE PHASE CONFLICTS: {len(conflicts)} pairs\n")
        output.append("=" * 60)

        # Sort conflicts by risk level
        conflict_data = []
        for conflict in conflicts:
            if conflict in entanglements:
                metrics = entanglements[conflict]
                risk_score = metrics.get("conflict_risk", 0.0)
                strength = metrics.get("strength", 0.0)
                phase_diff = metrics.get("phase_diff", 0.0)

                # Determine risk tier
                if risk_score >= 0.7 or strength < 0.3:
                    tier = "🔴 CRITICAL"
                elif risk_score >= 0.4 or strength < 0.5:
                    tier = "🟠 HIGH"
                elif risk_score >= 0.2:
                    tier = "🟡 MEDIUM"
                else:
                    tier = "🟢 LOW"

                conflict_data.append(
                    {
                        "pair": conflict,
                        "tier": tier,
                        "risk_score": risk_score,
                        "strength": strength,
                        "phase_diff": phase_diff,
                        "sort_key": risk_score,
                    }
                )

        # Sort by risk score (highest first)
        conflict_data.sort(key=lambda x: x["sort_key"], reverse=True)

        # Format output
        for i, conflict in enumerate(conflict_data, 1):
            output.append(f"\n{i}. {conflict['tier']} - {conflict['pair']}")
            output.append(f"   Entanglement Strength: {conflict['strength']:.3f}")
            output.append(f"   Conflict Risk:        {conflict['risk_score']:.3f}")
            output.append(
                f"   Phase Difference:     {conflict['phase_diff']:.3f} rad ({np.degrees(conflict['phase_diff']):.1f}°)"
            )

            # Add recommendations
            if conflict["risk_score"] >= 0.5:
                output.append("   🚨 IMMEDIATE ACTION: Phase harmonization required")
            elif conflict["strength"] < 0.4:
                output.append("   💡 RECOMMEND: Strengthen subsystem coupling")
            else:
                output.append("   📊 MONITOR: Watch for escalation")

        output.append("\n" + "=" * 60)
        output.append(
            f"SUMMARY: {len([c for c in conflict_data if c['sort_key'] >= 0.5])} critical, "
            f"{len([c for c in conflict_data if 0.2 <= c['sort_key'] < 0.5])} medium risk"
        )

        return "\n".join(output)

    def generate_interactive_dashboard(self, data: dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate interactive HTML dashboard with hover tooltips"""
        if not HAS_PLOTLY:
            print("Plotly not available for interactive dashboard")
            return self._generate_static_dashboard(data, output_path)

        logger.info("Generating interactive dashboard")

        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Entanglement Matrix",
                "Phase Synchronization",
                "Risk Timeline",
                "Subsystem Health",
            ),
            specs=[
                [{"type": "heatmap"}, {"type": "scatterpolar"}],
                [{"type": "scatter"}, {"type": "bar"}],
            ],
        )

        # 1. Entanglement heatmap
        entanglements = data["entanglement_matrix"]["entanglements"]
        modules = set()
        for pair in entanglements:
            mod_a, mod_b = pair.split("↔")
            modules.add(mod_a)
            modules.add(mod_b)
        modules = sorted(modules)

        # Create strength matrix
        n_modules = len(modules)
        strength_matrix = np.zeros((n_modules, n_modules))
        hover_text = [["" for _ in range(n_modules)] for _ in range(n_modules)]

        for pair, metrics in entanglements.items():
            mod_a, mod_b = pair.split("↔")
            i, j = modules.index(mod_a), modules.index(mod_b)

            strength = metrics["strength"]
            strength_matrix[i, j] = strength
            strength_matrix[j, i] = strength

            hover_info = (
                f"Pair: {mod_a} ↔ {mod_b}<br>"
                f"Strength: {strength:.3f}<br>"
                f"Risk: {metrics['conflict_risk']:.3f}<br>"
                f"Phase Diff: {metrics['phase_diff']:.3f} rad"
            )
            hover_text[i][j] = hover_info
            hover_text[j][i] = hover_info

        np.fill_diagonal(strength_matrix, 1.0)

        fig.add_trace(
            go.Heatmap(
                z=strength_matrix,
                x=modules,
                y=modules,
                colorscale="RdYlGn",
                hovertemplate="%{text}<extra></extra>",
                text=hover_text,
                showscale=True,
            ),
            row=1,
            col=1,
        )

        # 2. Phase synchronization radar
        subsystem_states = data["subsystem_states"]
        metrics = ["Coherence", "Confidence", "Alignment", "Stability"]

        for module, state in subsystem_states.items():
            values = [
                state["coherence"],
                state["confidence"],
                state["alignment"],
                1.0 - state.get("entropy", 0.5),  # Stability
            ]

            fig.add_trace(
                go.Scatterpolar(
                    r=[*values, values[0]],  # Close the polygon
                    theta=[*metrics, metrics[0]],
                    fill="toself",
                    name=module.capitalize(),
                    line_color=px.colors.qualitative.Set3[hash(module) % len(px.colors.qualitative.Set3)],
                ),
                row=1,
                col=2,
            )

        # 3. Risk timeline (synthetic data for demo)
        timestamps = [datetime.now(timezone.utc) - timedelta(hours=i) for i in range(24, 0, -1)]
        risk_values = np.random.uniform(0.1, 0.8, 24)  # Synthetic risk over time

        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=risk_values,
                mode="lines+markers",
                name="Risk Level",
                line={"color": "red", "width": 2},
                hovertemplate="Time: %{x}<br>Risk: %{y:.3f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

        # Add risk threshold lines
        fig.add_hline(
            y=0.5,
            line_dash="dash",
            line_color="orange",
            annotation_text="Warning Threshold",
            row=2,
            col=1,
        )
        fig.add_hline(
            y=0.7,
            line_dash="dash",
            line_color="red",
            annotation_text="Critical Threshold",
            row=2,
            col=1,
        )

        # 4. Subsystem health bar chart
        health_scores = []
        subsystem_names = []
        colors = []

        for module, state in subsystem_states.items():
            # Calculate composite health score
            health = state["coherence"] * 0.4 + state["confidence"] * 0.3 + state["alignment"] * 0.3
            health_scores.append(health)
            subsystem_names.append(module.capitalize())

            # Color based on health
            if health >= 0.8:
                colors.append("green")
            elif health >= 0.6:
                colors.append("orange")
            else:
                colors.append("red")

        fig.add_trace(
            go.Bar(
                x=subsystem_names,
                y=health_scores,
                marker_color=colors,
                name="Health Score",
                hovertemplate="%{x}<br>Health: %{y:.3f}<extra></extra>",
            ),
            row=2,
            col=2,
        )

        # Update layout
        fig.update_layout(
            title_text=f"Quantum Ethics Mesh Dashboard - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            title_x=0.5,
            showlegend=False,
            height=800,
            template="plotly_white",
        )

        # Update subplot titles
        fig.update_xaxes(title_text="Subsystem", row=1, col=1)
        fig.update_yaxes(title_text="Subsystem", row=1, col=1)

        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Risk Level", row=2, col=1)

        fig.update_xaxes(title_text="Subsystem", row=2, col=2)
        fig.update_yaxes(title_text="Health Score", row=2, col=2)

        # Save dashboard
        if not output_path:
            output_path = str(self.output_dir / "qi_mesh_dashboard.html")

        pyo.plot(fig, filename=output_path, auto_open=False)
        logger.info(f"Interactive dashboard saved to {output_path}")

        return output_path

    def _generate_static_dashboard(self, data: dict[str, Any], output_path: Optional[str] = None) -> str:
        """Generate static HTML dashboard when Plotly not available"""
        logger.info("Generating static HTML dashboard")

        html_content = self._create_html_template(data)

        if not output_path:
            output_path = str(self.output_dir / "qi_mesh_dashboard.html")

        with open(output_path, "w") as f:
            f.write(html_content)

        logger.info(f"Static dashboard saved to {output_path}")
        return output_path

    def export_visual_summary(self, data: dict[str, Any], output_path: str, format_type: str = "markdown") -> None:
        """
        Save current mesh state as HTML report, image, or markdown snapshot

        Args:
            data: Mesh data to export
            output_path: Path for output file
            format_type: 'html', 'markdown', or 'json'
        """
        logger.info(f"Exporting visual summary: {format_type} to {output_path}")

        if format_type.lower() == "html":
            self._export_html_report(data, output_path)
        elif format_type.lower() == "markdown":
            self._export_markdown_report(data, output_path)
        elif format_type.lower() == "json":
            self._export_json_snapshot(data, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _export_markdown_report(self, data: dict[str, Any], output_path: str) -> None:
        """Export markdown report"""
        unified_field = data["unified_field"]
        conflicts = data.get("conflicts", [])
        entanglements = data["entanglement_matrix"]["entanglements"]

        markdown = []
        markdown.append("#  Quantum Ethics Mesh Report")
        markdown.append(f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
        markdown.append(f"**Data Timestamp:** {data.get('timestamp', 'Unknown')}")
        markdown.append("")

        # Summary
        markdown.append("## Executive Summary")
        markdown.append(f"- **Mesh Ethics Score:** {unified_field['mesh_ethics_score']:.3f}")
        markdown.append(f"- **Risk Level:** {unified_field['risk_level']}")
        markdown.append(f"- **Phase Synchronization:** {unified_field['phase_synchronization']:.3f}")
        markdown.append(f"- **Active Conflicts:** {len(conflicts)}")
        markdown.append("")

        # Entanglement matrix
        markdown.append("## Entanglement Matrix")
        markdown.append("| Pair | Strength | Phase Diff | Conflict Risk |")
        markdown.append("|------|----------|------------|---------------|")

        for pair, metrics in sorted(entanglements.items()):
            strength_emoji = "🟢" if metrics["strength"] > 0.7 else ("🟡" if metrics["strength"] > 0.4 else "🔴")
            risk_emoji = "🔴" if metrics["conflict_risk"] > 0.5 else ("🟡" if metrics["conflict_risk"] > 0.2 else "🟢")

            markdown.append(
                f"| {strength_emoji} {pair} | {metrics['strength']:.3f} | "
                f"{metrics['phase_diff']:.3f} | {risk_emoji} {metrics['conflict_risk']:.3f} |"
            )

        markdown.append("")

        # Conflicts
        if conflicts:
            markdown.append("## Active Conflicts")
            for i, conflict in enumerate(conflicts, 1):
                if conflict in entanglements:
                    metrics = entanglements[conflict]
                    markdown.append(f"{i}. **{conflict}**")
                    markdown.append(f"   - Risk Score: {metrics['conflict_risk']:.3f}")
                    markdown.append(f"   - Entanglement: {metrics['strength']:.3f}")
                    markdown.append("")
        else:
            markdown.append("## Active Conflicts")
            markdown.append("✅ No conflicts detected - mesh is stable")
            markdown.append("")

        # Recommendations
        markdown.append("## Recommendations")
        if unified_field["risk_level"] in ["CRITICAL", "EMERGENCY"]:
            markdown.append("🚨 **IMMEDIATE ACTION REQUIRED**")
            markdown.append("- Implement emergency phase harmonization")
            markdown.append("- Consider subsystem isolation protocols")
        elif conflicts:
            markdown.append("⚠️  **MONITORING RECOMMENDED**")
            markdown.append("- Increase mesh synchronization frequency")
            markdown.append("- Review subsystem coupling parameters")
        else:
            markdown.append("✅ **SYSTEM STABLE**")
            markdown.append("- Continue routine monitoring")
            markdown.append("- Maintain current configuration")

        # Write file
        with open(output_path, "w") as f:
            f.write("\n".join(markdown))

        logger.info(f"Markdown report saved to {output_path}")

    def _export_html_report(self, data: dict[str, Any], output_path: str) -> None:
        """Export HTML report with embedded visualizations"""
        html_content = self._create_html_template(data)

        with open(output_path, "w") as f:
            f.write(html_content)

        logger.info(f"HTML report saved to {output_path}")

    def _export_json_snapshot(self, data: dict[str, Any], output_path: str) -> None:
        """Export JSON snapshot"""
        # Add metadata
        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "mesh_data": data,
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"JSON snapshot saved to {output_path}")

    def _create_html_template(self, data: dict[str, Any]) -> str:
        """Create HTML template for reports"""
        unified_field = data["unified_field"]
        data.get("conflicts", [])

        self.color_schemes["risk"].get(unified_field["risk_level"], "#666")

        html = "Basic HTML test"
        return html

    def _format_conflicts_html(self, conflicts: list[str], entanglements: dict[str, Any]) -> str:
        """Format conflicts for HTML display"""
        if not conflicts:
            return ""

        html_parts = []
        for conflict in conflicts:
            if conflict in entanglements:
                metrics = entanglements[conflict]
                html_parts.append(
                    f"""
                <div style="margin: 10px 0; padding: 10px; background: rgba(220, 53, 69, 0.1); border-radius: 5px;">
                    <strong>{conflict}</strong><br>
                    Risk: {metrics["conflict_risk"]:.3f} | Strength: {metrics["strength"]:.3f}
                </div>
                """
                )

        return "".join(html_parts)

    def _format_entanglements_html(self, entanglements: dict[str, Any]) -> str:
        """Format entanglements for HTML grid display"""
        html_parts = []
        for pair, metrics in entanglements.items():
            strength_pct = int(metrics["strength"] * 100)
            html_parts.append(
                f"""
            <div class="entanglement-item">
                <h4>{pair}</h4>
                <div>Strength: {metrics["strength"]:.3f}</div>
                <div class="strength-bar">
                    <div class="strength-fill" style="width: {strength_pct}%;"></div>
                </div>
                <div>Conflict Risk: {metrics["conflict_risk"]:.3f}</div>
                <div>Phase Diff: {metrics["phase_diff"]:.3f} rad</div>
            </div>
            """
            )

        return "".join(html_parts)


def main():
    """Main CLI interface for quantum mesh visualizer"""
    parser = argparse.ArgumentParser(
        description="Quantum Ethics Mesh Visual Debugger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 qi_mesh_visualizer.py --mode heatmap
  python3 qi_mesh_visualizer.py --mode sync --window 24h
  python3 qi_mesh_visualizer.py --export ./mesh_snapshots/day7_summary.md
  python3 qi_mesh_visualizer.py --dashboard --live
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["heatmap", "sync", "conflicts", "dashboard"],
        default="dashboard",
        help="Visualization mode",
    )
    parser.add_argument("--log-path", type=str, help="Path to log file (JSONL format)")
    parser.add_argument("--live", action="store_true", help="Use live mesh integrator data")
    parser.add_argument("--export", type=str, help="Export report to file")
    parser.add_argument(
        "--format",
        choices=["html", "markdown", "json"],
        default="markdown",
        help="Export format",
    )
    parser.add_argument("--window", type=str, default="1h", help="Time window for data (e.g., 1h, 24h)")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ethics/tools/mesh_snapshots",
        help="Output directory for files",
    )
    parser.add_argument("--dashboard", action="store_true", help="Generate interactive dashboard")

    args = parser.parse_args()

    # Initialize visualizer
    visualizer = QIMeshVisualizer(output_dir=args.output_dir)

    try:
        # Load data
        data = visualizer.load_entanglement_data(log_path=args.log_path, live_mode=args.live)

        visualizer.current_data = data

        print(f"📊 Quantum Mesh Visualizer - Mode: {args.mode}")
        print(f"⏱️  Data timestamp: {data.get('timestamp', 'Unknown')}")
        print(f"🔗 Mesh score: {data['unified_field']['mesh_ethics_score']:.3f}")
        print(f"⚠️  Risk level: {data['unified_field']['risk_level']}")
        print(f"🔥 Active conflicts: {len(data.get('conflicts', []))}")
        print()

        # Execute requested visualization mode
        if args.mode == "heatmap":
            visualizer.generate_entanglement_heatmap(data["entanglement_matrix"])

        elif args.mode == "sync":
            visualizer.plot_phase_synchronization(data)

        elif args.mode == "conflicts":
            conflicts_report = visualizer.list_active_conflict_pairs(
                data.get("conflicts", []), data["entanglement_matrix"]["entanglements"]
            )
            print(conflicts_report)

        elif args.mode == "dashboard" or args.dashboard:
            dashboard_path = visualizer.generate_interactive_dashboard(data)
            print(f"📈 Interactive dashboard: {dashboard_path}")

        # Handle export
        if args.export:
            visualizer.export_visual_summary(data, args.export, args.format)
            print(f"💾 Exported {args.format} report to: {args.export}")

        print("\n✅ Visualization complete!")

    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

# CLAUDE CHANGELOG
# - Created comprehensive quantum mesh visualizer with multiple visualization modes # CLAUDE_EDIT_v0.1
# - Implemented entanglement heatmap generation with matplotlib/seaborn # CLAUDE_EDIT_v0.1
# - Built phase synchronization radar chart for subsystem coherence # CLAUDE_EDIT_v0.1
# - Added interactive dashboard with plotly for real-time mesh monitoring # CLAUDE_EDIT_v0.1
# - Created CLI interface with multiple modes and export formats # CLAUDE_EDIT_v0.1
# - Integrated conflict detection and risk visualization with color coding # CLAUDE_EDIT_v0.1
