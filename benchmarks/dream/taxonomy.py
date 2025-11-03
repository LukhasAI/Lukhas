from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class ErrorType(Enum):
    """Classification of dream system errors."""
    NO_SNAPSHOTS = "no_snapshots"
    ALL_FILTERED = "all_filtered_stale"
    LOW_ALIGNMENT = "low_alignment_scores"
    HIGH_DRIFT = "high_drift_detected"
    TIMEOUT = "selection_timeout"
    EMOTION_INVALID = "emotion_validation_failed"
    STRATEGY_ERROR = "strategy_execution_failed"
    DETERMINISM_VIOLATION = "determinism_violation"
    MEMORY_EXHAUSTED = "memory_exhausted"
    CONFIG_INVALID = "invalid_configuration"

class Severity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"    # System unusable
    HIGH = "high"           # Major functionality impacted
    MEDIUM = "medium"       # Minor functionality impacted
    LOW = "low"            # Cosmetic or edge case

@dataclass
class ErrorPattern:
    """Defines an error detection pattern."""
    error_type: ErrorType
    severity: Severity
    symptoms: List[str]
    detection_rules: Dict[str, Any]
    mitigation: str
    expected_frequency: float  # 0.0 - 1.0

# Define error taxonomy
ERROR_PATTERNS = [
    ErrorPattern(
        error_type=ErrorType.NO_SNAPSHOTS,
        severity=Severity.CRITICAL,
        symptoms=["empty snapshot list", "no candidates available"],
        detection_rules={
            "snapshot_count": 0,
            "error_contains": ["no snapshots", "empty list"]
        },
        mitigation="Check memory subsystem, verify snapshot generation pipeline",
        expected_frequency=0.001
    ),
    ErrorPattern(
        error_type=ErrorType.ALL_FILTERED,
        severity=Severity.HIGH,
        symptoms=["all snapshots filtered as stale", "fallback to original list"],
        detection_rules={
            "filtered_count": 0,
            "original_count": ">0",
            "staleness_filtering": True
        },
        mitigation="Adjust MAX_AGE setting or check timestamp accuracy",
        expected_frequency=0.02
    ),
    ErrorPattern(
        error_type=ErrorType.LOW_ALIGNMENT,
        severity=Severity.MEDIUM,
        symptoms=["alignment scores below threshold", "poor emotional matching"],
        detection_rules={
            "max_alignment": "<0.3",
            "avg_alignment": "<0.2"
        },
        mitigation="Review emotion normalization, consider strategy tuning",
        expected_frequency=0.05
    ),
    ErrorPattern(
        error_type=ErrorType.HIGH_DRIFT,
        severity=Severity.MEDIUM,
        symptoms=["high drift values", "temporal instability"],
        detection_rules={
            "min_drift": ">0.7",
            "avg_drift": ">0.5"
        },
        mitigation="Check temporal weighting, verify system stability",
        expected_frequency=0.03
    ),
    ErrorPattern(
        error_type=ErrorType.TIMEOUT,
        severity=Severity.HIGH,
        symptoms=["selection timeout", "processing time exceeded"],
        detection_rules={
            "selection_time_ms": ">1000",
            "error_contains": ["timeout", "exceeded"]
        },
        mitigation="Optimize alignment strategies, reduce snapshot volume",
        expected_frequency=0.001
    ),
    ErrorPattern(
        error_type=ErrorType.EMOTION_INVALID,
        severity=Severity.MEDIUM,
        symptoms=["emotion validation failed", "invalid emotion values"],
        detection_rules={
            "emotion_errors": ">0",
            "error_contains": ["emotion", "validation", "invalid"]
        },
        mitigation="Check emotion input format, verify normalization",
        expected_frequency=0.01
    ),
    ErrorPattern(
        error_type=ErrorType.STRATEGY_ERROR,
        severity=Severity.HIGH,
        symptoms=["strategy execution failed", "alignment calculation error"],
        detection_rules={
            "strategy_errors": ">0",
            "error_contains": ["strategy", "alignment", "calculation"]
        },
        mitigation="Review strategy implementation, check input validation",
        expected_frequency=0.005
    ),
    ErrorPattern(
        error_type=ErrorType.DETERMINISM_VIOLATION,
        severity=Severity.CRITICAL,
        symptoms=["non-deterministic results", "different outputs same input"],
        detection_rules={
            "determinism_check": False,
            "seed_consistency": False
        },
        mitigation="Check PYTHONHASHSEED, verify stable sorting, audit randomness",
        expected_frequency=0.001
    ),
    ErrorPattern(
        error_type=ErrorType.MEMORY_EXHAUSTED,
        severity=Severity.CRITICAL,
        symptoms=["out of memory", "memory allocation failed"],
        detection_rules={
            "memory_usage_mb": ">1000",
            "error_contains": ["memory", "allocation", "OOM"]
        },
        mitigation="Reduce snapshot count, optimize memory usage, add pagination",
        expected_frequency=0.002
    ),
    ErrorPattern(
        error_type=ErrorType.CONFIG_INVALID,
        severity=Severity.HIGH,
        symptoms=["invalid configuration", "parameter out of range"],
        detection_rules={
            "config_errors": ">0",
            "error_contains": ["config", "parameter", "invalid", "range"]
        },
        mitigation="Validate configuration parameters, use safe defaults",
        expected_frequency=0.01
    )
]

class ErrorClassifier:
    """Classifies errors based on symptoms and patterns."""

    def __init__(self):
        self.patterns = {p.error_type: p for p in ERROR_PATTERNS}

    def classify_error(self, error_data: Dict[str, Any]) -> ErrorPattern | None:
        """Classify an error based on available data."""
        for pattern in ERROR_PATTERNS:
            if self._matches_pattern(error_data, pattern):
                return pattern
        return None

    def _matches_pattern(self, error_data: Dict[str, Any], pattern: ErrorPattern) -> bool:
        """Check if error data matches a pattern."""
        rules = pattern.detection_rules

        # Check error message content
        if "error_contains" in rules:
            error_msg = str(error_data.get("error", "")).lower()
            for term in rules["error_contains"]:
                if term.lower() in error_msg:
                    return True

        # Check numeric conditions
        for key, condition in rules.items():
            if key == "error_contains":
                continue

            if key not in error_data:
                continue

            value = error_data[key]

            if isinstance(condition, str) and condition.startswith(">"):
                threshold = float(condition[1:])
                if float(value) <= threshold:
                    return False
            elif isinstance(condition, str) and condition.startswith("<"):
                threshold = float(condition[1:])
                if float(value) >= threshold:
                    return False
            elif condition != value:
                return False

        return True

def analyze_error_distribution(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze error distribution in benchmark results."""
    classifier = ErrorClassifier()

    error_counts = {et.value: 0 for et in ErrorType}
    severity_counts = {s.value: 0 for s in Severity}
    total_errors = 0
    unclassified_errors = 0

    for result in results:
        if "error" in result or result.get("accuracy", 1.0) < 0.5:
            total_errors += 1

            # Create error data for classification
            error_data = {
                "error": result.get("error", ""),
                "accuracy": result.get("accuracy", 0.0),
                "snapshot_count": result.get("snapshot_count", 0),
                "selection_time_ms": result.get("selection_time_ms", 0.0),
                "max_alignment": result.get("max_alignment", 0.0),
                "avg_alignment": result.get("avg_alignment", 0.0),
                "min_drift": result.get("min_drift", 0.0),
                "avg_drift": result.get("avg_drift", 0.0),
            }

            pattern = classifier.classify_error(error_data)
            if pattern:
                error_counts[pattern.error_type.value] += 1
                severity_counts[pattern.severity.value] += 1
            else:
                unclassified_errors += 1

    return {
        "total_results": len(results),
        "total_errors": total_errors,
        "error_rate": total_errors / len(results) if results else 0.0,
        "error_distribution": error_counts,
        "severity_distribution": severity_counts,
        "unclassified_errors": unclassified_errors,
        "classification_coverage": (total_errors - unclassified_errors) / total_errors if total_errors > 0 else 1.0
    }

def generate_taxonomy_report(analysis: Dict[str, Any], out_path: str) -> None:
    """Generate comprehensive taxonomy report."""
    report = {
        "taxonomy_analysis": analysis,
        "error_patterns": [
            {
                "type": p.error_type.value,
                "severity": p.severity.value,
                "symptoms": p.symptoms,
                "mitigation": p.mitigation,
                "expected_frequency": p.expected_frequency,
                "observed_count": analysis["error_distribution"].get(p.error_type.value, 0)
            }
            for p in ERROR_PATTERNS
        ],
        "recommendations": []
    }

    # Generate recommendations based on observed errors
    for error_type, count in analysis["error_distribution"].items():
        if count > 0:
            pattern = next((p for p in ERROR_PATTERNS if p.error_type.value == error_type), None)
            if pattern:
                observed_freq = count / analysis["total_results"]
                if observed_freq > pattern.expected_frequency * 2:
                    report["recommendations"].append({
                        "priority": "high" if pattern.severity in [Severity.CRITICAL, Severity.HIGH] else "medium",
                        "issue": f"High frequency of {error_type} errors",
                        "observed_frequency": observed_freq,
                        "expected_frequency": pattern.expected_frequency,
                        "action": pattern.mitigation
                    })

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

def load_and_analyze(results_path: str) -> Dict[str, Any]:
    """Load benchmark results and perform taxonomy analysis."""
    results = []

    if results_path.endswith(".jsonl"):
        # JSONL format
        with open(results_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
    else:
        # JSON format
        with open(results_path) as f:
            data = json.load(f)
            results = data if isinstance(data, list) else [data]

    return analyze_error_distribution(results)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m benchmarks.dream.taxonomy <results_path> [output_path]")
        sys.exit(1)

    results_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "benchmarks/dream/taxonomy_report.json"

    try:
        analysis = load_and_analyze(results_path)
        generate_taxonomy_report(analysis, output_path)

        print("Taxonomy analysis complete:")
        print(f"  Total results: {analysis['total_results']}")
        print(f"  Error rate: {analysis['error_rate']:.1%}")
        print(f"  Classification coverage: {analysis['classification_coverage']:.1%}")
        print(f"  Report saved: {output_path}")

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)
