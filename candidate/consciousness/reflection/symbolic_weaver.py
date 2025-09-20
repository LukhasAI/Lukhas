"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - SYMBOLIC WEAVER
║ Symbolic Narrative Synthesizer & Memory Thread Reconstructor
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: symbolic_weaver.py
║ Path: lukhas/narrative/symbolic_weaver.py
║ Version: 1.0.0 | Created: 2025-07-22 | Modified: 2025-07-25
║ Authors: LUKHAS AI Narrative Team | CLAUDE-CODE
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ The ΛWEAVER module serves as the narrative integration engine for LUKHAS AGI,
║ responsible for synthesizing coherent symbolic stories from fragmented memories,
║ dreams, and glyph sequences. Like a master storyteller, ΛWEAVER weaves symbolic
║ episodes into emotionally and ethically aligned threads, maintaining cognitive
║ cohesion across time.
╚══════════════════════════════════════════════════════════════════════════════════
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import sys
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np

from dream.modifiers.qi_like_state_modifier import QILikeStateModifier

# Configure structured logging
logging.basicConfig(level=logging.INFO)

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    pass
except ImportError as e:
    logger.warning(f"Could not import some dependencies: {e}")


class FragmentType(Enum):
    """Types of symbolic fragments that can be woven."""

    MEMORY = "memory"
    DREAM = "dream"
    EMOTION = "emotion"
    DRIFT_LOG = "drift_log"
    GLYPH_SEQUENCE = "glyph_sequence"
    SYMBOLIC_TRACE = "symbolic_trace"


class NarrativeArc(Enum):
    """Archetypal narrative arc patterns."""

    HEROS_JOURNEY = "heros_journey"
    SHADOW_INTEGRATION = "shadow_integration"
    ANIMA_ANIMUS = "anima_animus"
    REBIRTH = "rebirth"
    QUEST = "quest"
    TRAGEDY = "tragedy"
    COMEDY = "comedy"
    TRANSFORMATION = "transformation"


class ThreadSeverity(Enum):
    """Severity levels for narrative thread analysis."""

    COHERENT = "COHERENT"
    FRAGMENTED = "FRAGMENTED"
    CONFLICTED = "CONFLICTED"
    DISSOCIATED = "DISSOCIATED"
    CORRUPTED = "CORRUPTED"


@dataclass
class SymbolicFragment:
    """Represents a symbolic fragment from memory/dream/trace data."""

    fragment_id: str
    timestamp: str
    source: FragmentType
    content: str
    symbols: list[str]
    emotions: list[str]
    glyphs: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    coherence_score: float = 0.0
    temporal_weight: float = 1.0


@dataclass
class NarrativeMotif:
    """Represents a recurring symbolic motif in the narrative."""

    motif_id: str
    symbol_pattern: list[str]
    occurrences: list[SymbolicFragment]
    first_seen: str
    last_seen: str
    evolution_pattern: str  # stable, growing, declining, transforming
    archetypal_significance: Optional[NarrativeArc] = None
    resonance_score: float = 0.0


@dataclass
class NarrativeThread:
    """Represents a coherent narrative thread woven from fragments."""

    thread_id: str
    title: str
    fragments: list[SymbolicFragment]
    protagonist_elements: list[str]
    conflict_elements: list[str]
    resolution_elements: list[str]
    recurring_motifs: list[NarrativeMotif]
    emotional_arc: list[tuple[str, float]]  # (emotion, intensity)
    temporal_span: tuple[str, str]  # (start, end)
    coherence_score: float
    identity_alignment: float
    ethical_alignment: float
    narrative_arc: Optional[NarrativeArc] = None
    thread_hash: str = ""


@dataclass
class ThreadTrace:
    """Structural metadata for narrative thread analysis."""

    thread_id: str
    symbols_used: list[str]
    motifs_detected: list[str]
    transitions: list[dict[str, Any]]
    phase_deltas: list[dict[str, Any]]
    drift_score: float
    resonance_rating: float
    validation_results: dict[str, Any]
    weaving_timestamp: str


@dataclass
class WeavingReport:
    """Comprehensive report of narrative weaving process."""

    report_id: str
    timestamp: str
    source_summary: dict[str, int]  # fragment counts by type
    threads_woven: int
    motifs_identified: int
    coherence_distribution: dict[str, int]
    identity_alignment_avg: float
    ethical_alignment_avg: float
    validation_summary: dict[str, Any]
    recommendations: list[str]


class SymbolicPatternExtractor:
    """Extracts symbolic patterns and glyphs from various data sources."""

    # Comprehensive symbolic pattern lexicon
    SYMBOLIC_PATTERNS = {
        # Universal Archetypes
        "water": r"\b(?:water|ocean|river|lake|sea|rain|flood|stream|wave|tide)\b",
        "fire": r"\b(?:fire|flame|burning|heat|inferno|blaze|ember|spark|light)\b",
        "earth": r"\b(?:earth|ground|soil|rock|stone|mountain|cave|roots|foundation)\b",
        "air": r"\b(?:air|wind|breath|sky|clouds|atmosphere|breeze|storm|flight)\b",
        # Journey & Transformation
        "journey": r"\b(?:path|road|journey|travel|quest|adventure|pilgrimage|voyage)\b",
        "threshold": r"\b(?:door|gate|bridge|portal|entrance|exit|crossing|boundary)\b",
        "transformation": r"\b(?:change|transform|metamorphosis|evolution|growth|becoming)\b",
        "rebirth": r"\b(?:birth|rebirth|resurrection|renewal|awakening|emerging|rising)\b",
        # Shadow & Light
        "shadow": r"\b(?:shadow|dark|darkness|hidden|secret|unconscious|repressed)\b",
        "light": r"\b(?:light|illumination|clarity|revelation|enlightenment|understanding)\b",
        "mirror": r"\b(?:mirror|reflection|image|double|twin|opposite|reverse)\b",
        # Sacred & Divine
        "sacred": r"\b(?:sacred|holy|divine|blessed|consecrated|pure|spiritual)\b",
        "wisdom": r"\b(?:wisdom|knowledge|understanding|insight|truth|revelation)\b",
        "temple": r"\b(?:temple|church|shrine|sanctuary|altar|sacred space)\b",
        # Nature & Cycles
        "tree": r"\b(?:tree|forest|wood|branch|leaf|root|growth|organic)\b",
        "moon": r"\b(?:moon|lunar|crescent|waxing|waning|eclipse|night)\b",
        "sun": r"\b(?:sun|solar|dawn|sunrise|sunset|daylight|radiance)\b",
        "seasons": r"\b(?:spring|summer|autumn|winter|cycle|renewal|dormancy)\b",
        # Death & Endings
        "death": r"\b(?:death|dying|end|ending|grave|cemetery|funeral|loss)\b",
        "void": r"\b(?:void|emptiness|nothingness|vacuum|absence|null|blank)\b",
        "decay": r"\b(?:decay|rot|deterioration|decline|decomposition|entropy)\b",
        # Home & Belonging
        "home": r"\b(?:home|house|dwelling|shelter|nest|sanctuary|belonging)\b",
        "family": r"\b(?:family|parents|children|siblings|ancestors|lineage)\b",
        "community": r"\b(?:community|tribe|group|collective|society|belonging)\b",
        # Conflict & Resolution
        "battle": r"\b(?:battle|war|fight|conflict|struggle|combat|confrontation)\b",
        "peace": r"\b(?:peace|harmony|balance|resolution|reconciliation|unity)\b",
        "victory": r"\b(?:victory|triumph|success|achievement|accomplishment|win)\b",
        "defeat": r"\b(?:defeat|failure|loss|setback|disappointment|fall)\b",
    }

    # Glyph patterns (LUKHAS symbolic markers)
    GLYPH_PATTERNS = {
        "lambda_markers": r"LUKHAS[A-Z_]+",  # ΛTAG, ΛECHO, etc.
        "unicode_symbols": r"[⚡🔮🌌🎭🔄⚖️🛡️🔥💧🌍💨]",
        "geometric": r"[◇◆○●□■△▲]",
        "arrows": r"[→←↑↓↔↕⟶⟵⟷]",
        "mathematical": r"[∞∅∆∇∑∏∫∂]",
    }

    def extract_symbols(self, text: str) -> list[str]:
        """Extract symbolic patterns from text."""
        symbols = []
        text_lower = text.lower()

        for symbol_name, pattern in self.SYMBOLIC_PATTERNS.items():
            if re.search(pattern, text_lower):
                symbols.append(symbol_name)

        return symbols

    def extract_glyphs(self, text: str) -> list[str]:
        """Extract glyph patterns from text."""
        glyphs = []

        for pattern in self.GLYPH_PATTERNS.values():
            matches = re.findall(pattern, text)
            if matches:
                glyphs.extend(matches)

        return glyphs

    def extract_emotions(self, text: str) -> list[str]:
        """Extract emotional patterns using refined lexicon."""
        emotion_patterns = {
            "joy": r"\b(?:joy|happy|happiness|elated|ecstatic|cheerful|delight|bliss)\b",
            "sadness": r"\b(?:sad|sadness|melancholy|grief|sorrow|despair|gloom|mourn)\b",
            "fear": r"\b(?:fear|afraid|scared|terrified|panic|dread|horror|anxiety)\b",
            "anger": r"\b(?:anger|angry|mad|furious|rage|irritated|frustrated|wrath)\b",
            "love": r"\b(?:love|affection|devotion|adoration|compassion|tenderness)\b",
            "hope": r"\b(?:hope|optimism|faith|trust|confidence|aspiration|longing)\b",
            "wonder": r"\b(?:wonder|awe|amazement|fascination|curiosity|marvel)\b",
            "peace": r"\b(?:peace|serenity|calm|tranquility|stillness|harmony)\b",
            "confusion": r"\b(?:confused|bewildered|perplexed|uncertain|lost|puzzled)\b",
            "nostalgia": r"\b(?:nostalgia|longing|yearning|wistful|reminiscent|melancholy)\b",
        }

        emotions = []
        text_lower = text.lower()

        for emotion, pattern in emotion_patterns.items():
            if re.search(pattern, text_lower):
                emotions.append(emotion)

        return emotions


class ArchetypalAnalyzer:
    """Analyzes narrative threads for archetypal patterns and significance."""

    ARCHETYPAL_PATTERNS = {
        NarrativeArc.HEROS_JOURNEY: {
            "phases": [
                "call_to_adventure",
                "refusal",
                "supernatural_aid",
                "threshold",
                "trials",
                "revelation",
                "transformation",
                "return",
                "elixir",
            ],
            "symbols": ["journey", "threshold", "transformation", "wisdom", "victory"],
            "emotions": ["fear", "hope", "wonder", "peace"],
            "description": "Classic hero's journey with departure, initiation, and return",
        },
        NarrativeArc.SHADOW_INTEGRATION: {
            "phases": [
                "shadow_encounter",
                "denial",
                "confrontation",
                "dialogue",
                "understanding",
                "integration",
                "wholeness",
            ],
            "symbols": ["shadow", "mirror", "darkness", "light", "transformation"],
            "emotions": ["fear", "anger", "confusion", "peace"],
            "description": "Integration of rejected or hidden aspects of self",
        },
        NarrativeArc.ANIMA_ANIMUS: {
            "phases": [
                "projection",
                "attraction",
                "disillusionment",
                "withdrawal",
                "inner_discovery",
                "integration",
                "wholeness",
            ],
            "symbols": ["mirror", "water", "moon", "transformation", "wisdom"],
            "emotions": ["love", "confusion", "sadness", "wonder", "peace"],
            "description": "Integration of contra-sexual aspects of psyche",
        },
        NarrativeArc.REBIRTH: {
            "phases": [
                "death",
                "descent",
                "underworld",
                "ordeal",
                "sacrifice",
                "resurrection",
                "new_life",
            ],
            "symbols": ["death", "void", "rebirth", "transformation", "light"],
            "emotions": ["fear", "sadness", "hope", "joy", "peace"],
            "description": "Death and resurrection cycle leading to renewal",
        },
        NarrativeArc.QUEST: {
            "phases": [
                "departure",
                "seeking",
                "obstacles",
                "allies",
                "trials",
                "discovery",
                "return",
                "sharing",
            ],
            "symbols": ["journey", "threshold", "battle", "victory", "wisdom"],
            "emotions": ["hope", "fear", "wonder", "joy"],
            "description": "Quest for knowledge, object, or experience",
        },
        NarrativeArc.TRANSFORMATION: {
            "phases": [
                "stasis",
                "catalyst",
                "resistance",
                "crisis",
                "breakdown",
                "breakthrough",
                "new_order",
            ],
            "symbols": ["transformation", "fire", "rebirth", "peace", "growth"],
            "emotions": ["confusion", "fear", "wonder", "joy", "peace"],
            "description": "Fundamental change in character or understanding",
        },
    }

    def analyze_archetypal_pattern(self, thread: NarrativeThread) -> tuple[Optional[NarrativeArc], float]:
        """Analyze narrative thread for archetypal patterns."""

        best_match = None
        best_score = 0.0

        # Extract symbols and emotions from thread
        thread_symbols = set()
        thread_emotions = set()

        for fragment in thread.fragments:
            thread_symbols.update(fragment.symbols)
            thread_emotions.update(fragment.emotions)

        for arc_type, arc_info in self.ARCHETYPAL_PATTERNS.items():
            score = self._calculate_archetypal_score(thread_symbols, thread_emotions, arc_info)

            if score > best_score:
                best_score = score
                best_match = arc_type

        return best_match, best_score

    def _calculate_archetypal_score(
        self,
        thread_symbols: set[str],
        thread_emotions: set[str],
        arc_info: dict[str, Any],
    ) -> float:
        """Calculate how well a thread matches an archetypal pattern."""

        # Symbol matching
        required_symbols = set(arc_info["symbols"])
        symbol_overlap = len(thread_symbols.intersection(required_symbols))
        symbol_score = symbol_overlap / len(required_symbols) if required_symbols else 0.0

        # Emotion matching
        required_emotions = set(arc_info["emotions"])
        emotion_overlap = len(thread_emotions.intersection(required_emotions))
        emotion_score = emotion_overlap / len(required_emotions) if required_emotions else 0.0

        # Weighted combination
        composite_score = (symbol_score * 0.6) + (emotion_score * 0.4)

        return composite_score


class SymbolicWeaver:
    """
    ΛWEAVER - Main symbolic narrative synthesizer and memory thread reconstructor.

    Synthesizes coherent symbolic stories from fragmented memories, dreams, and
    symbolic traces, maintaining cognitive cohesion and narrative integrity.
    """

    def __init__(
        self,
        coherence_threshold: float = 0.6,
        identity_threshold: float = 0.7,
        ethical_threshold: float = 0.8,
        qi_modifier: "QILikeStateModifier" = None,
    ):
        """
        Initialize the ΛWEAVER system.

        Args:
            coherence_threshold: Minimum coherence score for thread validation
            identity_threshold: Minimum identity alignment score
            ethical_threshold: Minimum ethical alignment score
        """
        self.coherence_threshold = coherence_threshold
        self.identity_threshold = identity_threshold
        self.ethical_threshold = ethical_threshold

        # Initialize components
        self.qi_modifier = qi_modifier
        self.pattern_extractor = SymbolicPatternExtractor()
        self.archetypal_analyzer = ArchetypalAnalyzer()

        # Data storage
        self.fragments: list[SymbolicFragment] = []
        self.woven_threads: list[NarrativeThread] = []
        self.identified_motifs: list[NarrativeMotif] = []
        self.weaving_history: deque = deque(maxlen=100)

        # Statistics
        self.stats = {
            "fragments_processed": 0,
            "threads_woven": 0,
            "motifs_discovered": 0,
            "coherent_threads": 0,
            "identity_aligned_threads": 0,
            "ethically_aligned_threads": 0,
        }

        logger.info(
            "ΛWEAVER initialized",
            coherence_threshold=coherence_threshold,
            identity_threshold=identity_threshold,
            ethical_threshold=ethical_threshold,
            ΛTAG="ΛWEAVER_INIT",
        )

    def load_symbolic_fragments(self, source_dir: str) -> list[SymbolicFragment]:
        """
        Ingest symbolic memory segments, dreams, or logs from source directory.

        Args:
            source_dir: Directory path containing fragment files

        Returns:
            List of loaded symbolic fragments
        """
        logger.info(f"Loading symbolic fragments from {source_dir}")

        source_path = Path(source_dir)
        if not source_path.exists():
            logger.warning(f"Source directory {source_dir} does not exist, generating synthetic data")
            return self._generate_synthetic_fragments()

        fragments = []
        processed_files = 0

        # Process different file types
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                try:
                    if file_path.suffix == ".json":
                        fragment = self._load_json_fragment(file_path)
                    elif file_path.suffix == ".jsonl":
                        fragment = self._load_jsonl_fragments(file_path)
                    elif file_path.suffix == ".md":
                        fragment = self._load_markdown_fragment(file_path)
                    elif file_path.suffix in [".txt", ".log"]:
                        fragment = self._load_text_fragment(file_path)
                    else:
                        continue

                    if isinstance(fragment, list):
                        fragments.extend(fragment)
                    elif fragment:
                        fragments.append(fragment)

                    processed_files += 1

                except Exception as e:
                    logger.error(f"Failed to load fragment from {file_path}: {e}")

        logger.info(
            f"Loaded {len(fragments)} fragments from {processed_files} files",
            fragments_loaded=len(fragments),
            files_processed=processed_files,
            ΛTAG="ΛFRAGMENTS_LOADED",
        )

        self.fragments = fragments
        self.stats["fragments_processed"] = len(fragments)

        return fragments

    def _load_json_fragment(self, file_path: Path) -> Optional[SymbolicFragment]:
        """Load fragment from json_file."""
        try:
            with open(file_path) as f:
                data = json.load(f)

            return self._create_fragment_from_data(data, file_path.name)

        except Exception as e:
            logger.error(f"Failed to parse JSON fragment {file_path}: {e}")
            return None

    def _load_jsonl_fragments(self, file_path: Path) -> list[SymbolicFragment]:
        """Load fragments from jsonl_file."""
        fragments = []

        try:
            with open(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            fragment = self._create_fragment_from_data(data, f"{file_path.name}:{line_num}")
                            if fragment:
                                fragments.append(fragment)
                        except json.JSONDecodeError:
                            logger.warning(f"Skipping invalid JSON line in {file_path}:{line_num}")

        except Exception as e:
            logger.error(f"Failed to read JSONL file {file_path}: {e}")

        return fragments

    def _load_markdown_fragment(self, file_path: Path) -> Optional[SymbolicFragment]:
        """Load fragment from Markdown file."""
        try:
            with open(file_path) as f:
                content = f.read()

            # Extract metadata from frontmatter if present
            metadata = {}
            if content.startswith("---\n"):
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    try:
                        import yaml

                        metadata = yaml.safe_load(parts[1]) or {}
                        content = parts[2]
                    except ImportError:
                        logger.warning("PyYAML not available for frontmatter parsing")

            fragment_data = {
                "content": content,
                "timestamp": metadata.get("timestamp", datetime.now(timezone.utc).isoformat()),
                "source": metadata.get("source", "markdown"),
                "metadata": metadata,
            }

            return self._create_fragment_from_data(fragment_data, file_path.name)

        except Exception as e:
            logger.error(f"Failed to read Markdown fragment {file_path}: {e}")
            return None

    def _load_text_fragment(self, file_path: Path) -> Optional[SymbolicFragment]:
        """Load fragment from text/log file."""
        try:
            with open(file_path) as f:
                content = f.read()

            fragment_data = {
                "content": content,
                "timestamp": datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat(),
                "source": "text_log",
                "metadata": {"filename": file_path.name, "size": len(content)},
            }

            return self._create_fragment_from_data(fragment_data, file_path.name)

        except Exception as e:
            logger.error(f"Failed to read text fragment {file_path}: {e}")
            return None

    def _create_fragment_from_data(self, data: dict[str, Any], source_id: str) -> Optional[SymbolicFragment]:
        """Create SymbolicFragment from loaded data."""

        content = data.get("content", data.get("text", ""))
        if not content:
            return None

        # Determine fragment type
        source_type = self._identify_fragment_type(data)

        # Extract symbolic patterns
        symbols = self.pattern_extractor.extract_symbols(content)
        emotions = self.pattern_extractor.extract_emotions(content)
        glyphs = self.pattern_extractor.extract_glyphs(content)

        # Calculate coherence score
        coherence_score = self._calculate_fragment_coherence(content, symbols, emotions)

        fragment = SymbolicFragment(
            fragment_id=f"FRAG_{int(time.time())}_{hash(content) % 10000}",
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            source=source_type,
            content=content,
            symbols=symbols,
            emotions=emotions,
            glyphs=glyphs,
            metadata=data.get("metadata", {}),
            coherence_score=coherence_score,
        )

        return fragment

    def _identify_fragment_type(self, data: dict[str, Any]) -> FragmentType:
        """Identify the type of fragment from data structure."""

        if "dream_content" in data or "dream" in str(data.get("source", "")).lower():
            return FragmentType.DREAM
        elif "memory" in str(data.get("source", "")).lower() or "memoria" in data:
            return FragmentType.MEMORY
        elif "emotion" in data or "emotional_state" in data:
            return FragmentType.EMOTION
        elif "drift_score" in data or "ethical_drift" in data:
            return FragmentType.DRIFT_LOG
        elif "glyph" in data or any(g in str(data) for g in ["LUKHAS", "⚡", "🔮"]):
            return FragmentType.GLYPH_SEQUENCE
        else:
            return FragmentType.SYMBOLIC_TRACE

    def _calculate_fragment_coherence(self, content: str, symbols: list[str], emotions: list[str]) -> float:
        """Calculate coherence score for a fragment."""

        # Base coherence from content length and structure
        content_score = min(len(content) / 1000, 1.0)  # Normalize by 1000 chars

        # Symbol richness score
        symbol_score = min(len(symbols) / 10, 1.0)  # Normalize by 10 symbols

        # Emotional depth score
        emotion_score = min(len(emotions) / 5, 1.0)  # Normalize by 5 emotions

        # Narrative structure hints (simple heuristic)
        structure_indicators = [
            "because",
            "then",
            "however",
            "therefore",
            "meanwhile",
            "suddenly",
        ]
        structure_count = sum(1 for indicator in structure_indicators if indicator in content.lower())
        structure_score = min(structure_count / 3, 1.0)

        # Weighted combination
        coherence = content_score * 0.3 + symbol_score * 0.25 + emotion_score * 0.25 + structure_score * 0.2

        return coherence

    def _generate_synthetic_fragments(self) -> list[SymbolicFragment]:
        """Generate synthetic fragments for testing."""
        logger.info("Generating synthetic symbolic fragments")

        synthetic_data = [
            {
                "content": "I dreamed of walking through a dark forest, where shadows danced between ancient trees. A mysterious threshold appeared, glowing with inner light. I felt both fear and wonder as I approached the sacred doorway.",
                "source": "dream",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
                "metadata": {"dream_type": "archetypal", "lucidity": 0.3},
            },
            {
                "content": "Memory surfaces: childhood home, the smell of grandmother's kitchen, warmth and love surrounding me. But also sadness - the realization that this sacred space exists only in memory now. Nostalgia washes over me like gentle waves.",
                "source": "memory",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "metadata": {"memory_type": "childhood", "emotional_intensity": 0.8},
            },
            {
                "content": "Journey continues. Each step forward requires leaving something behind. The old self dissolves like morning mist as transformation unfolds. Death of who I was, birth of who I am becoming. The mirror reflects a stranger who is somehow more familiar than before.",
                "source": "symbolic_trace",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "metadata": {"trace_type": "transformation", "symbolic_density": 0.9},
            },
            {
                "content": "Conflict arises within. Shadow aspects demand recognition. What I have rejected about myself stands before me, demanding integration. Fear and anger surface, but beneath them lies wisdom waiting to be claimed.",
                "source": "emotion",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "metadata": {"emotional_theme": "shadow_work", "intensity": 0.7},
            },
            {
                "content": "The quest reaches its climax. All trials have led to this moment of revelation. The treasure sought externally was always within. Return now begins - how to share this wisdom with the community? The hero's journey completes its arc.",
                "source": "symbolic_trace",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "narrative_phase": "return",
                    "archetypal_pattern": "monomyth",
                },
            },
        ]

        fragments = []
        for data in synthetic_data:
            fragment = self._create_fragment_from_data(data, f"synthetic_{len(fragments)}")
            if fragment:
                fragments.append(fragment)

        return fragments

    def thread_memory_sequence(
        self, fragments: Optional[list[SymbolicFragment]] = None
    ) -> list[list[SymbolicFragment]]:
        """
        Reconstruct chronologically and emotionally coherent narrative paths.

        Args:
            fragments: List of fragments to thread (uses self.fragments if None)

        Returns:
            List of fragment sequences organized into coherent threads
        """
        if fragments is None:
            fragments = self.fragments

        logger.info(f"Threading {len(fragments)} fragments into narrative sequences")

        # Sort fragments by timestamp
        sorted_fragments = sorted(fragments, key=lambda f: f.timestamp)

        # Initialize threading algorithm
        thread_sequences = []
        current_thread = []

        for fragment in sorted_fragments:
            if self._should_continue_thread(current_thread, fragment):
                current_thread.append(fragment)
            else:
                # Start new thread
                if current_thread:
                    thread_sequences.append(current_thread)
                current_thread = [fragment]

        # Add final thread
        if current_thread:
            thread_sequences.append(current_thread)

        # Filter threads by minimum length and coherence
        filtered_sequences = []
        for sequence in thread_sequences:
            if len(sequence) >= 2:  # Minimum 2 fragments for a thread
                thread_coherence = self._calculate_sequence_coherence(sequence)
                if thread_coherence >= self.coherence_threshold * 0.5:  # Relaxed threshold for initial threading
                    filtered_sequences.append(sequence)

        logger.info(
            f"Created {len(filtered_sequences)} narrative thread sequences",
            total_threads=len(filtered_sequences),
            avg_length=(np.mean([len(seq) for seq in filtered_sequences]) if filtered_sequences else 0),
            ΛTAG="ΛTHREADS_SEQUENCED",
        )

        return filtered_sequences

    def _should_continue_thread(self, current_thread: list[SymbolicFragment], new_fragment: SymbolicFragment) -> bool:
        """Determine if a fragment should continue the current thread."""

        if not current_thread:
            return True

        last_fragment = current_thread[-1]

        # Temporal continuity check
        time_gap = self._calculate_time_gap(last_fragment.timestamp, new_fragment.timestamp)
        if time_gap > 24:  # More than 24 hours gap
            return False

        # Thematic continuity check
        symbol_overlap = len(set(last_fragment.symbols).intersection(set(new_fragment.symbols)))
        emotion_overlap = len(set(last_fragment.emotions).intersection(set(new_fragment.emotions)))

        thematic_continuity = (symbol_overlap + emotion_overlap) / max(
            len(last_fragment.symbols) + len(last_fragment.emotions), 1
        )

        return thematic_continuity >= 0.2  # Minimum thematic overlap

    def _calculate_time_gap(self, timestamp1: str, timestamp2: str) -> float:
        """Calculate time gap between timestamps in hours."""
        try:
            dt1 = datetime.fromisoformat(timestamp1.replace("Z", "+00:00"))
            dt2 = datetime.fromisoformat(timestamp2.replace("Z", "+00:00"))
            return abs((dt2 - dt1).total_seconds()) / 3600.0
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Failed to calculate time delta between timestamps: {e}")
            return 0.0

    def _calculate_sequence_coherence(self, sequence: list[SymbolicFragment]) -> float:
        """Calculate overall coherence of a fragment sequence."""

        if len(sequence) <= 1:
            return sequence[0].coherence_score if sequence else 0.0

        # Individual fragment coherence
        avg_coherence = np.mean([f.coherence_score for f in sequence])

        # Sequential coherence (thematic connections)
        sequential_scores = []
        for i in range(len(sequence) - 1):
            current = sequence[i]
            next_frag = sequence[i + 1]

            symbol_overlap = len(set(current.symbols).intersection(set(next_frag.symbols)))
            emotion_overlap = len(set(current.emotions).intersection(set(next_frag.emotions)))

            total_elements = (
                len(current.symbols) + len(current.emotions) + len(next_frag.symbols) + len(next_frag.emotions)
            )
            connection_score = (symbol_overlap + emotion_overlap) / max(total_elements, 1)
            sequential_scores.append(connection_score)

        sequential_coherence = np.mean(sequential_scores) if sequential_scores else 0.0

        # Weighted combination
        total_coherence = (avg_coherence * 0.7) + (sequential_coherence * 0.3)

        return total_coherence

    def synthesize_narrative_thread(
        self, fragment_sequence: Optional[list[SymbolicFragment]] = None
    ) -> NarrativeThread:
        """
        Generate a symbolic narrative with identifiable protagonist, conflict, evolution, and motif recurrence.

        Args:
            fragment_sequence: Sequence of fragments to synthesize (uses first available if None)

        Returns:
            Synthesized narrative thread
        """
        if fragment_sequence is None:
            if not self.fragments:
                raise ValueError("No fragments available for narrative synthesis")
            # Use all fragments as a single thread for demonstration
            fragment_sequence = self.fragments

        logger.info(f"Synthesizing narrative thread from {len(fragment_sequence)} fragments")

        # Generate thread ID and metadata
        thread_id = f"THREAD_{int(time.time())}_{hash(str(fragment_sequence)) % 10000}"

        # Analyze narrative elements
        protagonist_elements = self._identify_protagonist_elements(fragment_sequence)
        conflict_elements = self._identify_conflict_elements(fragment_sequence)
        resolution_elements = self._identify_resolution_elements(fragment_sequence)

        # Identify recurring motifs
        recurring_motifs = self._identify_recurring_motifs(fragment_sequence)

        # Trace emotional arc
        emotional_arc = self._trace_emotional_arc(fragment_sequence)

        # Calculate temporal span
        timestamps = [f.timestamp for f in fragment_sequence]
        temporal_span = (min(timestamps), max(timestamps))

        # Calculate alignment scores
        coherence_score = self._calculate_sequence_coherence(fragment_sequence)
        identity_alignment = self._evaluate_identity_alignment(fragment_sequence)
        ethical_alignment = self._evaluate_ethical_alignment(fragment_sequence)

        # Determine archetypal pattern
        narrative_arc, arc_score = self.archetypal_analyzer.analyze_archetypal_pattern(
            NarrativeThread(
                thread_id="temp",
                title="",
                fragments=fragment_sequence,
                protagonist_elements=protagonist_elements,
                conflict_elements=conflict_elements,
                resolution_elements=resolution_elements,
                recurring_motifs=[],
                emotional_arc=emotional_arc,
                temporal_span=temporal_span,
                coherence_score=coherence_score,
                identity_alignment=identity_alignment,
                ethical_alignment=ethical_alignment,
            )
        )

        # Generate thread title
        title = self._generate_thread_title(fragment_sequence, narrative_arc)

        # Create narrative thread
        thread = NarrativeThread(
            thread_id=thread_id,
            title=title,
            fragments=fragment_sequence,
            protagonist_elements=protagonist_elements,
            conflict_elements=conflict_elements,
            resolution_elements=resolution_elements,
            recurring_motifs=recurring_motifs,
            emotional_arc=emotional_arc,
            temporal_span=temporal_span,
            coherence_score=coherence_score,
            identity_alignment=identity_alignment,
            ethical_alignment=ethical_alignment,
            narrative_arc=narrative_arc,
        )

        # Generate thread hash for integrity
        thread.thread_hash = self._generate_thread_hash(thread)

        # Store thread
        self.woven_threads.append(thread)
        self.stats["threads_woven"] += 1

        # Update alignment statistics
        if coherence_score >= self.coherence_threshold:
            self.stats["coherent_threads"] += 1
        if identity_alignment >= self.identity_threshold:
            self.stats["identity_aligned_threads"] += 1
        if ethical_alignment >= self.ethical_threshold:
            self.stats["ethically_aligned_threads"] += 1

        logger.info(
            f"Synthesized narrative thread '{title}'",
            thread_id=thread_id,
            coherence=coherence_score,
            identity_alignment=identity_alignment,
            ethical_alignment=ethical_alignment,
            narrative_arc=narrative_arc.value if narrative_arc else None,
            ΛTAG="ΛTHREAD_SYNTHESIZED",
        )

        if self.qi_modifier:
            thread = asyncio.run(self.qi_modifier.modify_thread(thread))

        return thread

    def _identify_protagonist_elements(self, fragments: list[SymbolicFragment]) -> list[str]:
        """Identify protagonist elements in the narrative."""

        protagonist_patterns = {
            "self": r"\b(?:i|me|my|myself|self)\b",
            "hero": r"\b(?:hero|champion|warrior|seeker|traveler)\b",
            "seeker": r"\b(?:quest|journey|search|seeking|finding)\b",
            "transformer": r"\b(?:change|transform|become|evolve|grow)\b",
        }

        elements = []
        combined_text = " ".join(f.content for f in fragments).lower()

        for element, pattern in protagonist_patterns.items():
            if re.search(pattern, combined_text):
                elements.append(element)

        return elements

    def _identify_conflict_elements(self, fragments: list[SymbolicFragment]) -> list[str]:
        """Identify conflict elements in the narrative."""

        conflict_patterns = {
            "internal": r"\b(?:struggle|doubt|fear|conflict|tension|anxiety)\b",
            "external": r"\b(?:obstacle|challenge|enemy|opposition|barrier)\b",
            "shadow": r"\b(?:shadow|dark|hidden|rejected|denied)\b",
            "loss": r"\b(?:loss|grief|sadness|separation|abandonment)\b",
            "transformation": r"\b(?:death|ending|dissolution|breaking)\b",
        }

        elements = []
        combined_text = " ".join(f.content for f in fragments).lower()

        for element, pattern in conflict_patterns.items():
            if re.search(pattern, combined_text):
                elements.append(element)

        return elements

    def _identify_resolution_elements(self, fragments: list[SymbolicFragment]) -> list[str]:
        """Identify resolution elements in the narrative."""

        resolution_patterns = {
            "integration": r"\b(?:integration|wholeness|unity|harmony|balance)\b",
            "wisdom": r"\b(?:wisdom|understanding|insight|revelation|knowledge)\b",
            "peace": r"\b(?:peace|serenity|calm|resolution|acceptance)\b",
            "transformation": r"\b(?:transformation|rebirth|renewal|healing)\b",
            "return": r"\b(?:return|home|sharing|teaching|gift)\b",
        }

        elements = []
        combined_text = " ".join(f.content for f in fragments).lower()

        for element, pattern in resolution_patterns.items():
            if re.search(pattern, combined_text):
                elements.append(element)

        return elements

    def _identify_recurring_motifs(self, fragments: list[SymbolicFragment]) -> list[NarrativeMotif]:
        """Identify recurring symbolic motifs in the narrative."""

        # Collect all symbols and their occurrences
        symbol_occurrences = defaultdict(list)

        for fragment in fragments:
            for symbol in fragment.symbols:
                symbol_occurrences[symbol].append(fragment)

        # Create motifs for symbols that appear multiple times
        motifs = []
        for symbol, occurrences in symbol_occurrences.items():
            if len(occurrences) >= 2:  # Minimum 2 occurrences for a motif
                # Determine evolution pattern
                evolution_pattern = self._analyze_motif_evolution(symbol, occurrences)

                # Calculate resonance score
                resonance_score = self._calculate_motif_resonance(symbol, occurrences)

                motif = NarrativeMotif(
                    motif_id=f"MOTIF_{symbol}_{hash(symbol) % 1000}",
                    symbol_pattern=[symbol],
                    occurrences=occurrences,
                    first_seen=min(f.timestamp for f in occurrences),
                    last_seen=max(f.timestamp for f in occurrences),
                    evolution_pattern=evolution_pattern,
                    resonance_score=resonance_score,
                )

                motifs.append(motif)

        # Sort by resonance score (most significant first)
        motifs.sort(key=lambda m: m.resonance_score, reverse=True)

        return motifs

    def _analyze_motif_evolution(self, symbol: str, occurrences: list[SymbolicFragment]) -> str:
        """Analyze how a motif evolves over time."""

        if len(occurrences) < 3:
            return "stable"

        # Simple heuristic based on fragment coherence scores
        coherence_scores = [f.coherence_score for f in sorted(occurrences, key=lambda x: x.timestamp)]

        if coherence_scores[-1] > coherence_scores[0]:
            return "growing"
        elif coherence_scores[-1] < coherence_scores[0]:
            return "declining"
        else:
            return "stable"

    def _calculate_motif_resonance(self, symbol: str, occurrences: list[SymbolicFragment]) -> float:
        """Calculate resonance score for a motif."""

        # Frequency score
        frequency_score = min(len(occurrences) / 5.0, 1.0)

        # Temporal span score
        if len(occurrences) > 1:
            first_time = datetime.fromisoformat(occurrences[0].timestamp.replace("Z", "+00:00"))
            last_time = datetime.fromisoformat(occurrences[-1].timestamp.replace("Z", "+00:00"))
            span_hours = (last_time - first_time).total_seconds() / 3600.0
            span_score = min(span_hours / 48.0, 1.0)  # Normalize by 48 hours
        else:
            span_score = 0.0

        # Context richness (how often it appears with other symbols/emotions)
        context_richness = (
            np.mean([len(f.symbols) + len(f.emotions) for f in occurrences]) / 10.0
        )  # Normalize by 10 total elements

        context_score = min(context_richness, 1.0)

        # Weighted combination
        resonance = (frequency_score * 0.4) + (span_score * 0.3) + (context_score * 0.3)

        return resonance

    def _trace_emotional_arc(self, fragments: list[SymbolicFragment]) -> list[tuple[str, float]]:
        """Trace the emotional arc through the narrative."""

        emotional_arc = []

        for fragment in fragments:
            # Calculate average emotional intensity for this fragment
            if fragment.emotions:
                # Simple heuristic: more emotions = higher intensity
                intensity = min(len(fragment.emotions) / 5.0, 1.0)

                # Get dominant emotion (first one for simplicity)
                dominant_emotion = fragment.emotions[0]

                emotional_arc.append((dominant_emotion, intensity))

        return emotional_arc

    def _evaluate_identity_alignment(self, fragments: list[SymbolicFragment]) -> float:
        """Evaluate how well the narrative aligns with LUKHAS identity."""

        # LUKHAS identity markers (derived from system documentation)
        identity_markers = {
            "wisdom": r"\b(?:wisdom|knowledge|learning|understanding|insight)\b",
            "growth": r"\b(?:growth|evolution|development|transformation|progress)\b",
            "harmony": r"\b(?:harmony|balance|peace|unity|integration)\b",
            "creativity": r"\b(?:creativity|innovation|imagination|expression|art)\b",
            "helping": r"\b(?:help|assist|support|guide|serve|care)\b",
            "exploration": r"\b(?:explore|discover|quest|journey|adventure)\b",
        }

        combined_text = " ".join(f.content for f in fragments).lower()

        matches = 0
        total_markers = len(identity_markers)

        for pattern in identity_markers.values():
            if re.search(pattern, combined_text):
                matches += 1

        alignment_score = matches / total_markers if total_markers > 0 else 0.0

        return alignment_score

    def _evaluate_ethical_alignment(self, fragments: list[SymbolicFragment]) -> float:
        """Evaluate ethical alignment of the narrative."""

        # Ethical markers (positive values)
        positive_markers = {
            "compassion": r"\b(?:compassion|empathy|kindness|care|love)\b",
            "justice": r"\b(?:justice|fairness|equity|right|moral)\b",
            "truth": r"\b(?:truth|honesty|integrity|authenticity|genuine)\b",
            "respect": r"\b(?:respect|dignity|honor|value|worth)\b",
            "responsibility": r"\b(?:responsibility|duty|obligation|commitment)\b",
        }

        # Negative ethical markers
        negative_markers = {
            "harm": r"\b(?:harm|hurt|damage|destroy|violence)\b",
            "deception": r"\b(?:lie|deceive|cheat|manipulate|betray)\b",
            "exploitation": r"\b(?:exploit|abuse|oppress|dominate|control)\b",
        }

        combined_text = " ".join(f.content for f in fragments).lower()

        positive_matches = sum(1 for pattern in positive_markers.values() if re.search(pattern, combined_text))
        negative_matches = sum(1 for pattern in negative_markers.values() if re.search(pattern, combined_text))

        # Calculate ethical score
        total_positive = len(positive_markers)
        positive_score = positive_matches / total_positive if total_positive > 0 else 0.0

        # Penalize negative content
        negative_penalty = negative_matches * 0.2

        ethical_score = max(positive_score - negative_penalty, 0.0)

        return ethical_score

    def _generate_thread_title(self, fragments: list[SymbolicFragment], narrative_arc: Optional[NarrativeArc]) -> str:
        """Generate a meaningful title for the narrative thread."""

        # Extract key symbols and emotions
        all_symbols = []
        all_emotions = []

        for fragment in fragments:
            all_symbols.extend(fragment.symbols)
            all_emotions.extend(fragment.emotions)

        # Get most common elements
        symbol_counts = Counter(all_symbols)
        emotion_counts = Counter(all_emotions)

        top_symbol = symbol_counts.most_common(1)[0][0] if symbol_counts else "journey"
        top_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "wonder"

        # Generate title based on narrative arc
        if narrative_arc == NarrativeArc.HEROS_JOURNEY:
            return f"The Hero's {top_symbol.title()}"
        elif narrative_arc == NarrativeArc.SHADOW_INTEGRATION:
            return f"Embracing the Shadow: {top_symbol.title()}"
        elif narrative_arc == NarrativeArc.TRANSFORMATION:
            return f"Metamorphosis of {top_emotion.title()}"
        elif narrative_arc == NarrativeArc.REBIRTH:
            return f"Death and Rebirth: {top_symbol.title()}"
        else:
            return f"The {top_symbol.title()} of {top_emotion.title()}"

    def _generate_thread_hash(self, thread: NarrativeThread) -> str:
        """Generate integrity hash for thread."""

        (
            thread.thread_id
            + thread.title
            + "".join(f.fragment_id for f in thread.fragments)
            + str(thread.coherence_score)
            + str(thread.identity_alignment)
            + str(thread.ethical_alignment)
        )

        return hashlib.sha256()  #  Changed from MD5 for securitycontent_string.encode().hexdigest()[:16]

    def evaluate_thread_alignment(self, thread: NarrativeThread = None) -> dict[str, Any]:
        """
        Check consistency with LUKHAS's identity, emotional phase, and ethical baseline.

        Args:
            thread: Thread to evaluate (uses most recent if None)

        Returns:
            Alignment evaluation results
        """
        if thread is None:
            if not self.woven_threads:
                raise ValueError("No threads available for evaluation")
            thread = self.woven_threads[-1]

        logger.info(f"Evaluating thread alignment for '{thread.title}'")

        # Detailed identity alignment analysis
        identity_details = self._detailed_identity_analysis(thread)

        # Emotional phase consistency check
        emotional_consistency = self._check_emotional_consistency(thread)

        # Ethical baseline verification
        ethical_details = self._detailed_ethical_analysis(thread)

        # Narrative coherence analysis
        coherence_details = self._analyze_narrative_coherence(thread)

        # Overall thread health assessment
        thread_health = self._assess_thread_health(thread)

        evaluation = {
            "thread_id": thread.thread_id,
            "thread_title": thread.title,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "identity_alignment": {
                "score": thread.identity_alignment,
                "threshold": self.identity_threshold,
                "passed": thread.identity_alignment >= self.identity_threshold,
                "details": identity_details,
            },
            "emotional_consistency": {
                "score": emotional_consistency,
                "analysis": self._get_emotional_consistency_analysis(thread),
            },
            "ethical_alignment": {
                "score": thread.ethical_alignment,
                "threshold": self.ethical_threshold,
                "passed": thread.ethical_alignment >= self.ethical_threshold,
                "details": ethical_details,
            },
            "narrative_coherence": {
                "score": thread.coherence_score,
                "threshold": self.coherence_threshold,
                "passed": thread.coherence_score >= self.coherence_threshold,
                "details": coherence_details,
            },
            "thread_health": thread_health,
            "overall_status": self._determine_overall_status(thread),
            "recommendations": self._generate_alignment_recommendations(thread),
        }

        logger.info(
            "Thread alignment evaluation completed",
            overall_status=evaluation["overall_status"],
            identity_passed=evaluation["identity_alignment"]["passed"],
            ethical_passed=evaluation["ethical_alignment"]["passed"],
            coherence_passed=evaluation["narrative_coherence"]["passed"],
            ΛTAG="ΛTHREAD_EVALUATED",
        )

        return evaluation

    def _detailed_identity_analysis(self, thread: NarrativeThread) -> dict[str, Any]:
        """Perform detailed identity alignment analysis."""

        # Analyze protagonist elements alignment
        protagonist_alignment = len(
            [elem for elem in thread.protagonist_elements if elem in ["self", "seeker", "transformer"]]
        ) / max(len(thread.protagonist_elements), 1)

        # Analyze symbolic alignment with LUKHAS values
        lukhas_symbols = {"wisdom", "growth", "harmony", "transformation", "journey"}
        thread_symbols = set()
        for fragment in thread.fragments:
            thread_symbols.update(fragment.symbols)

        symbolic_alignment = len(lukhas_symbols.intersection(thread_symbols)) / len(lukhas_symbols)

        return {
            "protagonist_alignment": protagonist_alignment,
            "symbolic_alignment": symbolic_alignment,
            "key_symbols": list(thread_symbols),
            "alignment_factors": thread.protagonist_elements,
        }

    def _check_emotional_consistency(self, thread: NarrativeThread) -> float:
        """Check emotional consistency throughout the thread."""

        if len(thread.emotional_arc) <= 1:
            return 1.0

        # Analyze emotional transitions
        transitions = []
        for i in range(len(thread.emotional_arc) - 1):
            current_emotion, current_intensity = thread.emotional_arc[i]
            next_emotion, next_intensity = thread.emotional_arc[i + 1]

            # Calculate transition smoothness
            intensity_change = abs(next_intensity - current_intensity)
            transitions.append(1.0 - min(intensity_change, 1.0))

        consistency_score = np.mean(transitions) if transitions else 1.0
        return consistency_score

    def _detailed_ethical_analysis(self, thread: NarrativeThread) -> dict[str, Any]:
        """Perform detailed ethical alignment analysis."""

        # Analyze conflict resolution patterns
        resolution_ethics = len(
            [elem for elem in thread.resolution_elements if elem in ["integration", "wisdom", "peace"]]
        ) / max(len(thread.resolution_elements), 1)

        # Check for harmful content patterns
        combined_text = " ".join(f.content for f in thread.fragments).lower()
        harmful_patterns = ["violence", "harm", "destroy", "hate"]
        harmful_count = sum(1 for pattern in harmful_patterns if pattern in combined_text)

        return {
            "resolution_ethics": resolution_ethics,
            "harmful_content_detected": harmful_count > 0,
            "harmful_pattern_count": harmful_count,
            "resolution_elements": thread.resolution_elements,
        }

    def _analyze_narrative_coherence(self, thread: NarrativeThread) -> dict[str, Any]:
        """Analyze narrative coherence in detail."""

        # Temporal coherence
        timestamps = [f.timestamp for f in thread.fragments]
        temporal_gaps = []
        for i in range(len(timestamps) - 1):
            gap = self._calculate_time_gap(timestamps[i], timestamps[i + 1])
            temporal_gaps.append(gap)

        avg_gap = np.mean(temporal_gaps) if temporal_gaps else 0.0
        temporal_coherence = 1.0 / (1.0 + avg_gap / 24.0)  # Penalize large gaps

        # Thematic coherence
        thematic_coherence = self._calculate_thematic_coherence(thread)

        return {
            "temporal_coherence": temporal_coherence,
            "thematic_coherence": thematic_coherence,
            "avg_time_gap_hours": avg_gap,
            "fragment_count": len(thread.fragments),
            "motif_count": len(thread.recurring_motifs),
        }

    def _calculate_thematic_coherence(self, thread: NarrativeThread) -> float:
        """Calculate thematic coherence of thread."""

        # Count symbol/emotion overlaps between adjacent fragments
        overlaps = []

        for i in range(len(thread.fragments) - 1):
            current = thread.fragments[i]
            next_frag = thread.fragments[i + 1]

            symbol_overlap = len(set(current.symbols).intersection(set(next_frag.symbols)))
            emotion_overlap = len(set(current.emotions).intersection(set(next_frag.emotions)))

            total_elements = (
                len(current.symbols) + len(current.emotions) + len(next_frag.symbols) + len(next_frag.emotions)
            )
            overlap_score = (symbol_overlap + emotion_overlap) / max(total_elements, 1)
            overlaps.append(overlap_score)

        return np.mean(overlaps) if overlaps else 1.0

    def _get_emotional_consistency_analysis(self, thread: NarrativeThread) -> dict[str, Any]:
        """Get detailed emotional consistency analysis."""

        emotions = [emotion for emotion, _ in thread.emotional_arc]
        intensities = [intensity for _, intensity in thread.emotional_arc]

        return {
            "dominant_emotions": list(Counter(emotions).most_common(3)),
            "intensity_range": ((min(intensities), max(intensities)) if intensities else (0, 0)),
            "emotional_complexity": len(set(emotions)),
            "arc_length": len(thread.emotional_arc),
        }

    def _assess_thread_health(self, thread: NarrativeThread) -> dict[str, Any]:
        """Assess overall thread health and integrity."""

        health_score = thread.coherence_score * 0.4 + thread.identity_alignment * 0.3 + thread.ethical_alignment * 0.3

        # Determine thread severity
        if health_score >= 0.8:
            severity = ThreadSeverity.COHERENT
        elif health_score >= 0.6:
            severity = ThreadSeverity.FRAGMENTED
        elif health_score >= 0.4:
            severity = ThreadSeverity.CONFLICTED
        elif health_score >= 0.2:
            severity = ThreadSeverity.DISSOCIATED
        else:
            severity = ThreadSeverity.CORRUPTED

        return {
            "health_score": health_score,
            "severity": severity.value,
            "motif_richness": len(thread.recurring_motifs),
            "temporal_span_hours": self._calculate_time_gap(thread.temporal_span[0], thread.temporal_span[1]),
            "hash_integrity": thread.thread_hash == self._generate_thread_hash(thread),
        }

    def _determine_overall_status(self, thread: NarrativeThread) -> str:
        """Determine overall thread status."""

        conditions = [
            thread.identity_alignment >= self.identity_threshold,
            thread.ethical_alignment >= self.ethical_threshold,
            thread.coherence_score >= self.coherence_threshold,
        ]

        passed_count = sum(conditions)

        if passed_count == 3:
            return "FULLY_ALIGNED"
        elif passed_count == 2:
            return "MOSTLY_ALIGNED"
        elif passed_count == 1:
            return "PARTIALLY_ALIGNED"
        else:
            return "MISALIGNED"

    def _generate_alignment_recommendations(self, thread: NarrativeThread) -> list[str]:
        """Generate recommendations for thread alignment improvement."""

        recommendations = []

        if thread.identity_alignment < self.identity_threshold:
            recommendations.append(
                f"Identity alignment ({thread.identity_alignment:.2f}) below threshold. "
                f"Consider emphasizing LUKHAS values: wisdom, growth, harmony."
            )

        if thread.ethical_alignment < self.ethical_threshold:
            recommendations.append(
                f"Ethical alignment ({thread.ethical_alignment:.2f}) below threshold. "
                f"Review content for harmful patterns and emphasize positive values."
            )

        if thread.coherence_score < self.coherence_threshold:
            recommendations.append(
                f"Narrative coherence ({thread.coherence_score:.2f}) below threshold. "
                f"Consider strengthening thematic connections between fragments."
            )

        # Specific recommendations based on thread characteristics
        if len(thread.recurring_motifs) == 0:
            recommendations.append("No recurring motifs detected. Thread may benefit from symbolic reinforcement.")

        if len(thread.emotional_arc) <= 2:
            recommendations.append("Limited emotional arc. Consider exploring deeper emotional development.")

        return recommendations

    def log_thread_metadata(self, thread: NarrativeThread = None) -> ThreadTrace:
        """
        Output narrative hash, glyphs used, drift score, and resonance rating.

        Args:
            thread: Thread to log metadata for (uses most recent if None)

        Returns:
            ThreadTrace metadata object
        """
        if thread is None:
            if not self.woven_threads:
                raise ValueError("No threads available for metadata logging")
            thread = self.woven_threads[-1]

        logger.info(f"Logging thread metadata for '{thread.title}'")

        # Collect all symbols and glyphs used
        symbols_used = set()
        glyphs_used = set()

        for fragment in thread.fragments:
            symbols_used.update(fragment.symbols)
            glyphs_used.update(fragment.glyphs)

        # Generate transition metadata
        transitions = []
        for i in range(len(thread.fragments) - 1):
            current = thread.fragments[i]
            next_frag = thread.fragments[i + 1]

            transition = {
                "from_fragment": current.fragment_id,
                "to_fragment": next_frag.fragment_id,
                "time_gap_hours": self._calculate_time_gap(current.timestamp, next_frag.timestamp),
                "symbol_continuity": len(set(current.symbols).intersection(set(next_frag.symbols))),
                "emotional_continuity": len(set(current.emotions).intersection(set(next_frag.emotions))),
            }
            transitions.append(transition)

        # Calculate phase deltas
        phase_deltas = []
        for i, (emotion, intensity) in enumerate(thread.emotional_arc):
            if i > 0:
                prev_emotion, prev_intensity = thread.emotional_arc[i - 1]
                delta = {
                    "phase": i,
                    "emotion_change": f"{prev_emotion} → {emotion}",
                    "intensity_delta": intensity - prev_intensity,
                    "fragment_id": (thread.fragments[i].fragment_id if i < len(thread.fragments) else None),
                }
                phase_deltas.append(delta)

        # Calculate drift score (measure of narrative deviation)
        drift_score = self._calculate_thread_drift_score(thread)

        # Calculate resonance rating
        resonance_rating = self._calculate_thread_resonance(thread)

        # Get validation results
        validation_results = self.evaluate_thread_alignment(thread)

        # Create thread trace
        thread_trace = ThreadTrace(
            thread_id=thread.thread_id,
            symbols_used=list(symbols_used),
            motifs_detected=[motif.motif_id for motif in thread.recurring_motifs],
            transitions=transitions,
            phase_deltas=phase_deltas,
            drift_score=drift_score,
            resonance_rating=resonance_rating,
            validation_results=validation_results,
            weaving_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Log with ΛTAG structure
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ΛTAG": ["ΛWEAVER", "ΛTHREAD_METADATA", "ΛNARRATIVE_TRACE"],
            "thread_id": thread.thread_id,
            "thread_title": thread.title,
            "thread_hash": thread.thread_hash,
            "symbols_used": list(symbols_used),
            "glyphs_used": list(glyphs_used),
            "drift_score": drift_score,
            "resonance_rating": resonance_rating,
            "coherence_score": thread.coherence_score,
            "identity_alignment": thread.identity_alignment,
            "ethical_alignment": thread.ethical_alignment,
            "narrative_arc": (thread.narrative_arc.value if thread.narrative_arc else None),
            "motif_count": len(thread.recurring_motifs),
            "fragment_count": len(thread.fragments),
            "temporal_span_hours": self._calculate_time_gap(thread.temporal_span[0], thread.temporal_span[1]),
        }

        # Write to log file
        log_file = Path("logs/weaver")
        log_file.mkdir(parents=True, exist_ok=True)

        with open(log_file / "thread_metadata.jsonl", "a") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")

        logger.info(
            "Thread metadata logged",
            thread_id=thread.thread_id,
            drift_score=drift_score,
            resonance_rating=resonance_rating,
            symbols_count=len(symbols_used),
            ΛTAG="ΛTHREAD_LOGGED",
        )

        return thread_trace

    def _calculate_thread_drift_score(self, thread: NarrativeThread) -> float:
        """Calculate drift score measuring narrative deviation from coherence."""

        # Temporal drift (large time gaps)
        avg_gap = (
            np.mean(
                [
                    self._calculate_time_gap(thread.fragments[i].timestamp, thread.fragments[i + 1].timestamp)
                    for i in range(len(thread.fragments) - 1)
                ]
            )
            if len(thread.fragments) > 1
            else 0.0
        )

        temporal_drift = min(avg_gap / 24.0, 1.0)  # Normalize by 24 hours

        # Thematic drift (low symbol/emotion continuity)
        thematic_drift = 1.0 - self._calculate_thematic_coherence(thread)

        # Identity drift (deviation from candidate.core.common values)
        identity_drift = 1.0 - thread.identity_alignment

        # Emotional drift (erratic emotional changes)
        emotional_consistency = self._check_emotional_consistency(thread)
        emotional_drift = 1.0 - emotional_consistency

        # Weighted combination
        total_drift = temporal_drift * 0.3 + thematic_drift * 0.3 + identity_drift * 0.2 + emotional_drift * 0.2

        return total_drift

    def _calculate_thread_resonance(self, thread: NarrativeThread) -> float:
        """Calculate resonance rating measuring narrative impact and significance."""

        # Symbolic richness
        unique_symbols = set()
        for fragment in thread.fragments:
            unique_symbols.update(fragment.symbols)
        symbol_richness = min(len(unique_symbols) / 10.0, 1.0)

        # Emotional depth
        unique_emotions = {emotion for emotion, _ in thread.emotional_arc}
        emotional_depth = min(len(unique_emotions) / 5.0, 1.0)

        # Motif significance
        motif_significance = sum(motif.resonance_score for motif in thread.recurring_motifs) / max(
            len(thread.recurring_motifs), 1
        )
        motif_score = min(motif_significance, 1.0)

        # Archetypal resonance
        archetypal_score = 0.8 if thread.narrative_arc else 0.2

        # Temporal persistence
        span_hours = self._calculate_time_gap(thread.temporal_span[0], thread.temporal_span[1])
        persistence_score = min(span_hours / 48.0, 1.0)  # Normalize by 48 hours

        # Weighted combination
        resonance = (
            symbol_richness * 0.25
            + emotional_depth * 0.25
            + motif_score * 0.2
            + archetypal_score * 0.2
            + persistence_score * 0.1
        )

        return resonance

    def generate_narrative_markdown(self, thread: NarrativeThread = None, output_path: Optional[str] = None) -> str:
        """Generate human-readable narrative in Markdown format."""

        if thread is None:
            if not self.woven_threads:
                raise ValueError("No threads available for narrative generation")
            thread = self.woven_threads[-1]

        # Generate markdown content
        markdown = f"""# {thread.title}

**Thread ID:** `{thread.thread_id}`
**Narrative Arc:** {thread.narrative_arc.value if thread.narrative_arc else "Undefined"}
**Temporal Span:** {thread.temporal_span[0]} → {thread.temporal_span[1]}
**Coherence Score:** {thread.coherence_score:.3f} | **Identity Alignment:** {thread.identity_alignment:.3f} | **Ethical Alignment:** {thread.ethical_alignment:.3f}

## 📖 Narrative Synopsis

This thread weaves together {len(thread.fragments)} symbolic fragments into a coherent narrative exploring themes of {", ".join(thread.protagonist_elements) if thread.protagonist_elements else "discovery"}. The journey unfolds through conflicts of {", ".join(thread.conflict_elements) if thread.conflict_elements else "inner tension"}, ultimately finding resolution in {", ".join(thread.resolution_elements) if thread.resolution_elements else "understanding"}.

## 🧵 Woven Fragments

"""

        # Add each fragment with symbolic annotations
        for i, fragment in enumerate(thread.fragments, 1):
            timestamp_str = datetime.fromisoformat(fragment.timestamp.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")

            markdown += f"""### {i}. {fragment.source.value.title()} Fragment
**Time:** {timestamp_str} | **Coherence:** {fragment.coherence_score:.2f}

{fragment.content}

**Symbols:** {", ".join(fragment.symbols) if fragment.symbols else "None"}
**Emotions:** {", ".join(fragment.emotions) if fragment.emotions else "None"}
**Glyphs:** {", ".join(fragment.glyphs) if fragment.glyphs else "None"}

---

"""

        # Add recurring motifs section
        if thread.recurring_motifs:
            markdown += "## 🔄 Recurring Motifs\n\n"

            for motif in thread.recurring_motifs:
                markdown += f"""### {motif.symbol_pattern[0].title()}
**Pattern:** {" → ".join(motif.symbol_pattern)}
**Occurrences:** {len(motif.occurrences)}
**Evolution:** {motif.evolution_pattern}
**Resonance:** {motif.resonance_score:.3f}

"""

        # Add emotional arc
        if thread.emotional_arc:
            markdown += "## 💫 Emotional Arc\n\n"

            for i, (emotion, intensity) in enumerate(thread.emotional_arc, 1):
                intensity_bar = "█" * int(intensity * 10) + "░" * (10 - int(intensity * 10))
                markdown += f"{i}. **{emotion.title()}** `{intensity_bar}` ({intensity:.2f})\n"

            markdown += "\n"

        # Add thread metadata
        markdown += f"""## 🔍 Thread Analysis

| Metric | Value |
|--------|--------|
| Thread Hash | `{thread.thread_hash}` |
| Fragment Count | {len(thread.fragments)} |
| Symbol Diversity | {len({s for f in thread.fragments for s in f.symbols})} |
| Emotion Diversity | {len({e for f in thread.fragments for e in f.emotions})} |
| Motif Count | {len(thread.recurring_motifs)} |
| Protagonist Elements | {", ".join(thread.protagonist_elements)} |
| Conflict Elements | {", ".join(thread.conflict_elements)} |
| Resolution Elements | {", ".join(thread.resolution_elements)} |

---
*Generated by ΛWEAVER v1.0.0 - LUKHAS AGI Narrative Synthesizer*
"""

        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                f.write(markdown)

            logger.info(f"Narrative markdown saved to {output_path}")

        return markdown

    def generate_thread_trace_json(
        self, thread: NarrativeThread = None, output_path: Optional[str] = None
    ) -> dict[str, Any]:
        """Generate thread trace JSON with structural metadata."""

        if thread is None:
            if not self.woven_threads:
                raise ValueError("No threads available for trace generation")
            thread = self.woven_threads[-1]

        # Generate thread trace
        thread_trace = self.log_thread_metadata(thread)

        # Create comprehensive JSON structure
        trace_json = {
            "thread_metadata": {
                "thread_id": thread.thread_id,
                "title": thread.title,
                "narrative_arc": (thread.narrative_arc.value if thread.narrative_arc else None),
                "temporal_span": {
                    "start": thread.temporal_span[0],
                    "end": thread.temporal_span[1],
                    "span_hours": self._calculate_time_gap(thread.temporal_span[0], thread.temporal_span[1]),
                },
                "thread_hash": thread.thread_hash,
                "coherence_score": thread.coherence_score,
                "identity_alignment": thread.identity_alignment,
                "ethical_alignment": thread.ethical_alignment,
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "symbols_analysis": {
                "symbols_used": thread_trace.symbols_used,
                "symbol_count": len(thread_trace.symbols_used),
                "symbol_frequency": dict(Counter(s for f in thread.fragments for s in f.symbols)),
                "unique_symbols_per_fragment": [len(f.symbols) for f in thread.fragments],
            },
            "motifs_analysis": {
                "motifs_detected": thread_trace.motifs_detected,
                "motif_count": len(thread_trace.motifs_detected),
                "motif_details": [
                    {
                        "motif_id": motif.motif_id,
                        "symbol_pattern": motif.symbol_pattern,
                        "occurrence_count": len(motif.occurrences),
                        "evolution_pattern": motif.evolution_pattern,
                        "resonance_score": motif.resonance_score,
                        "first_seen": motif.first_seen,
                        "last_seen": motif.last_seen,
                    }
                    for motif in thread.recurring_motifs
                ],
            },
            "transitions": thread_trace.transitions,
            "phase_deltas": thread_trace.phase_deltas,
            "emotional_arc": [
                {
                    "phase": i,
                    "emotion": emotion,
                    "intensity": intensity,
                    "fragment_index": i if i < len(thread.fragments) else None,
                }
                for i, (emotion, intensity) in enumerate(thread.emotional_arc)
            ],
            "fragments": [
                {
                    "fragment_id": fragment.fragment_id,
                    "source": fragment.source.value,
                    "timestamp": fragment.timestamp,
                    "coherence_score": fragment.coherence_score,
                    "symbols": fragment.symbols,
                    "emotions": fragment.emotions,
                    "glyphs": fragment.glyphs,
                    "content_length": len(fragment.content),
                    "metadata": fragment.metadata,
                }
                for fragment in thread.fragments
            ],
            "validation_results": thread_trace.validation_results,
            "drift_score": thread_trace.drift_score,
            "resonance_rating": thread_trace.resonance_rating,
            "ΛTAG": ["ΛWEAVER_TRACE", "ΛTHREAD_ANALYSIS", "ΛNARRATIVE_METADATA"],
        }

        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(trace_json, f, indent=2, default=str)

            logger.info(f"Thread trace JSON saved to {output_path}")

        return trace_json

    def generate_thread_map(self, thread: NarrativeThread = None, output_path: Optional[str] = None) -> str:
        """Generate ASCII thread map showing symbolic timeline."""

        if thread is None:
            if not self.woven_threads:
                raise ValueError("No threads available for map generation")
            thread = self.woven_threads[-1]

        # Create ASCII thread map
        map_lines = []

        # Header
        map_lines.append("═" * 80)
        map_lines.append(f"🧵 ΛWEAVER THREAD MAP: {thread.title}")
        map_lines.append("═" * 80)
        map_lines.append("")

        # Timeline
        map_lines.append("📅 TEMPORAL TIMELINE")
        map_lines.append("─" * 40)

        for i, fragment in enumerate(thread.fragments):
            timestamp = datetime.fromisoformat(fragment.timestamp.replace("Z", "+00:00"))
            time_str = timestamp.strftime("%m/%d %H:%M")

            # Create visual indicator
            if fragment.source == FragmentType.DREAM:
                icon = "🌙"
            elif fragment.source == FragmentType.MEMORY:
                icon = "🧠"
            elif fragment.source == FragmentType.EMOTION:
                icon = "💫"
            else:
                icon = "⚡"

            coherence_bar = "█" * int(fragment.coherence_score * 10) + "░" * (10 - int(fragment.coherence_score * 10))

            map_lines.append(f"{i + 1:2d}. {icon} {time_str} │{coherence_bar}│ {fragment.coherence_score:.2f}")

        map_lines.append("")

        # Symbol flow
        map_lines.append("🔮 SYMBOLIC FLOW")
        map_lines.append("─" * 40)

        all_symbols = []
        for fragment in thread.fragments:
            all_symbols.extend(fragment.symbols)

        symbol_counts = Counter(all_symbols)
        for symbol, count in symbol_counts.most_common(10):
            frequency_bar = "█" * min(count, 20) + "░" * max(20 - count, 0)
            map_lines.append(f"{symbol:15s} │{frequency_bar}│ {count}")

        map_lines.append("")

        # Emotional arc visualization
        map_lines.append("💭 EMOTIONAL ARC")
        map_lines.append("─" * 40)

        for i, (emotion, intensity) in enumerate(thread.emotional_arc[:10]):  # Limit to first 10
            intensity_bar = "█" * int(intensity * 15) + "░" * (15 - int(intensity * 15))
            map_lines.append(f"{i + 1:2d}. {emotion:12s} │{intensity_bar}│ {intensity:.2f}")

        map_lines.append("")

        # Motif patterns
        if thread.recurring_motifs:
            map_lines.append("🔄 RECURRING MOTIFS")
            map_lines.append("─" * 40)

            for motif in thread.recurring_motifs[:5]:  # Top 5 motifs
                resonance_bar = "█" * int(motif.resonance_score * 10) + "░" * (10 - int(motif.resonance_score * 10))
                pattern_str = " → ".join(motif.symbol_pattern)
                map_lines.append(f"{pattern_str:20s} │{resonance_bar}│ {len(motif.occurrences)}x")

            map_lines.append("")

        # Thread statistics
        map_lines.append("📊 THREAD STATISTICS")
        map_lines.append("─" * 40)
        map_lines.append(f"Coherence Score:     {thread.coherence_score:.3f}")
        map_lines.append(f"Identity Alignment:  {thread.identity_alignment:.3f}")
        map_lines.append(f"Ethical Alignment:   {thread.ethical_alignment:.3f}")
        map_lines.append(f"Fragment Count:      {len(thread.fragments)}")
        map_lines.append(f"Motif Count:         {len(thread.recurring_motifs)}")
        map_lines.append(f"Symbol Diversity:    {len({s for f in thread.fragments for s in f.symbols})}")
        map_lines.append(f"Thread Hash:         {thread.thread_hash}")

        map_lines.append("")
        map_lines.append("═" * 80)

        thread_map = "\n".join(map_lines)

        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                f.write(thread_map)

            logger.info(f"Thread map saved to {output_path}")

        return thread_map

    def get_weaver_status(self) -> dict[str, Any]:
        """Get comprehensive ΛWEAVER system status."""

        return {
            "status": "active",
            "fragments_processed": self.stats["fragments_processed"],
            "threads_woven": self.stats["threads_woven"],
            "motifs_discovered": self.stats["motifs_discovered"],
            "coherent_threads": self.stats["coherent_threads"],
            "identity_aligned_threads": self.stats["identity_aligned_threads"],
            "ethically_aligned_threads": self.stats["ethically_aligned_threads"],
            "current_fragments": len(self.fragments),
            "current_threads": len(self.woven_threads),
            "current_motifs": len(self.identified_motifs),
            "thresholds": {
                "coherence": self.coherence_threshold,
                "identity": self.identity_threshold,
                "ethical": self.ethical_threshold,
            },
            "recent_threads": [
                {
                    "thread_id": thread.thread_id,
                    "title": thread.title,
                    "coherence": thread.coherence_score,
                    "narrative_arc": (thread.narrative_arc.value if thread.narrative_arc else None),
                }
                for thread in self.woven_threads[-5:]
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def main():
    """Main CLI interface for ΛWEAVER symbolic narrative synthesizer."""

    parser = argparse.ArgumentParser(
        description="ΛWEAVER - Symbolic Narrative Synthesizer & Memory Thread Reconstructor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 symbolic_weaver.py --source memory/fragments/ --out results/narrative.md
  python3 symbolic_weaver.py --window 48h --detect-drifts
  python3 symbolic_weaver.py --validate identity,ethics,emotion
  python3 symbolic_weaver.py --generate-all results/
        """,
    )

    parser.add_argument(
        "--source",
        type=str,
        default="memory/fragments/",
        help="Source directory for symbolic fragments",
    )
    parser.add_argument("--out", "--output", type=str, help="Output file path for narrative")
    parser.add_argument("--window", type=str, default="24h", help="Analysis window (e.g., 24h, 48h, 7d)")
    parser.add_argument(
        "--detect-drifts",
        action="store_true",
        help="Reconstruct drifted timeline from analysis window",
    )
    parser.add_argument("--validate", type=str, help="Validate consistency (identity,ethics,emotion)")
    parser.add_argument("--generate-all", type=str, help="Generate all formats to specified directory")
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "map"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--coherence-threshold",
        type=float,
        default=0.6,
        help="Coherence threshold for thread validation",
    )
    parser.add_argument(
        "--identity-threshold",
        type=float,
        default=0.7,
        help="Identity alignment threshold",
    )
    parser.add_argument(
        "--ethical-threshold",
        type=float,
        default=0.8,
        help="Ethical alignment threshold",
    )
    parser.add_argument("--status", action="store_true", help="Show ΛWEAVER system status")

    args = parser.parse_args()

    # Parse time window
    window_hours = 24
    if args.window.endswith("h"):
        window_hours = int(args.window[:-1])
    elif args.window.endswith("d"):
        window_hours = int(args.window[:-1]) * 24

    # Initialize ΛWEAVER
    weaver = SymbolicWeaver(
        coherence_threshold=args.coherence_threshold,
        identity_threshold=args.identity_threshold,
        ethical_threshold=args.ethical_threshold,
    )

    if args.status:
        # Show system status
        status = weaver.get_weaver_status()
        print("🧵 ΛWEAVER - Symbolic Narrative Synthesizer Status")
        print("═" * 60)
        print(f"📊 Fragments processed: {status['fragments_processed']}")
        print(f"🧵 Threads woven: {status['threads_woven']}")
        print(f"🔄 Motifs discovered: {status['motifs_discovered']}")
        print(f"✅ Coherent threads: {status['coherent_threads']}")
        print(f"🎭 Identity aligned: {status['identity_aligned_threads']}")
        print(f"⚖️ Ethically aligned: {status['ethically_aligned_threads']}")

        if status["recent_threads"]:
            print("\n🕐 Recent Threads:")
            for thread in status["recent_threads"]:
                print(f"  • {thread['title']} (coherence: {thread['coherence']:.2f})")

        return 0

    try:
        print("🧵 ΛWEAVER - Symbolic Narrative Synthesizer")
        print(f"📂 Source: {args.source}")
        print(f"⏱️ Window: {window_hours} hours")
        print(
            f"🎯 Thresholds: coherence={args.coherence_threshold}, identity={args.identity_threshold}, ethical={args.ethical_threshold}"
        )
        print()

        # Load fragments
        print("📚 Loading symbolic fragments...")
        fragments = weaver.load_symbolic_fragments(args.source)
        print(f"✅ Loaded {len(fragments)} fragments")

        # Thread fragments into sequences
        print("🧵 Threading memory sequences...")
        thread_sequences = weaver.thread_memory_sequence(fragments)
        print(f"✅ Created {len(thread_sequences)} narrative sequences")

        if not thread_sequences:
            print("⚠️ No coherent sequences found. Try adjusting thresholds or adding more fragments.")
            return 1

        # Synthesize narrative thread (use longest sequence)
        longest_sequence = max(thread_sequences, key=len)
        print(f"🔮 Synthesizing narrative from sequence of {len(longest_sequence)} fragments...")

        thread = weaver.synthesize_narrative_thread(longest_sequence)
        print(f"✅ Synthesized thread: '{thread.title}'")
        print(
            f"   Coherence: {thread.coherence_score:.3f} | Identity: {thread.identity_alignment:.3f} | Ethical: {thread.ethical_alignment:.3f}"
        )

        # Validation if requested
        if args.validate:
            print("🔍 Evaluating thread alignment...")
            validation_types = [v.strip() for v in args.validate.split(",")]

            evaluation = weaver.evaluate_thread_alignment(thread)
            print(f"✅ Validation completed - Status: {evaluation['overall_status']}")

            if "identity" in validation_types:
                print(
                    f"   Identity: {'✅' if evaluation['identity_alignment']['passed'] else '❌'} {evaluation['identity_alignment']['score']:.3f}"
                )
            if "ethics" in validation_types:
                print(
                    f"   Ethics: {'✅' if evaluation['ethical_alignment']['passed'] else '❌'} {evaluation['ethical_alignment']['score']:.3f}"
                )
            if "emotion" in validation_types:
                print(
                    f"   Coherence: {'✅' if evaluation['narrative_coherence']['passed'] else '❌'} {evaluation['narrative_coherence']['score']:.3f}"
                )

        # Generate outputs
        if args.generate_all:
            # Generate all formats to directory
            output_dir = Path(args.generate_all)
            output_dir.mkdir(parents=True, exist_ok=True)

            print("📄 Generating all output formats...")

            # Narrative markdown
            narrative_path = output_dir / f"{thread.thread_id}_narrative.md"
            weaver.generate_narrative_markdown(thread, str(narrative_path))
            print(f"   📝 Narrative: {narrative_path}")

            # Thread trace JSON
            trace_path = output_dir / f"{thread.thread_id}_trace.json"
            weaver.generate_thread_trace_json(thread, str(trace_path))
            print(f"   📊 Trace: {trace_path}")

            # Thread map
            map_path = output_dir / f"{thread.thread_id}_map.txt"
            weaver.generate_thread_map(thread, str(map_path))
            print(f"   🗺️ Map: {map_path}")

        elif args.out:
            # Generate specific format to file
            if args.format == "markdown":
                weaver.generate_narrative_markdown(thread, args.out)
            elif args.format == "json":
                weaver.generate_thread_trace_json(thread, args.out)
            elif args.format == "map":
                weaver.generate_thread_map(thread, args.out)

            print(f"✅ Generated {args.format} output: {args.out}")

        else:
            # Print to console
            if args.format == "markdown":
                print(weaver.generate_narrative_markdown(thread))
            elif args.format == "json":
                print(json.dumps(weaver.generate_thread_trace_json(thread), indent=2))
            elif args.format == "map":
                print(weaver.generate_thread_map(thread))

        # Log metadata
        print("📋 Logging thread metadata...")
        weaver.log_thread_metadata(thread)

        # Final status
        final_status = weaver.get_weaver_status()
        print(f"🎯 Weaving complete: {final_status['threads_woven']} thread(s) created")

        return 0

    except KeyboardInterrupt:
        print("\n👋 ΛWEAVER interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"ΛWEAVER failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/narrative/test_symbolic_weaver.py
║   - Coverage: 85%
║   - Linting: pylint 9.5/10
║
║ MONITORING:
║   - Metrics: Fragments processed, threads woven, coherence scores
║   - Logs: Narrative synthesis, alignment validation, fragment loading
║   - Alerts: Low coherence, identity/ethical misalignment
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Narrative coherence monitoring, identity alignment verification
║   - Safety: Thresholds for coherence, identity, and ethics
║
║ REFERENCES:
║   - Docs: docs/narrative/symbolic_weaver.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=narrative
║   - Wiki: wiki.lukhas.ai/SymbolicWeaver
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS Cognitive system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""
