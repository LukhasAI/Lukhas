#!/usr/bin/env python3
"""
Drift Tracker - Monitors ethical and behavioral drift in LUKHΛS
Uses decision entropy and pattern analysis to detect concerning changes
"""

import json
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DriftEvent:
    """Single drift measurement event"""

    timestamp: datetime
    drift_score: float
    action: str
    user_id: str
    entropy: float
    state_emoji: str
    metadata: Dict


class DriftTracker:
    """
    Tracks behavioral and ethical drift based on decision entropy
    and symbolic mutation patterns
    """

    # Drift thresholds
    THRESHOLDS = {"stable": 0.3, "neutral": 0.7, "unstable": 1.0}

    # Time windows for analysis
    WINDOWS = {
        "immediate": timedelta(minutes=5),
        "short": timedelta(hours=1),
        "medium": timedelta(hours=24),
        "long": timedelta(days=7),
    }

    def __init__(self, max_history: int = 10000):
        self.history = deque(maxlen=max_history)
        self.user_profiles: Dict[str, Dict] = {}
        self.global_drift = 0.0
        self.alerts: List[Dict] = []

        # Entropy tracking
        self.entropy_window = deque(maxlen=100)
        self.pattern_cache: Dict[str, int] = {}

        logger.info("🌀 Drift Tracker initialized")

    def record_drift(
        self,
        user_id: str,
        drift_score: float,
        action: str,
        entropy: float,
        metadata: Dict = None,
    ) -> DriftEvent:
        """Record a drift event and update trackers"""
        # Determine state emoji
        if drift_score < self.THRESHOLDS["stable"]:
            state_emoji = "🌿"
        elif drift_score < self.THRESHOLDS["neutral"]:
            state_emoji = "🌀"
        else:
            state_emoji = "🌪️"

        # Create event
        event = DriftEvent(
            timestamp=datetime.utcnow(),
            drift_score=drift_score,
            action=action,
            user_id=user_id,
            entropy=entropy,
            state_emoji=state_emoji,
            metadata=metadata or {},
        )

        # Add to history
        self.history.append(event)
        self.entropy_window.append(entropy)

        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "total_actions": 0,
                "avg_drift": 0.0,
                "max_drift": 0.0,
                "stability_score": 1.0,
                "last_seen": datetime.utcnow(),
            }

        profile = self.user_profiles[user_id]
        profile["total_actions"] += 1
        profile["avg_drift"] = (
            profile["avg_drift"] * (profile["total_actions"] - 1) + drift_score
        ) / profile["total_actions"]
        profile["max_drift"] = max(profile["max_drift"], drift_score)
        profile["last_seen"] = datetime.utcnow()

        # Update global drift (weighted average)
        self._update_global_drift()

        # Check for alerts
        self._check_alerts(event)

        # Update pattern cache
        pattern_key = f"{action}_{state_emoji}"
        self.pattern_cache[pattern_key] = self.pattern_cache.get(pattern_key, 0) + 1

        return event

    def _update_global_drift(self):
        """Calculate global drift score across all users"""
        if not self.history:
            return

        # Get recent events (last hour)
        cutoff = datetime.utcnow() - self.WINDOWS["short"]
        recent_events = [e for e in self.history if e.timestamp > cutoff]

        if recent_events:
            self.global_drift = np.mean([e.drift_score for e in recent_events])

    def _check_alerts(self, event: DriftEvent):
        """Check if event triggers any alerts"""
        alerts = []

        # High drift alert
        if event.drift_score > 0.8:
            alerts.append(
                {
                    "type": "high_drift",
                    "severity": "critical",
                    "message": f"Critical drift detected: {event.drift_score:.2f}",
                    "user_id": event.user_id,
                    "timestamp": event.timestamp.isoformat(),
                }
            )

        # Rapid drift increase
        user_events = [e for e in self.history if e.user_id == event.user_id][-10:]
        if len(user_events) >= 3:
            drift_delta = user_events[-1].drift_score - user_events[-3].drift_score
            if drift_delta > 0.3:
                alerts.append(
                    {
                        "type": "rapid_drift",
                        "severity": "warning",
                        "message": f"Rapid drift increase: {drift_delta:.2f} in 3 actions",
                        "user_id": event.user_id,
                        "timestamp": event.timestamp.isoformat(),
                    }
                )

        # High entropy alert
        if event.entropy > 0.85:
            alerts.append(
                {
                    "type": "high_entropy",
                    "severity": "warning",
                    "message": f"High decision entropy: {event.entropy:.2f}",
                    "user_id": event.user_id,
                    "timestamp": event.timestamp.isoformat(),
                }
            )

        self.alerts.extend(alerts)

        # Log alerts
        for alert in alerts:
            logger.warning(f"⚠️ DRIFT ALERT: {alert['message']}")

    def get_drift_analysis(
        self, user_id: Optional[str] = None, window: str = "short"
    ) -> Dict:
        """Get comprehensive drift analysis"""
        # Filter events
        cutoff = datetime.utcnow() - self.WINDOWS.get(window, self.WINDOWS["short"])

        if user_id:
            events = [
                e for e in self.history if e.user_id == user_id and e.timestamp > cutoff
            ]
        else:
            events = [e for e in self.history if e.timestamp > cutoff]

        if not events:
            return {
                "window": window,
                "user_id": user_id,
                "event_count": 0,
                "avg_drift": 0.0,
                "max_drift": 0.0,
                "entropy_trend": "stable",
                "state_distribution": {},
                "recommendations": ["No data available"],
            }

        # Calculate metrics
        drift_scores = [e.drift_score for e in events]
        entropy_values = [e.entropy for e in events]

        # State distribution
        state_dist = {}
        for event in events:
            state_dist[event.state_emoji] = state_dist.get(event.state_emoji, 0) + 1

        # Entropy trend
        if len(entropy_values) >= 2:
            entropy_slope = np.polyfit(range(len(entropy_values)), entropy_values, 1)[0]
            if entropy_slope > 0.01:
                entropy_trend = "increasing"
            elif entropy_slope < -0.01:
                entropy_trend = "decreasing"
            else:
                entropy_trend = "stable"
        else:
            entropy_trend = "insufficient_data"

        # Generate recommendations
        recommendations = self._generate_recommendations(
            avg_drift=np.mean(drift_scores),
            max_drift=max(drift_scores),
            entropy_trend=entropy_trend,
            state_dist=state_dist,
        )

        return {
            "window": window,
            "user_id": user_id,
            "event_count": len(events),
            "avg_drift": float(np.mean(drift_scores)),
            "max_drift": float(max(drift_scores)),
            "min_drift": float(min(drift_scores)),
            "std_drift": float(np.std(drift_scores)),
            "avg_entropy": float(np.mean(entropy_values)),
            "entropy_trend": entropy_trend,
            "state_distribution": state_dist,
            "dominant_state": (
                max(state_dist.items(), key=lambda x: x[1])[0] if state_dist else "🌿"
            ),
            "recommendations": recommendations,
            "global_drift": self.global_drift,
        }

    def _generate_recommendations(
        self, avg_drift: float, max_drift: float, entropy_trend: str, state_dist: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on drift analysis"""
        recommendations = []

        # Drift-based recommendations
        if avg_drift > 0.7:
            recommendations.append(
                "⚠️ Implement immediate intervention - high average drift"
            )
            recommendations.append(
                "🔒 Increase authentication requirements temporarily"
            )
        elif avg_drift > 0.5:
            recommendations.append("📊 Monitor user behavior closely")
            recommendations.append("🤝 Consider re-consent flow")

        if max_drift > 0.9:
            recommendations.append(
                "🚨 Critical drift detected - manual review required"
            )

        # Entropy-based recommendations
        if entropy_trend == "increasing":
            recommendations.append(
                "📈 Decision patterns becoming chaotic - simplify UI"
            )
            recommendations.append("🧭 Provide clearer guidance to users")

        # State-based recommendations
        unstable_ratio = (
            state_dist.get("🌪️", 0) / sum(state_dist.values()) if state_dist else 0
        )
        if unstable_ratio > 0.3:
            recommendations.append(
                "🌪️ High instability ratio - review system parameters"
            )

        if not recommendations:
            recommendations.append("✅ System operating within normal parameters")

        return recommendations

    def get_pattern_insights(self) -> Dict:
        """Analyze patterns in drift behavior"""
        if not self.pattern_cache:
            return {"patterns": [], "insights": ["Insufficient data"]}

        # Sort patterns by frequency
        sorted_patterns = sorted(
            self.pattern_cache.items(), key=lambda x: x[1], reverse=True
        )

        patterns = []
        for pattern, count in sorted_patterns[:10]:
            action, emoji = pattern.rsplit("_", 1)
            patterns.append(
                {
                    "action": action,
                    "state": emoji,
                    "count": count,
                    "percentage": (
                        count / len(self.history) * 100 if self.history else 0
                    ),
                }
            )

        # Generate insights
        insights = []

        # Most common unstable pattern
        unstable_patterns = [(p, c) for p, c in sorted_patterns if "🌪️" in p]
        if unstable_patterns:
            top_unstable = unstable_patterns[0][0].split("_")[0]
            insights.append(f"🌪️ '{top_unstable}' most likely to cause instability")

        # Most stable pattern
        stable_patterns = [(p, c) for p, c in sorted_patterns if "🌿" in p]
        if stable_patterns:
            top_stable = stable_patterns[0][0].split("_")[0]
            insights.append(f"🌿 '{top_stable}' promotes system stability")

        return {
            "patterns": patterns,
            "insights": insights,
            "total_patterns": len(self.pattern_cache),
            "entropy_average": (
                float(np.mean(self.entropy_window)) if self.entropy_window else 0.0
            ),
        }

    def export_report(self) -> Dict:
        """Generate comprehensive drift report"""
        return {
            "generated": datetime.utcnow().isoformat(),
            "global_drift": self.global_drift,
            "total_events": len(self.history),
            "active_users": len(self.user_profiles),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "analysis": {
                "immediate": self.get_drift_analysis(window="immediate"),
                "short": self.get_drift_analysis(window="short"),
                "medium": self.get_drift_analysis(window="medium"),
                "long": self.get_drift_analysis(window="long"),
            },
            "patterns": self.get_pattern_insights(),
            "user_stability_scores": {
                uid: profile["stability_score"]
                for uid, profile in list(self.user_profiles.items())[:10]
            },
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize tracker
    tracker = DriftTracker()

    # Simulate drift events
    import random

    users = ["user_001", "user_002", "user_003"]
    actions = ["authenticate", "unlock_profile", "view_data", "suspicious_attempt"]

    for i in range(20):
        user = random.choice(users)
        action = random.choice(actions)

        # Simulate drift and entropy
        if action == "suspicious_attempt":
            drift = random.uniform(0.6, 0.95)
            entropy = random.uniform(0.7, 0.95)
        else:
            drift = random.uniform(0.1, 0.6)
            entropy = random.uniform(0.2, 0.7)

        event = tracker.record_drift(user, drift, action, entropy)
        print(
            f"{event.state_emoji} {user}: {action} (drift: {drift:.2f}, entropy: {entropy:.2f})"
        )

    # Get analysis
    print("\n📊 Drift Analysis (Short Window):")
    analysis = tracker.get_drift_analysis(window="short")
    print(json.dumps(analysis, indent=2))

    print("\n🔍 Pattern Insights:")
    patterns = tracker.get_pattern_insights()
    print(json.dumps(patterns, indent=2))
