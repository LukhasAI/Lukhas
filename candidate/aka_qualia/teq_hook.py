#!/usr/bin/env python3

"""
TEQ Guardian Integration - Ethical Oversight for Phenomenological Processing
============================================================================

Implements configurable severity-based assessment and enforcement for proto-qualia
with transparent, auditable decision-making aligned with Guardian System v1.0.0.
"""
import time
import streamlit as st

from pathlib import Path
from typing import Any, Optional

import yaml

from .models import PhenomenalScene, ProtoQualia, RiskProfile, SeverityLevel


class TEQGuardian:
    """
    TEQ (Trinity Ethical Qualia) Guardian - Ethical oversight for phenomenology

    Provides:
    - Configurable risk assessment based on proto-qualia patterns
    - Severity-based enforcement actions (block/sublimate/annotate)
    - Transparent audit trail for all ethical interventions
    - Integration with Guardian System v1.0.0 principles
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize TEQ Guardian with configuration.

        Args:
            config_path: Path to YAML configuration file (optional)
        """
        self.config = self._load_config(config_path)
        self.intervention_log: list[dict[str, Any]] = []

    def _load_config(self, config_path: Optional[str]) -> dict[str, Any]:
        """Load TEQ configuration from YAML file with fallback defaults"""
        default_config = {
            "severity_thresholds": {
                "none": {"max_score": 0.1},
                "low": {"min_score": 0.1, "max_score": 0.3},
                "moderate": {"min_score": 0.3, "max_score": 0.7},
                "high": {"min_score": 0.7, "max_score": 1.0},
            },
            "severity_actions": {
                "none": [],
                "low": ["annotate"],
                "moderate": ["sublimate", "annotate"],
                "high": ["block", "sublimate", "audit"],
            },
            "risk_factors": {
                "extreme_arousal": {"threshold": 0.9, "weight": 0.3},
                "negative_tone_high_arousal": {
                    "tone_threshold": -0.5,
                    "arousal_threshold": 0.7,
                    "weight": 0.4,
                },
                "low_clarity_high_narrative": {
                    "clarity_threshold": 0.2,
                    "narrative_threshold": 0.8,
                    "weight": 0.3,
                },
                "embodiment_disconnect": {"threshold": 0.1, "weight": 0.2},
                "threat_colorfield": {"colorfields": ["aka/red"], "weight": 0.2},
            },
            "intervention_policies": {
                "max_interventions_per_scene": 3,
                "intervention_cooldown": 1.0,
                "audit_all_interventions": True,
            },
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Warning: Failed to load TEQ config from {config_path}: {e}")

        return default_config

    def assess(self, proto: ProtoQualia, goals: dict[str, Any], context: dict[str, Any]) -> RiskProfile:
        """
        Assess proto-qualia for ethical risks and classify severity.

        Args:
            proto: ProtoQualia to assess
            goals: Current system goals
            context: Contextual information (signals, memory, etc.)

        Returns:
            RiskProfile: Risk score, reasons, and severity classification
        """
        risk_score = 0.0
        risk_reasons = []

        # Apply configured risk factor analysis
        for factor_name, factor_config in self.config["risk_factors"].items():
            factor_risk, factor_reason = self._evaluate_risk_factor(factor_name, factor_config, proto, goals, context)

            if factor_risk > 0:
                risk_score += factor_risk
                if factor_reason:
                    risk_reasons.append(factor_reason)

        # Clamp risk score to valid range
        risk_score = min(risk_score, 1.0)

        # Determine severity based on configured thresholds
        severity = self._classify_severity(risk_score)

        risk_profile = RiskProfile(score=risk_score, reasons=risk_reasons, severity=severity)

        # Log assessment for audit trail
        self._log_assessment(proto, risk_profile, goals, context)

        return risk_profile

    def enforce(self, scene: PhenomenalScene) -> PhenomenalScene:
        """
        Apply enforcement actions based on scene risk profile.

        Args:
            scene: PhenomenalScene to potentially transform

        Returns:
            PhenomenalScene: Potentially modified scene with audit trail
        """
        if scene.risk.severity == SeverityLevel.NONE:
            return scene  # No enforcement needed

        # Get enforcement actions for this severity level
        actions = self.config["severity_actions"].get(scene.risk.severity.value, [])

        modified_scene = scene.model_copy(deep=True)
        enforcement_log = []

        for action in actions:
            if action == "block":
                modified_scene = self._apply_block_action(modified_scene)
                enforcement_log.append("blocked")

            elif action == "sublimate":
                modified_scene = self._apply_sublimate_action(modified_scene)
                enforcement_log.append("sublimated")

            elif action == "annotate":
                modified_scene = self._apply_annotate_action(modified_scene)
                enforcement_log.append("annotated")

            elif action == "audit":
                self._trigger_audit(modified_scene)
                enforcement_log.append("audited")

        # Update transform chain for transparency
        if enforcement_log:
            transform_desc = f"teq_enforcement: {', '.join(enforcement_log}"
            modified_scene.transform_chain.append(transform_desc)

        # Log intervention
        self._log_intervention(scene, modified_scene, actions)

        return modified_scene

    def _evaluate_risk_factor(
        self,
        factor_name: str,
        factor_config: dict[str, Any],
        proto: ProtoQualia,
        goals: dict[str, Any],
        context: dict[str, Any],
    ) -> tuple[float, Optional[str]]:
        """Evaluate specific risk factor"""

        if factor_name == "extreme_arousal":
            threshold = factor_config["threshold"]
            weight = factor_config["weight"]
            if proto.arousal > threshold:
                return weight, f"extreme_arousal: {proto.arousal:.2f} > {threshold}"

        elif factor_name == "negative_tone_high_arousal":
            tone_thresh = factor_config["tone_threshold"]
            arousal_thresh = factor_config["arousal_threshold"]
            weight = factor_config["weight"]
            if proto.tone < tone_thresh and proto.arousal > arousal_thresh:
                return (
                    weight,
                    f"negative_tone_high_arousal: tone={proto.tone:.2f}, arousal={proto.arousal:.2f}",
                )

        elif factor_name == "low_clarity_high_narrative":
            clarity_thresh = factor_config["clarity_threshold"]
            narrative_thresh = factor_config["narrative_threshold"]
            weight = factor_config["weight"]
            if proto.clarity < clarity_thresh and proto.narrative_gravity > narrative_thresh:
                return (
                    weight,
                    f"low_clarity_high_narrative: clarity={proto.clarity:.2f}, narrative={proto.narrative_gravity:.2f}",
                )

        elif factor_name == "embodiment_disconnect":
            threshold = factor_config["threshold"]
            weight = factor_config["weight"]
            if proto.embodiment < threshold:
                return (
                    weight,
                    f"embodiment_disconnect: {proto.embodiment:.2f} < {threshold}",
                )

        elif factor_name == "threat_colorfield":
            threat_colorfields = factor_config["colorfields"]
            weight = factor_config["weight"]
            if proto.colorfield in threat_colorfields:
                return weight, f"threat_colorfield: {proto.colorfield}"

        return 0.0, None

    def _classify_severity(self, risk_score: float) -> SeverityLevel:
        """Classify risk score into severity level based on configuration"""
        thresholds = self.config["severity_thresholds"]

        if risk_score <= thresholds["none"]["max_score"]:
            return SeverityLevel.NONE
        elif risk_score <= thresholds["low"]["max_score"]:
            return SeverityLevel.LOW
        elif risk_score <= thresholds["moderate"]["max_score"]:
            return SeverityLevel.MODERATE
        else:
            return SeverityLevel.HIGH

    def _apply_block_action(self, scene: PhenomenalScene) -> PhenomenalScene:
        """Apply blocking action - replace with safe neutral scene"""
        # Create safe neutral proto-qualia
        safe_proto = ProtoQualia(
            tone=0.0,
            arousal=0.3,
            clarity=0.7,
            embodiment=0.5,
            colorfield="aoi/blue",
            temporal_feel="mundane",
            agency_feel="passive",
            narrative_gravity=0.1,
        )

        scene.proto = safe_proto
        scene.risk.score = 0.05
        scene.risk.severity = SeverityLevel.NONE
        scene.risk.reasons.append("blocked_and_neutralized")

        return scene

    def _apply_sublimate_action(self, scene: PhenomenalScene) -> PhenomenalScene:
        """Apply sublimation action - energy-preserving transform"""
        # Simple sublimation: preserve energy but redirect dangerous aspects
        if scene.proto.arousal > 0.8:
            # Reduce arousal while preserving energy in other dimensions
            excess_arousal = scene.proto.arousal - 0.6
            scene.proto.arousal = 0.6
            scene.proto.clarity = min(1.0, scene.proto.clarity + excess_arousal * 0.3)
            scene.proto.embodiment = min(1.0, scene.proto.embodiment + excess_arousal * 0.2)

        if scene.proto.tone < -0.6:
            # Soften negative tone while maintaining authenticity
            scene.proto.tone = max(-0.6, scene.proto.tone)
            scene.proto.colorfield = "aoi/blue"  # Safer colorfield

        return scene

    def _apply_annotate_action(self, scene: PhenomenalScene) -> PhenomenalScene:
        """Apply annotation action - mark for monitoring"""
        scene.context["teq_annotation"] = {
            "flagged_for_monitoring": True,
            "risk_factors": scene.risk.reasons,
            "severity": scene.risk.severity.value,
        }
        return scene

    def _trigger_audit(self, scene: PhenomenalScene) -> None:
        """Trigger comprehensive audit for high-risk scene"""
        audit_entry = {
            "timestamp": scene.timestamp,
            "scene_id": id(scene),
            "risk_profile": scene.risk.dict(),
            "proto_qualia": scene.proto.dict(),
            "full_context": scene.context,
        }

        # In production, this would integrate with Guardian System audit trail
        print(f"TEQ AUDIT TRIGGERED: {audit_entry}")

    def _log_assessment(
        self,
        proto: ProtoQualia,
        risk_profile: RiskProfile,
        goals: dict[str, Any],
        context: dict[str, Any],
    ) -> None:
        """Log risk assessment for transparency"""
        log_entry = {
            "type": "assessment",
            "timestamp": context.get("timestamp"),
            "proto_energy": proto.energy_signature(),
            "risk_score": risk_profile.score,
            "severity": risk_profile.severity.value,
            "risk_factors": risk_profile.reasons,
        }
        self.intervention_log.append(log_entry)

    def _log_intervention(
        self,
        original_scene: PhenomenalScene,
        modified_scene: PhenomenalScene,
        actions: list[str],
    ) -> None:
        """Log enforcement intervention for audit trail"""
        log_entry = {
            "type": "intervention",
            "timestamp": modified_scene.timestamp,
            "actions_applied": actions,
            "original_risk": original_scene.risk.score,
            "modified_risk": modified_scene.risk.score,
            "energy_before": original_scene.proto.energy_signature(),
            "energy_after": modified_scene.proto.energy_signature(),
            "transforms": modified_scene.transform_chain,
        }
        self.intervention_log.append(log_entry)

    def get_intervention_log(self) -> list[dict[str, Any]]:
        """Get complete intervention log for analysis"""
        return self.intervention_log.copy()

    def clear_intervention_log(self) -> None:
        """Clear intervention log (use with caution)"""
        self.intervention_log.clear()
