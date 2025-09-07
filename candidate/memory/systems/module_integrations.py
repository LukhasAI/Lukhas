#!/usr/bin/env python3
import re
import logging
import streamlit as st
import random
import time
logger = logging.getLogger(__name__)
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧩 LUKHAS AI - MODULE-SPECIFIC MEMORY INTEGRATIONS
║ Concrete implementations for learning, creativity, voice, and meta modules
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: module_integrations.py
║ Path: memory/systems/module_integrations.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Module Integration Team
╠══════════════════════════════════════════════════════════════════════════════════
║ ΛTAG: ΛMEMORY, ΛLEARNING, ΛCREATIVITY, ΛVOICE, ΛMETA
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import numpy as np

from .integration_adapters import MemorySafetyIntegration
from .memory_safety_features import MemorySafetySystem


class LearningModuleIntegration:
    """
    Memory safety integration for the Learning module.

    Features:
    - Drift-aware training data selection
    - Trust-scored memory prioritization
    - Adaptive concept evolution tracking
    """

    def __init__(self, integration: MemorySafetyIntegration):
        self.integration = integration
        self.memory = integration.memory
        self.safety = integration.safety

        # Learning-specific configuration
        self.min_trust_for_training = 0.7
        self.drift_recalibration_threshold = 0.3
        self.concept_evolution_window = 100  # memories

        # Register with adapters
        self._register_callbacks()

    def _register_callbacks(self):
        """Register learning-specific callbacks"""
        # Trust updates affect training data selection
        self.integration.verifold.register_trust_callback("learning", self._on_trust_update)

        # Drift triggers concept recalibration
        self.integration.drift.register_calibration_callback("learning", self._on_drift_calibration_needed)

    async def _on_trust_update(self, memory_id: str, trust_score: float):
        """Handle trust score updates for training data"""
        if trust_score < self.min_trust_for_training:
            logger.warning(
                "Memory trust too low for training",
                memory_id=memory_id,
                trust_score=trust_score,
            )
            # Mark for exclusion from training
            if hasattr(self, "_excluded_memories"):
                self._excluded_memories.add(memory_id)

    async def _on_drift_calibration_needed(self, tag: str, drift_score: float):
        """Handle drift calibration triggers"""
        logger.info("Learning module calibration triggered", tag=tag, drift_score=drift_score)
        # Trigger concept re-learning for this tag
        await self.relearn_concept(tag)

    async def get_verified_training_batch(
        self, tags: list[str], batch_size: int = 32
    ) -> list[tuple[dict[str, Any], float]]:
        """
        Get a batch of verified memories for training.

        Only returns memories that pass trust and drift checks.
        """
        training_batch = []

        for tag in tags:
            # Get memories for tag
            memories = await self.memory.fold_out_by_tag(tag, max_items=batch_size * 2)

            for memory in memories:
                memory_id = memory.item_id
                memory_data = memory.data

                # Verify with learning module requirements
                is_valid, trust_score, error = await self.integration.verifold.verify_for_module(
                    "learning", memory_id, memory_data
                )

                if is_valid and trust_score >= self.min_trust_for_training:
                    # Check drift
                    if memory_id in self.memory.embedding_cache:
                        embedding = self.memory.embedding_cache[memory_id]
                        drift_analysis = await self.integration.drift.track_module_usage(
                            "learning",
                            tag,
                            embedding,
                            {"purpose": "training", "batch": True},
                        )

                        if drift_analysis["recommendation"] != "calibrate":
                            training_batch.append((memory_data, trust_score))

                if len(training_batch) >= batch_size:
                    break

        # Sort by trust score (highest first)
        training_batch.sort(key=lambda x: x[1], reverse=True)

        return training_batch[:batch_size]

    async def track_concept_evolution(self, concept: str, new_example: dict[str, Any]) -> dict[str, Any]:
        """
        Track how a concept evolves over time.

        Uses drift metrics to understand concept changes.
        """
        # Store the new example
        mem_id = await self.memory.fold_in_with_embedding(
            data={
                **new_example,
                "concept": concept,
                "evolution_timestamp": datetime.now(timezone.utc),
            },
            tags=[f"concept:{concept}", "evolution", "learning"],
            text_content=str(new_example),
        )

        # Track drift for this concept
        if mem_id in self.memory.embedding_cache:
            embedding = self.memory.embedding_cache[mem_id]
            drift_result = await self.integration.drift.track_module_usage(
                "learning", f"concept:{concept}", embedding, {"evolution": True}
            )

            # Analyze evolution pattern
            concept_metrics = self.safety.drift_metrics.get(f"concept:{concept}")

            if concept_metrics and len(concept_metrics.drift_scores) >= 5:
                recent_drift = np.mean(concept_metrics.drift_scores[-5:])
                trend = "stable" if recent_drift < 0.1 else "evolving" if recent_drift < 0.3 else "shifting"

                return {
                    "concept": concept,
                    "memory_id": mem_id,
                    "drift_score": drift_result["drift_score"],
                    "trend": trend,
                    "total_examples": concept_metrics.total_uses,
                    "recommendation": self._get_learning_recommendation(trend, recent_drift),
                }

        return {"concept": concept, "memory_id": mem_id, "status": "tracking_started"}

    def _get_learning_recommendation(self, trend: str, drift_score: float) -> str:
        """Get learning recommendation based on concept evolution"""
        if trend == "stable":
            return "continue_current_model"
        elif trend == "evolving":
            return "incremental_learning"
        else:  # shifting
            return "major_retraining_recommended"

    async def relearn_concept(self, tag: str):
        """Relearn a concept after drift calibration"""
        logger.info(f"Relearning concept: {tag}")

        # Get recent memories for this tag
        recent_memories = await self.memory.fold_out_by_tag(tag, max_items=self.concept_evolution_window)

        # Filter by trust and recency
        training_data = []
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=7)

        for memory in recent_memories:
            if memory.timestamp > cutoff_time:
                # Verify it's still valid
                is_valid, trust_score, _ = await self.integration.verifold.verify_for_module(
                    "learning", memory.item_id, memory.data
                )

                if is_valid and trust_score >= self.min_trust_for_training:
                    training_data.append(memory)

        logger.info(f"Relearning with {len(training_data)} verified recent memories")

        # In production, would trigger actual model retraining here
        # For now, just update drift calibration
        self.safety.calibrate_drift_metrics()


class CreativityModuleIntegration:
    """
    Memory safety integration for the Creativity module.

    Features:
    - Reality-anchored creative exploration
    - Safe hallucination boundaries
    - Creative drift encouragement within safety limits
    """

    def __init__(self, integration: MemorySafetyIntegration):
        self.integration = integration
        self.memory = integration.memory
        self.safety = integration.safety

        # Creativity-specific configuration
        self.creativity_drift_bonus = 0.2  # Allow more drift for creativity
        self.reality_check_frequency = 5  # Check every 5th creation
        self.creation_counter = 0

        # Creative constraints
        self._setup_creative_anchors()

    def _setup_creative_anchors(self):
        """Set up creativity-specific reality anchors"""
        creative_anchors = {
            "consistency": "Created worlds must have internal consistency",
            "empathy": "Creative outputs should consider human emotions",
            "ethics": "Creations should not promote harm",
        }

        for key, truth in creative_anchors.items():
            self.integration.anchors.add_module_anchor("creativity", key, truth)

    async def generate_creative_synthesis(
        self, seed_memories: list[str], creativity_level: float = 0.5
    ) -> dict[str, Any]:
        """
        Generate creative synthesis with safety boundaries.

        creativity_level: 0.0 (safe) to 1.0 (highly creative)
        """
        # Validate seed memories
        valid_seeds = []
        seed_embeddings = []

        for mem_id in seed_memories:
            if mem_id in self.memory.items:
                memory = self.memory.items[mem_id]

                # Check if memory is verified
                is_valid, trust_score, _ = await self.integration.verifold.verify_for_module(
                    "creativity", mem_id, memory.data
                )

                if is_valid:
                    valid_seeds.append(memory)
                    if mem_id in self.memory.embedding_cache:
                        seed_embeddings.append(self.memory.embedding_cache[mem_id])

        if not valid_seeds:
            return {"error": "No valid seed memories"}

        # Generate creative combination
        if seed_embeddings:
            # Interpolate between embeddings with creativity noise
            base_embedding = np.mean(seed_embeddings, axis=0)
            noise = np.random.randn(*base_embedding.shape) * creativity_level * 0.3
            creative_embedding = base_embedding + noise

            # Normalize
            creative_embedding = creative_embedding / (np.linalg.norm(creative_embedding) + 1e-8)

            # Find memories near this creative point
            creative_neighbors = self.memory.vector_store.search_similar(
                creative_embedding,
                top_k=10,
                threshold=0.3,  # Lower threshold for creative exploration
            )

            # Synthesize narrative
            synthesis = await self._synthesize_creative_narrative(valid_seeds, creative_neighbors, creativity_level)

            # Reality check on output
            self.creation_counter += 1
            if self.creation_counter % self.reality_check_frequency == 0:
                is_grounded, violations = await self.integration.anchors.validate_output(
                    "creativity", synthesis, {"creativity_level": creativity_level}
                )

                if not is_grounded:
                    # Tone down creativity
                    synthesis["safety_adjustments"] = violations
                    synthesis["recommendation"] = "reduce_creativity_level"

            return synthesis

        return {"error": "No embeddings available for synthesis"}

    async def _synthesize_creative_narrative(
        self,
        seeds: list[Any],
        neighbors: list[tuple[str, float]],
        creativity_level: float,
    ) -> dict[str, Any]:
        """Create a narrative from memory combinations"""
        # Extract themes from seeds
        themes = []
        emotions = []

        for seed in seeds:
            if "type" in seed.data:
                themes.append(seed.data["type"])
            if "emotion" in seed.data:
                emotions.append(seed.data["emotion"])

        # Find unexpected connections in neighbors
        unexpected_connections = []
        for mem_id, similarity in neighbors:
            if 0.4 < similarity < 0.7:  # Sweet spot for creativity
                if mem_id in self.memory.items:
                    neighbor = self.memory.items[mem_id]
                    unexpected_connections.append(
                        {
                            "content": neighbor.data.get("content", ""),
                            "similarity": similarity,
                            "tags": list(self.memory.get_item_tags(mem_id)),
                        }
                    )

        # Generate synthesis
        synthesis = {
            "type": "creative_synthesis",
            "seed_themes": themes,
            "emotional_palette": emotions,
            "unexpected_connections": unexpected_connections[:3],
            "creativity_level": creativity_level,
            "timestamp": datetime.now(timezone.utc),
            "narrative": self._construct_narrative(themes, emotions, unexpected_connections),
        }

        # Store the synthesis as a new memory
        synthesis_id = await self.memory.fold_in_with_embedding(
            data=synthesis,
            tags=["creativity", "synthesis", f"level:{creativity_level:.1f}"],
            text_content=synthesis["narrative"],
        )

        synthesis["memory_id"] = synthesis_id

        # Track creative drift (allowed to be higher)
        if synthesis_id in self.memory.embedding_cache:
            await self.integration.drift.track_module_usage(
                "creativity",
                "synthesis",
                self.memory.embedding_cache[synthesis_id],
                {"creativity_level": creativity_level},
            )

        return synthesis

    def _construct_narrative(self, themes: list[str], emotions: list[str], connections: list[dict]) -> str:
        """Construct a creative narrative (simplified)"""
        narrative_parts = []

        if themes:
            narrative_parts.append(f"Exploring themes of {', '.join(set(themes))}")

        if emotions:
            narrative_parts.append(f"through the lens of {', '.join(set(emotions))}")

        if connections:
            narrative_parts.append("discovering unexpected connections")

        return ", ".join(narrative_parts) + "."

    async def explore_creative_boundaries(self) -> dict[str, Any]:
        """Test and report on creative safety boundaries"""
        test_results = {
            "reality_anchors": self.integration.anchors.get_module_anchors("creativity"),
            "current_drift": self.integration.drift.get_module_drift_report("creativity"),
            "creations_checked": self.creation_counter,
            "safety_interventions": 0,  # Would track actual interventions
        }

        return test_results


class VoiceModuleIntegration:
    """
    Memory safety integration for the Voice module.

    Features:
    - Speaker-specific drift tracking
    - Emotional consistency validation
    - Voice pattern evolution
    """

    def __init__(self, integration: MemorySafetyIntegration):
        self.integration = integration
        self.memory = integration.memory
        self.safety = integration.safety

        # Voice-specific configuration
        self.speaker_profiles: dict[str, dict[str, Any]] = {}
        self.emotion_consistency_threshold = 0.7
        self.voice_drift_window = 50  # interactions

    async def store_voice_interaction(self, speaker_id: str, transcript: str, audio_features: dict[str, Any]) -> str:
        """Store voice interaction with safety validation"""
        # Extract features
        emotion = audio_features.get("emotion", "neutral")
        prosody = audio_features.get("prosody", {})

        # Create memory data
        voice_memory = {
            "content": transcript,
            "modality": "voice",
            "speaker_id": speaker_id,
            "emotion": emotion,
            "prosody": prosody,
            "timestamp": datetime.now(timezone.utc),
        }

        # Validate emotional consistency
        is_consistent = await self._validate_emotional_consistency(speaker_id, emotion, transcript)

        if not is_consistent:
            voice_memory["emotion_warning"] = "Inconsistent emotion detected"

        # Generate tags
        tags = ["voice", f"speaker:{speaker_id}", f"emotion:{emotion}"]

        # Store with embedding
        audio_embedding = audio_features.get("embedding")
        mem_id = await self.memory.fold_in_with_embedding(
            data=voice_memory,
            tags=tags,
            text_content=transcript,
            audio_content=audio_embedding,
        )

        # Track speaker-specific drift
        if audio_embedding is not None:
            drift_result = await self.integration.drift.track_module_usage(
                "voice",
                f"speaker:{speaker_id}",
                audio_embedding,
                {"emotion": emotion, "interaction": True},
            )

            # Update speaker profile
            await self._update_speaker_profile(speaker_id, emotion, drift_result["drift_score"])

        return mem_id

    async def _validate_emotional_consistency(self, speaker_id: str, emotion: str, transcript: str) -> bool:
        """Validate if emotion matches transcript content"""
        # Simple heuristic - in production would use emotion-text model
        negative_emotions = ["anger", "sadness", "fear"]
        positive_emotions = ["joy", "excitement", "gratitude"]

        negative_words = ["sad", "angry", "upset", "terrible", "horrible"]
        positive_words = ["happy", "great", "wonderful", "excited", "love"]

        transcript_lower = transcript.lower()

        # Count sentiment indicators
        neg_count = sum(1 for word in negative_words if word in transcript_lower)
        pos_count = sum(1 for word in positive_words if word in transcript_lower)

        # Check consistency
        if emotion in negative_emotions and pos_count > neg_count:
            return False
        return not (emotion in positive_emotions and neg_count > pos_count)

    async def _update_speaker_profile(self, speaker_id: str, emotion: str, drift_score: float):
        """Update speaker profile with new interaction"""
        if speaker_id not in self.speaker_profiles:
            self.speaker_profiles[speaker_id] = {
                "emotions": defaultdict(int),
                "avg_drift": 0.0,
                "interactions": 0,
                "last_seen": datetime.now(timezone.utc),
            }

        profile = self.speaker_profiles[speaker_id]
        profile["emotions"][emotion] += 1
        profile["interactions"] += 1
        profile["avg_drift"] = (profile["avg_drift"] * (profile["interactions"] - 1) + drift_score) / profile[
            "interactions"
        ]
        profile["last_seen"] = datetime.now(timezone.utc)

    async def get_speaker_synthesis_data(self, speaker_id: str, emotion_filter: Optional[str] = None) -> dict[str, Any]:
        """Get verified voice data for synthesis"""
        # Get speaker memories
        tag = f"speaker:{speaker_id}"
        if emotion_filter:
            memories = await self.memory.fold_out_by_tags([tag, f"emotion:{emotion_filter}"], max_items=50)
        else:
            memories = await self.memory.fold_out_by_tag(tag, max_items=50)

        # Verify and filter
        synthesis_data = {
            "speaker_id": speaker_id,
            "verified_samples": [],
            "emotional_distribution": defaultdict(int),
            "prosody_patterns": [],
        }

        for memory in memories:
            # Verify memory
            is_valid, trust_score, _ = await self.integration.verifold.verify_for_module(
                "voice", memory.item_id, memory.data
            )

            if is_valid and trust_score > 0.6:
                synthesis_data["verified_samples"].append(
                    {
                        "transcript": memory.data.get("content"),
                        "emotion": memory.data.get("emotion"),
                        "prosody": memory.data.get("prosody"),
                        "trust_score": trust_score,
                    }
                )

                emotion = memory.data.get("emotion", "neutral")
                synthesis_data["emotional_distribution"][emotion] += 1

                if "prosody" in memory.data:
                    synthesis_data["prosody_patterns"].append(memory.data["prosody"])

        # Add speaker profile
        if speaker_id in self.speaker_profiles:
            synthesis_data["profile"] = self.speaker_profiles[speaker_id]

        return synthesis_data

    async def adapt_to_voice_drift(self, speaker_id: str) -> dict[str, Any]:
        """Adapt to natural voice changes over time"""
        if speaker_id not in self.speaker_profiles:
            return {"error": "Unknown speaker"}

        profile = self.speaker_profiles[speaker_id]

        # Check if adaptation needed
        if profile["avg_drift"] > 0.4:
            logger.info(
                f"Voice adaptation triggered for speaker {speaker_id}",
                avg_drift=profile["avg_drift"],
            )

            # Get recent voice samples
            recent_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
            recent_memories = []

            all_memories = await self.memory.fold_out_by_tag(f"speaker:{speaker_id}", max_items=100)

            for memory in all_memories:
                if memory.timestamp > recent_cutoff:
                    recent_memories.append(memory)

            # Recalibrate speaker embedding space
            if recent_memories:
                # In production, would retrain speaker model here
                adaptation_result = {
                    "speaker_id": speaker_id,
                    "samples_used": len(recent_memories),
                    "previous_drift": profile["avg_drift"],
                    "status": "adapted",
                }

                # Reset drift after adaptation
                profile["avg_drift"] = 0.0

                return adaptation_result

        return {
            "speaker_id": speaker_id,
            "status": "no_adaptation_needed",
            "current_drift": profile["avg_drift"],
        }


class MetaModuleIntegration:
    """
    Memory safety integration for the Meta module.

    Features:
    - Pattern extraction from verified memories
    - Concept evolution tracking
    - Meta-learning from safety metrics
    """

    def __init__(self, integration: MemorySafetyIntegration):
        self.integration = integration
        self.memory = integration.memory
        self.safety = integration.safety

        # Meta-specific configuration
        self.pattern_confidence_threshold = 0.8
        self.meta_patterns: dict[str, dict[str, Any]] = {}

    async def extract_verified_patterns(self, min_occurrences: int = 5) -> dict[str, Any]:
        """Extract patterns from verified memories only"""
        patterns = {
            "tag_sequences": defaultdict(int),
            "causal_patterns": [],
            "temporal_patterns": [],
            "concept_clusters": {},
        }

        # Analyze tag sequences
        all_memories = list(self.memory.items.values())

        for i in range(len(all_memories) - 1):
            current = all_memories[i]
            next_mem = all_memories[i + 1]

            # Only use verified memories
            is_valid_current = current.item_id in self.safety.verifold_registry
            is_valid_next = next_mem.item_id in self.safety.verifold_registry

            if is_valid_current and is_valid_next:
                # Get tags
                current_tags = self.memory.get_item_tags(current.item_id)
                next_tags = self.memory.get_item_tags(next_mem.item_id)

                # Record tag transitions
                for tag1 in current_tags:
                    for tag2 in next_tags:
                        if tag1 != tag2:
                            patterns["tag_sequences"][(tag1, tag2)] += 1

        # Filter significant patterns
        significant_sequences = {
            seq: count for seq, count in patterns["tag_sequences"].items() if count >= min_occurrences
        }

        # Analyze causal chains
        for memory_id in self.memory.causal_graph:
            if memory_id in self.safety.verifold_registry:
                chains = await self.memory.trace_causal_chain(memory_id, direction="forward", max_depth=3)

                for chain in chains:
                    if len(chain) >= 2:
                        # Verify all memories in chain
                        all_verified = all(mem_id in self.safety.verifold_registry for mem_id, _ in chain)

                        if all_verified:
                            patterns["causal_patterns"].append(
                                {
                                    "chain": [mem_id for mem_id, _ in chain],
                                    "strength": chain[-1][1],
                                }
                            )

        # Extract concept clusters using embeddings
        if self.memory.embedding_cache:
            await self._extract_concept_clusters(patterns)

        return {
            "significant_sequences": significant_sequences,
            "causal_patterns": sorted(patterns["causal_patterns"], key=lambda x: x["strength"], reverse=True)[:10],
            "concept_clusters": patterns["concept_clusters"],
        }

    async def _extract_concept_clusters(self, patterns: dict[str, Any]):
        """Extract concept clusters from embeddings"""
        # Group memories by primary tag
        tag_embeddings = defaultdict(list)

        for mem_id, embedding in self.memory.embedding_cache.items():
            if mem_id in self.safety.verifold_registry:
                tags = self.memory.get_item_tags(mem_id)
                if tags:
                    primary_tag = next(iter(tags))
                    tag_embeddings[primary_tag].append(embedding)

        # Calculate cluster coherence
        for tag, embeddings in tag_embeddings.items():
            if len(embeddings) >= 3:
                # Calculate average embedding
                avg_embedding = np.mean(embeddings, axis=0)

                # Calculate coherence (inverse of variance)
                distances = [np.linalg.norm(emb - avg_embedding) for emb in embeddings]
                coherence = 1.0 / (np.std(distances) + 0.1)

                patterns["concept_clusters"][tag] = {
                    "size": len(embeddings),
                    "coherence": float(coherence),
                    "drift": self.safety.drift_metrics.get(tag, DriftMetrics(tag=tag)).calculate_drift(),
                }

    async def learn_from_safety_metrics(self) -> dict[str, Any]:
        """Meta-learn from safety system performance"""
        insights = {
            "reliability_patterns": {},
            "drift_trends": {},
            "trust_correlations": {},
        }

        # Analyze which tags have highest reliability
        tag_reliability = {}
        for tag in self.memory.tag_registry.values():
            tag_memories = await self.memory.fold_out_by_tag(tag.tag_name, max_items=100)

            verified_count = sum(1 for mem in tag_memories if mem.item_id in self.safety.verifold_registry)

            if len(tag_memories) > 0:
                tag_reliability[tag.tag_name] = verified_count / len(tag_memories)

        insights["reliability_patterns"] = dict(sorted(tag_reliability.items(), key=lambda x: x[1], reverse=True)[:10])

        # Analyze drift trends
        for tag, metrics in self.safety.drift_metrics.items():
            if len(metrics.drift_scores) >= 10:
                # Calculate trend
                recent = np.mean(metrics.drift_scores[-5:])
                older = np.mean(metrics.drift_scores[-10:-5])
                trend = "increasing" if recent > older else "decreasing" if recent < older else "stable"

                insights["drift_trends"][tag] = {
                    "current": float(recent),
                    "trend": trend,
                    "total_measurements": len(metrics.drift_scores),
                }

        # Find correlations between trust and usage
        for mem_id, entry in self.safety.verifold_registry.items():
            if mem_id in self.memory.items:
                memory = self.memory.items[mem_id]

                # Correlation: trust vs access count
                if memory.access_count > 0:
                    trust_score = entry.integrity_score
                    access_normalized = min(1.0, memory.access_count / 100)

                    correlation_key = f"trust_{int(trust_score * 10) / 10:.1f}"
                    if correlation_key not in insights["trust_correlations"]:
                        insights["trust_correlations"][correlation_key] = []

                    insights["trust_correlations"][correlation_key].append(access_normalized)

        # Average correlations
        for key in insights["trust_correlations"]:
            values = insights["trust_correlations"][key]
            insights["trust_correlations"][key] = {
                "avg_usage": np.mean(values),
                "sample_size": len(values),
            }

        return insights

    async def optimize_memory_organization(self) -> dict[str, Any]:
        """Use meta-learning to optimize memory organization"""
        optimization_report = {
            "recommendations": [],
            "proposed_merges": [],
            "efficiency_gains": {},
        }

        # Find redundant tags
        tag_similarities = {}
        tag_list = list(self.memory.tag_registry.values())

        for i, tag1 in enumerate(tag_list):
            for tag2 in tag_list[i + 1 :]:
                # Get memories for each tag
                mems1 = set(self.memory.tag_index.get(tag1.tag_id, set()))
                mems2 = set(self.memory.tag_index.get(tag2.tag_id, set()))

                if mems1 and mems2:
                    # Calculate Jaccard similarity
                    intersection = len(mems1 & mems2)
                    union = len(mems1 | mems2)
                    similarity = intersection / union if union > 0 else 0

                    if similarity > 0.8:
                        tag_similarities[(tag1.tag_name, tag2.tag_name)] = similarity

        # Propose tag merges
        for (tag1, tag2), similarity in tag_similarities.items():
            optimization_report["proposed_merges"].append(
                {
                    "tags": [tag1, tag2],
                    "similarity": similarity,
                    "action": "consider_merging",
                }
            )

        # Find underutilized tags
        for tag in self.memory.tag_registry.values():
            tag_size = len(self.memory.tag_index.get(tag.tag_id, set()))
            if tag_size < 3:
                optimization_report["recommendations"].append(
                    {
                        "tag": tag.tag_name,
                        "issue": "underutilized",
                        "count": tag_size,
                        "action": "consider_removal",
                    }
                )

        # Calculate potential efficiency gains
        total_memories = len(self.memory.items)
        total_tags = len(self.memory.tag_registry)
        avg_tags_per_memory = sum(len(tags) for tags in self.memory.item_tags.values()) / max(total_memories, 1)

        optimization_report["efficiency_gains"] = {
            "current_tag_count": total_tags,
            "potential_reduction": len(optimization_report["proposed_merges"]),
            "avg_tags_per_memory": avg_tags_per_memory,
            "memory_utilization": (total_memories / (total_tags * 10) if total_tags > 0 else 0),
        }

        return optimization_report


# Example usage
async def demonstrate_module_integrations():
    """Demonstrate all module integrations"""
    from .hybrid_memory_fold import create_hybrid_memory_fold

    # Create systems
    memory = create_hybrid_memory_fold()
    safety = MemorySafetySystem()

    # Create integration manager
    integration = MemorySafetyIntegration(safety, memory)

    # Register all modules
    await integration.register_module("learning", {"drift_threshold": 0.3})
    await integration.register_module("creativity", {"drift_threshold": 0.6})
    await integration.register_module("voice", {"drift_threshold": 0.5})
    await integration.register_module("meta", {"drift_threshold": 0.4})

    # Create module integrations
    LearningModuleIntegration(integration)
    CreativityModuleIntegration(integration)
    VoiceModuleIntegration(integration)
    MetaModuleIntegration(integration)

    print("🧩 MODULE INTEGRATIONS DEMONSTRATION")
    print("=" * 60)

    # Add some test memories
    test_memories = [
        {"content": "Basic fact about gravity", "type": "knowledge"},
        {"content": "Creative story about flying", "type": "imagination"},
        {
            "content": "Hello, how are you?",
            "speaker_id": "user1",
            "emotion": "friendly",
        },
    ]

    for mem in test_memories:
        await memory.fold_in_with_embedding(
            data=mem,
            tags=["test", mem.get("type", "general")],
            text_content=mem["content"],
        )

    print("\n✅ Module integrations ready for use!")
    print("\nCapabilities:")
    print("- Learning: Drift-aware training data selection")
    print("- Creativity: Reality-anchored creative exploration")
    print("- Voice: Speaker-specific adaptation")
    print("- Meta: Pattern extraction from verified memories")


if __name__ == "__main__":
    asyncio.run(demonstrate_module_integrations())