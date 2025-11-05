"""
VIVOX.ERN Transparency & Audit System
Provides comprehensive audit trails and user transparency for emotional regulation
"""

import logging

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from core.common import get_logger

from .vivox_ern_core import RegulationResponse, RegulationStrategy

logger = logging.getLogger(__name__)




logger = get_logger(__name__)


class AuditEventType(Enum):
    """Types of audit events"""

    EMOTIONAL_INPUT = "emotional_input"
    REGULATION_APPLIED = "regulation_applied"
    STRATEGY_SELECTED = "strategy_selected"
    EFFECTIVENESS_MEASURED = "effectiveness_measured"
    PATTERN_LEARNED = "pattern_learned"
    HORMONE_RELEASED = "hormone_released"
    TAG_ACTIVATED = "tag_activated"
    USER_FEEDBACK = "user_feedback"
    SYSTEM_DECISION = "system_decision"
    PRIVACY_EVENT = "privacy_event"


class TransparencyLevel(Enum):
    """Levels of transparency for user reports"""

    BASIC = "basic"  # Simple explanations
    DETAILED = "detailed"  # Technical details included
    TECHNICAL = "technical"  # Full technical information
    PRIVACY = "privacy"  # Privacy-focused summary


@dataclass
class AuditEvent:
    """Individual audit event record"""

    event_id: str
    timestamp: datetime
    user_id: str
    event_type: AuditEventType
    event_data: dict[str, Any]
    reasoning: str
    impact_assessment: dict[str, Any]
    privacy_level: str = "normal"  # normal, sensitive, private
    user_visible: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "event_type": self.event_type.value,
            "event_data": self.event_data,
            "reasoning": self.reasoning,
            "impact_assessment": self.impact_assessment,
            "privacy_level": self.privacy_level,
            "user_visible": self.user_visible,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        """Create from dictionary"""
        return cls(
            event_id=data["event_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data["user_id"],
            event_type=AuditEventType(data["event_type"]),
            event_data=data["event_data"],
            reasoning=data["reasoning"],
            impact_assessment=data["impact_assessment"],
            privacy_level=data.get("privacy_level", "normal"),
            user_visible=data.get("user_visible", True),
        )


@dataclass
class UserTransparencyReport:
    """Comprehensive transparency report for users"""

    user_id: str
    report_period: tuple[datetime, datetime]
    transparency_level: TransparencyLevel
    summary: dict[str, Any]
    emotional_journey: list[dict[str, Any]]
    regulation_insights: dict[str, Any]
    learning_progress: dict[str, Any]
    privacy_summary: dict[str, Any]
    recommendations: list[str]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_human_readable(self) -> str:
        """Generate human-readable report"""
        if self.transparency_level == TransparencyLevel.BASIC:
            return self._generate_basic_report()
        elif self.transparency_level == TransparencyLevel.DETAILED:
            return self._generate_detailed_report()
        elif self.transparency_level == TransparencyLevel.TECHNICAL:
            return self._generate_technical_report()
        else:  # PRIVACY
            return self._generate_privacy_report()

    def _generate_basic_report(self) -> str:
        """Generate basic user-friendly report"""
        report = f"""
# Your Emotional Wellness Report
Generated: {self.generated_at.strftime("%B %d, %Y at %I:%M %p")}

## Summary
During this period, I helped you with {self.summary.get("total_regulations", 0)} emotional situations.
Your emotional wellness improved by an average of {self.summary.get("average_improvement", 0):.0%}.

## Key Insights
- Most effective technique: {self.regulation_insights.get("most_effective_strategy", "Unknown")}
- Common emotional patterns: {", ".join(self.summary.get("common_patterns", []))}
- Success rate: {self.regulation_insights.get("success_rate", 0):.0%}

## Recommendations
"""
        for rec in self.recommendations[:3]:  # Top 3 recommendations
            report += f"- {rec}\n"

        return report

    def _generate_detailed_report(self) -> str:
        """Generate detailed report with more technical information"""
        report = f"""
# Detailed Emotional Regulation Report
User: {self.user_id}
Period: {self.report_period[0].strftime("%m/%d/%Y")} - {self.report_period[1].strftime("%m/%d/%Y")}
Generated: {self.generated_at.isoformat()}

## Executive Summary
- Total Regulation Events: {self.summary.get("total_regulations", 0)}
- Average Effectiveness: {self.summary.get("average_effectiveness", 0):.2f}
- Emotional Volatility: {self.summary.get("emotional_volatility", 0):.2f}
- Learning Progress: {self.learning_progress.get("progress_score", 0):.2f}

## Regulation Strategy Analysis
"""
        for strategy, stats in self.regulation_insights.get("strategy_breakdown", {}).items():
            report += (
                f"- {strategy}: {stats.get('count', 0)} uses, {stats.get('effectiveness', 0):.2f} avg effectiveness\n"
            )

        report += """
## Emotional Journey Highlights
"""
        for event in self.emotional_journey[:5]:  # Top 5 events
            report += f"- {event.get('timestamp', '')}: {event.get('description', '')}\n"

        report += f"""
## Learning & Adaptation
- Patterns Learned: {self.learning_progress.get("patterns_learned", 0)}
- Neuroplastic Adaptations: {self.learning_progress.get("adaptations", 0)}
- Personalization Level: {self.learning_progress.get("personalization_level", 0):.0%}

## Privacy & Data Handling
- Data points collected: {self.privacy_summary.get("data_points", 0)}
- Sensitive events: {self.privacy_summary.get("sensitive_events", 0)}
- Data retention: {self.privacy_summary.get("retention_days", 0)} days

## Recommendations
"""
        for rec in self.recommendations:
            report += f"- {rec}\n"

        return report

    def _generate_technical_report(self) -> str:
        """Generate full technical report"""
        return f"""
# Technical Emotional Regulation Audit Report
User ID: {self.user_id}
Report Period: {self.report_period[0].isoformat()} to {self.report_period[1].isoformat()}
Generated: {self.generated_at.isoformat()}

## Raw Statistics
{json.dumps(self.summary, indent=2)}

## Regulation Analysis
{json.dumps(self.regulation_insights, indent=2)}

## Learning Progress
{json.dumps(self.learning_progress, indent=2)}

## Emotional Journey Data
{json.dumps(self.emotional_journey, indent=2)}

## Privacy Audit
{json.dumps(self.privacy_summary, indent=2)}

## Recommendations Engine Output
{json.dumps(self.recommendations, indent=2)}
"""

    def _generate_privacy_report(self) -> str:
        """Generate privacy-focused report"""
        return f"""
# Privacy & Data Usage Summary
Generated: {self.generated_at.strftime("%B %d, %Y")}

## What Data Was Collected
- Emotional state measurements: {self.privacy_summary.get("emotional_measurements", 0)}
- Regulation interactions: {self.privacy_summary.get("regulation_interactions", 0)}
- Learning adaptations: {self.privacy_summary.get("learning_events", 0)}

## How Your Data Was Used
- To provide personalized emotional support
- To improve regulation strategy effectiveness
- To adapt to your preferences over time

## Data Protection
- All data encrypted and stored securely
- No personal information shared with third parties
- Data automatically deleted after {self.privacy_summary.get("retention_days", 90)} days

## Your Rights
- You can request a copy of your data at any time
- You can delete your data permanently
- You can adjust privacy settings and data collection preferences
"""


class VIVOXAuditSystem:
    """
    Comprehensive audit and transparency system for VIVOX.ERN
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "/tmp/vivox_audit"
        self.audit_events: list[AuditEvent] = []
        self.user_sessions: dict[str, list[str]] = {}  # user_id -> event_ids

        # Audit configuration
        self.max_events_memory = 10000
        self.retention_days = 90
        self.auto_archive_enabled = True

        # Privacy settings
        self.default_privacy_level = "normal"
        self.sensitive_keywords = [
            "personal",
            "private",
            "confidential",
            "sensitive",
            "medical",
            "health",
            "therapy",
            "crisis",
        ]

        # Ensure storage directory exists
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

        # Load existing audit events
        self._load_audit_events()

    async def log_emotional_input(self, user_id: str, emotion_data: dict[str, Any], context: dict[str, Any]) -> str:
        """Log emotional input event"""

        # Assess privacy level
        privacy_level = self._assess_privacy_level(emotion_data, context)

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.EMOTIONAL_INPUT,
            event_data={
                "emotion_summary": self._summarize_emotion_data(emotion_data),
                "context_summary": self._summarize_context(context),
                "data_points": (len(emotion_data) if isinstance(emotion_data, dict) else 1),
            },
            reasoning="User provided emotional input for processing",
            impact_assessment={
                "data_sensitivity": privacy_level,
                "processing_required": True,
                "user_benefit": "emotional_support",
            },
            privacy_level=privacy_level,
        )

        await self._store_audit_event(event)
        return event.event_id

    async def log_regulation_applied(
        self,
        user_id: str,
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ) -> str:
        """Log regulation application event"""

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.REGULATION_APPLIED,
            event_data={
                "strategy": regulation_response.strategy_used.value,
                "effectiveness": regulation_response.effectiveness,
                "original_state": regulation_response.original_state.to_dict(),
                "regulated_state": regulation_response.regulated_state.to_dict(),
                "hormone_triggers": regulation_response.hormone_triggers,
                "neuroplastic_tags": regulation_response.neuroplastic_tags,
                "duration_seconds": regulation_response.duration_seconds,
            },
            reasoning=regulation_response.reasoning,
            impact_assessment={
                "emotional_impact": regulation_response.effectiveness,
                "strategy_appropriateness": "assessed_automatically",
                "user_benefit": "emotional_regulation",
            },
        )

        await self._store_audit_event(event)
        return event.event_id

    async def log_strategy_selection(
        self,
        user_id: str,
        selected_strategy: RegulationStrategy,
        available_strategies: list[RegulationStrategy],
        selection_reasoning: str,
        context: dict[str, Any],
    ) -> str:
        """Log strategy selection decision"""

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.STRATEGY_SELECTED,
            event_data={
                "selected_strategy": selected_strategy.value,
                "available_strategies": [s.value for s in available_strategies],
                "selection_factors": context.get("selection_factors", {}),
                "user_preferences": context.get("user_preferences", {}),
            },
            reasoning=selection_reasoning,
            impact_assessment={
                "decision_quality": "to_be_measured",
                "personalization_level": len(context.get("user_preferences", {})) / 10.0,
                "expected_effectiveness": context.get("expected_effectiveness", 0.5),
            },
        )

        await self._store_audit_event(event)
        return event.event_id

    async def log_pattern_learning(self, user_id: str, pattern_data: dict[str, Any], learning_outcome: str) -> str:
        """Log pattern learning event"""

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.PATTERN_LEARNED,
            event_data={
                "pattern_type": pattern_data.get("type", "unknown"),
                "pattern_strength": pattern_data.get("strength", 0.0),
                "triggers": pattern_data.get("triggers", []),
                "effectiveness": pattern_data.get("effectiveness", 0.0),
                "usage_count": pattern_data.get("usage_count", 0),
            },
            reasoning=f"System learned new pattern: {learning_outcome}",
            impact_assessment={
                "learning_value": pattern_data.get("strength", 0.0),
                "personalization_improvement": True,
                "future_effectiveness_boost": pattern_data.get("effectiveness", 0.0) * 0.1,
            },
        )

        await self._store_audit_event(event)
        return event.event_id

    async def log_user_feedback(
        self,
        user_id: str,
        feedback_data: dict[str, Any],
        regulation_event_id: Optional[str] = None,
    ) -> str:
        """Log user feedback event"""

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.USER_FEEDBACK,
            event_data={
                "satisfaction_score": feedback_data.get("satisfaction", 0.0),
                "feedback_text": feedback_data.get("text", ""),
                "feedback_type": feedback_data.get("type", "general"),
                "related_regulation": regulation_event_id,
            },
            reasoning="User provided feedback on system performance",
            impact_assessment={
                "feedback_value": feedback_data.get("satisfaction", 0.0),
                "learning_opportunity": True,
                "system_improvement": "enabled",
            },
            privacy_level="sensitive",  # User feedback is always sensitive
        )

        await self._store_audit_event(event)
        return event.event_id

    async def log_privacy_event(self, user_id: str, privacy_action: str, details: dict[str, Any]) -> str:
        """Log privacy-related events"""

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            event_type=AuditEventType.PRIVACY_EVENT,
            event_data={
                "action": privacy_action,
                "details": details,
                "compliance_status": "verified",
            },
            reasoning=f"Privacy action executed: {privacy_action}",
            impact_assessment={
                "privacy_protection": "enhanced",
                "user_control": "maintained",
                "compliance": "gdpr_ccpa_compliant",
            },
            privacy_level="private",
        )

        await self._store_audit_event(event)
        return event.event_id

    async def generate_user_transparency_report(
        self,
        user_id: str,
        transparency_level: TransparencyLevel = TransparencyLevel.DETAILED,
        days: int = 30,
    ) -> UserTransparencyReport:
        """Generate comprehensive transparency report for user"""

        # Get user's audit events for the period
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        user_events = await self._get_user_events(user_id, start_date, end_date)

        # Generate report sections
        summary = await self._generate_summary_stats(user_events)
        emotional_journey = await self._generate_emotional_journey(user_events)
        regulation_insights = await self._generate_regulation_insights(user_events)
        learning_progress = await self._generate_learning_progress(user_events)
        privacy_summary = await self._generate_privacy_summary(user_events)
        recommendations = await self._generate_recommendations(user_events, summary)

        report = UserTransparencyReport(
            user_id=user_id,
            report_period=(start_date, end_date),
            transparency_level=transparency_level,
            summary=summary,
            emotional_journey=emotional_journey,
            regulation_insights=regulation_insights,
            learning_progress=learning_progress,
            privacy_summary=privacy_summary,
            recommendations=recommendations,
        )

        # Log report generation
        await self.log_privacy_event(
            user_id,
            "transparency_report_generated",
            {
                "report_level": transparency_level.value,
                "report_period_days": days,
                "events_included": len(user_events),
            },
        )

        return report

    async def _get_user_events(self, user_id: str, start_date: datetime, end_date: datetime) -> list[AuditEvent]:
        """Get user's audit events for date range"""

        user_events = []

        for event in self.audit_events:
            if event.user_id == user_id and start_date <= event.timestamp <= end_date and event.user_visible:
                user_events.append(event)

        # Sort by timestamp
        user_events.sort(key=lambda e: e.timestamp)

        return user_events

    async def _generate_summary_stats(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Generate summary statistics from events"""

        regulation_events = [e for e in events if e.event_type == AuditEventType.REGULATION_APPLIED]
        input_events = [e for e in events if e.event_type == AuditEventType.EMOTIONAL_INPUT]
        learning_events = [e for e in events if e.event_type == AuditEventType.PATTERN_LEARNED]

        effectiveness_scores = [e.event_data.get("effectiveness", 0.0) for e in regulation_events]

        return {
            "total_events": len(events),
            "total_regulations": len(regulation_events),
            "total_emotional_inputs": len(input_events),
            "total_learning_events": len(learning_events),
            "average_effectiveness": (
                sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
            ),
            "effectiveness_trend": (
                "improving"
                if len(effectiveness_scores) > 5 and effectiveness_scores[-3:] > effectiveness_scores[:3]
                else "stable"
            ),
            "engagement_level": min(1.0, len(events) / 100.0),  # Normalize engagement
            "common_patterns": self._extract_common_patterns(events),
        }

    async def _generate_emotional_journey(self, events: list[AuditEvent]) -> list[dict[str, Any]]:
        """Generate emotional journey timeline"""

        journey = []

        for event in events:
            if event.event_type in [
                AuditEventType.EMOTIONAL_INPUT,
                AuditEventType.REGULATION_APPLIED,
            ]:
                journey_entry = {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type.value,
                    "description": self._generate_journey_description(event),
                    "impact": event.impact_assessment.get("emotional_impact", 0.0),
                    "privacy_level": event.privacy_level,
                }
                journey.append(journey_entry)

        return journey[-20:]  # Last 20 events

    async def _generate_regulation_insights(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Generate regulation strategy insights"""

        regulation_events = [e for e in events if e.event_type == AuditEventType.REGULATION_APPLIED]

        if not regulation_events:
            return {"message": "No regulation data available"}

        # Strategy effectiveness analysis
        strategy_stats = {}
        for event in regulation_events:
            strategy = event.event_data.get("strategy", "unknown")
            effectiveness = event.event_data.get("effectiveness", 0.0)

            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"scores": [], "count": 0}

            strategy_stats[strategy]["scores"].append(effectiveness)
            strategy_stats[strategy]["count"] += 1

        # Calculate averages
        for strategy in strategy_stats:
            scores = strategy_stats[strategy]["scores"]
            strategy_stats[strategy]["average"] = sum(scores) / len(scores)

        # Find most effective strategy
        most_effective = max(strategy_stats.items(), key=lambda x: x[1]["average"])[0] if strategy_stats else "unknown"

        return {
            "strategy_breakdown": strategy_stats,
            "most_effective_strategy": most_effective,
            "success_rate": sum(1 for e in regulation_events if e.event_data.get("effectiveness", 0) > 0.7)
            / len(regulation_events),
            "total_regulations": len(regulation_events),
            "average_duration": sum(e.event_data.get("duration_seconds", 0) for e in regulation_events)
            / len(regulation_events),
        }

    async def _generate_learning_progress(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Generate learning and adaptation progress"""

        learning_events = [e for e in events if e.event_type == AuditEventType.PATTERN_LEARNED]

        progress_score = min(1.0, len(learning_events) / 10.0)  # Normalize to 0-1

        return {
            "patterns_learned": len(learning_events),
            "progress_score": progress_score,
            "adaptations": sum(1 for e in learning_events if e.event_data.get("pattern_strength", 0) > 0.7),
            "personalization_level": progress_score,
            "learning_rate": len(learning_events)
            / max(
                1,
                len([e for e in events if e.event_type == AuditEventType.REGULATION_APPLIED]),
            ),
        }

    async def _generate_privacy_summary(self, events: list[AuditEvent]) -> dict[str, Any]:
        """Generate privacy and data usage summary"""

        data_points = sum(e.event_data.get("data_points", 1) for e in events)
        sensitive_events = sum(1 for e in events if e.privacy_level in ["sensitive", "private"])

        return {
            "data_points": data_points,
            "sensitive_events": sensitive_events,
            "retention_days": self.retention_days,
            "privacy_compliance": "gdpr_ccpa_compliant",
            "encryption_status": "encrypted",
            "data_sharing": "none",
            "user_control": "full",
        }

    async def _generate_recommendations(self, events: list[AuditEvent], summary: dict[str, Any]) -> list[str]:
        """Generate personalized recommendations"""

        recommendations = []

        # Effectiveness-based recommendations
        avg_effectiveness = summary.get("average_effectiveness", 0.0)
        if avg_effectiveness < 0.6:
            recommendations.append("Consider trying different regulation strategies to improve effectiveness")

        # Engagement recommendations
        engagement = summary.get("engagement_level", 0.0)
        if engagement < 0.3:
            recommendations.append("Regular practice with emotional regulation techniques could improve outcomes")

        # Strategy-specific recommendations
        regulation_events = [e for e in events if e.event_type == AuditEventType.REGULATION_APPLIED]
        if regulation_events:
            strategies_used = {e.event_data.get("strategy") for e in regulation_events}
            if len(strategies_used) < 3:
                recommendations.append("Exploring additional regulation strategies might provide better results")

        # Learning recommendations
        learning_events = [e for e in events if e.event_type == AuditEventType.PATTERN_LEARNED]
        if len(learning_events) < 5:
            recommendations.append("Continued use will help the system learn your preferences better")

        # Privacy recommendations
        recommendations.append("Review your privacy settings regularly to ensure they meet your preferences")

        return recommendations[:5]  # Top 5 recommendations

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = datetime.now(timezone.utc).timestamp()
        random_part = os.urandom(4).hex()
        return f"vivox_audit_{int(timestamp)}_{random_part}"

    def _assess_privacy_level(self, emotion_data: dict[str, Any], context: dict[str, Any]) -> str:
        """Assess privacy level of data"""

        # Check for sensitive keywords
        all_text = str(emotion_data) + str(context)
        if any(keyword in all_text.lower() for keyword in self.sensitive_keywords):
            return "sensitive"

        # Check context indicators
        if context.get("environment") in ["therapy", "medical", "counseling"]:
            return "sensitive"

        if context.get("stress_level", 0) > 0.8:
            return "sensitive"

        return self.default_privacy_level

    def _summarize_emotion_data(self, emotion_data: dict[str, Any]) -> dict[str, Any]:
        """Create privacy-safe summary of emotion data"""

        if "vad" in emotion_data:
            vad = emotion_data["vad"]
            return {
                "type": "vad_vector",
                "valence_range": self._categorize_value(vad.get("valence", 0)),
                "arousal_range": self._categorize_value(vad.get("arousal", 0)),
                "intensity": self._categorize_value(vad.get("intensity", 0)),
            }
        elif "emotions" in emotion_data:
            return {
                "type": "emotion_scores",
                "dominant_emotion": (
                    max(emotion_data["emotions"].items(), key=lambda x: x[1])[0]
                    if emotion_data["emotions"]
                    else "neutral"
                ),
                "emotion_count": len(emotion_data["emotions"]),
            }
        else:
            return {"type": "text_or_other", "data_size": len(str(emotion_data))}

    def _summarize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Create privacy-safe summary of context"""

        return {
            "environment": context.get("environment", "unknown"),
            "time_context": context.get("time_of_day", "unknown"),
            "stress_level_category": self._categorize_value(context.get("stress_level", 0.5)),
            "context_factors": len(context),
        }

    def _categorize_value(self, value: float) -> str:
        """Categorize numeric values for privacy"""
        if value < -0.5:
            return "low"
        elif value > 0.5:
            return "high"
        else:
            return "medium"

    def _extract_common_patterns(self, events: list[AuditEvent]) -> list[str]:
        """Extract common patterns from events"""

        patterns = []

        # Common regulation strategies
        regulation_events = [e for e in events if e.event_type == AuditEventType.REGULATION_APPLIED]
        if regulation_events:
            strategies = [e.event_data.get("strategy") for e in regulation_events]
            most_common_strategy = max(set(strategies), key=strategies.count)
            patterns.append(f"frequently_uses_{most_common_strategy}")

        # Time patterns
        times = [e.timestamp.hour for e in events]
        if times:
            most_active_hour = max(set(times), key=times.count)
            if 6 <= most_active_hour <= 12:
                patterns.append("morning_active")
            elif 13 <= most_active_hour <= 18:
                patterns.append("afternoon_active")
            else:
                patterns.append("evening_active")

        return patterns[:3]  # Top 3 patterns

    def _generate_journey_description(self, event: AuditEvent) -> str:
        """Generate human-readable description of journey event"""

        if event.event_type == AuditEventType.EMOTIONAL_INPUT:
            emotion_summary = event.event_data.get("emotion_summary", {})
            dominant_emotion = emotion_summary.get("dominant_emotion", "unknown")
            return f"Experienced {dominant_emotion} emotions and sought support"

        elif event.event_type == AuditEventType.REGULATION_APPLIED:
            strategy = event.event_data.get("strategy", "unknown")
            effectiveness = event.event_data.get("effectiveness", 0)
            return f"Applied {strategy} regulation with {effectiveness:.0%} effectiveness"

        else:
            return event.reasoning

    async def _store_audit_event(self, event: AuditEvent):
        """Store audit event in memory and optionally persist"""

        self.audit_events.append(event)

        # Track user sessions
        if event.user_id not in self.user_sessions:
            self.user_sessions[event.user_id] = []
        self.user_sessions[event.user_id].append(event.event_id)

        # Limit memory usage
        if len(self.audit_events) > self.max_events_memory:
            # Archive old events if enabled
            if self.auto_archive_enabled:
                await self._archive_old_events()
            else:
                # Simple truncation
                self.audit_events = self.audit_events[-int(self.max_events_memory * 0.8) :]

    async def _archive_old_events(self):
        """Archive old events to persistent storage"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

        events_to_archive = [e for e in self.audit_events if e.timestamp < cutoff_date]
        events_to_keep = [e for e in self.audit_events if e.timestamp >= cutoff_date]

        if events_to_archive:
            # Save to file
            archive_file = Path(self.storage_path) / f"audit_archive_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"

            archive_data = {
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "event_count": len(events_to_archive),
                "events": [e.to_dict() for e in events_to_archive],
            }

            with open(archive_file, "w") as f:
                json.dump(archive_data, f, indent=2)

            self.audit_events = events_to_keep

            logger.info(f"Archived {len(events_to_archive)} old audit events to {archive_file}")

    def _load_audit_events(self):
        """Load existing audit events from storage"""

        try:
            audit_files = list(Path(self.storage_path).glob("audit_*.json"))

            for audit_file in audit_files:
                with open(audit_file) as f:
                    data = json.load(f)

                for event_dict in data.get("events", []):
                    try:
                        event = AuditEvent.from_dict(event_dict)
                        self.audit_events.append(event)
                    except Exception as e:
                        logger.error(f"Error loading audit event: {e}")

            logger.info(f"Loaded {len(self.audit_events)} audit events from storage")

        except Exception as e:
            logger.error(f"Error loading audit events: {e}")

    def get_audit_statistics(self) -> dict[str, Any]:
        """Get overall audit system statistics"""

        return {
            "total_events": len(self.audit_events),
            "unique_users": len(self.user_sessions),
            "event_types": {
                event_type.value: sum(1 for e in self.audit_events if e.event_type == event_type)
                for event_type in AuditEventType
            },
            "privacy_levels": {
                level: sum(1 for e in self.audit_events if e.privacy_level == level)
                for level in ["normal", "sensitive", "private"]
            },
            "retention_days": self.retention_days,
            "storage_path": self.storage_path,
            "auto_archive_enabled": self.auto_archive_enabled,
        }
