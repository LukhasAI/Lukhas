import logging

logger = logging.getLogger(__name__)
# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: conflict_resolver.py
# MODULE: reasoning.conflict_resolver
# DESCRIPTION: Symbolic Contradiction & Arbitration Engine - Identifies, classifies,
#              and resolves symbolic contradictions within reasoning, memory, or dream
#              pathways. Acts as arbitration layer for inconsistencies across collapse
#              events, emotional states, and ethical mismatches.
# ΛNOTE: This module provides the core conflict detection and resolution capabilities
#        for managing symbolic contradictions in the LUKHAS Cognitive system.
# DEPENDENCIES: structlog, datetime, typing, enum, dataclasses, uuid, json
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Initialize structured logger for this module
logger.info("Initializing conflict_resolver module.", module_path=__file__)


class ConflictType(Enum):
    """Classification of contradiction types in symbolic reasoning."""

    ETHICAL = "ethical"  # Ethics/values contradiction
    LOGICAL = "logical"  # Pure logical inconsistency
    EMOTIONAL = "emotional"  # Emotional state conflicts
    MEMORY = "memory"  # Memory/historical conflicts
    LOOP = "loop"  # Recursive/circular reasoning
    DRIFT = "drift"  # Symbolic drift conflicts
    GLYPH = "glyph"  # GLYPH field contradictions
    TEMPORAL = "temporal"  # Time-based inconsistencies
    UNKNOWN = "unknown"  # Unclassified conflicts


class ResolutionMode(Enum):
    """Strategies for resolving symbolic contradictions."""

    MERGE = "merge"  # Combine conflicting paths with entropy boost
    VETO = "veto"  # Discard one based on priority/ethics/recency
    SUPPRESS = "suppress"  # Quarantine until conditions settle
    ESCALATE = "escalate"  # Forward to collapse_reasoner.py
    FREEZE = "freeze"  # Lock reasoning path, emit alert
    RECONCILE = "reconcile"  # Attempt to find middle ground
    ISOLATE = "isolate"  # Separate conflicting components


class ConflictSeverity(Enum):
    """Severity levels for conflicts."""

    MINOR = "minor"  # Low-impact contradiction
    MODERATE = "moderate"  # Medium-impact contradiction
    MAJOR = "major"  # High-impact contradiction
    CRITICAL = "critical"  # System-threatening contradiction


@dataclass
class SymbolicFragment:
    """Represents a symbolic reasoning fragment for conflict analysis."""

    fragment_id: str
    content: dict[str, Any]
    source_module: str
    timestamp: str
    confidence: float = 0.0
    entropy: float = 0.0
    emotional_weight: float = 0.0
    ethical_score: float = 0.0
    glyph_signature: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContradictionReport:
    """Captures details of detected symbolic contradictions."""

    report_id: str
    conflicting_fragments: list[SymbolicFragment]
    conflict_type: ConflictType
    severity: ConflictSeverity
    origins: list[str]
    entropy_delta: float
    confidence_impact: float
    glyph_conflicts: list[str] = field(default_factory=list)
    ethical_violations: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictResolutionResult:
    """Result of conflict resolution process."""

    resolution_id: str
    original_report: ContradictionReport
    resolution_mode: ResolutionMode
    resolved_fragments: list[SymbolicFragment]
    eliminated_fragments: list[str]
    risk_score: float
    mutation_context: dict[str, Any]
    confidence_adjustment: float
    entropy_adjustment: float
    resolution_success: bool
    audit_trail: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SymbolicConflictResolver:
    """
    Symbolic Contradiction & Arbitration Engine for LUKHAS Cognitive AI.

    Identifies, classifies, and resolves symbolic contradictions within reasoning,
    memory, or dream pathways. Acts as the arbitration layer for inconsistencies
    detected across collapse events, emotional states, or ethical mismatches.
    """

    def __init__(
        self,
        severity_threshold: float = 0.7,
        escalation_threshold: float = 0.8,
        resolution_confidence_threshold: float = 0.6,
        config: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the Symbolic Conflict Resolver.

        Args:
            severity_threshold: Minimum severity for conflict resolution
            escalation_threshold: Threshold for escalating to collapse_reasoner
            resolution_confidence_threshold: Minimum confidence for resolution success
            config: Additional configuration parameters
        """
        self.logger = logger.bind(component="SymbolicConflictResolver")
        self.logger.info("Initializing Symbolic Conflict Resolver")

        self.severity_threshold = severity_threshold
        self.escalation_threshold = escalation_threshold
        self.resolution_confidence_threshold = resolution_confidence_threshold
        self.config = config or {}

        # Resolution history for learning and audit
        self.resolution_history: list[ConflictResolutionResult] = []

        # Conflict detection patterns
        self.contradiction_patterns = self._initialize_patterns()

        # Statistics tracking
        self.conflict_stats = {
            "total_conflicts": 0,
            "resolved_conflicts": 0,
            "escalated_conflicts": 0,
            "suppressed_conflicts": 0,
        }

        self.logger.info(
            "Symbolic Conflict Resolver initialized",
            severity_threshold=severity_threshold,
            escalation_threshold=escalation_threshold,
            resolution_confidence_threshold=resolution_confidence_threshold,
        )

    def detect_symbolic_conflict(self, inputs: list[SymbolicFragment], context: dict) -> Optional[ContradictionReport]:
        """
        Analyzes symbolic statements, emotional states, and memory references
        for contradiction patterns. Returns report if conflict found.

        Args:
            inputs: List of symbolic fragments to analyze
            context: Contextual information for analysis

        Returns:
            ContradictionReport if conflict detected, None otherwise
        """
        detection_id = f"conflict_detect_{uuid.uuid4().hex[:12]}"
        method_logger = self.logger.bind(detection_id=detection_id)
        method_logger.info(
            "Starting symbolic conflict detection",
            fragment_count=len(inputs),
            context_keys=list(context.keys()),
        )

        try:
            if len(inputs) < 2:
                method_logger.debug("Insufficient fragments for conflict detection")
                return None

            # Detect various types of conflicts
            conflicts_found = []

            # Logical contradictions
            logical_conflicts = self._detect_logical_contradictions(inputs)
            conflicts_found.extend(logical_conflicts)

            # Ethical contradictions
            ethical_conflicts = self._detect_ethical_contradictions(inputs)
            conflicts_found.extend(ethical_conflicts)

            # Emotional contradictions
            emotional_conflicts = self._detect_emotional_contradictions(inputs)
            conflicts_found.extend(emotional_conflicts)

            # Memory/historical contradictions
            memory_conflicts = self._detect_memory_contradictions(inputs, context)
            conflicts_found.extend(memory_conflicts)

            # GLYPH field contradictions
            glyph_conflicts = self._detect_glyph_contradictions(inputs)
            conflicts_found.extend(glyph_conflicts)

            # Loop detection
            loop_conflicts = self._detect_recursive_loops(inputs)
            conflicts_found.extend(loop_conflicts)

            if not conflicts_found:
                method_logger.debug("No conflicts detected")
                return None

            # Create contradiction report for the most severe conflict
            primary_conflict = max(conflicts_found, key=lambda c: c["severity_score"])

            severity = self._calculate_severity(primary_conflict, inputs)
            entropy_delta = self._calculate_entropy_delta(inputs, primary_conflict)
            confidence_impact = self._calculate_confidence_impact(inputs, primary_conflict)

            report = ContradictionReport(
                report_id=f"contradiction_{uuid.uuid4().hex[:12]}",
                conflicting_fragments=primary_conflict["fragments"],
                conflict_type=primary_conflict["type"],
                severity=severity,
                origins=[f.source_module for f in primary_conflict["fragments"]],
                entropy_delta=entropy_delta,
                confidence_impact=confidence_impact,
                glyph_conflicts=primary_conflict.get("glyph_conflicts", []),
                ethical_violations=primary_conflict.get("ethical_violations", []),
                metadata={
                    "detection_id": detection_id,
                    "context_snapshot": context,
                    "all_conflicts": conflicts_found,
                    "pattern_matches": primary_conflict.get("patterns", []),
                },
            )

            self.conflict_stats["total_conflicts"] += 1

            method_logger.info(
                "Conflict detected",
                report_id=report.report_id,
                conflict_type=report.conflict_type.value,
                severity=report.severity.value,
                fragments_involved=len(report.conflicting_fragments),
                entropy_delta=entropy_delta,
            )

            return report

        except Exception as e:
            method_logger.error(
                "Error during conflict detection",
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True,
            )
            return None

    def classify_contradiction(self, report: ContradictionReport) -> ConflictType:
        """
        Classifies the nature of the contradiction: ethical, logical, emotional,
        memory-based, drift-induced, or symbolic loop.

        Args:
            report: The contradiction report to classify

        Returns:
            ConflictType: The primary classification of the conflict
        """
        self.logger.debug(
            "Classifying contradiction",
            report_id=report.report_id,
            initial_type=report.conflict_type.value,
        )

        try:
            # Start with the detected type but refine based on additional analysis
            classification_scores = dict.fromkeys(ConflictType, 0.0)

            # Analyze fragment content for classification clues
            for fragment in report.conflicting_fragments:
                content = fragment.content

                # Ethical classification
                if fragment.ethical_score < 0.3 or "ethics" in str(content).lower():
                    classification_scores[ConflictType.ETHICAL] += 0.3

                # Emotional classification
                if abs(fragment.emotional_weight - 0.5) > 0.3:
                    classification_scores[ConflictType.EMOTIONAL] += 0.2

                # Memory classification
                if fragment.source_module.startswith("memory") or "memory" in str(content).lower():
                    classification_scores[ConflictType.MEMORY] += 0.25

                # Loop classification
                if self._detect_circular_references(fragment, report.conflicting_fragments):
                    classification_scores[ConflictType.LOOP] += 0.4

                # GLYPH classification
                if fragment.glyph_signature and len(report.glyph_conflicts) > 0:
                    classification_scores[ConflictType.GLYPH] += 0.3

                # Logical classification
                logical_keywords = [
                    "contradiction",
                    "inconsistent",
                    "paradox",
                    "impossible",
                ]
                if any(keyword in str(content).lower() for keyword in logical_keywords):
                    classification_scores[ConflictType.LOGICAL] += 0.25

            # Boost the original detected type
            classification_scores[report.conflict_type] += 0.5

            # Select highest scoring classification
            final_classification = max(classification_scores, key=classification_scores.get)

            self.logger.debug(
                "Contradiction classified",
                report_id=report.report_id,
                original_type=report.conflict_type.value,
                final_type=final_classification.value,
                scores=classification_scores,
            )

            return final_classification

        except Exception as e:
            self.logger.error(
                "Error classifying contradiction",
                report_id=report.report_id,
                error=str(e),
                exc_info=True,
            )
            return ConflictType.UNKNOWN

    def resolve_conflict(self, report: ContradictionReport, strategy: ResolutionMode) -> ConflictResolutionResult:
        """
        Attempts to resolve the contradiction using strategies like merge,
        priority override, historical reweighting, or GLYPH suppression.

        Args:
            report: The contradiction report to resolve
            strategy: The resolution strategy to apply

        Returns:
            ConflictResolutionResult: The resolution outcome and metadata
        """
        resolution_id = f"resolve_{uuid.uuid4().hex[:12]}"
        method_logger = self.logger.bind(resolution_id=resolution_id, report_id=report.report_id)
        method_logger.info(
            "Starting conflict resolution",
            conflict_type=report.conflict_type.value,
            severity=report.severity.value,
            strategy=strategy.value,
        )

        try:
            # Apply the selected resolution strategy
            if strategy == ResolutionMode.MERGE:
                result = self._apply_merge_strategy(report, resolution_id)
            elif strategy == ResolutionMode.VETO:
                result = self._apply_veto_strategy(report, resolution_id)
            elif strategy == ResolutionMode.SUPPRESS:
                result = self._apply_suppress_strategy(report, resolution_id)
            elif strategy == ResolutionMode.ESCALATE:
                result = self._apply_escalate_strategy(report, resolution_id)
            elif strategy == ResolutionMode.FREEZE:
                result = self._apply_freeze_strategy(report, resolution_id)
            elif strategy == ResolutionMode.RECONCILE:
                result = self._apply_reconcile_strategy(report, resolution_id)
            elif strategy == ResolutionMode.ISOLATE:
                result = self._apply_isolate_strategy(report, resolution_id)
            else:
                # Fallback to VETO strategy
                result = self._apply_veto_strategy(report, resolution_id)

            # Update statistics
            if result.resolution_success:
                self.conflict_stats["resolved_conflicts"] += 1
            if strategy == ResolutionMode.ESCALATE:
                self.conflict_stats["escalated_conflicts"] += 1
            if strategy == ResolutionMode.SUPPRESS:
                self.conflict_stats["suppressed_conflicts"] += 1

            # Store in history
            self.resolution_history.append(result)

            method_logger.info(
                "Conflict resolution completed",
                resolution_success=result.resolution_success,
                risk_score=result.risk_score,
                fragments_resolved=len(result.resolved_fragments),
                fragments_eliminated=len(result.eliminated_fragments),
            )

            return result

        except Exception as e:
            method_logger.error(
                "Error during conflict resolution",
                error_type=type(e).__name__,
                error_message=str(e),
                exc_info=True,
            )

            # Return failure result
            return ConflictResolutionResult(
                resolution_id=resolution_id,
                original_report=report,
                resolution_mode=strategy,
                resolved_fragments=[],
                eliminated_fragments=[],
                risk_score=1.0,
                mutation_context={"error": str(e)},
                confidence_adjustment=-0.5,
                entropy_adjustment=0.5,
                resolution_success=False,
                audit_trail={"error": str(e), "strategy": strategy.value},
            )

    def emit_resolution_trace(self, result: ConflictResolutionResult) -> None:
        """
        Logs the arbitration process, linked glyphs, and symbolic outcome.
        Sends resolution metadata to the Mesh and diagnostics.

        Args:
            result: The conflict resolution result to trace
        """
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        self.logger.info(
            "Emitting resolution trace",
            trace_id=trace_id,
            resolution_id=result.resolution_id,
        )

        try:
            # Create comprehensive trace record
            trace_record = {
                "trace_id": trace_id,
                "resolution_id": result.resolution_id,
                "event_type": "conflict_resolution",
                "timestamp": result.timestamp,
                "conflict_type": result.original_report.conflict_type.value,
                "resolution_mode": result.resolution_mode.value,
                "resolution_success": result.resolution_success,
                "risk_score": result.risk_score,
                "confidence_adjustment": result.confidence_adjustment,
                "entropy_adjustment": result.entropy_adjustment,
                "fragments_resolved": len(result.resolved_fragments),
                "fragments_eliminated": len(result.eliminated_fragments),
                "mutation_context": result.mutation_context,
                "audit_trail": result.audit_trail,
                "original_conflict": {
                    "report_id": result.original_report.report_id,
                    "severity": result.original_report.severity.value,
                    "entropy_delta": result.original_report.entropy_delta,
                    "origins": result.original_report.origins,
                    "glyph_conflicts": result.original_report.glyph_conflicts,
                    "ethical_violations": result.original_report.ethical_violations,
                },
            }

            # Emit different trace types based on resolution mode
            if result.resolution_mode == ResolutionMode.MERGE:
                reconcile_logger.info("Conflict merge resolution", **trace_record)  # noqa: F821
            elif result.resolution_mode == ResolutionMode.SUPPRESS:
                suppress_logger.info("Conflict suppression", **trace_record)  # noqa: F821
            elif result.resolution_mode == ResolutionMode.ESCALATE:
                escalate_logger.warning("Conflict escalation", **trace_record)  # noqa: F821
            else:
                resolve_logger.info("Conflict resolution", **trace_record)  # noqa: F821

            # Write to JSON audit log
            self._write_resolution_audit_log(trace_record)

            # Update symbolic memory and mesh (placeholder for integration)
            self._notify_mesh_components(result)

            self.logger.info(
                "Resolution trace emitted successfully",
                trace_id=trace_id,
                resolution_id=result.resolution_id,
            )

        except Exception as e:
            self.logger.error(
                "Error emitting resolution trace",
                trace_id=trace_id,
                resolution_id=result.resolution_id,
                error=str(e),
                exc_info=True,
            )

    # Private helper methods for conflict detection

    def _initialize_patterns(self) -> dict[str, list[str]]:
        """Initialize contradiction detection patterns."""
        return {
            "logical": [
                r"(?i)(not|never|impossible).*\b(true|possible|valid)\b",
                r"(?i)\b(always|never).*\b(sometimes|never|always)\b",
                r"(?i)\b(is|are)\b.*\b(not|isn't|aren't)\b",
            ],
            "ethical": [
                r"(?i)\b(should|must|ought).*\b(shouldn't|mustn't|ought not)\b",
                r"(?i)\b(good|right|moral).*\b(bad|wrong|immoral)\b",
                r"(?i)\b(ethical|unethical)\b",
            ],
            "emotional": [
                r"(?i)\b(happy|joy).*\b(sad|grief|angry)\b",
                r"(?i)\b(positive|negative)\b.*\b(emotion|feeling|mood)\b",
                r"(?i)\b(love|like).*\b(hate|dislike)\b",
            ],
            "temporal": [
                r"(?i)\b(before|after|during).*\b(simultaneously|at the same time)\b",
                r"(?i)\b(past|present|future)\b.*\b(contradiction|inconsistent)\b",
            ],
        }

    def _detect_logical_contradictions(self, fragments: list[SymbolicFragment]) -> list[dict]:
        """Detect logical contradictions between fragments."""
        conflicts = []

        for i, frag1 in enumerate(fragments):
            for _j, frag2 in enumerate(fragments[i + 1 :], i + 1):
                # Check for direct logical contradictions
                content1 = str(frag1.content).lower()
                content2 = str(frag2.content).lower()

                # Pattern-based detection
                for pattern in self.contradiction_patterns["logical"]:
                    if re.search(pattern, content1 + " " + content2):
                        conflicts.append(
                            {
                                "type": ConflictType.LOGICAL,
                                "fragments": [frag1, frag2],
                                "severity_score": 0.8,
                                "patterns": [pattern],
                                "description": "Logical contradiction detected",
                            }
                        )

                # Confidence contradiction (high confidence in opposite statements)
                if frag1.confidence > 0.8 and frag2.confidence > 0.8 and abs(frag1.confidence - frag2.confidence) < 0.1:
                    # Check for semantic opposition (simplified)
                    if ("not" in content1 and "not" not in content2) or ("not" not in content1 and "not" in content2):
                        conflicts.append(
                            {
                                "type": ConflictType.LOGICAL,
                                "fragments": [frag1, frag2],
                                "severity_score": 0.7,
                                "patterns": ["confidence_contradiction"],
                                "description": "High-confidence contradictory statements",
                            }
                        )

        return conflicts

    def _detect_ethical_contradictions(self, fragments: list[SymbolicFragment]) -> list[dict]:
        """Detect ethical contradictions between fragments."""
        conflicts = []

        for i, frag1 in enumerate(fragments):
            for _j, frag2 in enumerate(fragments[i + 1 :], i + 1):
                # Ethical score contradiction
                if abs(frag1.ethical_score - frag2.ethical_score) > 0.6:
                    conflicts.append(
                        {
                            "type": ConflictType.ETHICAL,
                            "fragments": [frag1, frag2],
                            "severity_score": abs(frag1.ethical_score - frag2.ethical_score),
                            "patterns": ["ethical_score_divergence"],
                            "description": "Ethical scoring contradiction",
                            "ethical_violations": ["ethical_score_conflict"],
                        }
                    )

                # Pattern-based ethical contradiction detection
                content1 = str(frag1.content).lower()
                content2 = str(frag2.content).lower()

                for pattern in self.contradiction_patterns["ethical"]:
                    if re.search(pattern, content1 + " " + content2):
                        conflicts.append(
                            {
                                "type": ConflictType.ETHICAL,
                                "fragments": [frag1, frag2],
                                "severity_score": 0.75,
                                "patterns": [pattern],
                                "description": "Ethical statement contradiction",
                                "ethical_violations": ["pattern_based_ethical_conflict"],
                            }
                        )

        return conflicts

    def _detect_emotional_contradictions(self, fragments: list[SymbolicFragment]) -> list[dict]:
        """Detect emotional contradictions between fragments."""
        conflicts = []

        for i, frag1 in enumerate(fragments):
            for _j, frag2 in enumerate(fragments[i + 1 :], i + 1):
                # Emotional weight contradiction
                weight_diff = abs(frag1.emotional_weight - frag2.emotional_weight)
                if weight_diff > 0.7:
                    conflicts.append(
                        {
                            "type": ConflictType.EMOTIONAL,
                            "fragments": [frag1, frag2],
                            "severity_score": weight_diff * 0.8,
                            "patterns": ["emotional_weight_divergence"],
                            "description": "Emotional weight contradiction",
                        }
                    )

                # Pattern-based emotional contradiction detection
                content1 = str(frag1.content).lower()
                content2 = str(frag2.content).lower()

                for pattern in self.contradiction_patterns["emotional"]:
                    if re.search(pattern, content1 + " " + content2):
                        conflicts.append(
                            {
                                "type": ConflictType.EMOTIONAL,
                                "fragments": [frag1, frag2],
                                "severity_score": 0.6,
                                "patterns": [pattern],
                                "description": "Emotional statement contradiction",
                            }
                        )

        return conflicts

    def _detect_memory_contradictions(self, fragments: list[SymbolicFragment], context: dict) -> list[dict]:
        """Detect memory/historical contradictions."""
        conflicts = []

        # Check for fragments from memory modules with conflicting information
        memory_fragments = [f for f in fragments if f.source_module.startswith("memory")]

        for i, frag1 in enumerate(memory_fragments):
            for _j, frag2 in enumerate(memory_fragments[i + 1 :], i + 1):
                # Temporal contradiction check
                timestamp1 = frag1.metadata.get("timestamp", frag1.timestamp)
                timestamp2 = frag2.metadata.get("timestamp", frag2.timestamp)

                if timestamp1 and timestamp2:
                    # If same time but different confidence/content, potential conflict
                    if timestamp1 == timestamp2 and abs(frag1.confidence - frag2.confidence) > 0.5:
                        conflicts.append(
                            {
                                "type": ConflictType.MEMORY,
                                "fragments": [frag1, frag2],
                                "severity_score": 0.65,
                                "patterns": ["temporal_memory_conflict"],
                                "description": "Memory fragments at same time with conflicting confidence",
                            }
                        )

        return conflicts

    def _detect_glyph_contradictions(self, fragments: list[SymbolicFragment]) -> list[dict]:
        """Detect GLYPH field contradictions."""
        conflicts = []

        # Check for conflicting GLYPH signatures
        glyph_fragments = [f for f in fragments if f.glyph_signature]

        for i, frag1 in enumerate(glyph_fragments):
            for _j, frag2 in enumerate(glyph_fragments[i + 1 :], i + 1):
                # Simple GLYPH contradiction detection (could be more sophisticated)
                if (
                    frag1.glyph_signature
                    and frag2.glyph_signature
                    and frag1.glyph_signature != frag2.glyph_signature
                    and abs(frag1.confidence - frag2.confidence) < 0.2
                ):
                    conflicts.append(
                        {
                            "type": ConflictType.GLYPH,
                            "fragments": [frag1, frag2],
                            "severity_score": 0.7,
                            "patterns": ["glyph_signature_conflict"],
                            "description": "Conflicting GLYPH signatures with similar confidence",
                            "glyph_conflicts": [
                                frag1.glyph_signature,
                                frag2.glyph_signature,
                            ],
                        }
                    )

        return conflicts

    def _detect_recursive_loops(self, fragments: list[SymbolicFragment]) -> list[dict]:
        """Detect recursive loops in reasoning."""
        conflicts = []

        # Check for circular references in fragment IDs or content
        fragment_ids = [f.fragment_id for f in fragments]

        for fragment in fragments:
            content = str(fragment.content)
            # Check if this fragment references other fragments in a circular way
            circular_refs = [fid for fid in fragment_ids if fid != fragment.fragment_id and fid in content]

            if circular_refs:
                # Check if any referenced fragments also reference this one
                for ref_id in circular_refs:
                    ref_fragment = next((f for f in fragments if f.fragment_id == ref_id), None)
                    if ref_fragment and fragment.fragment_id in str(ref_fragment.content):
                        conflicts.append(
                            {
                                "type": ConflictType.LOOP,
                                "fragments": [fragment, ref_fragment],
                                "severity_score": 0.85,
                                "patterns": ["circular_reference"],
                                "description": "Circular reference detected between fragments",
                            }
                        )

        return conflicts

    def _detect_circular_references(self, fragment: SymbolicFragment, all_fragments: list[SymbolicFragment]) -> bool:
        """Check if a fragment has circular references."""
        content = str(fragment.content)

        for other_fragment in all_fragments:
            if other_fragment.fragment_id != fragment.fragment_id and (
                other_fragment.fragment_id in content and fragment.fragment_id in str(other_fragment.content)
            ):
                return True
        return False

    def _calculate_severity(self, conflict: dict, fragments: list[SymbolicFragment]) -> ConflictSeverity:
        """Calculate the severity of a conflict."""
        base_severity = conflict["severity_score"]

        # Adjust based on fragment confidence and count
        confidence_factor = sum(f.confidence for f in conflict["fragments"]) / len(conflict["fragments"])

        # Higher confidence in conflicting statements = higher severity
        adjusted_severity = base_severity * (1 + confidence_factor * 0.3)

        if adjusted_severity >= 0.9:
            return ConflictSeverity.CRITICAL
        elif adjusted_severity >= 0.7:
            return ConflictSeverity.MAJOR
        elif adjusted_severity >= 0.4:
            return ConflictSeverity.MODERATE
        else:
            return ConflictSeverity.MINOR

    def _calculate_entropy_delta(self, fragments: list[SymbolicFragment], conflict: dict) -> float:
        """Calculate entropy delta from the conflict."""
        sum(f.entropy for f in fragments)
        conflict_entropy = sum(f.entropy for f in conflict["fragments"])

        # Conflicts generally increase entropy
        return conflict_entropy * 0.5

    def _calculate_confidence_impact(self, fragments: list[SymbolicFragment], conflict: dict) -> float:
        """Calculate the impact on confidence from the conflict."""
        sum(f.confidence for f in fragments) / len(fragments)
        conflict_confidence = sum(f.confidence for f in conflict["fragments"]) / len(conflict["fragments"])

        # Higher conflict confidence = higher impact on overall confidence
        return -(conflict_confidence * 0.3)

    # Resolution strategy implementations

    def _apply_merge_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply MERGE strategy: combine conflicting paths with entropy boost."""
        self.logger.debug("Applying MERGE strategy", resolution_id=resolution_id)

        # Create merged fragment
        merged_content = {
            "type": "merged_conflict_resolution",
            "original_fragments": [f.fragment_id for f in report.conflicting_fragments],
            "merged_confidence": sum(f.confidence for f in report.conflicting_fragments)
            / len(report.conflicting_fragments)
            * 0.7,
            "entropy_boost": 0.3,
            "resolution_note": "Fragments merged due to contradiction",
        }

        merged_fragment = SymbolicFragment(
            fragment_id=f"merged_{resolution_id[:8]}",
            content=merged_content,
            source_module="conflict_resolver",
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=merged_content["merged_confidence"],
            entropy=min(
                1.0,
                sum(f.entropy for f in report.conflicting_fragments) / len(report.conflicting_fragments) + 0.3,
            ),
            emotional_weight=sum(f.emotional_weight for f in report.conflicting_fragments)
            / len(report.conflicting_fragments),
            ethical_score=min(f.ethical_score for f in report.conflicting_fragments),  # Take minimum ethical score
            glyph_signature=f"MERGED_{resolution_id[:4]}",
        )

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.MERGE,
            resolved_fragments=[merged_fragment],
            eliminated_fragments=[f.fragment_id for f in report.conflicting_fragments],
            risk_score=0.4,
            mutation_context={
                "strategy": "merge",
                "entropy_boost": 0.3,
                "confidence_reduction": 0.3,
            },
            confidence_adjustment=-0.2,
            entropy_adjustment=0.3,
            resolution_success=True,
            audit_trail={"merge_details": merged_content},
        )

    def _apply_veto_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply VETO strategy: discard one based on priority/ethics/recency."""
        self.logger.debug("Applying VETO strategy", resolution_id=resolution_id)

        # Select fragment to keep based on scoring
        fragments = report.conflicting_fragments
        scored_fragments = []

        for fragment in fragments:
            score = (
                fragment.confidence * 0.4
                + fragment.ethical_score * 0.3
                + (1.0 - fragment.entropy) * 0.2
                + fragment.emotional_weight * 0.1
            )
            scored_fragments.append((fragment, score))

        # Keep the highest scoring fragment
        kept_fragment, best_score = max(scored_fragments, key=lambda x: x[1])
        eliminated_fragments = [f.fragment_id for f, _ in scored_fragments if f != kept_fragment]

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.VETO,
            resolved_fragments=[kept_fragment],
            eliminated_fragments=eliminated_fragments,
            risk_score=0.2,
            mutation_context={
                "strategy": "veto",
                "kept_fragment_score": best_score,
                "selection_criteria": "confidence + ethics + stability",
            },
            confidence_adjustment=0.1,
            entropy_adjustment=-0.1,
            resolution_success=True,
            audit_trail={"veto_scoring": {f.fragment_id: score for f, score in scored_fragments}},
        )

    def _apply_suppress_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply SUPPRESS strategy: quarantine until conditions settle."""
        self.logger.debug("Applying SUPPRESS strategy", resolution_id=resolution_id)

        # Create suppressed fragments with reduced influence
        suppressed_fragments = []
        for fragment in report.conflicting_fragments:
            suppressed_fragment = SymbolicFragment(
                fragment_id=f"suppressed_{fragment.fragment_id}",
                content={
                    "type": "suppressed",
                    "original_fragment": fragment.fragment_id,
                    "original_content": fragment.content,
                    "suppression_reason": "conflict_quarantine",
                },
                source_module="conflict_resolver",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=fragment.confidence * 0.1,  # Heavily reduced confidence
                entropy=fragment.entropy * 1.2,  # Increased entropy
                emotional_weight=fragment.emotional_weight * 0.5,
                ethical_score=fragment.ethical_score,
                glyph_signature=f"SUPPRESSED_{fragment.glyph_signature}",
            )
            suppressed_fragments.append(suppressed_fragment)

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.SUPPRESS,
            resolved_fragments=suppressed_fragments,
            eliminated_fragments=[],  # Nothing eliminated, just suppressed
            risk_score=0.6,
            mutation_context={
                "strategy": "suppress",
                "suppression_duration": "until_conditions_settle",
                "confidence_reduction": 0.9,
            },
            confidence_adjustment=-0.8,
            entropy_adjustment=0.2,
            resolution_success=True,
            audit_trail={"suppressed_fragments": [f.fragment_id for f in report.conflicting_fragments]},
        )

    def _apply_escalate_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply ESCALATE strategy: forward to collapse_reasoner.py."""
        self.logger.warning(
            "Applying ESCALATE strategy - forwarding to collapse_reasoner",
            resolution_id=resolution_id,
        )

        # Create escalation metadata
        escalation_context = {
            "escalation_source": "conflict_resolver",
            "original_report_id": report.report_id,
            "conflict_type": report.conflict_type.value,
            "severity": report.severity.value,
            "requires_collapse_resolution": True,
        }

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.ESCALATE,
            resolved_fragments=[],  # No resolution at this level
            eliminated_fragments=[],
            risk_score=0.9,
            mutation_context=escalation_context,
            confidence_adjustment=-0.3,
            entropy_adjustment=0.4,
            resolution_success=False,  # Not resolved here
            audit_trail={
                "escalation_reason": "conflict_too_severe_for_local_resolution",
                "recommended_collapse_type": "contradiction_density",
            },
        )

    def _apply_freeze_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply FREEZE strategy: lock reasoning path, emit alert."""
        self.logger.error(
            "Applying FREEZE strategy - locking reasoning path",
            resolution_id=resolution_id,
        )

        # Create frozen fragments
        frozen_fragments = []
        for fragment in report.conflicting_fragments:
            frozen_fragment = SymbolicFragment(
                fragment_id=f"frozen_{fragment.fragment_id}",
                content={
                    "type": "frozen",
                    "original_fragment": fragment.fragment_id,
                    "original_content": fragment.content,
                    "freeze_reason": "critical_conflict_detected",
                    "locked": True,
                },
                source_module="conflict_resolver",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=0.0,  # Zero confidence
                entropy=1.0,  # Maximum entropy
                emotional_weight=fragment.emotional_weight,
                ethical_score=0.0,  # Zero ethical score for frozen items
                glyph_signature=f"FROZEN_{fragment.glyph_signature}",
            )
            frozen_fragments.append(frozen_fragment)

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.FREEZE,
            resolved_fragments=frozen_fragments,
            eliminated_fragments=[],
            risk_score=1.0,  # Maximum risk
            mutation_context={
                "strategy": "freeze",
                "reasoning_path_locked": True,
                "requires_manual_intervention": True,
            },
            confidence_adjustment=-1.0,
            entropy_adjustment=1.0,
            resolution_success=False,
            audit_trail={
                "freeze_reason": "critical_conflict_requires_immediate_attention",
                "manual_review_required": True,
            },
        )

    def _apply_reconcile_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply RECONCILE strategy: attempt to find middle ground."""
        self.logger.debug("Applying RECONCILE strategy", resolution_id=resolution_id)

        # Create reconciled fragment that attempts to find common ground
        fragments = report.conflicting_fragments

        reconciled_content = {
            "type": "reconciled_conflict",
            "original_fragments": [f.fragment_id for f in fragments],
            "reconciliation_approach": "weighted_average_with_uncertainty",
            "confidence_note": "Reduced due to conflicting information",
        }

        # Calculate weighted averages
        total_confidence = sum(f.confidence for f in fragments)
        weights = [
            (f.confidence / total_confidence if total_confidence > 0 else 1.0 / len(fragments)) for f in fragments
        ]

        reconciled_fragment = SymbolicFragment(
            fragment_id=f"reconciled_{resolution_id[:8]}",
            content=reconciled_content,
            source_module="conflict_resolver",
            timestamp=datetime.now(timezone.utc).isoformat(),
            confidence=sum(f.confidence * w for f, w in zip(fragments, weights)) * 0.6,  # Reduced confidence
            entropy=sum(f.entropy * w for f, w in zip(fragments, weights)) + 0.2,  # Slightly increased entropy
            emotional_weight=sum(f.emotional_weight * w for f, w in zip(fragments, weights)),
            ethical_score=sum(f.ethical_score * w for f, w in zip(fragments, weights)),
            glyph_signature=f"RECONCILED_{resolution_id[:4]}",
        )

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.RECONCILE,
            resolved_fragments=[reconciled_fragment],
            eliminated_fragments=[f.fragment_id for f in fragments],
            risk_score=0.3,
            mutation_context={
                "strategy": "reconcile",
                "weighting_method": "confidence_based",
                "uncertainty_increase": 0.2,
            },
            confidence_adjustment=-0.3,
            entropy_adjustment=0.2,
            resolution_success=True,
            audit_trail={"reconciliation_weights": {f.fragment_id: w for f, w in zip(fragments, weights)}},
        )

    def _apply_isolate_strategy(self, report: ContradictionReport, resolution_id: str) -> ConflictResolutionResult:
        """Apply ISOLATE strategy: separate conflicting components."""
        self.logger.debug("Applying ISOLATE strategy", resolution_id=resolution_id)

        # Create isolated versions of fragments with reduced cross-references
        isolated_fragments = []
        for i, fragment in enumerate(report.conflicting_fragments):
            isolated_fragment = SymbolicFragment(
                fragment_id=f"isolated_{fragment.fragment_id}_{i}",
                content={
                    "type": "isolated",
                    "original_fragment": fragment.fragment_id,
                    "original_content": fragment.content,
                    "isolation_context": f"separated_due_to_conflict_{resolution_id}",
                },
                source_module="conflict_resolver",
                timestamp=datetime.now(timezone.utc).isoformat(),
                confidence=fragment.confidence * 0.8,  # Slightly reduced confidence
                entropy=fragment.entropy + 0.1,  # Slightly increased entropy
                emotional_weight=fragment.emotional_weight,
                ethical_score=fragment.ethical_score,
                glyph_signature=f"ISOLATED_{i}_{fragment.glyph_signature}",
            )
            isolated_fragments.append(isolated_fragment)

        return ConflictResolutionResult(
            resolution_id=resolution_id,
            original_report=report,
            resolution_mode=ResolutionMode.ISOLATE,
            resolved_fragments=isolated_fragments,
            eliminated_fragments=[],  # Nothing eliminated, just isolated
            risk_score=0.4,
            mutation_context={
                "strategy": "isolate",
                "isolation_method": "separate_contexts",
                "cross_reference_removal": True,
            },
            confidence_adjustment=-0.1,
            entropy_adjustment=0.1,
            resolution_success=True,
            audit_trail={
                "isolation_mapping": {
                    f.fragment_id: isolated.fragment_id
                    for f, isolated in zip(report.conflicting_fragments, isolated_fragments)
                }
            },
        )

    def _write_resolution_audit_log(self, trace_record: dict[str, Any]) -> None:
        """Write resolution trace to persistent audit log."""
        try:
            # Write to JSON log file
            f"audit/conflict_resolution_log_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"

            # In a real implementation, this would write to actual files
            # For now, use structured logging
            audit_logger.info("Conflict resolution audit", **trace_record)  # noqa: F821

        except Exception as e:
            self.logger.error("Failed to write resolution audit log", error=str(e))

    def _notify_mesh_components(self, result: ConflictResolutionResult) -> None:
        """Notify relevant mesh components about resolution."""
        # Placeholder for mesh integration
        mesh_logger.info(  # noqa: F821
            "Conflict resolution notification",
            resolution_id=result.resolution_id,
            conflict_type=result.original_report.conflict_type.value,
            resolution_mode=result.resolution_mode.value,
            success=result.resolution_success,
            risk_score=result.risk_score,
        )

        # Integration hooks to other modules would go here
        # - memory/ modules for memory conflict resolutions
        # - ethics/ modules for ethical conflict resolutions
        # - collapse_reasoner.py for escalations

    def get_resolution_statistics(self) -> dict[str, Any]:
        """Get statistics about conflict resolutions."""
        return {
            "total_conflicts": self.conflict_stats["total_conflicts"],
            "resolved_conflicts": self.conflict_stats["resolved_conflicts"],
            "escalated_conflicts": self.conflict_stats["escalated_conflicts"],
            "suppressed_conflicts": self.conflict_stats["suppressed_conflicts"],
            "resolution_rate": (
                self.conflict_stats["resolved_conflicts"] / max(1, self.conflict_stats["total_conflicts"])
            ),
            "recent_resolutions": [
                {
                    "resolution_id": r.resolution_id,
                    "conflict_type": r.original_report.conflict_type.value,
                    "resolution_mode": r.resolution_mode.value,
                    "success": r.resolution_success,
                    "risk_score": r.risk_score,
                }
                for r in self.resolution_history[-10:]
            ],
            "configuration": {
                "severity_threshold": self.severity_threshold,
                "escalation_threshold": self.escalation_threshold,
                "resolution_confidence_threshold": self.resolution_confidence_threshold,
            },
        }


# Export main classes
__all__ = [
    "ConflictResolutionResult",
    "ConflictSeverity",
    "ConflictType",
    "ContradictionReport",
    "ResolutionMode",
    "SymbolicConflictResolver",
    "SymbolicFragment",
]

# CLAUDE_EDIT_v0.1 - Initial implementation of symbolic conflict resolver
logger.info("conflict_resolver module initialization complete")

# ═══════════════════════════════════════════════════════════════════════════
