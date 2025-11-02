"""
LUKHAS Metrics Collection ⚛️📊
Prometheus-compatible metrics for monitoring and alerting.
"""

import time

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, generate_latest

# Counters for security events
incident_blocked_tool = Counter(
    "lukhas_incident_blocked_tool_total",
    "Total number of blocked tool attempts",
    ["attempted_tool", "safety_mode"],
)

strict_auto_tighten = Counter(
    "lukhas_strict_auto_tighten_total",
    "Number of times safety auto-tightened to strict",
    ["trigger_reason"],
)

openai_errors = Counter(
    "lukhas_openai_errors_total",
    "OpenAI API errors by type",
    ["error_type", "status_code"],
)

# Histograms for performance
tool_duration_ms = Histogram(
    "lukhas_tool_duration_milliseconds",
    "Tool execution duration in milliseconds",
    ["tool_name", "status"],
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000),
)

openai_latency_ms = Histogram(
    "lukhas_openai_latency_milliseconds",
    "OpenAI API call latency in milliseconds",
    ["model", "safety_mode"],
    buckets=(100, 250, 500, 1000, 2000, 3000, 5000, 10000),
)

token_usage = Histogram(
    "lukhas_token_usage",
    "Tokens used per request",
    ["direction", "model"],  # direction: input/output
    buckets=(10, 50, 100, 250, 500, 1000, 2000, 4000, 8000),
)

# Gauges for current state
current_safety_mode = Gauge(
    "lukhas_current_safety_mode",
    "Current safety mode (0=creative, 1=balanced, 2=strict)",
    ["session_id"],
)

active_tool_calls = Gauge("lukhas_active_tool_calls", "Number of currently active tool calls")

feedback_lut_temperature = Gauge(
    "lukhas_feedback_lut_temperature_delta",
    "Current LUT temperature adjustment",
)

# Rate tracking
requests_per_minute = Counter(
    "lukhas_requests_per_minute",
    "Requests processed per minute",
    ["endpoint", "status"],
)

# === AKA QUALIA PHENOMENOLOGICAL METRICS (B4: Wave B Implementation) ===

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

# VIVOX integration health
akaq_vivox_drift_score = Gauge("akaq_vivox_drift_score", "VIVOX computed drift score")
akaq_vivox_drift_exceeded = Counter("akaq_vivox_drift_exceeded_total", "VIVOX drift threshold exceeded events")

# Processing performance for consciousness
akaq_processing_time = Histogram(
    "akaq_processing_time_seconds",
    "Full step() processing time",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)
akaq_regulation_processing_time = Histogram(
    "akaq_regulation_processing_time_seconds",
    "Regulation policy generation time",
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05),
)

# System counters
akaq_scenes_processed_total = Counter("akaq_scenes_processed_total", "Total phenomenological scenes processed")
akaq_regulations_applied_total = Counter("akaq_regulations_applied_total", "Total regulation policies applied")
akaq_energy_conservation_violations_total = Counter(
    "akaq_energy_conservation_violations_total", "Energy conservation violations"
)
akaq_teq_interventions_total = Counter("akaq_teq_interventions_total", "TEQ Guardian interventions", ["severity"])

# Action frequency counters
akaq_regulation_actions_total = Counter("akaq_regulation_actions_total", "Regulation actions by type", ["action_type"])


class MetricsCollector:
    """Centralized metrics collection"""

    def __init__(self):
        self.start_time = time.time()

    def record_blocked_tool(self, tool_name: str, safety_mode: str):
        """Record a blocked tool attempt"""
        incident_blocked_tool.labels(attempted_tool=tool_name, safety_mode=safety_mode).inc()

    def record_auto_tighten(self, reason: str = "high_risk"):
        """Record auto-tightening to strict mode"""
        strict_auto_tighten.labels(trigger_reason=reason).inc()

    def record_openai_error(self, error_type: str, status_code: int = 0):
        """Record OpenAI API error"""
        openai_errors.labels(error_type=error_type, status_code=str(status_code)).inc()

    def record_tool_duration(self, tool_name: str, duration_ms: float, status: str = "success"):
        """Record tool execution duration"""
        tool_duration_ms.labels(tool_name=tool_name, status=status).observe(duration_ms)

    def record_openai_latency(self, model: str, latency_ms: float, safety_mode: str = "balanced"):
        """Record OpenAI API latency"""
        openai_latency_ms.labels(model=model, safety_mode=safety_mode).observe(latency_ms)

    def record_token_usage(self, input_tokens: int, output_tokens: int, model: str = "gpt-4"):
        """Record token usage"""
        token_usage.labels(direction="input", model=model).observe(input_tokens)
        token_usage.labels(direction="output", model=model).observe(output_tokens)

    def set_safety_mode(self, mode: str, session_id: str = "default"):
        """Update current safety mode gauge"""
        mode_values = {"creative": 0, "balanced": 1, "strict": 2}
        current_safety_mode.labels(session_id=session_id).set(mode_values.get(mode, 1))

    def set_active_tools(self, count: int):
        """Update active tool calls gauge"""
        active_tool_calls.set(count)

    def set_lut_temperature(self, delta: float):
        """Update LUT temperature adjustment gauge"""
        feedback_lut_temperature.set(delta)

    def record_request(self, endpoint: str, status: str = "success"):
        """Record API request"""
        requests_per_minute.labels(endpoint=endpoint, status=status).inc()

    # === AKA QUALIA METRICS RECORDING METHODS ===

    def record_aka_qualia_scene(self, scene_result: dict):
        """Record complete Aka Qualia scene processing result (B4: akaq_ metrics integration)"""
        scene = scene_result.get("scene")
        metrics_data = scene_result.get("metrics")
        energy_snapshot = scene_result.get("energy_snapshot")
        vivox_results = scene_result.get("vivox_results", {})

        if not scene or not metrics_data:
            return

        episode_id = metrics_data.episode_id

        # Record proto-qualia dimensions
        akaq_tone.labels(episode_id=episode_id).set(scene.proto.tone)
        akaq_arousal.labels(episode_id=episode_id).set(scene.proto.arousal)
        akaq_clarity.labels(episode_id=episode_id).set(scene.proto.clarity)
        akaq_embodiment.labels(episode_id=episode_id).set(scene.proto.embodiment)
        akaq_narrative_gravity.labels(episode_id=episode_id).set(scene.proto.narrative_gravity)

        # Record consciousness quality metrics
        akaq_drift_phi.labels(episode_id=episode_id).set(metrics_data.drift_phi)
        akaq_congruence_index.labels(episode_id=episode_id).set(metrics_data.congruence_index)
        akaq_sublimation_rate.labels(episode_id=episode_id).set(metrics_data.sublimation_rate)
        akaq_neurosis_risk.labels(episode_id=episode_id).set(metrics_data.neurosis_risk)
        akaq_qualia_novelty.labels(episode_id=episode_id).set(metrics_data.qualia_novelty)
        akaq_repair_delta.labels(episode_id=episode_id).set(metrics_data.repair_delta)

        # Record risk assessment
        akaq_risk_score.labels(severity=scene.risk.severity.value).set(scene.risk.score)
        if scene.risk.score > 0.1:  # Only count meaningful interventions
            akaq_teq_interventions_total.labels(severity=scene.risk.severity.value).inc()

        # Record energy accounting
        if energy_snapshot:
            akaq_energy_before_regulation.set(energy_snapshot.energy_before)
            akaq_energy_after_regulation.set(energy_snapshot.energy_after)

            conservation_ratio = (
                energy_snapshot.energy_after / energy_snapshot.energy_before
                if energy_snapshot.energy_before > 0
                else 1.0
            )
            akaq_energy_conservation_ratio.set(conservation_ratio)

            if energy_snapshot.conservation_violation:
                akaq_energy_conservation_violations_total.inc()

        # Record VIVOX metrics
        if "drift_analysis" in vivox_results:
            drift_data = vivox_results["drift_analysis"]
            akaq_vivox_drift_score.set(drift_data.get("drift_score", 0.0))

            if drift_data.get("drift_exceeded", False):
                akaq_vivox_drift_exceeded.inc()

        # Increment scene counter
        akaq_scenes_processed_total.inc()

    def record_aka_qualia_regulation(self, policy: dict, audit_entry: dict):
        """Record regulation policy application"""
        akaq_regulation_gain.set(policy.get("gain", 1.0))
        akaq_regulation_pace.set(policy.get("pace", 1.0))

        # Record actions by type
        for action in policy.get("actions", []):
            akaq_regulation_actions_total.labels(action_type=action).inc()

        # Record processing time
        processing_time = audit_entry.get("performance_metrics", {}).get("processing_time_ms", 0) / 1000.0
        if processing_time > 0:
            akaq_regulation_processing_time.observe(processing_time)

        akaq_regulations_applied_total.inc()

    def record_aka_qualia_processing_time(self, duration_seconds: float):
        """Record overall Aka Qualia processing time"""
        akaq_processing_time.observe(duration_seconds)

    def get_metrics(self) -> bytes:
        """Generate Prometheus metrics output"""
        return generate_latest(REGISTRY)

    def check_alert_conditions(self) -> list:
        """Check for alert conditions"""
        alerts = []

        # Get current metric values (simplified for demo)
        # In production, query Prometheus or use metric._value

        # Check blocked tools rate
        # if blocked_tools_per_hour > 10:
        #     alerts.append({
        #         "level": "warning",
        #         "message": "High rate of blocked tool attempts",
        #         "metric": "incident_blocked_tool",
        #         "threshold": 10
        #     })

        # Check auto-tightening rate
        # if auto_tighten_per_hour > 5:
        #     alerts.append({
        #         "level": "warning",
        #         "message": "Frequent auto-tightening to strict mode",
        #         "metric": "strict_auto_tighten",
        #         "threshold": 5
        #     })

        # Check error rate
        # if openai_errors_per_minute > 1:
        #     alerts.append({
        #         "level": "critical",
        #         "message": "High OpenAI API error rate",
        #         "metric": "openai_errors",
        #         "threshold": 1
        #     })

        return alerts


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector"""
    return _metrics_collector
