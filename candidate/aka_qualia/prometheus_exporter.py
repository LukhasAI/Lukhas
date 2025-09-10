#!/usr/bin/env python3

"""
Prometheus Metrics Exporter for Aka Qualia
=========================================

Exports consciousness metrics with akaq_ prefixed gauges and counters
as specified by Freud-2025 for Wave B-B4 implementation.

Provides real-time observability into:
- Proto-qualia dimensions and energy
- Regulation policy effectiveness
- VIVOX integration health
- TEQ Guardian interventions
- Energy conservation compliance
"""
import time
from typing import Any, Optional

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

# Proto-qualia dimensional metrics
akaq_tone = Gauge("akaq_tone", "Proto-qualia tone dimension [-1,1]", ["episode_id"])
akaq_arousal = Gauge("akaq_arousal", "Proto-qualia arousal dimension [0,1]", ["episode_id"])
akaq_clarity = Gauge("akaq_clarity", "Proto-qualia clarity dimension [0,1]", ["episode_id"])
akaq_embodiment = Gauge("akaq_embodiment", "Proto-qualia embodiment dimension [0,1]", ["episode_id"])
akaq_narrative_gravity = Gauge("akaq_narrative_gravity", "Proto-qualia narrative gravity [0,1]", ["episode_id"])

# Energy accounting metrics (Freud-2025 formulas)
akaq_affect_energy = Gauge("akaq_affect_energy", "Computed affect energy E_t", ["episode_id"])
akaq_energy_before_regulation = Gauge("akaq_energy_before_regulation", "Energy snapshot before regulation")
akaq_energy_after_regulation = Gauge("akaq_energy_after_regulation", "Energy snapshot after regulation")
akaq_energy_conservation_ratio = Gauge("akaq_energy_conservation_ratio", "Energy conservation ratio (after/before)")
akaq_energy_delta_absolute = Gauge("akaq_energy_delta_absolute", "Absolute energy change |E_before - E_after|")

# Consciousness quality metrics
akaq_drift_phi = Gauge(
    "akaq_drift_phi",
    "Temporal coherence metric (1 = perfect coherence)",
    ["episode_id"],
)
akaq_congruence_index = Gauge("akaq_congruence_index", "Goals↔ethics↔scene alignment index", ["episode_id"])
akaq_sublimation_rate = Gauge("akaq_sublimation_rate", "Proportion of affect energy transformed", ["episode_id"])
akaq_neurosis_risk = Gauge("akaq_neurosis_risk", "Estimated loop recurrence probability", ["episode_id"])
akaq_qualia_novelty = Gauge("akaq_qualia_novelty", "Novelty compared to recent history", ["episode_id"])
akaq_repair_delta = Gauge("akaq_repair_delta", "Repair improvement after regulation", ["episode_id"])

# Risk and regulation metrics
akaq_risk_score = Gauge("akaq_risk_score", "TEQ Guardian risk assessment score", ["severity"])
akaq_regulation_gain = Gauge("akaq_regulation_gain", "Applied gain modulation factor")
akaq_regulation_pace = Gauge("akaq_regulation_pace", "Applied pace modulation factor")
akaq_regulation_actions_count = Gauge("akaq_regulation_actions_count", "Number of regulation actions applied")

# VIVOX integration health
akaq_vivox_drift_score = Gauge("akaq_vivox_drift_score", "VIVOX computed drift score")
akaq_vivox_drift_threshold = Gauge("akaq_vivox_drift_threshold", "VIVOX drift threshold (typically 0.15)")
akaq_vivox_collapse_hash_changes = Counter("akaq_vivox_collapse_hash_changes_total", "VIVOX CollapseHash changes")
akaq_vivox_stabilization_required = Counter("akaq_vivox_stabilization_required_total", "VIVOX stabilization events")

# Processing performance
akaq_processing_time = Histogram("akaq_processing_time_seconds", "Full step() processing time")
akaq_regulation_processing_time = Histogram(
    "akaq_regulation_processing_time_seconds", "Regulation policy generation time"
)
akaq_metrics_computation_time = Histogram("akaq_metrics_computation_time_seconds", "Metrics computation time")

# System counters
akaq_scenes_processed_total = Counter("akaq_scenes_processed_total", "Total phenomenological scenes processed")
akaq_regulations_applied_total = Counter("akaq_regulations_applied_total", "Total regulation policies applied")
akaq_energy_conservation_violations_total = Counter(
    "akaq_energy_conservation_violations_total", "Energy conservation violations"
)
akaq_teq_interventions_total = Counter("akaq_teq_interventions_total", "TEQ Guardian interventions", ["severity"])
akaq_cache_hits_total = Counter("akaq_cache_hits_total", "Regulation policy cache hits")
akaq_cache_misses_total = Counter("akaq_cache_misses_total", "Regulation policy cache misses")

# Action frequency counters
akaq_regulation_actions_total = Counter("akaq_regulation_actions_total", "Regulation actions by type", ["action_type"])

# System info
akaq_system_info = Info("akaq_system_info", "Aka Qualia system information")
akaq_vivox_integration_info = Info("akaq_vivox_integration_info", "VIVOX integration status")


class PrometheusExporter:
    """
    Prometheus metrics exporter for Aka Qualia system.

    Provides comprehensive observability into consciousness processing
    with standardized akaq_ prefixed metrics for monitoring and alerting.
    """

    def __init__(self, system_info: Optional[dict[str, str]] = None):
        """
        Initialize Prometheus exporter.

        Args:
            system_info: System metadata for info metrics
        """
        self.initialization_time = time.time()
        self.last_export_time = 0.0

        # Set system info
        if system_info:
            akaq_system_info.info(system_info)

    def update_proto_qualia_metrics(self, proto_qualia: Any, episode_id: str) -> None:
        """Update proto-qualia dimensional metrics"""
        akaq_tone.labels(episode_id=episode_id).set(proto_qualia.tone)
        akaq_arousal.labels(episode_id=episode_id).set(proto_qualia.arousal)
        akaq_clarity.labels(episode_id=episode_id).set(proto_qualia.clarity)
        akaq_embodiment.labels(episode_id=episode_id).set(proto_qualia.embodiment)
        akaq_narrative_gravity.labels(episode_id=episode_id).set(proto_qualia.narrative_gravity)

    def update_energy_metrics(self, energy_snapshot: Any) -> None:
        """Update energy accounting metrics"""
        akaq_energy_before_regulation.set(energy_snapshot.energy_before)
        akaq_energy_after_regulation.set(energy_snapshot.energy_after)

        # Compute derived metrics
        conservation_ratio = (
            energy_snapshot.energy_after / energy_snapshot.energy_before if energy_snapshot.energy_before > 0 else 1.0
        )
        akaq_energy_conservation_ratio.set(conservation_ratio)

        energy_delta = abs(energy_snapshot.energy_before - energy_snapshot.energy_after)
        akaq_energy_delta_absolute.set(energy_delta)

        # Count violations
        if energy_snapshot.conservation_violation:
            akaq_energy_conservation_violations_total.inc()

    def update_consciousness_quality_metrics(self, metrics: Any, episode_id: str) -> None:
        """Update consciousness quality metrics"""
        akaq_drift_phi.labels(episode_id=episode_id).set(metrics.drift_phi)
        akaq_congruence_index.labels(episode_id=episode_id).set(metrics.congruence_index)
        akaq_sublimation_rate.labels(episode_id=episode_id).set(metrics.sublimation_rate)
        akaq_neurosis_risk.labels(episode_id=episode_id).set(metrics.neurosis_risk)
        akaq_qualia_novelty.labels(episode_id=episode_id).set(metrics.qualia_novelty)
        akaq_repair_delta.labels(episode_id=episode_id).set(metrics.repair_delta)

    def update_regulation_metrics(self, policy: Any, audit_entry: Any) -> None:
        """Update regulation policy metrics"""
        akaq_regulation_gain.set(policy.gain)
        akaq_regulation_pace.set(policy.pace)
        akaq_regulation_actions_count.set(len(policy.actions))

        # Count regulation actions by type
        for action in policy.actions:
            akaq_regulation_actions_total.labels(action_type=action).inc()

        # Processing time from audit entry
        processing_time = audit_entry.performance_metrics.get("processing_time_ms", 0) / 1000.0
        akaq_regulation_processing_time.observe(processing_time)

        # Cache metrics
        if audit_entry.performance_metrics.get("cache_hit", False):
            akaq_cache_hits_total.inc()
        else:
            akaq_cache_misses_total.inc()

        akaq_regulations_applied_total.inc()

    def update_risk_metrics(self, risk_profile: Any) -> None:
        """Update TEQ Guardian risk metrics"""
        akaq_risk_score.labels(severity=risk_profile.severity.value).set(risk_profile.score)

        # Count interventions by severity
        if risk_profile.score > 0.1:  # Only count meaningful interventions
            akaq_teq_interventions_total.labels(severity=risk_profile.severity.value).inc()

    def update_vivox_metrics(self, vivox_results: dict[str, Any]) -> None:
        """Update VIVOX integration metrics"""
        if "drift_analysis" in vivox_results:
            drift_data = vivox_results["drift_analysis"]
            akaq_vivox_drift_score.set(drift_data.get("drift_score", 0.0))

            if drift_data.get("stabilization_required", False):
                akaq_vivox_stabilization_required.inc()

        # Set drift threshold (typically 0.15)
        akaq_vivox_drift_threshold.set(0.15)

        # Track collapse hash changes (would need additional logic to detect changes)
        # akaq_vivox_collapse_hash_changes.inc()  # Increment when hash changes

    def update_processing_performance(self, step_duration: float, metrics_duration: Optional[float] = None) -> None:
        """Update processing performance metrics"""
        akaq_processing_time.observe(step_duration)

        if metrics_duration is not None:
            akaq_metrics_computation_time.observe(metrics_duration)

    def record_scene_processed(self, result: dict[str, Any]) -> None:
        """Record a complete scene processing cycle"""
        akaq_scenes_processed_total.inc()

        # Extract and update all relevant metrics
        scene = result.get("scene")
        metrics = result.get("metrics")
        energy_snapshot = result.get("energy_snapshot")
        vivox_results = result.get("vivox_results", {})

        if scene and metrics:
            episode_id = metrics.episode_id

            # Update proto-qualia metrics
            self.update_proto_qualia_metrics(scene.proto, episode_id)

            # Update consciousness quality metrics
            self.update_consciousness_quality_metrics(metrics, episode_id)

            # Update risk metrics
            self.update_risk_metrics(scene.risk)

        # Update energy metrics
        if energy_snapshot:
            self.update_energy_metrics(energy_snapshot)

        # Update VIVOX metrics
        if vivox_results:
            self.update_vivox_metrics(vivox_results)

    def get_metrics_endpoint(self) -> tuple[str, str]:
        """
        Get Prometheus metrics in exposition format.

        Returns:
            Tuple of (metrics_content, content_type)
        """
        self.last_export_time = time.time()
        return generate_latest(), CONTENT_TYPE_LATEST

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get human-readable metrics summary"""
        current_time = time.time()
        uptime = current_time - self.initialization_time

        # Get counter values (note: in real Prometheus, we'd query the registry)
        return {
            "uptime_seconds": uptime,
            "last_export_time": self.last_export_time,
            "scenes_processed": (
                akaq_scenes_processed_total._value._value if hasattr(akaq_scenes_processed_total, "_value") else 0
            ),
            "regulations_applied": (
                akaq_regulations_applied_total._value._value if hasattr(akaq_regulations_applied_total, "_value") else 0
            ),
            "energy_violations": (
                akaq_energy_conservation_violations_total._value._value
                if hasattr(akaq_energy_conservation_violations_total, "_value")
                else 0
            ),
            "current_metrics": {
                "energy_conservation_ratio": (
                    akaq_energy_conservation_ratio._value._value
                    if hasattr(akaq_energy_conservation_ratio, "_value")
                    else 1.0
                ),
                "vivox_drift_score": (
                    akaq_vivox_drift_score._value._value if hasattr(akaq_vivox_drift_score, "_value") else 0.0
                ),
                "regulation_gain": (
                    akaq_regulation_gain._value._value if hasattr(akaq_regulation_gain, "_value") else 1.0
                ),
                "regulation_pace": (
                    akaq_regulation_pace._value._value if hasattr(akaq_regulation_pace, "_value") else 1.0
                ),
            },
        }

    def set_vivox_integration_status(self, status: dict[str, Any]) -> None:
        """Set VIVOX integration status info"""
        akaq_vivox_integration_info.info(
            {
                "drift_threshold": str(status.get("drift_threshold", "0.15")),
                "collapse_validation_enabled": str(status.get("collapse_validation_enabled", True)),
                "me_integration_enabled": str(status.get("me_integration_enabled", True)),
                "status": status.get("status", "unknown"),
            }
        )