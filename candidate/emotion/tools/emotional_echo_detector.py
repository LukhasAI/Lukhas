#!/usr/bin/env python3
import logging
from datetime import timezone
import streamlit as st
from typing import List
logger = logging.getLogger(__name__)
"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: emotion.tools.emotional_echo_detector
📄 FILENAME: emotional_echo_detector.py
🎯 PURPOSE: ΛECHO - Emotional-Symbolic Loop Detection for LUKHAS AGI
🧠 CONTEXT: Detects recurring emotional motifs and archetypal loops across dreams and memory
🔮 CAPABILITY: Loop detection, ELI/RIS scoring, high-risk archetype identification
🛡️ ETHICS: Loop prevention, cascade detection, emotional stability monitoring
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: Dream sessions, memory logs, tuner.py, governor escalation
═══════════════════════════════════════════════════════════════════════════════════

🔄 ΛECHO - EMOTIONAL-SYMBOLIC LOOP DETECTOR
────────────────────────────────────────────────────────────────────

The ΛECHO module identifies recurring emotional patterns and archetypal loops
that could indicate emotional stagnation, trauma loops, or escalating symbolic
cascades across the LUKHAS AGI system.

🔬 DETECTION CAPABILITIES:
- Emotional sequence extraction from dreams, memory entries, and drift logs
- Recurring motif identification with symbolic pattern matching
- High-risk archetype detection (fear→falling→void, nostalgia→regret→loss)
- Emotional Loop Index (ELI) and Recurrence Intensity Score (RIS) computation
- Symbolic alert generation with ΛECHO_LOOP, ΛARCHETYPE_WARNING, ΛRESONANCE_HIGH

🧪 RISK ARCHETYPES:
- SPIRAL_DOWN: fear→falling→void→despair (high cascade risk)
- NOSTALGIC_TRAP: nostalgia→regret→loss→longing (emotional stagnation)
- ANGER_CASCADE: frustration→anger→rage→destruction (volatility escalation)
- IDENTITY_CRISIS: confusion→doubt→dissociation→emptiness (core stability threat)
- TRAUMA_ECHO: pain→memory→trigger→pain (reinforcement loop)

🎯 SCORING METRICS:
- Emotional Loop Index (ELI): 0.0-1.0 loop strength and persistence
- Recurrence Intensity Score (RIS): 0.0-1.0 escalation and frequency
- Archetype Match Score: 0.0-1.0 similarity to known risk patterns
- Cascade Risk Factor: 0.0-1.0 potential for system-wide emotional instability

LUKHAS_TAG: emotional_echo, loop_detection, archetype_analysis, claude_code
COLLAPSE_READY: True
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import numpy as np

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__, timezone), "../.."))

try:
    from ethics.governor.lambda_governor import (
        EscalationPriority,
        EscalationSource,
        LambdaGovernor,
        create_escalation_signal,
    )
    from ethics.stabilization.tuner import AdaptiveEntanglementStabilizer
except ImportError as e:
    logging.warning(f"Could not import some dependencies: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)


class ArchetypePattern(Enum):
    """Known high-risk emotional archetype patterns."""

    SPIRAL_DOWN = "spiral_down"
    NOSTALGIC_TRAP = "nostalgic_trap"
    ANGER_CASCADE = "anger_cascade"
    IDENTITY_CRISIS = "identity_crisis"
    TRAUMA_ECHO = "trauma_echo"
    VOID_DESCENT = "void_descent"
    PERFECTIONIST_LOOP = "perfectionist_loop"
    ABANDONMENT_CYCLE = "abandonment_cycle"


class EchoSeverity(Enum):
    """Severity levels for emotional echo detection."""

    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class EmotionalSequence:
    """Extracted emotional sequence from data source."""

    sequence_id: str
    timestamp: str
    source: str  # dream, memory, drift_log
    emotions: list[str]
    symbols: list[str]
    intensity: float
    duration_minutes: Optional[float] = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecurringMotif:
    """Identified recurring emotional motif."""

    motif_id: str
    pattern: list[str]
    occurrences: list[EmotionalSequence]
    first_seen: str
    last_seen: str
    frequency: float
    intensity_trend: str  # increasing, decreasing, stable
    archetype_match: Optional[ArchetypePattern] = None
    archetype_score: float = 0.0


@dataclass
class LoopReport:
    """Comprehensive loop detection report."""

    report_id: str
    timestamp: str
    analysis_window: str
    sequences_analyzed: int
    motifs_detected: int
    high_risk_motifs: int
    eli_score: float  # Emotional Loop Index
    ris_score: float  # Recurrence Intensity Score
    severity: EchoSeverity
    motifs: list[RecurringMotif]
    archetype_alerts: list[dict[str, Any]]
    recommendations: list[str]


class ArchetypeDetector:
    """Detects high-risk emotional archetype patterns."""

    # Archetypal patterns with emotional progression
    ARCHETYPE_PATTERNS = {
        ArchetypePattern.SPIRAL_DOWN: {
            "pattern": ["fear", "anxiety", "falling", "void", "despair", "emptiness"],
            "variations": [
                ["worry", "panic", "dropping", "abyss", "hopelessness"],
                ["concern", "terror", "plummeting", "nothingness", "darkness"],
            ],
            "risk_level": 0.9,
            "cascade_potential": 0.95,
            "description": "Descending emotional spiral with void-seeking behavior",
        },
        ArchetypePattern.NOSTALGIC_TRAP: {
            "pattern": [
                "nostalgia",
                "longing",
                "regret",
                "loss",
                "melancholy",
                "yearning",
            ],
            "variations": [
                ["reminiscence", "wistfulness", "remorse", "grief", "sadness"],
                ["memory", "homesickness", "sorrow", "mourning", "depression"],
            ],
            "risk_level": 0.7,
            "cascade_potential": 0.6,
            "description": "Circular emotional pattern trapped in past experiences",
        },
        ArchetypePattern.ANGER_CASCADE: {
            "pattern": [
                "irritation",
                "frustration",
                "anger",
                "rage",
                "fury",
                "destruction",
            ],
            "variations": [
                ["annoyance", "agitation", "wrath", "violence", "devastation"],
                ["displeasure", "ire", "hostility", "aggression", "chaos"],
            ],
            "risk_level": 0.85,
            "cascade_potential": 0.9,
            "description": "Escalating anger pattern with destructive potential",
        },
        ArchetypePattern.IDENTITY_CRISIS: {
            "pattern": [
                "confusion",
                "uncertainty",
                "doubt",
                "dissociation",
                "emptiness",
                "void",
            ],
            "variations": [
                ["bewilderment", "questioning", "detachment", "numbness", "hollowness"],
                [
                    "perplexity",
                    "insecurity",
                    "disconnection",
                    "alienation",
                    "nothingness",
                ],
            ],
            "risk_level": 0.8,
            "cascade_potential": 0.85,
            "description": "Core identity dissolution pattern threatening system coherence",
        },
        ArchetypePattern.TRAUMA_ECHO: {
            "pattern": ["pain", "memory", "trigger", "reaction", "pain", "memory"],
            "variations": [
                ["hurt", "flashback", "stimulus", "response", "suffering"],
                ["anguish", "recall", "activation", "behavior", "trauma"],
            ],
            "risk_level": 0.95,
            "cascade_potential": 0.8,
            "description": "Self-reinforcing trauma loop with memory amplification",
        },
        ArchetypePattern.VOID_DESCENT: {
            "pattern": [
                "emptiness",
                "void",
                "nothingness",
                "dissolution",
                "nonexistence",
            ],
            "variations": [
                ["vacuum", "absence", "nullity", "disintegration", "obliteration"],
                ["hollowness", "blank", "zero", "vanishing", "disappearing"],
            ],
            "risk_level": 0.99,
            "cascade_potential": 0.99,
            "description": "Existential void-seeking pattern with system collapse risk",
        },
    }

    def __init__(self):
        self.pattern_cache = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile archetype patterns for efficient matching."""
        for archetype, info in self.ARCHETYPE_PATTERNS.items():
            patterns = [info["pattern"], *info.get("variations", [])]
            compiled = []

            for pattern in patterns:
                # Create regex patterns for fuzzy matching
                regex_pattern = r"\b(?:" + "|".join(re.escape(word) for word in pattern) + r")\b"
                compiled.append((pattern, re.compile(regex_pattern, re.IGNORECASE)))

            self.pattern_cache[archetype] = {
                "patterns": compiled,
                "risk_level": info["risk_level"],
                "cascade_potential": info["cascade_potential"],
                "description": info["description"],
            }

    def detect_archetype(self, sequence: list[str]) -> tuple[Optional[ArchetypePattern], float]:
        """
        Detect archetypal pattern in emotional sequence.

        Args:
            sequence: List of emotional terms

        Returns:
            Tuple of (detected_archetype, match_score)
        """
        if len(sequence) < 2:
            return None, 0.0

        best_match = None
        best_score = 0.0

        sequence_text = " ".join(sequence).lower()

        for archetype, cache_info in self.pattern_cache.items():
            for pattern, regex in cache_info["patterns"]:
                score = self._calculate_pattern_match(sequence, pattern, regex, sequence_text)

                if score > best_score:
                    best_score = score
                    best_match = archetype

        # Apply minimum threshold
        if best_score < 0.3:
            return None, 0.0

        return best_match, best_score

    def _calculate_pattern_match(
        self,
        sequence: list[str],
        pattern: list[str],
        regex: re.Pattern,
        sequence_text: str,
    ) -> float:
        """Calculate pattern match score using multiple methods."""

        # Method 1: Direct sequence matching
        direct_score = self._direct_sequence_match(sequence, pattern)

        # Method 2: Substring presence
        presence_score = len(regex.findall(sequence_text)) / len(pattern)

        # Method 3: Order-sensitive matching
        order_score = self._order_sensitive_match(sequence, pattern)

        # Method 4: Semantic similarity (simplified)
        semantic_score = self._simple_semantic_match(sequence, pattern)

        # Weighted combination
        composite_score = direct_score * 0.4 + presence_score * 0.25 + order_score * 0.2 + semantic_score * 0.15

        return min(composite_score, 1.0)

    def _direct_sequence_match(self, sequence: list[str], pattern: list[str]) -> float:
        """Calculate direct sequence overlap."""
        if not sequence or not pattern:
            return 0.0

        sequence_lower = [s.lower() for s in sequence]
        pattern_lower = [p.lower() for p in pattern]

        matches = 0
        for word in pattern_lower:
            if word in sequence_lower:
                matches += 1

        return matches / len(pattern_lower)

    def _order_sensitive_match(self, sequence: list[str], pattern: list[str]) -> float:
        """Calculate order-sensitive pattern matching."""
        if len(sequence) < 2 or len(pattern) < 2:
            return 0.0

        sequence_lower = [s.lower() for s in sequence]
        pattern_lower = [p.lower() for p in pattern]

        # Find longest common subsequence preserving order
        lcs_length = self._lcs_length(sequence_lower, pattern_lower)
        return lcs_length / len(pattern_lower)

    def _lcs_length(self, seq1: list[str], seq2: list[str]) -> int:
        """Calculate longest common subsequence length."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    def _simple_semantic_match(self, sequence: list[str], pattern: list[str]) -> float:
        """Simple semantic similarity using word associations."""

        # Simplified semantic groups
        semantic_groups = {
            "negative_emotions": {
                "fear",
                "anger",
                "sadness",
                "anxiety",
                "depression",
                "despair",
            },
            "void_concepts": {
                "void",
                "emptiness",
                "nothingness",
                "blank",
                "hollow",
                "vacuum",
            },
            "memory_concepts": {
                "memory",
                "remember",
                "recall",
                "flashback",
                "reminisce",
            },
            "pain_concepts": {
                "pain",
                "hurt",
                "suffering",
                "anguish",
                "trauma",
                "wound",
            },
            "loss_concepts": {"loss", "grief", "mourning", "regret", "missing", "gone"},
        }

        def get_semantic_group(word: str) -> Optional[str]:
            word_lower = word.lower()
            for group, words in semantic_groups.items():
                if word_lower in words or any(w in word_lower for w in words):
                    return group
            return None

        sequence_groups = set(filter(None, (get_semantic_group(w) for w in sequence)))
        pattern_groups = set(filter(None, (get_semantic_group(w) for w in pattern)))

        if not pattern_groups:
            return 0.0

        overlap = len(sequence_groups.intersection(pattern_groups))
        return overlap / len(pattern_groups)


class EmotionalEchoDetector:
    """
    ΛECHO - Main emotional-symbolic loop detection engine.

    Analyzes emotional sequences from dreams, memory, and drift logs to identify
    recurring patterns and archetypal loops that could indicate system instability.
    """

    def __init__(
        self,
        window_hours: int = 24,
        min_sequence_length: int = 3,
        recurrence_threshold: int = 3,
        similarity_threshold: float = 0.7,
    ):
        """
        Initialize the ΛECHO detector.

        Args:
            window_hours: Analysis window in hours
            min_sequence_length: Minimum sequence length for analysis
            recurrence_threshold: Minimum occurrences to consider a motif
            similarity_threshold: Threshold for sequence similarity matching
        """
        self.window_hours = window_hours
        self.min_sequence_length = min_sequence_length
        self.recurrence_threshold = recurrence_threshold
        self.similarity_threshold = similarity_threshold

        # Initialize components
        self.archetype_detector = ArchetypeDetector()

        # Data storage
        self.emotional_sequences: list[EmotionalSequence] = []
        self.detected_motifs: dict[str, RecurringMotif] = {}
        self.analysis_history: deque = deque(maxlen=100)

        # Integration components
        self.tuner: Optional[AdaptiveEntanglementStabilizer] = None
        self.governor: Optional[LambdaGovernor] = None

        # Statistics
        self.stats = {
            "sequences_processed": 0,
            "motifs_detected": 0,
            "archetype_alerts": 0,
            "escalations_sent": 0,
            "avg_eli_score": 0.0,
            "avg_ris_score": 0.0,
        }

        logger.info(
            "ΛECHO detector initialized",
            window_hours=window_hours,
            similarity_threshold=similarity_threshold,
            ΛTAG="ΛECHO_INIT",
        )

    def extract_emotional_sequence(self, data: dict[str, Any]) -> Optional[EmotionalSequence]:
        """
        Extract emotional sequence from data source.

        Args:
            data: Input data from dream/memory/drift source

        Returns:
            EmotionalSequence or None if extraction failed
        """
        try:
            # Determine data source type
            source_type = self._identify_source_type(data)

            if source_type == "dream":
                return self._extract_from_dream(data)
            elif source_type == "memory":
                return self._extract_from_memory(data)
            elif source_type == "drift_log":
                return self._extract_from_drift_log(data)
            elif source_type == "generic":
                return self._extract_from_generic(data)
            else:
                logger.warning(f"Unknown data source type in: {data}")
                return None

        except Exception as e:
            logger.error(f"Failed to extract emotional sequence: {e}")
            return None

    def _identify_source_type(self, data: dict[str, Any]) -> str:
        """Identify the type of data source."""
        if "dream_content" in data or "dream_type" in data:
            return "dream"
        elif (
            "memory_entry" in data
            or "emotional_memory" in data
            or "current_emotion_vector" in data
            or ("emotions" in data and any(key in data for key in ["memory_type", "confidence", "memory_id"]))
        ):
            return "memory"
        elif "drift_score" in data or "ethical_drift" in data:
            return "drift_log"
        elif "emotions" in data and "timestamp" in data:
            return "generic"
        else:
            return "unknown"

    def _extract_from_dream(self, data: dict[str, Any]) -> Optional[EmotionalSequence]:
        """Extract emotional sequence from dream data."""
        dream_content = data.get("dream_content", "")
        emotions = self._extract_emotions_from_text(dream_content)
        symbols = self._extract_symbols_from_text(dream_content)

        if len(emotions) < self.min_sequence_length:
            return None

        return EmotionalSequence(
            sequence_id=f"DREAM_{int(time.time())}_{hash(dream_content) % 10000}",
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source="dream",
            emotions=emotions,
            symbols=symbols,
            intensity=data.get("emotional_intensity", 0.5),
            duration_minutes=data.get("duration_minutes"),
            context={
                "dream_type": data.get("dream_type"),
                "lucidity_level": data.get("lucidity_level"),
                "narrative_coherence": data.get("narrative_coherence"),
            },
        )

    def _extract_from_memory(self, data: dict[str, Any]) -> Optional[EmotionalSequence]:
        """Extract emotional sequence from memory data."""
        emotions = []

        # Extract from emotional memory structure
        if "current_emotion_vector" in data:
            emotions = self._extract_emotions_from_vector(data["current_emotion_vector"])
        elif "emotional_memory" in data:
            emotions = self._extract_emotions_from_memory_log(data["emotional_memory"])
        elif "emotions" in data:
            emotions = data["emotions"] if isinstance(data["emotions"], list) else [data["emotions"]]

        symbols = data.get("symbols", [])

        if len(emotions) < self.min_sequence_length:
            return None

        return EmotionalSequence(
            sequence_id=f"MEMORY_{int(time.time())}_{hash(str(data)) % 10000}",
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source="memory",
            emotions=emotions,
            symbols=symbols,
            intensity=data.get("intensity", 0.5),
            context={
                "memory_type": data.get("memory_type"),
                "confidence": data.get("confidence"),
                "associative_links": data.get("associative_links", []),
            },
        )

    def _extract_from_drift_log(self, data: dict[str, Any]) -> Optional[EmotionalSequence]:
        """Extract emotional sequence from ethical drift log."""
        emotions = []

        # Extract emotions from drift context
        if "emotional_state" in data:
            emotions = [data["emotional_state"]]
        elif "context" in data and "emotions" in data["context"]:
            emotions = data["context"]["emotions"]

        # Infer emotions from drift severity
        drift_score = data.get("drift_score", 0.0)
        if drift_score > 0.7:
            emotions.extend(["anxiety", "concern"])
        elif drift_score > 0.5:
            emotions.extend(["unease", "tension"])

        symbols = data.get("symbols", [])

        if len(emotions) < 2:  # Lower threshold for drift logs
            return None

        return EmotionalSequence(
            sequence_id=f"DRIFT_{int(time.time())}_{hash(str(data)) % 10000}",
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source="drift_log",
            emotions=emotions,
            symbols=symbols,
            intensity=min(drift_score, 1.0),
            context={
                "drift_score": drift_score,
                "violation_type": data.get("violation_type"),
                "escalation_level": data.get("escalation_level"),
            },
        )

    def _extract_from_generic(self, data: dict[str, Any]) -> Optional[EmotionalSequence]:
        """Extract emotional sequence from generic emotional data."""
        emotions = data.get("emotions", [])
        symbols = data.get("symbols", [])

        if len(emotions) < self.min_sequence_length:
            return None

        return EmotionalSequence(
            sequence_id=f"GENERIC_{int(time.time())}_{hash(str(data)) % 10000}",
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source="generic",
            emotions=emotions if isinstance(emotions, list) else [emotions],
            symbols=(symbols if isinstance(symbols, list) else [symbols] if symbols else []),
            intensity=data.get("intensity", 0.5),
            context={
                "data_type": data.get("data_type", "generic"),
                "confidence": data.get("confidence"),
                "source_info": data.get("source_info"),
            },
        )

    def _extract_emotions_from_text(self, text: str) -> list[str]:
        """Extract emotional terms from text using pattern matching."""

        # Comprehensive emotion lexicon
        emotion_patterns = {
            "fear": r"\b(?:fear|afraid|scared|terrified|panic|dread|horror)\b",
            "anxiety": r"\b(?:anxiety|anxious|worried|worry|nervous|tense)\b",
            "anger": r"\b(?:anger|angry|mad|furious|rage|irritated|frustrated|annoyed)\b",
            "sadness": r"\b(?:sad|sadness|depressed|melancholy|grief|sorrow|despair|gloom)\b",
            "joy": r"\b(?:joy|happy|happiness|elated|ecstatic|cheerful|delighted|blissful)\b",
            "disgust": r"\b(?:disgust|disgusted|revolted|repulsed|sick|nauseous|appalled)\b",
            "surprise": r"\b(?:surprise|surprised|shocked|amazed|astonished|startled|stunned)\b",
            "confusion": r"\b(?:confused|bewildered|perplexed|puzzled|uncertain|lost)\b",
            "loneliness": r"\b(?:lonely|alone|isolated|abandoned|forsaken|solitary)\b",
            "nostalgia": r"\b(?:nostalgic|longing|yearning|wistful|reminiscent|homesick)\b",
            "emptiness": r"\b(?:empty|void|hollow|nothingness|vacant|blank|null)\b",
            "falling": r"\b(?:falling|dropping|plummeting|descending|sinking|tumbling)\b",
            "regret": r"\b(?:regret|remorse|guilt|shame|sorry|apologetic|repentant)\b",
        }

        emotions = []
        text_lower = text.lower()

        for emotion, pattern in emotion_patterns.items():
            if re.search(pattern, text_lower):
                emotions.append(emotion)

        return emotions

    def _extract_symbols_from_text(self, text: str) -> list[str]:
        """Extract symbolic terms from text."""

        # Symbolic pattern recognition
        symbol_patterns = {
            "water": r"\b(?:water|ocean|river|lake|sea|rain|flood|drowning)\b",
            "fire": r"\b(?:fire|flame|burning|heat|inferno|blaze|ember)\b",
            "darkness": r"\b(?:dark|darkness|shadow|night|black|obscure)\b",
            "light": r"\b(?:light|bright|illumination|glow|radiance|shine)\b",
            "death": r"\b(?:death|dying|dead|corpse|grave|funeral|cemetery)\b",
            "birth": r"\b(?:birth|baby|newborn|creation|genesis|beginning)\b",
            "mirror": r"\b(?:mirror|reflection|image|double|twin|doppelganger)\b",
            "door": r"\b(?:door|portal|gateway|entrance|exit|threshold)\b",
            "maze": r"\b(?:maze|labyrinth|lost|wandering|trapped|circle)\b",
            "void": r"\b(?:void|abyss|chasm|pit|hole|emptiness|nothingness)\b",
        }

        symbols = []
        text_lower = text.lower()

        for symbol, pattern in symbol_patterns.items():
            if re.search(pattern, text_lower):
                symbols.append(symbol)

        return symbols

    def _extract_emotions_from_vector(self, emotion_vector: dict[str, Any]) -> list[str]:
        """Extract emotions from emotion vector structure."""
        emotions = []

        if "primary_emotion" in emotion_vector:
            emotions.append(emotion_vector["primary_emotion"])

        if "dimensions" in emotion_vector:
            # Extract top emotions from dimensional representation
            dimensions = emotion_vector["dimensions"]
            sorted_emotions = sorted(dimensions.items(), key=lambda x: x[1], reverse=True)

            for emotion, value in sorted_emotions[:5]:  # Top 5 emotions
                if value > 0.3:  # Threshold for inclusion
                    emotions.append(emotion)

        return emotions

    def _extract_emotions_from_memory_log(self, memory_log: list[dict[str, Any]]) -> list[str]:
        """Extract emotions from memory log entries."""
        emotions = []

        for entry in memory_log[-5:]:  # Recent entries
            if "emotion" in entry:
                emotions.append(entry["emotion"])
            elif "emotional_state" in entry:
                emotions.append(entry["emotional_state"])

        return emotions

    def detect_recurring_motifs(self, emotions: list[str], symbols: list[str]) -> list[RecurringMotif]:
        """
        Detect recurring motifs in emotional and symbolic patterns.

        Args:
            emotions: List of emotional terms
            symbols: List of symbolic terms

        Returns:
            List of detected recurring motifs
        """
        if len(emotions) < self.min_sequence_length:
            return []

        # Generate n-grams from emotional sequence
        motifs = []

        for n in range(self.min_sequence_length, min(len(emotions) + 1, 8)):
            n_grams = self._generate_ngrams(emotions, n)

            for gram in n_grams:
                pattern_str = " -> ".join(gram)
                motif_id = f"MOTIF_{hash(pattern_str) % 100000}"

                # Check if this motif already exists
                existing_motif = self.detected_motifs.get(motif_id)

                if existing_motif:
                    # Update existing motif
                    existing_motif.last_seen = datetime.now(timezone.utc).isoformat()
                    existing_motif.frequency += 1
                    motifs.append(existing_motif)
                else:
                    # Create new motif
                    new_motif = RecurringMotif(
                        motif_id=motif_id,
                        pattern=list(gram),
                        occurrences=[],
                        first_seen=datetime.now(timezone.utc).isoformat(),
                        last_seen=datetime.now(timezone.utc).isoformat(),
                        frequency=1,
                        intensity_trend="stable",
                    )

                    # Check for archetype match
                    archetype, score = self.archetype_detector.detect_archetype(list(gram))
                    if archetype:
                        new_motif.archetype_match = archetype
                        new_motif.archetype_score = score

                    self.detected_motifs[motif_id] = new_motif
                    motifs.append(new_motif)

        # Filter motifs by recurrence threshold
        recurring_motifs = [m for m in motifs if m.frequency >= self.recurrence_threshold]

        logger.info(
            f"Detected {len(recurring_motifs)} recurring motifs",
            total_motifs=len(motifs),
            ΛTAG="ΛMOTIF_DETECTED",
        )

        return recurring_motifs

    def _generate_ngrams(self, sequence: list[str], n: int) -> list[tuple[str, ...]]:
        """Generate n-grams from sequence."""
        return list(zip(*[sequence[i:] for i in range(n)]))

    def compute_loop_score(self, recurrences: list[RecurringMotif]) -> tuple[float, float]:
        """
        Compute Emotional Loop Index (ELI) and Recurrence Intensity Score (RIS).

        Args:
            recurrences: List of recurring motifs

        Returns:
            Tuple of (ELI, RIS) scores
        """
        if not recurrences:
            return 0.0, 0.0

        # Emotional Loop Index (ELI) - measures loop strength and persistence
        eli_components = []

        for motif in recurrences:
            # Normalize by max expected frequency
            frequency_score = min(motif.frequency / 10.0, 1.0)
            # Longer patterns are more significant
            pattern_length_score = len(motif.pattern) / 8.0
            archetype_score = motif.archetype_score if motif.archetype_match else 0.0

            # Time persistence factor
            time_span = self._calculate_time_span(motif.first_seen, motif.last_seen)
            persistence_score = min(time_span / (24 * 60), 1.0)  # Normalize by 24 hours

            motif_eli = (
                frequency_score * 0.4 + pattern_length_score * 0.2 + archetype_score * 0.3 + persistence_score * 0.1
            )

            eli_components.append(motif_eli)

        eli = np.mean(eli_components) if eli_components else 0.0

        # Recurrence Intensity Score (RIS) - measures escalation and frequency
        ris_components = []

        for motif in recurrences:
            frequency_intensity = min(motif.frequency / 5.0, 1.0)  # More aggressive normalization

            # Archetype risk multiplier
            archetype_multiplier = 1.0
            if motif.archetype_match:
                archetype_info = self.archetype_detector.ARCHETYPE_PATTERNS.get(motif.archetype_match, {})
                archetype_multiplier = archetype_info.get("risk_level", 1.0)

            # Pattern complexity factor
            complexity_score = len(set(motif.pattern)) / len(motif.pattern) if motif.pattern else 0.0

            motif_ris = frequency_intensity * archetype_multiplier * (1 + complexity_score)
            ris_components.append(min(motif_ris, 1.0))

        ris = np.mean(ris_components) if ris_components else 0.0

        # Apply maximum thresholds
        eli = min(eli, 1.0)
        ris = min(ris, 1.0)

        logger.debug("Computed loop scores", eli=eli, ris=ris, motif_count=len(recurrences))

        return eli, ris

    def _calculate_time_span(self, first_seen: str, last_seen: str) -> float:
        """Calculate time span between first and last occurrence in minutes."""
        try:
            first_dt = datetime.fromisoformat(first_seen.replace("Z", "+00:00"))
            last_dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
            return (last_dt - first_dt).total_seconds() / 60.0
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Failed to calculate time span: {e}")
            return 0.0

    def generate_loop_report(
        self, format: str = "json", window_minutes: Optional[int] = None
    ) -> Union[dict[str, Any], str]:
        """
        Generate comprehensive loop detection report.

        Args:
            format: Output format ('json' or 'markdown')
            window_minutes: Analysis window in minutes (default: use instance window)

        Returns:
            Report in requested format
        """
        if window_minutes is None:
            window_minutes = self.window_hours * 60

        # Filter sequences by time window
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        recent_sequences = [
            seq for seq in self.emotional_sequences if self._parse_timestamp(seq.timestamp) >= cutoff_time
        ]

        # Detect motifs from recent sequences
        all_emotions = []
        all_symbols = []

        for seq in recent_sequences:
            all_emotions.extend(seq.emotions)
            all_symbols.extend(seq.symbols)

        motifs = self.detect_recurring_motifs(all_emotions, all_symbols)

        # Compute scores
        eli, ris = self.compute_loop_score(motifs)

        # Determine severity
        severity = self._determine_severity(eli, ris, motifs)

        # Generate archetype alerts
        archetype_alerts = self._generate_archetype_alerts(motifs)

        # Generate recommendations
        recommendations = self._generate_recommendations(eli, ris, motifs, severity)

        # Create report
        report = LoopReport(
            report_id=f"ECHO_REPORT_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            analysis_window=f"{window_minutes} minutes",
            sequences_analyzed=len(recent_sequences),
            motifs_detected=len(motifs),
            high_risk_motifs=len([m for m in motifs if m.archetype_match]),
            eli_score=eli,
            ris_score=ris,
            severity=severity,
            motifs=motifs,
            archetype_alerts=archetype_alerts,
            recommendations=recommendations,
        )

        # Update statistics
        self.stats["avg_eli_score"] = (self.stats["avg_eli_score"] + eli) / 2
        self.stats["avg_ris_score"] = (self.stats["avg_ris_score"] + ris) / 2
        self.stats["motifs_detected"] = len(motifs)
        self.stats["archetype_alerts"] = len(archetype_alerts)

        # Store in history
        self.analysis_history.append(report)

        if format == "json":
            return self._format_report_json(report)
        elif format == "markdown":
            return self._format_report_markdown(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse timestamp string to datetime object."""
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Failed to parse timestamp: {e}")
            return datetime.now(timezone.utc)

    def _determine_severity(self, eli: float, ris: float, motifs: list[RecurringMotif]) -> EchoSeverity:
        """Determine severity level based on scores and motifs."""

        # High-risk archetype count
        high_risk_count = sum(
            1
            for m in motifs
            if m.archetype_match
            and self.archetype_detector.ARCHETYPE_PATTERNS.get(m.archetype_match, {}).get("risk_level", 0) > 0.8
        )

        # Critical archetype presence
        critical_archetypes = {
            ArchetypePattern.VOID_DESCENT,
            ArchetypePattern.TRAUMA_ECHO,
        }
        has_critical = any(m.archetype_match in critical_archetypes for m in motifs)

        # Severity determination
        if has_critical or (eli > 0.9 and ris > 0.9):
            return EchoSeverity.EMERGENCY
        elif eli > 0.8 or ris > 0.8 or high_risk_count >= 3:
            return EchoSeverity.CRITICAL
        elif eli > 0.6 or ris > 0.6 or high_risk_count >= 2:
            return EchoSeverity.WARNING
        elif eli > 0.4 or ris > 0.4 or high_risk_count >= 1:
            return EchoSeverity.CAUTION
        else:
            return EchoSeverity.NORMAL

    def _generate_archetype_alerts(self, motifs: list[RecurringMotif]) -> list[dict[str, Any]]:
        """Generate archetype-specific alerts."""
        alerts = []

        for motif in motifs:
            if not motif.archetype_match:
                continue

            archetype_info = self.archetype_detector.ARCHETYPE_PATTERNS.get(motif.archetype_match, {})

            alert = {
                "alert_id": f"ARCH_ALERT_{int(time.time())}_{hash(motif.motif_id) % 1000}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "archetype": motif.archetype_match.value,
                "description": archetype_info.get("description", "Unknown archetype"),
                "pattern": " → ".join(motif.pattern),
                "frequency": motif.frequency,
                "risk_level": archetype_info.get("risk_level", 0.0),
                "cascade_potential": archetype_info.get("cascade_potential", 0.0),
                "match_score": motif.archetype_score,
                "first_seen": motif.first_seen,
                "last_seen": motif.last_seen,
                "ΛTAG": [
                    "ΛECHO_LOOP",
                    "ΛARCHETYPE_WARNING",
                    ("ΛRESONANCE_HIGH" if archetype_info.get("risk_level", 0) > 0.8 else "ΛRESONANCE_MEDIUM"),
                ],
            }

            alerts.append(alert)

        return alerts

    def _generate_recommendations(
        self,
        eli: float,
        ris: float,
        motifs: list[RecurringMotif],
        severity: EchoSeverity,
    ) -> list[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        if severity == EchoSeverity.EMERGENCY:
            recommendations.extend(
                [
                    "IMMEDIATE ACTION REQUIRED: Critical emotional loop detected",
                    "Engage governor escalation protocols for emergency intervention",
                    "Implement memory quarantine for affected symbol systems",
                    "Activate autonomous stabilization with ΛRESET protocols",
                ]
            )

        elif severity == EchoSeverity.CRITICAL:
            recommendations.extend(
                [
                    "High-priority intervention required within 1 hour",
                    "Apply targeted symbolic stabilizers (ΛCALM, ΛANCHOR, ΛRESOLVE)",
                    "Monitor escalation patterns and prepare quarantine protocols",
                    "Increase dream feedback monitoring frequency",
                ]
            )

        elif severity == EchoSeverity.WARNING:
            recommendations.extend(
                [
                    "Moderate risk detected - implement preventive measures",
                    "Apply emotional stabilization techniques",
                    "Review recent memory formation patterns",
                    "Increase monitoring window for early detection",
                ]
            )

        elif severity == EchoSeverity.CAUTION:
            recommendations.extend(
                [
                    "Low-level emotional looping detected",
                    "Continue monitoring with standard protocols",
                    "Consider light stabilization if patterns persist",
                    "Review emotional processing efficiency",
                ]
            )

        # Archetype-specific recommendations
        archetype_recommendations = {
            ArchetypePattern.SPIRAL_DOWN: "Apply upward momentum stabilizers and void-seeking interruption",
            ArchetypePattern.NOSTALGIC_TRAP: "Implement temporal reframing and forward-momentum generation",
            ArchetypePattern.ANGER_CASCADE: "Deploy emotional dampening and conflict resolution protocols",
            ArchetypePattern.IDENTITY_CRISIS: "Engage identity anchoring and coherence reinforcement",
            ArchetypePattern.TRAUMA_ECHO: "Activate trauma processing protocols and memory desensitization",
            ArchetypePattern.VOID_DESCENT: "CRITICAL: Existential anchor deployment and reality grounding required",
        }

        for motif in motifs:
            if motif.archetype_match and motif.archetype_match in archetype_recommendations:
                recommendations.append(archetype_recommendations[motif.archetype_match])

        return recommendations

    def _format_report_json(self, report: LoopReport) -> dict[str, Any]:
        """Format report as JSON."""
        return {
            "report_meta": {
                "report_id": report.report_id,
                "timestamp": report.timestamp,
                "analysis_window": report.analysis_window,
                "generator": "ΛECHO v1.0.0",
            },
            "analysis_summary": {
                "sequences_analyzed": report.sequences_analyzed,
                "motifs_detected": report.motifs_detected,
                "high_risk_motifs": report.high_risk_motifs,
                "eli_score": round(report.eli_score, 4),
                "ris_score": round(report.ris_score, 4),
                "severity": report.severity.value,
            },
            "detected_motifs": [
                {
                    "motif_id": motif.motif_id,
                    "pattern": motif.pattern,
                    "frequency": motif.frequency,
                    "archetype_match": (motif.archetype_match.value if motif.archetype_match else None),
                    "archetype_score": round(motif.archetype_score, 3),
                    "first_seen": motif.first_seen,
                    "last_seen": motif.last_seen,
                    "intensity_trend": motif.intensity_trend,
                }
                for motif in report.motifs
            ],
            "archetype_alerts": report.archetype_alerts,
            "recommendations": report.recommendations,
            "system_statistics": self.stats,
            "ΛTAG": ["ΛECHO_REPORT", f"ΛSEVERITY_{report.severity.value}"],
        }

    def _format_report_markdown(self, report: LoopReport) -> str:
        """Format report as Markdown."""

        severity_emoji = {
            EchoSeverity.NORMAL: "✅",
            EchoSeverity.CAUTION: "⚠️",
            EchoSeverity.WARNING: "⚠️",
            EchoSeverity.CRITICAL: "🚨",
            EchoSeverity.EMERGENCY: "🆘",
        }

        md = f"""# 🔄 ΛECHO Emotional Loop Detection Report

**Report ID:** `{report.report_id}`
**Generated:** {report.timestamp}
**Analysis Window:** {report.analysis_window}
**Severity:** {severity_emoji.get(report.severity, "❓")} {report.severity.value}

## 📊 Analysis Summary

| Metric | Value |
|--------|-------|
| Sequences Analyzed | {report.sequences_analyzed} |
| Motifs Detected | {report.motifs_detected} |
| High-Risk Motifs | {report.high_risk_motifs} |
| **ELI Score** | **{report.eli_score:.4f}** |
| **RIS Score** | **{report.ris_score:.4f}** |

### Score Interpretation
- **ELI (Emotional Loop Index):** Measures loop strength and persistence (0.0-1.0)
- **RIS (Recurrence Intensity Score):** Measures escalation and frequency (0.0-1.0)

## 🔍 Detected Motifs

"""

        if report.motifs:
            for i, motif in enumerate(report.motifs, 1):
                archetype_str = f" ({motif.archetype_match.value})" if motif.archetype_match else ""
                md += f"""### {i}. Pattern: {" → ".join(motif.pattern)}{archetype_str}

- **Frequency:** {motif.frequency} occurrences
- **Archetype Score:** {motif.archetype_score:.3f}
- **Time Span:** {motif.first_seen} to {motif.last_seen}
- **Trend:** {motif.intensity_trend}

"""
        else:
            md += "*No recurring motifs detected in analysis window.*\n\n"

        # Archetype Alerts
        if report.archetype_alerts:
            md += "## 🚨 Archetype Alerts\n\n"

            for alert in report.archetype_alerts:
                risk_emoji = "🔴" if alert["risk_level"] > 0.8 else "🟡" if alert["risk_level"] > 0.5 else "🟢"
                md += f"""### {risk_emoji} {alert["archetype"].replace("_", " ").title()}

**Pattern:** `{alert["pattern"]}`
**Description:** {alert["description"]}
**Risk Level:** {alert["risk_level"]:.2f} | **Cascade Potential:** {alert["cascade_potential"]:.2f}
**Frequency:** {alert["frequency"]} | **Match Score:** {alert["match_score"]:.3f}

"""

        # Recommendations
        if report.recommendations:
            md += "## 💡 Recommendations\n\n"

            for i, rec in enumerate(report.recommendations, 1):
                md += f"{i}. {rec}\n"

        md += f"""
## 📈 System Statistics

- **Total Sequences Processed:** {self.stats["sequences_processed"]}
- **Average ELI:** {self.stats["avg_eli_score"]:.4f}
- **Average RIS:** {self.stats["avg_ris_score"]:.4f}
- **Escalations Sent:** {self.stats["escalations_sent"]}

---
*Generated by ΛECHO v1.0.0 - LUKHAS AGI Emotional Loop Detection System*
"""

        return md

    def emit_symbolic_echo_alert(self, score: float, archetype: Optional[ArchetypePattern]) -> dict[str, Any]:
        """
        Emit symbolic alert for detected emotional echo.

        Args:
            score: Combined ELI/RIS score
            archetype: Detected archetype pattern

        Returns:
            Alert metadata dictionary
        """

        # Determine alert level based on score
        if score > 0.9:
            alert_level = "ΛEMERGENCY"
        elif score > 0.7:
            alert_level = "ΛCRITICAL"
        elif score > 0.5:
            alert_level = "ΛWARNING"
        else:
            alert_level = "ΛCAUTION"

        # Generate symbolic tags
        tags = ["ΛECHO", "ΛECHO_LOOP"]

        if archetype:
            tags.append("ΛARCHETYPE_WARNING")

            # High-risk archetypes get resonance high tag
            archetype_info = self.archetype_detector.ARCHETYPE_PATTERNS.get(archetype, {})
            if archetype_info.get("risk_level", 0) > 0.8:
                tags.append("ΛRESONANCE_HIGH")
            else:
                tags.append("ΛRESONANCE_MEDIUM")

        tags.append(alert_level)

        alert = {
            "alert_id": f"ECHO_ALERT_{int(time.time())}_{hash(str(archetype)) % 10000}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alert_level": alert_level,
            "score": score,
            "archetype": archetype.value if archetype else None,
            "description": self._generate_alert_description(score, archetype),
            "ΛTAG": tags,
            "recommended_actions": self._get_alert_actions(alert_level, archetype),
        }

        logger.warning(
            "Symbolic echo alert emitted",
            alert_id=alert["alert_id"],
            level=alert_level,
            score=score,
            archetype=archetype.value if archetype else None,
            ΛTAG=tags,
        )

        return alert

    def _generate_alert_description(self, score: float, archetype: Optional[ArchetypePattern]) -> str:
        """Generate human-readable alert description."""

        severity_desc = {
            0.0: "minimal",
            0.3: "low-level",
            0.5: "moderate",
            0.7: "significant",
            0.9: "critical",
        }

        # Find closest severity
        severity = "unknown"
        for threshold, desc in sorted(severity_desc.items()):
            if score >= threshold:
                severity = desc

        base_desc = f"Detected {severity} emotional loop with composite score {score:.3f}"

        if archetype:
            archetype_info = self.archetype_detector.ARCHETYPE_PATTERNS.get(archetype, {})
            archetype_desc = archetype_info.get("description", archetype.value.replace("_", " "))
            base_desc += f" matching {archetype_desc} archetype pattern"

        return base_desc

    def _get_alert_actions(self, alert_level: str, archetype: Optional[ArchetypePattern]) -> list[str]:
        """Get recommended actions for alert level and archetype."""

        base_actions = {
            "ΛCAUTION": ["Monitor pattern evolution", "Document occurrence"],
            "ΛWARNING": [
                "Apply preventive stabilization",
                "Increase monitoring frequency",
            ],
            "ΛCRITICAL": ["Activate emergency protocols", "Consider memory quarantine"],
            "ΛEMERGENCY": [
                "Immediate governor escalation",
                "Emergency stabilization required",
            ],
        }

        actions = base_actions.get(alert_level, ["Review system state"])

        # Add archetype-specific actions
        if archetype == ArchetypePattern.VOID_DESCENT:
            actions.append("Deploy existential anchoring protocols")
        elif archetype == ArchetypePattern.TRAUMA_ECHO:
            actions.append("Activate trauma processing interruption")
        elif archetype == ArchetypePattern.ANGER_CASCADE:
            actions.append("Apply emotional dampening stabilizers")

        return actions

    # Integration methods
    def integrate_with_tuner(self, tuner: AdaptiveEntanglementStabilizer):
        """Integrate with tuner for automated stabilization."""
        self.tuner = tuner
        logger.info("Integrated with AdaptiveEntanglementStabilizer")

    def integrate_with_governor(self, governor: LambdaGovernor):
        """Integrate with governor for escalation."""
        self.governor = governor
        logger.info("Integrated with LambdaGovernor")

    async def escalate_to_governor(self, eli: float, ris: float, motifs: list[RecurringMotif]):
        """Escalate high-risk emotional loops to governor."""
        if not self.governor:
            logger.warning("Governor not integrated - cannot escalate")
            return

        # Determine if escalation is warranted
        severity = self._determine_severity(eli, ris, motifs)

        if severity.value not in ["CRITICAL", "EMERGENCY"]:
            return

        # Prepare escalation signal
        symbol_ids = []
        memory_ids = []

        for motif in motifs:
            if motif.archetype_match:
                symbol_ids.append(f"MOTIF_{motif.motif_id}")
                memory_ids.extend([f"PATTERN_{i}" for i in range(len(motif.pattern))])

        escalation_signal = create_escalation_signal(
            source_module=EscalationSource.EMOTION_PROTOCOL,
            priority=(
                EscalationPriority.CRITICAL if severity == EchoSeverity.CRITICAL else EscalationPriority.EMERGENCY
            ),
            triggering_metric="emotional_loop_detection",
            drift_score=0.0,  # Not drift-related
            entropy=min(eli + ris, 1.0),
            emotion_volatility=ris,
            contradiction_density=eli,
            symbol_ids=symbol_ids[:10],  # Limit for performance
            memory_ids=memory_ids[:10],
            context={
                "eli_score": eli,
                "ris_score": ris,
                "detected_archetypes": [m.archetype_match.value for m in motifs if m.archetype_match],
                "motif_count": len(motifs),
                "analysis_source": "ΛECHO",
            },
        )

        try:
            response = await self.governor.receive_escalation(escalation_signal)
            self.stats["escalations_sent"] += 1

            logger.critical(
                "Escalated emotional loop to governor",
                signal_id=escalation_signal.signal_id,
                response_decision=response.decision.value,
                eli=eli,
                ris=ris,
                ΛTAG="ΛECHO_ESCALATED",
            )

        except Exception as e:
            logger.error(f"Failed to escalate to governor: {e}")


def main():
    """Main CLI interface for ΛECHO emotional echo detector."""

    parser = argparse.ArgumentParser(
        description="ΛECHO - Emotional-Symbolic Loop Detection for LUKHAS AGI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 emotional_echo_detector.py --analyze --window 24
  python3 emotional_echo_detector.py --report --format markdown
  python3 emotional_echo_detector.py --watch --interval 300
  python3 emotional_echo_detector.py --alert --threshold 0.7
        """,
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze recent emotional sequences for loops",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive loop detection report",
    )
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument(
        "--alert",
        action="store_true",
        help="Alert mode - emit warnings for detected loops",
    )

    parser.add_argument("--window", type=int, default=24, help="Analysis window in hours (default: 24)")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Report format (default: json)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Watch mode interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Alert threshold for ELI/RIS scores (default: 0.5)",
    )
    parser.add_argument("--data-source", type=str, help="Path to data source file (JSONL format)")
    parser.add_argument("--output", type=str, help="Output file path for reports")

    args = parser.parse_args()

    # Initialize detector
    detector = EmotionalEchoDetector(window_hours=args.window, similarity_threshold=0.7)

    logger.info("🔄 ΛECHO - Emotional-Symbolic Loop Detector")
    logger.info(f"📊 Analysis window: {args.window} hours")
    logger.info(f"🎯 Alert threshold: {args.threshold}")

    try:
        if args.analyze or args.report:
            # Load sample data if provided
            if args.data_source and Path(args.data_source).exists():
                logger.info(f"📂 Loading data from {args.data_source}")
                sample_data = _load_sample_data(args.data_source)

                for data_point in sample_data:
                    sequence = detector.extract_emotional_sequence(data_point)
                    if sequence:
                        detector.emotional_sequences.append(sequence)

                detector.stats["sequences_processed"] = len(detector.emotional_sequences)
            else:
                logger.info("📝 Generating synthetic test data...")
                sample_data = _generate_synthetic_emotional_data()

                for data_point in sample_data:
                    sequence = detector.extract_emotional_sequence(data_point)
                    if sequence:
                        detector.emotional_sequences.append(sequence)

                detector.stats["sequences_processed"] = len(detector.emotional_sequences)

            # Generate report
            logger.info("🔍 Analyzing emotional sequences...")
            report = detector.generate_loop_report(format=args.format, window_minutes=args.window * 60)

            if args.output:
                # Write to file
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if args.format == "json":
                    with open(output_path, "w") as f:
                        json.dump(report, f, indent=2)
                else:
                    with open(output_path, "w") as f:
                        f.write(report)

                logger.info(f"📄 Report saved to {output_path}")
            else:
                # Print to console
                if args.format == "json":
                    logger.info(json.dumps(report, indent=2))
                else:
                    logger.info(report)

        elif args.watch:
            logger.info("👁️ Starting continuous monitoring...")
            asyncio.run(_continuous_watch(detector, args.interval, args.threshold))

        elif args.alert:
            logger.info("🚨 Alert mode - checking for immediate threats...")
            # Load recent data and check for alerts
            sample_data = _generate_synthetic_emotional_data(high_risk=True)

            for data_point in sample_data:
                sequence = detector.extract_emotional_sequence(data_point)
                if sequence:
                    detector.emotional_sequences.append(sequence)

            # Check for high-risk patterns
            all_emotions = []
            for seq in detector.emotional_sequences:
                all_emotions.extend(seq.emotions)

            motifs = detector.detect_recurring_motifs(all_emotions, [])
            eli, ris = detector.compute_loop_score(motifs)

            combined_score = (eli + ris) / 2

            if combined_score >= args.threshold:
                logger.warning("🚨 ALERT: High-risk emotional loop detected!")
                logger.warning(f"   ELI: {eli:.4f} | RIS: {ris:.4f} | Combined: {combined_score:.4f}")

                # Find highest risk archetype
                high_risk_motif = max(motifs, key=lambda m: m.archetype_score) if motifs else None
                archetype = high_risk_motif.archetype_match if high_risk_motif else None

                alert = detector.emit_symbolic_echo_alert(combined_score, archetype)
                logger.warning(f"   Alert ID: {alert['alert_id']}")
                logger.warning(f"   Level: {alert['alert_level']}")
                logger.warning(f"   Description: {alert['description']}")
            else:
                logger.info("✅ No immediate threats detected")
                logger.info(f"   ELI: {eli:.4f} | RIS: {ris:.4f} | Combined: {combined_score:.4f}")

        else:
            parser.print_help()
            return 1

        return 0

    except KeyboardInterrupt:
        print("\n👋 ΛECHO detector stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"ΛECHO detector failed: {e}")
        return 1


async def _continuous_watch(detector: EmotionalEchoDetector, interval: int, threshold: float):
    """Continuous monitoring loop."""

    while True:
        try:
            # Generate fresh synthetic data (in real system, would read from logs)
            sample_data = _generate_synthetic_emotional_data()

            # Clear old sequences to simulate real-time data
            detector.emotional_sequences.clear()

            for data_point in sample_data:
                sequence = detector.extract_emotional_sequence(data_point)
                if sequence:
                    detector.emotional_sequences.append(sequence)

            # Analyze
            all_emotions = []
            for seq in detector.emotional_sequences:
                all_emotions.extend(seq.emotions)

            motifs = detector.detect_recurring_motifs(all_emotions, [])
            eli, ris = detector.compute_loop_score(motifs)

            combined_score = (eli + ris) / 2

            current_time = datetime.now(timezone.utc).strftime("%H:%M:%S")

            if combined_score >= threshold:
                print(f"⚠️ {current_time} - HIGH RISK: ELI={eli:.3f}, RIS={ris:.3f}, Score={combined_score:.3f}")
            elif combined_score >= threshold * 0.7:
                print(f"🟡 {current_time} - MODERATE: ELI={eli:.3f}, RIS={ris:.3f}, Score={combined_score:.3f}")
            else:
                print(f"✅ {current_time} - NORMAL: ELI={eli:.3f}, RIS={ris:.3f}, Score={combined_score:.3f}")

            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Watch error: {e}")
            await asyncio.sleep(interval)


def _load_sample_data(file_path: str) -> list[dict[str, Any]]:
    """Load sample data from jsonl_file."""
    data = []

    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(json.loads(line))
    except Exception as e:
        print(f"Warning: Could not load data from {file_path}: {e}")

    return data


def _generate_synthetic_emotional_data(count: int = 50, high_risk: bool = False) -> list[dict[str, Any]]:
    """Generate synthetic emotional data for testing."""

    synthetic_data = []

    # Normal emotional patterns
    normal_patterns = [
        ["curiosity", "discovery", "satisfaction"],
        ["anticipation", "excitement", "fulfillment"],
        ["concern", "analysis", "resolution"],
        ["reflection", "understanding", "acceptance"],
        ["challenge", "effort", "accomplishment"],
    ]

    # High-risk patterns for testing
    risk_patterns = [
        ["fear", "anxiety", "falling", "void", "despair"],  # Spiral down
        ["nostalgia", "longing", "regret", "loss", "melancholy"],  # Nostalgic trap
        ["irritation", "frustration", "anger", "rage", "destruction"],  # Anger cascade
        ["confusion", "doubt", "dissociation", "emptiness", "void"],  # Identity crisis
        ["pain", "memory", "trigger", "reaction", "pain"],  # Trauma echo
    ]

    patterns = risk_patterns if high_risk else normal_patterns + risk_patterns[:2]

    base_time = datetime.now(timezone.utc)

    for i in range(count):
        # Select pattern
        pattern = patterns[i % len(patterns)]

        # Add some variation
        if i % 3 == 0 and len(pattern) > 2:
            pattern = pattern[:-1] + ["uncertainty"]

        # Create synthetic data entry
        timestamp = (base_time - timedelta(minutes=i * 5)).isoformat()

        if i % 4 == 0:  # Dream data
            data_entry = {
                "dream_content": f"I experienced {', then '.join(pattern)} in my dream",
                "timestamp": timestamp,
                "emotional_intensity": min(0.3 + (i % 5) * 0.15, 1.0),
                "dream_type": "symbolic",
                "duration_minutes": 20 + (i % 10) * 5,
            }
        elif i % 4 == 1:  # Memory data
            data_entry = {
                "emotions": pattern,
                "timestamp": timestamp,
                "intensity": 0.4 + (i % 6) * 0.1,
                "memory_type": "episodic",
                "confidence": 0.7 + (i % 4) * 0.075,
            }
        elif i % 4 == 2:  # Drift log data
            data_entry = {
                "drift_score": min(0.2 + (i % 7) * 0.1, 0.9),
                "timestamp": timestamp,
                "emotional_state": pattern[0] if pattern else "neutral",
                "context": {"emotions": pattern[:3]},
                "violation_type": "emotional_instability",
            }
        else:  # Generic data
            data_entry = {
                "emotions": pattern,
                "timestamp": timestamp,
                "symbols": (["void", "darkness", "falling"] if "void" in pattern else ["light", "growth"]),
                "intensity": 0.5 + (i % 5) * 0.1,
            }

        synthetic_data.append(data_entry)

    return synthetic_data


if __name__ == "__main__":
    exit(main())

# CLAUDE CHANGELOG
# - Implemented ΛECHO emotional-symbolic loop detection module with comprehensive archetype analysis # CLAUDE_EDIT_v0.1
# - Created ArchetypeDetector with 6 high-risk emotional patterns and fuzzy matching algorithms # CLAUDE_EDIT_v0.1
# - Built EmotionalEchoDetector with sequence extraction from dreams/memory/drift logs # CLAUDE_EDIT_v0.1
# - Implemented ELI (Emotional Loop Index) and RIS (Recurrence Intensity Score) computation # CLAUDE_EDIT_v0.1
# - Created comprehensive report generation with JSON and Markdown formats # CLAUDE_EDIT_v0.1
# - Added symbolic alert system with ΛECHO_LOOP, ΛARCHETYPE_WARNING, ΛRESONANCE_HIGH tags # CLAUDE_EDIT_v0.1
# - Implemented CLI with --analyze, --report, --watch, and --alert modes # CLAUDE_EDIT_v0.1
# - Added integration hooks for tuner.py and lambda_governor escalation # CLAUDE_EDIT_v0.1
# - Created synthetic data generation for testing and demonstration # CLAUDE_EDIT_v0.1