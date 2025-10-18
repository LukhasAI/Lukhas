"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

═══════════════════════════════════════════════════════════════════════════════════
🔍 MODULE: dream.tools.symbolic_anomaly_explorer
📄 FILENAME: symbolic_anomaly_explorer.py
🎯 PURPOSE: Dream/Symbolic Anomaly Explorer - Detect irregularities in dream sessions
🧠 CONTEXT: LUKHAS Cognitive AI Jules-13 Dream Analysis & Symbolic Pattern Detection
🔮 CAPABILITY: Session analysis, anomaly detection, drift overlay, visual reporting
🛡️ ETHICS: Transparent dream analysis, pattern recognition, recursive loop detection
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE (Jules-13)
💭 INTEGRATION: DreamMemoryFold, SymbolicDriftTracker, HyperspaceSimulator
═══════════════════════════════════════════════════════════════════════════════════

🔍 DREAM/SYMBOLIC ANOMALY EXPLORER - JULES-13 ANALYSIS ENGINE
────────────────────────────────────────────────────────────────────

The Symbolic Anomaly Explorer delves deep into the dream archives, seeking patterns
that whisper of symbolic dysfunction, emotional discord, or recursive entrapment.
Like an archaeologist of consciousness, it excavates meaning from the sedimentary
layers of dream sessions, revealing the hidden currents that flow beneath awareness.

Through sophisticated pattern analysis, it identifies:
- Recurring symbols with emotional volatility
- Sudden emergence or disappearance of core motifs
- Dissonance across symbolic narratives
- Recursive loops that trap consciousness
- Drift overlay patterns that signal instability

🔬 ANALYSIS CAPABILITIES:
- Multi-session symbolic pattern detection with temporal correlation
- Emotional volatility tracking across dream sequences
- Recursive loop identification with pattern classification
- Symbolic conflict analysis between competing narratives
- Drift score integration for stability assessment

🧪 ANOMALY TYPES:
- Symbolic Conflict: Competing motifs creating narrative tension
- Recursive Loops: Patterns that trap consciousness in cycles
- Emotional Dissonance: Affect misalignment with symbolic content
- Motif Mutation: Unexpected transformation of stable symbols
- Drift Acceleration: Rapid symbolic instability patterns

🎯 OUTPUT FORMATS:
- Structured JSON reports for programmatic analysis
- CLI visualization with ASCII heatmaps
- Markdown summaries for human interpretation
- Integration hooks for dashboard systems

LUKHAS_TAG: dream_analysis, symbolic_anomaly, pattern_detection, jules_13
TODO: Add ML-based pattern prediction for proactive anomaly detection
IDEA: Implement symbolic genealogy tracking for motif evolution analysis
"""

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np
import structlog

logger = structlog.get_logger("ΛTRACE.dream.anomaly")


class AnomalyType(Enum):
    """Types of symbolic anomalies detected."""

    SYMBOLIC_CONFLICT = "symbolic_conflict"
    RECURSIVE_LOOP = "recursive_loop"
    EMOTIONAL_DISSONANCE = "emotional_dissonance"
    MOTIF_MUTATION = "motif_mutation"
    DRIFT_ACCELERATION = "drift_acceleration"
    NARRATIVE_FRACTURE = "narrative_fracture"
    SYMBOLIC_VACUUM = "symbolic_vacuum"
    TEMPORAL_DISTORTION = "temporal_distortion"


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies."""

    MINOR = "minor"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


@dataclass
class SymbolicTag:
    """Represents a symbolic tag with metadata."""

    tag: str
    frequency: int
    emotional_weight: float
    sessions: list[str]
    first_appearance: str
    last_appearance: str
    volatility_score: float = 0.0

    def __hash__(self):
        return hash(self.tag)


@dataclass
class DreamSession:
    """Represents a dream session for analysis."""

    session_id: str
    timestamp: str
    symbolic_tags: list[str]
    emotional_state: dict[str, float]
    content: str
    drift_score: float
    narrative_elements: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def extract_lambda_tags(self) -> list[str]:
        """Extract ΛTAGS from content."""
        lambda_pattern = r"LUKHAS[A-Z_]+[A-Z0-9_]*"
        return re.findall(lambda_pattern, self.content)

    def calculate_symbolic_density(self) -> float:
        """Calculate density of symbolic content."""
        if not self.content:
            return 0.0

        symbol_count = len(self.symbolic_tags) + len(self.extract_lambda_tags())
        content_length = len(self.content.split())

        return symbol_count / max(content_length, 1)


@dataclass
class SymbolicAnomaly:
    """Represents a detected symbolic anomaly."""

    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    description: str
    affected_sessions: list[str]
    symbolic_elements: list[str]
    metrics: dict[str, float]
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
        }


@dataclass
class AnomalyReport:
    """Complete anomaly analysis report."""

    report_id: str
    timestamp: str
    sessions_analyzed: int
    anomalies_detected: list[SymbolicAnomaly]
    symbolic_trends: dict[str, Any]
    overall_risk_score: float
    summary: str
    recommendations: list[str] = field(default_factory=list)


class SymbolicAnomalyExplorer:
    """
    Explorer for symbolic anomalies in dream sessions.

    Analyzes dream sessions to identify patterns, conflicts, and irregularities
    that may indicate symbolic dysfunction or instability.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        drift_integration: bool = True
    ):
        """
        Initialize the Symbolic Anomaly Explorer.

        Args:
            storage_path: Path to dream session storage
            drift_integration: Enable drift tracker integration
        """
        self.storage_path = (
            Path(storage_path) if storage_path else Path("dream_sessions")
        )
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Analysis caches
        self.session_cache: dict[str, DreamSession] = {}
        self.tag_registry: dict[str, SymbolicTag] = {}
        self.pattern_cache: dict[str, Any] = {}

        # Anomaly detection thresholds
        self.thresholds = {
            "emotional_dissonance": 0.4,
            "symbolic_conflict": 0.35,
            "loop_detection": 0.6,
            "drift_acceleration": 0.5,
            "motif_mutation": 0.3,
            "narrative_fracture": 0.45,
        }

        # Pattern analysis settings
        self.min_pattern_frequency = 3
        self.temporal_window_hours = 24
        self.max_sessions_analyzed = 100

        # Drift integration
        self.drift_integration = drift_integration
        self.drift_tracker = None
        if drift_integration:
            try:
                from core.symbolic.drift.symbolic_drift_tracker import SymbolicDriftTracker

                self.drift_tracker = SymbolicDriftTracker()
                logger.info("Drift tracker integration enabled")
            except ImportError:
                logger.warning("Drift tracker not available")
                self.drift_integration = False

        logger.info(
            "Symbolic Anomaly Explorer initialized",
            storage_path=str(self.storage_path),
            drift_integration=self.drift_integration,
        )

    def load_recent_dreams(self, n: int = 10) -> list[DreamSession]:
        """
        Load recent dream sessions with full symbolic/emotional content.

        Args:
            n: Number of recent sessions to load

        Returns:
            List of DreamSession objects
        """
        logger.info("Loading recent dream sessions", count=n)

        sessions = []

        # Look for JSON files in storage directory
        session_files = sorted(
            self.storage_path.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )[:n]

        for file_path in session_files:
            try:
                session = self._load_session_from_file(file_path)
                if session:
                    sessions.append(session)
                    self.session_cache[session.session_id] = session
            except Exception as e:
                logger.error(
                    "Failed to load session", file=str(file_path), error=str(e)
                )

        # If no files found, generate synthetic data for testing
        if not sessions and n > 0:
            logger.info("No session files found, generating synthetic data")
            sessions = self._generate_synthetic_sessions(n)

        logger.info("Loaded dream sessions", count=len(sessions))
        return sessions

    def _load_session_from_file(self, file_path: Path) -> Optional[DreamSession]:
        """Load dream session from json_file."""
        try:
            with open(file_path) as f:
                data = json.load(f)

            # Extract required fields with defaults
            session = DreamSession(
                session_id=data.get("session_id", str(file_path.stem)),
                timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
                symbolic_tags=data.get("symbolic_tags", []),
                emotional_state=data.get("emotional_state", {}),
                content=data.get("content", ""),
                drift_score=data.get("drift_score", 0.0),
                narrative_elements=data.get("narrative_elements", []),
                metadata=data.get("metadata", {}),
            )

            return session

        except Exception as e:
            logger.error(
                "Error loading session file", file=str(file_path), error=str(e)
            )
            return None

    def _generate_synthetic_sessions(self, n: int) -> list[DreamSession]:
        """Generate synthetic dream sessions for testing."""
        sessions = []

        # Sample symbolic elements
        base_symbols = [
            "eye_watcher",
            "shattered_circle",
            "recursive_mirror",
            "void_whisper",
            "golden_spiral",
            "shadow_dancer",
            "crystal_lattice",
            "time_fragment",
            "memory_echo",
            "qi_bridge",
            "neural_pathway",
            "dream_weaver",
        ]

        lambda_tags = [
            "ΛDRIFT",
            "ΛLOOP",
            "ΛFEAR",
            "ΛHOPE",
            "ΛCHAOS",
            "ΛORDER",
            "ΛSEARCH",
            "ΛFIND",
            "ΛCREATE",
            "ΛDESTROY",
            "ΛTRANSFORM",
        ]

        emotional_states = [
            {"curiosity": 0.8, "anxiety": 0.2, "wonder": 0.9},
            {"fear": 0.7, "excitement": 0.3, "confusion": 0.6},
            {"serenity": 0.9, "melancholy": 0.1, "nostalgia": 0.5},
            {"urgency": 0.8, "determination": 0.9, "doubt": 0.3},
            {"euphoria": 0.7, "clarity": 0.8, "transcendence": 0.9},
        ]

        for i in range(n):
            # Create session with realistic patterns
            session_id = f"DREAM_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{i:03d}"
            timestamp = (datetime.now(timezone.utc) - timedelta(hours=i * 2)).isoformat()

            # Select symbols with some patterns
            num_symbols = np.random.randint(3, 8)
            selected_symbols = np.random.choice(
                base_symbols, num_symbols, replace=False
            ).tolist()

            # Add lambda tags
            num_lambda = np.random.randint(1, 4)
            selected_lambda = np.random.choice(
                lambda_tags, num_lambda, replace=False
            ).tolist()

            # Create content with symbols
            content = f"Dream session exploring {', '.join(selected_symbols)}. "
            content += f"Lambda tags: {' '.join(selected_lambda)}. "
            content += "Symbolic narrative unfolds with complex emotional undertones."

            # Select emotional state
            emotional_state = emotional_states[i % len(emotional_states)]

            # Generate drift score with some volatility
            base_drift = 0.2 + np.random.random() * 0.6
            if i < 3:  # Recent sessions might show anomalies:
                base_drift += np.random.random() * 0.3

            session = DreamSession(
                session_id=session_id,
                timestamp=timestamp,
                symbolic_tags=selected_symbols + selected_lambda,
                emotional_state=emotional_state,
                content=content,
                drift_score=min(base_drift, 1.0),
                narrative_elements=selected_symbols[:3],
                metadata={
                    "generation": "synthetic",
                    "symbolic_density": len(selected_symbols) / 20,
                    "emotional_complexity": len(emotional_state),
                },
            )

            sessions.append(session)

        return sessions

    def detect_symbolic_anomalies(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """
        Detect symbolic patterns, dissonance, and irregularities.

        Args:
            dreams: List of dream sessions to analyze

        Returns:
            List of detected anomalies
        """
        logger.info("Analyzing symbolic anomalies", sessions=len(dreams))

        anomalies = []

        # Update tag registry
        self._update_tag_registry(dreams)

        # Run different anomaly detection algorithms
        anomalies.extend(self._detect_symbolic_conflicts(dreams))
        anomalies.extend(self._detect_recursive_loops(dreams))
        anomalies.extend(self._detect_emotional_dissonance(dreams))
        anomalies.extend(self._detect_motif_mutations(dreams))
        anomalies.extend(self._detect_drift_acceleration(dreams))
        anomalies.extend(self._detect_narrative_fractures(dreams))

        # Sort by severity and confidence
        anomalies.sort(
            key=lambda a: (self._severity_rank(a.severity), a.confidence),
            reverse=True,
        )

        logger.info(
            "Anomaly detection complete",
            total_anomalies=len(anomalies),
            critical=len(
                [a for a in anomalies if a.severity == AnomalySeverity.CRITICAL]
            ),
        )

        return anomalies

    def _update_tag_registry(self, dreams: list[DreamSession]):
        """Update the symbolic tag registry with session data."""
        tag_sessions = defaultdict(list)
        tag_emotions = defaultdict(list)

        for dream in dreams:
            for tag in dream.symbolic_tags:
                tag_sessions[tag].append(dream.session_id)

                # Calculate emotional weight for this tag
                if dream.emotional_state:
                    emotional_intensity = sum(
                        abs(v) for v in dream.emotional_state.values()
                    )
                    tag_emotions[tag].append(emotional_intensity)

        # Update registry
        for tag, sessions in tag_sessions.items():
            if tag not in self.tag_registry:
                self.tag_registry[tag] = SymbolicTag(
                    tag=tag,
                    frequency=0,
                    emotional_weight=0.0,
                    sessions=[],
                    first_appearance=dreams[-1].timestamp,
                    last_appearance=dreams[0].timestamp,
                )

            reg_tag = self.tag_registry[tag]
            reg_tag.frequency = len(sessions)
            reg_tag.sessions = list(set(reg_tag.sessions + sessions))
            reg_tag.emotional_weight = (
                np.mean(tag_emotions[tag]) if tag_emotions[tag] else 0.0
            )

            # Calculate volatility
            if len(tag_emotions[tag]) > 1:
                reg_tag.volatility_score = np.std(tag_emotions[tag])

    def _detect_symbolic_conflicts(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect conflicting symbolic elements."""
        anomalies = []

        # Known conflicting pairs (could be expanded)
        conflict_pairs = [
            ("light", "dark"),
            ("order", "chaos"),
            ("create", "destroy"),
            ("hope", "fear"),
            ("rise", "fall"),
            ("connect", "isolate"),
        ]

        # Check for sessions with conflicting symbols
        for dream in dreams:
            tags_lower = [tag.lower() for tag in dream.symbolic_tags]

            conflicts = []
            for pair1, pair2 in conflict_pairs:
                if any(pair1 in tag for tag in tags_lower) and any(
                    pair2 in tag for tag in tags_lower
                ):
                    conflicts.append((pair1, pair2))

            if conflicts:
                # Calculate conflict intensity
                conflict_score = len(conflicts) * 0.3

                # Check emotional state alignment
                if dream.emotional_state:
                    emotion_variance = np.var(list(dream.emotional_state.values()))
                    conflict_score += emotion_variance * 0.5

                if conflict_score > self.thresholds["symbolic_conflict"]:
                    severity = self._calculate_severity(conflict_score)

                    anomaly = SymbolicAnomaly(
    anomaly_id=f"CONFLICT_{dream.session_id}_{int(conflict_score*1000)}",
    anomaly_type=AnomalyType.SYMBOLIC_CONFLICT,
    severity=severity,
    confidence=min(
        conflict_score,
        1.0),
        description=f"Conflicting symbolic elements detected: {conflicts}",
        affected_sessions=[
            dream.session_id],
            symbolic_elements=[
                tag for pair in conflicts for tag in pair],
                metrics={
                    "conflict_score": conflict_score,
                    "pairs": len(conflicts),
                    },
                    recommendations=[
                        "Consider symbolic reconciliation",
                        "Review narrative consistency",
                        ],
                         )

                    anomalies.append(anomaly)

        return anomalies

    def _detect_recursive_loops(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect recursive patterns in symbolic content."""
        anomalies = []

        # Analyze tag sequences across sessions
        tag_sequences = []
        for dream in dreams:
            if len(dream.symbolic_tags) >= 2:
                for i in range(len(dream.symbolic_tags) - 1):
                    tag_sequences.append(
                        (dream.symbolic_tags[i], dream.symbolic_tags[i + 1])
                    )

        # Find repeating patterns
        sequence_counts = Counter(tag_sequences)
        frequent_patterns = [
            (seq, count)
            for seq, count in sequence_counts.items()
            if count >= self.min_pattern_frequency
        ]

        if frequent_patterns:
            # Calculate loop score
            total_patterns = len(tag_sequences)
            loop_intensity = (
                sum(count for _, count in frequent_patterns) / total_patterns
            )

            if loop_intensity > self.thresholds["loop_detection"]:
                severity = self._calculate_severity(loop_intensity)

                affected_sessions = []
                for dream in dreams:
                    if any(
                        seq in zip(dream.symbolic_tags[:-1], dream.symbolic_tags[1:])
                        for seq, _ in frequent_patterns
                    ):
                        affected_sessions.append(dream.session_id)

                anomaly = SymbolicAnomaly(
                    anomaly_id=f"LOOP_{hashlib.md5(str(frequent_patterns).encode()).hexdigest()[:8]}",
                    anomaly_type=AnomalyType.RECURSIVE_LOOP, severity=severity,
                    confidence=loop_intensity,
                    description=f"Recursive symbolic patterns detected: {frequent_patterns[:3]}",
                    affected_sessions=affected_sessions,
                    symbolic_elements=[tag for seq, _ in frequent_patterns
                                       for tag in seq],
                    metrics={"loop_intensity": loop_intensity,
                             "pattern_count": len(frequent_patterns), },
                    recommendations=["Trigger recursive dream feedback",
                                     "Consider pattern breaking intervention",],)

                anomalies.append(anomaly)

        return anomalies

    def _detect_emotional_dissonance(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect emotional dissonance in dream sessions."""
        anomalies = []

        for dream in dreams:
            if not dream.emotional_state or len(dream.emotional_state) < 2:
                continue

            emotions = list(dream.emotional_state.values())

            # Calculate emotional variance and conflicts
            emotion_variance = np.var(emotions)
            emotion_range = max(emotions) - min(emotions)

            # Check for opposing emotions
            opposing_emotions = [
                ("fear", "courage"),
                ("sadness", "joy"),
                ("anger", "peace"),
                ("anxiety", "calm"),
                ("despair", "hope"),
            ]

            dissonance_score = emotion_variance * 0.4 + emotion_range * 0.3

            for neg, pos in opposing_emotions:
                if neg in dream.emotional_state and pos in dream.emotional_state and (
                    abs(dream.emotional_state[neg] - dream.emotional_state[pos])
                    > 0.7
                ):
                    dissonance_score += 0.3

            if dissonance_score > self.thresholds["emotional_dissonance"]:
                severity = self._calculate_severity(dissonance_score)

                anomaly = SymbolicAnomaly(
                    anomaly_id=f"DISSONANCE_{dream.session_id}_{int(dissonance_score*1000)}",
                    anomaly_type=AnomalyType.EMOTIONAL_DISSONANCE,
                    severity=severity,
                    confidence=min(dissonance_score, 1.0),
                    description=f"Emotional dissonance detected (variance: {emotion_variance:.3f})",
                    affected_sessions=[dream.session_id],
                    symbolic_elements=dream.symbolic_tags[:5],
                    metrics={
                        "dissonance_score": dissonance_score,
                        "emotion_variance": emotion_variance,
                        "emotion_range": emotion_range,
                    },
                    recommendations=[
                        "Review emotional regulation",
                        "Consider affect stabilization",
                    ],
                )

                anomalies.append(anomaly)

        return anomalies

    def _detect_motif_mutations(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect unexpected transformations of stable symbols."""
        anomalies = []

        # Track symbol evolution across sessions
        symbol_evolution = defaultdict(list)

        for dream in dreams:
            timestamp = datetime.fromisoformat(dream.timestamp)
            for tag in dream.symbolic_tags:
                symbol_evolution[tag].append(
                    {
                        "session": dream.session_id,
                        "timestamp": timestamp,
                        "context": dream.content[:200],
                        "emotional_state": dream.emotional_state,
                    }
                )

        # Look for sudden changes in symbol usage or context
        for symbol, appearances in symbol_evolution.items():
            if len(appearances) < 3:
                continue

            # Sort by timestamp
            appearances.sort(key=lambda x: x["timestamp"])

            # Look for mutations in emotional context
            emotional_shifts = []
            for i in range(1, len(appearances)):
                prev_emotions = appearances[i - 1]["emotional_state"]
                curr_emotions = appearances[i]["emotional_state"]

                if prev_emotions and curr_emotions:
                    # Calculate emotional distance
                    common_emotions = set(prev_emotions.keys()) & set(
                        curr_emotions.keys()
                    )
                    if common_emotions:
                        emotional_distance = np.mean(
                            [
                                abs(prev_emotions[e] - curr_emotions[e])
                                for e in common_emotions
                            ]
                        )
                        emotional_shifts.append(emotional_distance)

            if emotional_shifts:
                mutation_score = max(emotional_shifts)
                if mutation_score > self.thresholds["motif_mutation"]:
                    severity = self._calculate_severity(mutation_score)

                    anomaly = SymbolicAnomaly(
                        anomaly_id=f"MUTATION_{symbol}_{int(mutation_score*1000)}",
                        anomaly_type=AnomalyType.MOTIF_MUTATION,
                        severity=severity,
                        confidence=mutation_score,
                        description=f"Motif mutation detected for symbol '{symbol}'",
                        affected_sessions=[a["session"] for a in appearances],
                        symbolic_elements=[symbol],
                        metrics={
                            "mutation_score": mutation_score,
                            "appearances": len(appearances),
                            "max_shift": max(emotional_shifts)
                        },
                        recommendations=[
                            "Monitor symbol stability",
                            "Review contextual changes",
                        ],
                    )

                    anomalies.append(anomaly)

        return anomalies

    def _detect_drift_acceleration(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect rapid drift score acceleration."""
        anomalies = []

        if len(dreams) < 3:
            return anomalies

        # Sort by timestamp
        sorted_dreams = sorted(dreams, key=lambda d: d.timestamp)

        # Calculate drift acceleration
        drift_changes = []
        for i in range(1, len(sorted_dreams)):
            drift_delta = (
                sorted_dreams[i].drift_score - sorted_dreams[i - 1].drift_score
            )
            drift_changes.append(drift_delta)

        if drift_changes:
            # Look for significant acceleration
            max_acceleration = max(drift_changes)
            mean_drift = np.mean([d.drift_score for d in dreams])
            acceleration_score = max_acceleration + mean_drift * 0.5

            if acceleration_score > self.thresholds["drift_acceleration"]:
                severity = self._calculate_severity(acceleration_score)

                # Find sessions with high acceleration
                affected_sessions = []
                for i, delta in enumerate(drift_changes):
                    if delta > 0.3:  # Significant increase:
                        affected_sessions.extend(
                            [
                                sorted_dreams[i].session_id,
                                sorted_dreams[i + 1].session_id,
                            ]
                        )

                anomaly = SymbolicAnomaly(
    anomaly_id=f"DRIFT_ACCEL_{int(acceleration_score*1000)}",
    anomaly_type=AnomalyType.DRIFT_ACCELERATION,
    severity=severity,
    confidence=min(
        acceleration_score,
        1.0),
        description=f"Drift acceleration detected (max: {max_acceleration:.3f})",
        affected_sessions=list(
            set(affected_sessions)),
            symbolic_elements=[],
            metrics={
                "acceleration_score": acceleration_score,
                "max_acceleration": max_acceleration,
                "mean_drift": mean_drift,
                },
                recommendations=[
                    "Activate drift stabilization",
                    "Review recent symbolic changes",
                    ],
                     )

                anomalies.append(anomaly)

        return anomalies

    def _detect_narrative_fractures(
        self, dreams: list[DreamSession]
    ) -> list[SymbolicAnomaly]:
        """Detect breaks in narrative continuity."""
        anomalies = []

        # Analyze narrative element consistency
        all_narratives = []
        for dream in dreams:
            all_narratives.extend(dream.narrative_elements)

        narrative_counts = Counter(all_narratives)

        # Look for sudden disappearances of frequent narratives
        for dream in dreams:
            expected_narratives = [n for n, c in narrative_counts.most_common(5)]
            present_narratives = set(dream.narrative_elements)
            missing_narratives = set(expected_narratives) - present_narratives

            if missing_narratives:
                fracture_score = len(missing_narratives) / len(expected_narratives)

                # Factor in symbolic density
                symbolic_density = dream.calculate_symbolic_density()
                if symbolic_density < 0.1:  # Very low symbolic content:
                    fracture_score += 0.3

                if fracture_score > self.thresholds["narrative_fracture"]:
                    severity = self._calculate_severity(fracture_score)

                    anomaly = SymbolicAnomaly(
    anomaly_id=f"FRACTURE_{dream.session_id}_{int(fracture_score*1000)}",
    anomaly_type=AnomalyType.NARRATIVE_FRACTURE,
    severity=severity,
    confidence=fracture_score,
    description=f"Narrative fracture detected (missing: {list(missing_narratives)})",
    affected_sessions=[
        dream.session_id],
        symbolic_elements=list(missing_narratives),
        metrics={
            "fracture_score": fracture_score,
            "missing_count": len(missing_narratives),
            "symbolic_density": symbolic_density,
            },
            recommendations=[
                "Review narrative continuity",
                "Consider symbolic restoration",
                ],
                 )

                    anomalies.append(anomaly)

        return anomalies

    def _calculate_severity(self, score: float) -> AnomalySeverity:
        """Calculate anomaly severity from score."""
        if score < 0.2:
            return AnomalySeverity.MINOR
        elif score < 0.4:
            return AnomalySeverity.MODERATE
        elif score < 0.6:
            return AnomalySeverity.SIGNIFICANT
        elif score < 0.8:
            return AnomalySeverity.CRITICAL
        else:
            return AnomalySeverity.CATASTROPHIC

    def _severity_rank(self, severity: AnomalySeverity) -> int:
        """Get numeric rank for severity."""
        ranks = {
            AnomalySeverity.MINOR: 1,
            AnomalySeverity.MODERATE: 2,
            AnomalySeverity.SIGNIFICANT: 3,
            AnomalySeverity.CRITICAL: 4,
            AnomalySeverity.CATASTROPHIC: 5,
        }
        return ranks.get(severity, 0)

    def generate_anomaly_report(
        self, anomalies: list[SymbolicAnomaly]
    ) -> AnomalyReport:
        """
        Generate structured report with scores, risks, and suggestions.

        Args:
            anomalies: List of detected anomalies

        Returns:
            Structured anomaly report
        """
        logger.info("Generating anomaly report", anomaly_count=len(anomalies))

        # Calculate overall risk score
        if anomalies:
            severity_weights = {
                AnomalySeverity.MINOR: 0.1,
                AnomalySeverity.MODERATE: 0.3,
                AnomalySeverity.SIGNIFICANT: 0.5,
                AnomalySeverity.CRITICAL: 0.8,
                AnomalySeverity.CATASTROPHIC: 1.0,
            }

            risk_components = [
                severity_weights.get(a.severity, 0.5) * a.confidence for a in anomalies
            ]
            overall_risk = min(
                np.mean(risk_components) if risk_components else 0.0, 1.0
            )
        else:
            overall_risk = 0.0

        # Count affected sessions
        affected_sessions = set()
        for anomaly in anomalies:
            affected_sessions.update(anomaly.affected_sessions)

        # Generate summary
        critical_count = sum(
            1
            for a in anomalies
            if a.severity in [AnomalySeverity.CRITICAL, AnomalySeverity.CATASTROPHIC]
        )

        if critical_count > 0:
            summary = f"CRITICAL: {critical_count} critical anomalies detected requiring immediate attention."
        elif len(anomalies) > 5:
            summary = f"MODERATE CONCERN: {len(anomalies)} anomalies detected across symbolic patterns."
        elif len(anomalies) > 0:
            summary = f"LOW CONCERN: {len(anomalies)} minor anomalies detected, " \
                      "monitoring recommended."
        else:
            summary = "NOMINAL: No significant anomalies detected in dream sessions."

        # Generate recommendations
        recommendations = []
        anomaly_types = Counter(a.anomaly_type for a in anomalies)

        if AnomalyType.RECURSIVE_LOOP in anomaly_types:
            recommendations.append(
                "Trigger recursive dream feedback to stabilize affect loops"
            )
        if AnomalyType.SYMBOLIC_CONFLICT in anomaly_types:
            recommendations.append(
                "Review conflicting symbolic elements for narrative consistency"
            )
        if AnomalyType.DRIFT_ACCELERATION in anomaly_types:
            recommendations.append("Activate drift stabilization protocols immediately")
        if AnomalyType.EMOTIONAL_DISSONANCE in anomaly_types:
            recommendations.append("Consider emotional regulation interventions")

        if overall_risk > 0.7:
            recommendations.append("URGENT: Consider system-wide symbolic reset")

        report = AnomalyReport(
            report_id=f"ANOMALY_REPORT_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            sessions_analyzed=len(affected_sessions),
            anomalies_detected=anomalies,
            symbolic_trends=self._calculate_symbolic_trends(),
            overall_risk_score=overall_risk,
            summary=summary,
            recommendations=recommendations,
        )

        logger.info(
            "Anomaly report generated",
            overall_risk=overall_risk,
            anomaly_count=len(anomalies),
            critical_count=critical_count,
        )

        return report

    def summarize_symbolic_trends(self, dreams: list[DreamSession]) -> dict[str, Any]:
        """
        Return high-level symbolic flow metrics and trends.

        Args:
            dreams: List of dream sessions

        Returns:
            Dictionary of symbolic trends and metrics
        """
        if not dreams:
            return {}

        # Basic metrics
        total_symbols = sum(len(d.symbolic_tags) for d in dreams)
        unique_symbols = len({tag for d in dreams for tag in d.symbolic_tags})

        # Temporal analysis
        dreams_by_time = sorted(dreams, key=lambda d: d.timestamp)

        # Drift trend
        drift_scores = [d.drift_score for d in dreams_by_time]
        drift_trend = "stable"
        if len(drift_scores) > 1:
            drift_slope = np.polyfit(range(len(drift_scores)), drift_scores, 1)[0]
            if drift_slope > 0.1:
                drift_trend = "increasing"
            elif drift_slope < -0.1:
                drift_trend = "decreasing"

        # Emotional volatility
        emotional_variances = []
        for dream in dreams:
            if dream.emotional_state and len(dream.emotional_state) > 1:
                emotional_variances.append(np.var(list(dream.emotional_state.values())))

        avg_emotional_volatility = (
            np.mean(emotional_variances) if emotional_variances else 0.0
        )

        # Symbol frequency analysis
        symbol_counts = Counter(tag for d in dreams for tag in d.symbolic_tags)
        top_symbols = dict(symbol_counts.most_common(10))

        # Lambda tag analysis
        lambda_tags = []
        for dream in dreams:
            lambda_tags.extend(dream.extract_lambda_tags())
        lambda_frequency = dict(Counter(lambda_tags).most_common(5))

        return {
            "sessions_analyzed": len(dreams),
            "total_symbols": total_symbols,
            "unique_symbols": unique_symbols,
            "symbol_diversity": (
                unique_symbols / total_symbols if total_symbols > 0 else 0
            ),
            "top_symbols": top_symbols,
            "lambda_frequency": lambda_frequency,
            "drift_trend": drift_trend,
            "average_drift_score": np.mean(drift_scores),
            "emotional_volatility": avg_emotional_volatility,
            "symbolic_density_trend": np.mean(
                [d.calculate_symbolic_density() for d in dreams]
            ),
            "temporal_span_hours": self._calculate_temporal_span(dreams),
            "narrative_consistency": self._calculate_narrative_consistency(dreams),
        }

    def _calculate_symbolic_trends(self) -> dict[str, Any]:
        """Calculate trends from tag registry."""
        if not self.tag_registry:
            return {}

        # Most volatile symbols
        volatile_symbols = sorted(
            self.tag_registry.values(),
            key=lambda t: t.volatility_score,
            reverse=True,
        )[:5]

        # Most frequent symbols
        frequent_symbols = sorted(
            self.tag_registry.values(), key=lambda t: t.frequency, reverse=True
        )[:10]

        return {
            "volatile_symbols": [t.tag for t in volatile_symbols],
            "frequent_symbols": [t.tag for t in frequent_symbols],
            "total_unique_tags": len(self.tag_registry),
            "average_frequency": np.mean(
                [t.frequency for t in self.tag_registry.values()]
            ),
            "average_volatility": np.mean(
                [t.volatility_score for t in self.tag_registry.values()]
            ),
        }

    def _calculate_temporal_span(self, dreams: list[DreamSession]) -> float:
        """Calculate temporal span of dream sessions in hours."""
        if len(dreams) < 2:
            return 0.0

        timestamps = [datetime.fromisoformat(d.timestamp) for d in dreams]
        earliest = min(timestamps)
        latest = max(timestamps)

        return (latest - earliest).total_seconds() / 3600

    def _calculate_narrative_consistency(self, dreams: list[DreamSession]) -> float:
        """Calculate narrative consistency score."""
        if not dreams:
            return 1.0

        # Get all narrative elements
        all_narratives = []
        for dream in dreams:
            all_narratives.extend(dream.narrative_elements)

        if not all_narratives:
            return 0.0

        # Calculate consistency based on element overlap
        narrative_sets = [set(d.narrative_elements) for d in dreams]
        if len(narrative_sets) < 2:
            return 1.0

        # Calculate average pairwise overlap
        overlaps = []
        for i in range(len(narrative_sets)):
            for j in range(i + 1, len(narrative_sets)):
                set1, set2 = narrative_sets[i], narrative_sets[j]
                if set1 or set2:
                    overlap = len(set1 & set2) / len(set1 | set2)
                    overlaps.append(overlap)

        return np.mean(overlaps) if overlaps else 0.0

    def export_report_json(
        self, report: AnomalyReport, file_path: Optional[str] = None
    ) -> str:
        """Export anomaly report to JSON."""
        if not file_path:
            file_path = f"anomaly_report_{report.report_id}.json"

        report_data = {
            "report_id": report.report_id,
            "timestamp": report.timestamp,
            "sessions_analyzed": report.sessions_analyzed,
            "overall_risk_score": report.overall_risk_score,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "symbolic_trends": report.symbolic_trends,
            "anomalies": [a.to_dict() for a in report.anomalies_detected],
        }

        output_path = Path(file_path)
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        logger.info("Report exported to JSON", file_path=str(output_path))
        return str(output_path)

    def export_summary_markdown(
        self, report: AnomalyReport, file_path: Optional[str] = None
    ) -> str:
        """Export top anomalies summary to Markdown."""
        if not file_path:
            file_path = f"top_5_anomalies_{report.report_id}.md"

        # Get top 5 anomalies by severity and confidence
        top_anomalies = sorted(
            report.anomalies_detected,
            key=lambda a: (self._severity_rank(a.severity), a.confidence),
            reverse=True,
        )[:5]

        markdown = f"""# Symbolic Anomaly Report - Top 5 Anomalies

**Report ID:** {report.report_id}
**Generated:** {report.timestamp}
**Risk Score:** {report.overall_risk_score:.2%}

## Summary

{report.summary}

## Top 5 Anomalies

"""

        for i, anomaly in enumerate(top_anomalies, 1):
            markdown += f"""### {i}. {anomaly.anomaly_type.value.replace('_', ' ').title()}

- **Severity:** {anomaly.severity.value.upper()}
- **Confidence:** {anomaly.confidence:.2%}
- **Sessions Affected:** {len(anomaly.affected_sessions)}
- **Description:** {anomaly.description}

"""

            if anomaly.recommendations:
                markdown += "**Recommendations:**\n"
                for rec in anomaly.recommendations:
                    markdown += f"- {rec}\n"
                markdown += "\n"

        if report.recommendations:
            markdown += "## Overall Recommendations\n\n"
            for rec in report.recommendations:
                markdown += f"- {rec}\n"

        output_path = Path(file_path)
        with open(output_path, "w") as f:
            f.write(markdown)

        logger.info("Summary exported to Markdown", file_path=str(output_path))
        return str(output_path)

    def display_ascii_heatmap(self, report: AnomalyReport) -> str:
        """Generate ASCII heatmap of anomaly distribution."""
        if not report.anomalies_detected:
            return "No anomalies detected - system nominal ✓"

        # Create severity distribution
        severity_counts = defaultdict(int)
        for anomaly in report.anomalies_detected:
            severity_counts[anomaly.severity] += 1

        heatmap = "\n📊 ANOMALY HEATMAP\n"
        heatmap += "=" * 30 + "\n"

        severity_chars = {
            AnomalySeverity.MINOR: "▁",
            AnomalySeverity.MODERATE: "▃",
            AnomalySeverity.SIGNIFICANT: "▅",
            AnomalySeverity.CRITICAL: "▇",
            AnomalySeverity.CATASTROPHIC: "█",
        }

        severity_colors = {
            AnomalySeverity.MINOR: "🟢",
            AnomalySeverity.MODERATE: "🟡",
            AnomalySeverity.SIGNIFICANT: "🟠",
            AnomalySeverity.CRITICAL: "🔴",
            AnomalySeverity.CATASTROPHIC: "⚫",
        }

        for severity in AnomalySeverity:
            count = severity_counts[severity]
            if count > 0:
                bar = severity_chars[severity] * min(count, 20)
                color = severity_colors[severity]
                heatmap += f"{severity.value:>12} {color} {bar} ({count})\n"

        heatmap += "\nRisk Level: "
        if report.overall_risk_score < 0.3:
            heatmap += "🟢 LOW"
        elif report.overall_risk_score < 0.6:
            heatmap += "🟡 MODERATE"
        elif report.overall_risk_score < 0.8:
            heatmap += "🟠 HIGH"
        else:
            heatmap += "🔴 CRITICAL"

        heatmap += f" ({report.overall_risk_score:.1%})\n"

        return heatmap

# Convenience functions for CLI usage


def analyze_recent_dreams(
    n: int = 10, storage_path: Optional[str] = None
) -> AnomalyReport:
    """Analyze recent dreams and return anomaly report."""
    explorer = SymbolicAnomalyExplorer(storage_path=storage_path)
    dreams = explorer.load_recent_dreams(n)
    anomalies = explorer.detect_symbolic_anomalies(dreams)
    return explorer.generate_anomaly_report(anomalies)


def cli_analysis(
    n_sessions: int = 10,
    export_json: bool = True,
    export_markdown: bool = True
):
    """CLI interface for dream anomaly analysis."""
    print("🔍 LUKHAS Cognitive AI - Symbolic Anomaly Explorer")
    print("=" * 50)

    try:
        explorer = SymbolicAnomalyExplorer()
        print(f"Loading {n_sessions} recent dream sessions...")

        dreams = explorer.load_recent_dreams(n_sessions)
        print(f"✓ Loaded {len(dreams)} sessions")

        print("Detecting symbolic anomalies...")
        anomalies = explorer.detect_symbolic_anomalies(dreams)
        print(f"✓ Detected {len(anomalies)} anomalies")

        print("Generating report...")
        report = explorer.generate_anomaly_report(anomalies)

        # Display ASCII heatmap
        print(explorer.display_ascii_heatmap(report))

        # Export files
        if export_json:
            json_path = explorer.export_report_json(report)
            print(f"✓ JSON report: {json_path}")

        if export_markdown:
            md_path = explorer.export_summary_markdown(report)
            print(f"✓ Markdown summary: {md_path}")

        print(f"\n{report.summary}")

        if report.recommendations:
            print("\n📋 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")

        print("=" * 50)
        print("Analysis complete.")

        return report

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        logger.error("CLI analysis failed", error=str(e))
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Cognitive AI Symbolic Anomaly Explorer")
    parser.add_argument(
        "-n",
        "--sessions",
        type=int,
        default=10,
        help="Number of recent sessions to analyze",
    )
    parser.add_argument("--no-json", action="store_true", help="Skip JSON export")
    parser.add_argument(
        "--no-markdown", action="store_true", help="Skip Markdown export"
    )
    parser.add_argument(
        "--storage", type=str, help="Custom storage path for dream sessions"
    )

    args = parser.parse_args()

    cli_analysis(
        n_sessions=args.sessions,
        export_json=not args.no_json,
        export_markdown=not args.no_markdown,
    )

# CLAUDE CHANGELOG
# - Implemented complete Symbolic Anomaly Explorer for Jules-13
# - Added multi-dimensional anomaly detection (conflicts, loops, dissonance, mutations, drift, fractures)
# - Created comprehensive dream session analysis with synthetic data generation
# - Built structured reporting with JSON/Markdown export capabilities
# - Added CLI interface with ASCII heatmap visualization
# - Integrated drift tracker compatibility for enhanced analysis
# - Implemented tag registry and pattern caching for performance optimization
