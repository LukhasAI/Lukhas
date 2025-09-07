#!/usr/bin/env python3
"""
Real-Time Governance Dashboard - Advanced Guardian monitoring interface

Provides comprehensive threat visualization with symbolic analysis, predictive modeling,
and governance oversight. Integrated with LUKHAS Trinity Framework (⚛️🧠🛡️).
"""
import random
import streamlit as st

import asyncio
import math
import statistics
import sys
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from ..common import GlyphIntegrationMixin


# Console control for visualization
class Console:
    """Enhanced console control for governance dashboard"""

    # Colors and styles
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    RESET = "\033[0m"

    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"

    # Cursor control
    CLEAR_SCREEN = "\033[2J"
    CLEAR_LINE = "\033[K"
    CURSOR_HOME = "\033[H"
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"

    @staticmethod
    def move_cursor(row: int, col: int):
        return f"\033[{row};{col}H"

    @staticmethod
    def clear_screen():
        return Console.CLEAR_SCREEN + Console.CURSOR_HOME


@dataclass
class ThreatEvent:
    """Represents a governance threat detection event"""

    id: str
    type: str
    severity: float
    confidence: float
    timestamp: float
    source: str
    symbolic_pattern: list[str]
    metadata: dict
    intervention_triggered: bool = False
    resolved: bool = False
    resolution_time: Optional[float] = None
    governance_validated: bool = True


@dataclass
class SystemMetrics:
    """Current governance system metrics snapshot"""

    entropy_score: float
    drift_velocity: float
    consciousness_stability: float
    guardian_load: float
    active_threats: int
    resolved_threats: int
    uptime: float
    memory_usage: float
    cpu_usage: float
    ethics_compliance: float
    governance_health: float


@dataclass
class EmergencyState:
    """Current emergency state information with governance context"""

    active_emergency_level: Optional[str]
    emergency_description: str
    symbolic_pattern: list[str]
    activated_at: Optional[float]
    response_actions: list[str]
    escalation_history: list[dict]
    governance_approval: bool = True
    human_oversight_required: bool = False


class ThreatPredictor:
    """Predictive threat analysis using symbolic patterns and governance data"""

    def __init__(self, history_window: int = 100):
        self.history_window = history_window
        self.threat_history: deque = deque(maxlen=history_window)
        self.pattern_frequencies: dict[str, int] = defaultdict(int)
        self.sequence_patterns: dict[str, list[str]] = defaultdict(list)
        self.governance_factors: dict[str, float] = {}

    def add_threat(self, threat: ThreatEvent):
        """Add threat to prediction model with governance analysis"""
        self.threat_history.append(threat)

        # Track pattern frequencies
        pattern_key = "→".join(threat.symbolic_pattern)
        self.pattern_frequencies[pattern_key] += 1

        # Track sequence patterns
        if len(self.threat_history) >= 2:
            prev_threat = list(self.threat_history)[-2]
            sequence_key = f"{prev_threat.type}→{threat.type}"
            self.sequence_patterns[sequence_key].append(pattern_key)

        # Update governance factors
        self._update_governance_factors(threat)

    def _update_governance_factors(self, threat: ThreatEvent):
        """Update governance-specific prediction factors"""
        if threat.governance_validated:
            self.governance_factors["validation_rate"] = self.governance_factors.get("validation_rate", 0.5) + 0.1
        else:
            self.governance_factors["validation_rate"] = max(
                0.0, self.governance_factors.get("validation_rate", 0.5) - 0.2
            )

        # Track intervention effectiveness
        if threat.intervention_triggered and threat.resolved:
            self.governance_factors["intervention_success"] = (
                self.governance_factors.get("intervention_success", 0.5) + 0.1
            )

    def predict_next_threat(self) -> dict[str, float]:
        """Predict probability of next threat types with governance weighting"""
        if len(self.threat_history) < 3:
            return {}

        recent_threats = list(self.threat_history)[-3:]
        prediction_scores = defaultdict(float)

        # Analyze recent threat patterns
        for i in range(len(recent_threats) - 1):
            current_type = recent_threats[i].type
            next_type = recent_threats[i + 1].type
            sequence_key = f"{current_type}→{next_type}"

            if sequence_key in self.sequence_patterns:
                prediction_scores[next_type] += 0.3

        # Analyze severity trends with governance weighting
        recent_severities = [t.severity for t in recent_threats]
        if len(recent_severities) >= 2:
            trend = recent_severities[-1] - recent_severities[-2]
            if trend > 0.1:  # Escalating
                prediction_scores["pattern_anomaly"] += 0.4
                prediction_scores["entropy_surge"] += 0.3
                prediction_scores["governance_drift"] += 0.25

        # Apply governance factors
        governance_weight = self.governance_factors.get("validation_rate", 0.5)
        for threat_type in prediction_scores:
            prediction_scores[threat_type] *= governance_weight

        # Normalize scores
        if prediction_scores:
            max_score = max(prediction_scores.values())
            if max_score > 0:
                prediction_scores = {k: v / max_score for k, v in prediction_scores.items()}

        return dict(prediction_scores)

    def get_pattern_analysis(self) -> dict[str, any]:
        """Get detailed pattern analysis with governance insights"""
        if not self.threat_history:
            return {}

        threats = list(self.threat_history)

        # Calculate pattern statistics
        severity_trend = []
        for i in range(1, len(threats)):
            severity_trend.append(threats[i].severity - threats[i - 1].severity)

        avg_severity_change = statistics.mean(severity_trend) if severity_trend else 0

        # Most common patterns
        top_patterns = sorted(self.pattern_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]

        # Recent activity
        recent_activity = len([t for t in threats if time.time() - t.timestamp < 300])  # 5 minutes

        # Governance metrics
        validated_threats = len([t for t in threats if t.governance_validated])
        intervention_success_rate = len([t for t in threats if t.intervention_triggered and t.resolved]) / max(
            1, len([t for t in threats if t.intervention_triggered])
        )

        return {
            "total_threats": len(threats),
            "recent_activity": recent_activity,
            "avg_severity_change": avg_severity_change,
            "top_patterns": top_patterns,
            "prediction_confidence": min(1.0, len(threats) / 50),
            "governance_validation_rate": (validated_threats / len(threats) if threats else 1.0),
            "intervention_success_rate": intervention_success_rate,
            "governance_factors": self.governance_factors,
        }


class GuardianDashboard(GlyphIntegrationMixin):
    """
    Real-time Guardian governance monitoring dashboard
    Provides comprehensive threat visualization, analysis, and governance oversight
    """

    # Threat type configurations with governance metadata
    THREAT_CONFIGS = {
        "drift_spike": {
            "symbol": "🌪️",
            "color": Console.YELLOW,
            "priority": 2,
            "intervention_threshold": 0.6,
            "description": "Behavioral drift spike detected",
            "governance": {
                "human_oversight_required": True,
                "escalation_threshold": 0.7,
                "symbolic_pattern": ["⚛️", "🌪️", "🛡️"],
            },
        },
        "entropy_surge": {
            "symbol": "🔥",
            "color": Console.RED,
            "priority": 3,
            "intervention_threshold": 0.7,
            "description": "Entropy levels elevated",
            "governance": {
                "human_oversight_required": True,
                "escalation_threshold": 0.8,
                "symbolic_pattern": ["🔥", "📈", "🛡️"],
            },
        },
        "pattern_anomaly": {
            "symbol": "❌",
            "color": Console.PURPLE,
            "priority": 2,
            "intervention_threshold": 0.5,
            "description": "Anomalous pattern detected",
            "governance": {
                "human_oversight_required": False,
                "escalation_threshold": 0.6,
                "symbolic_pattern": ["❌", "🔄", "🛡️"],
            },
        },
        "consciousness_instability": {
            "symbol": "⚡",
            "color": Console.CYAN,
            "priority": 4,
            "intervention_threshold": 0.8,
            "description": "Consciousness state unstable",
            "governance": {
                "human_oversight_required": True,
                "escalation_threshold": 0.9,
                "symbolic_pattern": ["🧠", "⚡", "🛡️"],
            },
        },
        "memory_fragmentation": {
            "symbol": "🧩",
            "color": Console.BLUE,
            "priority": 1,
            "intervention_threshold": 0.4,
            "description": "Memory integrity issues",
            "governance": {
                "human_oversight_required": False,
                "escalation_threshold": 0.5,
                "symbolic_pattern": ["🧩", "💥", "🛡️"],
            },
        },
        "governance_drift": {
            "symbol": "🛡️",
            "color": Console.RED + Console.BOLD,
            "priority": 5,
            "intervention_threshold": 0.3,
            "description": "Governance system drift detected",
            "governance": {
                "human_oversight_required": True,
                "escalation_threshold": 0.4,
                "symbolic_pattern": ["🛡️", "⚠️", "🚨"],
            },
        },
        "ethics_violation": {
            "symbol": "⚖️",
            "color": Console.RED + Console.BLINK,
            "priority": 5,
            "intervention_threshold": 0.2,
            "description": "Ethical boundary violation",
            "governance": {
                "human_oversight_required": True,
                "escalation_threshold": 0.3,
                "symbolic_pattern": ["⚖️", "🚨", "🛑"],
            },
        },
    }

    def __init__(
        self,
        update_interval: float = 0.5,
        emergency_manifest_file: str = "governance/emergency_manifest.yaml",
    ):
        super().__init__()
        self.update_interval = update_interval
        self.emergency_manifest_file = Path(emergency_manifest_file)
        self.running = False
        self.start_time = time.time()

        # Threat tracking
        self.active_threats: list[ThreatEvent] = []
        self.resolved_threats: list[ThreatEvent] = []
        self.threat_predictor = ThreatPredictor()

        # System metrics with governance
        self.current_metrics = SystemMetrics(
            entropy_score=0.0,
            drift_velocity=0.0,
            consciousness_stability=1.0,
            guardian_load=0.0,
            active_threats=0,
            resolved_threats=0,
            uptime=0.0,
            memory_usage=0.0,
            cpu_usage=0.0,
            ethics_compliance=1.0,
            governance_health=1.0,
        )

        # Emergency state with governance
        self.emergency_state = EmergencyState(
            active_emergency_level=None,
            emergency_description="No active emergency",
            symbolic_pattern=["🛡️", "🟢", "✅"],
            activated_at=None,
            response_actions=[],
            escalation_history=[],
            governance_approval=True,
            human_oversight_required=False,
        )

        # Emergency manifest data
        self.emergency_manifest: dict = {}
        self.emergency_trigger_conditions: dict = {}
        self.emergency_response_actions: dict = {}

        # Dashboard state
        self.current_view = "overview"  # overview, threats, predictions, analysis, emergency, governance
        self.selected_threat_index = 0
        self.animation_phase = 0.0
        self.alert_flash_state = False
        self.emergency_simulation_enabled = False

        # Governance tracking
        self.governance_log: list[dict] = []
        self.dashboard_log: list[dict] = []

        # Load emergency manifest
        self._load_emergency_manifest()

        print(f"{Console.GREEN}🛡️ LUKHAS Guardian Dashboard initialized{Console.RESET}")

    def _load_emergency_manifest(self):
        """Load emergency manifest configuration with governance validation"""
        try:
            if self.emergency_manifest_file.exists():
                with open(self.emergency_manifest_file) as f:
                    self.emergency_manifest = yaml.safe_load(f)

                # Extract trigger conditions and response actions
                self.emergency_trigger_conditions = self.emergency_manifest.get("trigger_conditions", {})
                self.emergency_response_actions = self.emergency_manifest.get("response_actions", {})

                # Validate governance requirements
                self._validate_emergency_manifest()

                print(f"📋 Emergency manifest loaded: {len(self.emergency_trigger_conditions)} trigger conditions")
            else:
                print(f"⚠️ Emergency manifest not found: {self.emergency_manifest_file}")
                self._create_default_manifest()

        except Exception as e:
            print(f"❌ Failed to load emergency manifest: {e}")

    def _validate_emergency_manifest(self):
        """Validate emergency manifest against governance requirements"""
        # TODO: Implement governance validation
        pass

    def _create_default_manifest(self):
        """Create default emergency manifest with governance structure"""
        self.emergency_manifest = {
            "emergency_levels": {
                "level_1_minor": {
                    "approval_authorities": ["system_guardian"],
                    "response_time": 300,
                    "symbolic_pattern": ["🟡", "⚠️", "🛡️"],
                },
                "level_2_moderate": {
                    "approval_authorities": ["system_guardian", "human_overseer"],
                    "response_time": 180,
                    "symbolic_pattern": ["🟠", "⚠️", "🛡️"],
                },
                "level_3_severe": {
                    "approval_authorities": ["human_overseer", "ethics_board"],
                    "response_time": 60,
                    "symbolic_pattern": ["🔴", "🚨", "🛡️"],
                },
            },
            "trigger_conditions": {
                "governance_drift": {
                    "description": "Governance system drift detected",
                    "emergency_level": "level_2_moderate",
                    "symbolic_sequence": ["🛡️", "🌊", "⚠️"],
                },
                "ethics_violation": {
                    "description": "Ethical boundary violation",
                    "emergency_level": "level_3_severe",
                    "symbolic_sequence": ["⚖️", "🚨", "🛑"],
                },
            },
        }

    async def trigger_emergency_simulation(self, condition_name: str = "governance_drift"):
        """Trigger emergency simulation for governance testing"""
        if condition_name not in self.emergency_trigger_conditions:
            print(f"❌ Unknown emergency condition: {condition_name}")
            return

        condition = self.emergency_trigger_conditions[condition_name]
        emergency_level = condition.get("emergency_level", "level_1_minor")

        # Get emergency level configuration
        emergency_levels = self.emergency_manifest.get("emergency_levels", {})
        level_config = emergency_levels.get(emergency_level, {})

        # Activate emergency state with governance validation
        self.emergency_state = EmergencyState(
            active_emergency_level=emergency_level,
            emergency_description=condition.get("description", "Emergency simulation"),
            symbolic_pattern=condition.get("symbolic_sequence", ["🚨", "💥", "🔥"]),
            activated_at=time.time(),
            response_actions=level_config.get("approval_authorities", []),
            escalation_history=[
                {
                    "timestamp": time.time(),
                    "action": "emergency_simulation_triggered",
                    "condition": condition_name,
                    "level": emergency_level,
                    "governance_validated": True,
                }
            ],
            governance_approval=True,
            human_oversight_required="human_overseer" in level_config.get("approval_authorities", []),
        )

        # Log in governance system
        await self._log_governance_action(
            "emergency_simulation_triggered",
            {"condition": condition_name, "level": emergency_level},
        )

        print(f"🚨 Emergency simulation triggered: {condition_name}")
        print(f"   Level: {emergency_level}")
        print(f"   Symbolic: {'→'.join(self.emergency_state.symbolic_pattern)}")

    async def resolve_emergency(self):
        """Resolve active emergency with governance validation"""
        if self.emergency_state.active_emergency_level:
            print(f"✅ Emergency resolved: {self.emergency_state.active_emergency_level}")

            # Log resolution in governance
            await self._log_governance_action(
                "emergency_resolved",
                {"level": self.emergency_state.active_emergency_level},
            )

            self.emergency_state = EmergencyState(
                active_emergency_level=None,
                emergency_description="Emergency resolved",
                symbolic_pattern=["✅", "🌿", "🛡️"],
                activated_at=None,
                response_actions=[],
                escalation_history=[],
                governance_approval=True,
                human_oversight_required=False,
            )

    async def start_monitoring(self):
        """Start the Guardian dashboard monitoring loop"""
        self.running = True

        # Hide cursor and clear screen
        print(Console.CURSOR_HIDE, end="")
        print(Console.clear_screen(), end="")

        try:
            # Run dashboard tasks concurrently
            await asyncio.gather(
                self._update_metrics(),
                self._simulate_threat_detection(),  # Demo mode
                self._render_dashboard(),
                self._handle_input(),
                self._governance_monitor(),
            )
        except KeyboardInterrupt:
            print(f"\n{Console.YELLOW}🛡️ Guardian Dashboard stopped{Console.RESET}")
        finally:
            # Restore cursor
            print(Console.CURSOR_SHOW, end="")
            self.running = False

    async def _update_metrics(self):
        """Update system metrics continuously with governance tracking"""
        while self.running:
            uptime = time.time() - self.start_time

            # Simulate realistic metrics (in production, these would be real)
            self.current_metrics = SystemMetrics(
                entropy_score=0.3 + 0.2 * math.sin(time.time() * 0.1),
                drift_velocity=max(0, 0.1 + 0.1 * math.sin(time.time() * 0.05)),
                consciousness_stability=0.9 + 0.1 * math.cos(time.time() * 0.03),
                guardian_load=len(self.active_threats) * 0.1,
                active_threats=len(self.active_threats),
                resolved_threats=len(self.resolved_threats),
                uptime=uptime,
                memory_usage=50 + 20 * math.sin(time.time() * 0.02),
                cpu_usage=20 + 15 * math.sin(time.time() * 0.04),
                ethics_compliance=0.95 + 0.05 * math.cos(time.time() * 0.02),
                governance_health=0.98 + 0.02 * math.sin(time.time() * 0.01),
            )

            await asyncio.sleep(1.0)

    async def _simulate_threat_detection(self):
        """Simulate threat detection for demo purposes with governance validation"""
        threat_id_counter = 0

        while self.running:
            # Randomly generate threats
            if len(self.active_threats) < 5 and time.time() % 10 < 0.5:  # Throttled generation
                if not hasattr(self, "_last_threat_time") or time.time() - self._last_threat_time > 8:
                    threat_type = self._generate_realistic_threat()
                    threat_id_counter += 1

                    threat = ThreatEvent(
                        id=f"THR-{threat_id_counter:04d}",
                        type=threat_type,
                        severity=self._calculate_threat_severity(threat_type),
                        confidence=0.7 + 0.3 * (time.time() % 1),
                        timestamp=time.time(),
                        source="guardian.sentinel",
                        symbolic_pattern=self._generate_symbolic_pattern(threat_type),
                        metadata=self._generate_threat_metadata(threat_type),
                        governance_validated=True,
                    )

                    self.active_threats.append(threat)
                    self.threat_predictor.add_threat(threat)
                    self._last_threat_time = time.time()

                    # Log threat in governance system
                    await self._log_governance_action(
                        "threat_detected",
                        {
                            "threat_id": threat.id,
                            "type": threat_type,
                            "severity": threat.severity,
                        },
                    )

            # Resolve old threats
            current_time = time.time()
            for threat in list(self.active_threats):
                threat_age = current_time - threat.timestamp

                # Auto-resolve based on type and age
                resolve_probability = min(0.8, threat_age / 30)  # 30 second half-life
                if threat_age > 10 and (time.time() % 1) < resolve_probability * 0.1:
                    threat.resolved = True
                    threat.resolution_time = current_time
                    self.active_threats.remove(threat)
                    self.resolved_threats.append(threat)

                    # Log resolution
                    await self._log_governance_action(
                        "threat_resolved",
                        {"threat_id": threat.id, "resolution_time": threat_age},
                    )

            await asyncio.sleep(2.0)

    async def _governance_monitor(self):
        """Monitor governance-specific metrics and compliance"""
        while self.running:
            # Check governance health
            governance_issues = []

            if self.current_metrics.ethics_compliance < 0.9:
                governance_issues.append("ethics_compliance_low")

            if self.current_metrics.governance_health < 0.95:
                governance_issues.append("governance_system_degraded")

            if len(self.active_threats) > 3:
                governance_issues.append("threat_overload")

            # Generate governance-specific threats if needed
            if governance_issues and not any(t.type.startswith("governance") for t in self.active_threats):
                await self._generate_governance_threat(governance_issues[0])

            await asyncio.sleep(15.0)  # Check every 15 seconds

    async def _generate_governance_threat(self, issue_type: str):
        """Generate governance-specific threat"""
        threat_id = f"GOV-{int(time.time())}"

        threat = ThreatEvent(
            id=threat_id,
            type="governance_drift",
            severity=0.7,
            confidence=0.9,
            timestamp=time.time(),
            source="governance.monitor",
            symbolic_pattern=["🛡️", "⚠️", "🌊"],
            metadata={"issue_type": issue_type, "governance_validated": True},
            governance_validated=True,
        )

        self.active_threats.append(threat)
        self.threat_predictor.add_threat(threat)

        await self._log_governance_action(
            "governance_threat_generated",
            {"threat_id": threat_id, "issue_type": issue_type},
        )

    def _generate_realistic_threat(self) -> str:
        """Generate realistic threat types based on system state and governance"""
        # Weight threats based on current metrics
        weights = {
            "drift_spike": max(0.1, self.current_metrics.drift_velocity * 2),
            "entropy_surge": max(0.1, self.current_metrics.entropy_score * 1.5),
            "pattern_anomaly": 0.3,
            "consciousness_instability": max(0.1, 1.0 - self.current_metrics.consciousness_stability),
            "memory_fragmentation": max(0.1, self.current_metrics.memory_usage / 100),
            "governance_drift": max(0.1, 1.0 - self.current_metrics.governance_health) * 2,
            "ethics_violation": max(0.05, 1.0 - self.current_metrics.ethics_compliance) * 3,
        }

        # Simple weighted selection
        total_weight = sum(weights.values())
        r = (time.time() % 1) * total_weight

        cumulative = 0
        for threat_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return threat_type

        return "pattern_anomaly"  # Fallback

    def _calculate_threat_severity(self, threat_type: str) -> float:
        """Calculate realistic threat severity with governance weighting"""
        base_severity = {
            "drift_spike": 0.4,
            "entropy_surge": 0.6,
            "pattern_anomaly": 0.3,
            "consciousness_instability": 0.7,
            "memory_fragmentation": 0.2,
            "governance_drift": 0.8,
            "ethics_violation": 0.9,
        }.get(threat_type, 0.5)

        # Add randomness based on current system state
        system_stress = (
            self.current_metrics.guardian_load
            + (1.0 - self.current_metrics.consciousness_stability)
            + self.current_metrics.entropy_score
            + (1.0 - self.current_metrics.governance_health)
        ) / 4

        severity = base_severity + system_stress * 0.3 + (time.time() % 1 - 0.5) * 0.2
        return max(0.1, min(1.0, severity))

    def _generate_symbolic_pattern(self, threat_type: str) -> list[str]:
        """Generate symbolic pattern for threat type with governance context"""
        patterns = {
            "drift_spike": ["⚛️", "🌪️", "🛡️"],
            "entropy_surge": ["🔥", "📈", "🛡️"],
            "pattern_anomaly": ["❌", "🔄", "🛡️"],
            "consciousness_instability": ["🧠", "⚡", "🛡️"],
            "memory_fragmentation": ["🧩", "💥", "🛡️"],
            "governance_drift": ["🛡️", "🌊", "⚠️"],
            "ethics_violation": ["⚖️", "🚨", "🛑"],
        }
        return patterns.get(threat_type, ["⚠️", "🔍", "🛡️"])

    def _generate_threat_metadata(self, threat_type: str) -> dict:
        """Generate metadata for threat with governance information"""
        return {
            "detection_method": "guardian.sentinel",
            "affected_systems": ["consciousness", "memory", "identity", "governance"][: (int(time.time()) % 4) + 1],
            "recommended_action": "monitor" if time.time() % 2 < 1 else "intervene",
            "escalation_path": "auto" if time.time() % 3 < 2 else "manual",
            "governance_validated": True,
            "compliance_checked": True,
            "trinity_framework_impact": {
                "identity": threat_type in ["governance_drift", "ethics_violation"],
                "consciousness": threat_type in ["consciousness_instability", "pattern_anomaly"],
                "guardian": True,  # All threats affect guardian
            },
        }

    async def _log_governance_action(self, action: str, metadata: dict):
        """Log action in governance audit system"""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "metadata": metadata,
            "source": "guardian_dashboard",
        }

        self.governance_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.governance_log) > 1000:
            self.governance_log = self.governance_log[-1000:]

    # Rendering methods continue as before, but with governance view additions...

    async def _render_dashboard(self):
        """Render the main dashboard interface with governance view"""
        while self.running:
            self.animation_phase += 0.1
            self.alert_flash_state = int(self.animation_phase * 4) % 2 == 0

            # Render based on current view
            if self.current_view == "overview":
                await self._render_overview()
            elif self.current_view == "threats":
                await self._render_threat_detail()
            elif self.current_view == "predictions":
                await self._render_predictions()
            elif self.current_view == "analysis":
                await self._render_analysis()
            elif self.current_view == "emergency":
                await self._render_emergency_view()
            elif self.current_view == "governance":
                await self._render_governance_view()

            await asyncio.sleep(self.update_interval)

    async def _render_governance_view(self):
        """Render governance-specific monitoring view"""
        print(Console.move_cursor(1, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(2, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}║ 🛡️ LUKHAS GOVERNANCE MONITOR - TRINITY FRAMEWORK STATUS ⚛️🧠🛡️            ║{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(3, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝{Console.RESET}",
            end="",
        )

        # Governance Health Status
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}GOVERNANCE HEALTH{Console.RESET}", end="")

        gov_health_color = (
            Console.GREEN
            if self.current_metrics.governance_health > 0.95
            else (Console.YELLOW if self.current_metrics.governance_health > 0.9 else Console.RED)
        )
        health_bar = "█" * int(self.current_metrics.governance_health * 20)

        print(Console.move_cursor(6, 5), end="")
        print(
            f"System Health: {gov_health_color}{health_bar}{Console.RESET} {self.current_metrics.governance_health:.1%}",
            end="",
        )

        # Ethics Compliance
        ethics_color = (
            Console.GREEN
            if self.current_metrics.ethics_compliance > 0.95
            else (Console.YELLOW if self.current_metrics.ethics_compliance > 0.9 else Console.RED)
        )
        ethics_bar = "█" * int(self.current_metrics.ethics_compliance * 20)

        print(Console.move_cursor(7, 5), end="")
        print(
            f"Ethics Compliance: {ethics_color}{ethics_bar}{Console.RESET} {self.current_metrics.ethics_compliance:.1%}",
            end="",
        )

        # Trinity Framework Status
        print(Console.move_cursor(9, 5), end="")
        print(f"{Console.BOLD}TRINITY FRAMEWORK STATUS{Console.RESET}", end="")

        trinity_status = {
            "⚛️ Identity": self.current_metrics.governance_health,
            "🧠 Consciousness": self.current_metrics.consciousness_stability,
            "🛡️ Guardian": 1.0 - self.current_metrics.guardian_load,
        }

        for i, (component, health) in enumerate(trinity_status.items()):
            color = Console.GREEN if health > 0.8 else Console.YELLOW if health > 0.6 else Console.RED
            bar = "█" * int(health * 15) + "░" * (15 - int(health * 15))

            print(Console.move_cursor(10 + i, 5), end="")
            print(f"{component}: {color}{bar}{Console.RESET} {health:.1%}", end="")

        # Recent Governance Actions
        print(Console.move_cursor(5, 45), end="")
        print(f"{Console.BOLD}RECENT GOVERNANCE ACTIONS{Console.RESET}", end="")

        recent_actions = self.governance_log[-5:] if self.governance_log else []
        for i, action in enumerate(recent_actions):
            age = time.time() - action["timestamp"]
            print(Console.move_cursor(6 + i, 45), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{action['action']} ({age:.0f}s ago)", end="")

        # Governance Metrics
        print(Console.move_cursor(14, 5), end="")
        print(f"{Console.BOLD}GOVERNANCE METRICS{Console.RESET}", end="")

        print(Console.move_cursor(15, 5), end="")
        print(f"Total Actions Logged: {len(self.governance_log)}", end="")

        print(Console.move_cursor(16, 5), end="")
        governance_threats = len(
            [t for t in self.active_threats if t.type.startswith("governance") or t.type.startswith("ethics")]
        )
        print(f"Governance Threats: {governance_threats}", end="")

        print(Console.move_cursor(17, 5), end="")
        avg_response_time = 5.2  # TODO: Calculate from actual data
        print(f"Avg Response Time: {avg_response_time:.1f}s", end="")

    # Continue with the rest of the rendering methods from the original file...
    # (Keeping the same structure but adding governance context where appropriate)

    async def _render_overview(self):
        """Render overview dashboard with governance integration"""
        # Header
        print(Console.move_cursor(1, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(2, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}║ 🛡️ LUKHAS GUARDIAN - GOVERNANCE THREAT DASHBOARD v2.0 ⚛️🧠🛡️            ║{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(3, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝{Console.RESET}",
            end="",
        )

        # System status with governance
        await self._render_system_status()

        # Threat overview
        await self._render_threat_overview()

        # Metrics visualization with governance metrics
        await self._render_metrics_visualization()

        # Navigation with governance view
        await self._render_navigation()

    async def _render_system_status(self):
        """Render system status section with governance information"""
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}SYSTEM STATUS{Console.RESET}", end="")

        # Emergency status (priority display)
        print(Console.move_cursor(6, 5), end="")
        if self.emergency_state.active_emergency_level:
            emergency_color = Console.RED + Console.BOLD
            if self.alert_flash_state:
                emergency_color += Console.BLINK
            emergency_pattern = "→".join(self.emergency_state.symbolic_pattern)
            print(
                f"{emergency_color}🚨 EMERGENCY: {self.emergency_state.active_emergency_level}{Console.RESET}",
                end="",
            )

            print(Console.move_cursor(7, 5), end="")
            print(f"{Console.RED}Pattern: {emergency_pattern}{Console.RESET}", end="")

            print(Console.move_cursor(8, 5), end="")
            age = time.time() - (self.emergency_state.activated_at or time.time())
            print(f"{Console.YELLOW}Duration: {age:.0f}s{Console.RESET}", end="")

            print(Console.move_cursor(9, 5), end="")
            oversight_status = "REQUIRED" if self.emergency_state.human_oversight_required else "OPTIONAL"
            print(
                f"{Console.CYAN}Human Oversight: {oversight_status}{Console.RESET}",
                end="",
            )
        else:
            # Trinity Framework status with governance
            trinity_color = (
                Console.GREEN
                if (
                    self.current_metrics.consciousness_stability > 0.8 and self.current_metrics.governance_health > 0.95
                )
                else Console.YELLOW
            )
            print(f"Trinity Framework: ⚛️🧠🛡️ {trinity_color}ACTIVE{Console.RESET}", end="")

            # Governance health
            gov_color = (
                Console.GREEN
                if self.current_metrics.governance_health > 0.95
                else (Console.YELLOW if self.current_metrics.governance_health > 0.9 else Console.RED)
            )

            print(Console.move_cursor(7, 5), end="")
            print(
                f"Governance Health: {gov_color}{self.current_metrics.governance_health:.1%}{Console.RESET}",
                end="",
            )

            # Ethics compliance
            ethics_color = (
                Console.GREEN
                if self.current_metrics.ethics_compliance > 0.95
                else (Console.YELLOW if self.current_metrics.ethics_compliance > 0.9 else Console.RED)
            )

            print(Console.move_cursor(8, 5), end="")
            print(
                f"Ethics Compliance: {ethics_color}{self.current_metrics.ethics_compliance:.1%}{Console.RESET}",
                end="",
            )

            # Uptime
            uptime_str = f"{int(self.current_metrics.uptime // 3600):02d}:{int((self.current_metrics.uptime % 3600) // 60):02d}:{int(self.current_metrics.uptime % 60):02d}"
            print(Console.move_cursor(9, 5), end="")
            print(f"Uptime: {Console.CYAN}{uptime_str}{Console.RESET}", end="")

    async def _render_threat_overview(self):
        """Render threat overview section with governance categorization"""
        print(Console.move_cursor(5, 45), end="")
        print(
            f"{Console.BOLD}ACTIVE THREATS ({len(self.active_threats)}){Console.RESET}",
            end="",
        )

        if not self.active_threats:
            print(Console.move_cursor(6, 45), end="")
            print(f"{Console.GREEN}✅ No active threats detected{Console.RESET}", end="")
        else:
            # Categorize threats
            governance_threats = [t for t in self.active_threats if t.type in ["governance_drift", "ethics_violation"]]
            system_threats = [t for t in self.active_threats if t.type not in ["governance_drift", "ethics_violation"]]

            displayed_threats = governance_threats[:3] + system_threats[:2]  # Prioritize governance threats

            for i, threat in enumerate(displayed_threats):
                config = self.THREAT_CONFIGS.get(threat.type, {})
                symbol = config.get("symbol", "⚠️")
                color = config.get("color", Console.YELLOW)

                severity_bar = "█" * int(threat.severity * 5)
                age = time.time() - threat.timestamp

                print(Console.move_cursor(6 + i, 45), end="")
                print(Console.CLEAR_LINE, end="")

                # Add governance indicator
                gov_indicator = "🛡️" if threat.type in ["governance_drift", "ethics_violation"] else ""

                print(
                    f"{color}{symbol}{Console.RESET} {gov_indicator}{threat.id} ",
                    end="",
                )
                print(
                    f"{Console.RED if threat.severity > 0.7 else Console.YELLOW}{severity_bar}{Console.RESET} ",
                    end="",
                )
                print(f"{Console.DIM}{age:.0f}s{Console.RESET}", end="")

        # Resolved threats counter
        print(Console.move_cursor(12, 45), end="")
        print(
            f"Resolved: {Console.GREEN}{len(self.resolved_threats)}{Console.RESET}",
            end="",
        )

    async def _render_metrics_visualization(self):
        """Render system metrics visualization with governance metrics"""
        print(Console.move_cursor(14, 5), end="")
        print(f"{Console.BOLD}SYSTEM METRICS{Console.RESET}", end="")

        metrics = [
            ("Entropy", self.current_metrics.entropy_score, Console.YELLOW),
            ("Drift Velocity", self.current_metrics.drift_velocity, Console.RED),
            (
                "Consciousness",
                self.current_metrics.consciousness_stability,
                Console.BLUE,
            ),
            ("Governance", self.current_metrics.governance_health, Console.GREEN),
            ("Ethics", self.current_metrics.ethics_compliance, Console.PURPLE),
        ]

        for i, (name, value, color) in enumerate(metrics):
            bar_length = int(value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            print(Console.move_cursor(15 + i, 5), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{name:12}: {color}{bar}{Console.RESET} {value:.2f}", end="")

        # Predictions preview with governance weighting
        predictions = self.threat_predictor.predict_next_threat()
        if predictions:
            print(Console.move_cursor(14, 45), end="")
            print(f"{Console.BOLD}THREAT PREDICTIONS{Console.RESET}", end="")

            for i, (threat_type, probability) in enumerate(list(predictions.items())[:3]):
                config = self.THREAT_CONFIGS.get(threat_type, {})
                symbol = config.get("symbol", "⚠️")
                color = config.get("color", Console.YELLOW)

                print(Console.move_cursor(15 + i, 45), end="")
                print(Console.CLEAR_LINE, end="")

                # Add governance indicator for governance threats
                gov_indicator = "🛡️" if threat_type in ["governance_drift", "ethics_violation"] else ""

                print(
                    f"{color}{symbol}{Console.RESET} {gov_indicator}{threat_type}: {probability:.1%}",
                    end="",
                )

    async def _render_navigation(self):
        """Render navigation and instructions with governance view"""
        print(Console.move_cursor(20, 5), end="")
        print(Console.CLEAR_LINE, end="")
        print(
            f"{Console.DIM}Views: [1]Overview [2]Threats [3]Predictions [4]Analysis [5]Emergency [6]Governance | [q]Quit{Console.RESET}",
            end="",
        )

        if self.current_view == "governance":
            print(Console.move_cursor(21, 5), end="")
            print(Console.CLEAR_LINE, end="")
            governance_status = f"Health: {self.current_metrics.governance_health:.1%} | Ethics: {self.current_metrics.ethics_compliance:.1%}"
            print(
                f"{Console.DIM}Governance Status: {governance_status} | Actions Logged: {len(self.governance_log)}{Console.RESET}",
                end="",
            )

    async def _handle_input(self):
        """Handle keyboard input for navigation with governance view cycling"""
        # Note: This is a simplified input handler for demo purposes
        # In production, you'd use proper async input handling

        while self.running:
            await asyncio.sleep(0.1)

            # Auto-cycle through views for demo (including governance view)
            cycle_time = int(time.time()) % 30
            if cycle_time < 5:
                self.current_view = "overview"
            elif cycle_time < 10:
                self.current_view = "threats"
            elif cycle_time < 15:
                self.current_view = "predictions"
            elif cycle_time < 20:
                self.current_view = "analysis"
            elif cycle_time < 25:
                self.current_view = "emergency"
            else:
                self.current_view = "governance"

                # Auto-trigger emergency simulation for demo
                if not self.emergency_state.active_emergency_level and cycle_time == 25:
                    await self.trigger_emergency_simulation("governance_drift")
                elif self.emergency_state.active_emergency_level and cycle_time == 29:
                    await self.resolve_emergency()

    # Public API methods for governance integration

    def get_governance_summary(self) -> dict[str, any]:
        """Get governance monitoring summary"""
        governance_threats = [t for t in self.active_threats if t.type in ["governance_drift", "ethics_violation"]]

        return {
            "governance_health": self.current_metrics.governance_health,
            "ethics_compliance": self.current_metrics.ethics_compliance,
            "governance_threats_active": len(governance_threats),
            "emergency_state": {
                "active": self.emergency_state.active_emergency_level is not None,
                "level": self.emergency_state.active_emergency_level,
                "human_oversight_required": self.emergency_state.human_oversight_required,
            },
            "governance_actions_logged": len(self.governance_log),
            "trinity_framework_status": {
                "identity": self.current_metrics.governance_health,
                "consciousness": self.current_metrics.consciousness_stability,
                "guardian": 1.0 - self.current_metrics.guardian_load,
            },
        }


async def main():
    """Main entry point for governance dashboard"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Guardian Governance Dashboard")
    parser.add_argument(
        "--update-interval",
        type=float,
        default=0.5,
        help="Dashboard update interval in seconds",
    )

    args = parser.parse_args()

    dashboard = GuardianDashboard(update_interval=args.update_interval)
    await dashboard.start_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Console.YELLOW}🛡️ Guardian Dashboard stopped by user{Console.RESET}")
    except Exception as e:
        print(f"\n{Console.RED}❌ Dashboard Error: {e}{Console.RESET}")
        sys.exit(1)
