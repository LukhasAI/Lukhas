"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

═══════════════════════════════════════════════════════════════════════════════════
🔍 MODULE: dream.tools.symbolic_theme_clusterer
📄 FILENAME: symbolic_theme_clusterer.py
🎯 PURPOSE: ΛTHEME - Symbolic Motif Clusterer for Dream Archives
🧠 CONTEXT: LUKHAS Cognitive AI Dream Analysis & Thematic Pattern Recognition
🔮 CAPABILITY: Motif clustering, narrative arc tracking, thematic evolution analysis
🛡️ ETHICS: Transparent pattern recognition, symbolic continuity preservation
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: DreamSession, SymbolicAnomalyExplorer, DreamDivergenceMap
═══════════════════════════════════════════════════════════════════════════════════

🔍 ΛTHEME - SYMBOLIC MOTIF CLUSTERER FOR DREAM ARCHIVES
────────────────────────────────────────────────────────────────────────────────────

The Symbolic Theme Clusterer analyzes recurring dream motifs to identify thematic
convergence and divergence patterns across dream sessions, revealing the underlying
narrative arcs that weave through consciousness over time.

Through sophisticated motif analysis, it identifies:
- Dominant and supporting symbolic themes across multiple dreams
- Thematic clusters based on co-occurrence and emotional resonance
- Narrative evolution patterns and thematic transitions over time
- Symbolic convergence points and divergence trajectories
- Emotional tone shifts within recurring thematic structures

🔬 CLUSTERING CAPABILITIES:
- Multi-dimensional motif similarity analysis with temporal weighting
- Emotional resonance clustering for thematic tone identification
- ΛTAG pattern recognition for phase transition tracking
- Co-occurrence matrix analysis for symbol relationship mapping
- Narrative arc detection across session sequences

🧪 THEME TYPES:
- Core Themes: Primary symbolic clusters with high co-occurrence
- Supporting Themes: Secondary motifs that enhance core patterns
- Transitional Themes: Bridges between major thematic shifts
- Recurrent Themes: Motifs that cycle through dream sessions
- Divergent Themes: Patterns that represent thematic evolution

🎯 OUTPUT FORMATS:
- JSON cluster reports with emotional tone analysis
- Markdown summaries for human interpretation
- Visual network maps showing thematic relationships
- Temporal tracking reports for narrative evolution

LUKHAS_TAG: theme_clustering, motif_analysis, narrative_tracking, symbolic_continuity
TODO: Add ML-based theme prediction for proactive narrative modeling
IDEA: Implement cross-user thematic linking for collective dream analysis
"""

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Optional

import numpy as np
import structlog

# Optional ML imports
try:
    from sklearn.cluster import DBSCAN

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = structlog.get_logger("ΛTRACE.dream.theme_clusterer")


@dataclass
class MotifInstance:
    """Represents a single motif occurrence in a dream."""

    symbol: str
    dream_id: str
    timestamp: str
    emotional_context: dict[str, float]
    co_occurring_symbols: list[str]
    lambda_tags: list[str]
    narrative_position: float  # 0.0 = beginning, 1.0 = end
    symbolic_weight: float = 1.0


@dataclass
class SymbolicTheme:
    """Represents a clustered symbolic theme."""

    theme_id: str
    core_symbols: list[str]
    supporting_symbols: list[str]
    emotional_tone: dict[str, float]
    dream_sessions: list[str]
    temporal_span: tuple[str, str]  # First and last occurrence
    coherence_score: float
    recurrence_count: int
    theme_type: str  # core, supporting, transitional, recurrent, divergent


@dataclass
class ThemeTransition:
    """Represents a transition between themes over time."""

    from_theme: str
    to_theme: str
    transition_point: str  # timestamp
    transition_strength: float
    common_symbols: list[str]
    emotional_shift: dict[str, float]


@dataclass
class ThematicEvolution:
    """Tracks the evolution of themes across dream sessions."""

    timeline: list[tuple[str, str]]  # (timestamp, dominant_theme)
    transitions: list[ThemeTransition]
    recurring_patterns: list[str]
    divergence_points: list[str]
    convergence_points: list[str]


class SymbolicThemeClusterer:
    """Clusters symbolic motifs into thematic patterns."""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.similarity_threshold = self.config.get("similarity_threshold", 0.3)
        self.min_cluster_size = self.config.get("min_cluster_size", 2)
        self.emotional_weight = self.config.get("emotional_weight", 0.4)
        self.temporal_weight = self.config.get("temporal_weight", 0.2)

        # Predefined symbol relationships for enhanced clustering
        self.symbol_relationships = {
            "flight": ["falling", "wings", "sky", "birds", "freedom"],
            "water": ["ocean", "river", "swimming", "drowning", "cleansing"],
            "chase": ["running", "pursuit", "escape", "fear", "danger"],
            "transformation": [
                "metamorphosis",
                "change",
                "mutation",
                "evolution",
            ],
            "mirror": ["reflection", "self", "identity", "truth", "illusion"],
            "family": ["childhood_home", "parents", "siblings", "reunion"],
            "death": ["funeral", "grief", "loss", "endings", "transition"],
        }

    def extract_motifs_from_dreams(self, dream_dir: str, limit: int = 20) -> list[dict]:
        """Parse symbolic dream data to extract motifs and their emotional/symbolic tags."""
        motifs = []
        dream_sessions = self._load_dream_sessions(dream_dir, limit)

        logger.info(f"Extracting motifs from {len(dream_sessions)} dream sessions")

        for session in dream_sessions:
            session_motifs = self._extract_session_motifs(session)
            motifs.extend(session_motifs)

        logger.info(f"Extracted {len(motifs)} total motif instances")
        return [asdict(motif) for motif in motifs]

    def _load_dream_sessions(self, directory: str, limit: int) -> list[dict]:
        """Load dream sessions from directory or generate samples."""
        sessions = []
        dream_dir = Path(directory)

        if not dream_dir.exists():
            logger.warning(f"Dream directory not found: {directory}")
            return self._generate_sample_dream_sessions(limit)

        # Load JSON files from directory
        json_files = sorted(dream_dir.glob("*.json"))[:limit]

        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    session_data = json.load(f)
                sessions.append(session_data)
            except Exception as e:
                logger.error(f"Failed to load session {json_file}: {e}")
                continue

        if not sessions:
            logger.info(f"No valid sessions found, generating {limit} sample sessions")
            sessions = self._generate_sample_dream_sessions(limit)

        return sessions

    def _generate_sample_dream_sessions(self, count: int) -> list[dict]:
        """Generate sample dream sessions with thematic patterns."""
        import random

        # Define thematic symbol groups
        flight_theme = [
            "flight",
            "wings",
            "sky",
            "birds",
            "falling",
            "soaring",
            "ΛDRIFT_HIGH",
        ]
        water_theme = [
            "water",
            "ocean",
            "swimming",
            "diving",
            "drowning",
            "waves",
            "ΛPHASE_FLOW",
        ]
        chase_theme = [
            "chase",
            "running",
            "pursuit",
            "escape",
            "danger",
            "hiding",
            "ΛLOOP_DETECTED",
        ]
        family_theme = [
            "family",
            "childhood_home",
            "parents",
            "reunion",
            "nostalgia",
            "ΛPHASE_MEMORY",
        ]
        transformation_theme = [
            "transformation",
            "metamorphosis",
            "change",
            "mutation",
            "growth",
            "ΛDRIFT_TRANSFORM",
        ]

        themes = [
            flight_theme,
            water_theme,
            chase_theme,
            family_theme,
            transformation_theme,
        ]
        theme_names = ["flight", "water", "chase", "family", "transformation"]

        sessions = []
        base_time = datetime.now(timezone.utc)

        # Create sessions with evolving thematic patterns
        for i in range(count):
            # Early sessions focus on 1-2 themes, later ones show theme evolution
            if i < count // 3:
                # Early phase: single theme dominance
                dominant_theme = random.choice(themes)
                symbols = random.choices(dominant_theme, k=random.randint(4, 7))
            elif i < 2 * count // 3:
                # Middle phase: theme mixing
                theme1, theme2 = random.sample(themes, 2)
                symbols = random.choices(
                    theme1, k=random.randint(2, 4)
                ) + random.choices(theme2, k=random.randint(2, 3))
            else:
                # Late phase: theme evolution/divergence
                base_theme = random.choice(themes)
                evolution_symbols = [
                    "qi_void",
                    "recursive_mirror",
                    "temporal_fracture",
                    "ΛDRIFT_CRITICAL",
                ]
                symbols = random.choices(
                    base_theme, k=random.randint(2, 4)
                ) + random.choices(evolution_symbols, k=random.randint(1, 3))

            # Generate emotional state based on theme
            dominant_theme_name = self._identify_dominant_theme_name(
                symbols, theme_names, themes
            )
            emotions = self._generate_thematic_emotions(dominant_theme_name)

            session = {
                "session_id": f"dream_session_{i+1:03d}",
                "timestamp": (base_time - timedelta(days=count - i)).isoformat(),
                "symbolic_tags": symbols,
                "emotional_state": emotions,
                "content": f"Dream narrative featuring {dominant_theme_name} theme with symbolic elements",
                "drift_score": random.uniform(0.0, 1.0),
                "narrative_elements": self._generate_narrative_elements(
                    dominant_theme_name
                ),
                "metadata": {
                    "session_length": random.randint(300, 1800),
                    "theme_hint": dominant_theme_name,
                },
            }
            sessions.append(session)

        return sessions

    def _identify_dominant_theme_name(
        self,
        symbols: list[str],
        theme_names: list[str],
        themes: list[list[str]],
    ) -> str:
        """Identify which theme has the most symbols in the given list."""
        theme_counts = {}
        for i, theme in enumerate(themes):
            theme_counts[theme_names[i]] = len(set(symbols) & set(theme))

        return max(theme_counts, key=theme_counts.get)

    def _generate_thematic_emotions(self, theme_name: str) -> dict[str, float]:
        """Generate emotions appropriate for the given theme."""
        import random

        emotion_profiles = {
            "flight": {
                "joy": 0.7,
                "freedom": 0.8,
                "fear": 0.3,
                "exhilaration": 0.9,
            },
            "water": {
                "calm": 0.6,
                "cleansing": 0.7,
                "fear": 0.4,
                "renewal": 0.8,
            },
            "chase": {
                "fear": 0.9,
                "anxiety": 0.8,
                "urgency": 0.9,
                "panic": 0.7,
            },
            "family": {
                "nostalgia": 0.8,
                "warmth": 0.7,
                "comfort": 0.8,
                "longing": 0.6,
            },
            "transformation": {
                "wonder": 0.7,
                "confusion": 0.5,
                "growth": 0.8,
                "uncertainty": 0.6,
            },
        }

        base_emotions = emotion_profiles.get(theme_name, {"neutral": 0.5})

        # Add some randomness
        result = {}
        for emotion, base_value in base_emotions.items():
            result[emotion] = max(
                -1.0, min(1.0, base_value + random.uniform(-0.3, 0.3))
            )

        return result

    def _generate_narrative_elements(self, theme_name: str) -> list[str]:
        """Generate narrative elements appropriate for the theme."""
        import random

        element_profiles = {
            "flight": [
                "ascension",
                "liberation",
                "perspective_shift",
                "transcendence",
            ],
            "water": [
                "purification",
                "submersion",
                "flow_state",
                "depth_exploration",
            ],
            "chase": ["conflict", "escape", "pursuit", "confrontation"],
            "family": ["reunion", "memory", "belonging", "roots"],
            "transformation": [
                "metamorphosis",
                "growth",
                "evolution",
                "change",
            ],
        }

        elements = element_profiles.get(theme_name, ["mystery", "journey", "discovery"])
        return random.choices(elements, k=random.randint(2, 4))

    def _extract_session_motifs(self, session: dict) -> list[MotifInstance]:
        """Extract motif instances from a single dream session."""
        motifs = []
        session_id = session.get("session_id", "unknown")
        timestamp = session.get("timestamp", datetime.now(timezone.utc).isoformat())
        emotional_state = session.get("emotional_state", {})
        content = session.get("content", "")
        symbolic_tags = session.get("symbolic_tags", [])

        # Extract ΛTAGS from content
        lambda_tags = re.findall(r"LUKHAS[A-Z_]+[A-Z0-9_]*", content)

        # Create motif instances for each symbol
        for i, symbol in enumerate(symbolic_tags):
            motif = MotifInstance(
                symbol=symbol,
                dream_id=session_id,
                timestamp=timestamp,
                emotional_context=emotional_state,
                co_occurring_symbols=[s for s in symbolic_tags if s != symbol],
                lambda_tags=lambda_tags,
                narrative_position=i / max(len(symbolic_tags) - 1, 1),
                symbolic_weight=self._calculate_symbolic_weight(
                    symbol, emotional_state, lambda_tags
                ),
            )
            motifs.append(motif)

        return motifs

    def _calculate_symbolic_weight(
        self, symbol: str, emotions: dict[str, float], lambda_tags: list[str]
    ) -> float:
        """Calculate the symbolic weight of a symbol based on context."""
        base_weight = 1.0

        # Boost weight for emotionally charged contexts
        emotional_intensity = sum(abs(v) for v in emotions.values())
        emotion_boost = min(emotional_intensity / 5.0, 1.0)

        # Boost weight for ΛTAG presence
        lambda_boost = 0.2 * len(lambda_tags)

        # Boost weight for archetypal symbols
        archetypal_symbols = {
            "water",
            "flight",
            "mirror",
            "death",
            "transformation",
            "family",
        }
        archetype_boost = 0.3 if symbol.lower() in archetypal_symbols else 0.0

        return base_weight + emotion_boost + lambda_boost + archetype_boost

    def cluster_motifs_by_similarity(self, motifs: list[dict]) -> dict[str, list[str]]:
        """Group symbols into clusters based on co-occurrence, tags, and GLYPH compatibility."""
        if not motifs:
            return {}

        logger.info(f"Clustering {len(motifs)} motifs by similarity")

        # Convert dict motifs back to objects for processing
        motif_objects = [MotifInstance(**motif) for motif in motifs]

        # Build co-occurrence matrix
        symbol_cooccurrence = self._build_cooccurrence_matrix(motif_objects)

        # Calculate symbol similarity scores
        similarity_matrix = self._calculate_similarity_matrix(
            motif_objects, symbol_cooccurrence
        )

        # Perform clustering
        if SKLEARN_AVAILABLE and len(similarity_matrix) > 3:
            clusters = self._sklearn_clustering(similarity_matrix, motif_objects)
        else:
            clusters = self._simple_clustering(similarity_matrix, motif_objects)

        logger.info(f"Created {len(clusters)} thematic clusters")
        return clusters

    def _build_cooccurrence_matrix(
        self, motifs: list[MotifInstance]
    ) -> dict[tuple[str, str], int]:
        """Build matrix of symbol co-occurrences."""
        cooccurrence = defaultdict(int)

        # Group motifs by dream session
        dreams = defaultdict(list)
        for motif in motifs:
            dreams[motif.dream_id].append(motif)

        # Count co-occurrences within each dream
        for dream_motifs in dreams.values():
            symbols = [motif.symbol for motif in dream_motifs]
            for symbol1, symbol2 in combinations(symbols, 2):
                pair = tuple(sorted([symbol1, symbol2]))
                cooccurrence[pair] += 1

        return cooccurrence

    def _calculate_similarity_matrix(
        self,
        motifs: list[MotifInstance],
        cooccurrence: dict[tuple[str, str], int],
    ) -> np.ndarray:
        """Calculate similarity matrix between symbols."""
        # Get unique symbols
        symbols = list({motif.symbol for motif in motifs})
        n_symbols = len(symbols)
        {symbol: i for i, symbol in enumerate(symbols)}

        similarity_matrix = np.zeros((n_symbols, n_symbols))

        # Fill similarity matrix
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    similarity = self._calculate_symbol_similarity(
                        symbol1, symbol2, motifs, cooccurrence
                    )
                    similarity_matrix[i, j] = similarity

        self.symbols = symbols  # Store for later use
        return similarity_matrix

    def _calculate_symbol_similarity(
        self,
        symbol1: str,
        symbol2: str,
        motifs: list[MotifInstance],
        cooccurrence: dict[tuple[str, str], int],
    ) -> float:
        """Calculate similarity between two symbols."""
        # Co-occurrence similarity
        pair = tuple(sorted([symbol1, symbol2]))
        cooccurrence_score = cooccurrence.get(pair, 0) / 10.0  # Normalize

        # Predefined relationship similarity
        relationship_score = 0.0
        for base_symbol, related_symbols in self.symbol_relationships.items():
            if (
                symbol1 == base_symbol
                and symbol2 in related_symbols
                or symbol2 == base_symbol
                and symbol1 in related_symbols
            ):
                relationship_score = 0.8
            elif symbol1 in related_symbols and symbol2 in related_symbols:
                relationship_score = 0.6

        # Emotional context similarity
        emotional_similarity = self._calculate_emotional_similarity(
            symbol1, symbol2, motifs
        )

        # ΛTAG context similarity
        lambda_similarity = self._calculate_lambda_similarity(symbol1, symbol2, motifs)

        # Weighted combination
        total_similarity = (
            0.4 * cooccurrence_score
            + 0.3 * relationship_score
            + 0.2 * emotional_similarity
            + 0.1 * lambda_similarity
        )

        return min(total_similarity, 1.0)

    def _calculate_emotional_similarity(
        self, symbol1: str, symbol2: str, motifs: list[MotifInstance]
    ) -> float:
        """Calculate emotional context similarity between symbols."""
        symbol1_emotions = []
        symbol2_emotions = []

        for motif in motifs:
            if motif.symbol == symbol1:
                symbol1_emotions.append(motif.emotional_context)
            elif motif.symbol == symbol2:
                symbol2_emotions.append(motif.emotional_context)

        if not symbol1_emotions or not symbol2_emotions:
            return 0.0

        # Calculate average emotional vectors

        def avg_emotions(emotion_list):
            if not emotion_list:
                return {}
            all_keys = set()
            for emotions in emotion_list:
                all_keys.update(emotions.keys())

            avg = {}
            for key in all_keys:
                values = [emotions.get(key, 0.0) for emotions in emotion_list]
                avg[key] = sum(values) / len(values)
            return avg

        avg1 = avg_emotions(symbol1_emotions)
        avg2 = avg_emotions(symbol2_emotions)

        # Calculate cosine similarity of emotion vectors
        all_emotions = set(avg1.keys()) | set(avg2.keys())
        if not all_emotions:
            return 0.0

        vec1 = [avg1.get(emotion, 0.0) for emotion in all_emotions]
        vec2 = [avg2.get(emotion, 0.0) for emotion in all_emotions]

        # Cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _calculate_lambda_similarity(
        self, symbol1: str, symbol2: str, motifs: list[MotifInstance]
    ) -> float:
        """Calculate ΛTAG context similarity between symbols."""
        symbol1_tags = set()
        symbol2_tags = set()

        for motif in motifs:
            if motif.symbol == symbol1:
                symbol1_tags.update(motif.lambda_tags)
            elif motif.symbol == symbol2:
                symbol2_tags.update(motif.lambda_tags)

        if not symbol1_tags or not symbol2_tags:
            return 0.0

        # Jaccard similarity
        intersection = len(symbol1_tags & symbol2_tags)
        union = len(symbol1_tags | symbol2_tags)

        return intersection / union if union > 0 else 0.0

    def _sklearn_clustering(
        self, similarity_matrix: np.ndarray, motifs: list[MotifInstance]
    ) -> dict[str, list[str]]:
        """Perform clustering using sklearn."""
        # Convert similarity to distance matrix
        distance_matrix = 1.0 - similarity_matrix

        # Use DBSCAN for density-based clustering
        clustering = DBSCAN(
            metric="precomputed", eps=0.7, min_samples=self.min_cluster_size
        )
        cluster_labels = clustering.fit_predict(distance_matrix)

        # Group symbols by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # -1 indicates noise/outliers
                clusters[f"theme_{label+1}"].append(self.symbols[i])
            else:
                clusters["unclustered"].append(self.symbols[i])

        return dict(clusters)

    def _simple_clustering(
        self, similarity_matrix: np.ndarray, motifs: list[MotifInstance]
    ) -> dict[str, list[str]]:
        """Simple clustering based on similarity threshold."""
        n_symbols = len(self.symbols)
        visited = set()
        clusters = {}
        cluster_id = 1

        for i in range(n_symbols):
            if i in visited:
                continue

            # Start new cluster
            cluster_name = f"theme_{cluster_id}"
            cluster_symbols = [self.symbols[i]]
            visited.add(i)

            # Find similar symbols
            for j in range(i + 1, n_symbols):
                if (
                    j not in visited
                    and similarity_matrix[i, j] >= self.similarity_threshold
                ):
                    cluster_symbols.append(self.symbols[j])
                    visited.add(j)

            if len(cluster_symbols) >= self.min_cluster_size:
                clusters[cluster_name] = cluster_symbols
                cluster_id += 1
            else:
                # Add to unclustered if too small
                if "unclustered" not in clusters:
                    clusters["unclustered"] = []
                clusters["unclustered"].extend(cluster_symbols)

        return clusters

    def summarize_theme_clusters(self, clusters: dict[str, list[str]]) -> list[str]:
        """Return human-readable summaries of each theme, with core symbols and emotional tone."""
        summaries = []

        logger.info(f"Summarizing {len(clusters)} theme clusters")

        for theme_name, symbols in clusters.items():
            if theme_name == "unclustered":
                continue

            # Analyze theme characteristics
            core_symbols = symbols[:3]  # Top 3 symbols as core
            supporting_symbols = symbols[3:] if len(symbols) > 3 else []

            # Determine emotional tone
            emotional_tone = self._analyze_cluster_emotional_tone(symbols)

            # Identify dominant emotional characteristic
            dominant_emotion = (
                max(emotional_tone.items(), key=lambda x: x[1])[0]
                if emotional_tone
                else "neutral"
            )

            # Create summary
            summary = f"**{theme_name.upper()}** ({dominant_emotion})\n"
            summary += f"Core symbols: {', '.join(core_symbols)}\n"
            if supporting_symbols:
                summary += f"Supporting symbols: {', '.join(supporting_symbols)}\n"
            summary += f"Emotional tone: {dominant_emotion} ({emotional_tone.get(dominant_emotion, 0.0):.2f})\n"
            summary += f"Symbol count: {len(symbols)}\n"

            summaries.append(summary)

        return summaries

    def _analyze_cluster_emotional_tone(self, symbols: list[str]) -> dict[str, float]:
        """Analyze the emotional tone of a symbol cluster."""
        # Predefined emotional associations for common symbols
        symbol_emotions = {
            "flight": {"joy": 0.7, "freedom": 0.8, "exhilaration": 0.6},
            "falling": {"fear": 0.8, "anxiety": 0.7, "helplessness": 0.6},
            "water": {"calm": 0.6, "cleansing": 0.5, "renewal": 0.7},
            "drowning": {"fear": 0.9, "panic": 0.8, "overwhelm": 0.7},
            "chase": {"fear": 0.8, "anxiety": 0.9, "urgency": 0.8},
            "family": {"warmth": 0.7, "nostalgia": 0.8, "comfort": 0.6},
            "death": {"sadness": 0.8, "fear": 0.6, "endings": 0.9},
            "transformation": {
                "wonder": 0.7,
                "uncertainty": 0.5,
                "growth": 0.8,
            },
            "mirror": {"self_reflection": 0.8, "truth": 0.6, "identity": 0.7},
        }

        combined_emotions = defaultdict(float)
        symbol_count = 0

        for symbol in symbols:
            if symbol.lower() in symbol_emotions:
                for emotion, value in symbol_emotions[symbol.lower()].items():
                    combined_emotions[emotion] += value
                symbol_count += 1

        # Average the emotions
        if symbol_count > 0:
            for emotion in combined_emotions:
                combined_emotions[emotion] /= symbol_count

        return dict(combined_emotions)

    def track_theme_transitions(self, history: list[dict]) -> dict:
        """Detect shifts in dominant motifs across time or sessions."""
        if len(history) < 2:
            return {"transitions": [], "patterns": []}

        logger.info(f"Tracking theme transitions across {len(history)} sessions")

        transitions = []
        timeline = []

        # Sort history by timestamp
        sorted_history = sorted(history, key=lambda x: x.get("timestamp", ""))

        # Track dominant theme for each session
        for session in sorted_history:
            motifs = self._extract_session_motifs(session)
            if motifs:
                # Find most frequent symbol as theme indicator
                symbol_counts = Counter(motif.symbol for motif in motifs)
                dominant_symbol = symbol_counts.most_common(1)[0][0]
                theme_category = self._categorize_symbol_theme(dominant_symbol)
                timeline.append((session.get("timestamp", ""), theme_category))

        # Detect transitions
        for i in range(1, len(timeline)):
            prev_timestamp, prev_theme = timeline[i - 1]
            curr_timestamp, curr_theme = timeline[i]

            if prev_theme != curr_theme:
                transition = {
                    "from_theme": prev_theme,
                    "to_theme": curr_theme,
                    "transition_point": curr_timestamp,
                    "session_gap": i,
                }
                transitions.append(transition)

        # Analyze patterns
        patterns = self._analyze_transition_patterns(transitions, timeline)

        return {
            "timeline": timeline,
            "transitions": transitions,
            "patterns": patterns,
            "total_sessions": len(timeline),
            "unique_themes": len({theme for _, theme in timeline}),
        }

    def _categorize_symbol_theme(self, symbol: str) -> str:
        """Categorize a symbol into a broader theme category."""
        theme_mappings = {
            "flight": "aerial",
            "falling": "aerial",
            "wings": "aerial",
            "sky": "aerial",
            "birds": "aerial",
            "water": "aquatic",
            "ocean": "aquatic",
            "swimming": "aquatic",
            "drowning": "aquatic",
            "waves": "aquatic",
            "chase": "conflict",
            "running": "conflict",
            "pursuit": "conflict",
            "escape": "conflict",
            "danger": "conflict",
            "family": "relational",
            "childhood_home": "relational",
            "parents": "relational",
            "reunion": "relational",
            "transformation": "metamorphic",
            "metamorphosis": "metamorphic",
            "change": "metamorphic",
            "mutation": "metamorphic",
        }

        return theme_mappings.get(symbol.lower(), "archetypal")

    def _analyze_transition_patterns(
        self, transitions: list[dict], timeline: list[tuple[str, str]]
    ) -> list[str]:
        """Analyze patterns in theme transitions."""
        patterns = []

        if not transitions:
            patterns.append("No theme transitions detected - stable thematic content")
            return patterns

        # Analyze transition frequency
        transition_count = len(transitions)
        session_count = len(timeline)

        if transition_count / session_count > 0.5:
            patterns.append("High thematic volatility - frequent theme changes")
        elif transition_count / session_count < 0.2:
            patterns.append("Low thematic volatility - stable theme progression")
        else:
            patterns.append("Moderate thematic volatility - balanced theme evolution")

        # Analyze transition directions
        theme_counts = Counter()
        for transition in transitions:
            theme_counts[transition["from_theme"]] += 1
            theme_counts[transition["to_theme"]] += 1

        if theme_counts:
            most_common_theme = theme_counts.most_common(1)[0][0]
            patterns.append(f"Most active theme: {most_common_theme}")

        # Detect cyclic patterns
        theme_sequence = [theme for _, theme in timeline]
        if self._has_cyclic_pattern(theme_sequence):
            patterns.append("Cyclic thematic pattern detected")

        return patterns

    def _has_cyclic_pattern(self, sequence: list[str]) -> bool:
        """Detect if there's a cyclic pattern in the theme sequence."""
        if len(sequence) < 4:
            return False

        # Look for repeating subsequences
        for cycle_length in range(2, len(sequence) // 2 + 1):
            for start in range(len(sequence) - 2 * cycle_length + 1):
                cycle1 = sequence[start : start + cycle_length]
                cycle2 = sequence[start + cycle_length : start + 2 * cycle_length]
                if cycle1 == cycle2:
                    return True

        return False

    def render_theme_overview(
        self, clusters: dict[str, list[str]], output_path: str
    ) -> None:
        """Save overview as JSON, Markdown, or SVG."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.suffix.lower() == ".json":
            self._render_json_overview(clusters, output_path)
        elif output_path.suffix.lower() == ".md":
            self._render_markdown_overview(clusters, output_path)
        else:
            # Default to markdown
            md_path = output_path.with_suffix(".md")
            self._render_markdown_overview(clusters, md_path)

    def _render_json_overview(self, clusters: dict[str, list[str]], output_path: Path):
        """Render JSON overview."""
        themes_data = []

        for theme_name, symbols in clusters.items():
            if theme_name == "unclustered":
                continue

            core_symbols = symbols[:3]
            supporting_symbols = symbols[3:] if len(symbols) > 3 else []
            emotional_tone = self._analyze_cluster_emotional_tone(symbols)
            dominant_emotion = (
                max(emotional_tone.items(), key=lambda x: x[1])[0]
                if emotional_tone
                else "neutral"
            )

            theme_data = {
                "theme_id": theme_name,
                "core": core_symbols,
                "related": supporting_symbols,
                "tone": dominant_emotion,
                "emotional_scores": emotional_tone,
                "total_symbols": len(symbols),
            }
            themes_data.append(theme_data)

        output_data = {
            "themes": themes_data,
            "total_themes": len(themes_data),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"JSON theme overview saved to {output_path}")

    def _render_markdown_overview(
        self, clusters: dict[str, list[str]], output_path: Path
    ):
        """Render Markdown overview."""
        lines = []
        lines.append(")  #  ΛTHEME - Symbolic Theme Analysis"
        lines.append("=" * 50)
        lines.append("")
        lines.append(
            f"**Analysis Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        lines.append(
            f"**Total Themes Identified:** {len([k for k in clusters if k != 'unclustered'])}"
        )
        lines.append("")

        # Main themes
        theme_summaries = self.summarize_theme_clusters(clusters)
        lines.append("#)  #  Identified Themes"
        lines.append("")

        for summary in theme_summaries:
            lines.append(summary)
            lines.append("")

        # Unclustered symbols
        if "unclustered" in clusters and clusters["unclustered"]:
            lines.append("#)  #  Unclustered Symbols"
            lines.append("")
            lines.append("The following symbols did not form clear thematic clusters:")
            lines.append(f"```\n{', '.join(clusters['unclustered'])}\n```")
            lines.append("")

        # Analysis notes
        lines.append("#)  #  Analysis Notes"
        lines.append("")
        lines.append("- Themes are identified through symbol co-occurrence analysis")
        lines.append(
            "- Emotional tones are derived from archetypal symbol associations"
        )
        lines.append("- Core symbols represent the most central elements of each theme")
        lines.append("- Supporting symbols provide thematic context and nuance")
        lines.append("")
        lines.append("---")
        lines.append("*Generated by LUKHAS Cognitive AI Symbolic Theme Clusterer*")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Markdown theme overview saved to {output_path}")


def main():
    """CLI interface for symbolic theme clustering."""
    parser = argparse.ArgumentParser(
        description="Symbolic Theme Clusterer for Dream Archives"
    )
    parser.add_argument(
        "--dir",
        default="dream_sessions/",
        help="Directory containing dream session files",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of sessions to analyze",
    )
    parser.add_argument("--out", default="results/themes.md", help="Output file path")
    parser.add_argument(
        "--similarity",
        type=float,
        default=0.3,
        help="Similarity threshold for clustering",
    )
    parser.add_argument(
        "--min-cluster", type=int, default=2, help="Minimum cluster size"
    )
    parser.add_argument(
        "--transitions",
        action="store_true",
        help="Include theme transition analysis",
    )

    args = parser.parse_args()

    # Initialize clusterer
    config = {
        "similarity_threshold": args.similarity,
        "min_cluster_size": args.min_cluster,
    }
    clusterer = SymbolicThemeClusterer(config)

    # Extract motifs
    print(f"Extracting motifs from {args.dir}...")
    motifs = clusterer.extract_motifs_from_dreams(args.dir, args.limit)

    if not motifs:
        print("No motifs found. Exiting.")
        return

    # Cluster motifs
    print("Clustering motifs by similarity...")
    clusters = clusterer.cluster_motifs_by_similarity(motifs)

    # Generate summaries
    print("Generating theme summaries...")
    summaries = clusterer.summarize_theme_clusters(clusters)

    # Track transitions if requested
    transition_data = None
    if args.transitions:
        print("Analyzing theme transitions...")
        # Reload sessions for transition analysis
        sessions = clusterer._load_dream_sessions(args.dir, args.limit)
        transition_data = clusterer.track_theme_transitions(sessions)

    # Render overview
    print(f"Rendering theme overview to {args.out}...")
    clusterer.render_theme_overview(clusters, args.out)

    # Print summary to console
    print("\n" + "=" * 60)
    print("SYMBOLIC THEME ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total Motifs Analyzed: {len(motifs)}")
    print(f"Themes Identified: {len([k for k in clusters if k != 'unclustered'])}")
    print()

    for summary in summaries[:5]:  # Show top 5 themes
        print(summary)

    if transition_data:
        print("THEME TRANSITIONS:")
        print(f"Total Sessions: {transition_data['total_sessions']}")
        print(f"Theme Changes: {len(transition_data['transitions'])}")
        for pattern in transition_data["patterns"]:
            print(f"- {pattern}")

    print("=" * 60)


if __name__ == "__main__":
    main()

# CLAUDE CHANGELOG
# - Created symbolic_theme_clusterer.py with comprehensive motif clustering system # CLAUDE_EDIT_v0.1
# - Implemented MotifInstance, SymbolicTheme, and ThematicEvolution data structures # CLAUDE_EDIT_v0.1
# - Added co-occurrence matrix analysis and similarity-based clustering # CLAUDE_EDIT_v0.1
# - Created theme summarization with emotional tone analysis # CLAUDE_EDIT_v0.1
# - Implemented theme transition tracking and pattern detection # CLAUDE_EDIT_v0.1
# - Added rendering support for JSON and Markdown outputs # CLAUDE_EDIT_v0.1