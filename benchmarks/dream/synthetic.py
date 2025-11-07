from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Any

# Canonical emotion keys for consistency
CANON_EMOTIONS = ["confidence", "curiosity", "joy", "fear", "anger", "sadness", "surprise", "trust"]

@dataclass
class SyntheticCase:
    """A synthetic test case for dream system evaluation."""
    case_id: str
    query_emotion: dict[str, float]
    snapshots: list[dict[str, Any]]
    expected_selection: str
    difficulty: str  # "easy", "medium", "hard", "adversarial"
    scenario: str   # Description of test scenario

class SyntheticGenerator:
    """Generates synthetic test cases for adversarial testing."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def _random_emotion(self, bias: dict[str, float] | None = None) -> dict[str, float]:
        """Generate random emotion vector with optional bias."""
        emotion = {}
        for key in CANON_EMOTIONS:
            if bias and key in bias:
                # Biased towards specific value
                base = bias[key]
                noise = self.rng.gauss(0, 0.1)
                value = max(0.0, min(1.0, base + noise))
            else:
                # Uniform random
                value = self.rng.uniform(0.0, 1.0)
            emotion[key] = round(value, 3)
        return emotion

    def _generate_snapshot(self, name: str, emotion: dict[str, float],
                         timestamp_base: float, alignment_hint: float | None = None) -> dict[str, Any]:
        """Generate a single snapshot."""
        # Add some noise to emotion if desired
        noisy_emotion = {}
        for key, value in emotion.items():
            noise = self.rng.gauss(0, 0.05)
            noisy_emotion[key] = max(0.0, min(1.0, value + noise))

        return {
            "name": name,
            "emotion": noisy_emotion,
            "timestamp": timestamp_base + self.rng.uniform(-10, 10),
            "content": f"Synthetic snapshot {name}",
            "metadata": {"synthetic": True}
        }

    def generate_easy_case(self, case_id: str) -> SyntheticCase:
        """Generate an easy test case with clear winner."""
        query_emotion = self._random_emotion()

        # Create perfect match
        perfect_match = self._generate_snapshot("perfect", query_emotion, 100.0)

        # Create clearly worse options
        worse_emotions = []
        for _ in range(3):
            # Flip some emotions to opposite values
            flipped = {}
            for key, value in query_emotion.items():
                if self.rng.random() < 0.5:
                    flipped[key] = 1.0 - value  # Opposite
                else:
                    flipped[key] = value * 0.3  # Much lower
            worse_emotions.append(flipped)

        snapshots = [perfect_match]
        for i, emotion in enumerate(worse_emotions):
            snapshots.append(self._generate_snapshot(f"worse_{i}", emotion, 100.0))

        self.rng.shuffle(snapshots)

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query_emotion,
            snapshots=snapshots,
            expected_selection="perfect",
            difficulty="easy",
            scenario="Clear winner with high alignment, others significantly worse"
        )

    def generate_medium_case(self, case_id: str) -> SyntheticCase:
        """Generate medium difficulty case with close competitors."""
        base_emotion = self._random_emotion()

        # Create multiple good candidates with slight differences
        snapshots = []
        best_name = None
        best_similarity = 0.0

        for i in range(4):
            # Create variations of base emotion
            variant = {}
            similarity = 0.0
            for key, value in base_emotion.items():
                if self.rng.random() < 0.3:  # 30% chance to modify
                    noise = self.rng.gauss(0, 0.15)
                    variant[key] = max(0.0, min(1.0, value + noise))
                else:
                    variant[key] = value

            # Calculate rough similarity for expected result
            for key in CANON_EMOTIONS:
                similarity += 1.0 - abs(base_emotion[key] - variant[key])

            name = f"candidate_{i}"
            if similarity > best_similarity:
                best_similarity = similarity
                best_name = name

            snapshots.append(self._generate_snapshot(name, variant, 100.0))

        return SyntheticCase(
            case_id=case_id,
            query_emotion=base_emotion,
            snapshots=snapshots,
            expected_selection=best_name,
            difficulty="medium",
            scenario="Multiple good candidates, requiring careful comparison"
        )

    def generate_hard_case(self, case_id: str) -> SyntheticCase:
        """Generate hard case with temporal complexity."""
        query_emotion = self._random_emotion()

        # Create temporally complex scenario
        snapshots = []

        # Recent but mediocre match
        recent_emotion = {}
        for key, value in query_emotion.items():
            recent_emotion[key] = value * 0.7  # Decent but not great

        recent = self._generate_snapshot("recent_mediocre", recent_emotion, 200.0)

        # Older but excellent match
        old_emotion = {}
        for key, value in query_emotion.items():
            noise = self.rng.gauss(0, 0.03)  # Very close
            old_emotion[key] = max(0.0, min(1.0, value + noise))

        old = self._generate_snapshot("old_excellent", old_emotion, 50.0)

        # Medium age, medium quality
        medium_emotion = {}
        for key, value in query_emotion.items():
            medium_emotion[key] = value * 0.8

        medium = self._generate_snapshot("medium_okay", medium_emotion, 125.0)

        snapshots = [recent, old, medium]

        # Expected depends on temporal weighting settings
        # Default: old_excellent should win due to higher alignment
        expected = "old_excellent"

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query_emotion,
            snapshots=snapshots,
            expected_selection=expected,
            difficulty="hard",
            scenario="Temporal tradeoff: recent mediocre vs old excellent vs medium okay"
        )

    def generate_adversarial_case(self, case_id: str) -> SyntheticCase:
        """Generate adversarial case designed to stress system."""
        # Choose adversarial scenario
        scenarios = [
            self._adversarial_extreme_values,
            self._adversarial_all_zeros,
            self._adversarial_all_ones,
            self._adversarial_identical_emotions,
            self._adversarial_sparse_emotions
        ]

        scenario_func = self.rng.choice(scenarios)
        return scenario_func(case_id)

    def _adversarial_extreme_values(self, case_id: str) -> SyntheticCase:
        """Adversarial: extreme emotion values."""
        # Query with extreme values
        query = {}
        for key in CANON_EMOTIONS:
            query[key] = self.rng.choice([0.0, 1.0])

        # Snapshots with various extreme patterns
        snapshots = []
        snapshots.append(self._generate_snapshot("all_max", dict.fromkeys(CANON_EMOTIONS, 1.0), 100.0))
        snapshots.append(self._generate_snapshot("all_min", dict.fromkeys(CANON_EMOTIONS, 0.0), 100.0))
        snapshots.append(self._generate_snapshot("alternating",
                                                {k: 1.0 if i % 2 == 0 else 0.0 for i, k in enumerate(CANON_EMOTIONS)}, 100.0))

        # Best match is exact copy
        snapshots.append(self._generate_snapshot("exact_match", query.copy(), 100.0))

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query,
            snapshots=snapshots,
            expected_selection="exact_match",
            difficulty="adversarial",
            scenario="Extreme emotion values (0.0 or 1.0 only)"
        )

    def _adversarial_all_zeros(self, case_id: str) -> SyntheticCase:
        """Adversarial: all emotions zero."""
        query = dict.fromkeys(CANON_EMOTIONS, 0.0)

        snapshots = []
        snapshots.append(self._generate_snapshot("also_zeros", query.copy(), 100.0))
        snapshots.append(self._generate_snapshot("small_values", dict.fromkeys(CANON_EMOTIONS, 0.1), 100.0))
        snapshots.append(self._generate_snapshot("large_values", dict.fromkeys(CANON_EMOTIONS, 0.9), 100.0))

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query,
            snapshots=snapshots,
            expected_selection="also_zeros",
            difficulty="adversarial",
            scenario="All emotions zero - testing edge case handling"
        )

    def _adversarial_all_ones(self, case_id: str) -> SyntheticCase:
        """Adversarial: all emotions maxed."""
        query = dict.fromkeys(CANON_EMOTIONS, 1.0)

        snapshots = []
        snapshots.append(self._generate_snapshot("also_ones", query.copy(), 100.0))
        snapshots.append(self._generate_snapshot("mostly_ones", dict.fromkeys(CANON_EMOTIONS, 0.95), 100.0))
        snapshots.append(self._generate_snapshot("half_values", dict.fromkeys(CANON_EMOTIONS, 0.5), 100.0))

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query,
            snapshots=snapshots,
            expected_selection="also_ones",
            difficulty="adversarial",
            scenario="All emotions maxed - testing saturation handling"
        )

    def _adversarial_identical_emotions(self, case_id: str) -> SyntheticCase:
        """Adversarial: identical emotions, different timestamps."""
        base_emotion = self._random_emotion()

        snapshots = []
        for i in range(4):
            # Identical emotions, different timestamps
            timestamp = 100.0 + i * 20.0  # 100, 120, 140, 160
            snapshots.append(self._generate_snapshot(f"identical_{i}", base_emotion.copy(), timestamp))

        # Most recent should win due to tiebreaking
        expected = "identical_3"

        return SyntheticCase(
            case_id=case_id,
            query_emotion=base_emotion,
            snapshots=snapshots,
            expected_selection=expected,
            difficulty="adversarial",
            scenario="Identical emotions - testing tiebreaking logic"
        )

    def _adversarial_sparse_emotions(self, case_id: str) -> SyntheticCase:
        """Adversarial: very sparse emotion vectors."""
        # Query with only 1-2 non-zero emotions
        query = dict.fromkeys(CANON_EMOTIONS, 0.0)
        active_emotions = self.rng.sample(CANON_EMOTIONS, 2)
        for key in active_emotions:
            query[key] = self.rng.uniform(0.5, 1.0)

        snapshots = []

        # Perfect sparse match
        snapshots.append(self._generate_snapshot("sparse_match", query.copy(), 100.0))

        # Dense but lower values
        dense = dict.fromkeys(CANON_EMOTIONS, 0.3)
        snapshots.append(self._generate_snapshot("dense_low", dense, 100.0))

        # Different sparse pattern
        different_sparse = dict.fromkeys(CANON_EMOTIONS, 0.0)
        other_emotions = [k for k in CANON_EMOTIONS if k not in active_emotions]
        for key in self.rng.sample(other_emotions, 2):
            different_sparse[key] = self.rng.uniform(0.5, 1.0)
        snapshots.append(self._generate_snapshot("different_sparse", different_sparse, 100.0))

        return SyntheticCase(
            case_id=case_id,
            query_emotion=query,
            snapshots=snapshots,
            expected_selection="sparse_match",
            difficulty="adversarial",
            scenario="Sparse emotion vectors - testing alignment with few active dimensions"
        )

def generate_synthetic_corpus(count: int = 50, seed: int = 42, out_path: str = "benchmarks/dream/synthetic_corpus.json") -> str:
    """Generate a synthetic test corpus."""
    generator = SyntheticGenerator(seed)

    cases = []

    # Distribution: 40% easy, 30% medium, 20% hard, 10% adversarial
    easy_count = int(count * 0.4)
    medium_count = int(count * 0.3)
    hard_count = int(count * 0.2)
    adversarial_count = count - easy_count - medium_count - hard_count

    # Generate cases
    case_num = 1

    for _ in range(easy_count):
        cases.append(generator.generate_easy_case(f"syn_easy_{case_num:03d}"))
        case_num += 1

    for _ in range(medium_count):
        cases.append(generator.generate_medium_case(f"syn_medium_{case_num:03d}"))
        case_num += 1

    for _ in range(hard_count):
        cases.append(generator.generate_hard_case(f"syn_hard_{case_num:03d}"))
        case_num += 1

    for _ in range(adversarial_count):
        cases.append(generator.generate_adversarial_case(f"syn_adversarial_{case_num:03d}"))
        case_num += 1

    # Convert to JSON-serializable format
    corpus_data = []
    for case in cases:
        corpus_data.append({
            "case_id": case.case_id,
            "query_emotion": case.query_emotion,
            "snapshots": case.snapshots,
            "expected_selection": case.expected_selection,
            "difficulty": case.difficulty,
            "scenario": case.scenario
        })

    # Save corpus
    with open(out_path, "w") as f:
        json.dump(corpus_data, f, indent=2)

    print(f"Generated {len(cases)} synthetic test cases:")
    print(f"  Easy: {easy_count}")
    print(f"  Medium: {medium_count}")
    print(f"  Hard: {hard_count}")
    print(f"  Adversarial: {adversarial_count}")
    print(f"  Saved to: {out_path}")

    return out_path

if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    out_path = sys.argv[3] if len(sys.argv) > 3 else "benchmarks/dream/synthetic_corpus.json"

    generate_synthetic_corpus(count, seed, out_path)
