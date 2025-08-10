"""
Memory test fixtures and utilities for LUKHAS AGI test suite.

This module provides reusable test data generators and fixtures
for memory-related tests.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


def generate_test_memories(
    count: int = 10, base_timestamp: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Generate test memory samples with realistic data.

    Args:
        count: Number of memories to generate
        base_timestamp: Starting timestamp (defaults to now)

    Returns:
        List of memory dictionaries
    """
    if base_timestamp is None:
        base_timestamp = datetime.now(timezone.utc)

    memories = []
    emotions = ["joy", "sadness", "fear", "anger", "surprise", "trust", "anticipation"]
    glyphs = ["Λ", "Ψ", "Ω", "Δ", "Σ", "Θ", "Φ"]

    for i in range(count):
        # Create temporal spacing
        timestamp = base_timestamp - timedelta(hours=i * random.uniform(0.5, 2.0))

        # Generate memory content
        memory = {
            "id": f"mem_{i:04d}_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            "content": f"Memory content {i}: "
            + random.choice(
                [
                    "Observed pattern in data stream",
                    "Emotional resonance detected",
                    "Symbolic convergence noted",
                    "Causal relationship identified",
                    "Dream state transition recorded",
                    "Consciousness level fluctuation",
                    "Ethical boundary approached",
                ]
            ),
            "timestamp": timestamp.isoformat(),
            "importance_score": random.uniform(0.1, 1.0),
            "fold_eligible": random.random() > 0.3,  # 70% eligible
            "emotional_valence": random.uniform(-1.0, 1.0),
            "arousal": random.uniform(0.0, 1.0),
            "dominance": random.uniform(0.0, 1.0),
            "primary_emotion": random.choice(emotions),
            "emotion_vector": {
                emotion: (
                    random.uniform(0.0, 0.3)
                    if emotion
                    != (
                        memories[-1]["primary_emotion"]
                        if memories
                        else random.choice(emotions)
                    )
                    else random.uniform(0.5, 1.0)
                )
                for emotion in emotions
            },
            "symbolic_markers": random.sample(glyphs, k=random.randint(0, 3)),
            "causal_lineage": [f"event_{j}" for j in range(max(0, i - 3), i)],
            "metadata": {
                "source": random.choice(
                    ["perception", "introspection", "dream", "reasoning"]
                ),
                "category": random.choice(
                    ["episodic", "semantic", "procedural", "symbolic"]
                ),
                "confidence": random.uniform(0.5, 1.0),
                "processed": random.choice([True, False]),
                "tags": random.sample(
                    ["important", "recurring", "novel", "conflicting", "integrated"],
                    k=random.randint(0, 3),
                ),
            },
            "compression_eligible": i % 2 == 0,
            "fold_metadata": {
                "fold_level": 0,
                "last_accessed": timestamp.isoformat(),
                "access_count": random.randint(0, 10),
                "compression_ratio": None,
            },
        }

        memories.append(memory)

    return memories


def generate_fold_hierarchy(depth: int = 3, breadth: int = 3) -> Dict[str, Any]:
    """
    Generate a hierarchical fold structure for testing.

    Args:
        depth: Maximum depth of fold hierarchy
        breadth: Number of children per fold

    Returns:
        Hierarchical fold structure
    """

    def create_fold_node(
        level: int, index: int, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        fold_id = f"fold_L{level}_N{index}"

        node = {
            "fold_id": fold_id,
            "parent_id": parent_id,
            "level": level,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "compression_ratio": 0.5
            + (level * 0.1),  # Higher compression at deeper levels
            "symbolic_hash": f"hash_{fold_id}_{random.randint(1000, 9999)}",
            "content_summary": f"Fold at level {level}, containing compressed memories",
            "metadata": {
                "fold_count": 0,
                "total_memories": random.randint(10, 100),
                "convergence_score": random.uniform(0.5, 1.0),
            },
            "children": [],
        }

        if level < depth:
            for i in range(breadth):
                child = create_fold_node(level + 1, i, fold_id)
                node["children"].append(child)
                node["metadata"]["fold_count"] += 1

        return node

    root = create_fold_node(1, 0)
    return root


def generate_dream_sequence(length: int = 5) -> List[Dict[str, Any]]:
    """
    Generate a sequence of dream states for testing.

    Args:
        length: Number of dream states in sequence

    Returns:
        List of dream state dictionaries
    """
    phases = ["NREM1", "NREM2", "NREM3", "REM"]
    emotional_tones = [
        "neutral",
        "contemplative",
        "anxious",
        "euphoric",
        "melancholic",
        "curious",
    ]

    sequence = []
    for i in range(length):
        phase_index = i % len(phases)

        dream_state = {
            "sequence_index": i,
            "timestamp": (
                datetime.now(timezone.utc) + timedelta(minutes=i * 90)
            ).isoformat(),
            "phase": phases[phase_index],
            "depth": 0.3 + (0.2 * phase_index),  # Deeper in later phases
            "duration_minutes": random.uniform(10, 90),
            "symbolic_density": random.uniform(0.3, 1.0),
            "narrative_coherence": random.uniform(0.2, 0.9),
            "emotional_tone": random.choice(emotional_tones),
            "memory_consolidation_active": phase_index == 3,  # Active during REM
            "symbolic_elements": random.sample(
                ["Λ", "Ψ", "Ω", "Δ", "Σ"], k=random.randint(1, 4)
            ),
            "dream_content": {
                "themes": random.sample(
                    [
                        "transformation",
                        "journey",
                        "discovery",
                        "conflict",
                        "integration",
                        "creation",
                        "dissolution",
                    ],
                    k=random.randint(1, 3),
                ),
                "entities": [f"entity_{j}" for j in range(random.randint(1, 5))],
                "emotional_trajectory": [random.uniform(-1, 1) for _ in range(5)],
            },
            "introspective_insights": [
                f"Insight {j}: "
                + random.choice(
                    [
                        "Pattern emerging in symbolic space",
                        "Causal connection identified",
                        "Emotional resonance detected",
                        "Memory consolidation in progress",
                        "Contradiction resolved",
                    ]
                )
                for j in range(random.randint(1, 3))
            ],
            "drift_metrics": {
                "drift_score": random.uniform(0.1, 0.5),
                "stability": random.uniform(0.5, 0.9),
                "entropy": random.uniform(0.2, 0.7),
            },
        }

        sequence.append(dream_state)

    return sequence


def create_test_fold_with_memories(
    num_memories: int = 20, fold_level: int = 1
) -> Dict[str, Any]:
    """
    Create a complete test fold with embedded memories.

    Args:
        num_memories: Number of memories to include
        fold_level: Compression level of the fold

    Returns:
        Complete fold structure with memories
    """
    memories = generate_test_memories(num_memories)

    # Sort by timestamp
    memories.sort(key=lambda m: m["timestamp"])

    # Calculate fold statistics
    total_size = sum(len(json.dumps(m)) for m in memories)
    compressed_size = int(
        total_size * (0.7 - fold_level * 0.1)
    )  # More compression at higher levels

    fold = {
        "fold_id": f"test_fold_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "fold_level": fold_level,
        "memories": memories,
        "statistics": {
            "memory_count": len(memories),
            "original_size_bytes": total_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": compressed_size / total_size,
            "time_span_hours": (
                datetime.fromisoformat(memories[-1]["timestamp"])
                - datetime.fromisoformat(memories[0]["timestamp"])
            ).total_seconds()
            / 3600,
            "importance_mean": np.mean([m["importance_score"] for m in memories]),
            "importance_std": np.std([m["importance_score"] for m in memories]),
            "emotional_valence_mean": np.mean(
                [m["emotional_valence"] for m in memories]
            ),
            "symbolic_density": len([m for m in memories if m["symbolic_markers"]])
            / len(memories),
        },
        "symbolic_summary": {
            "dominant_glyphs": ["Λ", "Ψ"],  # Would be calculated from actual content
            "resonance_pattern": "ΛΨΩΛ",
            "symbolic_hash": f"hash_{random.randint(100000, 999999)}",
        },
        "causal_summary": {
            "root_events": list(
                set(m["causal_lineage"][0] for m in memories if m["causal_lineage"])
            ),
            "lineage_depth": max(len(m["causal_lineage"]) for m in memories),
            "convergence_points": ["event_5", "event_12"],  # Would be calculated
        },
    }

    return fold


def generate_symbolic_test_data() -> Dict[str, Any]:
    """Generate test data for symbolic processing tests."""
    return {
        "glyphs": {
            "primary": ["Λ", "Ψ", "Ω"],
            "secondary": ["Δ", "Σ", "Θ"],
            "tertiary": ["Φ", "Π", "Ξ"],
        },
        "resonance_patterns": [
            {"pattern": "ΛΨΩ", "strength": 0.9, "stability": 0.8},
            {"pattern": "ΩΛΨ", "strength": 0.7, "stability": 0.6},
            {"pattern": "ΨΩΛ", "strength": 0.5, "stability": 0.9},
        ],
        "symbolic_states": [
            {
                "state_id": "coherent",
                "glyphs_active": ["Λ", "Ψ", "Ω"],
                "resonance": 0.9,
                "entropy": 0.2,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "state_id": "transitional",
                "glyphs_active": ["Δ", "Λ"],
                "resonance": 0.5,
                "entropy": 0.5,
                "timestamp": (
                    datetime.now(timezone.utc) + timedelta(minutes=30)
                ).isoformat(),
            },
            {
                "state_id": "chaotic",
                "glyphs_active": ["Ξ", "Π", "Θ"],
                "resonance": 0.2,
                "entropy": 0.9,
                "timestamp": (
                    datetime.now(timezone.utc) + timedelta(hours=1)
                ).isoformat(),
            },
        ],
        "transformation_rules": [
            {"from": "Λ", "to": "Ψ", "condition": "high_resonance", "probability": 0.7},
            {"from": "Ψ", "to": "Ω", "condition": "low_entropy", "probability": 0.8},
            {"from": "Ω", "to": "Λ", "condition": "convergence", "probability": 0.6},
        ],
    }


def save_test_data(
    data: Any, filename: str, directory: str = "tests/test_data"
) -> Path:
    """
    Save test data to file for later use.

    Args:
        data: Data to save
        filename: Output filename
        directory: Output directory

    Returns:
        Path to saved file
    """
    output_dir = Path(directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    if filename.endswith(".json"):
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    elif filename.endswith(".jsonl"):
        with open(output_path, "w") as f:
            if isinstance(data, list):
                for item in data:
                    f.write(json.dumps(item, default=str) + "\n")
            else:
                f.write(json.dumps(data, default=str) + "\n")

    return output_path


def load_test_data(filename: str, directory: str = "tests/test_data") -> Any:
    """
    Load test data from file.

    Args:
        filename: Input filename
        directory: Input directory

    Returns:
        Loaded data
    """
    input_path = Path(directory) / filename

    if not input_path.exists():
        raise FileNotFoundError(f"Test data file not found: {input_path}")

    if filename.endswith(".json"):
        with open(input_path) as f:
            return json.load(f)
    elif filename.endswith(".jsonl"):
        data = []
        with open(input_path) as f:
            for line in f:
                data.append(json.loads(line))
        return data

    return None


# Validation helpers
def validate_memory_structure(memory: Dict[str, Any]) -> bool:
    """Validate that a memory has the required structure."""
    required_fields = ["id", "content", "timestamp", "importance_score"]
    return all(field in memory for field in required_fields)


def validate_fold_structure(fold: Dict[str, Any]) -> bool:
    """Validate that a fold has the required structure."""
    required_fields = ["fold_id", "created_at", "fold_level"]
    return all(field in fold for field in required_fields)
