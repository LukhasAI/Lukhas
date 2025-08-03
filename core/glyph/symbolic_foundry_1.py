#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony


LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - ΛFOUNDRY Symbolic Mutation Engine

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

ΛFOUNDRY - Symbolic Mutation Engine & Entropy-Driven Glyph Synthesizer

Evolves and synthesizes new GLYPHs based on symbolic entropy patterns,
emotional deltas, and system need-states. Generates adaptive cognitive
expansions through targeted symbolic creativity with comprehensive safety
validation.

Key Features:
• Entropy Pressure Analysis - Zone detection across symbolic spaces
• 6 Mutation Algorithms - Semantic blend, emotional shift, entropy driven, etc.
• Viability Scoring - Coherence, novelty, emotional harmony, safety
• GLYPH Registry - Version tracking with complete provenance chains
• Safety Classification - SAFE, CAUTION, REVIEW, RESTRICTED levels

Mutation Methods:
• semantic_blend - Semantic transformation patterns
• emotional_shift - Emotional resonance modifications
• entropy_driven - Entropy pressure evolution
• contextual_merge - Context-aware integration
• creative_synthesis - Creative element synthesis
• repair_focused - Repair and optimization focus

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: ΛFOUNDRY Symbolic Mutation Engine initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 3

import os
import re
import json
import hashlib
import argparse
import logging
import random
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any, Optional, NamedTuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import structlog

# Initialize logger for ΛTRACE using structlog
logger = structlog.get_logger("ΛTRACE.glyphs.lambda_foundry")


@dataclass
class EntropyZone:
    """Represents a symbolic zone with elevated entropy requiring evolution."""

    zone_id: str
    location: str  # File path or symbolic space
    entropy_level: float
    pressure_indicators: List[str]
    affected_glyphs: List[str]
    emotional_context: Dict[str, float]
    urgency_score: float
    suggested_mutations: List[str]


@dataclass
class GlyphCandidate:
    """Represents a candidate GLYPH generated through mutation."""

    candidate_id: str
    source_glyphs: List[str]
    mutated_symbol: str
    semantic_context: str
    emotional_profile: Dict[str, float]
    coherence_score: float
    novelty_score: float
    safety_classification: str
    origin_hash: str
    mutation_method: str
    entropy_lineage: str


@dataclass
class GlyphRecord:
    """Registry record for validated GLYPHs."""

    glyph_id: str
    symbol: str
    semantic_meaning: str
    emotional_resonance: Dict[str, float]
    creation_timestamp: str
    source_entropy_zone: str
    viability_score: float
    safety_rating: str
    version: str
    provenance_chain: List[str]
    usage_contexts: List[str]
    stability_metrics: Dict[str, float]


class ΛFoundry:
    """
    ΛFOUNDRY - Symbolic Mutation Engine & Entropy-Driven Glyph Synthesizer

    Evolves adaptive GLYPHs through entropy pressure analysis, semantic mutation,
    and comprehensive viability validation with ethical safety measures.
    """

    def __init__(self,
                 source_directories: List[str] = None,
                 output_directory: str = "results/glyph_mutations",
                 log_directory: str = "logs/foundry"):
        """Initialize ΛFOUNDRY with source scanning and output configurations."""

        self.source_directories = source_directories or [
            "memory", "dream", "ethics", "reasoning",
            "consciousness", "emotion", "symbolism"
        ]

        self.output_directory = Path(output_directory)
        self.log_directory = Path(log_directory)
        self.registry_file = self.output_directory / "glyph_registry.json"

        # Create necessary directories
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # GLYPH pattern detection
        self.glyph_patterns = [
            r"Λ[A-Z][A-Z0-9_]*",      # Standard ΛTAG format
            r"ΛT[A-Z][A-Z0-9_]*",     # ΛT prefix variants
            r"GLYPH[A-Z0-9_]*",       # GLYPH references
            r"Λ[a-z][a-z0-9_]*"       # Lowercase lambda symbols
        ]

        # Entropy pressure thresholds
        self.entropy_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }

        # Mutation algorithms
        self.mutation_methods = [
            'semantic_blend',
            'emotional_shift',
            'entropy_driven',
            'contextual_merge',
            'creative_synthesis',
            'repair_focused'
        ]

        # Safety classification levels
        self.safety_levels = ['SAFE', 'CAUTION', 'REVIEW', 'RESTRICTED']

        # Emotional resonance patterns
        self.emotional_patterns = {
            'harmony': ['CALM', 'BALANCED', 'STABLE', 'FLOW'],
            'tension': ['ANXIETY', 'STRESS', 'CONFLICT', 'PRESSURE'],
            'creativity': ['INSIGHT', 'DISCOVERY', 'INNOVATION', 'BREAKTHROUGH'],
            'protection': ['GUARD', 'SHIELD', 'SECURE', 'FORTRESS'],
            'growth': ['EVOLVE', 'EXPAND', 'DEVELOP', 'FLOURISH']
        }

        # Initialize registries
        self.entropy_zones: List[EntropyZone] = []
        self.glyph_candidates: List[GlyphCandidate] = []
        self.glyph_registry: Dict[str, GlyphRecord] = {}
        self.foundry_events: List[Dict[str, Any]] = []

        # Load existing registry if available
        self._load_glyph_registry()

        logger.info("ΛFOUNDRY initialized",
                   source_directories=self.source_directories,
                   output_dir=str(self.output_directory))

    def analyze_entropy_pressure(self,
                                entropy_threshold: str = "medium",
                                focus_directories: List[str] = None) -> List[EntropyZone]:
        """
        Detect symbolic zones with elevated entropy demanding evolution.

        Args:
            entropy_threshold: Pressure level ('low', 'medium', 'high', 'critical')
            focus_directories: Specific directories to analyze (optional)

        Returns:
            List of EntropyZone objects with pressure analysis
        """
        logger.info("Starting entropy pressure analysis",
                   threshold=entropy_threshold)

        target_dirs = focus_directories or self.source_directories
        threshold_value = self.entropy_thresholds.get(entropy_threshold, 0.6)

        detected_zones = []

        for directory in target_dirs:
            if not os.path.exists(directory):
                logger.warning("Directory not found", directory=directory)
                continue

            dir_zones = self._analyze_directory_entropy(directory, threshold_value)
            detected_zones.extend(dir_zones)

            logger.info("Directory analysis complete",
                       directory=directory,
                       zones_found=len(dir_zones))

        self.entropy_zones = detected_zones

        # Log entropy analysis event
        self._log_foundry_event("entropy_analysis", {
            "threshold": entropy_threshold,
            "zones_detected": len(detected_zones),
            "high_pressure_zones": len([z for z in detected_zones if z.entropy_level > 0.8]),
            "directories_scanned": len(target_dirs)
        })

        logger.info("Entropy pressure analysis complete",
                   total_zones=len(detected_zones),
                   high_pressure=len([z for z in detected_zones if z.entropy_level > 0.8]))

        return detected_zones

    def _analyze_directory_entropy(self, directory: str, threshold: float) -> List[EntropyZone]:
        """Analyze entropy pressure within a single directory."""
        zones = []

        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.md', '.json', '.txt')):
                    file_path = os.path.join(root, file)

                    try:
                        zone = self._analyze_file_entropy(file_path, threshold)
                        if zone and zone.entropy_level >= threshold:
                            zones.append(zone)
                    except Exception as e:
                        logger.warning("Failed to analyze file entropy",
                                     file_path=file_path, error=str(e))

        return zones

    def _analyze_file_entropy(self, file_path: str, threshold: float) -> Optional[EntropyZone]:
        """Analyze entropy pressure within a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return None

        # Extract existing GLYPHs
        affected_glyphs = []
        for pattern in self.glyph_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            affected_glyphs.extend([m.upper() for m in matches])

        if not affected_glyphs:
            return None

        # Calculate entropy indicators
        entropy_indicators = self._calculate_entropy_indicators(content, affected_glyphs)
        entropy_level = entropy_indicators['composite_entropy']

        if entropy_level < threshold:
            return None

        # Extract emotional context
        emotional_context = self._extract_emotional_context(content)

        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(entropy_indicators, emotional_context)

        # Generate mutation suggestions
        suggested_mutations = self._suggest_mutations(affected_glyphs, entropy_indicators)

        zone_id = f"zone_{hashlib.md5(file_path.encode()).hexdigest()[:8]}"

        return EntropyZone(
            zone_id=zone_id,
            location=file_path,
            entropy_level=entropy_level,
            pressure_indicators=entropy_indicators['indicators'],
            affected_glyphs=list(set(affected_glyphs)),
            emotional_context=emotional_context,
            urgency_score=urgency_score,
            suggested_mutations=suggested_mutations
        )

    def _calculate_entropy_indicators(self, content: str, glyphs: List[str]) -> Dict[str, Any]:
        """Calculate entropy pressure indicators for content analysis."""
        indicators = []
        entropy_scores = []

        # Text complexity entropy
        if len(content) > 0:
            unique_chars = len(set(content.lower()))
            text_entropy = unique_chars / max(100, len(content)) * 2.0
            entropy_scores.append(min(1.0, text_entropy))

            if text_entropy > 0.15:
                indicators.append("high_text_complexity")

        # GLYPH density entropy
        glyph_density = len(glyphs) / max(100, len(content.split())) * 10.0
        entropy_scores.append(min(1.0, glyph_density))

        if glyph_density > 0.1:
            indicators.append("high_glyph_density")

        # GLYPH diversity entropy
        unique_glyphs = len(set(glyphs))
        diversity_entropy = unique_glyphs / max(1, len(glyphs))
        entropy_scores.append(diversity_entropy)

        if diversity_entropy > 0.7:
            indicators.append("high_glyph_diversity")

        # Pattern fragmentation entropy
        pattern_breaks = len(re.findall(r'[A-Z]{2,}[_\-][A-Z]{2,}', content))
        fragmentation_entropy = min(1.0, pattern_breaks / max(10, len(content.split())) * 5.0)
        entropy_scores.append(fragmentation_entropy)

        if fragmentation_entropy > 0.3:
            indicators.append("pattern_fragmentation")

        # Error pattern entropy
        error_patterns = ['TODO', 'FIXME', 'BUG', 'ERROR', 'FAIL', 'BROKEN']
        error_count = sum(content.upper().count(pattern) for pattern in error_patterns)
        error_entropy = min(1.0, error_count / max(10, len(content.split())) * 3.0)
        entropy_scores.append(error_entropy)

        if error_entropy > 0.2:
            indicators.append("error_accumulation")

        # Calculate composite entropy
        composite_entropy = sum(entropy_scores) / len(entropy_scores) if entropy_scores else 0.0

        return {
            'composite_entropy': composite_entropy,
            'indicators': indicators,
            'component_scores': {
                'text_complexity': entropy_scores[0] if len(entropy_scores) > 0 else 0.0,
                'glyph_density': entropy_scores[1] if len(entropy_scores) > 1 else 0.0,
                'diversity': entropy_scores[2] if len(entropy_scores) > 2 else 0.0,
                'fragmentation': entropy_scores[3] if len(entropy_scores) > 3 else 0.0,
                'error_pattern': entropy_scores[4] if len(entropy_scores) > 4 else 0.0
            }
        }

    def _extract_emotional_context(self, content: str) -> Dict[str, float]:
        """Extract emotional resonance context from content."""
        emotional_context = {}
        content_upper = content.upper()

        for emotion_type, keywords in self.emotional_patterns.items():
            score = 0.0
            for keyword in keywords:
                score += content_upper.count(keyword) * 0.1
            emotional_context[emotion_type] = min(1.0, score)

        # Normalize scores
        total_score = sum(emotional_context.values())
        if total_score > 0:
            for emotion in emotional_context:
                emotional_context[emotion] = emotional_context[emotion] / total_score

        return emotional_context

    def _calculate_urgency_score(self, entropy_indicators: Dict[str, Any],
                               emotional_context: Dict[str, float]) -> float:
        """Calculate urgency score for entropy zone evolution priority."""
        base_urgency = entropy_indicators['composite_entropy']

        # Boost urgency for critical indicators
        critical_indicators = ['high_glyph_density', 'pattern_fragmentation', 'error_accumulation']
        critical_boost = sum(0.1 for indicator in critical_indicators
                           if indicator in entropy_indicators['indicators'])

        # Emotional context modifiers
        tension_boost = emotional_context.get('tension', 0.0) * 0.15
        protection_boost = emotional_context.get('protection', 0.0) * 0.1

        urgency_score = min(1.0, base_urgency + critical_boost + tension_boost + protection_boost)

        return urgency_score

    def _suggest_mutations(self, glyphs: List[str],
                         entropy_indicators: Dict[str, Any]) -> List[str]:
        """Suggest specific mutation strategies for detected GLYPHs."""
        suggestions = []

        unique_glyphs = list(set(glyphs))

        # Semantic blending suggestions
        if len(unique_glyphs) >= 2:
            suggestions.append(f"semantic_blend:{unique_glyphs[0]},{unique_glyphs[1]}")

        # Entropy-driven mutations
        if 'high_text_complexity' in entropy_indicators['indicators']:
            suggestions.append(f"entropy_driven:{unique_glyphs[0] if unique_glyphs else 'ΛCOMPLEX'}")

        # Fragmentation repair
        if 'pattern_fragmentation' in entropy_indicators['indicators']:
            suggestions.append(f"repair_focused:fragmentation_repair")

        # Error-driven evolution
        if 'error_accumulation' in entropy_indicators['indicators']:
            suggestions.append(f"repair_focused:error_mitigation")

        # Creative synthesis for high diversity
        if 'high_glyph_diversity' in entropy_indicators['indicators']:
            suggestions.append(f"creative_synthesis:diversity_integration")

        return suggestions[:5]  # Limit to top 5 suggestions

    def mutate_glyphs(self,
                     source_glyphs: List[str] = None,
                     mutation_method: str = "auto",
                     creativity_level: float = 0.5) -> List[GlyphCandidate]:
        """
        Generate new candidate GLYPHs from semantic drift and emotional tone shifts.

        Args:
            source_glyphs: Specific GLYPHs to mutate (auto-detect if None)
            mutation_method: Method to use ('auto', 'semantic_blend', etc.)
            creativity_level: Mutation creativity factor (0.0-1.0)

        Returns:
            List of GlyphCandidate objects
        """
        logger.info("Starting GLYPH mutation process",
                   mutation_method=mutation_method,
                   creativity_level=creativity_level)

        if source_glyphs is None:
            # Auto-detect source GLYPHs from entropy zones
            source_glyphs = []
            for zone in self.entropy_zones:
                source_glyphs.extend(zone.affected_glyphs)
            source_glyphs = list(set(source_glyphs))[:20]  # Limit for performance

        if not source_glyphs:
            logger.warning("No source GLYPHs available for mutation")
            return []

        candidates = []

        for i, source_glyph in enumerate(source_glyphs):
            try:
                # Determine mutation method
                if mutation_method == "auto":
                    method = random.choice(self.mutation_methods)
                else:
                    method = mutation_method

                # Generate candidate using selected method
                candidate = self._generate_glyph_candidate(
                    source_glyph, method, creativity_level, i
                )

                if candidate:
                    candidates.append(candidate)

            except Exception as e:
                logger.warning("Failed to mutate GLYPH",
                             source_glyph=source_glyph, error=str(e))

        self.glyph_candidates.extend(candidates)

        # Log mutation event
        self._log_foundry_event("glyph_mutation", {
            "source_glyphs_count": len(source_glyphs),
            "candidates_generated": len(candidates),
            "mutation_method": mutation_method,
            "creativity_level": creativity_level,
            "successful_mutations": len([c for c in candidates if c.coherence_score > 0.5])
        })

        logger.info("GLYPH mutation complete",
                   candidates_generated=len(candidates),
                   viable_candidates=len([c for c in candidates if c.coherence_score > 0.6]))

        return candidates

    def _generate_glyph_candidate(self, source_glyph: str, method: str,
                                creativity_level: float, sequence_num: int) -> Optional[GlyphCandidate]:
        """Generate a single GLYPH candidate using specified mutation method."""

        candidate_id = f"candidate_{sequence_num:03d}_{datetime.now().strftime('%H%M%S')}"

        # Generate mutated symbol based on method
        if method == "semantic_blend":
            mutated_symbol = self._semantic_blend_mutation(source_glyph, creativity_level)
            semantic_context = f"Semantic blend from {source_glyph}"
        elif method == "emotional_shift":
            mutated_symbol = self._emotional_shift_mutation(source_glyph, creativity_level)
            semantic_context = f"Emotional resonance shift from {source_glyph}"
        elif method == "entropy_driven":
            mutated_symbol = self._entropy_driven_mutation(source_glyph, creativity_level)
            semantic_context = f"Entropy pressure evolution from {source_glyph}"
        elif method == "contextual_merge":
            mutated_symbol = self._contextual_merge_mutation(source_glyph, creativity_level)
            semantic_context = f"Contextual integration from {source_glyph}"
        elif method == "creative_synthesis":
            mutated_symbol = self._creative_synthesis_mutation(source_glyph, creativity_level)
            semantic_context = f"Creative synthesis from {source_glyph}"
        elif method == "repair_focused":
            mutated_symbol = self._repair_focused_mutation(source_glyph, creativity_level)
            semantic_context = f"Repair-focused evolution from {source_glyph}"
        else:
            # Default to semantic blend
            mutated_symbol = self._semantic_blend_mutation(source_glyph, creativity_level)
            semantic_context = f"Default semantic evolution from {source_glyph}"

        if not mutated_symbol or mutated_symbol == source_glyph:
            return None

        # Generate emotional profile
        emotional_profile = self._generate_emotional_profile(mutated_symbol, source_glyph)

        # Calculate scores
        coherence_score = self._calculate_coherence_score(mutated_symbol, source_glyph)
        novelty_score = self._calculate_novelty_score(mutated_symbol)

        # Determine safety classification
        safety_classification = self._classify_safety(mutated_symbol, emotional_profile)

        # Generate origin hash and lineage
        origin_data = f"{source_glyph}:{method}:{creativity_level}:{datetime.now().isoformat()}"
        origin_hash = hashlib.sha256(origin_data.encode()).hexdigest()[:16]

        entropy_lineage = self._generate_entropy_lineage(source_glyph)

        return GlyphCandidate(
            candidate_id=candidate_id,
            source_glyphs=[source_glyph],
            mutated_symbol=mutated_symbol,
            semantic_context=semantic_context,
            emotional_profile=emotional_profile,
            coherence_score=coherence_score,
            novelty_score=novelty_score,
            safety_classification=safety_classification,
            origin_hash=origin_hash,
            mutation_method=method,
            entropy_lineage=entropy_lineage
        )

    def _semantic_blend_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate semantic blend mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Semantic transformation patterns
        transforms = {
            'TRACE': ['TRACK', 'TRAIL', 'FOLLOW', 'MONITOR'],
            'PHASE': ['STAGE', 'CYCLE', 'STEP', 'WAVE'],
            'DRIFT': ['FLOW', 'SHIFT', 'MOVE', 'CURRENT'],
            'HARMONY': ['SYNC', 'ALIGN', 'TUNE', 'BALANCE'],
            'ENTROPY': ['CHAOS', 'DISORDER', 'RANDOM', 'FLUX'],
            'GOVERN': ['CONTROL', 'RULE', 'GUIDE', 'DIRECT'],
            'MEMORY': ['STORE', 'RECALL', 'CACHE', 'ARCHIVE']
        }

        for key, options in transforms.items():
            if key in base:
                if random.random() < creativity:
                    replacement = random.choice(options)
                    base = base.replace(key, replacement)
                break

        # Add creativity-based modifications
        if creativity > 0.7:
            # High creativity: compound mutations
            suffixes = ['_MESH', '_CORE', '_FLUX', '_LINK', '_NODE']
            if random.random() < 0.4:
                base += random.choice(suffixes)

        return f"Λ{base}"

    def _emotional_shift_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate emotional resonance shift mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Emotional transformation mapping
        emotional_shifts = {
            'positive': ['BRIGHT', 'WARM', 'FLOW', 'LIFT', 'SHINE'],
            'protective': ['SHIELD', 'GUARD', 'WARD', 'SECURE', 'FORT'],
            'dynamic': ['PULSE', 'SURGE', 'SPARK', 'BURST', 'RUSH'],
            'stable': ['ANCHOR', 'GROUND', 'ROOT', 'BASE', 'STEADY'],
            'adaptive': ['FLEX', 'ADAPT', 'MORPH', 'SHIFT', 'EVOLVE']
        }

        # Choose emotional direction based on creativity
        if creativity > 0.6:
            emotion_type = random.choice(list(emotional_shifts.keys()))
            modifier = random.choice(emotional_shifts[emotion_type])

            # Integrate emotional modifier
            if random.random() < 0.5:
                base = f"{modifier}_{base}"
            else:
                base = f"{base}_{modifier}"

        return f"Λ{base}"

    def _entropy_driven_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate entropy pressure driven mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Entropy-based transformations
        entropy_patterns = {
            'fragmentation': ['SPLIT', 'BREAK', 'SHARD', 'DIVIDE'],
            'fusion': ['MERGE', 'BLEND', 'FUSE', 'UNITE'],
            'amplification': ['BOOST', 'SURGE', 'PEAK', 'MAX'],
            'compression': ['COMPACT', 'DENSE', 'TIGHT', 'FOCUS'],
            'dispersion': ['SPREAD', 'SCATTER', 'WIDE', 'EXPAND']
        }

        # Select entropy transformation
        entropy_type = random.choice(list(entropy_patterns.keys()))
        transform = random.choice(entropy_patterns[entropy_type])

        # Apply entropy-driven modification
        if creativity > 0.5:
            # High entropy: more dramatic changes
            base = f"{transform}_{base}"
        else:
            # Low entropy: subtle modifications
            base = f"{base}_{transform}"

        return f"Λ{base}"

    def _contextual_merge_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate contextual integration mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Context-aware prefixes and suffixes
        contexts = {
            'system': ['SYS', 'CORE', 'NET', 'GRID'],
            'temporal': ['TIME', 'CLOCK', 'CYCLE', 'PERIOD'],
            'spatial': ['SPACE', 'ZONE', 'AREA', 'FIELD'],
            'relational': ['LINK', 'BOND', 'TIE', 'CONNECT'],
            'functional': ['TOOL', 'UTIL', 'FUNC', 'OPS']
        }

        context_type = random.choice(list(contexts.keys()))
        context_mod = random.choice(contexts[context_type])

        # Merge with context
        if random.random() < 0.5:
            base = f"{context_mod}{base}"
        else:
            base = f"{base}{context_mod}"

        return f"Λ{base}"

    def _creative_synthesis_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate creative synthesis mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Creative synthesis elements
        creative_elements = {
            'quantum': ['QBIT', 'WAVE', 'FIELD', 'FLUX'],
            'organic': ['CELL', 'GROW', 'LIFE', 'BIO'],
            'geometric': ['ANGLE', 'CURVE', 'SPIRAL', 'MATRIX'],
            'musical': ['TONE', 'CHORD', 'RHYTHM', 'BEAT'],
            'crystalline': ['CRYSTAL', 'PRISM', 'FACET', 'LATTICE']
        }

        synthesis_type = random.choice(list(creative_elements.keys()))
        element = random.choice(creative_elements[synthesis_type])

        # Synthesize with creative element
        if creativity > 0.8:
            # Very creative: complex synthesis
            base = f"{element}{base}SYNTH"
        elif creativity > 0.6:
            base = f"{element}_{base}"
        else:
            base = f"{base}_{element}"

        return f"Λ{base}"

    def _repair_focused_mutation(self, source_glyph: str, creativity: float) -> str:
        """Generate repair-focused mutation."""
        base = source_glyph.replace("Λ", "").replace("GLYPH", "")

        # Repair-focused modifications
        repair_patterns = {
            'restoration': ['RESTORE', 'REPAIR', 'FIX', 'HEAL'],
            'reinforcement': ['STRONG', 'SOLID', 'FIRM', 'STABLE'],
            'protection': ['SAFE', 'SECURE', 'GUARD', 'PROTECT'],
            'optimization': ['OPT', 'TUNE', 'REFINE', 'POLISH'],
            'validation': ['VERIFY', 'CHECK', 'VALID', 'CONFIRM']
        }

        repair_type = random.choice(list(repair_patterns.keys()))
        repair_mod = random.choice(repair_patterns[repair_type])

        # Apply repair focus
        base = f"{repair_mod}_{base}"

        return f"Λ{base}"

    def _generate_emotional_profile(self, mutated_symbol: str, source_glyph: str) -> Dict[str, float]:
        """Generate emotional resonance profile for mutated GLYPH."""
        profile = {}

        # Base emotional resonance from symbol analysis
        symbol_upper = mutated_symbol.upper()

        # Analyze emotional keywords in symbol
        for emotion_type, keywords in self.emotional_patterns.items():
            score = 0.0
            for keyword in keywords:
                if keyword in symbol_upper:
                    score += 0.3
            profile[emotion_type] = min(1.0, score + random.uniform(-0.1, 0.1))

        # Inheritance from source GLYPH
        source_upper = source_glyph.upper()
        for emotion_type in profile:
            # Inherit some emotional characteristics
            inheritance_factor = 0.2
            for keyword in self.emotional_patterns[emotion_type]:
                if keyword in source_upper:
                    profile[emotion_type] += inheritance_factor

        # Normalize profile
        total = sum(profile.values())
        if total > 0:
            for emotion in profile:
                profile[emotion] = profile[emotion] / total

        return profile

    def _calculate_coherence_score(self, mutated_symbol: str, source_glyph: str) -> float:
        """Calculate semantic coherence score for mutation."""
        # Base coherence from symbol structure
        structure_score = 0.5

        # Length appropriateness
        if 8 <= len(mutated_symbol) <= 20:
            structure_score += 0.2

        # Λ prefix maintained
        if mutated_symbol.startswith('Λ'):
            structure_score += 0.2

        # Character pattern consistency
        symbol_body = mutated_symbol.replace('Λ', '')
        if re.match(r'^[A-Z][A-Z0-9_]*$', symbol_body):
            structure_score += 0.1

        # Semantic similarity to source
        common_roots = 0
        source_parts = re.split(r'[_\-]', source_glyph.replace('Λ', ''))
        mutated_parts = re.split(r'[_\-]', symbol_body)

        for part in source_parts:
            if any(part in m_part or m_part in part for m_part in mutated_parts):
                common_roots += 1

        similarity_score = common_roots / max(1, len(source_parts)) * 0.3

        total_score = min(1.0, structure_score + similarity_score)
        return total_score

    def _calculate_novelty_score(self, mutated_symbol: str) -> float:
        """Calculate novelty score for mutation uniqueness."""
        # Check against existing registry
        if mutated_symbol in self.glyph_registry:
            return 0.0  # Already exists

        # Base novelty score
        novelty = 0.7

        # Character uniqueness
        unique_chars = len(set(mutated_symbol.lower()))
        char_novelty = unique_chars / max(1, len(mutated_symbol))
        novelty += char_novelty * 0.2

        # Pattern novelty (uncommon combinations)
        uncommon_patterns = ['_SYNTH', '_FLUX', '_MESH', 'QUANTUM', 'CRYSTAL']
        for pattern in uncommon_patterns:
            if pattern in mutated_symbol:
                novelty += 0.1
                break

        return min(1.0, novelty)

    def _classify_safety(self, mutated_symbol: str, emotional_profile: Dict[str, float]) -> str:
        """Classify safety level of mutated GLYPH."""
        # Start with SAFE classification
        safety_level = 'SAFE'

        # Check for potentially unsafe patterns
        unsafe_patterns = ['BREAK', 'DESTROY', 'KILL', 'HARM', 'ATTACK', 'CORRUPT']
        for pattern in unsafe_patterns:
            if pattern in mutated_symbol.upper():
                safety_level = 'RESTRICTED'
                break

        # Check emotional profile for tension/conflict
        tension_score = emotional_profile.get('tension', 0.0)
        if tension_score > 0.8:
            if safety_level == 'SAFE':
                safety_level = 'CAUTION'

        # Check for review-needed patterns
        review_patterns = ['OVERRIDE', 'BYPASS', 'FORCE', 'IGNORE']
        for pattern in review_patterns:
            if pattern in mutated_symbol.upper():
                if safety_level == 'SAFE':
                    safety_level = 'REVIEW'
                break

        return safety_level

    def _generate_entropy_lineage(self, source_glyph: str) -> str:
        """Generate entropy lineage chain for provenance tracking."""
        # Find entropy zone containing source GLYPH
        source_zone = None
        for zone in self.entropy_zones:
            if source_glyph in zone.affected_glyphs:
                source_zone = zone
                break

        if source_zone:
            lineage = f"{source_zone.zone_id}:entropy_{source_zone.entropy_level:.3f}"
        else:
            lineage = f"unknown_zone:entropy_0.500"

        return lineage

    def score_glyph_viability(self, candidates: List[GlyphCandidate] = None) -> List[GlyphCandidate]:
        """
        Evaluate coherence, novelty, emotional harmony, and ethical safety.

        Args:
            candidates: Specific candidates to score (uses all if None)

        Returns:
            List of candidates with updated viability scores
        """
        if candidates is None:
            candidates = self.glyph_candidates

        logger.info("Starting GLYPH viability scoring", candidates_count=len(candidates))

        scored_candidates = []

        for candidate in candidates:
            try:
                # Composite viability score
                viability_score = self._calculate_composite_viability(candidate)

                # Update candidate with enhanced scoring
                enhanced_candidate = self._enhance_candidate_scoring(candidate, viability_score)
                scored_candidates.append(enhanced_candidate)

            except Exception as e:
                logger.warning("Failed to score candidate",
                             candidate_id=candidate.candidate_id, error=str(e))
                scored_candidates.append(candidate)  # Keep original

        # Log scoring event
        high_viability = len([c for c in scored_candidates
                            if hasattr(c, 'viability_score') and c.viability_score > 0.8])

        self._log_foundry_event("viability_scoring", {
            "candidates_scored": len(scored_candidates),
            "high_viability_count": high_viability,
            "safe_candidates": len([c for c in scored_candidates
                                  if c.safety_classification == 'SAFE']),
            "restricted_candidates": len([c for c in scored_candidates
                                        if c.safety_classification == 'RESTRICTED'])
        })

        logger.info("GLYPH viability scoring complete",
                   high_viability=high_viability,
                   total_scored=len(scored_candidates))

        return scored_candidates

    def _calculate_composite_viability(self, candidate: GlyphCandidate) -> float:
        """Calculate composite viability score from multiple factors."""
        # Weight factors
        weights = {
            'coherence': 0.3,
            'novelty': 0.25,
            'emotional_harmony': 0.2,
            'safety': 0.25
        }

        # Calculate emotional harmony score
        emotional_harmony = self._calculate_emotional_harmony(candidate.emotional_profile)

        # Calculate safety score
        safety_scores = {'SAFE': 1.0, 'CAUTION': 0.7, 'REVIEW': 0.5, 'RESTRICTED': 0.2}
        safety_score = safety_scores.get(candidate.safety_classification, 0.5)

        # Composite calculation
        viability_score = (
            candidate.coherence_score * weights['coherence'] +
            candidate.novelty_score * weights['novelty'] +
            emotional_harmony * weights['emotional_harmony'] +
            safety_score * weights['safety']
        )

        return min(1.0, viability_score)

    def _calculate_emotional_harmony(self, emotional_profile: Dict[str, float]) -> float:
        """Calculate emotional harmony score from profile balance."""
        if not emotional_profile:
            return 0.5  # Neutral

        # Check for emotional balance
        values = list(emotional_profile.values())
        if not values:
            return 0.5

        # Harmony favors balanced emotional states
        variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
        balance_score = 1.0 - min(1.0, variance * 2)

        # Boost for positive emotions
        positive_emotions = ['harmony', 'growth', 'creativity']
        positive_boost = sum(emotional_profile.get(emotion, 0.0) for emotion in positive_emotions) * 0.1

        harmony_score = min(1.0, balance_score + positive_boost)
        return harmony_score

    def _enhance_candidate_scoring(self, candidate: GlyphCandidate, viability_score: float) -> GlyphCandidate:
        """Enhance candidate with additional scoring metadata."""
        # Create enhanced candidate with viability score
        enhanced = GlyphCandidate(
            candidate_id=candidate.candidate_id,
            source_glyphs=candidate.source_glyphs,
            mutated_symbol=candidate.mutated_symbol,
            semantic_context=candidate.semantic_context,
            emotional_profile=candidate.emotional_profile,
            coherence_score=candidate.coherence_score,
            novelty_score=candidate.novelty_score,
            safety_classification=candidate.safety_classification,
            origin_hash=candidate.origin_hash,
            mutation_method=candidate.mutation_method,
            entropy_lineage=candidate.entropy_lineage
        )

        # Add viability score as dynamic attribute
        enhanced.viability_score = viability_score

        return enhanced

    def register_new_glyph(self, candidate: GlyphCandidate,
                          usage_contexts: List[str] = None) -> Optional[GlyphRecord]:
        """
        Add validated GLYPH to the global registry with version tracking.

        Args:
            candidate: Validated GlyphCandidate to register
            usage_contexts: Suggested usage contexts

        Returns:
            GlyphRecord if registration successful, None otherwise
        """
        logger.info("Registering new GLYPH",
                   symbol=candidate.mutated_symbol,
                   candidate_id=candidate.candidate_id)

        # Validation checks
        if not hasattr(candidate, 'viability_score'):
            logger.warning("Cannot register unscored candidate",
                          candidate_id=candidate.candidate_id)
            return None

        if candidate.viability_score < 0.6:
            logger.warning("Cannot register low viability candidate",
                          candidate_id=candidate.candidate_id,
                          viability_score=candidate.viability_score)
            return None

        if candidate.safety_classification == 'RESTRICTED':
            logger.warning("Cannot register restricted candidate",
                          candidate_id=candidate.candidate_id)
            return None

        # Check for existing registration
        if candidate.mutated_symbol in self.glyph_registry:
            logger.warning("GLYPH already registered",
                          symbol=candidate.mutated_symbol)
            return self.glyph_registry[candidate.mutated_symbol]

        # Generate GLYPH record
        glyph_id = f"glyph_{hashlib.md5(candidate.mutated_symbol.encode()).hexdigest()[:12]}"

        # Build provenance chain
        provenance_chain = [
            f"source:{','.join(candidate.source_glyphs)}",
            f"method:{candidate.mutation_method}",
            f"lineage:{candidate.entropy_lineage}",
            f"registered:{datetime.now().isoformat()}"
        ]

        # Calculate stability metrics
        stability_metrics = {
            'coherence': candidate.coherence_score,
            'novelty': candidate.novelty_score,
            'viability': candidate.viability_score,
            'emotional_balance': self._calculate_emotional_harmony(candidate.emotional_profile)
        }

        # Create registry record
        glyph_record = GlyphRecord(
            glyph_id=glyph_id,
            symbol=candidate.mutated_symbol,
            semantic_meaning=candidate.semantic_context,
            emotional_resonance=candidate.emotional_profile,
            creation_timestamp=datetime.now().isoformat(),
            source_entropy_zone=candidate.entropy_lineage.split(':')[0] if ':' in candidate.entropy_lineage else 'unknown',
            viability_score=candidate.viability_score,
            safety_rating=candidate.safety_classification,
            version="1.0",
            provenance_chain=provenance_chain,
            usage_contexts=usage_contexts or [],
            stability_metrics=stability_metrics
        )

        # Register GLYPH
        self.glyph_registry[candidate.mutated_symbol] = glyph_record

        # Save registry to file
        self._save_glyph_registry()

        # Log registration event
        self._log_foundry_event("glyph_registration", {
            "glyph_symbol": candidate.mutated_symbol,
            "glyph_id": glyph_id,
            "viability_score": candidate.viability_score,
            "safety_rating": candidate.safety_classification,
            "source_glyphs": candidate.source_glyphs,
            "registry_size": len(self.glyph_registry)
        })

        logger.info("GLYPH registration successful",
                   symbol=candidate.mutated_symbol,
                   glyph_id=glyph_id,
                   registry_size=len(self.glyph_registry))

        return glyph_record

    def _load_glyph_registry(self):
        """Load existing GLYPH registry from file."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    registry_data = json.load(f)

                # Convert to GlyphRecord objects
                for symbol, record_data in registry_data.items():
                    self.glyph_registry[symbol] = GlyphRecord(**record_data)

                logger.info("GLYPH registry loaded",
                           registry_size=len(self.glyph_registry))

            except Exception as e:
                logger.warning("Failed to load GLYPH registry", error=str(e))

    def _save_glyph_registry(self):
        """Save GLYPH registry to file."""
        try:
            registry_data = {}
            for symbol, record in self.glyph_registry.items():
                registry_data[symbol] = asdict(record)

            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)

            logger.info("GLYPH registry saved", registry_size=len(self.glyph_registry))

        except Exception as e:
            logger.error("Failed to save GLYPH registry", error=str(e))

    def log_foundry_event(self, event_type: str, event_data: Dict[str, Any]):
        """Public interface for logging foundry events."""
        self._log_foundry_event(event_type, event_data)

    def _log_foundry_event(self, event_type: str, event_data: Dict[str, Any]):
        """ΛTAG-structured logs capturing glyph mutation and synthesis provenance."""

        # Create structured event
        event = {
            "ΛFOUNDRY_EVENT": event_type,
            "timestamp": datetime.now().isoformat(),
            "event_id": f"foundry_{hashlib.md5(f'{event_type}{datetime.now().isoformat()}'.encode()).hexdigest()[:8]}",
            "ΛTAGS": {
                "ΛFOUNDRY": True,
                "ΛMUTATION": event_type in ['glyph_mutation', 'entropy_analysis'],
                "ΛREGISTRATION": event_type == 'glyph_registration',
                "ΛVIABILITY": event_type == 'viability_scoring'
            },
            "event_data": event_data
        }

        # Add to internal events log
        self.foundry_events.append(event)

        # Write to structured log file
        log_file = self.log_directory / "foundry_events.jsonl"
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.warning("Failed to write foundry event log", error=str(e))

        # Log to structlog
        logger.info("ΛFOUNDRY event logged",
                   event_type=event_type,
                   event_id=event["event_id"])

    def generate_mutation_report(self, output_format: str = "markdown",
                               output_file: str = "mutation_report") -> str:
        """
        Generate comprehensive mutation report.

        Args:
            output_format: 'markdown' or 'json'
            output_file: Output filename (without extension)

        Returns:
            Path to generated report file
        """
        logger.info("Generating mutation report",
                   format=output_format,
                   candidates_count=len(self.glyph_candidates))

        if output_format == "markdown":
            report_path = self.output_directory / f"{output_file}.md"
            self._generate_markdown_report(report_path)
        elif output_format == "json":
            report_path = self.output_directory / f"{output_file}.json"
            self._generate_json_report(report_path)
        else:
            raise ValueError(f"Unsupported format: {output_format}")

        logger.info("Mutation report generated", report_path=str(report_path))
        return str(report_path)

    def _generate_markdown_report(self, report_path: Path):
        """Generate Markdown format mutation report."""
        lines = [
            "# 🏭 ΛFOUNDRY Mutation Report",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Entropy Zones Analyzed:** {len(self.entropy_zones)}",
            f"**Candidates Generated:** {len(self.glyph_candidates)}",
            f"**GLYPHs Registered:** {len(self.glyph_registry)}",
            "",
            "## 📊 Executive Summary",
            ""
        ]

        # Statistics
        if self.glyph_candidates:
            scored_candidates = [c for c in self.glyph_candidates
                               if hasattr(c, 'viability_score')]

            high_viability = len([c for c in scored_candidates if c.viability_score > 0.8])
            safe_candidates = len([c for c in self.glyph_candidates
                                 if c.safety_classification == 'SAFE'])

            lines.extend([
                f"- **High Viability Candidates:** {high_viability}/{len(scored_candidates)}",
                f"- **Safe Classifications:** {safe_candidates}/{len(self.glyph_candidates)}",
                f"- **Average Coherence:** {sum(c.coherence_score for c in self.glyph_candidates) / len(self.glyph_candidates):.3f}",
                f"- **Average Novelty:** {sum(c.novelty_score for c in self.glyph_candidates) / len(self.glyph_candidates):.3f}",
                ""
            ])

        # Entropy Zones
        lines.extend([
            "## 🌡️ Entropy Zone Analysis",
            ""
        ])

        for zone in self.entropy_zones[:5]:  # Top 5 zones
            lines.extend([
                f"### Zone {zone.zone_id}",
                f"**Location:** `{zone.location}`",
                f"**Entropy Level:** {zone.entropy_level:.3f}",
                f"**Urgency Score:** {zone.urgency_score:.3f}",
                f"**Affected GLYPHs:** {', '.join(zone.affected_glyphs[:5])}",
                ""
            ])

        # Generated Candidates
        lines.extend([
            "## 🧬 Generated GLYPH Candidates",
            ""
        ])

        # Sort candidates by viability score
        sorted_candidates = sorted(self.glyph_candidates,
                                 key=lambda c: getattr(c, 'viability_score', 0.0),
                                 reverse=True)

        for candidate in sorted_candidates[:10]:  # Top 10 candidates
            viability = getattr(candidate, 'viability_score', 0.0)
            safety_emoji = {"SAFE": "🟢", "CAUTION": "🟡", "REVIEW": "🔍", "RESTRICTED": "🔴"}.get(
                candidate.safety_classification, "⚪"
            )

            lines.extend([
                f"### {candidate.mutated_symbol} {safety_emoji}",
                f"**Source:** {', '.join(candidate.source_glyphs)}",
                f"**Method:** {candidate.mutation_method}",
                f"**Viability:** {viability:.3f}",
                f"**Coherence:** {candidate.coherence_score:.3f}",
                f"**Novelty:** {candidate.novelty_score:.3f}",
                f"**Context:** {candidate.semantic_context}",
                ""
            ])

        # Registered GLYPHs
        if self.glyph_registry:
            lines.extend([
                "## 📋 Registered GLYPHs",
                ""
            ])

            for symbol, record in list(self.glyph_registry.items())[:5]:
                lines.extend([
                    f"### {symbol}",
                    f"**ID:** {record.glyph_id}",
                    f"**Created:** {record.creation_timestamp[:19]}",
                    f"**Viability:** {record.viability_score:.3f}",
                    f"**Safety:** {record.safety_rating}",
                    f"**Meaning:** {record.semantic_meaning}",
                    ""
                ])

        # Footer
        lines.extend([
            "---",
            "",
            "## 🔖 ΛTAG Annotations",
            "",
            f"- **ΛFOUNDRY_GENERATED**: {datetime.now().isoformat()}",
            f"- **ΛFOUNDRY_VERSION**: 1.0",
            f"- **ΛFOUNDRY_MUTATIONS**: {len(self.glyph_candidates)}",
            "",
            "*Generated by ΛFOUNDRY - Symbolic Mutation Engine for LUKHAS AGI*"
        ])

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _generate_json_report(self, report_path: Path):
        """Generate JSON format mutation report."""

        # Convert candidates with viability scores
        candidates_data = []
        for candidate in self.glyph_candidates:
            candidate_dict = asdict(candidate)
            if hasattr(candidate, 'viability_score'):
                candidate_dict['viability_score'] = candidate.viability_score
            candidates_data.append(candidate_dict)

        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "foundry_version": "1.0",
                "report_type": "mutation_analysis"
            },
            "summary": {
                "entropy_zones_analyzed": len(self.entropy_zones),
                "candidates_generated": len(self.glyph_candidates),
                "glyphs_registered": len(self.glyph_registry),
                "high_viability_candidates": len([c for c in self.glyph_candidates
                                                if hasattr(c, 'viability_score') and c.viability_score > 0.8]),
                "safe_candidates": len([c for c in self.glyph_candidates
                                     if c.safety_classification == 'SAFE'])
            },
            "entropy_zones": [asdict(zone) for zone in self.entropy_zones],
            "glyph_candidates": candidates_data,
            "registered_glyphs": {symbol: asdict(record)
                                for symbol, record in self.glyph_registry.items()},
            "foundry_events": self.foundry_events
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)


def main():
    """CLI interface for ΛFOUNDRY."""
    parser = argparse.ArgumentParser(
        description="ΛFOUNDRY - Symbolic Mutation Engine & Entropy-Driven Glyph Synthesizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python symbolic_foundry.py --source memory/ dream/ --mutate
  python symbolic_foundry.py --entropy-zones high --output results/new_glyphs.md
  python symbolic_foundry.py --repair-mode --creativity-level 0.8
  python symbolic_foundry.py --simulate --mutation-method semantic_blend
        """
    )

    parser.add_argument("--source", nargs="+",
                       help="Source directories to scan for entropy zones")

    parser.add_argument("--entropy-zones",
                       choices=['low', 'medium', 'high', 'critical'],
                       default='medium',
                       help="Entropy threshold for zone detection")

    parser.add_argument("--mutate", action="store_true",
                       help="Generate GLYPH mutations from detected zones")

    parser.add_argument("--mutation-method",
                       choices=['auto', 'semantic_blend', 'emotional_shift',
                               'entropy_driven', 'contextual_merge',
                               'creative_synthesis', 'repair_focused'],
                       default='auto',
                       help="Mutation method to use")

    parser.add_argument("--creativity-level", type=float, default=0.5,
                       help="Creativity factor for mutations (0.0-1.0)")

    parser.add_argument("--repair-mode", action="store_true",
                       help="Focus on repairing damaged/collapsed GLYPHs")

    parser.add_argument("--simulate", action="store_true",
                       help="Preview mode without actual mutations")

    parser.add_argument("--output", default="mutation_report",
                       help="Output base filename")

    parser.add_argument("--output-format",
                       choices=['markdown', 'json', 'both'],
                       default='markdown',
                       help="Report output format")

    parser.add_argument("--register-viable", action="store_true",
                       help="Automatically register high-viability candidates")

    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    try:
        print("🏭 ΛFOUNDRY - Symbolic Mutation Engine")
        print("="*50)

        # Initialize foundry
        foundry = ΛFoundry(source_directories=args.source)

        print(f"📂 Source directories: {', '.join(foundry.source_directories)}")
        print(f"🌡️ Entropy threshold: {args.entropy_zones}")
        print(f"🧬 Mutation method: {args.mutation_method}")
        print(f"🎨 Creativity level: {args.creativity_level}")
        print()

        # Analyze entropy pressure
        print("🔍 Analyzing entropy pressure...")
        entropy_zones = foundry.analyze_entropy_pressure(
            entropy_threshold=args.entropy_zones,
            focus_directories=args.source
        )
        print(f"   Found {len(entropy_zones)} entropy zones")

        if args.mutate or args.simulate:
            print("🧬 Generating GLYPH mutations...")

            if args.repair_mode:
                # Focus on high-entropy zones for repair
                high_entropy_glyphs = []
                for zone in entropy_zones:
                    if zone.entropy_level > 0.7:
                        high_entropy_glyphs.extend(zone.affected_glyphs)
                source_glyphs = list(set(high_entropy_glyphs))[:10]
            else:
                source_glyphs = None

            candidates = foundry.mutate_glyphs(
                source_glyphs=source_glyphs,
                mutation_method=args.mutation_method,
                creativity_level=args.creativity_level
            )
            print(f"   Generated {len(candidates)} candidates")

            # Score viability
            print("📊 Scoring GLYPH viability...")
            scored_candidates = foundry.score_glyph_viability(candidates)

            high_viability = len([c for c in scored_candidates
                                if hasattr(c, 'viability_score') and c.viability_score > 0.8])
            print(f"   {high_viability} high-viability candidates")

            # Register viable candidates if requested
            if args.register_viable and not args.simulate:
                print("📋 Registering viable GLYPHs...")
                registered_count = 0

                for candidate in scored_candidates:
                    if (hasattr(candidate, 'viability_score') and
                        candidate.viability_score > 0.8 and
                        candidate.safety_classification in ['SAFE', 'CAUTION']):

                        record = foundry.register_new_glyph(candidate)
                        if record:
                            registered_count += 1

                print(f"   Registered {registered_count} new GLYPHs")

        # Generate reports
        print("📝 Generating reports...")

        if args.output_format in ['markdown', 'both']:
            markdown_path = foundry.generate_mutation_report('markdown', args.output)
            print(f"   Markdown: {markdown_path}")

        if args.output_format in ['json', 'both']:
            json_path = foundry.generate_mutation_report('json', args.output)
            print(f"   JSON: {json_path}")

        # Summary
        print("\n✅ ΛFOUNDRY execution completed!")
        print(f"📊 Summary:")
        print(f"   • Entropy zones: {len(entropy_zones)}")
        print(f"   • Candidates generated: {len(foundry.glyph_candidates)}")
        print(f"   • GLYPHs registered: {len(foundry.glyph_registry)}")
        print(f"   • Events logged: {len(foundry.foundry_events)}")

        if args.simulate:
            print("\n🎭 SIMULATION MODE - No actual mutations performed")

    except Exception as e:
        print(f"❌ ΛFOUNDRY execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())


"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠═══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/test_symbolic_foundry.py
║   - Coverage: 0% (Legacy code - tests pending)
║   - Linting: Not yet evaluated
║
║ MONITORING:
║   - Metrics: Entropy zones, mutation counts, viability scores
║   - Logs: foundry_events.jsonl (ΛTAG structured)
║   - Alerts: High entropy zones, restricted GLYPHs
║
║ COMPLIANCE:
║   - Standards: LUKHAS Symbolic Safety Protocol
║   - Ethics: Safety classification system (4 levels)
║   - Safety: Viability scoring prevents unstable mutations
║
║ REFERENCES:
║   - Docs: docs/symbolic/foundry.md
║   - Issues: github.com/lukhas-ai/agi/issues?label=symbolic-foundry
║   - Wiki: internal.lukhas.ai/wiki/symbolic-mutation
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
║
║ CHANGELOG:
║   - v2.0.0 (2025-07-25): Recovered from archive and updated headers
║   - v1.0.0 (2025-07-22): Initial implementation with 6 mutation methods
╚═══════════════════════════════════════════════════════════════════════════════
"""