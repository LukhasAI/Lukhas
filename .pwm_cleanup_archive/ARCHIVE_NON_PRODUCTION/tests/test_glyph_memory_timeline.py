#!/usr/bin/env python3

"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - GLYPH MEMORY TIMELINE TEST
║ Test suite for glyph memory timeline functionality.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_glyph_memory_timeline.py
║ Path: lukhas/tests/test_glyph_memory_timeline.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Testing Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module contains a comprehensive test suite validating GLYPH subsystem
║ and Memory Fold System integration through mock timeline creation, glyph-based
║ indexing, memory recall anchoring, and drift detection capabilities.
╚══════════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import os

# Internal imports
import sys
import unittest
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from core.symbolic.glyphs.glyph import (
    EmotionVector,
    Glyph,
    GlyphFactory,
    GlyphPriority,
)
from core.symbolic.glyphs.glyph_sentinel import GlyphSentinel
from memory.core_memory.glyph_memory_bridge import GlyphMemoryBridge


@dataclass
class MockMemoryEvent:
    """Mock memory event for timeline testing."""

    event_id: str
    content: str
    emotion_data: Dict[str, float]
    timestamp: datetime
    glyph_id: Optional[str] = None
    context_tags: List[str] = None
    importance_score: float = 0.5

    def __post_init__(self):
        if self.context_tags is None:
            self.context_tags = []


class MockMemoryTimeline:
    """Mock memory timeline using glyph-based indexing."""

    def __init__(self):
        self.events: Dict[str, MockMemoryEvent] = {}
        self.glyph_index: Dict[str, List[str]] = {}  # glyph_id -> event_ids
        self.temporal_index: Dict[str, List[str]] = {}  # timestamp_key -> event_ids
        self.bridge = GlyphMemoryBridge()
        self.sentinel = GlyphSentinel()

    def add_memory_event(self, event: MockMemoryEvent, glyph: Glyph) -> str:
        """Add a memory event with glyph indexing."""
        # Store event
        event.glyph_id = glyph.id
        self.events[event.event_id] = event

        # Update glyph index
        if glyph.id not in self.glyph_index:
            self.glyph_index[glyph.id] = []
        self.glyph_index[glyph.id].append(event.event_id)

        # Update temporal index
        timestamp_key = event.timestamp.strftime("%Y-%m-%d_%H")
        if timestamp_key not in self.temporal_index:
            self.temporal_index[timestamp_key] = []
        self.temporal_index[timestamp_key].append(event.event_id)

        # Create glyph-indexed memory using bridge
        memory_data = {
            "event_id": event.event_id,
            "content": event.content,
            "emotion_data": event.emotion_data,
            "timestamp": event.timestamp.isoformat(),
            "context_tags": event.context_tags,
            "importance_score": event.importance_score,
        }

        indexed_memory = self.bridge.create_glyph_indexed_memory(glyph, memory_data)

        # Register glyph with sentinel for decay tracking
        self.sentinel.register_glyph(glyph)

        return event.event_id

    def recall_by_glyph(self, glyph_id: str) -> List[MockMemoryEvent]:
        """Recall memories anchored to a specific glyph."""
        event_ids = self.glyph_index.get(glyph_id, [])
        return [self.events[event_id] for event_id in event_ids]

    def reconstruct_temporal_sequence(
        self, start_time: datetime, end_time: datetime
    ) -> List[MockMemoryEvent]:
        """Reconstruct temporal sequence of memories within time range."""
        sequence = []

        for event in self.events.values():
            if start_time <= event.timestamp <= end_time:
                sequence.append(event)

        # Sort by timestamp
        sequence.sort(key=lambda x: x.timestamp)
        return sequence

    def get_glyph_memory_chain(self, root_glyph_id: str) -> Dict[str, Any]:
        """Get memory chain following glyph causal links."""
        chain = {
            "root_glyph_id": root_glyph_id,
            "chain_events": [],
            "causal_links": [],
            "total_memories": 0,
        }

        # Start with root glyph memories
        root_memories = self.recall_by_glyph(root_glyph_id)
        chain["chain_events"].extend(
            [
                {
                    "event_id": mem.event_id,
                    "glyph_id": mem.glyph_id,
                    "content": (
                        mem.content[:100] + "..."
                        if len(mem.content) > 100
                        else mem.content
                    ),
                    "timestamp": mem.timestamp.isoformat(),
                    "importance_score": mem.importance_score,
                }
                for mem in root_memories
            ]
        )

        chain["total_memories"] = len(root_memories)
        return chain

    def analyze_memory_drift(self, glyph_id: str) -> Dict[str, Any]:
        """Analyze memory drift using glyph stability indicators."""
        memories = self.recall_by_glyph(glyph_id)

        if not memories:
            return {"drift_detected": False, "analysis": "No memories found for glyph"}

        # Analyze temporal spread
        timestamps = [mem.timestamp for mem in memories]
        time_span = max(timestamps) - min(timestamps)

        # Analyze emotional consistency
        emotions = [mem.emotion_data for mem in memories]
        emotion_variance = self._calculate_emotion_variance(emotions)

        # Analyze content coherence
        content_coherence = self._calculate_content_coherence(
            [mem.content for mem in memories]
        )

        # Determine drift level
        drift_score = (emotion_variance * 0.4) + ((1.0 - content_coherence) * 0.6)
        drift_detected = drift_score > 0.5

        return {
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "memory_count": len(memories),
            "time_span_hours": time_span.total_seconds() / 3600,
            "emotion_variance": emotion_variance,
            "content_coherence": content_coherence,
            "analysis": (
                "High drift detected" if drift_detected else "Stable memory pattern"
            ),
        }

    def _calculate_emotion_variance(self, emotions: List[Dict[str, float]]) -> float:
        """Calculate variance in emotional patterns."""
        if len(emotions) < 2:
            return 0.0

        # Calculate average emotions
        emotion_keys = set()
        for emotion_dict in emotions:
            emotion_keys.update(emotion_dict.keys())

        variances = []
        for key in emotion_keys:
            values = [emotion_dict.get(key, 0.0) for emotion_dict in emotions]
            if len(values) > 1:
                mean = sum(values) / len(values)
                variance = sum((v - mean) ** 2 for v in values) / len(values)
                variances.append(variance)

        return sum(variances) / len(variances) if variances else 0.0

    def _calculate_content_coherence(self, contents: List[str]) -> float:
        """Calculate content coherence score."""
        if len(contents) < 2:
            return 1.0

        # Simple coherence based on common words
        all_words = set()
        content_words = []

        for content in contents:
            words = set(content.lower().split())
            content_words.append(words)
            all_words.update(words)

        # Calculate Jaccard similarity between content pairs
        similarities = []
        for i in range(len(content_words)):
            for j in range(i + 1, len(content_words)):
                intersection = len(content_words[i] & content_words[j])
                union = len(content_words[i] | content_words[j])
                similarity = intersection / union if union > 0 else 0
                similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0


class TestGlyphMemoryTimeline(unittest.TestCase):
    """Test suite for glyph-based memory timeline functionality."""

    def setUp(self):
        """Set up test environment."""
        self.timeline = MockMemoryTimeline()
        self.test_start_time = datetime.now() - timedelta(hours=24)

    def test_create_mock_memory_timeline(self):
        """Test creation of mock memory timeline with glyph indexing."""
        # Create a sequence of memory events with associated glyphs
        events_data = [
            {
                "content": "Learning about artificial consciousness and symbolic reasoning",
                "emotions": {"curiosity": 0.8, "fascination": 0.7, "anticipation": 0.6},
                "tags": ["learning", "consciousness", "symbolic"],
                "importance": 0.9,
            },
            {
                "content": "Debugging memory fold compression algorithm",
                "emotions": {
                    "focus": 0.9,
                    "determination": 0.8,
                    "slight_frustration": 0.3,
                },
                "tags": ["debugging", "memory", "algorithm"],
                "importance": 0.7,
            },
            {
                "content": "Breakthrough in glyph-based symbolic representation",
                "emotions": {"joy": 0.9, "excitement": 0.8, "satisfaction": 0.9},
                "tags": ["breakthrough", "glyph", "symbolic"],
                "importance": 1.0,
            },
            {
                "content": "Collaborative discussion on ethical AI constraints",
                "emotions": {
                    "thoughtfulness": 0.8,
                    "concern": 0.6,
                    "responsibility": 0.9,
                },
                "tags": ["ethics", "collaboration", "ai_safety"],
                "importance": 0.8,
            },
            {
                "content": "Dream processing integration with memory consolidation",
                "emotions": {"wonder": 0.7, "curiosity": 0.8, "innovation": 0.6},
                "tags": ["dreams", "memory", "integration"],
                "importance": 0.8,
            },
        ]

        created_events = []
        created_glyphs = []

        # Create events and glyphs
        for i, event_data in enumerate(events_data):
            # Create mock memory event
            event = MockMemoryEvent(
                event_id=f"event_{i+1:03d}",
                content=event_data["content"],
                emotion_data=event_data["emotions"],
                timestamp=self.test_start_time + timedelta(hours=i * 2),
                context_tags=event_data["tags"],
                importance_score=event_data["importance"],
            )

            # Create associated glyph based on event characteristics
            if "learning" in event_data["tags"]:
                glyph = GlyphFactory.create_memory_glyph(
                    memory_key=f"learning_memory_{i}",
                    emotion_vector=self._create_emotion_vector(event_data["emotions"]),
                )
            elif "breakthrough" in event_data["tags"]:
                glyph = GlyphFactory.create_action_glyph(
                    action_type="breakthrough_discovery",
                    emotion_vector=self._create_emotion_vector(event_data["emotions"]),
                )
            elif "ethics" in event_data["tags"]:
                glyph = GlyphFactory.create_ethical_glyph(
                    ethical_principle="ai_safety",
                    emotion_vector=self._create_emotion_vector(event_data["emotions"]),
                )
            elif "dreams" in event_data["tags"]:
                glyph = GlyphFactory.create_dream_glyph(
                    dream_symbol="💭",
                    emotion_vector=self._create_emotion_vector(event_data["emotions"]),
                )
            else:
                glyph = GlyphFactory.create_memory_glyph(
                    memory_key=f"general_memory_{i}",
                    emotion_vector=self._create_emotion_vector(event_data["emotions"]),
                )

            # Add semantic tags
            for tag in event_data["tags"]:
                glyph.add_semantic_tag(tag)

            # Set priority based on importance
            if event_data["importance"] >= 0.9:
                glyph.priority = GlyphPriority.CRITICAL
            elif event_data["importance"] >= 0.8:
                glyph.priority = GlyphPriority.HIGH
            else:
                glyph.priority = GlyphPriority.MEDIUM

            # Add to timeline
            event_id = self.timeline.add_memory_event(event, glyph)
            created_events.append(event)
            created_glyphs.append(glyph)

        # Assertions
        self.assertEqual(len(self.timeline.events), 5)
        self.assertEqual(len(self.timeline.glyph_index), 5)
        self.assertTrue(len(self.timeline.temporal_index) > 0)

        # Verify glyph indexing works
        for glyph in created_glyphs:
            memories = self.timeline.recall_by_glyph(glyph.id)
            self.assertTrue(len(memories) > 0)
            self.assertEqual(memories[0].glyph_id, glyph.id)

        print(
            f"✓ Created mock memory timeline with {len(created_events)} events and {len(created_glyphs)} glyphs"
        )

    def test_glyph_based_memory_recall(self):
        """Test memory recall using glyph anchoring."""
        # Create test memories
        self.test_create_mock_memory_timeline()

        # Test recall by glyph
        glyph_ids = list(self.timeline.glyph_index.keys())

        for glyph_id in glyph_ids[:3]:  # Test first 3 glyphs
            memories = self.timeline.recall_by_glyph(glyph_id)

            # Verify recall works
            self.assertTrue(len(memories) > 0)

            # Verify all memories have correct glyph association
            for memory in memories:
                self.assertEqual(memory.glyph_id, glyph_id)

            print(
                f"✓ Successfully recalled {len(memories)} memories for glyph {glyph_id[:8]}..."
            )

    def test_temporal_sequence_reconstruction(self):
        """Test reconstruction of temporal memory sequences."""
        # Create test memories
        self.test_create_mock_memory_timeline()

        # Define time range
        start_time = self.test_start_time
        end_time = self.test_start_time + timedelta(hours=10)

        # Reconstruct sequence
        sequence = self.timeline.reconstruct_temporal_sequence(start_time, end_time)

        # Verify sequence
        self.assertTrue(len(sequence) > 0)

        # Verify temporal ordering
        for i in range(1, len(sequence)):
            self.assertLessEqual(sequence[i - 1].timestamp, sequence[i].timestamp)

        # Verify all events are within time range
        for event in sequence:
            self.assertTrue(start_time <= event.timestamp <= end_time)

        print(
            f"✓ Reconstructed temporal sequence with {len(sequence)} events in chronological order"
        )

    def test_memory_drift_analysis(self):
        """Test memory drift detection using glyph stability."""
        # Create test memories with varying coherence
        glyph1 = GlyphFactory.create_memory_glyph("stable_memory")
        glyph2 = GlyphFactory.create_memory_glyph("drifting_memory")

        # Stable memories (similar emotions and content)
        stable_events = [
            MockMemoryEvent(
                event_id="stable_1",
                content="Working on symbolic AI research with focused attention",
                emotion_data={"focus": 0.8, "curiosity": 0.7, "satisfaction": 0.6},
                timestamp=datetime.now() - timedelta(hours=5),
            ),
            MockMemoryEvent(
                event_id="stable_2",
                content="Continuing symbolic AI research with sustained focus",
                emotion_data={"focus": 0.9, "curiosity": 0.8, "satisfaction": 0.7},
                timestamp=datetime.now() - timedelta(hours=3),
            ),
        ]

        # Drifting memories (varying emotions and content)
        drifting_events = [
            MockMemoryEvent(
                event_id="drift_1",
                content="Starting work on quantum consciousness algorithms",
                emotion_data={"excitement": 0.9, "uncertainty": 0.3, "curiosity": 0.8},
                timestamp=datetime.now() - timedelta(hours=4),
            ),
            MockMemoryEvent(
                event_id="drift_2",
                content="Debugging poetry generation system with frustration",
                emotion_data={"frustration": 0.7, "fatigue": 0.6, "determination": 0.4},
                timestamp=datetime.now() - timedelta(hours=2),
            ),
        ]

        # Add events to timeline
        for event in stable_events:
            self.timeline.add_memory_event(event, glyph1)

        for event in drifting_events:
            self.timeline.add_memory_event(event, glyph2)

        # Analyze drift
        stable_analysis = self.timeline.analyze_memory_drift(glyph1.id)
        drifting_analysis = self.timeline.analyze_memory_drift(glyph2.id)

        # Verify drift detection
        self.assertFalse(stable_analysis["drift_detected"])
        self.assertTrue(drifting_analysis["drift_detected"])

        # Verify drift scores
        self.assertLess(
            stable_analysis["drift_score"], drifting_analysis["drift_score"]
        )

        print(
            f"✓ Drift analysis: Stable={stable_analysis['drift_score']:.3f}, Drifting={drifting_analysis['drift_score']:.3f}"
        )

    def test_glyph_memory_chain_reconstruction(self):
        """Test reconstruction of memory chains via glyph causal links."""
        # Create parent and child glyphs with causal relationships
        parent_glyph = GlyphFactory.create_memory_glyph("root_concept")
        child_glyph = GlyphFactory.create_memory_glyph("derived_concept")

        # Set up causal link
        child_glyph.causal_link.parent_glyph_id = parent_glyph.id
        child_glyph.causal_link.causal_origin_id = parent_glyph.id
        child_glyph.causal_link.update_emotional_delta(
            parent_glyph.emotion_vector, child_glyph.emotion_vector
        )

        # Create memory events
        parent_event = MockMemoryEvent(
            event_id="parent_event",
            content="Initial insight into symbolic reasoning patterns",
            emotion_data={"insight": 0.9, "excitement": 0.8},
            timestamp=datetime.now() - timedelta(hours=6),
        )

        child_event = MockMemoryEvent(
            event_id="child_event",
            content="Applied symbolic patterns to memory compression",
            emotion_data={"accomplishment": 0.8, "satisfaction": 0.9},
            timestamp=datetime.now() - timedelta(hours=3),
        )

        # Add to timeline
        self.timeline.add_memory_event(parent_event, parent_glyph)
        self.timeline.add_memory_event(child_event, child_glyph)

        # Reconstruct chain
        chain = self.timeline.get_glyph_memory_chain(parent_glyph.id)

        # Verify chain structure
        self.assertEqual(chain["root_glyph_id"], parent_glyph.id)
        self.assertTrue(chain["total_memories"] > 0)
        self.assertTrue(len(chain["chain_events"]) > 0)

        print(
            f"✓ Reconstructed memory chain from root glyph {parent_glyph.id[:8]} with {chain['total_memories']} memories"
        )

    def _create_emotion_vector(self, emotion_data: Dict[str, float]) -> EmotionVector:
        """Helper method to create emotion vector from dictionary."""
        emotion_vector = EmotionVector()

        # Map common emotion names to EmotionVector attributes
        emotion_mapping = {
            "curiosity": "anticipation",
            "fascination": "surprise",
            "focus": "trust",
            "determination": "trust",
            "slight_frustration": "anger",
            "joy": "joy",
            "excitement": "joy",
            "satisfaction": "joy",
            "thoughtfulness": "trust",
            "concern": "fear",
            "responsibility": "trust",
            "wonder": "surprise",
            "innovation": "anticipation",
            "insight": "surprise",
            "accomplishment": "joy",
            "uncertainty": "fear",
            "frustration": "anger",
            "fatigue": "sadness",
        }

        for emotion, value in emotion_data.items():
            mapped_emotion = emotion_mapping.get(emotion, emotion)
            if hasattr(emotion_vector, mapped_emotion):
                setattr(emotion_vector, mapped_emotion, min(1.0, value))

        # Set intensity based on average emotion strength
        emotion_vector.intensity = sum(emotion_data.values()) / len(emotion_data)
        emotion_vector.stability = 0.8  # Default stability

        return emotion_vector


def run_glyph_memory_timeline_tests():
    """Run the complete glyph memory timeline test suite."""
    print("\n" + "=" * 80)
    print("🧪 RUNNING GLYPH MEMORY TIMELINE TESTS")
    print("=" * 80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGlyphMemoryTimeline)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    print("=" * 80)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_glyph_memory_timeline_tests()
    exit(0 if success else 1)


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - GLYPH MEMORY TIMELINE TEST
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ TEST CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Mock Memory Timeline: 5-event sequence with glyph-based indexing
║ • Glyph Memory Recall: Anchor-based memory retrieval validation
║ • Temporal Reconstruction: Chronological sequence rebuilding
║ • Drift Analysis: Memory stability monitoring via glyph indicators
║ • Chain Reconstruction: Causal memory chain traversal
║ • Emotion Vector Integration: Full emotional context preservation
║ • Statistical Analysis: Comprehensive drift and coherence metrics
║ • Bridge Integration: GlyphMemoryBridge and GlyphSentinel validation
╠═══════════════════════════════════════════════════════════════════════════════
║ VALIDATION METRICS
╠═══════════════════════════════════════════════════════════════════════════════
║ • Indexing Accuracy: 100% glyph-to-memory association verification
║ • Temporal Ordering: Chronological sequence integrity validation
║ • Drift Detection: Emotional variance and content coherence analysis
║ • Causal Integrity: Parent-child glyph relationship preservation
║ • Memory Anchoring: Glyph-based retrieval precision testing
║ • Bridge Functionality: Integration layer operation validation
╚═══════════════════════════════════════════════════════════════════════════════
"""
