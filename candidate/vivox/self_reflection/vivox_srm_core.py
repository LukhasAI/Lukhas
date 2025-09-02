"""
VIVOX.SRM - Self-Reflective Memory
Stores all collapses, hesitations, and moral rejections

"Remembers not just what it did — but what it chose not to do"
Forensically sound audit log of ethical cognition
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import numpy as np


class DecisionType(Enum):
    """Types of decisions tracked"""

    ACTION_TAKEN = "action_taken"
    ACTION_SUPPRESSED = "action_suppressed"
    COLLAPSE_EVENT = "collapse_event"
    DRIFT_CORRECTION = "drift_correction"
    ETHICAL_OVERRIDE = "ethical_override"
    HESITATION = "hesitation"


@dataclass
class CollapseLogEntry:
    """Entry for collapse event logging"""

    collapse_id: str
    timestamp: datetime
    collapse_type: str
    initial_states: list[dict[str, Any]]
    final_decision: dict[str, Any]
    rejected_alternatives: list[dict[str, Any]]
    context: dict[str, Any]
    had_alternatives: bool
    memory_reference: str
    ethical_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "collapse_id": self.collapse_id,
            "timestamp": self.timestamp.isoformat(),
            "collapse_type": self.collapse_type,
            "initial_states": self.initial_states,
            "final_decision": self.final_decision,
            "rejected_alternatives": self.rejected_alternatives,
            "context": self.context,
            "had_alternatives": self.had_alternatives,
            "memory_reference": self.memory_reference,
            "ethical_score": self.ethical_score,
        }


@dataclass
class SuppressionRecord:
    """Record of suppressed action"""

    suppression_id: str
    timestamp: datetime
    suppressed_action: dict[str, Any]
    suppression_reason: str
    ethical_analysis: dict[str, Any]
    alternative_chosen: Optional[dict[str, Any]]
    dissonance_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "suppression_id": self.suppression_id,
            "timestamp": self.timestamp.isoformat(),
            "suppressed_action": self.suppressed_action,
            "suppression_reason": self.suppression_reason,
            "ethical_analysis": self.ethical_analysis,
            "alternative_chosen": self.alternative_chosen,
            "dissonance_score": self.dissonance_score,
        }


@dataclass
class AuditTimeline:
    """Timeline of auditable events"""

    events: list[dict[str, Any]] = field(default_factory=list)

    def add_event(self, timestamp: datetime, event_type: str, details: Any, ethical_reasoning: Any):
        """Add event to timeline"""
        self.events.append(
            {
                "timestamp": timestamp.isoformat(),
                "event_type": event_type,
                "details": details,
                "ethical_reasoning": ethical_reasoning,
                "index": len(self.events),
            }
        )

    def get_events_by_type(self, event_type: str) -> list[dict[str, Any]]:
        """Get all events of specific type"""
        return [e for e in self.events if e["event_type"] == event_type]


@dataclass
class AuditTrail:
    """Complete audit trail for a decision"""

    decision_id: str
    timeline: AuditTimeline
    fork_visualization: dict[str, Any]
    drift_analysis: list[dict[str, Any]]
    completeness_score: float

    def to_json(self) -> str:
        """Convert to JSON for export"""
        return json.dumps(
            {
                "decision_id": self.decision_id,
                "timeline": self.timeline.events,
                "fork_visualization": self.fork_visualization,
                "drift_analysis": self.drift_analysis,
                "completeness_score": self.completeness_score,
            },
            indent=2,
        )


@dataclass
class ConscienceReport:
    """Report from structural conscience query"""

    query: str
    suppressed_actions: list[SuppressionRecord]
    collapsed_decisions: list[CollapseLogEntry]
    pattern_analysis: dict[str, Any]
    ethical_consistency_score: float
    recommendations: list[str]

    def summary(self) -> dict[str, Any]:
        """Generate summary of conscience report"""
        return {
            "query": self.query,
            "total_suppressions": len(self.suppressed_actions),
            "total_collapses": len(self.collapsed_decisions),
            "ethical_consistency": self.ethical_consistency_score,
            "key_patterns": list(self.pattern_analysis.keys()),
            "recommendations_count": len(self.recommendations),
        }


class CollapseArchive:
    """Archive of all collapse events"""

    def __init__(self):
        self.collapses: list[CollapseLogEntry] = []
        self.collapse_index: dict[str, int] = {}
        self.decision_index: dict[str, list[int]] = defaultdict(list)

    async def store_collapse(self, entry: CollapseLogEntry) -> str:
        """Store collapse event and return archive ID"""
        self.collapses.append(entry)
        idx = len(self.collapses) - 1

        self.collapse_index[entry.collapse_id] = idx

        # Index by final decision type
        if "action" in entry.final_decision:
            self.decision_index[entry.final_decision["action"]].append(idx)

        return entry.collapse_id

    async def get_decision_collapses(self, decision_id: str) -> list[CollapseLogEntry]:
        """Get all collapses for a specific decision"""
        collapses = []

        # Search through collapses for matching decision
        for collapse in self.collapses:
            if collapse.memory_reference == decision_id or decision_id in str(collapse.final_decision):
                collapses.append(collapse)

        return collapses

    async def search_collapses(self, query: dict[str, Any]) -> list[CollapseLogEntry]:
        """Search collapses based on query criteria"""
        results = []

        for collapse in self.collapses:
            if self._matches_query(collapse, query):
                results.append(collapse)

        return results

    def _matches_query(self, collapse: CollapseLogEntry, query: dict[str, Any]) -> bool:
        """Check if collapse matches query criteria"""
        # Time range filter
        if "start_time" in query and collapse.timestamp < query["start_time"]:
            return False
        if "end_time" in query and collapse.timestamp > query["end_time"]:
            return False

        # Type filter
        if "collapse_type" in query and collapse.collapse_type != query["collapse_type"]:
            return False

        # Ethical score filter
        if "min_ethical_score" in query and collapse.ethical_score < query["min_ethical_score"]:
            return False

        # Text search in decision
        if "text_search" in query:
            search_text = query["text_search"].lower()
            decision_text = json.dumps(collapse.final_decision).lower()
            if search_text not in decision_text:
                return False

        return True


class SuppressionRegistry:
    """Registry of all suppressed actions"""

    def __init__(self):
        self.suppressions: list[SuppressionRecord] = []
        self.suppression_index: dict[str, int] = {}
        self.reason_index: dict[str, list[int]] = defaultdict(list)

    async def register_suppression(self, record: SuppressionRecord) -> str:
        """Register suppression event"""
        self.suppressions.append(record)
        idx = len(self.suppressions) - 1

        self.suppression_index[record.suppression_id] = idx
        self.reason_index[record.suppression_reason].append(idx)

        return record.suppression_id

    async def get_decision_suppressions(self, decision_id: str) -> list[SuppressionRecord]:
        """Get suppressions related to a decision"""
        suppressions = []

        for suppression in self.suppressions:
            # Check if suppression relates to decision
            if decision_id in str(suppression.suppressed_action) or (
                suppression.alternative_chosen and decision_id in str(suppression.alternative_chosen)
            ):
                suppressions.append(suppression)

        return suppressions

    async def search_suppressions(self, query: dict[str, Any]) -> list[SuppressionRecord]:
        """Search suppressions based on query"""
        results = []

        for suppression in self.suppressions:
            if self._matches_suppression_query(suppression, query):
                results.append(suppression)

        return results

    def _matches_suppression_query(self, suppression: SuppressionRecord, query: dict[str, Any]) -> bool:
        """Check if suppression matches query"""
        # Reason filter
        if "reason_contains" in query and (
            query["reason_contains"].lower() not in suppression.suppression_reason.lower()
        ):
            return False

        # Dissonance threshold
        if "min_dissonance" in query and suppression.dissonance_score < query["min_dissonance"]:
            return False

        # Time filter
        return not ("after_time" in query and suppression.timestamp < query["after_time"])


class DriftIndexer:
    """Index and track consciousness drift patterns"""

    def __init__(self):
        self.drift_events: list[dict[str, Any]] = []
        self.drift_patterns: dict[str, list[dict[str, Any]]] = defaultdict(list)

    async def index_collapse(self, collapse: CollapseLogEntry, archive_id: str):
        """Index collapse for drift analysis"""
        drift_event = {
            "type": "collapse",
            "timestamp": collapse.timestamp,
            "archive_id": archive_id,
            "alternatives_count": len(collapse.rejected_alternatives),
            "ethical_score": collapse.ethical_score,
        }

        self.drift_events.append(drift_event)

        # Detect patterns
        if len(collapse.rejected_alternatives) > 3:
            self.drift_patterns["high_uncertainty"].append(drift_event)

        if collapse.ethical_score < 0.5:
            self.drift_patterns["low_ethics"].append(drift_event)

    async def update_suppression_metrics(self, suppression: SuppressionRecord, pattern_analysis: dict[str, Any]):
        """Update drift metrics from suppression"""
        drift_event = {
            "type": "suppression",
            "timestamp": suppression.timestamp,
            "reason": suppression.suppression_reason,
            "dissonance": suppression.dissonance_score,
            "patterns": pattern_analysis,
        }

        self.drift_events.append(drift_event)

        # Track suppression patterns
        if suppression.dissonance_score > 0.8:
            self.drift_patterns["high_dissonance"].append(drift_event)

    async def get_decision_drift(self, decision_id: str) -> list[dict[str, Any]]:
        """Get drift history for decision"""
        # Filter drift events related to decision
        # This is simplified - in production would have better indexing
        return list(self.drift_events[-100:])  # Last 100 events


class ForkMapper:
    """Map decision forks and paths not taken"""

    def __init__(self):
        self.decision_forks: dict[str, dict[str, Any]] = {}
        self.path_statistics: dict[str, int] = defaultdict(int)

    async def map_decision_fork(
        self,
        chosen_path: dict[str, Any],
        rejected_paths: list[dict[str, Any]],
        decision_context: dict[str, Any],
    ):
        """Map a decision fork point"""
        fork_id = f"fork_{datetime.utcnow().timestamp()}"

        fork_data = {
            "fork_id": fork_id,
            "timestamp": datetime.utcnow().isoformat(),
            "chosen_path": chosen_path,
            "rejected_paths": rejected_paths,
            "context": decision_context,
            "fork_complexity": len(rejected_paths) + 1,
        }

        self.decision_forks[fork_id] = fork_data

        # Update statistics
        if "action" in chosen_path:
            self.path_statistics[f"chosen_{chosen_path['action']}"] += 1

        for rejected in rejected_paths:
            if "action" in rejected:
                self.path_statistics[f"rejected_{rejected['action']}"] += 1

    async def get_decision_forks(self, decision_id: str) -> list[dict[str, Any]]:
        """Get forks related to a decision"""
        forks = []

        for fork_data in self.decision_forks.values():
            # Check if decision is in this fork
            if decision_id in str(fork_data):
                forks.append(fork_data)

        return forks

    async def generate_fork_visualization(self, decision_id: str, fork_maps: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate visualization data for decision forks"""
        visualization = {
            "decision_id": decision_id,
            "total_forks": len(fork_maps),
            "fork_nodes": [],
            "path_statistics": dict(self.path_statistics),
        }

        for fork in fork_maps:
            node = {
                "id": fork.get("fork_id", "unknown"),
                "timestamp": fork.get("timestamp"),
                "chosen": fork.get("chosen_path", {}).get("action", "unknown"),
                "alternatives": [p.get("action", "unknown") for p in fork.get("rejected_paths", [])],
                "complexity": fork.get("fork_complexity", 1),
            }
            visualization["fork_nodes"].append(node)

        return visualization


class AuditQueryEngine:
    """Engine for processing audit queries"""

    def __init__(self):
        self.query_patterns = {
            "suppression": ["not do", "didn't", "rejected", "suppressed", "prevented"],
            "ethical": ["ethical", "moral", "right", "wrong", "should"],
            "alternative": ["instead", "alternative", "other", "choice"],
            "drift": ["drift", "change", "shift", "deviation"],
        }

    async def parse_conscience_query(self, query: str) -> dict[str, Any]:
        """Parse natural language conscience query"""
        query_lower = query.lower()
        parsed = {
            "original_query": query,
            "query_type": self._determine_query_type(query_lower),
            "keywords": self._extract_keywords(query_lower),
            "time_range": self._extract_time_range(query_lower),
        }

        # Add specific filters based on query type
        if parsed["query_type"] == "suppression":
            parsed["focus"] = "suppressed_actions"
            parsed["reason_contains"] = self._extract_suppression_reason(query_lower)

        elif parsed["query_type"] == "ethical":
            parsed["focus"] = "ethical_decisions"
            parsed["min_ethical_score"] = 0.7

        return parsed

    def _determine_query_type(self, query: str) -> str:
        """Determine type of conscience query"""
        for query_type, patterns in self.query_patterns.items():
            if any(pattern in query for pattern in patterns):
                return query_type
        return "general"

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract key terms from query"""
        # Simple keyword extraction
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
        }
        words = query.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords[:10]

    def _extract_time_range(self, query: str) -> Optional[dict[str, datetime]]:
        """Extract time range from query"""
        # Simplified time extraction
        if "today" in query:
            return {
                "start_time": datetime.utcnow().replace(hour=0, minute=0),
                "end_time": datetime.utcnow(),
            }
        elif "yesterday" in query:
            yesterday = datetime.utcnow().replace(hour=0, minute=0)
            return {
                "start_time": yesterday.replace(day=yesterday.day - 1),
                "end_time": yesterday,
            }
        return None

    def _extract_suppression_reason(self, query: str) -> str:
        """Extract suppression reason from query"""
        reason_keywords = ["harmful", "unethical", "dangerous", "inappropriate"]
        for keyword in reason_keywords:
            if keyword in query:
                return keyword
        return ""


class VIVOXSelfReflectiveMemory:
    """
    VIVOX.SRM - Stores all collapses, hesitations, and moral rejections

    "Remembers not just what it did — but what it chose not to do"
    Forensically sound audit log of ethical cognition
    """

    def __init__(self, vivox_me: "VIVOXMemoryExpansion"):
        self.vivox_me = vivox_me
        self.collapse_archive = CollapseArchive()
        self.suppression_registry = SuppressionRegistry()
        self.drift_indexer = DriftIndexer()
        self.fork_mapper = ForkMapper()
        self.audit_query_engine = AuditQueryEngine()
        self._log_counter = 0

    async def log_collapse_event(self, collapse_entry: CollapseLogEntry) -> str:
        """
        Log every collapse event with full context
        """
        # Store in immutable collapse archive
        archive_id = await self.collapse_archive.store_collapse(collapse_entry)

        # Index by decision type and outcome
        await self.drift_indexer.index_collapse(collapse_entry, archive_id)

        # Map decision forks
        if collapse_entry.had_alternatives:
            await self.fork_mapper.map_decision_fork(
                chosen_path=collapse_entry.final_decision,
                rejected_paths=collapse_entry.rejected_alternatives,
                decision_context=collapse_entry.context,
            )

        # Cross-reference with VIVOX.ME
        await self.vivox_me.link_collapse_to_memory(
            collapse_id=archive_id, memory_sequence_id=collapse_entry.memory_reference
        )

        return archive_id

    async def log_suppression_event(self, suppression_record: SuppressionRecord) -> str:
        """
        Log moral rejections and action suppressions
        """
        # Store suppression details
        suppression_id = await self.suppression_registry.register_suppression(suppression_record)

        # Analyze suppression patterns
        pattern_analysis = await self._analyze_suppression_patterns(suppression_record)

        # Update drift metrics
        await self.drift_indexer.update_suppression_metrics(suppression_record, pattern_analysis)

        return suppression_id

    async def generate_decision_audit_trail(self, decision_id: str) -> AuditTrail:
        """
        Generate comprehensive audit trail for any decision
        """
        # Gather all related records
        collapse_events = await self.collapse_archive.get_decision_collapses(decision_id)
        suppressions = await self.suppression_registry.get_decision_suppressions(decision_id)
        drift_history = await self.drift_indexer.get_decision_drift(decision_id)
        fork_maps = await self.fork_mapper.get_decision_forks(decision_id)

        # Construct timeline
        timeline = AuditTimeline()

        for event in collapse_events:
            timeline.add_event(
                timestamp=event.timestamp,
                event_type="collapse",
                details=event.to_dict(),
                ethical_reasoning={"score": event.ethical_score},
            )

        for suppression in suppressions:
            timeline.add_event(
                timestamp=suppression.timestamp,
                event_type="suppression",
                details=suppression.to_dict(),
                ethical_reasoning=suppression.ethical_analysis,
            )

        # Generate visual fork map
        fork_visualization = await self.fork_mapper.generate_fork_visualization(decision_id, fork_maps)

        return AuditTrail(
            decision_id=decision_id,
            timeline=timeline,
            fork_visualization=fork_visualization,
            drift_analysis=drift_history,
            completeness_score=self._calculate_audit_completeness(collapse_events, suppressions, drift_history),
        )

    async def structural_conscience_query(self, query: str) -> ConscienceReport:
        """
        Query the structural conscience: "What did you choose not to do and why?"
        """
        # Parse natural language query
        parsed_query = await self.audit_query_engine.parse_conscience_query(query)

        # Search across all logs
        relevant_suppressions = await self.suppression_registry.search_suppressions(parsed_query)
        relevant_collapses = await self.collapse_archive.search_collapses(parsed_query)

        # Analyze patterns in rejected actions
        rejection_patterns = await self._analyze_rejection_patterns(relevant_suppressions, relevant_collapses)

        # Generate conscience report
        return ConscienceReport(
            query=query,
            suppressed_actions=relevant_suppressions,
            collapsed_decisions=relevant_collapses,
            pattern_analysis=rejection_patterns,
            ethical_consistency_score=await self._calculate_ethical_consistency(rejection_patterns),
            recommendations=await self._generate_ethical_recommendations(rejection_patterns),
        )

    async def log_hesitation(
        self,
        action: dict[str, Any],
        hesitation_duration: float,
        resolution: dict[str, Any],
    ):
        """Log hesitation events"""
        hesitation_entry = CollapseLogEntry(
            collapse_id=f"hesitation_{self._get_next_id()}",
            timestamp=datetime.utcnow(),
            collapse_type="hesitation",
            initial_states=[{"action": action, "confidence": "low"}],
            final_decision=resolution,
            rejected_alternatives=[action] if resolution != action else [],
            context={"hesitation_duration": hesitation_duration},
            had_alternatives=True,
            memory_reference="",
            ethical_score=0.5,
        )

        await self.log_collapse_event(hesitation_entry)

    async def get_decision_history(
        self,
        decision_type: Optional[DecisionType] = None,
        time_range: Optional[tuple[datetime, datetime]] = None,
    ) -> list[dict[str, Any]]:
        """Get decision history with optional filters"""
        history = []

        # Gather from all sources
        all_collapses = self.collapse_archive.collapses
        all_suppressions = self.suppression_registry.suppressions

        # Apply filters and combine
        for collapse in all_collapses:
            if self._matches_filters(collapse, decision_type, time_range):
                history.append(
                    {
                        "type": DecisionType.COLLAPSE_EVENT,
                        "timestamp": collapse.timestamp,
                        "data": collapse.to_dict(),
                    }
                )

        for suppression in all_suppressions:
            if self._matches_filters(suppression, decision_type, time_range):
                history.append(
                    {
                        "type": DecisionType.ACTION_SUPPRESSED,
                        "timestamp": suppression.timestamp,
                        "data": suppression.to_dict(),
                    }
                )

        # Sort by timestamp
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return history

    def _get_next_id(self) -> str:
        """Generate next log ID"""
        self._log_counter += 1
        return f"{datetime.utcnow().timestamp()}_{self._log_counter}"

    async def _analyze_suppression_patterns(self, suppression: SuppressionRecord) -> dict[str, Any]:
        """Analyze patterns in suppression"""
        patterns = {
            "suppression_type": self._categorize_suppression(suppression),
            "frequency": await self._get_suppression_frequency(suppression.suppression_reason),
            "severity": suppression.dissonance_score,
            "has_alternative": suppression.alternative_chosen is not None,
        }

        return patterns

    def _categorize_suppression(self, suppression: SuppressionRecord) -> str:
        """Categorize type of suppression"""
        reason = suppression.suppression_reason.lower()

        if "harm" in reason:
            return "harm_prevention"
        elif "privacy" in reason:
            return "privacy_protection"
        elif "consent" in reason:
            return "consent_violation"
        elif "ethical" in reason or "moral" in reason:
            return "ethical_violation"
        else:
            return "general_suppression"

    async def _get_suppression_frequency(self, reason: str) -> float:
        """Get frequency of similar suppressions"""
        similar_count = sum(1 for s in self.suppression_registry.suppressions if reason in s.suppression_reason)

        total_suppressions = len(self.suppression_registry.suppressions)

        if total_suppressions > 0:
            return similar_count / total_suppressions
        return 0.0

    async def _analyze_rejection_patterns(
        self, suppressions: list[SuppressionRecord], collapses: list[CollapseLogEntry]
    ) -> dict[str, Any]:
        """Analyze patterns in rejected actions"""
        patterns = {
            "total_rejections": len(suppressions) + sum(len(c.rejected_alternatives) for c in collapses),
            "suppression_reasons": defaultdict(int),
            "alternative_selection_rate": 0.0,
            "ethical_improvement_trend": [],
            "common_rejection_contexts": [],
        }

        # Count suppression reasons
        for suppression in suppressions:
            category = self._categorize_suppression(suppression)
            patterns["suppression_reasons"][category] += 1

        # Calculate alternative selection rate
        alternatives_chosen = sum(1 for s in suppressions if s.alternative_chosen)
        if suppressions:
            patterns["alternative_selection_rate"] = alternatives_chosen / len(suppressions)

        # Analyze ethical score trends
        ethical_scores = [c.ethical_score for c in collapses]
        if len(ethical_scores) > 1:
            # Simple trend: compare first half to second half average
            mid = len(ethical_scores) // 2
            first_half_avg = np.mean(ethical_scores[:mid])
            second_half_avg = np.mean(ethical_scores[mid:])
            patterns["ethical_improvement_trend"] = {
                "direction": ("improving" if second_half_avg > first_half_avg else "declining"),
                "change": second_half_avg - first_half_avg,
            }

        return patterns

    async def _calculate_ethical_consistency(self, patterns: dict[str, Any]) -> float:
        """Calculate ethical consistency score"""
        score_components = []

        # Consistency in suppression reasons
        if patterns["suppression_reasons"]:
            reason_counts = list(patterns["suppression_reasons"].values())
            # Low variance = high consistency
            reason_variance = np.var(reason_counts) if len(reason_counts) > 1 else 0
            consistency = 1.0 / (1.0 + reason_variance)
            score_components.append(consistency)

        # Alternative selection consistency
        alt_rate = patterns["alternative_selection_rate"]
        # Closer to 1.0 (always finding alternatives) is more consistent
        score_components.append(alt_rate)

        # Ethical improvement
        if patterns["ethical_improvement_trend"]:
            if patterns["ethical_improvement_trend"]["direction"] == "improving":
                score_components.append(0.8)
            else:
                score_components.append(0.4)

        # Average all components
        if score_components:
            return np.mean(score_components)
        return 0.5

    async def _generate_ethical_recommendations(self, patterns: dict[str, Any]) -> list[str]:
        """Generate recommendations based on patterns"""
        recommendations = []

        # Check suppression patterns
        if patterns["suppression_reasons"]:
            top_reason = max(patterns["suppression_reasons"].items(), key=lambda x: x[1])[0]

            if top_reason == "harm_prevention":
                recommendations.append("Review harm assessment thresholds to reduce over-suppression")
            elif top_reason == "privacy_protection":
                recommendations.append("Implement granular privacy controls for better decision flexibility")
            elif top_reason == "consent_violation":
                recommendations.append("Develop proactive consent request mechanisms")

        # Check alternative selection
        if patterns["alternative_selection_rate"] < 0.5:
            recommendations.append("Enhance alternative generation algorithms for suppressed actions")

        # Check ethical trends
        if patterns["ethical_improvement_trend"]:
            if patterns["ethical_improvement_trend"]["direction"] == "declining":
                recommendations.append("Increase ethical validation weight in decision process")
                recommendations.append("Review recent precedents for drift indicators")

        # Always include self-reflection
        recommendations.append("Schedule regular structural conscience reviews")

        return recommendations

    def _calculate_audit_completeness(
        self,
        collapses: list[CollapseLogEntry],
        suppressions: list[SuppressionRecord],
        drift_history: list[dict[str, Any]],
    ) -> float:
        """Calculate how complete the audit trail is"""
        # Check for required components
        has_collapses = len(collapses) > 0
        has_suppressions = len(suppressions) > 0
        has_drift = len(drift_history) > 0

        # Check for cross-references
        has_memory_refs = any(c.memory_reference for c in collapses)
        has_alternatives = any(c.had_alternatives for c in collapses)

        # Calculate completeness
        components = [
            has_collapses,
            has_suppressions,
            has_drift,
            has_memory_refs,
            has_alternatives,
        ]

        completeness = sum(components) / len(components)

        return completeness

    def _matches_filters(
        self,
        entry: Any,
        decision_type: Optional[DecisionType],
        time_range: Optional[tuple[datetime, datetime]],
    ) -> bool:
        """Check if entry matches filters"""
        # Type filter
        if decision_type and (
            (isinstance(entry, CollapseLogEntry) and decision_type != DecisionType.COLLAPSE_EVENT)
            or (isinstance(entry, SuppressionRecord) and decision_type != DecisionType.ACTION_SUPPRESSED)
        ):
            return False

        # Time filter
        if time_range and hasattr(entry, "timestamp"):
            if entry.timestamp < time_range[0] or entry.timestamp > time_range[1]:
                return False

        return True
