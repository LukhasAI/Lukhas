from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple


class Environment(Enum):
    """Deployment environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_LOAD = "high_load"
    LOW_LATENCY = "low_latency"

class Priority(Enum):
    """Optimization priorities."""
    ACCURACY = "accuracy"
    LATENCY = "latency"
    COVERAGE = "coverage"
    STABILITY = "stability"
    BALANCED = "balanced"

@dataclass
class ConfigProfile:
    """Configuration profile for specific environment/priority."""
    name: str
    environment: Environment
    priority: Priority
    config: Dict[str, Any]
    performance_targets: Dict[str, float]
    rationale: str

@dataclass
class PerformanceMetrics:
    """Performance metrics for a configuration."""
    accuracy: float
    coverage: float
    latency_p50: float
    latency_p95: float
    stability: float
    error_rate: float

class ConfigChooser:
    """Intelligent configuration selection system."""

    def __init__(self):
        self.profiles = self._define_profiles()

    def _define_profiles(self) -> List[ConfigProfile]:
        """Define standard configuration profiles."""
        return [
            ConfigProfile(
                name="dev_fast",
                environment=Environment.DEVELOPMENT,
                priority=Priority.LATENCY,
                config={
                    "strategy": "overlap",
                    "use_objective": "0",
                    "alignment_threshold": 0.3,
                    "drift_threshold": 0.5,
                    "confidence_threshold": 0.5,
                    "max_age_sec": 0,  # No staleness filtering
                    "half_life_sec": 0,  # No temporal weighting
                },
                performance_targets={
                    "accuracy": 0.7,
                    "latency_p95": 0.1,
                    "coverage": 0.8
                },
                rationale="Development environment optimized for fast iteration"
            ),
            ConfigProfile(
                name="staging_balanced",
                environment=Environment.STAGING,
                priority=Priority.BALANCED,
                config={
                    "strategy": "cosine",
                    "use_objective": "1",
                    "alignment_threshold": 0.4,
                    "drift_threshold": 0.4,
                    "confidence_threshold": 0.6,
                    "max_age_sec": 300,  # 5 minutes
                    "half_life_sec": 120,  # 2 minutes
                },
                performance_targets={
                    "accuracy": 0.8,
                    "latency_p95": 0.05,
                    "coverage": 0.85
                },
                rationale="Staging environment with balanced performance"
            ),
            ConfigProfile(
                name="prod_accuracy",
                environment=Environment.PRODUCTION,
                priority=Priority.ACCURACY,
                config={
                    "strategy": "blend",
                    "use_objective": "1",
                    "alignment_threshold": 0.5,
                    "drift_threshold": 0.3,
                    "confidence_threshold": 0.7,
                    "max_age_sec": 600,  # 10 minutes
                    "half_life_sec": 180,  # 3 minutes
                    "hybrid_alpha": 0.6,
                },
                performance_targets={
                    "accuracy": 0.9,
                    "latency_p95": 0.1,
                    "coverage": 0.9
                },
                rationale="Production environment optimized for accuracy"
            ),
            ConfigProfile(
                name="prod_latency",
                environment=Environment.PRODUCTION,
                priority=Priority.LATENCY,
                config={
                    "strategy": "overlap",
                    "use_objective": "0",
                    "alignment_threshold": 0.4,
                    "drift_threshold": 0.4,
                    "confidence_threshold": 0.6,
                    "max_age_sec": 0,  # No filtering for speed
                    "half_life_sec": 0,  # No temporal weighting
                },
                performance_targets={
                    "accuracy": 0.8,
                    "latency_p95": 0.02,
                    "coverage": 0.8
                },
                rationale="Production environment optimized for low latency"
            ),
            ConfigProfile(
                name="high_load",
                environment=Environment.HIGH_LOAD,
                priority=Priority.LATENCY,
                config={
                    "strategy": "overlap",
                    "use_objective": "0",
                    "alignment_threshold": 0.3,
                    "drift_threshold": 0.5,
                    "confidence_threshold": 0.5,
                    "max_age_sec": 0,
                    "half_life_sec": 0,
                    "max_snapshots": 20,  # Limit processing
                },
                performance_targets={
                    "accuracy": 0.75,
                    "latency_p95": 0.01,
                    "coverage": 0.7
                },
                rationale="High load environment with aggressive optimization"
            )
        ]

    def extract_metrics(self, benchmark_results: List[Dict[str, Any]]) -> Dict[str, PerformanceMetrics]:
        """Extract performance metrics from benchmark results."""
        metrics_by_config = {}

        for result in benchmark_results:
            config_key = f"{result.get('strategy', 'unknown')}_{result.get('use_objective', '0')}"

            metrics = PerformanceMetrics(
                accuracy=result.get('accuracy', 0.0),
                coverage=result.get('coverage>=0.5', 0.0),
                latency_p50=result.get('p50_ms', 0.0),
                latency_p95=result.get('p95_ms', 0.0),
                stability=result.get('stability', 0.0),
                error_rate=1.0 - result.get('accuracy', 0.0)  # Rough approximation
            )

            metrics_by_config[config_key] = metrics

        return metrics_by_config

    def score_config(self, metrics: PerformanceMetrics, profile: ConfigProfile) -> Tuple[float, Dict[str, float]]:
        """Score a configuration against a profile's targets."""
        targets = profile.performance_targets
        priority = profile.priority

        scores = {}

        # Individual metric scores (0.0 = target met, higher = worse)
        if 'accuracy' in targets:
            scores['accuracy'] = max(0.0, targets['accuracy'] - metrics.accuracy)

        if 'latency_p95' in targets:
            scores['latency'] = max(0.0, metrics.latency_p95 - targets['latency_p95'])

        if 'coverage' in targets:
            scores['coverage'] = max(0.0, targets['coverage'] - metrics.coverage)

        # Stability score (higher is better, so invert)
        scores['stability'] = max(0.0, 1.0 - metrics.stability)

        # Priority-weighted composite score
        weights = self._get_priority_weights(priority)
        composite_score = sum(scores.get(k, 0.0) * w for k, w in weights.items())

        return composite_score, scores

    def _get_priority_weights(self, priority: Priority) -> Dict[str, float]:
        """Get weights for different priorities."""
        if priority == Priority.ACCURACY:
            return {'accuracy': 0.5, 'coverage': 0.3, 'latency': 0.1, 'stability': 0.1}
        elif priority == Priority.LATENCY:
            return {'latency': 0.6, 'accuracy': 0.2, 'coverage': 0.1, 'stability': 0.1}
        elif priority == Priority.COVERAGE:
            return {'coverage': 0.5, 'accuracy': 0.3, 'latency': 0.1, 'stability': 0.1}
        elif priority == Priority.STABILITY:
            return {'stability': 0.5, 'accuracy': 0.3, 'latency': 0.1, 'coverage': 0.1}
        else:  # BALANCED
            return {'accuracy': 0.3, 'latency': 0.3, 'coverage': 0.2, 'stability': 0.2}

    def recommend_config(self, benchmark_path: str, environment: Environment,
                        priority: Priority = Priority.BALANCED) -> Dict[str, Any]:
        """Recommend best configuration based on benchmark results."""
        # Load benchmark results
        with open(benchmark_path, 'r') as f:
            if benchmark_path.endswith('.jsonl'):
                results = []
                for line in f:
                    line = line.strip()
                    if line:
                        results.append(json.loads(line))
            else:
                results = json.load(f)

        # Extract metrics
        metrics_by_config = self.extract_metrics(results)

        if not metrics_by_config:
            return {"error": "No valid benchmark results found"}

        # Find relevant profiles
        relevant_profiles = [p for p in self.profiles
                           if p.environment == environment or
                              (p.priority == priority and p.environment in [Environment.PRODUCTION, Environment.STAGING])]

        if not relevant_profiles:
            # Fallback: use balanced production profile
            relevant_profiles = [p for p in self.profiles if p.name == "staging_balanced"]

        best_config = None
        best_score = float('inf')
        best_profile = None
        all_scores = {}

        # Score each available configuration against each relevant profile
        for config_key, metrics in metrics_by_config.items():
            config_scores = {}

            for profile in relevant_profiles:
                score, breakdown = self.score_config(metrics, profile)
                config_scores[profile.name] = {
                    'score': score,
                    'breakdown': breakdown,
                    'profile': profile
                }

                if score < best_score:
                    best_score = score
                    best_config = config_key
                    best_profile = profile

            all_scores[config_key] = config_scores

        # Generate recommendation
        recommendation = {
            "recommended_config": best_config,
            "recommended_profile": best_profile.name if best_profile else None,
            "confidence_score": max(0.0, 1.0 - best_score),  # Convert penalty to confidence
            "environment": environment.value,
            "priority": priority.value,
            "config_details": best_profile.config if best_profile else {},
            "rationale": best_profile.rationale if best_profile else "No suitable profile found",
            "performance_prediction": metrics_by_config.get(best_config).__dict__ if best_config in metrics_by_config else {},
            "alternatives": []
        }

        # Add top 3 alternatives
        sorted_configs = sorted(all_scores.items(),
                               key=lambda x: min(s['score'] for s in x[1].values()))

        for config_key, scores in sorted_configs[1:4]:  # Skip best (first)
            best_profile_for_config = min(scores.values(), key=lambda x: x['score'])
            recommendation["alternatives"].append({
                "config": config_key,
                "profile": best_profile_for_config['profile'].name,
                "score": best_profile_for_config['score'],
                "rationale": best_profile_for_config['profile'].rationale
            })

        return recommendation

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters."""
        issues = []
        warnings = []

        # Check required parameters
        required = ['strategy', 'use_objective']
        for param in required:
            if param not in config:
                issues.append(f"Missing required parameter: {param}")

        # Validate ranges
        ranges = {
            'alignment_threshold': (0.0, 1.0),
            'drift_threshold': (0.0, 1.0),
            'confidence_threshold': (0.0, 1.0),
            'hybrid_alpha': (0.0, 1.0),
            'max_age_sec': (0, 3600),  # Max 1 hour
            'half_life_sec': (0, 1800)  # Max 30 minutes
        }

        for param, (min_val, max_val) in ranges.items():
            if param in config:
                value = config[param]
                if not isinstance(value, (int, float)) or value < min_val or value > max_val:
                    issues.append(f"{param} must be between {min_val} and {max_val}")

        # Validate strategy
        valid_strategies = ['overlap', 'cosine', 'blend', 'switch', 'vote']
        if config.get('strategy') not in valid_strategies:
            issues.append(f"strategy must be one of: {valid_strategies}")

        # Warnings for potentially problematic combinations
        if config.get('max_age_sec', 0) > 0 and config.get('half_life_sec', 0) == 0:
            warnings.append("Staleness filtering enabled without temporal weighting")

        if config.get('strategy') == 'blend' and 'hybrid_alpha' not in config:
            warnings.append("Blend strategy without hybrid_alpha parameter")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

def load_and_recommend(benchmark_path: str, environment: str, priority: str = "balanced") -> Dict[str, Any]:
    """Load benchmark results and generate recommendation."""
    try:
        env = Environment(environment.lower())
        prio = Priority(priority.lower())
    except ValueError as e:
        return {"error": f"Invalid parameter: {e}"}

    chooser = ConfigChooser()
    return chooser.recommend_config(benchmark_path, env, prio)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m benchmarks.dream.chooser <benchmark_path> <environment> [priority]")
        print(f"Environments: {[e.value for e in Environment]}")
        print(f"Priorities: {[p.value for p in Priority]}")
        sys.exit(1)

    benchmark_path = sys.argv[1]
    environment = sys.argv[2]
    priority = sys.argv[3] if len(sys.argv) > 3 else "balanced"

    try:
        recommendation = load_and_recommend(benchmark_path, environment, priority)

        if "error" in recommendation:
            print(f"Error: {recommendation['error']}")
            sys.exit(1)

        print("\n=== CONFIGURATION RECOMMENDATION ===")
        print(f"Environment: {recommendation['environment']}")
        print(f"Priority: {recommendation['priority']}")
        print(f"Recommended: {recommendation['recommended_config']} ({recommendation['recommended_profile']})")
        print(f"Confidence: {recommendation['confidence_score']:.1%}")
        print(f"Rationale: {recommendation['rationale']}")

        print("\nConfiguration:")
        for key, value in recommendation['config_details'].items():
            print(f"  {key}: {value}")

        if recommendation['alternatives']:
            print("\nAlternatives:")
            for alt in recommendation['alternatives']:
                print(f"  {alt['config']} ({alt['profile']}) - score: {alt['score']:.3f}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
