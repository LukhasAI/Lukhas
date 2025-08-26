# ΛORIGIN_AGENT: Claude-4-Harmonizer
# ΛTASK_ID: CLAUDE_11_SYMBOLIC_DRIFT_ENGINE
# ΛCOMMIT_WINDOW: drift-scoring-engine-implementation
# ΛPROVED_BY: Human Overseer (AGI_DEV)
# ΛUDIT: Complete symbolic drift scoring engine implementation
# CLAUDE_EDIT_v0.1: Merged from core/symbolic_core/ as part of consolidation

"""

#TAG:consciousness
#TAG:states
#TAG:neuroplastic
#TAG:colony


Enterprise Symbolic Drift Tracker for LUKHAS AGI

This module implements comprehensive symbolic drift detection, quantification,
and analysis across memory, reasoning, emotional, and ethical dimensions.
Replaces stub implementations with production-grade drift scoring algorithms.

Core Capabilities:
- Multi-dimensional symbolic state comparison
- Recursive drift loop detection
- GLYPH divergence analysis with entropy calculations
- Phase-based drift classification (EARLY/MIDDLE/CASCADE)
- Real-time drift alerts with safety thresholds
- Enterprise logging with ΛTRACE integration
"""

# Add logging
from candidate.core.common import get_logger

logger = get_logger(__name__)

import hashlib
import json
import math
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

# ΛNOTE: Enterprise symbolic drift tracking with multi-dimensional analysis


class DriftPhase(Enum):
    """Symbolic drift phase classification"""

    EARLY = "EARLY"  # Initial deviation (0.0-0.25)
    MIDDLE = "MIDDLE"  # Moderate drift (0.25-0.5)
    LATE = "LATE"  # Significant drift (0.5-0.75)
    CASCADE = "CASCADE"  # Critical drift requiring intervention (0.75-1.0)


@dataclass
class DriftScore:
    """Comprehensive drift scoring result"""

    overall_score: float  # 0.0-1.0 overall drift magnitude
    entropy_delta: float  # Change in symbolic entropy
    glyph_divergence: float  # GLYPH/symbol overlap vs novelty
    emotional_drift: float  # Emotional polarity/magnitude change
    ethical_drift: float  # Ethical alignment deviation
    temporal_decay: float  # Time-weighted decay factor
    phase: DriftPhase  # Classification of drift phase
    recursive_indicators: list[str]  # Detected recursive patterns
    risk_level: str  # LOW/MEDIUM/HIGH/CRITICAL
    metadata: dict[str, Any]  # Additional context and measurements


@dataclass
class SymbolicState:
    """Symbolic state snapshot for drift comparison"""

    session_id: str
    timestamp: datetime
    symbols: list[str]  # GLYPHs, ΛTAGS, symbolic markers
    emotional_vector: list[float]  # VAD or emotional state
    ethical_alignment: float  # Ethical consistency score
    entropy: float  # State entropy measurement
    context_metadata: dict[str, Any]  # Additional state context
    hash_signature: str  # State fingerprint for comparison


class SymbolicDriftTracker:
    """
    Enterprise symbolic drift detection and analysis engine.

    Tracks symbolic state evolution across sessions, detecting divergence
    in emotional, ethical, and semantic dimensions with recursive pattern
    analysis and safety threshold enforcement.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the symbolic drift tracker with configuration.

        Args:
            config: Configuration parameters including thresholds and storage options
        """
        self.config = config or {}

        # Configuration parameters with enterprise defaults
        self.drift_thresholds = {
            "caution": self.config.get("caution_threshold", 0.4),
            "warning": self.config.get("warning_threshold", 0.6),
            "critical": self.config.get("critical_threshold", 0.75),
            "cascade": self.config.get("cascade_threshold", 0.9),
        }

        self.entropy_decay_rate = self.config.get("entropy_decay_rate", 0.05)
        self.temporal_window_hours = self.config.get("temporal_window_hours", 24)
        self.max_session_history = self.config.get("max_session_history", 1000)
        self.recursive_detection_window = self.config.get("recursive_window", 10)

        # State storage
        self.symbolic_states: dict[str, list[SymbolicState]] = defaultdict(list)
        self.drift_records: list[dict[str, Any]] = []
        self.recursive_patterns: dict[str, list[str]] = defaultdict(list)
        self.alert_history: deque = deque(maxlen=100)

        # Drift analysis cache
        self.drift_cache: dict[str, DriftScore] = {}
        self.last_cache_cleanup = datetime.now()

        logger.info(
            f"SymbolicDriftTracker initialized with enterprise configuration - config: {self.config}, thresholds: {self.drift_thresholds}"
        )

    def calculate_symbolic_drift(
        self,
        current_symbols: list[str],
        prior_symbols: list[str],
        context: dict[str, Any],
    ) -> float:
        """
        Compares current and historical GLYPH/tag states and outputs a DriftScore.

        Analyzes symbolic divergence across multiple dimensions:
        - Symbol overlap and novelty detection
        - Emotional polarity and magnitude shifts
        - Entropy change analysis
        - Temporal decay factors

        Args:
            current_symbols: Current GLYPH/ΛTAG state
            prior_symbols: Historical baseline symbols
            context: Additional context including emotional vectors, timestamps

        Returns:
            float: DriftScore between 0.0 (no drift) and 1.0 (maximum drift)
        """
        if not current_symbols and not prior_symbols:
            return 0.0

        # ΛDRIFT: Core drift calculation with multi-dimensional analysis
        logger.debug(
            "Calculating symbolic drift",
            current_count=len(current_symbols),
            prior_count=len(prior_symbols),
            context_keys=list(context.keys()),
            tag="ΛDRIFT",
        )

        try:
            # 1. Symbol Set Analysis (30% weight)
            symbol_drift = self._calculate_symbol_set_drift(
                current_symbols, prior_symbols
            )

            # 2. Emotional Vector Drift (25% weight)
            emotional_drift = self._calculate_emotional_drift(context)

            # 3. Entropy Delta Analysis (20% weight)
            entropy_drift = self._calculate_entropy_drift(
                current_symbols, prior_symbols
            )

            # 4. Ethical Alignment Drift (15% weight)
            ethical_drift = self._calculate_ethical_drift(context)

            # 5. Temporal Decay Factor (10% weight)
            temporal_factor = self._calculate_temporal_decay(context)

            # Weighted combination
            weighted_score = (
                symbol_drift * 0.30
                + emotional_drift * 0.25
                + entropy_drift * 0.20
                + ethical_drift * 0.15
                + temporal_factor * 0.10
            )

            # Apply non-linear scaling for critical drift detection
            drift_score = self._apply_nonlinear_scaling(weighted_score)

            # ΛDELTA: Log entropy delta for analysis
            logger.info(
                "Symbolic drift calculated",
                drift_score=round(drift_score, 3),
                symbol_drift=round(symbol_drift, 3),
                emotional_drift=round(emotional_drift, 3),
                entropy_drift=round(entropy_drift, 3),
                ethical_drift=round(ethical_drift, 3),
                temporal_factor=round(temporal_factor, 3),
                tag="ΛDELTA",
            )

            return min(1.0, max(0.0, drift_score))

        except Exception as e:
            logger.error(
                "Error calculating symbolic drift",
                error=str(e),
                current_symbols=current_symbols[:5],  # Limit for logging
                prior_symbols=prior_symbols[:5],
                tag="ΛTRACE",
            )
            return 0.0

    def register_symbolic_state(
        self, session_id: str, symbols: list[str], metadata: dict[str, Any]
    ) -> None:
        """
        Stores symbolic state snapshot for future drift comparison.

        Creates comprehensive state representation including emotional vectors,
        ethical alignment, entropy calculations, and contextual metadata.

        Args:
            session_id: Unique session identifier
            symbols: Current GLYPH/ΛTAG symbolic state
            metadata: Additional state context (emotions, ethics, timestamps)
        """
        timestamp = datetime.now()

        # Calculate state entropy
        entropy = self._calculate_state_entropy(symbols, metadata)

        # Extract emotional vector with validation
        emotional_vector = metadata.get("emotional_vector", [0.0, 0.0, 0.0])
        if not isinstance(emotional_vector, list) or len(emotional_vector) < 3:
            emotional_vector = [0.0, 0.0, 0.0]  # Default VAD vector

        # Extract ethical alignment with validation
        ethical_alignment = metadata.get("ethical_alignment", 0.5)
        if not isinstance(ethical_alignment, (int, float)):
            ethical_alignment = 0.5

        # Generate state hash for comparison
        state_hash = self._generate_state_hash(
            symbols, emotional_vector, ethical_alignment
        )

        # Create symbolic state snapshot
        symbolic_state = SymbolicState(
            session_id=session_id,
            timestamp=timestamp,
            symbols=symbols[:],  # Copy to prevent mutation
            emotional_vector=emotional_vector[:],
            ethical_alignment=float(ethical_alignment),
            entropy=entropy,
            context_metadata=metadata.copy(),
            hash_signature=state_hash,
        )

        # Store state with session history management
        self.symbolic_states[session_id].append(symbolic_state)

        # Maintain session history limits
        if len(self.symbolic_states[session_id]) > self.max_session_history:
            self.symbolic_states[session_id] = self.symbolic_states[session_id][
                -self.max_session_history :
            ]

        logger.info(
            "Symbolic state registered",
            session_id=session_id,
            symbol_count=len(symbols),
            entropy=round(entropy, 3),
            emotional_vector=emotional_vector,
            ethical_alignment=round(ethical_alignment, 3),
            state_hash=state_hash[:8],
            tag="ΛTRACE",
        )

        # Perform drift analysis if prior states exist
        if len(self.symbolic_states[session_id]) > 1:
            self._analyze_drift_for_session(session_id)

    def detect_recursive_drift_loops(self, symbol_sequences: list[list[str]]) -> bool:
        """
        Detects repeated symbolic recursion patterns indicating potential loops.

        Analyzes symbol sequences for recurring patterns that might indicate
        problematic feedback loops (e.g., dream → collapse → dream → collapse).

        Args:
            symbol_sequences: List of symbol sequences to analyze for patterns

        Returns:
            bool: True if recursive patterns detected, False otherwise
        """
        if len(symbol_sequences) < 3:
            return False

        logger.debug(
            "Analyzing recursive drift patterns",
            sequence_count=len(symbol_sequences),
            window_size=self.recursive_detection_window,
            tag="ΛDRIFT",
        )

        try:
            # 1. Exact sequence matching
            exact_loops = self._detect_exact_sequence_loops(symbol_sequences)

            # 2. Pattern similarity analysis
            similar_patterns = self._detect_similar_pattern_loops(symbol_sequences)

            # 3. Symbol frequency oscillation
            frequency_loops = self._detect_frequency_oscillations(symbol_sequences)

            # 4. Cascade pattern detection
            cascade_patterns = self._detect_cascade_patterns(symbol_sequences)

            has_recursion = any(
                [exact_loops, similar_patterns, frequency_loops, cascade_patterns]
            )

            if has_recursion:
                loop_indicators = []
                if exact_loops:
                    loop_indicators.append("exact_sequence_repetition")
                if similar_patterns:
                    loop_indicators.append("pattern_similarity_loops")
                if frequency_loops:
                    loop_indicators.append("symbol_frequency_oscillation")
                if cascade_patterns:
                    loop_indicators.append("cascade_pattern_detected")

                logger.warning(
                    "Recursive drift loops detected",
                    loop_types=loop_indicators,
                    sequence_length=len(symbol_sequences),
                    tag="ΛDRIFT",
                )

                # Store pattern for analysis
                pattern_key = f"recursive_{datetime.now().isoformat()}"
                self.recursive_patterns[pattern_key] = loop_indicators

            return has_recursion

        except Exception as e:
            logger.error(
                "Error detecting recursive drift loops",
                error=str(e),
                sequence_count=len(symbol_sequences),
                tag="ΛTRACE",
            )
            return False

    def emit_drift_alert(self, score: float, context: dict[str, Any]) -> None:
        """
        Logs drift spikes and triggers safety emitters for critical thresholds.

        Implements tiered alerting system with escalating responses based on
        drift severity. Includes safety mechanisms for CASCADE phase drift.

        Args:
            score: Drift score (0.0-1.0)
            context: Alert context including session info and metadata
        """
        timestamp = datetime.now()

        # Determine alert level based on thresholds
        if score >= self.drift_thresholds["cascade"]:
            alert_level = "CASCADE"
            risk_level = "CRITICAL"
        elif score >= self.drift_thresholds["critical"]:
            alert_level = "CRITICAL"
            risk_level = "HIGH"
        elif score >= self.drift_thresholds["warning"]:
            alert_level = "WARNING"
            risk_level = "MEDIUM"
        elif score >= self.drift_thresholds["caution"]:
            alert_level = "CAUTION"
            risk_level = "LOW"
        else:
            return  # No alert needed for low drift

        alert_data = {
            "timestamp": timestamp.isoformat(),
            "drift_score": score,
            "alert_level": alert_level,
            "risk_level": risk_level,
            "session_id": context.get("session_id", "unknown"),
            "context": context,
            "thresholds": self.drift_thresholds,
        }

        # ΛPHASE: Log phase-specific alerts
        logger.warning(
            f"Symbolic drift alert - {alert_level}",
            drift_score=round(score, 3),
            alert_level=alert_level,
            risk_level=risk_level,
            session_id=context.get("session_id"),
            tag="ΛPHASE",
        )

        # Store alert in history
        self.alert_history.append(alert_data)

        # CASCADE phase safety measures
        if alert_level == "CASCADE":
            self._trigger_cascade_safety_measures(score, context)

        # Emit to external systems
        self._emit_to_external_systems(alert_data)

    # ΛDRIFT_POINT: Implementation of core drift calculation methods

    def _calculate_symbol_set_drift(
        self, current: list[str], prior: list[str]
    ) -> float:
        """Calculate drift based on symbol set overlap and divergence."""
        if not current and not prior:
            return 0.0

        current_set = set(current)
        prior_set = set(prior)

        # Jaccard distance with frequency weighting
        intersection = len(current_set.intersection(prior_set))
        union = len(current_set.union(prior_set))

        if union == 0:
            return 0.0

        jaccard_similarity = intersection / union
        jaccard_distance = 1.0 - jaccard_similarity

        # Frequency analysis for weighted drift
        current_freq = {symbol: current.count(symbol) for symbol in current_set}
        prior_freq = {symbol: prior.count(symbol) for symbol in prior_set}

        frequency_drift = 0.0
        all_symbols = current_set.union(prior_set)

        for symbol in all_symbols:
            curr_freq = current_freq.get(symbol, 0)
            prev_freq = prior_freq.get(symbol, 0)
            max_freq = max(curr_freq, prev_freq, 1)
            frequency_drift += abs(curr_freq - prev_freq) / max_freq

        frequency_drift = frequency_drift / len(all_symbols) if all_symbols else 0.0

        # Combine Jaccard distance with frequency drift
        symbol_drift = (jaccard_distance * 0.7) + (frequency_drift * 0.3)

        return min(1.0, symbol_drift)

    def _calculate_emotional_drift(self, context: dict[str, Any]) -> float:
        """Calculate emotional vector drift from context."""
        current_emotion = context.get("current_emotional_vector", [0.0, 0.0, 0.0])
        prior_emotion = context.get("prior_emotional_vector", [0.0, 0.0, 0.0])

        if len(current_emotion) < 3 or len(prior_emotion) < 3:
            return 0.0

        # Euclidean distance in VAD space
        emotional_distance = math.sqrt(
            sum(
                (curr - prev) ** 2 for curr, prev in zip(current_emotion, prior_emotion)
            )
        )

        # Normalize by maximum possible distance in VAD space (sqrt(3) for [-1,1] range)
        max_distance = math.sqrt(3)
        emotional_drift = min(1.0, emotional_distance / max_distance)

        return emotional_drift

    def _calculate_entropy_drift(self, current: list[str], prior: list[str]) -> float:
        """Calculate entropy change between symbol sets."""
        current_entropy = self._calculate_shannon_entropy(current)
        prior_entropy = self._calculate_shannon_entropy(prior)

        entropy_delta = abs(current_entropy - prior_entropy)

        # Normalize by maximum possible entropy change
        max_entropy = math.log2(max(len(set(current + prior)), 1))
        entropy_drift = (
            min(1.0, entropy_delta / max_entropy) if max_entropy > 0 else 0.0
        )

        return entropy_drift

    def _calculate_ethical_drift(self, context: dict[str, Any]) -> float:
        """Calculate ethical alignment drift from context."""
        current_ethics = context.get("current_ethical_alignment", 0.5)
        prior_ethics = context.get("prior_ethical_alignment", 0.5)

        if not isinstance(current_ethics, (int, float)) or not isinstance(
            prior_ethics, (int, float)
        ):
            return 0.0

        ethical_drift = abs(current_ethics - prior_ethics)

        return min(1.0, ethical_drift)

    def _calculate_temporal_decay(self, context: dict[str, Any]) -> float:
        """Calculate temporal decay factor for drift weighting."""
        timestamp = context.get("timestamp")
        prior_timestamp = context.get("prior_timestamp")

        if not timestamp or not prior_timestamp:
            return 0.0

        try:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            if isinstance(prior_timestamp, str):
                prior_timestamp = datetime.fromisoformat(
                    prior_timestamp.replace("Z", "+00:00")
                )

            time_delta = timestamp - prior_timestamp
            hours_elapsed = time_delta.total_seconds() / 3600

            # Exponential decay factor
            decay_factor = math.exp(-self.entropy_decay_rate * hours_elapsed)
            temporal_drift = 1.0 - decay_factor

            return min(1.0, temporal_drift)

        except Exception:
            return 0.0

    def _apply_nonlinear_scaling(self, weighted_score: float) -> float:
        """Apply non-linear scaling to emphasize critical drift levels."""
        # Sigmoid-based scaling to emphasize high drift scores
        scaled = 1.0 / (1.0 + math.exp(-10 * (weighted_score - 0.5)))
        return scaled

    def _calculate_state_entropy(
        self, symbols: list[str], metadata: dict[str, Any]
    ) -> float:
        """Calculate comprehensive state entropy including symbols and metadata."""
        # Symbol entropy
        symbol_entropy = self._calculate_shannon_entropy(symbols)

        # Emotional entropy (if available)
        emotional_vector = metadata.get("emotional_vector", [])
        emotional_entropy = 0.0
        if emotional_vector:
            # Calculate entropy of emotional dimensions
            total_magnitude = sum(abs(x) for x in emotional_vector)
            if total_magnitude > 0:
                probabilities = [abs(x) / total_magnitude for x in emotional_vector]
                emotional_entropy = -sum(
                    p * math.log2(p + 1e-9) for p in probabilities if p > 0
                )

        # Combine entropies
        combined_entropy = (symbol_entropy * 0.7) + (emotional_entropy * 0.3)

        return combined_entropy

    def _calculate_shannon_entropy(self, symbols: list[str]) -> float:
        """Calculate Shannon entropy for a list of symbols."""
        if not symbols:
            return 0.0

        symbol_counts = {}
        for symbol in symbols:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        total_symbols = len(symbols)
        entropy = 0.0

        for count in symbol_counts.values():
            probability = count / total_symbols
            entropy -= probability * math.log2(probability)

        return entropy

    def _generate_state_hash(
        self,
        symbols: list[str],
        emotional_vector: list[float],
        ethical_alignment: float,
    ) -> str:
        """Generate hash signature for state comparison."""
        state_string = json.dumps(
            {
                "symbols": sorted(symbols),
                "emotional_vector": [round(x, 3) for x in emotional_vector],
                "ethical_alignment": round(ethical_alignment, 3),
            },
            sort_keys=True,
        )

        return hashlib.sha256(state_string.encode()).hexdigest()

    def _analyze_drift_for_session(self, session_id: str) -> None:
        """Analyze drift for a specific session with the latest state."""
        states = self.symbolic_states[session_id]
        if len(states) < 2:
            return

        current_state = states[-1]
        prior_state = states[-2]

        # Prepare context for drift calculation
        context = {
            "session_id": session_id,
            "timestamp": current_state.timestamp,
            "prior_timestamp": prior_state.timestamp,
            "current_emotional_vector": current_state.emotional_vector,
            "prior_emotional_vector": prior_state.emotional_vector,
            "current_ethical_alignment": current_state.ethical_alignment,
            "prior_ethical_alignment": prior_state.ethical_alignment,
            "current_entropy": current_state.entropy,
            "prior_entropy": prior_state.entropy,
        }

        # Calculate drift score
        drift_score = self.calculate_symbolic_drift(
            current_state.symbols, prior_state.symbols, context
        )

        # Check for alerts
        if drift_score >= self.drift_thresholds["caution"]:
            self.emit_drift_alert(drift_score, context)

    def _detect_exact_sequence_loops(self, sequences: list[list[str]]) -> bool:
        """Detect exact repeating sequences in symbol patterns."""
        if len(sequences) < 4:
            return False

        # Convert sequences to strings for pattern matching
        sequence_strings = [",".join(seq) for seq in sequences]

        # Look for repeating patterns of length 2-5
        for pattern_length in range(2, min(6, len(sequences) // 2 + 1)):
            for start_idx in range(len(sequences) - 2 * pattern_length + 1):
                pattern = sequence_strings[start_idx : start_idx + pattern_length]
                next_pattern = sequence_strings[
                    start_idx + pattern_length : start_idx + 2 * pattern_length
                ]

                if pattern == next_pattern:
                    return True

        return False

    def _detect_similar_pattern_loops(self, sequences: list[list[str]]) -> bool:
        """Detect similar (not exact) repeating patterns."""
        if len(sequences) < 6:
            return False

        # Calculate similarity between sequences using Jaccard index
        similarities = []
        for i in range(len(sequences) - 3):
            for j in range(i + 3, len(sequences)):
                seq1_set = set(sequences[i])
                seq2_set = set(sequences[j])

                if not seq1_set and not seq2_set:
                    similarity = 1.0
                elif not seq1_set or not seq2_set:
                    similarity = 0.0
                else:
                    intersection = len(seq1_set.intersection(seq2_set))
                    union = len(seq1_set.union(seq2_set))
                    similarity = intersection / union if union > 0 else 0.0

                similarities.append(similarity)

        # Check for high similarity patterns
        high_similarity_count = sum(1 for sim in similarities if sim > 0.8)
        return high_similarity_count >= 3

    def _detect_frequency_oscillations(self, sequences: list[list[str]]) -> bool:
        """Detect symbol frequency oscillations indicating loops."""
        if len(sequences) < 5:
            return False

        # Track symbol frequencies over time
        all_symbols = set()
        for seq in sequences:
            all_symbols.update(seq)

        for symbol in all_symbols:
            frequencies = []
            for seq in sequences:
                freq = seq.count(symbol) / len(seq) if seq else 0.0
                frequencies.append(freq)

            # Check for oscillating pattern in frequencies
            if self._is_oscillating_pattern(frequencies):
                return True

        return False

    def _is_oscillating_pattern(
        self, values: list[float], threshold: float = 0.3
    ) -> bool:
        """Check if a list of values shows oscillating pattern."""
        if len(values) < 4:
            return False

        # Simple oscillation detection: alternating high/low values
        oscillations = 0
        for i in range(1, len(values) - 1):
            if ((values[i] > values[i - 1] and values[i] > values[i + 1]) or (
                values[i] < values[i - 1] and values[i] < values[i + 1]
            )) and abs(values[i] - values[i - 1]) > threshold:
                oscillations += 1

        return oscillations >= 2

    def _detect_cascade_patterns(self, sequences: list[list[str]]) -> bool:
        """Detect cascade patterns indicating potential system instability."""
        if len(sequences) < 3:
            return False

        # Look for increasing symbol diversity (potential cascade)
        diversities = [len(set(seq)) for seq in sequences]

        # Check for rapid diversity increase
        for i in range(len(diversities) - 2):
            if (
                diversities[i + 1] > diversities[i] * 1.5
                and diversities[i + 2] > diversities[i + 1] * 1.5
            ):
                return True

        # Look for cascade-related symbols
        cascade_symbols = [
            "ΛCASCADE",
            "ΛCOLLAPSE",
            "ΛCRISIS",
            "ΛEMERGENCY",
            "ΛOVERLOAD",
        ]
        for seq in sequences[-3:]:  # Check recent sequences
            cascade_count = sum(
                1 for symbol in seq if any(cs in symbol for cs in cascade_symbols)
            )
            if cascade_count >= 2:
                return True

        return False

    def _trigger_cascade_safety_measures(
        self, score: float, context: dict[str, Any]
    ) -> None:
        """Trigger safety measures for CASCADE phase drift."""
        logger.critical(
            "CASCADE PHASE DRIFT DETECTED - Triggering safety measures",
            drift_score=score,
            session_id=context.get("session_id"),
            safety_measures="symbolic_quarantine",
            tag="ΛPHASE",
        )

        # Implement symbolic quarantine
        session_id = context.get("session_id")
        if session_id:
            self._implement_symbolic_quarantine(session_id)

        # Alert external collapse reasoner
        self._alert_collapse_reasoner(score, context)

    def _implement_symbolic_quarantine(self, session_id: str) -> None:
        """Implement symbolic quarantine for unstable sessions."""
        quarantine_marker = f"ΛQUARANTINE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if session_id in self.symbolic_states:
            # Mark latest state with quarantine
            latest_state = self.symbolic_states[session_id][-1]
            latest_state.context_metadata["quarantine_status"] = "ACTIVE"
            latest_state.context_metadata["quarantine_marker"] = quarantine_marker

        logger.warning(
            "Symbolic quarantine implemented",
            session_id=session_id,
            quarantine_marker=quarantine_marker,
            tag="ΛPHASE",
        )

    def _alert_collapse_reasoner(self, score: float, context: dict[str, Any]) -> None:
        """Alert collapse reasoner system of critical drift."""
        alert_payload = {
            "alert_type": "SYMBOLIC_DRIFT_CASCADE",
            "drift_score": score,
            "timestamp": datetime.now().isoformat(),
            "session_id": context.get("session_id"),
            "context": context,
            "recommended_action": "IMMEDIATE_INTERVENTION",
        }

        # In production, this would emit to actual collapse reasoner
        logger.critical("COLLAPSE REASONER ALERT", payload=alert_payload, tag="ΛPHASE")

    def _emit_to_external_systems(self, alert_data: dict[str, Any]) -> None:
        """Emit drift alerts to external diagnostic and monitoring systems."""
        emission_targets = ["diagnostics/", "dream/", "memory/fold_engine.py"]

        for target in emission_targets:
            logger.info(
                f"Emitting drift alert to {target}",
                alert_data=alert_data,
                target_system=target,
                tag="ΛTRACE",
            )

        # JSON emitter for UI telemetry / Mesh diagnostics
        try:
            telemetry_data = {
                "type": "symbolic_drift_alert",
                "timestamp": alert_data["timestamp"],
                "score": alert_data["drift_score"],
                "level": alert_data["alert_level"],
                "session": alert_data["session_id"],
            }

            # In production, this would emit to actual mesh/UI systems
            logger.info(
                "Mesh telemetry emission", telemetry=telemetry_data, tag="ΛTRACE"
            )

        except Exception as e:
            logger.error("Failed to emit telemetry data", error=str(e), tag="ΛTRACE")

    # Legacy compatibility methods (maintaining interface)

    def record_drift(
        self, symbol_id: str, current_state: dict, reference_state: dict, context: str
    ):
        """Legacy compatibility method for record_drift interface."""
        # Convert legacy format to new format
        current_symbols = current_state.get("symbols", [])
        reference_symbols = reference_state.get("symbols", [])

        metadata = {
            "emotional_vector": current_state.get("emotional_vector", [0.0, 0.0, 0.0]),
            "ethical_alignment": current_state.get("ethical_alignment", 0.5),
            "context": context,
            "legacy_call": True,
        }

        # Use session ID as symbol_id for compatibility
        self.register_symbolic_state(symbol_id, current_symbols, metadata)

        # Calculate drift score
        drift_context = {
            "session_id": symbol_id,
            "current_emotional_vector": current_state.get(
                "emotional_vector", [0.0, 0.0, 0.0]
            ),
            "prior_emotional_vector": reference_state.get(
                "emotional_vector", [0.0, 0.0, 0.0]
            ),
            "current_ethical_alignment": current_state.get("ethical_alignment", 0.5),
            "prior_ethical_alignment": reference_state.get("ethical_alignment", 0.5),
            "timestamp": datetime.now(),
            "prior_timestamp": datetime.now() - timedelta(hours=1),
        }

        drift_score = self.calculate_symbolic_drift(
            current_symbols, reference_symbols, drift_context
        )

        # Check for alerts
        if drift_score >= self.drift_thresholds["caution"]:
            self.emit_drift_alert(drift_score, drift_context)

    def register_drift(self, drift_magnitude: float, metadata: dict):
        """Legacy compatibility method for register_drift interface."""
        logger.info(
            "Legacy drift registration",
            drift_magnitude=drift_magnitude,
            metadata=metadata,
            tag="ΛTRACE",
        )

        # Store in drift records for compatibility
        drift_event = {
            "drift_magnitude": drift_magnitude,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
        }
        self.drift_records.append(drift_event)

    def calculate_entropy(self, symbol_id: str) -> float:
        """Calculate symbolic entropy for a given symbol/session."""
        if symbol_id not in self.symbolic_states:
            return 0.0

        states = self.symbolic_states[symbol_id]
        if not states:
            return 0.0

        # Return entropy of most recent state
        latest_state = states[-1]
        return latest_state.entropy

    def log_phase_mismatch(
        self, symbol_id: str, phase_a: str, phase_b: str, mismatch_details: dict
    ):
        """Log mismatch between symbolic phases with detailed analysis."""
        logger.warning(
            "Symbolic phase mismatch detected",
            symbol_id=symbol_id,
            phase_a=phase_a,
            phase_b=phase_b,
            details=mismatch_details,
            tag="ΛPHASE",
        )

        # Analyze phase mismatch severity
        mismatch_score = self._calculate_phase_mismatch_score(
            phase_a, phase_b, mismatch_details
        )

        if mismatch_score > 0.7:
            # High severity phase mismatch
            self.emit_drift_alert(
                mismatch_score,
                {
                    "session_id": symbol_id,
                    "alert_type": "phase_mismatch",
                    "phase_a": phase_a,
                    "phase_b": phase_b,
                    "mismatch_details": mismatch_details,
                },
            )

    def _calculate_phase_mismatch_score(
        self, phase_a: str, phase_b: str, details: dict
    ) -> float:
        """Calculate severity score for phase mismatches."""
        # Basic scoring based on phase difference and details
        phase_severity = {
            "expected_reasoning_path": 0.3,
            "actual_reasoning_path_diverged": 0.8,
            "cascade_phase": 0.9,
            "collapse_phase": 1.0,
        }

        score_a = phase_severity.get(phase_a, 0.5)
        score_b = phase_severity.get(phase_b, 0.5)

        base_score = abs(score_a - score_b)

        # Factor in deviation score from details
        deviation_score = details.get("deviation_score", 0.0)
        combined_score = (base_score + deviation_score) / 2.0

        return min(1.0, combined_score)

    def summarize_drift(self, time_window: str = "all") -> dict:
        """Generate comprehensive drift summary with analytics."""
        current_time = datetime.now()

        # Parse time window
        if time_window == "all":
            start_time = None
        elif time_window.endswith("h"):
            hours = int(time_window[:-1])
            start_time = current_time - timedelta(hours=hours)
        elif time_window.endswith("d"):
            days = int(time_window[:-1])
            start_time = current_time - timedelta(days=days)
        else:
            start_time = None

        # Collect relevant states and alerts
        total_sessions = len(self.symbolic_states)
        total_states = sum(len(states) for states in self.symbolic_states.values())

        # Filter alerts by time window
        relevant_alerts = []
        if start_time:
            for alert in self.alert_history:
                alert_time = datetime.fromisoformat(alert["timestamp"])
                if alert_time >= start_time:
                    relevant_alerts.append(alert)
        else:
            relevant_alerts = list(self.alert_history)

        # Calculate summary statistics
        alert_counts = {"CAUTION": 0, "WARNING": 0, "CRITICAL": 0, "CASCADE": 0}
        total_drift_score = 0.0
        alert_count = len(relevant_alerts)

        for alert in relevant_alerts:
            level = alert["alert_level"]
            alert_counts[level] = alert_counts.get(level, 0) + 1
            total_drift_score += alert["drift_score"]

        average_drift = total_drift_score / alert_count if alert_count > 0 else 0.0

        # Risk assessment
        risk_level = "LOW"
        if alert_counts["CASCADE"] > 0:
            risk_level = "CRITICAL"
        elif alert_counts["CRITICAL"] > 0:
            risk_level = "HIGH"
        elif alert_counts["WARNING"] > 2:
            risk_level = "MEDIUM"

        summary = {
            "time_window": time_window,
            "analysis_timestamp": current_time.isoformat(),
            "total_sessions": total_sessions,
            "total_states": total_states,
            "alert_summary": {
                "total_alerts": alert_count,
                "alert_breakdown": alert_counts,
                "average_drift_score": round(average_drift, 3),
                "risk_level": risk_level,
            },
            "recursive_patterns": len(self.recursive_patterns),
            "active_quarantines": self._count_active_quarantines(),
            "system_health": (
                "stable" if risk_level in ["LOW", "MEDIUM"] else "unstable"
            ),
            "recommendations": self._generate_recommendations(alert_counts, risk_level),
        }

        logger.info(
            "Drift summary generated",
            time_window=time_window,
            total_alerts=alert_count,
            risk_level=risk_level,
            system_health=summary["system_health"],
            tag="ΛTRACE",
        )

        return summary

    def _count_active_quarantines(self) -> int:
        """Count sessions with active quarantine status."""
        quarantine_count = 0
        for states in self.symbolic_states.values():
            if (
                states
                and states[-1].context_metadata.get("quarantine_status") == "ACTIVE"
            ):
                quarantine_count += 1
        return quarantine_count

    def _generate_recommendations(
        self, alert_counts: dict[str, int], risk_level: str
    ) -> list[str]:
        """Generate recommendations based on drift analysis."""
        recommendations = []

        if risk_level == "CRITICAL":
            recommendations.append(
                "IMMEDIATE: Review CASCADE phase sessions for instability"
            )
            recommendations.append("IMMEDIATE: Implement additional safety constraints")

        if alert_counts.get("CASCADE", 0) > 0:
            recommendations.append("Investigate symbolic quarantine effectiveness")

        if alert_counts.get("WARNING", 0) > 5:
            recommendations.append("Consider adjusting drift sensitivity thresholds")

        if len(self.recursive_patterns) > 3:
            recommendations.append("Analyze recursive pattern causes")

        if not recommendations:
            recommendations.append("System operating within normal parameters")

        return recommendations


# Main execution for testing and demonstration
if __name__ == "__main__":
    print("🔍 LUKHAS Symbolic Drift Tracker - Enterprise Implementation")
    print("=" * 60)

    # Initialize tracker with enterprise configuration
    config = {
        "caution_threshold": 0.3,
        "warning_threshold": 0.5,
        "critical_threshold": 0.7,
        "cascade_threshold": 0.85,
        "entropy_decay_rate": 0.08,
        "temporal_window_hours": 12,
        "max_session_history": 500,
    }

    tracker = SymbolicDriftTracker(config)

    # Test symbolic state registration
    print("\n📊 Testing Symbolic State Registration...")

    session_id = "test_session_001"

    # Initial state
    initial_symbols = ["ΛAWARE", "ΛTRACE", "hope", "stability"]
    initial_metadata = {
        "emotional_vector": [0.6, 0.3, 0.7],  # VAD: positive, calm, strong
        "ethical_alignment": 0.85,
        "context": "Initial reasoning session",
    }

    tracker.register_symbolic_state(session_id, initial_symbols, initial_metadata)

    # Evolved state with drift
    evolved_symbols = ["ΛAWARE", "ΛDRIFT", "uncertainty", "ΛPHASE", "cascade"]
    evolved_metadata = {
        "emotional_vector": [0.2, 0.8, 0.4],  # VAD: negative, aroused, weak
        "ethical_alignment": 0.65,
        "context": "Post-reasoning drift detected",
    }

    tracker.register_symbolic_state(session_id, evolved_symbols, evolved_metadata)

    # Test drift calculation
    print("\n🎯 Testing Drift Calculation...")

    drift_context = {
        "session_id": session_id,
        "current_emotional_vector": evolved_metadata["emotional_vector"],
        "prior_emotional_vector": initial_metadata["emotional_vector"],
        "current_ethical_alignment": evolved_metadata["ethical_alignment"],
        "prior_ethical_alignment": initial_metadata["ethical_alignment"],
        "timestamp": datetime.now(),
        "prior_timestamp": datetime.now() - timedelta(hours=2),
    }

    drift_score = tracker.calculate_symbolic_drift(
        evolved_symbols, initial_symbols, drift_context
    )

    print(f"Calculated Drift Score: {drift_score:.3f}")

    # Test recursive pattern detection
    print("\n🔄 Testing Recursive Pattern Detection...")

    symbol_sequences = [
        ["ΛDREAM", "hope", "exploration"],
        ["ΛCOLLAPSE", "fear", "ΛDRIFT"],
        ["ΛDREAM", "hope", "exploration"],  # Repeat
        ["ΛCOLLAPSE", "fear", "ΛDRIFT"],  # Repeat
        ["ΛCASCADE", "ΛEMERGENCY"],  # Escalation
    ]

    has_recursion = tracker.detect_recursive_drift_loops(symbol_sequences)
    print(f"Recursive Patterns Detected: {has_recursion}")

    # Test cascade alert
    print("\n🚨 Testing CASCADE Alert System...")

    cascade_symbols = ["ΛCASCADE", "ΛCRISIS", "ΛOVERLOAD", "instability"]
    cascade_metadata = {
        "emotional_vector": [-0.8, 0.9, 0.1],  # Extreme negative, high arousal
        "ethical_alignment": 0.3,  # Low ethical alignment
        "context": "System instability cascade detected",
    }

    tracker.register_symbolic_state(session_id, cascade_symbols, cascade_metadata)

    # Generate comprehensive summary
    print("\n📋 Generating Drift Summary...")

    summary = tracker.summarize_drift("24h")
    print(f"System Health: {summary['system_health']}")
    print(f"Total Alerts: {summary['alert_summary']['total_alerts']}")
    print(f"Risk Level: {summary['alert_summary']['risk_level']}")
    print(f"Active Quarantines: {summary['active_quarantines']}")

    print("\n📝 Recommendations:")
    for rec in summary["recommendations"]:
        print(f"  • {rec}")

    print("\n✅ Enterprise Symbolic Drift Tracker Implementation Complete")
    print(f"📊 Sessions Tracked: {len(tracker.symbolic_states)}")
    print(f"🎯 Drift Records: {len(tracker.drift_records)}")
    print(f"🚨 Alert History: {len(tracker.alert_history)}")
    print(f"🔄 Recursive Patterns: {len(tracker.recursive_patterns)}")
