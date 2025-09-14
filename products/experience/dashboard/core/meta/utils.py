#!/usr/bin/env python3
"""
LUKHΛS Meta Dashboard Utilities
Helper functions for dashboard data processing
"""

import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional


def load_meta_metrics(path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load meta metrics from json_file.

    Args:
        path: Path to metrics file (defaults to data/meta_metrics.json)

    Returns:
        Dict containing meta metrics
    """
    if path is None:
        path = Path("data/meta_metrics.json")

    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
        else:
            # Return default metrics if file doesn't exist
            return {
                "average_drift": 0.0,
                "triad_coherence": 1.0,
                "entropy_level": 0.0,
                "persona_distribution": {},
                "total_evaluations": 0,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as e:
        print(f"Error loading meta metrics: {e}")
        return {}


def parse_jsonl_snapshots(path: Optional[Path] = None) -> list[dict[str, Any]]:
    """
    Parse JSONL snapshot file for drift history.

    Args:
        path: Path to snapshots file (defaults to data/drift_audit_results.jsonl)

    Returns:
        List of snapshot dictionaries
    """
    if path is None:
        path = Path("data/drift_audit_results.jsonl")

    snapshots = []

    try:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.strip():
                        snapshots.append(json.loads(line))
    except Exception as e:
        print(f"Error parsing snapshots: {e}")

    return snapshots


def calculate_drift_trends(snapshots: list[dict[str, Any]], window_hours: int = 24) -> dict[str, Any]:
    """
    Calculate drift trends from snapshots.

    Args:
        snapshots: List of snapshot dictionaries
        window_hours: Time window for trend calculation

    Returns:
        Dict containing trend analysis
    """
    if not snapshots:
        return {
            "trend": "stable",
            "average_drift": 0.0,
            "max_drift": 0.0,
            "min_drift": 0.0,
            "data_points": 0,
        }

    # Filter snapshots within time window
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    recent_snapshots = []

    for snap in snapshots:
        try:
            timestamp = datetime.fromisoformat(snap.get("timestamp", "").replace("Z", "+00:00"))
            if timestamp > cutoff_time:
                recent_snapshots.append(snap)
        except BaseException:
            continue

    if not recent_snapshots:
        recent_snapshots = snapshots[-10:]  # Use last 10 if no recent data

    # Extract drift scores
    drift_scores = [s.get("drift_score", 0.0) for s in recent_snapshots if "drift_score" in s]

    if not drift_scores:
        return {
            "trend": "unknown",
            "average_drift": 0.0,
            "max_drift": 0.0,
            "min_drift": 0.0,
            "data_points": 0,
        }

    # Calculate statistics
    avg_drift = statistics.mean(drift_scores)
    max_drift = max(drift_scores)
    min_drift = min(drift_scores)

    # Determine trend
    if len(drift_scores) >= 3:
        first_half = drift_scores[: len(drift_scores) // 2]
        second_half = drift_scores[len(drift_scores) // 2 :]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        if avg_second > avg_first * 1.1:
            trend = "increasing"
        elif avg_second < avg_first * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "trend": trend,
        "average_drift": avg_drift,
        "max_drift": max_drift,
        "min_drift": min_drift,
        "data_points": len(drift_scores),
        "time_window_hours": window_hours,
    }


def entropy_color_code(entropy: float) -> tuple[str, str]:
    """
    Get color code and status for entropy level.

    Args:
        entropy: Entropy value (0.0-1.0)

    Returns:
        Tuple of (hex_color, status_text)
    """
    if entropy < 0.3:
        return "#00ff00", "stable"
    elif entropy < 0.5:
        return "#88ff00", "low"
    elif entropy < 0.7:
        return "#ffff00", "medium"
    elif entropy < 0.85:
        return "#ff8800", "high"
    else:
        return "#ff0000", "critical"


def format_persona_distribution(distribution: dict[str, int]) -> list[dict[str, Any]]:
    """
    Format persona distribution for visualization.

    Args:
        distribution: Dict of persona names to counts

    Returns:
        List of formatted persona data
    """
    total = sum(distribution.values())

    if total == 0:
        return []

    formatted = []
    for persona, count in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        formatted.append(
            {
                "name": persona,
                "count": count,
                "percentage": (count / total) * 100,
                "emoji": get_persona_emoji(persona),
            }
        )

    return formatted


def get_persona_emoji(persona: str) -> str:
    """Get emoji representation for a persona"""
    emoji_map = {
        "The Stabilizer": "⚖️",
        "The Navigator": "🧭",
        "The Alchemist": "🔮",
        "The Guardian": "🛡️",
        "The Architect": "🏛️",
        "The Healer": "💚",
        "The Shadow": "🌑",
        "The Destroyer": "💀",
        "The Creator": "✨",
        "The Scholar": "📚",
        "The Trickster": "🎭",
        "The Wanderer": "🌍",
    }
    return emoji_map.get(persona, "❓")


def calculate_system_health(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate overall system health score.

    Args:
        metrics: Current system metrics

    Returns:
        Dict containing health assessment
    """
    # Base health score
    health_score = 100.0
    issues = []

    # Check drift score
    drift = metrics.get("average_drift", 0.0)
    if drift > 0.7:
        health_score -= 30
        issues.append("Critical drift detected")
    elif drift > 0.5:
        health_score -= 15
        issues.append("Elevated drift levels")

    # Check Trinity coherence
    coherence = metrics.get("triad_coherence", 1.0)
    if coherence < 0.3:
        health_score -= 25
        issues.append("Low Trinity coherence")
    elif coherence < 0.6:
        health_score -= 10
        issues.append("Trinity alignment degraded")

    # Check entropy
    entropy = metrics.get("entropy_level", 0.0)
    if entropy > 0.85:
        health_score -= 20
        issues.append("Critical entropy levels")
    elif entropy > 0.7:
        health_score -= 10
        issues.append("High entropy detected")

    # Determine health status
    if health_score >= 90:
        status = "excellent"
        color = "#00ff00"
    elif health_score >= 75:
        status = "good"
        color = "#88ff00"
    elif health_score >= 60:
        status = "fair"
        color = "#ffff00"
    elif health_score >= 40:
        status = "poor"
        color = "#ff8800"
    else:
        status = "critical"
        color = "#ff0000"

    return {
        "score": max(0, health_score),
        "status": status,
        "color": color,
        "issues": issues,
        "triad_aligned": coherence > 0.7,
        "recommendation": get_health_recommendation(health_score, issues),
    }


def get_health_recommendation(score: float, issues: list[str]) -> str:
    """Get health recommendation based on score and issues"""
    if score >= 90:
        return "System operating optimally. Continue monitoring."
    elif score >= 75:
        return "Minor adjustments recommended. Monitor closely."
    elif score >= 60:
        return "Intervention suggested. Review " + ", ".join(issues[:2])
    elif score >= 40:
        return "Immediate action required. Address: " + ", ".join(issues)
    else:
        return "CRITICAL: System requires emergency stabilization!"


# TODO: Add more utility functions:
# - Time series smoothing for trend visualization
# - Anomaly detection in drift patterns
# - Persona transition analysis
# - Guardian intervention correlation
# - Export functions for reporting
