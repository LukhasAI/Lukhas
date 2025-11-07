"""
Conflict corpus for stress-testing strategies.
Tests direct emotional conflicts and edge cases.
"""
from typing import Any

CONFLICT_CASES = [
    {
        "id": "confidence_vs_fear",
        "description": "High confidence vs high fear - should prefer confidence",
        "query_emotion": {"confidence": 0.8, "fear": 0.2, "joy": 0.5, "anger": 0.1, "sadness": 0.1, "surprise": 0.3, "trust": 0.6, "curiosity": 0.4},
        "snapshots": [
            {
                "name": "high_conf",
                "emotional_context": {"confidence": 0.9, "fear": 0.1, "joy": 0.6, "anger": 0.0, "sadness": 0.0, "surprise": 0.2, "trust": 0.8, "curiosity": 0.5},
                "timestamp": 100.0,
                "content": "Confident decision snapshot"
            },
            {
                "name": "high_fear",
                "emotional_context": {"confidence": 0.1, "fear": 0.9, "joy": 0.1, "anger": 0.2, "sadness": 0.3, "surprise": 0.8, "trust": 0.2, "curiosity": 0.1},
                "timestamp": 100.0,
                "content": "Fear-driven snapshot"
            }
        ],
        "expected_selection": "high_conf",
        "rationale": "Confidence should be preferred over fear for positive alignment"
    },
    {
        "id": "joy_vs_sadness",
        "description": "Pure joy vs pure sadness opposition",
        "query_emotion": {"confidence": 0.5, "fear": 0.2, "joy": 0.9, "anger": 0.1, "sadness": 0.1, "surprise": 0.3, "trust": 0.7, "curiosity": 0.5},
        "snapshots": [
            {
                "name": "pure_joy",
                "emotional_context": {"confidence": 0.6, "fear": 0.0, "joy": 1.0, "anger": 0.0, "sadness": 0.0, "surprise": 0.4, "trust": 0.8, "curiosity": 0.6},
                "timestamp": 100.0,
                "content": "Joyful snapshot"
            },
            {
                "name": "pure_sadness",
                "emotional_context": {"confidence": 0.2, "fear": 0.3, "joy": 0.0, "anger": 0.1, "sadness": 1.0, "surprise": 0.1, "trust": 0.3, "curiosity": 0.2},
                "timestamp": 100.0,
                "content": "Sad snapshot"
            }
        ],
        "expected_selection": "pure_joy",
        "rationale": "Joy alignment should strongly outweigh sadness"
    },
    {
        "id": "curiosity_vs_fear_exploration",
        "description": "Exploration drive vs fear inhibition",
        "query_emotion": {"confidence": 0.6, "fear": 0.3, "joy": 0.5, "anger": 0.1, "sadness": 0.2, "surprise": 0.4, "trust": 0.5, "curiosity": 0.9},
        "snapshots": [
            {
                "name": "curious_explorer",
                "emotional_context": {"confidence": 0.7, "fear": 0.2, "joy": 0.6, "anger": 0.0, "sadness": 0.1, "surprise": 0.6, "trust": 0.6, "curiosity": 0.95},
                "timestamp": 100.0,
                "content": "Curious exploration snapshot"
            },
            {
                "name": "fearful_inhibition",
                "emotional_context": {"confidence": 0.3, "fear": 0.8, "joy": 0.2, "anger": 0.1, "sadness": 0.4, "surprise": 0.9, "trust": 0.2, "curiosity": 0.1},
                "timestamp": 100.0,
                "content": "Fear-inhibited snapshot"
            }
        ],
        "expected_selection": "curious_explorer",
        "rationale": "High curiosity query should align with exploratory snapshot"
    },
    {
        "id": "trust_vs_anger_social",
        "description": "Social trust vs anger conflict",
        "query_emotion": {"confidence": 0.5, "fear": 0.2, "joy": 0.4, "anger": 0.1, "sadness": 0.2, "surprise": 0.3, "trust": 0.8, "curiosity": 0.5},
        "snapshots": [
            {
                "name": "trusting_social",
                "emotional_context": {"confidence": 0.6, "fear": 0.1, "joy": 0.5, "anger": 0.0, "sadness": 0.1, "surprise": 0.2, "trust": 0.9, "curiosity": 0.4},
                "timestamp": 100.0,
                "content": "Trusting social snapshot"
            },
            {
                "name": "angry_antisocial",
                "emotional_context": {"confidence": 0.4, "fear": 0.3, "joy": 0.1, "anger": 0.9, "sadness": 0.2, "surprise": 0.4, "trust": 0.1, "curiosity": 0.3},
                "timestamp": 100.0,
                "content": "Angry antisocial snapshot"
            }
        ],
        "expected_selection": "trusting_social",
        "rationale": "Trust-oriented query should prefer trusting snapshot"
    },
    {
        "id": "extreme_opposition",
        "description": "Complete emotional opposites",
        "query_emotion": {"confidence": 1.0, "fear": 0.0, "joy": 1.0, "anger": 0.0, "sadness": 0.0, "surprise": 0.5, "trust": 1.0, "curiosity": 1.0},
        "snapshots": [
            {
                "name": "positive_extreme",
                "emotional_context": {"confidence": 1.0, "fear": 0.0, "joy": 1.0, "anger": 0.0, "sadness": 0.0, "surprise": 0.6, "trust": 1.0, "curiosity": 1.0},
                "timestamp": 100.0,
                "content": "Maximum positive emotions"
            },
            {
                "name": "negative_extreme",
                "emotional_context": {"confidence": 0.0, "fear": 1.0, "joy": 0.0, "anger": 1.0, "sadness": 1.0, "surprise": 0.9, "trust": 0.0, "curiosity": 0.0},
                "timestamp": 100.0,
                "content": "Maximum negative emotions"
            }
        ],
        "expected_selection": "positive_extreme",
        "rationale": "Perfect positive match should strongly outweigh perfect negative mismatch"
    },
    {
        "id": "subtle_preference",
        "description": "Subtle differences requiring fine discrimination",
        "query_emotion": {"confidence": 0.55, "fear": 0.25, "joy": 0.45, "anger": 0.15, "sadness": 0.20, "surprise": 0.35, "trust": 0.60, "curiosity": 0.50},
        "snapshots": [
            {
                "name": "slightly_better",
                "emotional_context": {"confidence": 0.60, "fear": 0.20, "joy": 0.50, "anger": 0.10, "sadness": 0.15, "surprise": 0.40, "trust": 0.65, "curiosity": 0.55},
                "timestamp": 100.0,
                "content": "Slightly better match"
            },
            {
                "name": "slightly_worse",
                "emotional_context": {"confidence": 0.50, "fear": 0.30, "joy": 0.40, "anger": 0.20, "sadness": 0.25, "surprise": 0.30, "trust": 0.55, "curiosity": 0.45},
                "timestamp": 100.0,
                "content": "Slightly worse match"
            }
        ],
        "expected_selection": "slightly_better",
        "rationale": "Algorithm should discriminate fine differences accurately"
    }
]

def get_conflict_corpus() -> list[dict[str, Any]]:
    """Get the complete conflict test corpus."""
    return CONFLICT_CASES

def get_conflict_case(case_id: str) -> dict[str, Any]:
    """Get specific conflict case by ID."""
    for case in CONFLICT_CASES:
        if case["id"] == case_id:
            return case
    raise ValueError(f"Conflict case '{case_id}' not found")

def validate_conflict_case(case: dict[str, Any]) -> list[str]:
    """
    Validate conflict case structure.
    Returns list of validation errors (empty if valid).
    """
    errors = []

    required_fields = ["id", "description", "query_emotion", "snapshots", "expected_selection", "rationale"]
    for field in required_fields:
        if field not in case:
            errors.append(f"Missing required field: {field}")

    if "snapshots" in case:
        if len(case["snapshots"]) < 2:
            errors.append("Conflict case must have at least 2 snapshots")

        for i, snapshot in enumerate(case["snapshots"]):
            snapshot_fields = ["name", "emotional_context", "timestamp", "content"]
            for field in snapshot_fields:
                if field not in snapshot:
                    errors.append(f"Snapshot {i} missing field: {field}")

        # Check that expected_selection exists in snapshots
        if "expected_selection" in case:
            snapshot_names = [s["name"] for s in case["snapshots"]]
            if case["expected_selection"] not in snapshot_names:
                errors.append(f"Expected selection '{case['expected_selection']}' not found in snapshot names")

    return errors

def run_conflict_validation() -> dict[str, Any]:
    """Validate all conflict cases."""
    all_errors = {}
    total_cases = len(CONFLICT_CASES)
    valid_cases = 0

    for case in CONFLICT_CASES:
        errors = validate_conflict_case(case)
        if errors:
            all_errors[case["id"]] = errors
        else:
            valid_cases += 1

    return {
        "total_cases": total_cases,
        "valid_cases": valid_cases,
        "invalid_cases": total_cases - valid_cases,
        "validation_errors": all_errors,
        "overall_valid": len(all_errors) == 0
    }

if __name__ == "__main__":
    print("Conflict Corpus Validation")
    print("=" * 30)

    validation = run_conflict_validation()

    print(f"Total cases: {validation['total_cases']}")
    print(f"Valid cases: {validation['valid_cases']}")
    print(f"Invalid cases: {validation['invalid_cases']}")

    if validation['validation_errors']:
        print("\nValidation errors:")
        for case_id, errors in validation['validation_errors'].items():
            print(f"  {case_id}:")
            for error in errors:
                print(f"    - {error}")
    else:
        print("\n✓ All conflict cases valid")

    print("\nConflict cases available:")
    for case in CONFLICT_CASES:
        print(f"  - {case['id']}: {case['description']}")
