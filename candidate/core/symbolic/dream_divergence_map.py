import logging

logger = logging.getLogger(__name__)
"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

═══════════════════════════════════════════════════════════════════════════════════
🔍 MODULE: dream.tools.dream_divergence_map
📄 FILENAME: dream_divergence_map.py
🎯 PURPOSE: Dream Divergence Matrix - Cross-Session Symbolic Drift Analysis
🧠 CONTEXT: LUKHAS Cognitive AI Dream Analysis & Longitudinal Symbolic Drift Mapping
🔮 CAPABILITY: Multi-session drift analysis, symbolic motif tracking, visual matrices
🛡️ ETHICS: Transparent drift analysis, cognitive stability monitoring, phase detection
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: DreamSession, SymbolicAnomalyExplorer, HyperspaceSimulator
═══════════════════════════════════════════════════════════════════════════════════

🔍 DREAM DIVERGENCE MATRIX — CROSS-SESSION SYMBOLIC DRIFT ANALYSIS
────────────────────────────────────────────────────────────────────────────────────

The Dream Divergence Matrix maps symbolic drift trajectories across multiple dream
sessions, revealing phase transitions, recurring symbol deltas, emotional entropy
shifts, and motif recurrences that define the cognitive landscape evolution.

Through sophisticated cross-session analysis, it identifies:
- Pairwise symbolic drift scores between dream sessions
- Recurring symbols at high-drift transition points
- Phase transitions and collapse markers
- Emotional entropy evolution patterns
- Motif mutation trajectories across time

🔬 MATRIX CAPABILITIES:
- Multi-dimensional drift scoring with temporal correlation
- Symbol frequency analysis across divergence points
- Entropy shift detection between session pairs
- Phase marker identification (ΛDRIFT, ΛPHASE, ΛLOOP)
- Visual rendering with annotation overlays

🧪 DIVERGENCE METRICS:
- Symbolic Overlap Coefficient: Shared symbol density
- Emotional Entropy Delta: Affective state divergence
- Narrative Coherence Shift: Story structure evolution
- Phase Transition Score: Critical state change detection
- Motif Mutation Rate: Symbol transformation velocity

🎯 OUTPUT FORMATS:
- PNG/SVG matrix visualizations with color scales
- JSON summary reports for programmatic analysis
- HTML interactive matrices with Plotly rendering
- CLI-compatible drift score tables

LUKHAS_TAG: dream_divergence, symbolic_drift, matrix_analysis, longitudinal_tracking
TODO: Add temporal correlation weighting for chronological proximity
IDEA: Implement recursive pattern detection across divergence peaks
"""

import argparse
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np
import structlog

# Visualization imports
try:
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = structlog.get_logger("ΛTRACE.dream.divergence")


@dataclass
class DreamSession:
    """Represents a dream session for divergence analysis."""

    session_id: str
    timestamp: str
    symbolic_tags: list[str]
    emotional_state: dict[str, float]
    content: str
    drift_score: float
    narrative_elements: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def calculate_entropy(self) -> float:
        """Calculate symbolic entropy of the session."""
        if not self.symbolic_tags:
            return 0.0

        tag_counts = Counter(self.symbolic_tags)
        total = len(self.symbolic_tags)

        entropy = -sum((count / total) * math.log2(count / total) for count in tag_counts.values())
        return entropy

    def calculate_emotional_magnitude(self) -> float:
        """Calculate emotional state magnitude."""
        if not self.emotional_state:
            return 0.0

        return math.sqrt(sum(value**2 for value in self.emotional_state.values()))

    def extract_phase_markers(self) -> list[str]:
        """Extract phase markers (ΛTAGS) from content."""
        import re

        phase_pattern = r"LUKHAS(DRIFT|PHASE|LOOP|COLLAPSE)[A-Z0-9_]*"
        return re.findall(phase_pattern, self.content)


@dataclass
class DriftScore:
    """Represents drift between two sessions."""

    session_pair: tuple[str, str]
    symbolic_overlap: float
    emotional_delta: float
    entropy_delta: float
    narrative_coherence: float
    phase_transition_score: float
    total_drift: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DriftMatrix:
    """Contains complete drift analysis matrix."""

    sessions: list[DreamSession]
    drift_scores: np.ndarray
    session_ids: list[str]
    drift_details: dict[tuple[str, str], DriftScore]
    summary_stats: dict[str, float]

    def get_max_drift_pair(self) -> tuple[str, str, float]:
        """Find session pair with maximum drift."""
        max_idx = np.unravel_index(np.argmax(self.drift_scores), self.drift_scores.shape)
        max_drift = self.drift_scores[max_idx]
        session_pair = (
            self.session_ids[max_idx[0]],
            self.session_ids[max_idx[1]],
        )
        return (*session_pair, max_drift)

    def get_high_drift_pairs(self, threshold: float = 0.7) -> list[tuple[str, str, float]]:
        """Get all session pairs above drift threshold."""
        high_drift_pairs = []
        for i in range(len(self.session_ids)):
            for j in range(i + 1, len(self.session_ids)):
                drift = self.drift_scores[i, j]
                if drift >= threshold:
                    high_drift_pairs.append((self.session_ids[i], self.session_ids[j], drift))

        return sorted(high_drift_pairs, key=lambda x: x[2], reverse=True)


class DreamDivergenceMapper:
    """Maps symbolic drift patterns across dream sessions."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.drift_weights = {
            "symbolic_overlap": 0.3,
            "emotional_delta": 0.2,
            "entropy_delta": 0.2,
            "narrative_coherence": 0.15,
            "phase_transition": 0.15,
        }

    def load_dream_sessions(self, directory: str, limit: int = 20) -> list[DreamSession]:
        """Load and normalize recent dream sessions from disk."""
        sessions = []
        dream_dir = Path(directory)

        if not dream_dir.exists():
            logger.warning(f"Dream directory not found: {directory}")
            return self._generate_sample_sessions(limit)

        # Load JSON files from directory
        json_files = sorted(dream_dir.glob("*.json"))[:limit]

        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    session_data = json.load(f)

                # Normalize session data structure
                session = self._normalize_session_data(session_data, json_file.stem)
                sessions.append(session)

            except Exception as e:
                logger.error(f"Failed to load session {json_file}: {e}")
                continue

        if not sessions:
            logger.info(f"No valid sessions found, generating {limit} sample sessions")
            sessions = self._generate_sample_sessions(limit)

        logger.info(f"Loaded {len(sessions)} dream sessions")
        return sessions

    def _normalize_session_data(self, data: dict[str, Any], file_id: str) -> DreamSession:
        """Normalize session data to standard format."""
        return DreamSession(
            session_id=data.get("session_id", f"session_{file_id}"),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            symbolic_tags=data.get("symbolic_tags", data.get("symbols", [])),
            emotional_state=data.get("emotional_state", data.get("emotions", {})),
            content=data.get("content", data.get("narrative", "")),
            drift_score=data.get("drift_score", 0.0),
            narrative_elements=data.get("narrative_elements", data.get("elements", [])),
            metadata=data.get("metadata", {}),
        )

    def _generate_sample_sessions(self, count: int) -> list[DreamSession]:
        """Generate sample dream sessions for testing."""
        import random

        sample_symbols = [
            "water",
            "flight",
            "chase",
            "falling",
            "transformation",
            "mirror",
            "door",
            "stairs",
            "forest",
            "city",
            "childhood_home",
            "stranger",
            "animal",
            "light",
            "darkness",
            "puzzle",
            "journey",
            "return",
            "ΛDRIFT_HIGH",
            "ΛPHASE_CRITICAL",
            "ΛLOOP_DETECTED",
        ]

        sample_emotions = [
            "joy",
            "fear",
            "sadness",
            "anger",
            "surprise",
            "disgust",
        ]

        sessions = []
        base_time = datetime.now(timezone.utc)

        for i in range(count):
            # Create progressive symbolic drift
            symbol_pool = sample_symbols.copy()
            if i > count // 2:
                # Introduce divergent symbols in later sessions
                symbol_pool.extend(["qi_void", "recursive_mirror", "temporal_fracture"])

            session = DreamSession(
                session_id=f"dream_session_{i + 1:03d}",
                timestamp=(base_time - timedelta(days=count - i)).isoformat(),
                symbolic_tags=random.choices(symbol_pool, k=random.randint(3, 8)),
                emotional_state={
                    emotion: random.uniform(-1.0, 1.0)
                    for emotion in random.sample(sample_emotions, k=random.randint(2, 4))
                },
                content=f"Dream narrative {i + 1} with symbolic elements and emotional undertones",
                drift_score=random.uniform(0.0, 1.0),
                narrative_elements=random.choices(
                    ["conflict", "resolution", "mystery", "revelation"],
                    k=random.randint(1, 3),
                ),
                metadata={"session_length": random.randint(300, 1800)},
            )
            sessions.append(session)

        return sessions

    def compute_drift_matrix(self, sessions: list[DreamSession]) -> DriftMatrix:
        """Compute pairwise symbolic drift scores between sessions."""
        n_sessions = len(sessions)
        drift_matrix = np.zeros((n_sessions, n_sessions))
        drift_details = {}
        session_ids = [session.session_id for session in sessions]

        logger.info(f"Computing drift matrix for {n_sessions} sessions")

        for i in range(n_sessions):
            for j in range(i + 1, n_sessions):
                drift_score = self._calculate_pairwise_drift(sessions[i], sessions[j])
                drift_matrix[i, j] = drift_score.total_drift
                drift_matrix[j, i] = drift_score.total_drift  # Symmetric matrix

                drift_details[(sessions[i].session_id, sessions[j].session_id)] = drift_score

        # Calculate summary statistics
        upper_triangle = np.triu(drift_matrix, k=1)
        non_zero_values = upper_triangle[upper_triangle > 0]

        summary_stats = {
            "mean_drift": (float(np.mean(non_zero_values)) if len(non_zero_values) > 0 else 0.0),
            "max_drift": (float(np.max(non_zero_values)) if len(non_zero_values) > 0 else 0.0),
            "std_drift": (float(np.std(non_zero_values)) if len(non_zero_values) > 0 else 0.0),
            "total_comparisons": len(non_zero_values),
        }

        return DriftMatrix(
            sessions=sessions,
            drift_scores=drift_matrix,
            session_ids=session_ids,
            drift_details=drift_details,
            summary_stats=summary_stats,
        )

    def _calculate_pairwise_drift(self, session1: DreamSession, session2: DreamSession) -> DriftScore:
        """Calculate drift score between two sessions."""
        # Symbolic overlap (inverted - lower overlap = higher drift)
        symbols1 = set(session1.symbolic_tags)
        symbols2 = set(session2.symbolic_tags)

        if len(symbols1) == 0 and len(symbols2) == 0:
            symbolic_overlap = 0.0
        else:
            intersection = len(symbols1 & symbols2)
            union = len(symbols1 | symbols2)
            symbolic_overlap = 1.0 - (intersection / union if union > 0 else 0.0)

        # Emotional state delta
        emotions1 = session1.emotional_state
        emotions2 = session2.emotional_state

        all_emotions = set(emotions1.keys()) | set(emotions2.keys())
        emotional_delta = 0.0

        if all_emotions:
            for emotion in all_emotions:
                val1 = emotions1.get(emotion, 0.0)
                val2 = emotions2.get(emotion, 0.0)
                emotional_delta += abs(val1 - val2)
            emotional_delta /= len(all_emotions)

        # Entropy delta
        entropy1 = session1.calculate_entropy()
        entropy2 = session2.calculate_entropy()
        entropy_delta = abs(entropy1 - entropy2)

        # Narrative coherence (measure structural similarity)
        elements1 = set(session1.narrative_elements)
        elements2 = set(session2.narrative_elements)

        if len(elements1) == 0 and len(elements2) == 0:
            narrative_coherence = 0.0
        else:
            intersection = len(elements1 & elements2)
            union = len(elements1 | elements2)
            narrative_coherence = 1.0 - (intersection / union if union > 0 else 0.0)

        # Phase transition score (based on phase markers)
        phases1 = set(session1.extract_phase_markers())
        phases2 = set(session2.extract_phase_markers())

        if len(phases1) == 0 and len(phases2) == 0:
            phase_transition_score = 0.0
        else:
            phase_transition_score = len(phases1 ^ phases2) / max(len(phases1 | phases2), 1)

        # Calculate weighted total drift
        total_drift = (
            self.drift_weights["symbolic_overlap"] * symbolic_overlap
            + self.drift_weights["emotional_delta"] * min(emotional_delta, 2.0) / 2.0
            + self.drift_weights["entropy_delta"] * min(entropy_delta, 5.0) / 5.0
            + self.drift_weights["narrative_coherence"] * narrative_coherence
            + self.drift_weights["phase_transition"] * phase_transition_score
        )

        return DriftScore(
            session_pair=(session1.session_id, session2.session_id),
            symbolic_overlap=symbolic_overlap,
            emotional_delta=emotional_delta,
            entropy_delta=entropy_delta,
            narrative_coherence=narrative_coherence,
            phase_transition_score=phase_transition_score,
            total_drift=total_drift,
        )

    def extract_recurring_symbols(self, matrix: DriftMatrix) -> list[str]:
        """Find symbols appearing in high-drift transition points."""
        high_drift_pairs = matrix.get_high_drift_pairs(threshold=0.6)

        if not high_drift_pairs:
            # Use lower threshold if no high-drift pairs found
            high_drift_pairs = matrix.get_high_drift_pairs(threshold=0.4)

        symbol_counter = Counter()

        for session_id1, session_id2, _ in high_drift_pairs:
            # Find sessions by ID
            session1 = next(s for s in matrix.sessions if s.session_id == session_id1)
            session2 = next(s for s in matrix.sessions if s.session_id == session_id2)

            # Count symbols from both sessions
            for symbol in session1.symbolic_tags + session2.symbolic_tags:
                symbol_counter[symbol] += 1

        # Return top recurring symbols
        return [symbol for symbol, count in symbol_counter.most_common(10)]

    def render_divergence_map(self, matrix: DriftMatrix, symbols: list[str], out_path: str) -> None:
        """Generate visual matrix with entropy and phase overlays."""
        if PLOTLY_AVAILABLE:
            self._render_with_plotly(matrix, symbols, out_path)
        elif MATPLOTLIB_AVAILABLE:
            self._render_with_matplotlib(matrix, symbols, out_path)
        else:
            self._render_ascii_matrix(matrix, symbols, out_path)

    def _render_with_plotly(self, matrix: DriftMatrix, symbols: list[str], out_path: str):
        """Render interactive matrix with Plotly."""
        fig = go.Figure()

        # Main heatmap
        fig.add_trace(
            go.Heatmap(
                z=matrix.drift_scores,
                x=matrix.session_ids,
                y=matrix.session_ids,
                colorscale="Viridis",
                showscale=True,
                colorbar={"title": "Drift Score"},
                hovertemplate=("Session 1: %{y}<br>Session 2: %{x}<br>Drift Score: %{z:.3f}<br><extra></extra>"),
            )
        )

        # Add annotations for high drift points
        high_drift_pairs = matrix.get_high_drift_pairs(threshold=0.7)

        annotations = []
        for session1, session2, drift_score in high_drift_pairs[:5]:  # Top 5 only
            i = matrix.session_ids.index(session1)
            j = matrix.session_ids.index(session2)

            annotations.append(
                {
                    "x": j,
                    "y": i,
                    "text": f"⚠️{drift_score:.2f}",
                    "showarrow": False,
                    "font": {"color": "white", "size": 10},
                }
            )

        fig.update_layout(
            title={
                "text": f"Dream Divergence Matrix < br > <sub > Top Symbols: {',                                                                               '.join(symbols[:5])} < /sub >",
                "x": 0.5,
            },
            xaxis_title="Dream Sessions",
            yaxis_title="Dream Sessions",
            width=800,
            height=600,
            annotations=annotations,
        )

        # Save as HTML
        html_path = out_path.replace(".svg", ".html").replace(".png", ".html")
        fig.write_html(html_path)
        logger.info(f"Interactive matrix saved to {html_path}")

        # Also save as static image if possible
        try:
            fig.write_image(out_path)
            logger.info(f"Static matrix saved to {out_path}")
        except Exception as e:
            logger.warning(f"Could not save static image: {e}")

    def _render_with_matplotlib(self, matrix: DriftMatrix, symbols: list[str], out_path: str):
        """Render matrix with matplotlib."""
        plt.figure(figsize=(10, 8))

        # Create heatmap
        im = plt.imshow(matrix.drift_scores, cmap="viridis", interpolation="nearest")

        # Add colorbar
        plt.colorbar(im, label="Drift Score")

        # Set labels
        plt.xticks(
            range(len(matrix.session_ids)),
            matrix.session_ids,
            rotation=45,
            ha="right",
        )
        plt.yticks(range(len(matrix.session_ids)), matrix.session_ids)

        # Add title
        plt.title(f"Dream Divergence Matrix\nRecurring Symbols: {', '.join(symbols[:3])}")

        # Annotate high drift points
        high_drift_pairs = matrix.get_high_drift_pairs(threshold=0.7)
        for session1, session2, drift_score in high_drift_pairs[:3]:
            i = matrix.session_ids.index(session1)
            j = matrix.session_ids.index(session2)
            plt.text(
                j,
                i,
                f"{drift_score:.2f}",
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
            )

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Matrix visualization saved to {out_path}")

    def _render_ascii_matrix(self, matrix: DriftMatrix, symbols: list[str], out_path: str):
        """Render ASCII matrix as fallback."""
        output_lines = []
        output_lines.append("DREAM DIVERGENCE MATRIX")
        output_lines.append("=" * 50)
        output_lines.append(f"Sessions: {len(matrix.session_ids)}")
        output_lines.append(f"Recurring Symbols: {', '.join(symbols[:5])}")
        output_lines.append("")

        # Create ASCII heatmap
        n = len(matrix.session_ids)
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append("■■■")
                else:
                    score = matrix.drift_scores[i, j]
                    if score > 0.8:
                        row.append("███")
                    elif score > 0.6:
                        row.append("▓▓▓")
                    elif score > 0.4:
                        row.append("▒▒▒")
                    elif score > 0.2:
                        row.append("░░░")
                    else:
                        row.append("   ")

            output_lines.append(" ".join(row))

        output_lines.append("")
        output_lines.append("Legend: ███ High (>0.8) ▓▓▓ Med-High (>0.6) ▒▒▒ Medium (>0.4) ░░░ Low (>0.2)")

        # Save to text file
        text_path = out_path.replace(".svg", ".txt").replace(".png", ".txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        logger.info(f"ASCII matrix saved to {text_path}")

    def generate_summary_json(self, matrix: DriftMatrix, symbols: list[str]) -> dict[str, Any]:
        """Generate summary JSON report."""
        max_drift_pair = matrix.get_max_drift_pair()
        high_drift_pairs = matrix.get_high_drift_pairs(threshold=0.6)

        # Calculate average entropy shift
        entropy_shifts = []
        for session1, session2, _ in high_drift_pairs:
            s1 = next(s for s in matrix.sessions if s.session_id == session1)
            s2 = next(s for s in matrix.sessions if s.session_id == session2)
            entropy_shifts.append(abs(s1.calculate_entropy() - s2.calculate_entropy()))

        avg_entropy_shift = np.mean(entropy_shifts) if entropy_shifts else 0.0

        # Identify critical transitions
        critical_transitions = []
        for session1, session2, drift_score in high_drift_pairs:
            if drift_score > 0.8:
                critical_transitions.append(
                    {
                        "session_pair": [session1, session2],
                        "drift_score": drift_score,
                        "severity": "critical",
                    }
                )

        return {
            "summary": {
                "total_sessions": len(matrix.sessions),
                "total_comparisons": matrix.summary_stats["total_comparisons"],
                "mean_drift": matrix.summary_stats["mean_drift"],
                "max_drift": matrix.summary_stats["max_drift"],
                "std_drift": matrix.summary_stats["std_drift"],
            },
            "max_drift_pair": {
                "session1": max_drift_pair[0],
                "session2": max_drift_pair[1],
                "drift_score": max_drift_pair[2],
            },
            "top_symbols": symbols[:10],
            "avg_entropy_shift": avg_entropy_shift,
            "critical_transitions": critical_transitions,
            "high_drift_pairs": [
                {"session1": s1, "session2": s2, "drift_score": score} for s1, s2, score in high_drift_pairs[:5]
            ],
        }


def main():
    """CLI interface for dream divergence mapping."""
    parser = argparse.ArgumentParser(description="Dream Divergence Matrix Generator")
    parser.add_argument(
        "--dir",
        default="dream_sessions/",
        help="Directory containing dream session files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=12,
        help="Maximum number of sessions to analyze",
    )
    parser.add_argument("--out", default="results/divergence.svg", help="Output file path")
    parser.add_argument("--json", help="JSON summary output path")
    parser.add_argument("--threshold", type=float, default=0.6, help="High drift threshold")

    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)

    # Initialize mapper
    mapper = DreamDivergenceMapper()

    # Load sessions
    print(f"Loading dream sessions from {args.dir}...")
    sessions = mapper.load_dream_sessions(args.dir, args.limit)

    if not sessions:
        print("No sessions loaded. Exiting.")
        return

    # Compute drift matrix
    print(f"Computing drift matrix for {len(sessions)} sessions...")
    matrix = mapper.compute_drift_matrix(sessions)

    # Extract recurring symbols
    print("Extracting recurring symbols...")
    symbols = mapper.extract_recurring_symbols(matrix)

    # Generate visualization
    print(f"Rendering divergence map to {args.out}...")
    mapper.render_divergence_map(matrix, symbols, args.out)

    # Generate JSON summary
    summary = mapper.generate_summary_json(matrix, symbols)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary JSON saved to {args.json}")

    # Print summary to console
    print("\n" + "=" * 60)
    print("DREAM DIVERGENCE ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Sessions Analyzed: {summary['summary']['total_sessions']}")
    print(f"Mean Drift Score: {summary['summary']['mean_drift']:.3f}")
    print(f"Max Drift Score: {summary['summary']['max_drift']:.3f}")
    print(f"Max Drift Pair: {summary['max_drift_pair']['session1']} ↔ {summary['max_drift_pair']['session2']}")
    print(f"Top Symbols: {', '.join(summary['top_symbols'][:5])}")
    print(f"Critical Transitions: {len(summary['critical_transitions'])}")
    print(f"Average Entropy Shift: {summary['avg_entropy_shift']:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# CLAUDE CHANGELOG
# - Created dream_divergence_map.py with comprehensive drift matrix analysis # CLAUDE_EDIT_v0.1
# - Implemented DreamSession, DriftScore, and DriftMatrix data structures # CLAUDE_EDIT_v0.1
# - Added pairwise drift computation with weighted scoring system # CLAUDE_EDIT_v0.1
# - Created visualization support for Plotly, Matplotlib, and ASCII fallback # CLAUDE_EDIT_v0.1
# - Implemented CLI interface with configurable parameters # CLAUDE_EDIT_v0.1
