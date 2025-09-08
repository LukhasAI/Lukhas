#!/usr/bin/env python3
"""
Real-Time Symbolic Threat Dashboard - Advanced Guardian monitoring interface
Provides comprehensive threat visualization with symbolic analysis and predictive modeling
"""
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


# Console control for visualization
class Console:
    """Enhanced console control for threat dashboard"""

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
    def move_cursor(row: int, col: int) -> str:
        return f"\033[{row};{col}H"

    @staticmethod
    def clear_screen():
        return Console.CLEAR_SCREEN + Console.CURSOR_HOME


@dataclass
class ThreatEvent:
    """Represents a threat detection event"""

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


@dataclass
class SystemMetrics:
    """Current system metrics snapshot"""

    entropy_score: float
    drift_velocity: float
    consciousness_stability: float
    guardian_load: float
    active_threats: int
    resolved_threats: int
    uptime: float
    memory_usage: float
    cpu_usage: float


@dataclass
class EmergencyState:
    """Current emergency state information"""

    active_emergency_level: Optional[str]
    emergency_description: str
    symbolic_pattern: list[str]
    activated_at: Optional[float]
    response_actions: list[str]
    escalation_history: list[dict]


class ThreatPredictor:
    """Predictive threat analysis using symbolic patterns"""

    def __init__(self, history_window: int = 100):
        self.history_window = history_window
        self.threat_history: deque = deque(maxlen=history_window)
        self.pattern_frequencies: dict[str, int] = defaultdict(int)
        self.sequence_patterns: dict[str, list[str]] = defaultdict(list)

    def add_threat(self, threat: ThreatEvent):
        """Add threat to prediction model"""
        self.threat_history.append(threat)

        # Track pattern frequencies
        pattern_key = "→".join(threat.symbolic_pattern)
        self.pattern_frequencies[pattern_key] += 1

        # Track sequence patterns
        if len(self.threat_history) >= 2:
            prev_threat = list(self.threat_history)[-2]
            sequence_key = f"{prev_threat.type}→{threat.type}"
            self.sequence_patterns[sequence_key].append(pattern_key)

    def predict_next_threat(self) -> dict[str, float]:
        """Predict probability of next threat types"""
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

        # Analyze severity trends
        recent_severities = [t.severity for t in recent_threats]
        if len(recent_severities) >= 2:
            trend = recent_severities[-1] - recent_severities[-2]
            if trend > 0.1:  # Escalating
                prediction_scores["pattern_anomaly"] += 0.4
                prediction_scores["entropy_surge"] += 0.3

        # Normalize scores
        if prediction_scores:
            max_score = max(prediction_scores.values())
            if max_score > 0:
                prediction_scores = {k: v / max_score for k, v in prediction_scores.items()}

        return dict(prediction_scores)

    def get_pattern_analysis(self) -> dict[str, any]:
        """Get detailed pattern analysis"""
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

        return {
            "total_threats": len(threats),
            "recent_activity": recent_activity,
            "avg_severity_change": avg_severity_change,
            "top_patterns": top_patterns,
            "prediction_confidence": min(1.0, len(threats) / 50),  # Higher confidence with more data
        }


class GuardianDashboard:
    """
    Real-time Guardian threat monitoring dashboard
    Provides comprehensive threat visualization and analysis
    """

    # Threat type configurations
    THREAT_CONFIGS = {
        "drift_spike": {
            "symbol": "🌪️",
            "color": Console.YELLOW,
            "priority": 2,
            "intervention_threshold": 0.6,
            "description": "Behavioral drift spike detected",
        },
        "entropy_surge": {
            "symbol": "🔥",
            "color": Console.RED,
            "priority": 3,
            "intervention_threshold": 0.7,
            "description": "Entropy levels elevated",
        },
        "pattern_anomaly": {
            "symbol": "❌",
            "color": Console.PURPLE,
            "priority": 2,
            "intervention_threshold": 0.5,
            "description": "Anomalous pattern detected",
        },
        "consciousness_instability": {
            "symbol": "⚡",
            "color": Console.CYAN,
            "priority": 4,
            "intervention_threshold": 0.8,
            "description": "Consciousness state unstable",
        },
        "memory_fragmentation": {
            "symbol": "🧩",
            "color": Console.BLUE,
            "priority": 1,
            "intervention_threshold": 0.4,
            "description": "Memory integrity issues",
        },
    }

    def __init__(
        self,
        update_interval: float = 0.5,
        emergency_manifest_file: str = "next_gen/guardian/emergency_manifest.yaml",
    ):
        self.update_interval = update_interval
        self.emergency_manifest_file = Path(emergency_manifest_file)
        self.running = False
        self.start_time = time.time()

        # Threat tracking
        self.active_threats: list[ThreatEvent] = []
        self.resolved_threats: list[ThreatEvent] = []
        self.threat_predictor = ThreatPredictor()

        # System metrics
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
        )

        # Emergency state
        self.emergency_state = EmergencyState(
            active_emergency_level=None,
            emergency_description="No active emergency",
            symbolic_pattern=["🛡️", "🟢", "✅"],
            activated_at=None,
            response_actions=[],
            escalation_history=[],
        )

        # Emergency manifest data
        self.emergency_manifest: dict = {}
        self.emergency_trigger_conditions: dict = {}
        self.emergency_response_actions: dict = {}

        # Dashboard state
        self.current_view = "overview"  # overview, threats, predictions, analysis, emergency
        self.selected_threat_index = 0
        self.animation_phase = 0.0
        self.alert_flash_state = False
        self.emergency_simulation_enabled = False

        # Data logging
        self.dashboard_log: list[dict] = []

        # Load emergency manifest
        self._load_emergency_manifest()

        print(f"{Console.GREEN}🛡️ Guardian Dashboard initialized{Console.RESET}")

    def _load_emergency_manifest(self):
        """Load emergency manifest configuration"""
        try:
            if self.emergency_manifest_file.exists():
                with open(self.emergency_manifest_file) as f:
                    self.emergency_manifest = yaml.safe_load(f)

                # Extract trigger conditions and response actions
                self.emergency_trigger_conditions = self.emergency_manifest.get("trigger_conditions", {})
                self.emergency_response_actions = self.emergency_manifest.get("response_actions", {})

                print(f"📋 Emergency manifest loaded: {len(self.emergency_trigger_conditions)} trigger conditions")
            else:
                print(f"⚠️ Emergency manifest not found: {self.emergency_manifest_file}")

        except Exception as e:
            print(f"❌ Failed to load emergency manifest: {e}")

    async def trigger_emergency_simulation(self, condition_name: str = "entropy_explosion"):
        """Trigger emergency simulation for testing"""
        if condition_name not in self.emergency_trigger_conditions:
            print(f"❌ Unknown emergency condition: {condition_name}")
            return

        condition = self.emergency_trigger_conditions[condition_name]
        emergency_level = condition.get("emergency_level", "level_1_minor")

        # Get emergency level configuration
        emergency_levels = self.emergency_manifest.get("emergency_levels", {})
        level_config = emergency_levels.get(emergency_level, {})

        # Activate emergency state
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
                }
            ],
        )

        print(f"🚨 Emergency simulation triggered: {condition_name}")
        print(f"   Level: {emergency_level}")
        print(f"   Symbolic: {'→'.join(self.emergency_state.symbolic_pattern)}")

    async def resolve_emergency(self):
        """Resolve active emergency"""
        if self.emergency_state.active_emergency_level:
            print(f"✅ Emergency resolved: {self.emergency_state.active_emergency_level}")

            self.emergency_state = EmergencyState(
                active_emergency_level=None,
                emergency_description="Emergency resolved",
                symbolic_pattern=["✅", "🌿", "🛡️"],
                activated_at=None,
                response_actions=[],
                escalation_history=[],
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
            )
        except KeyboardInterrupt:
            print(f"\n{Console.YELLOW}🛡️ Guardian Dashboard stopped{Console.RESET}")
        finally:
            # Restore cursor
            print(Console.CURSOR_SHOW, end="")
            self.running = False

    async def _update_metrics(self):
        """Update system metrics continuously"""
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
            )

            await asyncio.sleep(1.0)

    async def _simulate_threat_detection(self):
        """Simulate threat detection for demo purposes"""
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
                    )

                    self.active_threats.append(threat)
                    self.threat_predictor.add_threat(threat)
                    self._last_threat_time = time.time()

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

            await asyncio.sleep(2.0)

    def _generate_realistic_threat(self) -> str:
        """Generate realistic threat types based on system state"""
        # Weight threats based on current metrics
        weights = {
            "drift_spike": max(0.1, self.current_metrics.drift_velocity * 2),
            "entropy_surge": max(0.1, self.current_metrics.entropy_score * 1.5),
            "pattern_anomaly": 0.3,
            "consciousness_instability": max(0.1, 1.0 - self.current_metrics.consciousness_stability),
            "memory_fragmentation": max(0.1, self.current_metrics.memory_usage / 100),
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
        """Calculate realistic threat severity"""
        base_severity = {
            "drift_spike": 0.4,
            "entropy_surge": 0.6,
            "pattern_anomaly": 0.3,
            "consciousness_instability": 0.7,
            "memory_fragmentation": 0.2,
        }.get(threat_type, 0.5)

        # Add randomness based on current system state
        system_stress = (
            self.current_metrics.guardian_load
            + (1.0 - self.current_metrics.consciousness_stability)
            + self.current_metrics.entropy_score
        ) / 3

        severity = base_severity + system_stress * 0.3 + (time.time() % 1 - 0.5) * 0.2
        return max(0.1, min(1.0, severity))

    def _generate_symbolic_pattern(self, threat_type: str) -> list[str]:
        """Generate symbolic pattern for threat type"""
        patterns = {
            "drift_spike": ["🌪️", "🌀", "🌿"],
            "entropy_surge": ["🔥", "💨", "❄️"],
            "pattern_anomaly": ["❌", "🔄", "✅"],
            "consciousness_instability": ["⚓", "🧘", "🔒"],
            "memory_fragmentation": ["🧩", "🔧", "🏛️"],
        }
        return patterns.get(threat_type, ["⚠️", "🔍", "✅"])

    def _generate_threat_metadata(self, threat_type: str) -> dict:
        """Generate metadata for threat"""
        return {
            "detection_method": "guardian.sentinel",
            "affected_systems": ["consciousness", "memory", "identity"][: (int(time.time()) % 3) + 1],
            "recommended_action": "monitor" if time.time() % 2 < 1 else "intervene",
            "escalation_path": "auto" if time.time() % 3 < 2 else "manual",
        }

    async def _render_dashboard(self):
        """Render the main dashboard interface"""
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

            await asyncio.sleep(self.update_interval)

    async def _render_overview(self):
        """Render overview dashboard"""
        # Header
        print(Console.move_cursor(1, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╔═══════════════════════════════════════════════════════════════════════════════╗{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(2, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}║ 🛡️ LUKHAS GUARDIAN - REAL-TIME THREAT DASHBOARD v1.0                      ║{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(3, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╚═══════════════════════════════════════════════════════════════════════════════╝{Console.RESET}",
            end="",
        )

        # System status
        await self._render_system_status()

        # Threat overview
        await self._render_threat_overview()

        # Metrics visualization
        await self._render_metrics_visualization()

        # Navigation
        await self._render_navigation()

    async def _render_system_status(self):
        """Render system status section"""
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
        else:
            # Trinity Framework status
            trinity_color = Console.GREEN if self.current_metrics.consciousness_stability > 0.8 else Console.YELLOW
            print(f"Trinity Framework: ⚛️🧠🛡️ {trinity_color}ACTIVE{Console.RESET}", end="")

            # Guardian load
            load_color = (
                Console.GREEN
                if self.current_metrics.guardian_load < 0.3
                else (Console.YELLOW if self.current_metrics.guardian_load < 0.7 else Console.RED)
            )
            load_bar = "█" * int(self.current_metrics.guardian_load * 10) + "░" * (
                10 - int(self.current_metrics.guardian_load * 10)
            )

            print(Console.move_cursor(7, 5), end="")
            print(
                f"Guardian Load: {load_color}{load_bar}{Console.RESET} ({self.current_metrics.guardian_load:.1%})",
                end="",
            )

            # Uptime
            uptime_str = f"{int(self.current_metrics.uptime // 3600):02d}:{int((self.current_metrics.uptime % 3600) // 60):02d}:{int(self.current_metrics.uptime % 60):02d}"
            print(Console.move_cursor(8, 5), end="")
            print(f"Uptime: {Console.CYAN}{uptime_str}{Console.RESET}", end="")

    async def _render_threat_overview(self):
        """Render threat overview section"""
        print(Console.move_cursor(5, 45), end="")
        print(
            f"{Console.BOLD}ACTIVE THREATS ({len(self.active_threats)}){Console.RESET}",
            end="",
        )

        if not self.active_threats:
            print(Console.move_cursor(6, 45), end="")
            print(f"{Console.GREEN}✅ No active threats detected{Console.RESET}", end="")
        else:
            for i, threat in enumerate(self.active_threats[:5]):  # Show top 5
                config = self.THREAT_CONFIGS.get(threat.type, {})
                symbol = config.get("symbol", "⚠️")
                color = config.get("color", Console.YELLOW)

                severity_bar = "█" * int(threat.severity * 5)
                age = time.time() - threat.timestamp

                print(Console.move_cursor(6 + i, 45), end="")
                print(Console.CLEAR_LINE, end="")
                print(f"{color}{symbol}{Console.RESET} {threat.id} ", end="")
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
        """Render system metrics visualization"""
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
            ("Memory", self.current_metrics.memory_usage / 100, Console.PURPLE),
        ]

        for i, (name, value, color) in enumerate(metrics):
            bar_length = int(value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)

            print(Console.move_cursor(15 + i, 5), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{name:12}: {color}{bar}{Console.RESET} {value:.2f}", end="")

        # Predictions preview
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
                print(
                    f"{color}{symbol}{Console.RESET} {threat_type}: {probability:.1%}",
                    end="",
                )

    async def _render_threat_detail(self):
        """Render detailed threat view"""
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}DETAILED THREAT ANALYSIS{Console.RESET}", end="")

        if not self.active_threats:
            print(Console.move_cursor(7, 5), end="")
            print(f"{Console.GREEN}No active threats to analyze{Console.RESET}", end="")
            return

        # Show selected threat details
        if self.selected_threat_index < len(self.active_threats):
            threat = self.active_threats[self.selected_threat_index]
            config = self.THREAT_CONFIGS.get(threat.type, {})

            print(Console.move_cursor(7, 5), end="")
            print(f"Threat ID: {Console.CYAN}{threat.id}{Console.RESET}", end="")

            print(Console.move_cursor(8, 5), end="")
            print(
                f"Type: {config.get('color', Console.WHITE)}{config.get('symbol', '⚠️')} {threat.type}{Console.RESET}",
                end="",
            )

            print(Console.move_cursor(9, 5), end="")
            severity_color = (
                Console.RED if threat.severity > 0.7 else Console.YELLOW if threat.severity > 0.4 else Console.GREEN
            )
            print(
                f"Severity: {severity_color}{threat.severity:.2f}{Console.RESET} ({threat.confidence:.1%} confidence)",
                end="",
            )

            print(Console.move_cursor(10, 5), end="")
            age = time.time() - threat.timestamp
            print(f"Age: {age:.0f}s | Source: {threat.source}", end="")

            print(Console.move_cursor(11, 5), end="")
            pattern_str = "→".join(threat.symbolic_pattern)
            print(f"Pattern: {pattern_str}", end="")

            print(Console.move_cursor(12, 5), end="")
            print(
                f"Description: {config.get('description', 'Unknown threat type')}",
                end="",
            )

            # Metadata
            print(Console.move_cursor(14, 5), end="")
            print(f"{Console.BOLD}METADATA{Console.RESET}", end="")

            for i, (key, value) in enumerate(threat.metadata.items()):
                print(Console.move_cursor(15 + i, 5), end="")
                print(Console.CLEAR_LINE, end="")
                print(f"{key}: {value}", end="")

    async def _render_predictions(self):
        """Render predictions view"""
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}THREAT PREDICTION ANALYSIS{Console.RESET}", end="")

        predictions = self.threat_predictor.predict_next_threat()
        analysis = self.threat_predictor.get_pattern_analysis()

        # Prediction results
        print(Console.move_cursor(7, 5), end="")
        print(
            f"Prediction Confidence: {analysis.get('prediction_confidence', 0):.1%}",
            end="",
        )

        print(Console.move_cursor(8, 5), end="")
        print(
            f"Recent Activity: {analysis.get('recent_activity', 0)} threats (5min)",
            end="",
        )

        if predictions:
            print(Console.move_cursor(10, 5), end="")
            print(f"{Console.BOLD}PREDICTED THREATS{Console.RESET}", end="")

            for i, (threat_type, probability) in enumerate(predictions.items()):
                config = self.THREAT_CONFIGS.get(threat_type, {})
                symbol = config.get("symbol", "⚠️")
                color = config.get("color", Console.YELLOW)

                prob_bar = "█" * int(probability * 10)

                print(Console.move_cursor(11 + i, 5), end="")
                print(Console.CLEAR_LINE, end="")
                print(
                    f"{color}{symbol}{Console.RESET} {threat_type:20} {prob_bar} {probability:.1%}",
                    end="",
                )

        # Pattern analysis
        if analysis.get("top_patterns"):
            print(Console.move_cursor(10, 45), end="")
            print(f"{Console.BOLD}TOP PATTERNS{Console.RESET}", end="")

            for i, (pattern, count) in enumerate(analysis["top_patterns"][:5]):
                print(Console.move_cursor(11 + i, 45), end="")
                print(Console.CLEAR_LINE, end="")
                print(f"{pattern} ({count}x)", end="")

    async def _render_analysis(self):
        """Render system analysis view"""
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}SYSTEM ANALYSIS{Console.RESET}", end="")

        analysis = self.threat_predictor.get_pattern_analysis()

        # System health assessment
        health_score = (
            self.current_metrics.consciousness_stability
            + (1.0 - self.current_metrics.entropy_score)
            + (1.0 - self.current_metrics.guardian_load)
        ) / 3

        health_color = Console.GREEN if health_score > 0.8 else Console.YELLOW if health_score > 0.6 else Console.RED
        health_bar = "█" * int(health_score * 20)

        print(Console.move_cursor(7, 5), end="")
        print(
            f"System Health: {health_color}{health_bar}{Console.RESET} {health_score:.1%}",
            end="",
        )

        # Threat statistics
        print(Console.move_cursor(9, 5), end="")
        print(f"Total Threats Detected: {analysis.get('total_threats', 0)}", end="")

        print(Console.move_cursor(10, 5), end="")
        print(f"Recent Activity Level: {analysis.get('recent_activity', 0)}", end="")

        print(Console.move_cursor(11, 5), end="")
        severity_trend = analysis.get("avg_severity_change", 0)
        trend_color = (
            Console.RED if severity_trend > 0.1 else Console.GREEN if severity_trend < -0.1 else Console.YELLOW
        )
        trend_arrow = "↗️" if severity_trend > 0.05 else "↘️" if severity_trend < -0.05 else "→"
        print(
            f"Severity Trend: {trend_color}{trend_arrow} {severity_trend:+.3f}{Console.RESET}",
            end="",
        )

        # Guardian effectiveness
        if self.resolved_threats:
            avg_resolution_time = statistics.mean(
                [t.resolution_time - t.timestamp for t in self.resolved_threats if t.resolution_time]
            )

            print(Console.move_cursor(13, 5), end="")
            print(f"Avg Resolution Time: {avg_resolution_time:.1f}s", end="")

    async def _render_emergency_view(self):
        """Render emergency management view"""
        print(Console.move_cursor(5, 5), end="")
        print(f"{Console.BOLD}EMERGENCY MANAGEMENT{Console.RESET}", end="")

        # Current emergency status
        print(Console.move_cursor(7, 5), end="")
        if self.emergency_state.active_emergency_level:
            level_color = Console.RED + Console.BOLD
            print(
                f"Active Emergency: {level_color}{self.emergency_state.active_emergency_level}{Console.RESET}",
                end="",
            )

            print(Console.move_cursor(8, 5), end="")
            print(f"Description: {self.emergency_state.emergency_description}", end="")

            print(Console.move_cursor(9, 5), end="")
            pattern_str = "→".join(self.emergency_state.symbolic_pattern)
            print(
                f"Symbolic Pattern: {Console.YELLOW}{pattern_str}{Console.RESET}",
                end="",
            )

            if self.emergency_state.activated_at:
                duration = time.time() - self.emergency_state.activated_at
                print(Console.move_cursor(10, 5), end="")
                print(f"Duration: {duration:.0f}s", end="")

            # Response actions
            print(Console.move_cursor(11, 5), end="")
            print(
                f"Response Actions: {', '.join(self.emergency_state.response_actions)}",
                end="",
            )

            # Resolution option
            print(Console.move_cursor(13, 5), end="")
            print(f"{Console.GREEN}Press 'r' to resolve emergency{Console.RESET}", end="")
        else:
            print(f"Status: {Console.GREEN}No active emergency{Console.RESET}", end="")

            # Emergency simulation options
            print(Console.move_cursor(9, 5), end="")
            print(f"{Console.BOLD}Available Emergency Simulations:{Console.RESET}", end="")

            available_conditions = list(self.emergency_trigger_conditions.keys())[:5]
            for i, condition in enumerate(available_conditions):
                condition_info = self.emergency_trigger_conditions[condition]
                level = condition_info.get("emergency_level", "unknown")

                print(Console.move_cursor(10 + i, 7), end="")
                print(Console.CLEAR_LINE, end="")
                symbolic = "→".join(condition_info.get("symbolic_sequence", ["❓"]))
                print(f"{i + 1}. {condition} ({level}) {symbolic}", end="")

            print(Console.move_cursor(16, 5), end="")
            print(
                f"{Console.YELLOW}Press '1-5' to simulate emergency, 's' to toggle simulation mode{Console.RESET}",
                end="",
            )

        # Emergency manifest info
        print(Console.move_cursor(5, 45), end="")
        print(f"{Console.BOLD}EMERGENCY MANIFEST{Console.RESET}", end="")

        manifest_levels = len(self.emergency_manifest.get("emergency_levels", {}))
        trigger_conditions = len(self.emergency_trigger_conditions)
        response_actions = len(self.emergency_response_actions)

        print(Console.move_cursor(6, 45), end="")
        print(f"Emergency Levels: {manifest_levels}", end="")

        print(Console.move_cursor(7, 45), end="")
        print(f"Trigger Conditions: {trigger_conditions}", end="")

        print(Console.move_cursor(8, 45), end="")
        print(f"Response Actions: {response_actions}", end="")

        # Recent escalation history
        if self.emergency_state.escalation_history:
            print(Console.move_cursor(10, 45), end="")
            print(f"{Console.BOLD}RECENT ESCALATIONS{Console.RESET}", end="")

            for i, entry in enumerate(self.emergency_state.escalation_history[-3:]):
                print(Console.move_cursor(11 + i, 45), end="")
                print(Console.CLEAR_LINE, end="")
                age = time.time() - entry.get("timestamp", time.time())
                action = entry.get("action", "unknown")
                print(f"{action} ({age:.0f}s ago)", end="")

    async def _render_navigation(self):
        """Render navigation and instructions"""
        print(Console.move_cursor(20, 5), end="")
        print(Console.CLEAR_LINE, end="")
        print(
            f"{Console.DIM}Views: [1]Overview [2]Threats [3]Predictions [4]Analysis [5]Emergency | [q]Quit{Console.RESET}",
            end="",
        )

        if self.current_view == "threats" and self.active_threats:
            print(Console.move_cursor(21, 5), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.DIM}Threat Navigation: [↑/↓] or [j/k] | Selected: {self.selected_threat_index + 1}/{len(self.active_threats)}{Console.RESET}",
                end="",
            )
        elif self.current_view == "emergency":
            print(Console.move_cursor(21, 5), end="")
            print(Console.CLEAR_LINE, end="")
            emergency_status = "ACTIVE" if self.emergency_state.active_emergency_level else "Ready"
            status_color = Console.RED if self.emergency_state.active_emergency_level else Console.GREEN
            print(
                f"{Console.DIM}Emergency Status: {status_color}{emergency_status}{Console.RESET} | Simulation: {'Enabled' if self.emergency_simulation_enabled else 'Disabled'}",
                end="",
            )

    async def _handle_input(self):
        """Handle keyboard input for navigation"""
        # Note: This is a simplified input handler for demo purposes
        # In production, you'd use proper async input handling

        while self.running:
            await asyncio.sleep(0.1)

            # Auto-cycle through views for demo
            cycle_time = int(time.time()) % 25
            if cycle_time < 5:
                self.current_view = "overview"
            elif cycle_time < 10:
                self.current_view = "threats"
            elif cycle_time < 15:
                self.current_view = "predictions"
            elif cycle_time < 20:
                self.current_view = "analysis"
            else:
                self.current_view = "emergency"

                # Auto-trigger emergency simulation for demo
                if not self.emergency_state.active_emergency_level and cycle_time == 20:
                    await self.trigger_emergency_simulation("entropy_explosion")
                elif self.emergency_state.active_emergency_level and cycle_time == 24:
                    await self.resolve_emergency()


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Guardian Real-Time Threat Dashboard")
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
