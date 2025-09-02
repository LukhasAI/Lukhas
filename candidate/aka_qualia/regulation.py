#!/usr/bin/env python3

"""
Regulation Policy v1 with Audit Logging
=====================================

Enhanced regulation system for Aka Qualia with:
- Heuristic policy generation based on proto-qualia and risk assessment
- Energy-aware sublimation actions
- Comprehensive audit trail logging
- Configurable policy rules and thresholds
"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from candidate.aka_qualia.models import PhenomenalScene, RegulationPolicy


@dataclass
class RegulationAuditEntry:
    """Audit trail entry for regulation decisions"""

    timestamp: float
    scene_id: str
    proto_qualia_snapshot: dict[str, Any]
    risk_assessment: dict[str, Any]
    policy_decision: dict[str, Any]
    energy_before: float
    energy_after: float
    conservation_ratio: float
    decision_rationale: list[str]
    performance_metrics: dict[str, float]


class RegulationPolicyEngine:
    """
    Enhanced regulation policy engine with audit logging.

    Implements heuristic-based policy generation with configurable rules,
    energy accounting, and comprehensive audit trails for compliance.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize regulation engine.

        Args:
            config: Configuration overrides
        """
        self.config = self._load_config(config)
        self.audit_log: list[RegulationAuditEntry] = []
        self.policy_cache: dict[str, tuple[RegulationPolicy, float]] = {}
        self.initialization_time = time.time()

        # Policy rule thresholds (configurable)
        self.thresholds = {
            "high_arousal": self.config.get("high_arousal_threshold", 0.8),
            "low_clarity": self.config.get("low_clarity_threshold", 0.3),
            "high_risk": self.config.get("high_risk_threshold", 0.6),
            "moderate_risk": self.config.get("moderate_risk_threshold", 0.3),
            "high_narrative_gravity": self.config.get("high_narrative_gravity_threshold", 0.7),
            "energy_conservation_tolerance": self.config.get("energy_conservation_tolerance", 0.05),
        }

    def _load_config(self, config_override: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Load configuration with defaults"""
        default_config = {
            "enable_audit_logging": True,
            "enable_policy_caching": True,
            "max_audit_entries": 1000,
            "safe_palette": "aoi/blue",
            "conservative_mode": False,
            "energy_conservation_strict": True,
            "audit_log_path": "logs/regulation_audit.jsonl",
        }

        if config_override:
            default_config.update(config_override)

        return default_config

    def generate_policy(
        self,
        scene: PhenomenalScene,
        guardian_state: dict[str, Any],
        energy_before: float,
    ) -> tuple[RegulationPolicy, RegulationAuditEntry]:
        """
        Generate regulation policy with comprehensive audit logging.

        Args:
            scene: PhenomenalScene to regulate
            guardian_state: Guardian system state
            energy_before: Energy snapshot before regulation

        Returns:
            Tuple of (RegulationPolicy, RegulationAuditEntry)
        """
        start_time = time.time()
        scene_hash = self._compute_scene_hash(scene)

        # Check cache if enabled
        if self.config["enable_policy_caching"] and scene_hash in self.policy_cache:
            cached_policy, cache_time = self.policy_cache[scene_hash]
            if time.time() - cache_time < 300:  # 5-minute cache TTL
                return cached_policy, self._create_cached_audit_entry(scene, cached_policy, energy_before)

        # Decision rationale tracking
        rationale = []
        actions = []

        # Rule 1: High arousal regulation
        if scene.proto.arousal > self.thresholds["high_arousal"]:
            actions.append("breathing")
            rationale.append(
                f"High arousal {scene.proto.arousal:.3f} > {self.thresholds['high_arousal']} → breathing regulation"
            )

        # Rule 2: Low clarity enhancement
        if scene.proto.clarity < self.thresholds["low_clarity"]:
            actions.append("focus-shift")
            rationale.append(
                f"Low clarity {scene.proto.clarity:.3f} < {self.thresholds['low_clarity']} → focus enhancement"
            )

        # Rule 3: Risk-based interventions
        if scene.risk.score > self.thresholds["high_risk"]:
            actions.extend(["pause", "reframe"])
            rationale.append(f"High risk {scene.risk.score:.3f} > {self.thresholds['high_risk']} → pause+reframe")
        elif scene.risk.score > self.thresholds["moderate_risk"]:
            actions.append("reframe")
            rationale.append(f"Moderate risk {scene.risk.score:.3f} > {self.thresholds['moderate_risk']} → reframe")

        # Rule 4: Narrative gravity loop prevention
        if scene.proto.narrative_gravity > self.thresholds["high_narrative_gravity"] and scene.proto.clarity < 0.5:
            actions.append("focus-shift")
            rationale.append(
                f"High narrative gravity {scene.proto.narrative_gravity:.3f} + low clarity → loop prevention"
            )

        # Rule 5: Conservative mode overrides
        if self.config["conservative_mode"]:
            if scene.proto.arousal > 0.6:  # Lower threshold in conservative mode
                actions.append("breathing")
                rationale.append("Conservative mode: preemptive arousal regulation")

        # Compute gain and pace modulation
        gain = self._compute_gain_modulation(scene, rationale)
        pace = self._compute_pace_modulation(scene, rationale)

        # Color contrast override for high-risk scenes
        color_contrast = None
        if scene.risk.severity.value in ["moderate", "high"]:
            color_contrast = self.config["safe_palette"]
            rationale.append(f"Risk severity {scene.risk.severity.value} → safe palette override")

        # Remove duplicate actions
        actions = list(set(actions))

        # Create policy
        policy = RegulationPolicy(gain=gain, pace=pace, color_contrast=color_contrast, actions=actions)

        # Performance metrics
        processing_time = time.time() - start_time
        performance_metrics = {
            "processing_time_ms": processing_time * 1000,
            "rules_triggered": len(rationale),
            "actions_count": len(actions),
            "cache_hit": False,
        }

        # Create audit entry
        audit_entry = RegulationAuditEntry(
            timestamp=time.time(),
            scene_id=scene_hash,
            proto_qualia_snapshot={
                "tone": scene.proto.tone,
                "arousal": scene.proto.arousal,
                "clarity": scene.proto.clarity,
                "embodiment": scene.proto.embodiment,
                "narrative_gravity": scene.proto.narrative_gravity,
            },
            risk_assessment={
                "score": scene.risk.score,
                "severity": scene.risk.severity.value,
                "reasons": scene.risk.reasons,
            },
            policy_decision={
                "gain": gain,
                "pace": pace,
                "color_contrast": color_contrast,
                "actions": actions,
            },
            energy_before=energy_before,
            energy_after=0.0,  # Will be updated after regulation
            conservation_ratio=1.0,  # Will be updated
            decision_rationale=rationale,
            performance_metrics=performance_metrics,
        )

        # Cache policy if enabled
        if self.config["enable_policy_caching"]:
            self.policy_cache[scene_hash] = (policy, time.time())

        # Log audit entry
        if self.config["enable_audit_logging"]:
            self._log_audit_entry(audit_entry)

        return policy, audit_entry

    def update_audit_entry_post_regulation(self, audit_entry: RegulationAuditEntry, energy_after: float) -> None:
        """Update audit entry with post-regulation energy data"""
        audit_entry.energy_after = energy_after
        audit_entry.conservation_ratio = (
            energy_after / audit_entry.energy_before if audit_entry.energy_before > 0 else 1.0
        )

        # Check energy conservation
        energy_delta = abs(audit_entry.energy_before - energy_after)
        if energy_delta > self.thresholds["energy_conservation_tolerance"]:
            audit_entry.decision_rationale.append(
                f"Energy conservation violation: Δ={energy_delta:.4f} > {self.thresholds['energy_conservation_tolerance']}"
            )

        # Update performance metrics
        audit_entry.performance_metrics["energy_conservation_ratio"] = audit_entry.conservation_ratio
        audit_entry.performance_metrics["energy_delta"] = energy_delta
        audit_entry.performance_metrics["conservation_violation"] = (
            energy_delta > self.thresholds["energy_conservation_tolerance"]
        )

    def _compute_gain_modulation(self, scene: PhenomenalScene, rationale: list[str]) -> float:
        """Compute gain modulation based on risk and proto-qualia"""
        # Base gain (inverse of risk)
        base_gain = max(0.2, 1.0 - scene.risk.score)

        # Adjust for extreme values
        if scene.proto.arousal > 0.9:
            base_gain *= 0.7  # Reduce gain for extreme arousal
            rationale.append(f"Extreme arousal → gain reduction to {base_gain:.2f}")
        elif scene.proto.arousal < 0.1:
            base_gain *= 1.2  # Boost gain for low arousal
            rationale.append(f"Low arousal → gain boost to {base_gain:.2f}")

        return min(1.0, base_gain)

    def _compute_pace_modulation(self, scene: PhenomenalScene, rationale: list[str]) -> float:
        """Compute pace modulation based on temporal dynamics"""
        # Base pace (inverse of arousal)
        base_pace = max(0.3, 1.0 - scene.proto.arousal)

        # Adjust for temporal feel
        if scene.proto.temporal_feel.value == "urgent":
            base_pace *= 0.8  # Slow down urgent experiences
            rationale.append(f"Urgent temporal feel → pace reduction to {base_pace:.2f}")
        elif scene.proto.temporal_feel.value == "suspended":
            base_pace *= 1.1  # Speed up suspended experiences
            rationale.append(f"Suspended temporal feel → pace increase to {base_pace:.2f}")

        return min(1.0, base_pace)

    def _compute_scene_hash(self, scene: PhenomenalScene) -> str:
        """Compute hash for scene caching"""
        # Use key proto-qualia and risk factors for hashing
        hash_data = {
            "tone": round(scene.proto.tone, 3),
            "arousal": round(scene.proto.arousal, 3),
            "clarity": round(scene.proto.clarity, 3),
            "embodiment": round(scene.proto.embodiment, 3),
            "narrative_gravity": round(scene.proto.narrative_gravity, 3),
            "risk_score": round(scene.risk.score, 3),
            "risk_severity": scene.risk.severity.value,
            "temporal_feel": scene.proto.temporal_feel.value,
            "agency_feel": scene.proto.agency_feel.value,
        }

        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]

    def _create_cached_audit_entry(
        self, scene: PhenomenalScene, policy: RegulationPolicy, energy_before: float
    ) -> RegulationAuditEntry:
        """Create audit entry for cached policy"""
        return RegulationAuditEntry(
            timestamp=time.time(),
            scene_id=self._compute_scene_hash(scene),
            proto_qualia_snapshot={
                "tone": scene.proto.tone,
                "arousal": scene.proto.arousal,
                "clarity": scene.proto.clarity,
                "embodiment": scene.proto.embodiment,
                "narrative_gravity": scene.proto.narrative_gravity,
            },
            risk_assessment={
                "score": scene.risk.score,
                "severity": scene.risk.severity.value,
                "reasons": scene.risk.reasons,
            },
            policy_decision={
                "gain": policy.gain,
                "pace": policy.pace,
                "color_contrast": policy.color_contrast,
                "actions": policy.actions,
            },
            energy_before=energy_before,
            energy_after=0.0,
            conservation_ratio=1.0,
            decision_rationale=["Policy retrieved from cache"],
            performance_metrics={
                "processing_time_ms": 0.1,  # Minimal cache lookup time
                "cache_hit": True,
                "rules_triggered": 0,
                "actions_count": len(policy.actions),
            },
        )

    def _log_audit_entry(self, entry: RegulationAuditEntry) -> None:
        """Log audit entry to persistent storage"""
        # Add to in-memory log
        self.audit_log.append(entry)

        # Trim log if too large
        if len(self.audit_log) > self.config["max_audit_entries"]:
            self.audit_log = self.audit_log[-self.config["max_audit_entries"] :]

        # Write to file if path configured
        if "audit_log_path" in self.config:
            try:
                log_path = Path(self.config["audit_log_path"])
                log_path.parent.mkdir(parents=True, exist_ok=True)

                with open(log_path, "a") as f:
                    json.dump(asdict(entry), f)
                    f.write("\n")

            except Exception as e:
                print(f"Warning: Failed to write audit log: {e}")

    def get_audit_statistics(self) -> dict[str, Any]:
        """Get audit trail statistics"""
        if not self.audit_log:
            return {"total_entries": 0}

        # Compute statistics
        total_entries = len(self.audit_log)
        avg_processing_time = (
            sum(e.performance_metrics.get("processing_time_ms", 0) for e in self.audit_log) / total_entries
        )
        cache_hit_rate = sum(1 for e in self.audit_log if e.performance_metrics.get("cache_hit", False)) / total_entries
        conservation_violations = sum(
            1 for e in self.audit_log if e.performance_metrics.get("conservation_violation", False)
        )

        # Action frequency
        action_counts = {}
        for entry in self.audit_log:
            for action in entry.policy_decision["actions"]:
                action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_entries": total_entries,
            "average_processing_time_ms": avg_processing_time,
            "cache_hit_rate": cache_hit_rate,
            "conservation_violations": conservation_violations,
            "conservation_violation_rate": conservation_violations / total_entries,
            "action_frequency": action_counts,
            "recent_entries": min(10, total_entries),
        }

    def export_audit_log(self, format: str = "json") -> str:
        """Export complete audit log for analysis"""
        if format == "json":
            return json.dumps([asdict(entry) for entry in self.audit_log], indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
