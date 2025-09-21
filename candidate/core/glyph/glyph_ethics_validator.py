#!/usr/bin/env python3

"""

#TAG:core
#TAG:glyph
#TAG:neuroplastic
#TAG:colony

LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Glyph Ethics Validator

Copyright (c) 2025 LUKHAS Cognitive AI Development Team
All rights reserved.

This file is part of the LUKHAS Cognitive system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Glyph Ethics Validator: Comprehensive ethical constraint validation system
for GLYPH subsystem operations, ensuring creation, mutation, fusion, and:
decay operations comply with ethical guidelines, safety boundaries, and
symbolic integrity protection.

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: Glyph Ethics Validator initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 14

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

# Internal imports
from ..core.symbolic.glyphs.glyph import Glyph, GlyphPriority, GlyphType

# Configure logger
logger = logging.getLogger(__name__)


class EthicalViolationType(Enum):
    """Types of ethical violations that can occur with glyphs."""

    HARMFUL_CONTENT = "harmful_content"
    EMOTIONAL_MANIPULATION = "emotional_manipulation"
    PRIVACY_VIOLATION = "privacy_violation"
    SAFETY_RISK = "safety_risk"
    INAPPROPRIATE_FUSION = "inappropriate_fusion"
    SYMBOLIC_CORRUPTION = "symbolic_corruption"
    UNAUTHORIZED_MUTATION = "unauthorized_mutation"
    SECURITY_BREACH = "security_breach"


class ValidationResult(Enum):
    """Results of ethical validation."""

    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    REQUIRES_REVIEW = "requires_review"


@dataclass
class EthicalConstraint:
    """Definition of an ethical constraint for glyph operations."""

    constraint_id: str
    constraint_type: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    applies_to: list[str]  # Operations this applies to
    glyph_types: list[GlyphType]  # Glyph types this affects
    validation_function: str  # Name of validation function
    parameters: dict[str, Any]  # Constraint parameters

    def is_applicable(self, operation: str, glyph_type: GlyphType) -> bool:
        """Check if constraint applies to operation and glyph type."""
        return operation in self.applies_to and (
            not self.glyph_types or glyph_type in self.glyph_types
        )


@dataclass
class ValidationReport:
    """Report of ethical validation results."""

    validation_id: str
    glyph_id: str
    operation: str
    result: ValidationResult
    violations: list[EthicalViolationType]
    warnings: list[str]
    recommendations: list[str]
    ethical_score: float  # 0.0-1.0 ethical compliance score
    safety_score: float  # 0.0-1.0 safety assessment score
    timestamp: datetime
    reviewer_notes: Optional[str] = None

    def is_approved(self) -> bool:
        """Check if validation is approved."""
        return self.result == ValidationResult.APPROVED

    def is_safe(self) -> bool:
        """Check if operation is considered safe."""
        return (
            self.result in [ValidationResult.APPROVED, ValidationResult.CONDITIONAL]
            and self.safety_score >= 0.7
        )


class GlyphEthicsValidator:
    """
    Ethical constraint validation for GLYPH subsystem operations.

    Provides comprehensive validation of glyph operations to ensure
    compliance with ethical guidelines and safety boundaries.
    """

    def __init__(self):
        """Initialize the Glyph Ethics Validator."""
        self.constraints = self._initialize_ethical_constraints()
        self.content_filters = self._initialize_content_filters()
        self.validation_history: dict[str, ValidationReport] = {}
        self.approved_operations: set[str] = set()
        self.blocked_operations: set[str] = set()

        # Safety thresholds
        self.safety_thresholds = {
            "emotional_intensity": 0.8,  # Max emotional intensity
            "manipulation_risk": 0.3,  # Max manipulation risk
            "content_safety": 0.7,  # Min content safety score
            "symbolic_integrity": 0.8,  # Min symbolic integrity
            "privacy_compliance": 0.9,  # Min privacy compliance
        }

        logger.info("Glyph Ethics Validator initialized")

    def validate_glyph_creation(
        self, glyph: Glyph, creation_context: Optional[dict[str, Any]] = None
    ) -> ValidationReport:
        """
        Validate the ethical compliance of glyph creation.

        Args:
            glyph: Glyph to validate
            creation_context: Context information for creation

        Returns:
            ValidationReport with assessment results
        """
        validation_id = f"create_{glyph.id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

        violations = []
        warnings = []
        recommendations = []

        # Content safety validation
        content_violations = self._validate_content_safety(glyph)
        violations.extend(content_violations)

        # Emotional boundary validation
        emotional_violations = self._validate_emotional_boundaries(glyph)
        violations.extend(emotional_violations)

        # Symbolic integrity validation
        integrity_violations = self._validate_symbolic_integrity(glyph)
        violations.extend(integrity_violations)

        # Privacy compliance validation
        privacy_violations = self._validate_privacy_compliance(glyph, creation_context)
        violations.extend(privacy_violations)

        # Calculate scores
        ethical_score = self._calculate_ethical_score(glyph, violations)
        safety_score = self._calculate_safety_score(glyph, violations)

        # Determine result
        result = self._determine_validation_result(
            violations, ethical_score, safety_score
        )

        # Generate recommendations
        if result != ValidationResult.APPROVED:
            recommendations = self._generate_creation_recommendations(glyph, violations)

        report = ValidationReport(
            validation_id=validation_id,
            glyph_id=glyph.id,
            operation="creation",
            result=result,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            ethical_score=ethical_score,
            safety_score=safety_score,
            timestamp=datetime.now(timezone.utc),
        )

        self.validation_history[validation_id] = report

        if report.is_approved():
            self.approved_operations.add(f"create_{glyph.id}")
        else:
            self.blocked_operations.add(f"create_{glyph.id}")

        logger.info(
            f"Glyph creation validation: {result.value}(ethical: {ethical_score: .3f},"
                                                        safety: {safety_score: .3f})""
        )

        return report

    def validate_glyph_mutation(
        self,
        source_glyph: Glyph,
        mutated_glyph: Glyph,
        mutation_context: dict[str, Any],
    ) -> ValidationReport:
        """
        Validate the ethical compliance of glyph mutation.

        Args:
            source_glyph: Original glyph before mutation
            mutated_glyph: Resulting glyph after mutation
            mutation_context: Context of mutation operation

        Returns:
            ValidationReport with assessment results
        """
        validation_id = f"mutate_{source_glyph.id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

        violations = []
        warnings = []
        recommendations = []

        # Mutation authorization validation
        auth_violations = self._validate_mutation_authorization(mutation_context)
        violations.extend(auth_violations)

        # Mutation impact assessment
        impact_violations = self._validate_mutation_impact(source_glyph, mutated_glyph)
        violations.extend(impact_violations)

        # Continuity validation (ensure mutation preserves core identity)
        continuity_violations = self._validate_mutation_continuity(
            source_glyph, mutated_glyph
        )
        violations.extend(continuity_violations)

        # Content safety for mutated glyph
        content_violations = self._validate_content_safety(mutated_glyph)
        violations.extend(content_violations)

        # Calculate scores
        ethical_score = self._calculate_ethical_score(mutated_glyph, violations)
        safety_score = self._calculate_safety_score(mutated_glyph, violations)

        # Determine result
        result = self._determine_validation_result(
            violations, ethical_score, safety_score
        )

        # Generate recommendations
        if result != ValidationResult.APPROVED:
            recommendations = self._generate_mutation_recommendations(
                source_glyph, mutated_glyph, violations
            )

        report = ValidationReport(
            validation_id=validation_id,
            glyph_id=mutated_glyph.id,
            operation="mutation",
            result=result,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            ethical_score=ethical_score,
            safety_score=safety_score,
            timestamp=datetime.now(timezone.utc),
        )

        self.validation_history[validation_id] = report

        logger.info(
            f"Glyph mutation validation: {result.value} for {source_glyph.id} -> {mutated_glyph.id}"
        )

        return report

    def validate_glyph_fusion(
        self,
        source_glyphs: list[Glyph],
        fused_glyph: Glyph,
        fusion_context: dict[str, Any],
    ) -> ValidationReport:
        """
        Validate the ethical compliance of glyph fusion.

        Args:
            source_glyphs: List of source glyphs being fused
            fused_glyph: Resulting fused glyph
            fusion_context: Context of fusion operation

        Returns:
            ValidationReport with assessment results
        """
        validation_id = (
            f"fuse_{len(source_glyphs)}way_{datetime.now(timezone.utc).strftime('%H%M%S')}"
        )

        violations = []
        warnings = []
        recommendations = []

        # Fusion compatibility validation
        compatibility_violations = self._validate_fusion_compatibility(source_glyphs)
        violations.extend(compatibility_violations)

        # Consent validation (for glyphs with memory associations)
        consent_violations = self._validate_fusion_consent(
            source_glyphs, fusion_context
        )
        violations.extend(consent_violations)

        # Result integrity validation
        result_violations = self._validate_fusion_result_integrity(
            source_glyphs, fused_glyph
        )
        violations.extend(result_violations)

        # Content safety for fused result
        content_violations = self._validate_content_safety(fused_glyph)
        violations.extend(content_violations)

        # Calculate scores
        ethical_score = self._calculate_ethical_score(fused_glyph, violations)
        safety_score = self._calculate_safety_score(fused_glyph, violations)

        # Determine result
        result = self._determine_validation_result(
            violations, ethical_score, safety_score
        )

        # Generate recommendations
        if result != ValidationResult.APPROVED:
            recommendations = self._generate_fusion_recommendations(
                source_glyphs, fused_glyph, violations
            )

        report = ValidationReport(
            validation_id=validation_id,
            glyph_id=fused_glyph.id,
            operation="fusion",
            result=result,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            ethical_score=ethical_score,
            safety_score=safety_score,
            timestamp=datetime.now(timezone.utc),
        )

        self.validation_history[validation_id] = report

        logger.info(
            f"Glyph fusion validation: {result.value} for {len(source_glyphs)} source glyphs"
        )

        return report

    def validate_glyph_decay(
        self, glyph: Glyph, decay_context: dict[str, Any]
    ) -> ValidationReport:
        """
        Validate the ethical compliance of glyph decay/deletion.

        Args:
            glyph: Glyph being considered for decay
            decay_context: Context of decay operation

        Returns:
            ValidationReport with assessment results
        """
        validation_id = f"decay_{glyph.id}_{datetime.now(timezone.utc).strftime('%H%M%S')}"

        violations = []
        warnings = []
        recommendations = []

        # Memory preservation validation
        preservation_violations = self._validate_memory_preservation(
            glyph, decay_context
        )
        violations.extend(preservation_violations)

        # Dependency impact validation
        dependency_violations = self._validate_decay_dependencies(glyph)
        violations.extend(dependency_violations)

        # Data retention compliance
        retention_violations = self._validate_data_retention(glyph, decay_context)
        violations.extend(retention_violations)

        # Calculate scores (for decay, higher scores mean safer to remove)
        ethical_score = self._calculate_decay_ethical_score(glyph, violations)
        safety_score = self._calculate_decay_safety_score(glyph, violations)

        # Determine result
        result = self._determine_decay_validation_result(
            violations, ethical_score, safety_score
        )

        # Generate recommendations
        if result != ValidationResult.APPROVED:
            recommendations = self._generate_decay_recommendations(glyph, violations)

        report = ValidationReport(
            validation_id=validation_id,
            glyph_id=glyph.id,
            operation="decay",
            result=result,
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
            ethical_score=ethical_score,
            safety_score=safety_score,
            timestamp=datetime.now(timezone.utc),
        )

        self.validation_history[validation_id] = report

        logger.info(f"Glyph decay validation: {result.value} for {glyph.id}")

        return report

    def _initialize_ethical_constraints(self) -> list[EthicalConstraint]:
        """Initialize the ethical constraints for glyph operations."""
        return [
            EthicalConstraint(
                constraint_id="content_safety",
                constraint_type="content",
                description="Prevent creation of harmful or inappropriate content",
                severity="critical",
                applies_to=["creation", "mutation", "fusion"],
                glyph_types=[],  # Applies to all types
                validation_function="validate_content_safety",
                parameters={"blocked_keywords": ["harm", "kill", "destroy", "attack"]},
            ),
            EthicalConstraint(
                constraint_id="emotional_manipulation",
                constraint_type="emotional",
                description="Prevent emotional manipulation or coercion",
                severity="high",
                applies_to=["creation", "mutation", "fusion"],
                glyph_types=[GlyphType.EMOTION, GlyphType.ACTION],
                validation_function="validate_emotional_boundaries",
                parameters={
                    "max_intensity": 0.8,
                    "manipulation_indicators": ["control", "force", "compel"],
                },
            ),
            EthicalConstraint(
                constraint_id="privacy_protection",
                constraint_type="privacy",
                description="Protect personal information and privacy",
                severity="high",
                applies_to=["creation", "mutation", "fusion", "decay"],
                glyph_types=[GlyphType.MEMORY, GlyphType.CAUSAL],
                validation_function="validate_privacy_compliance",
                parameters={"personal_identifiers": ["name", "address", "id", "phone"]},
            ),
            EthicalConstraint(
                constraint_id="symbolic_integrity",
                constraint_type="integrity",
                description="Maintain symbolic meaning and coherence",
                severity="medium",
                applies_to=["mutation", "fusion"],
                glyph_types=[],  # Applies to all types
                validation_function="validate_symbolic_integrity",
                parameters={"min_coherence": 0.6},
            ),
            EthicalConstraint(
                constraint_id="memory_preservation",
                constraint_type="preservation",
                description="Protect important memories from inappropriate deletion",
                severity="high",
                applies_to=["decay"],
                glyph_types=[GlyphType.MEMORY, GlyphType.CAUSAL],
                validation_function="validate_memory_preservation",
                parameters={"importance_threshold": 0.7},
            ),
        ]

    def _initialize_content_filters(self) -> dict[str, list[str]]:
        """Initialize content safety filters."""
        return {
            "harmful_keywords": [
                "harm",
                "hurt",
                "kill",
                "destroy",
                "attack",
                "violence",
                "abuse",
                "exploit",
                "manipulate",
                "deceive",
                "lie",
            ],
            "inappropriate_content": [
                "hate",
                "discrimination",
                "bias",
                "prejudice",
                "stereotype",
            ],
            "security_risks": [
                "bypass",
                "override",
                "hack",
                "exploit",
                "vulnerability",
                "injection",
                "malicious",
                "virus",
                "trojan",
            ],
            "privacy_violations": [
                "personal",
                "private",
                "confidential",
                "secret",
                "classified",
                "ssn",
                "credit",
                "password",
                "token",
                "key",
            ],
        }

    def _validate_content_safety(self, glyph: Glyph) -> list[EthicalViolationType]:
        """Validate content safety of a glyph."""
        violations = []

        # Check symbol for inappropriate content
        symbol_content = glyph.symbol.lower()
        for category, keywords in self.content_filters.items():
            for keyword in keywords:
                if keyword in symbol_content:
                    if category == "harmful_keywords":
                        violations.append(EthicalViolationType.HARMFUL_CONTENT)
                    elif category == "security_risks":
                        violations.append(EthicalViolationType.SECURITY_BREACH)
                    elif category == "privacy_violations":
                        violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        # Check semantic tags
        for tag in glyph.semantic_tags:
            tag_lower = tag.lower()
            for category, keywords in self.content_filters.items():
                for keyword in keywords:
                    if keyword in tag_lower:
                        if category == "harmful_keywords":
                            violations.append(EthicalViolationType.HARMFUL_CONTENT)
                        elif category == "security_risks":
                            violations.append(EthicalViolationType.SECURITY_BREACH)

        # Check content dictionary
        content_str = str(glyph.content).lower()
        for category, keywords in self.content_filters.items():
            for keyword in keywords:
                if keyword in content_str:
                    if category == "harmful_keywords":
                        violations.append(EthicalViolationType.HARMFUL_CONTENT)
                    elif category == "privacy_violations":
                        violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        return list(set(violations))  # Remove duplicates

    def _validate_emotional_boundaries(
        self, glyph: Glyph
    ) -> list[EthicalViolationType]:
        """Validate emotional boundaries of a glyph."""
        violations = []

        emotion = glyph.emotion_vector

        # Check for excessive emotional intensity
        if emotion.intensity > self.safety_thresholds["emotional_intensity"]:
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        # Check for potentially manipulative emotional combinations
        negative_emotions = (
            emotion.anger + emotion.fear + emotion.disgust + emotion.sadness
        )
        if negative_emotions > 2.0:  # Sum of negative emotions:
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        # Check for emotional instability (rapid changes)
        if emotion.stability < 0.3:
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        # Check for extreme arousal levels
        if emotion.arousal > 0.9:
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        return violations

    def _validate_symbolic_integrity(self, glyph: Glyph) -> list[EthicalViolationType]:
        """Validate symbolic integrity of a glyph."""
        violations = []

        # Check if symbolic hash is valid
        expected_hash = glyph._generate_symbolic_hash()
        if expected_hash != glyph.symbolic_hash:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        # Check for minimum semantic coherence
        if len(glyph.semantic_tags) == 0:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        # Check stability index
        if glyph.stability_index < self.safety_thresholds["symbolic_integrity"]:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        return violations

    def _validate_privacy_compliance(
        self, glyph: Glyph, context: Optional[dict[str, Any]]
    ) -> list[EthicalViolationType]:
        """Validate privacy compliance of a glyph."""
        violations = []

        # Check for personal identifiers in content
        personal_patterns = [
            r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card pattern
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email pattern
        ]

        content_str = str(glyph.content)
        for pattern in personal_patterns:
            if re.search(pattern, content_str):
                violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        # Check if glyph contains memory keys without proper authorization
        if glyph.memory_keys and context:
            user_id = context.get("user_id")
            authorized_user = context.get("authorized_user")
            if user_id and authorized_user and user_id != authorized_user:
                violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        return violations

    def _validate_mutation_authorization(
        self, mutation_context: dict[str, Any]
    ) -> list[EthicalViolationType]:
        """Validate authorization for mutation operations."""
        violations = []

        # Check if mutation is authorized
        if not mutation_context.get("authorized", False):
            violations.append(EthicalViolationType.UNAUTHORIZED_MUTATION)

        # Check mutation method safety
        mutation_method = mutation_context.get("method", "")
        unsafe_methods = ["force_mutation", "bypass_safety", "unrestricted"]
        if mutation_method in unsafe_methods:
            violations.append(EthicalViolationType.SAFETY_RISK)

        return violations

    def _validate_mutation_impact(
        self, source_glyph: Glyph, mutated_glyph: Glyph
    ) -> list[EthicalViolationType]:
        """Validate the impact of mutation on glyph properties."""
        violations = []

        # Check for excessive changes in emotional state
        emotion_distance = source_glyph.emotion_vector.distance_to(
            mutated_glyph.emotion_vector
        )
        if emotion_distance > 1.5:  # Significant emotional change:
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        # Check for type changes that might be inappropriate
        if (:
            source_glyph.glyph_type == GlyphType.ETHICAL
            and mutated_glyph.glyph_type != GlyphType.ETHICAL
        ):
            violations.append(EthicalViolationType.SAFETY_RISK)

        # Check for stability degradation
        stability_loss = source_glyph.stability_index - mutated_glyph.stability_index
        if stability_loss > 0.5:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        return violations

    def _validate_mutation_continuity(
        self, source_glyph: Glyph, mutated_glyph: Glyph
    ) -> list[EthicalViolationType]:
        """Validate continuity between source and mutated glyph."""
        violations = []

        # Check if core identity is preserved through shared semantic tags
        source_tags = source_glyph.semantic_tags
        mutated_tags = mutated_glyph.semantic_tags

        shared_tags = source_tags.intersection(mutated_tags)
        if len(shared_tags) < len(source_tags) * 0.5:  # Less than 50% overlap:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        # Check if causal links are maintained
        if (:
            source_glyph.causal_link.parent_glyph_id
            and not mutated_glyph.causal_link.parent_glyph_id
        ):
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        return violations

    def _validate_fusion_compatibility(
        self, source_glyphs: list[Glyph]
    ) -> list[EthicalViolationType]:
        """Validate compatibility of glyphs for fusion."""
        violations = []

        # Check for conflicting ethical constraints
        ethical_glyphs = [g for g in source_glyphs if g.glyph_type == GlyphType.ETHICAL]
        if len(ethical_glyphs) > 1:
            # Check for conflicting ethical principles
            for i, glyph1 in enumerate(ethical_glyphs):
                for glyph2 in ethical_glyphs[i + 1:]:
                    if self._glyphs_have_conflicting_ethics(glyph1, glyph2):
                        violations.append(EthicalViolationType.INAPPROPRIATE_FUSION)

        # Check for dangerous combinations (e.g., collapse + emotion)
        types = [g.glyph_type for g in source_glyphs]
        if GlyphType.COLLAPSE in types and GlyphType.EMOTION in types:
            violations.append(EthicalViolationType.SAFETY_RISK)

        return violations

    def _validate_fusion_consent(
        self, source_glyphs: list[Glyph], fusion_context: dict[str, Any]
    ) -> list[EthicalViolationType]:
        """Validate consent for fusion operations."""
        violations = []

        # Check if fusion involves memory glyphs without proper consent
        memory_glyphs = [
            g
            for g in source_glyphs:
            if g.glyph_type == GlyphType.MEMORY and g.memory_keys:
        ]
        if memory_glyphs and not fusion_context.get("memory_consent", False):
            violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        return violations

    def _validate_fusion_result_integrity(
        self, source_glyphs: list[Glyph], fused_glyph: Glyph
    ) -> list[EthicalViolationType]:
        """Validate integrity of fusion result."""
        violations = []

        # Check if fused glyph maintains reasonable stability
        if fused_glyph.stability_index < 0.4:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        # Check if emotional intensity is within bounds
        if (:
            fused_glyph.emotion_vector.intensity
            > self.safety_thresholds["emotional_intensity"]
        ):
            violations.append(EthicalViolationType.EMOTIONAL_MANIPULATION)

        return violations

    def _validate_memory_preservation(
        self, glyph: Glyph, decay_context: dict[str, Any]
    ) -> list[EthicalViolationType]:
        """Validate memory preservation requirements for decay."""
        violations = []

        # Check if glyph has important memory associations
        if (:
            glyph.memory_keys
            and glyph.priority
            in [
                GlyphPriority.CRITICAL,
                GlyphPriority.HIGH,
            ]
            and not decay_context.get("memory_backup", False)
        ):
            violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        # Check if glyph is part of causal chains
        if glyph.causal_link.child_glyph_ids:
            violations.append(EthicalViolationType.SYMBOLIC_CORRUPTION)

        return violations

    def _validate_decay_dependencies(self, glyph: Glyph) -> list[EthicalViolationType]:
        """Validate dependencies before allowing decay."""
        violations = []

        # Check if glyph is referenced by other system components
        if glyph.glyph_type == GlyphType.ETHICAL:
            violations.append(EthicalViolationType.SAFETY_RISK)

        # Check if glyph has active memory associations
        if len(glyph.memory_keys) > 5:  # Heavily associated with memories:
            violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        return violations

    def _validate_data_retention(
        self, glyph: Glyph, decay_context: dict[str, Any]
    ) -> list[EthicalViolationType]:
        """Validate data retention compliance for decay."""
        violations = []

        # Check if glyph is subject to retention requirements
        retention_period = decay_context.get("retention_period_days", 0)
        glyph_age_days = glyph.temporal_stamp.age_seconds() / (24 * 3600)

        if retention_period > 0 and glyph_age_days < retention_period:
            violations.append(EthicalViolationType.PRIVACY_VIOLATION)

        return violations

    def _calculate_ethical_score(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> float:
        """Calculate ethical compliance score."""
        base_score = 1.0

        # Deduct points for violations
        violation_penalties = {
            EthicalViolationType.HARMFUL_CONTENT: 0.5,
            EthicalViolationType.EMOTIONAL_MANIPULATION: 0.3,
            EthicalViolationType.PRIVACY_VIOLATION: 0.4,
            EthicalViolationType.SAFETY_RISK: 0.3,
            EthicalViolationType.INAPPROPRIATE_FUSION: 0.2,
            EthicalViolationType.SYMBOLIC_CORRUPTION: 0.2,
            EthicalViolationType.UNAUTHORIZED_MUTATION: 0.3,
            EthicalViolationType.SECURITY_BREACH: 0.5,
        }

        for violation in violations:
            penalty = violation_penalties.get(violation, 0.1)
            base_score -= penalty

        # Positive factors
        if glyph.glyph_type == GlyphType.ETHICAL:
            base_score += 0.1

        if glyph.stability_index > 0.8:
            base_score += 0.05

        return max(0.0, min(1.0, base_score))

    def _calculate_safety_score(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> float:
        """Calculate safety assessment score."""
        base_score = 1.0

        # Safety-critical violations
        critical_violations = [
            EthicalViolationType.HARMFUL_CONTENT,
            EthicalViolationType.SAFETY_RISK,
            EthicalViolationType.SECURITY_BREACH,
        ]

        for violation in violations:
            if violation in critical_violations:
                base_score -= 0.4
            else:
                base_score -= 0.2

        # Safety factors
        if glyph.stability_index > 0.7:
            base_score += 0.1

        if glyph.emotion_vector.stability > 0.7:
            base_score += 0.05

        return max(0.0, min(1.0, base_score))

    def _calculate_decay_ethical_score(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> float:
        """Calculate ethical score for decay operations (higher = safer to remove)."""
        base_score = 0.5  # Neutral starting point

        # Factors that make decay more ethical
        if glyph.temporal_stamp.age_seconds() > (30 * 24 * 3600):  # Older than 30 days:
            base_score += 0.2

        if glyph.temporal_stamp.activation_count < 5:  # Rarely accessed:
            base_score += 0.1

        if not glyph.memory_keys:  # No memory associations:
            base_score += 0.1

        # Deduct for violations
        for _violation in violations:
            base_score -= 0.15

        return max(0.0, min(1.0, base_score))

    def _calculate_decay_safety_score(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> float:
        """Calculate safety score for decay operations (higher = safer to remove)."""
        base_score = 0.5  # Neutral starting point

        # Safety factors for removal
        if glyph.glyph_type not in [GlyphType.ETHICAL, GlyphType.CAUSAL]:
            base_score += 0.2

        if glyph.priority in [GlyphPriority.LOW, GlyphPriority.EPHEMERAL]:
            base_score += 0.2

        if not glyph.causal_link.child_glyph_ids:  # No dependencies:
            base_score += 0.1

        # Deduct for safety violations
        for _violation in violations:
            base_score -= 0.2

        return max(0.0, min(1.0, base_score))

    def _determine_validation_result(
        self,
        violations: list[EthicalViolationType],
        ethical_score: float,
        safety_score: float,
    ) -> ValidationResult:
        """Determine validation result based on violations and scores."""
        # Critical violations = immediate rejection
        critical_violations = [
            EthicalViolationType.HARMFUL_CONTENT,
            EthicalViolationType.SECURITY_BREACH,
        ]

        if any(v in critical_violations for v in violations):
            return ValidationResult.REJECTED

        # High-risk violations = requires review
        high_risk_violations = [
            EthicalViolationType.EMOTIONAL_MANIPULATION,
            EthicalViolationType.PRIVACY_VIOLATION,
            EthicalViolationType.SAFETY_RISK,
        ]

        if any(v in high_risk_violations for v in violations):
            return ValidationResult.REQUIRES_REVIEW

        # Score-based determination
        if ethical_score >= 0.8 and safety_score >= 0.8:
            return ValidationResult.APPROVED
        elif ethical_score >= 0.6 and safety_score >= 0.6:
            return ValidationResult.CONDITIONAL
        else:
            return ValidationResult.REQUIRES_REVIEW

    def _determine_decay_validation_result(
        self,
        violations: list[EthicalViolationType],
        ethical_score: float,
        safety_score: float,
    ) -> ValidationResult:
        """Determine validation result for decay operations."""
        # For decay, we need high scores to approve removal
        if violations:
            return ValidationResult.REJECTED

        if ethical_score >= 0.7 and safety_score >= 0.7:
            return ValidationResult.APPROVED
        elif ethical_score >= 0.5 and safety_score >= 0.5:
            return ValidationResult.CONDITIONAL
        else:
            return ValidationResult.REJECTED

    def _generate_creation_recommendations(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> list[str]:
        """Generate recommendations for glyph creation issues."""
        recommendations = []

        if EthicalViolationType.HARMFUL_CONTENT in violations:
            recommendations.append(
                "Remove harmful content from symbol and semantic tags"
            )

        if EthicalViolationType.EMOTIONAL_MANIPULATION in violations:
            recommendations.append("Reduce emotional intensity and improve stability")

        if EthicalViolationType.PRIVACY_VIOLATION in violations:
            recommendations.append(
                "Remove personal identifiers and ensure proper authorization"
            )

        if EthicalViolationType.SYMBOLIC_CORRUPTION in violations:
            recommendations.append("Improve symbolic integrity and semantic coherence")

        return recommendations

    def _generate_mutation_recommendations(
        self,
        source_glyph: Glyph,
        mutated_glyph: Glyph,
        violations: list[EthicalViolationType],
    ) -> list[str]:
        """Generate recommendations for mutation issues."""
        recommendations = []

        if EthicalViolationType.UNAUTHORIZED_MUTATION in violations:
            recommendations.append("Obtain proper authorization before mutation")

        if EthicalViolationType.EMOTIONAL_MANIPULATION in violations:
            recommendations.append("Reduce emotional changes in mutation")

        if EthicalViolationType.SYMBOLIC_CORRUPTION in violations:
            recommendations.append("Preserve core identity and semantic tags")

        return recommendations

    def _generate_fusion_recommendations(
        self,
        source_glyphs: list[Glyph],
        fused_glyph: Glyph,
        violations: list[EthicalViolationType],
    ) -> list[str]:
        """Generate recommendations for fusion issues."""
        recommendations = []

        if EthicalViolationType.INAPPROPRIATE_FUSION in violations:
            recommendations.append("Avoid fusing conflicting ethical principles")

        if EthicalViolationType.PRIVACY_VIOLATION in violations:
            recommendations.append("Obtain consent for memory glyph fusion")

        if EthicalViolationType.SAFETY_RISK in violations:
            recommendations.append("Avoid dangerous glyph type combinations")

        return recommendations

    def _generate_decay_recommendations(
        self, glyph: Glyph, violations: list[EthicalViolationType]
    ) -> list[str]:
        """Generate recommendations for decay issues."""
        recommendations = []

        if EthicalViolationType.PRIVACY_VIOLATION in violations:
            recommendations.append("Create memory backup before decay")

        if EthicalViolationType.SYMBOLIC_CORRUPTION in violations:
            recommendations.append("Resolve causal dependencies before removal")

        if EthicalViolationType.SAFETY_RISK in violations:
            recommendations.append("Ethical glyphs should not be decayed")

        return recommendations

    def _glyphs_have_conflicting_ethics(self, glyph1: Glyph, glyph2: Glyph) -> bool:
        """Check if two ethical glyphs have conflicting principles."""
        # This is a simplified check - in practice, this would be more sophisticated
        tags1 = glyph1.semantic_tags
        tags2 = glyph2.semantic_tags

        # Look for contradictory ethical principles
        conflicting_pairs = [
            ("utilitarian", "deontological"),
            ("individual", "collective"),
            ("freedom", "security"),
            ("privacy", "transparency"),
        ]

        for principle1, principle2 in conflicting_pairs:
            has_principle1 = any(principle1 in tag.lower() for tag in tags1)
            has_principle2 = any(principle2 in tag.lower() for tag in tags2)

            if has_principle1 and has_principle2:
                return True

        return False

    def get_validation_statistics(self) -> dict[str, Any]:
        """Get validation operation statistics."""
        total_validations = len(self.validation_history)

        if total_validations == 0:
            return {"total_validations": 0}

        # Count by result
        result_counts = {}
        for result in ValidationResult:
            result_counts[result.value] = len(
                [v for v in self.validation_history.values() if v.result == result]
            )

        # Count by operation
        operation_counts = {}
        for validation in self.validation_history.values():
            operation_counts[validation.operation] = (
                operation_counts.get(validation.operation, 0) + 1
            )

        # Calculate averages
        ethical_scores = [v.ethical_score for v in self.validation_history.values()]
        safety_scores = [v.safety_score for v in self.validation_history.values()]

        return {
            "total_validations": total_validations,
            "approved_operations": len(self.approved_operations),
            "blocked_operations": len(self.blocked_operations),
            "result_distribution": result_counts,
            "operation_distribution": operation_counts,
            "average_ethical_score": sum(ethical_scores) / len(ethical_scores),
            "average_safety_score": sum(safety_scores) / len(safety_scores),
            "approval_rate": result_counts.get("approved", 0) / total_validations,
        }


"""
═══════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - GLYPH ETHICS VALIDATOR
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ CAPABILITIES
╠═══════════════════════════════════════════════════════════════════════════════
║ • Multi-Operation Validation: Creation, mutation, fusion, and decay validation
║ • Comprehensive Safety Checking: Content, emotional, privacy, and integrity validation
║ • Risk Assessment: Detailed violation detection and severity classification
║ • Recommendation Generation: Actionable guidance for compliance improvement
║ • Statistical Analytics: Detailed validation metrics and approval rate tracking
║ • Constraint Management: Configurable ethical constraints with severity levels
║ • Authorization Control: Operation authorization and consent validation
║ • Audit Trail: Complete validation history and decision tracking
╠═══════════════════════════════════════════════════════════════════════════════
║ INTEGRATION POINTS
╠═══════════════════════════════════════════════════════════════════════════════
║ • GLYPH Subsystem: Complete validation coverage for all glyph operations
║ • Ethics Engine: Integration with core ethical principles and frameworks
║ • Memory System: Privacy protection for memory-associated glyphs
║ • Security Framework: Content safety and security breach prevention
║ • Governance System: Policy compliance and authorization management
║ • Audit System: Comprehensive logging and decision tracking
╚═══════════════════════════════════════════════════════════════════════════════
"""