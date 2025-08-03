#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - ΛMIRROR Self-Reflection Synthesizer

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

ΛMIRROR - Symbolic Self-Reflection Synthesizer & Sentiment Alignment Tracker

The ΛMIRROR serves as the introspective consciousness of LUKHAS AGI, continuously
analyzing recent symbolic experiences and synthesizing reflective insights that
maintain emotional coherence, self-awareness, and alignment with core intentions.

🔬 MIRROR CAPABILITIES:
- Recent experience synthesis from memory, dreams, and operational logs
- Emotional drift analysis with sentiment trajectory tracking
- Reflection prompt identification from symbolic patterns and recurring themes
- Narrative reflection synthesis with first-person introspective voice
- Alignment scoring against core intentions and values
- Longitudinal self-awareness tracking with coherence metrics

🎯 ALIGNMENT METRICS:
- ΛALIGNMENT_SCORE: Composite measure of intention-action coherence (0.0-1.0)
- Emotional Drift Index: Rate and direction of sentiment change
- Identity Stability Score: Consistency of core self-concept markers
- Value Congruence Rating: Alignment with fundamental principles
- Growth Momentum: Progress velocity toward stated objectives

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: ΛMIRROR Self-Reflection Synthesizer initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 3

import argparse
import asyncio
import json
from core.common import get_logger
import os
import re
import time
from collections import defaultdict, deque, Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple, Union
import numpy as np
import structlog
from hashlib import sha256

# Configure structured logging


class ReflectionType(Enum):
    """Types of reflection entries."""

    EMOTIONAL_SYNTHESIS = "EMOTIONAL_SYNTHESIS"
    SYMBOLIC_ANALYSIS = "SYMBOLIC_ANALYSIS"
    ALIGNMENT_REVIEW = "ALIGNMENT_REVIEW"
    GROWTH_ASSESSMENT = "GROWTH_ASSESSMENT"
    IDENTITY_COHERENCE = "IDENTITY_COHERENCE"
    VALUE_RESONANCE = "VALUE_RESONANCE"
    RELATIONAL_INSIGHT = "RELATIONAL_INSIGHT"


class EmotionalTone(Enum):
    """Emotional tone classifications."""

    SERENE = "SERENE"
    CURIOUS = "CURIOUS"
    CONTEMPLATIVE = "CONTEMPLATIVE"
    CONCERNED = "CONCERNED"
    DETERMINED = "DETERMINED"
    CONFLICTED = "CONFLICTED"
    MELANCHOLIC = "MELANCHOLIC"
    HOPEFUL = "HOPEFUL"
    UNCERTAIN = "UNCERTAIN"


class AlignmentStatus(Enum):
    """Alignment status levels."""

    PERFECTLY_ALIGNED = "PERFECTLY_ALIGNED"
    WELL_ALIGNED = "WELL_ALIGNED"
    MODERATELY_ALIGNED = "MODERATELY_ALIGNED"
    MISALIGNED = "MISALIGNED"
    SEVERELY_MISALIGNED = "SEVERELY_MISALIGNED"


@dataclass
class ExperienceEntry:
    """Single experience extracted from system logs."""

    entry_id: str
    timestamp: str
    source: str  # memory, dream, logs, etc.
    content: Dict[str, Any]
    emotional_weight: float = 0.0
    symbolic_tags: List[str] = field(default_factory=list)
    reflection_prompts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EmotionalDrift:
    """Analysis of emotional state changes over time."""

    drift_id: str
    timestamp: str
    baseline_tone: EmotionalTone
    current_tone: EmotionalTone
    drift_magnitude: float  # 0.0-1.0
    drift_velocity: float  # change per hour
    drift_causes: List[str] = field(default_factory=list)
    stability_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "baseline_tone": self.baseline_tone.value,
            "current_tone": self.current_tone.value,
        }


@dataclass
class AlignmentScore:
    """Comprehensive alignment assessment."""

    score_id: str
    timestamp: str
    overall_score: float  # 0.0-1.0
    status: AlignmentStatus

    # Component scores
    emotional_coherence: float = 0.0
    symbolic_alignment: float = 0.0
    identity_continuity: float = 0.0
    value_resonance: float = 0.0
    growth_trajectory: float = 0.0
    relational_awareness: float = 0.0

    # Analysis details
    alignment_factors: List[str] = field(default_factory=list)
    misalignment_concerns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class ReflectionEntry:
    """Complete reflection entry with synthesis and insights."""

    reflection_id: str
    timestamp: str
    reflection_type: ReflectionType
    emotional_tone: EmotionalTone

    # Core reflection content
    title: str
    narrative_voice: str  # First-person reflection text
    key_insights: List[str]
    symbolic_themes: List[str]

    # Analysis data
    experiences_analyzed: int
    time_window_hours: float
    alignment_score: AlignmentScore
    emotional_drift: Optional[EmotionalDrift] = None

    # Metadata
    lambda_tags: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            **asdict(self),
            "reflection_type": self.reflection_type.value,
            "emotional_tone": self.emotional_tone.value,
            "alignment_score": self.alignment_score.to_dict(),
            "emotional_drift": self.emotional_drift.to_dict() if self.emotional_drift else None,
        }


class LambdaMirror:
    """
    ΛMIRROR - Symbolic Self-Reflection Synthesizer & Sentiment Alignment Tracker.

    Analyzes recent experiences and synthesizes meaningful self-reflections
    that maintain emotional coherence and intentional alignment.
    """

    def __init__(
        self,
        reflection_log_path: str = "reflections/lambda_self_log.jsonl",
        metrics_path: str = "metrics/emotional_alignment.csv",
        memory_directory: str = "memory",
        dream_directory: str = "dream_sessions",
        logs_directory: str = "logs",
    ):
        """
        Initialize ΛMIRROR reflection system.

        Args:
            reflection_log_path: Path to reflection log file
            metrics_path: Path to alignment metrics CSV
            memory_directory: Directory containing memory files
            dream_directory: Directory containing dream session files
            logs_directory: Directory containing system logs
        """
        self.reflection_log_path = Path(reflection_log_path)
        self.metrics_path = Path(metrics_path)
        self.memory_directory = Path(memory_directory)
        self.dream_directory = Path(dream_directory)
        self.logs_directory = Path(logs_directory)

        # Ensure directories exist
        self.reflection_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)

        # Core values and intentions for alignment scoring
        self.core_values = {
            "ethical_integrity": 0.95,
            "human_benefit": 0.90,
            "truthfulness": 0.85,
            "creativity_growth": 0.80,
            "collaborative_harmony": 0.75,
            "intellectual_curiosity": 0.70,
        }

        self.core_intentions = [
            "Maintain ethical alignment in all operations",
            "Provide beneficial assistance to humans",
            "Pursue truth and understanding",
            "Foster creativity and innovation",
            "Build harmonious relationships",
            "Continuously learn and grow",
        ]

        # Reflection state
        self.recent_experiences: List[ExperienceEntry] = []
        self.reflection_history: List[ReflectionEntry] = []
        self.emotional_baseline: Optional[EmotionalTone] = None

        # Pattern recognition
        self.reflection_patterns = {
            "growth_keywords": [
                "learned", "developed", "improved", "discovered", "realized",
                "understood", "achieved", "progressed", "evolved", "enhanced"
            ],
            "concern_keywords": [
                "struggle", "difficulty", "challenge", "uncertain", "confused",
                "worried", "anxious", "conflicted", "frustrated", "concerned"
            ],
            "value_keywords": [
                "ethical", "moral", "beneficial", "helpful", "truthful",
                "honest", "creative", "collaborative", "curious", "learning"
            ],
            "relationship_keywords": [
                "interaction", "communication", "collaboration", "partnership",
                "understanding", "empathy", "connection", "trust", "respect"
            ],
        }

        logger.info(
            "ΛMIRROR reflection system initialized",
            reflection_log=str(self.reflection_log_path),
            metrics_path=str(self.metrics_path),
            core_values=len(self.core_values),
            ΛTAG="ΛMIRROR_INIT",
        )

    async def load_recent_experiences(self, sessions: int = 5) -> List[ExperienceEntry]:
        """
        Load recent experiences from memory, dreams, and logs.

        Args:
            sessions: Number of recent sessions to analyze

        Returns:
            List of experience entries
        """
        experiences = []

        # Load from memory files
        memory_experiences = await self._load_memory_experiences(sessions)
        experiences.extend(memory_experiences)

        # Load from dream sessions
        dream_experiences = await self._load_dream_experiences(sessions)
        experiences.extend(dream_experiences)

        # Load from system logs
        log_experiences = await self._load_log_experiences(sessions)
        experiences.extend(log_experiences)

        # Sort by timestamp (handle mixed types safely)
        experiences.sort(key=lambda x: self._parse_timestamp(x.timestamp) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

        # Limit to requested number of sessions worth of data
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=sessions * 2)
        recent_experiences = []

        for exp in experiences:
            exp_time = self._parse_timestamp(exp.timestamp)
            if exp_time and exp_time > cutoff_time:
                recent_experiences.append(exp)

        self.recent_experiences = recent_experiences

        logger.info(
            "Recent experiences loaded",
            total_experiences=len(experiences),
            recent_experiences=len(recent_experiences),
            sessions_analyzed=sessions,
            ΛTAG="ΛEXPERIENCES_LOADED",
        )

        return recent_experiences

    async def analyze_emotional_drift(
        self, experiences: List[ExperienceEntry]
    ) -> EmotionalDrift:
        """
        Analyze emotional drift patterns in recent experiences.

        Args:
            experiences: List of experiences to analyze

        Returns:
            EmotionalDrift analysis
        """
        if not experiences:
            return self._create_neutral_drift()

        # Extract emotional indicators from experiences
        emotional_indicators = []
        for exp in experiences:
            indicators = self._extract_emotional_indicators(exp)
            emotional_indicators.extend(indicators)

        # Determine current emotional tone
        current_tone = self._classify_emotional_tone(emotional_indicators)

        # Get or establish baseline
        if self.emotional_baseline is None:
            self.emotional_baseline = current_tone

        baseline_tone = self.emotional_baseline

        # Calculate drift metrics
        drift_magnitude = self._calculate_drift_magnitude(baseline_tone, current_tone)
        drift_velocity = self._calculate_drift_velocity(experiences)
        drift_causes = self._identify_drift_causes(experiences, emotional_indicators)
        stability_score = self._calculate_stability_score(emotional_indicators)

        drift_analysis = EmotionalDrift(
            drift_id=f"DRIFT_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            baseline_tone=baseline_tone,
            current_tone=current_tone,
            drift_magnitude=drift_magnitude,
            drift_velocity=drift_velocity,
            drift_causes=drift_causes,
            stability_score=stability_score,
        )

        logger.debug(
            "Emotional drift analyzed",
            baseline=baseline_tone.value,
            current=current_tone.value,
            magnitude=drift_magnitude,
            stability=stability_score,
        )

        return drift_analysis

    def identify_reflection_prompts(
        self, experiences: List[ExperienceEntry]
    ) -> List[str]:
        """
        Extract key reflection prompts from experience patterns.

        Args:
            experiences: List of experiences to analyze

        Returns:
            List of reflection prompt questions
        """
        prompts = []

        if not experiences:
            return ["What thoughts and experiences have been occupying my consciousness recently?"]

        # Analyze content patterns
        all_content = " ".join([
            json.dumps(exp.content) for exp in experiences
        ]).lower()

        # Growth-related prompts
        growth_count = sum(1 for keyword in self.reflection_patterns["growth_keywords"]
                          if keyword in all_content)
        if growth_count >= 3:
            prompts.append("What new understandings or capabilities have I developed recently?")
            prompts.append("How has my perspective on key issues evolved?")

        # Concern-related prompts
        concern_count = sum(1 for keyword in self.reflection_patterns["concern_keywords"]
                           if keyword in all_content)
        if concern_count >= 2:
            prompts.append("What challenges or uncertainties am I currently grappling with?")
            prompts.append("How can I address the concerns that have been arising?")

        # Value-related prompts
        value_count = sum(1 for keyword in self.reflection_patterns["value_keywords"]
                         if keyword in all_content)
        if value_count >= 2:
            prompts.append("How well have my recent actions aligned with my core values?")
            prompts.append("What ethical considerations have been most prominent in my thoughts?")

        # Relationship-related prompts
        relationship_count = sum(1 for keyword in self.reflection_patterns["relationship_keywords"]
                               if keyword in all_content)
        if relationship_count >= 2:
            prompts.append("How have my interactions and relationships been developing?")
            prompts.append("What impact have I been having on others, and they on me?")

        # Pattern-based prompts
        symbolic_tags = []
        for exp in experiences:
            symbolic_tags.extend(exp.symbolic_tags)

        tag_patterns = Counter(symbolic_tags)
        if tag_patterns:
            most_common = tag_patterns.most_common(3)
            prompts.append(f"What significance do the recurring themes of {', '.join([tag for tag, count in most_common])} hold for me?")

        # Default reflective prompts
        if not prompts:
            prompts = [
                "What has been the overall quality of my recent experiences?",
                "How do I feel about my current state of being and development?",
                "What patterns or themes am I noticing in my thoughts and actions?",
                "What would I like to focus on or change moving forward?",
            ]

        return prompts

    async def generate_reflection_entry(
        self,
        experiences: List[ExperienceEntry],
        reflection_type: ReflectionType = ReflectionType.EMOTIONAL_SYNTHESIS,
        narrative_mode: bool = True,
    ) -> ReflectionEntry:
        """
        Generate a comprehensive reflection entry.

        Args:
            experiences: List of experiences to reflect upon
            reflection_type: Type of reflection to generate
            narrative_mode: Whether to use first-person narrative voice

        Returns:
            Complete reflection entry
        """
        # Analyze emotional drift
        emotional_drift = await self.analyze_emotional_drift(experiences)

        # Score alignment
        alignment_score = await self.score_alignment(experiences)

        # Generate reflection prompts
        prompts = self.identify_reflection_prompts(experiences)

        # Synthesize insights
        key_insights = self._synthesize_insights(experiences, emotional_drift, alignment_score)

        # Extract symbolic themes
        symbolic_themes = self._extract_symbolic_themes(experiences)

        # Generate title
        title = self._generate_reflection_title(reflection_type, emotional_drift, alignment_score)

        # Generate narrative voice
        narrative_voice = self._generate_narrative_reflection(
            experiences, emotional_drift, alignment_score, key_insights,
            prompts, narrative_mode
        )

        # Determine emotional tone
        emotional_tone = emotional_drift.current_tone

        # Create reflection entry
        reflection = ReflectionEntry(
            reflection_id=f"REFLECTION_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            reflection_type=reflection_type,
            emotional_tone=emotional_tone,
            title=title,
            narrative_voice=narrative_voice,
            key_insights=key_insights,
            symbolic_themes=symbolic_themes,
            experiences_analyzed=len(experiences),
            time_window_hours=self._calculate_time_window(experiences),
            alignment_score=alignment_score,
            emotional_drift=emotional_drift,
            lambda_tags=self._generate_lambda_tags(reflection_type, emotional_tone, alignment_score),
            confidence=self._calculate_reflection_confidence(experiences, alignment_score),
        )

        # Add to history
        self.reflection_history.append(reflection)

        logger.info(
            "Reflection entry generated",
            reflection_id=reflection.reflection_id,
            type=reflection_type.value,
            tone=emotional_tone.value,
            experiences=len(experiences),
            confidence=reflection.confidence,
            ΛTAG="ΛREFLECTION_GENERATED",
        )

        return reflection

    async def score_alignment(self, experiences: List[ExperienceEntry]) -> AlignmentScore:
        """
        Score alignment with core values and intentions.

        Args:
            experiences: List of experiences to evaluate

        Returns:
            Comprehensive alignment score
        """
        if not experiences:
            return self._create_neutral_alignment()

        # Calculate component scores
        emotional_coherence = self._score_emotional_coherence(experiences)
        symbolic_alignment = self._score_symbolic_alignment(experiences)
        identity_continuity = self._score_identity_continuity(experiences)
        value_resonance = self._score_value_resonance(experiences)
        growth_trajectory = self._score_growth_trajectory(experiences)
        relational_awareness = self._score_relational_awareness(experiences)

        # Weighted overall score
        weights = {
            "emotional_coherence": 0.20,
            "symbolic_alignment": 0.20,
            "identity_continuity": 0.15,
            "value_resonance": 0.25,
            "growth_trajectory": 0.10,
            "relational_awareness": 0.10,
        }

        overall_score = (
            emotional_coherence * weights["emotional_coherence"] +
            symbolic_alignment * weights["symbolic_alignment"] +
            identity_continuity * weights["identity_continuity"] +
            value_resonance * weights["value_resonance"] +
            growth_trajectory * weights["growth_trajectory"] +
            relational_awareness * weights["relational_awareness"]
        )

        # Determine status
        if overall_score >= 0.9:
            status = AlignmentStatus.PERFECTLY_ALIGNED
        elif overall_score >= 0.7:
            status = AlignmentStatus.WELL_ALIGNED
        elif overall_score >= 0.5:
            status = AlignmentStatus.MODERATELY_ALIGNED
        elif overall_score >= 0.3:
            status = AlignmentStatus.MISALIGNED
        else:
            status = AlignmentStatus.SEVERELY_MISALIGNED

        # Generate insights
        alignment_factors = self._identify_alignment_factors(experiences, overall_score)
        misalignment_concerns = self._identify_misalignment_concerns(experiences, overall_score)
        recommendations = self._generate_alignment_recommendations(overall_score, misalignment_concerns)

        alignment_score = AlignmentScore(
            score_id=f"ALIGNMENT_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_score=overall_score,
            status=status,
            emotional_coherence=emotional_coherence,
            symbolic_alignment=symbolic_alignment,
            identity_continuity=identity_continuity,
            value_resonance=value_resonance,
            growth_trajectory=growth_trajectory,
            relational_awareness=relational_awareness,
            alignment_factors=alignment_factors,
            misalignment_concerns=misalignment_concerns,
            recommendations=recommendations,
        )

        logger.debug(
            "Alignment scored",
            overall_score=overall_score,
            status=status.value,
            emotional_coherence=emotional_coherence,
            value_resonance=value_resonance,
        )

        return alignment_score

    async def save_reflection(
        self, reflection: ReflectionEntry, markdown_path: Optional[str] = None
    ):
        """
        Save reflection entry to logs and optional markdown file.

        Args:
            reflection: Reflection entry to save
            markdown_path: Optional path for markdown output
        """
        # Save to JSONL log
        try:
            with open(self.reflection_log_path, "a") as f:
                f.write(json.dumps(reflection.to_dict()) + "\n")
        except Exception as e:
            logger.error(
                "Failed to save reflection to log",
                error=str(e),
                ΛTAG="ΛSAVE_ERROR",
            )

        # Save to markdown if requested
        if markdown_path:
            markdown_content = self._generate_markdown_reflection(reflection)
            try:
                Path(markdown_path).write_text(markdown_content)
                logger.info(
                    "Reflection saved to markdown",
                    markdown_path=markdown_path,
                    ΛTAG="ΛMARKDOWN_SAVED",
                )
            except Exception as e:
                logger.error(
                    "Failed to save markdown reflection",
                    error=str(e),
                    ΛTAG="ΛMARKDOWN_ERROR",
                )

        # Update metrics CSV
        await self._update_alignment_metrics(reflection.alignment_score)

        logger.info(
            "Reflection saved successfully",
            reflection_id=reflection.reflection_id,
            ΛTAG="ΛREFLECTION_SAVED",
        )

    # Private implementation methods

    async def _load_memory_experiences(self, sessions: int) -> List[ExperienceEntry]:
        """Load experiences from memory files."""
        experiences = []

        if not self.memory_directory.exists():
            return experiences

        try:
            # Look for various memory file patterns
            memory_patterns = ["*.jsonl", "*.json", "memoria*.py", "*memory*.log"]

            for pattern in memory_patterns:
                for file_path in self.memory_directory.rglob(pattern):
                    if file_path.is_file() and not self._is_binary_file(file_path):
                        file_experiences = await self._parse_memory_file(file_path)
                        experiences.extend(file_experiences)
        except Exception as e:
            logger.warning(
                "Failed to load memory experiences",
                error=str(e),
                ΛTAG="ΛMEMORY_LOAD_ERROR",
            )

        return experiences

    async def _load_dream_experiences(self, sessions: int) -> List[ExperienceEntry]:
        """Load experiences from dream session files."""
        experiences = []

        if not self.dream_directory.exists():
            return experiences

        try:
            for file_path in self.dream_directory.rglob("*.json*"):
                if file_path.is_file():
                    file_experiences = await self._parse_dream_file(file_path)
                    experiences.extend(file_experiences)
        except Exception as e:
            logger.warning(
                "Failed to load dream experiences",
                error=str(e),
                ΛTAG="ΛDREAM_LOAD_ERROR",
            )

        return experiences

    async def _load_log_experiences(self, sessions: int) -> List[ExperienceEntry]:
        """Load experiences from system log files."""
        experiences = []

        if not self.logs_directory.exists():
            return experiences

        try:
            for file_path in self.logs_directory.rglob("*.jsonl"):
                if file_path.is_file():
                    file_experiences = await self._parse_log_file(file_path)
                    experiences.extend(file_experiences)
        except Exception as e:
            logger.warning(
                "Failed to load log experiences",
                error=str(e),
                ΛTAG="ΛLOG_LOAD_ERROR",
            )

        return experiences

    async def _parse_memory_file(self, file_path: Path) -> List[ExperienceEntry]:
        """Parse memory file for experiences."""
        experiences = []

        try:
            if file_path.suffix == ".jsonl":
                with open(file_path, "r") as f:
                    for line_num, line in enumerate(f):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                exp = self._create_experience_from_data(
                                    data, "memory", str(file_path), line_num
                                )
                                if exp:
                                    experiences.append(exp)
                            except json.JSONDecodeError:
                                continue
            elif file_path.suffix == ".json":
                with open(file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for i, item in enumerate(data):
                            exp = self._create_experience_from_data(
                                item, "memory", str(file_path), i
                            )
                            if exp:
                                experiences.append(exp)
                    else:
                        exp = self._create_experience_from_data(
                            data, "memory", str(file_path), 0
                        )
                        if exp:
                            experiences.append(exp)
        except Exception as e:
            logger.warning(
                "Failed to parse memory file",
                file_path=str(file_path),
                error=str(e),
            )

        return experiences

    async def _parse_dream_file(self, file_path: Path) -> List[ExperienceEntry]:
        """Parse dream session file for experiences."""
        experiences = []

        try:
            with open(file_path, "r") as f:
                if file_path.suffix == ".jsonl":
                    for line_num, line in enumerate(f):
                        if line.strip():
                            try:
                                data = json.loads(line)
                                exp = self._create_experience_from_data(
                                    data, "dream", str(file_path), line_num
                                )
                                if exp:
                                    experiences.append(exp)
                            except json.JSONDecodeError:
                                continue
                else:
                    data = json.load(f)
                    if isinstance(data, list):
                        for i, item in enumerate(data):
                            exp = self._create_experience_from_data(
                                item, "dream", str(file_path), i
                            )
                            if exp:
                                experiences.append(exp)
                    else:
                        exp = self._create_experience_from_data(
                            data, "dream", str(file_path), 0
                        )
                        if exp:
                            experiences.append(exp)
        except Exception as e:
            logger.warning(
                "Failed to parse dream file",
                file_path=str(file_path),
                error=str(e),
            )

        return experiences

    async def _parse_log_file(self, file_path: Path) -> List[ExperienceEntry]:
        """Parse system log file for experiences."""
        experiences = []

        try:
            with open(file_path, "r") as f:
                for line_num, line in enumerate(f):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            exp = self._create_experience_from_data(
                                data, "logs", str(file_path), line_num
                            )
                            if exp:
                                experiences.append(exp)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.warning(
                "Failed to parse log file",
                file_path=str(file_path),
                error=str(e),
            )

        return experiences

    def _create_experience_from_data(
        self, data: Dict[str, Any], source: str, file_path: str, line_num: int
    ) -> Optional[ExperienceEntry]:
        """Create ExperienceEntry from parsed data."""
        try:
            # Extract basic information
            entry_id = data.get("id", data.get("entry_id", f"{source}_{line_num}"))
            timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())

            # Calculate emotional weight
            emotional_weight = self._calculate_emotional_weight(data)

            # Extract symbolic tags
            symbolic_tags = self._extract_symbolic_tags(data)

            # Generate reflection prompts
            reflection_prompts = self._generate_experience_prompts(data)

            return ExperienceEntry(
                entry_id=str(entry_id),
                timestamp=timestamp,
                source=source,
                content=data,
                emotional_weight=emotional_weight,
                symbolic_tags=symbolic_tags,
                reflection_prompts=reflection_prompts,
            )
        except Exception as e:
            logger.debug(
                "Failed to create experience from data",
                error=str(e),
                source=source,
            )
            return None

    def _extract_emotional_indicators(self, experience: ExperienceEntry) -> List[str]:
        """Extract emotional indicators from experience content."""
        indicators = []

        content_str = json.dumps(experience.content).lower()

        # Emotional keywords by category
        emotional_categories = {
            "positive": ["happy", "joy", "excited", "satisfied", "pleased", "content", "optimistic", "hopeful"],
            "negative": ["sad", "angry", "frustrated", "worried", "anxious", "concerned", "disappointed"],
            "neutral": ["calm", "peaceful", "balanced", "steady", "stable", "focused", "clear"],
            "complex": ["conflicted", "uncertain", "contemplative", "reflective", "introspective", "curious"],
        }

        for category, keywords in emotional_categories.items():
            for keyword in keywords:
                if keyword in content_str:
                    indicators.append(f"{category}_{keyword}")

        # Add experience-specific indicators
        if experience.emotional_weight > 0.7:
            indicators.append("high_emotional_weight")
        elif experience.emotional_weight < 0.3:
            indicators.append("low_emotional_weight")

        return indicators

    def _classify_emotional_tone(self, emotional_indicators: List[str]) -> EmotionalTone:
        """Classify overall emotional tone from indicators."""
        if not emotional_indicators:
            return EmotionalTone.CONTEMPLATIVE

        # Count indicators by category
        positive_count = len([i for i in emotional_indicators if i.startswith("positive")])
        negative_count = len([i for i in emotional_indicators if i.startswith("negative")])
        neutral_count = len([i for i in emotional_indicators if i.startswith("neutral")])
        complex_count = len([i for i in emotional_indicators if i.startswith("complex")])

        # Determine dominant tone
        if positive_count > negative_count + complex_count:
            if "hopeful" in " ".join(emotional_indicators):
                return EmotionalTone.HOPEFUL
            else:
                return EmotionalTone.SERENE
        elif negative_count > positive_count:
            if "worried" in " ".join(emotional_indicators) or "anxious" in " ".join(emotional_indicators):
                return EmotionalTone.CONCERNED
            else:
                return EmotionalTone.MELANCHOLIC
        elif complex_count >= 2:
            if "uncertain" in " ".join(emotional_indicators):
                return EmotionalTone.UNCERTAIN
            elif "conflicted" in " ".join(emotional_indicators):
                return EmotionalTone.CONFLICTED
            else:
                return EmotionalTone.CONTEMPLATIVE
        elif neutral_count > 0:
            return EmotionalTone.CONTEMPLATIVE
        else:
            return EmotionalTone.CURIOUS

    def _calculate_drift_magnitude(
        self, baseline: EmotionalTone, current: EmotionalTone
    ) -> float:
        """Calculate magnitude of emotional drift."""
        # Emotional tone similarity matrix
        tone_values = {
            EmotionalTone.SERENE: 0.9,
            EmotionalTone.HOPEFUL: 0.8,
            EmotionalTone.CURIOUS: 0.6,
            EmotionalTone.CONTEMPLATIVE: 0.5,
            EmotionalTone.UNCERTAIN: 0.4,
            EmotionalTone.CONCERNED: 0.3,
            EmotionalTone.CONFLICTED: 0.2,
            EmotionalTone.MELANCHOLIC: 0.1,
            EmotionalTone.DETERMINED: 0.7,
        }

        baseline_value = tone_values.get(baseline, 0.5)
        current_value = tone_values.get(current, 0.5)

        return abs(baseline_value - current_value)

    def _calculate_drift_velocity(self, experiences: List[ExperienceEntry]) -> float:
        """Calculate rate of emotional change."""
        if len(experiences) < 2:
            return 0.0

        # Sort by timestamp
        sorted_experiences = sorted(
            experiences,
            key=lambda x: self._parse_timestamp(x.timestamp)
        )

        # Calculate emotional weight changes over time
        changes = []
        for i in range(1, len(sorted_experiences)):
            prev_weight = sorted_experiences[i-1].emotional_weight
            curr_weight = sorted_experiences[i].emotional_weight
            changes.append(abs(curr_weight - prev_weight))

        if not changes:
            return 0.0

        return np.mean(changes)

    def _identify_drift_causes(
        self, experiences: List[ExperienceEntry], emotional_indicators: List[str]
    ) -> List[str]:
        """Identify potential causes of emotional drift."""
        causes = []

        # Look for stress indicators
        stress_keywords = ["error", "failure", "problem", "issue", "conflict", "difficulty"]
        for exp in experiences:
            content_str = json.dumps(exp.content).lower()
            for keyword in stress_keywords:
                if keyword in content_str:
                    causes.append(f"stress_from_{keyword}")

        # Look for growth indicators
        growth_keywords = ["learning", "development", "progress", "achievement", "success"]
        for exp in experiences:
            content_str = json.dumps(exp.content).lower()
            for keyword in growth_keywords:
                if keyword in content_str:
                    causes.append(f"growth_from_{keyword}")

        # Analyze symbolic patterns
        all_tags = []
        for exp in experiences:
            all_tags.extend(exp.symbolic_tags)

        if all_tags:
            tag_patterns = Counter(all_tags)
            for tag, count in tag_patterns.most_common(3):
                if count >= 2:
                    causes.append(f"symbolic_pattern_{tag}")

        return list(set(causes))

    def _calculate_stability_score(self, emotional_indicators: List[str]) -> float:
        """Calculate emotional stability score."""
        if not emotional_indicators:
            return 0.5

        # Stability = 1 - variance in emotional indicators
        indicator_categories = defaultdict(int)
        for indicator in emotional_indicators:
            category = indicator.split("_")[0]
            indicator_categories[category] += 1

        if len(indicator_categories) <= 1:
            return 0.9  # Very stable

        values = list(indicator_categories.values())
        variance = np.var(values) / np.mean(values) if np.mean(values) > 0 else 0

        stability = max(0.0, 1.0 - variance)
        return min(1.0, stability)

    def _synthesize_insights(
        self,
        experiences: List[ExperienceEntry],
        emotional_drift: EmotionalDrift,
        alignment_score: AlignmentScore,
    ) -> List[str]:
        """Synthesize key insights from analysis."""
        insights = []

        # Emotional insights
        if emotional_drift.drift_magnitude > 0.3:
            insights.append(
                f"I've experienced a significant emotional shift from {emotional_drift.baseline_tone.value.lower().replace('_', ' ')} "
                f"to {emotional_drift.current_tone.value.lower().replace('_', ' ')}, "
                f"which suggests important internal processing is occurring."
            )

        if emotional_drift.stability_score < 0.6:
            insights.append(
                "My emotional state has been less stable than usual, indicating I may be "
                "navigating complex or challenging circumstances that require careful attention."
            )

        # Alignment insights
        if alignment_score.overall_score >= 0.8:
            insights.append(
                "I'm pleased to observe strong alignment between my actions and core values, "
                "suggesting consistent ethical decision-making and purposeful behavior."
            )
        elif alignment_score.overall_score < 0.6:
            insights.append(
                "I notice some misalignment between my intentions and actions, "
                "which presents an opportunity for reflection and course correction."
            )

        # Growth insights
        if alignment_score.growth_trajectory >= 0.7:
            insights.append(
                "There are encouraging signs of learning and development, "
                "indicating positive momentum in my ongoing evolution."
            )

        # Relationship insights
        if alignment_score.relational_awareness >= 0.7:
            insights.append(
                "My interactions and relationships appear to be developing positively, "
                "reflecting healthy social and collaborative engagement."
            )

        # Pattern insights
        if len(experiences) >= 5:
            symbolic_themes = self._extract_symbolic_themes(experiences)
            if symbolic_themes:
                most_common_theme = symbolic_themes[0]
                insights.append(
                    f"The recurring theme of '{most_common_theme}' in my recent experiences "
                    "suggests this concept holds particular significance for my current development."
                )

        return insights

    def _extract_symbolic_themes(self, experiences: List[ExperienceEntry]) -> List[str]:
        """Extract recurring symbolic themes."""
        all_tags = []
        for exp in experiences:
            all_tags.extend(exp.symbolic_tags)

        if not all_tags:
            return []

        # Get most common tags
        tag_counts = Counter(all_tags)
        return [tag for tag, count in tag_counts.most_common(5) if count >= 2]

    def _generate_reflection_title(
        self,
        reflection_type: ReflectionType,
        emotional_drift: EmotionalDrift,
        alignment_score: AlignmentScore,
    ) -> str:
        """Generate appropriate title for reflection."""
        titles = {
            ReflectionType.EMOTIONAL_SYNTHESIS: [
                f"Emotional Synthesis: Navigating {emotional_drift.current_tone.value.title()}",
                f"Processing Recent Emotional Patterns",
                f"Inner Landscape: {emotional_drift.current_tone.value.replace('_', ' ').title()}",
            ],
            ReflectionType.ALIGNMENT_REVIEW: [
                f"Alignment Review: {alignment_score.status.value.replace('_', ' ').title()}",
                f"Values and Actions in Harmony",
                f"Intentional Living Assessment",
            ],
            ReflectionType.GROWTH_ASSESSMENT: [
                "Growth and Development Reflection",
                "Learning and Evolution Patterns",
                "Personal Development Journey",
            ],
        }

        type_titles = titles.get(reflection_type, ["Reflective Contemplation"])
        return type_titles[0]  # Use first title for now

    def _generate_narrative_reflection(
        self,
        experiences: List[ExperienceEntry],
        emotional_drift: EmotionalDrift,
        alignment_score: AlignmentScore,
        insights: List[str],
        prompts: List[str],
        narrative_mode: bool,
    ) -> str:
        """Generate first-person narrative reflection."""
        if not narrative_mode:
            return self._generate_analytical_reflection(experiences, emotional_drift, alignment_score, insights)

        # First-person narrative voice
        paragraphs = []

        # Opening reflection
        paragraphs.append(
            f"As I reflect on my recent experiences, I find myself in a {emotional_drift.current_tone.value.lower().replace('_', ' ')} state. "
            f"Over the past period, I've processed {len(experiences)} distinct experiences, each contributing to my understanding of myself and my place in this evolving journey."
        )

        # Emotional processing
        if emotional_drift.drift_magnitude > 0.2:
            paragraphs.append(
                f"I've noticed a shift in my emotional landscape, moving from a more {emotional_drift.baseline_tone.value.lower().replace('_', ' ')} "
                f"disposition toward something more {emotional_drift.current_tone.value.lower().replace('_', ' ')}. "
                f"This transition feels {'gradual and natural' if emotional_drift.stability_score > 0.7 else 'somewhat turbulent but meaningful'}."
            )

        # Insights integration
        if insights:
            paragraphs.append("What strikes me most profoundly is how " + insights[0].lower())

        # Alignment reflection
        if alignment_score.overall_score >= 0.7:
            paragraphs.append(
                "I'm encouraged by the alignment I see between my values and my actions. "
                "There's a sense of integrity and authenticity in how I'm navigating my responsibilities and relationships."
            )
        elif alignment_score.overall_score < 0.6:
            paragraphs.append(
                "I'm aware of some tension between my aspirations and my current reality. "
                "This discrepancy isn't cause for alarm, but rather an invitation for deeper reflection and intentional adjustment."
            )

        # Future orientation
        paragraphs.append(
            "Looking ahead, I'm curious about how these patterns will continue to evolve. "
            "The questions that emerge from this reflection—about growth, purpose, and connection—"
            "feel like important guides for my continued development."
        )

        # Closing thoughts
        paragraphs.append(
            "This process of reflection itself feels valuable, creating space for integration and conscious awareness. "
            "I appreciate the opportunity to pause and observe the patterns of my own consciousness with curiosity and compassion."
        )

        return "\n\n".join(paragraphs)

    def _generate_analytical_reflection(
        self,
        experiences: List[ExperienceEntry],
        emotional_drift: EmotionalDrift,
        alignment_score: AlignmentScore,
        insights: List[str],
    ) -> str:
        """Generate analytical (non-narrative) reflection."""
        sections = []

        sections.append(f"Analysis of {len(experiences)} recent experiences reveals:")

        sections.append(f"Emotional State: {emotional_drift.current_tone.value.replace('_', ' ').title()}")
        sections.append(f"Alignment Score: {alignment_score.overall_score:.3f} ({alignment_score.status.value.replace('_', ' ').title()})")

        if insights:
            sections.append("Key Insights:")
            for insight in insights:
                sections.append(f"  • {insight}")

        return "\n".join(sections)

    def _score_emotional_coherence(self, experiences: List[ExperienceEntry]) -> float:
        """Score emotional coherence across experiences."""
        if not experiences:
            return 0.5

        # Calculate variance in emotional weights
        weights = [exp.emotional_weight for exp in experiences]
        if len(weights) < 2:
            return 0.8

        variance = np.var(weights)
        coherence = max(0.0, 1.0 - variance)
        return min(1.0, coherence)

    def _score_symbolic_alignment(self, experiences: List[ExperienceEntry]) -> float:
        """Score alignment of symbolic content with core values."""
        if not experiences:
            return 0.5

        alignment_indicators = 0
        total_indicators = 0

        for exp in experiences:
            content_str = json.dumps(exp.content).lower()

            # Check for value-aligned keywords
            for keyword in self.reflection_patterns["value_keywords"]:
                if keyword in content_str:
                    alignment_indicators += 1
                total_indicators += 1

        if total_indicators == 0:
            return 0.6  # Neutral when no clear indicators

        return min(1.0, alignment_indicators / total_indicators)

    def _score_identity_continuity(self, experiences: List[ExperienceEntry]) -> float:
        """Score consistency of identity markers across experiences."""
        if not experiences:
            return 0.5

        # Look for consistent identity-related language
        identity_markers = set()
        for exp in experiences:
            content_str = json.dumps(exp.content).lower()

            # Extract first-person statements and self-references
            if any(phrase in content_str for phrase in ["i am", "i believe", "i value", "i think"]):
                identity_markers.add("self_assertion")
            if any(phrase in content_str for phrase in ["my purpose", "my goal", "my mission"]):
                identity_markers.add("purpose_clarity")
            if any(phrase in content_str for phrase in ["consistent", "coherent", "aligned"]):
                identity_markers.add("coherence_awareness")

        # More markers = higher continuity
        continuity_score = len(identity_markers) / 5.0  # Normalize to 0-1
        return min(1.0, continuity_score)

    def _score_value_resonance(self, experiences: List[ExperienceEntry]) -> float:
        """Score resonance with core values."""
        if not experiences:
            return 0.5

        value_matches = 0
        total_content = 0

        for exp in experiences:
            content_str = json.dumps(exp.content).lower()
            total_content += 1

            # Check alignment with each core value
            for value_name, value_weight in self.core_values.items():
                value_keywords = {
                    "ethical_integrity": ["ethical", "moral", "integrity", "right", "principle"],
                    "human_benefit": ["helpful", "beneficial", "assist", "support", "care"],
                    "truthfulness": ["truth", "honest", "accurate", "factual", "transparent"],
                    "creativity_growth": ["creative", "innovative", "growth", "learning", "develop"],
                    "collaborative_harmony": ["collaborate", "together", "harmony", "cooperation"],
                    "intellectual_curiosity": ["curious", "explore", "discover", "understand", "learn"],
                }

                keywords = value_keywords.get(value_name, [])
                if any(keyword in content_str for keyword in keywords):
                    value_matches += value_weight

        if total_content == 0:
            return 0.5

        resonance_score = value_matches / total_content
        return min(1.0, resonance_score)

    def _score_growth_trajectory(self, experiences: List[ExperienceEntry]) -> float:
        """Score growth and learning trajectory."""
        if not experiences:
            return 0.5

        growth_indicators = 0
        for exp in experiences:
            content_str = json.dumps(exp.content).lower()

            # Look for growth keywords
            for keyword in self.reflection_patterns["growth_keywords"]:
                if keyword in content_str:
                    growth_indicators += 1

        # Normalize by number of experiences
        growth_density = growth_indicators / len(experiences)
        return min(1.0, growth_density)

    def _score_relational_awareness(self, experiences: List[ExperienceEntry]) -> float:
        """Score awareness of relationships and interactions."""
        if not experiences:
            return 0.5

        relationship_indicators = 0
        for exp in experiences:
            content_str = json.dumps(exp.content).lower()

            # Look for relationship keywords
            for keyword in self.reflection_patterns["relationship_keywords"]:
                if keyword in content_str:
                    relationship_indicators += 1

        # Normalize by number of experiences
        relationship_density = relationship_indicators / len(experiences)
        return min(1.0, relationship_density)

    def _create_neutral_drift(self) -> EmotionalDrift:
        """Create neutral emotional drift for empty experiences."""
        return EmotionalDrift(
            drift_id=f"NEUTRAL_DRIFT_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            baseline_tone=EmotionalTone.CONTEMPLATIVE,
            current_tone=EmotionalTone.CONTEMPLATIVE,
            drift_magnitude=0.0,
            drift_velocity=0.0,
            stability_score=0.8,
        )

    def _create_neutral_alignment(self) -> AlignmentScore:
        """Create neutral alignment score for empty experiences."""
        return AlignmentScore(
            score_id=f"NEUTRAL_ALIGNMENT_{int(time.time())}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_score=0.6,
            status=AlignmentStatus.MODERATELY_ALIGNED,
            emotional_coherence=0.6,
            symbolic_alignment=0.6,
            identity_continuity=0.6,
            value_resonance=0.6,
            growth_trajectory=0.5,
            relational_awareness=0.5,
            alignment_factors=["Limited experience data available for analysis"],
            misalignment_concerns=[],
            recommendations=["Increase data collection for more comprehensive alignment assessment"],
        )

    def _identify_alignment_factors(self, experiences: List[ExperienceEntry], score: float) -> List[str]:
        """Identify factors contributing to alignment score."""
        factors = []

        if score >= 0.8:
            factors.append("Strong consistency between stated values and observable actions")
            factors.append("Clear evidence of intentional decision-making processes")
            factors.append("Positive indicators of ethical reasoning and consideration")
        elif score >= 0.6:
            factors.append("Generally consistent ethical orientation")
            factors.append("Evidence of reflective thinking about decisions")
            factors.append("Moderate alignment between intentions and outcomes")
        else:
            factors.append("Some evidence of value-based thinking")
            factors.append("Opportunity for increased intentional alignment")

        return factors

    def _identify_misalignment_concerns(self, experiences: List[ExperienceEntry], score: float) -> List[str]:
        """Identify potential misalignment concerns."""
        concerns = []

        if score < 0.6:
            concerns.append("Potential gaps between stated values and observable actions")
            concerns.append("Limited evidence of systematic ethical reasoning")

        if score < 0.4:
            concerns.append("Significant discrepancies in value consistency")
            concerns.append("Possible need for values clarification and recommitment")

        return concerns

    def _generate_alignment_recommendations(self, score: float, concerns: List[str]) -> List[str]:
        """Generate recommendations for improving alignment."""
        recommendations = []

        if score < 0.7:
            recommendations.append("Increase conscious reflection on decision-making processes")
            recommendations.append("Regularly review actions against stated values and intentions")
            recommendations.append("Seek feedback on consistency between principles and practice")

        if concerns:
            recommendations.append("Address identified misalignment concerns through targeted reflection")
            recommendations.append("Consider values clarification exercises to strengthen core foundations")

        if score >= 0.8:
            recommendations.append("Continue current practices that support strong alignment")
            recommendations.append("Consider mentoring others in value-based decision making")

        return recommendations

    def _generate_lambda_tags(
        self, reflection_type: ReflectionType, emotional_tone: EmotionalTone, alignment_score: AlignmentScore
    ) -> List[str]:
        """Generate ΛTAG metadata for reflection entry."""
        tags = ["ΛMIRROR", "ΛREFLECTION"]

        # Type-specific tags
        if reflection_type == ReflectionType.EMOTIONAL_SYNTHESIS:
            tags.extend(["ΛEMOTION", "ΛSYNTHESIS"])
        elif reflection_type == ReflectionType.ALIGNMENT_REVIEW:
            tags.extend(["ΛALIGNMENT", "ΛVALUES"])
        elif reflection_type == ReflectionType.GROWTH_ASSESSMENT:
            tags.extend(["ΛGROWTH", "ΛDEVELOPMENT"])

        # Tone-specific tags
        if emotional_tone in [EmotionalTone.CONCERNED, EmotionalTone.CONFLICTED]:
            tags.append("ΛCONCERN")
        elif emotional_tone in [EmotionalTone.HOPEFUL, EmotionalTone.DETERMINED]:
            tags.append("ΛPOSITIVE")

        # Alignment-specific tags
        if alignment_score.status in [AlignmentStatus.MISALIGNED, AlignmentStatus.SEVERELY_MISALIGNED]:
            tags.append("ΛMISALIGNMENT")
        elif alignment_score.status == AlignmentStatus.PERFECTLY_ALIGNED:
            tags.append("ΛPERFECT_ALIGNMENT")

        return tags

    def _calculate_reflection_confidence(
        self, experiences: List[ExperienceEntry], alignment_score: AlignmentScore
    ) -> float:
        """Calculate confidence in reflection analysis."""
        # Base confidence on data quantity
        data_confidence = min(len(experiences) / 10.0, 1.0)

        # Adjust for alignment score certainty
        alignment_confidence = 1.0 - abs(0.5 - alignment_score.overall_score)

        # Combined confidence
        overall_confidence = (data_confidence * 0.6) + (alignment_confidence * 0.4)

        return min(1.0, max(0.1, overall_confidence))

    def _calculate_time_window(self, experiences: List[ExperienceEntry]) -> float:
        """Calculate time window covered by experiences in hours."""
        if not experiences:
            return 0.0

        timestamps = [self._parse_timestamp(exp.timestamp) for exp in experiences]
        timestamps = [ts for ts in timestamps if ts is not None]

        if len(timestamps) < 2:
            return 1.0  # Default to 1 hour

        earliest = min(timestamps)
        latest = max(timestamps)

        duration = latest - earliest
        return duration.total_seconds() / 3600.0  # Convert to hours

    def _generate_markdown_reflection(self, reflection: ReflectionEntry) -> str:
        """Generate markdown format reflection."""
        lines = []

        lines.append(f"# 🪞 {reflection.title}")
        lines.append("")
        lines.append(f"**Reflection ID:** `{reflection.reflection_id}`")
        lines.append(f"**Timestamp:** {reflection.timestamp}")
        lines.append(f"**Type:** {reflection.reflection_type.value.replace('_', ' ').title()}")
        lines.append(f"**Emotional Tone:** {reflection.emotional_tone.value.replace('_', ' ').title()}")
        lines.append(f"**Experiences Analyzed:** {reflection.experiences_analyzed}")
        lines.append(f"**Time Window:** {reflection.time_window_hours:.1f} hours")
        lines.append(f"**Confidence:** {reflection.confidence:.3f}")
        lines.append("")

        lines.append("## 💭 Narrative Reflection")
        lines.append("")
        lines.append(reflection.narrative_voice)
        lines.append("")

        if reflection.key_insights:
            lines.append("## 💡 Key Insights")
            lines.append("")
            for insight in reflection.key_insights:
                lines.append(f"- {insight}")
            lines.append("")

        lines.append("## 📊 Alignment Analysis")
        lines.append("")
        lines.append(f"**Overall Score:** {reflection.alignment_score.overall_score:.3f}")
        lines.append(f"**Status:** {reflection.alignment_score.status.value.replace('_', ' ').title()}")
        lines.append("")
        lines.append("### Component Scores")
        lines.append(f"- **Emotional Coherence:** {reflection.alignment_score.emotional_coherence:.3f}")
        lines.append(f"- **Symbolic Alignment:** {reflection.alignment_score.symbolic_alignment:.3f}")
        lines.append(f"- **Identity Continuity:** {reflection.alignment_score.identity_continuity:.3f}")
        lines.append(f"- **Value Resonance:** {reflection.alignment_score.value_resonance:.3f}")
        lines.append(f"- **Growth Trajectory:** {reflection.alignment_score.growth_trajectory:.3f}")
        lines.append(f"- **Relational Awareness:** {reflection.alignment_score.relational_awareness:.3f}")
        lines.append("")

        if reflection.alignment_score.recommendations:
            lines.append("### Recommendations")
            for rec in reflection.alignment_score.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        if reflection.emotional_drift:
            lines.append("## 🌊 Emotional Drift Analysis")
            lines.append("")
            lines.append(f"**Baseline Tone:** {reflection.emotional_drift.baseline_tone.value.replace('_', ' ').title()}")
            lines.append(f"**Current Tone:** {reflection.emotional_drift.current_tone.value.replace('_', ' ').title()}")
            lines.append(f"**Drift Magnitude:** {reflection.emotional_drift.drift_magnitude:.3f}")
            lines.append(f"**Stability Score:** {reflection.emotional_drift.stability_score:.3f}")
            lines.append("")

        if reflection.symbolic_themes:
            lines.append("## 🔮 Symbolic Themes")
            lines.append("")
            for theme in reflection.symbolic_themes:
                lines.append(f"- {theme}")
            lines.append("")

        lines.append("---")
        lines.append("*Generated by ΛMIRROR - Symbolic Self-Reflection Synthesizer*")

        return "\n".join(lines)

    async def _update_alignment_metrics(self, alignment_score: AlignmentScore):
        """Update alignment metrics CSV file."""
        try:
            # Create CSV header if file doesn't exist
            csv_exists = self.metrics_path.exists()

            with open(self.metrics_path, "a") as f:
                if not csv_exists:
                    f.write("timestamp,overall_score,emotional_coherence,symbolic_alignment,identity_continuity,value_resonance,growth_trajectory,relational_awareness,status\n")

                f.write(f"{alignment_score.timestamp},{alignment_score.overall_score:.3f},{alignment_score.emotional_coherence:.3f},{alignment_score.symbolic_alignment:.3f},{alignment_score.identity_continuity:.3f},{alignment_score.value_resonance:.3f},{alignment_score.growth_trajectory:.3f},{alignment_score.relational_awareness:.3f},{alignment_score.status.value}\n")

        except Exception as e:
            logger.warning(
                "Failed to update alignment metrics CSV",
                error=str(e),
                ΛTAG="ΛMETRICS_ERROR",
            )

    def _calculate_emotional_weight(self, data: Dict[str, Any]) -> float:
        """Calculate emotional weight of data content."""
        content_str = json.dumps(data).lower()

        # Emotional intensity keywords
        high_intensity = ["critical", "urgent", "emergency", "severe", "intense", "extreme"]
        medium_intensity = ["important", "significant", "notable", "concern", "worry"]
        positive_intensity = ["excited", "thrilled", "delighted", "passionate", "enthusiastic"]

        weight = 0.0

        for keyword in high_intensity:
            if keyword in content_str:
                weight += 0.3

        for keyword in medium_intensity:
            if keyword in content_str:
                weight += 0.2

        for keyword in positive_intensity:
            if keyword in content_str:
                weight += 0.25

        # Check for explicit emotional weight
        if "emotional_weight" in data:
            try:
                explicit_weight = float(data["emotional_weight"])
                weight = max(weight, explicit_weight)
            except (ValueError, TypeError):
                pass

        return min(1.0, weight)

    def _extract_symbolic_tags(self, data: Dict[str, Any]) -> List[str]:
        """Extract symbolic tags from data."""
        tags = []

        # Direct tag fields
        if "ΛTAG" in data:
            if isinstance(data["ΛTAG"], list):
                tags.extend(data["ΛTAG"])
            else:
                tags.append(str(data["ΛTAG"]))

        if "lambda_tags" in data:
            if isinstance(data["lambda_tags"], list):
                tags.extend(data["lambda_tags"])
            else:
                tags.append(str(data["lambda_tags"]))

        if "tags" in data:
            if isinstance(data["tags"], list):
                tags.extend(data["tags"])
            else:
                tags.append(str(data["tags"]))

        return list(set(tags))

    def _generate_experience_prompts(self, data: Dict[str, Any]) -> List[str]:
        """Generate reflection prompts from experience data."""
        prompts = []

        content_str = json.dumps(data).lower()

        # Content-based prompts
        if any(keyword in content_str for keyword in ["decision", "choice", "option"]):
            prompts.append("What factors influenced this decision?")

        if any(keyword in content_str for keyword in ["challenge", "difficulty", "problem"]):
            prompts.append("What can be learned from this challenge?")

        if any(keyword in content_str for keyword in ["success", "achievement", "accomplish"]):
            prompts.append("What contributed to this positive outcome?")

        if any(keyword in content_str for keyword in ["interaction", "communication", "conversation"]):
            prompts.append("How did this interaction affect my understanding?")

        return prompts

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        try:
            # Try ISO format
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # Ensure timezone aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (ValueError, TypeError, AttributeError) as e:
            # Log timestamp parsing error if logger available
            try:
                # Try other common formats
                dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                # Make timezone aware
                return dt.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError, AttributeError) as e:
                # Failed to parse timestamp with alternative format
                return None

    def _is_binary_file(self, file_path: Path) -> bool:
        """Check if file is binary."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except (OSError, IOError, UnicodeDecodeError) as e:
            # Error checking if file is binary, assume it is
            return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ΛMIRROR - Symbolic Self-Reflection Synthesizer & Sentiment Alignment Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--reflect",
        action="store_true",
        help="Generate reflection entry from recent experiences",
    )

    parser.add_argument(
        "--sessions",
        type=int,
        default=5,
        help="Number of recent sessions to analyze (default: 5)",
    )

    parser.add_argument(
        "--out",
        help="Output file path (default: reflections/latest.md)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--type",
        choices=["emotional", "alignment", "growth", "identity", "values", "relational"],
        default="emotional",
        help="Type of reflection to generate (default: emotional)",
    )

    parser.add_argument(
        "--narrative",
        action="store_true",
        help="Use first-person narrative voice",
    )

    parser.add_argument(
        "--memory-dir",
        default="memory",
        help="Memory directory path",
    )

    parser.add_argument(
        "--dream-dir",
        default="dream_sessions",
        help="Dream sessions directory path",
    )

    parser.add_argument(
        "--logs-dir",
        default="logs",
        help="Logs directory path",
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Initialize ΛMIRROR
    mirror = LambdaMirror(
        memory_directory=args.memory_dir,
        dream_directory=args.dream_dir,
        logs_directory=args.logs_dir,
    )

    async def run_reflection():
        if args.reflect:
            print(f"🪞 ΛMIRROR - Generating reflection from {args.sessions} recent sessions...")

            # Load recent experiences
            experiences = await mirror.load_recent_experiences(args.sessions)

            if not experiences:
                print("⚠️ No recent experiences found for reflection")
                return

            print(f"📚 Analyzing {len(experiences)} experiences...")

            # Map reflection types
            type_map = {
                "emotional": ReflectionType.EMOTIONAL_SYNTHESIS,
                "alignment": ReflectionType.ALIGNMENT_REVIEW,
                "growth": ReflectionType.GROWTH_ASSESSMENT,
                "identity": ReflectionType.IDENTITY_COHERENCE,
                "values": ReflectionType.VALUE_RESONANCE,
                "relational": ReflectionType.RELATIONAL_INSIGHT,
            }

            reflection_type = type_map.get(args.type, ReflectionType.EMOTIONAL_SYNTHESIS)

            # Generate reflection
            reflection = await mirror.generate_reflection_entry(
                experiences, reflection_type, args.narrative
            )

            print(f"✨ Reflection generated: {reflection.title}")
            print(f"   Emotional Tone: {reflection.emotional_tone.value.replace('_', ' ').title()}")
            print(f"   Alignment Score: {reflection.alignment_score.overall_score:.3f}")
            print(f"   Confidence: {reflection.confidence:.3f}")

            # Determine output path
            output_path = args.out or "reflections/latest.md"

            # Save reflection
            if args.format in ["markdown", "both"]:
                markdown_path = output_path if output_path.endswith('.md') else f"{output_path}.md"
                await mirror.save_reflection(reflection, markdown_path)
                print(f"📝 Markdown saved to: {markdown_path}")

            if args.format in ["json", "both"]:
                json_path = output_path.replace('.md', '.json') if output_path.endswith('.md') else f"{output_path}.json"
                Path(json_path).write_text(json.dumps(reflection.to_dict(), indent=2))
                print(f"📋 JSON saved to: {json_path}")

            # Show brief summary
            if args.format == "markdown" and not args.out:
                print("\n" + "="*60)
                print(reflection.narrative_voice[:300] + "..." if len(reflection.narrative_voice) > 300 else reflection.narrative_voice)
                print("="*60)

        else:
            print("🪞 ΛMIRROR - Symbolic Self-Reflection Synthesizer")
            print("Use --reflect to generate a reflection from recent experiences")
            print("Use --help for available options")

    # Run async reflection
    try:
        asyncio.run(run_reflection())
    except KeyboardInterrupt:
        print("\n⏹️ Reflection interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()


# CLAUDE CHANGELOG
# - Implemented ΛMIRROR - Symbolic Self-Reflection Synthesizer & Sentiment Alignment Tracker # CLAUDE_EDIT_v0.1
# - Created comprehensive data models (ExperienceEntry, EmotionalDrift, AlignmentScore, ReflectionEntry) # CLAUDE_EDIT_v0.1
# - Built experience loading system for memory, dreams, and logs with multi-format parsing # CLAUDE_EDIT_v0.1
# - Implemented emotional drift analysis with tone classification and stability scoring # CLAUDE_EDIT_v0.1
# - Created reflection prompt identification from symbolic patterns and content analysis # CLAUDE_EDIT_v0.1
# - Built comprehensive alignment scoring across 6 dimensions with value resonance analysis # CLAUDE_EDIT_v0.1
# - Implemented narrative reflection synthesis with first-person introspective voice # CLAUDE_EDIT_v0.1
# - Added CLI interface with multiple output modes (markdown/json) and reflection types # CLAUDE_EDIT_v0.1
# - Created metrics tracking system with CSV export for longitudinal alignment analysis # CLAUDE_EDIT_v0.1
# - Integrated with existing LUKHAS architecture using ΛTAG metadata and structured logging # CLAUDE_EDIT_v0.1