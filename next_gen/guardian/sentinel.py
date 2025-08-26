#!/usr/bin/env python3
"""
Guardian Sentinel - Detects unstable drift and entropy spikes
Monitors system health and triggers interventions when needed
"""

import asyncio
import json
import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import websockets

logger = logging.getLogger(__name__)


@dataclass
class ThreatIndicator:
    """Represents a potential threat or anomaly"""

    indicator_type: str  # drift_spike, entropy_surge, pattern_anomaly
    severity: float  # 0.0 to 1.0
    source: str
    timestamp: datetime
    details: dict
    recommended_action: str

    def to_alert(self) -> dict:
        """Convert to WebSocket alert format"""
        return {
            "type": "guardian_alert",
            "indicator": self.indicator_type,
            "severity": self.severity,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "action": self.recommended_action,
        }


class GuardianSentinel:
    """
    Monitors system health and detects threats to stability
    Triggers interventions based on configurable thresholds
    """

    # Severity thresholds
    SEVERITY_LEVELS = {"low": 0.3, "medium": 0.5, "high": 0.7, "critical": 0.9}

    # Monitoring thresholds
    THRESHOLDS = {
        "drift_rate": 0.1,  # Max drift change per minute
        "entropy_spike": 0.3,  # Max entropy increase
        "pattern_disruption": 0.5,  # Pattern coherence threshold
        "memory_fragmentation": 0.7,  # Memory coherence threshold
        "consciousness_instability": 0.4,  # State change frequency
    }

    def __init__(
        self,
        websocket_url: str = "ws://localhost:8765",
        alert_threshold: float = 0.5,
        monitoring_interval: int = 5,
    ):
        self.websocket_url = websocket_url
        self.alert_threshold = alert_threshold
        self.monitoring_interval = monitoring_interval

        # Monitoring windows
        self.drift_history = deque(maxlen=100)
        self.entropy_history = deque(maxlen=100)
        self.pattern_history = deque(maxlen=50)
        self.consciousness_history = deque(maxlen=50)

        # Threat tracking
        self.active_threats: list[ThreatIndicator] = []
        self.intervention_history: list[dict] = []

        # System state
        self.monitoring_active = False
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None

        logger.info("🛡️ Guardian Sentinel initialized")
        logger.info(f"   Alert threshold: {alert_threshold}")
        logger.info(f"   Monitoring interval: {monitoring_interval}s")

    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.monitoring_active = True

        # Connect to WebSocket for alerts
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info("📡 Connected to WebSocket for alerts")
        except Exception as e:
            logger.warning(f"Could not connect to WebSocket: {e}")
            self.websocket = None

        # Start monitoring tasks
        await asyncio.gather(
            self._monitor_drift(),
            self._monitor_entropy(),
            self._monitor_patterns(),
            self._monitor_consciousness(),
        )

    async def _monitor_drift(self):
        """Monitor drift rate changes"""
        while self.monitoring_active:
            try:
                # Simulate drift reading (in production, read from TrustHelix)
                current_drift = self._read_current_drift()
                self.drift_history.append(
                    {"value": current_drift, "timestamp": datetime.utcnow()}
                )

                # Check for spikes
                if len(self.drift_history) >= 2:
                    recent = [d["value"] for d in list(self.drift_history)[-10:]]
                    drift_rate = max(recent) - min(recent)

                    if drift_rate > self.THRESHOLDS["drift_rate"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="drift_spike",
                                severity=min(drift_rate / 0.5, 1.0),
                                source="drift_monitor",
                                timestamp=datetime.utcnow(),
                                details={
                                    "drift_rate": drift_rate,
                                    "current_drift": current_drift,
                                    "recent_values": recent[-5:],
                                },
                                recommended_action="stabilize_drift",
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in drift monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_entropy(self):
        """Monitor entropy spikes"""
        while self.monitoring_active:
            try:
                # Simulate entropy reading
                current_entropy = self._read_current_entropy()
                self.entropy_history.append(
                    {"value": current_entropy, "timestamp": datetime.utcnow()}
                )

                # Check for surges
                if len(self.entropy_history) >= 2:
                    prev_entropy = self.entropy_history[-2]["value"]
                    entropy_spike = current_entropy - prev_entropy

                    if entropy_spike > self.THRESHOLDS["entropy_spike"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="entropy_surge",
                                severity=min(entropy_spike / 0.5, 1.0),
                                source="entropy_monitor",
                                timestamp=datetime.utcnow(),
                                details={
                                    "entropy_spike": entropy_spike,
                                    "current_entropy": current_entropy,
                                    "previous_entropy": prev_entropy,
                                },
                                recommended_action="reduce_entropy",
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in entropy monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_patterns(self):
        """Monitor pattern disruption"""
        while self.monitoring_active:
            try:
                # Simulate pattern coherence reading
                pattern_coherence = self._read_pattern_coherence()
                self.pattern_history.append(
                    {"coherence": pattern_coherence, "timestamp": datetime.utcnow()}
                )

                # Check for disruption
                if pattern_coherence < self.THRESHOLDS["pattern_disruption"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="pattern_anomaly",
                            severity=(1.0 - pattern_coherence),
                            source="pattern_monitor",
                            timestamp=datetime.utcnow(),
                            details={
                                "pattern_coherence": pattern_coherence,
                                "threshold": self.THRESHOLDS["pattern_disruption"],
                            },
                            recommended_action="reinforce_patterns",
                        )
                    )

                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"Error in pattern monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_consciousness(self):
        """Monitor consciousness state stability"""
        while self.monitoring_active:
            try:
                # Simulate consciousness state reading
                current_state = self._read_consciousness_state()
                self.consciousness_history.append(
                    {"state": current_state, "timestamp": datetime.utcnow()}
                )

                # Check for instability (too many state changes)
                if len(self.consciousness_history) >= 10:
                    recent_states = [
                        h["state"] for h in list(self.consciousness_history)[-10:]
                    ]
                    unique_states = len(set(recent_states))
                    instability = unique_states / 10.0

                    if instability > self.THRESHOLDS["consciousness_instability"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="consciousness_instability",
                                severity=instability,
                                source="consciousness_monitor",
                                timestamp=datetime.utcnow(),
                                details={
                                    "unique_states": unique_states,
                                    "recent_states": recent_states[-5:],
                                    "instability_score": instability,
                                },
                                recommended_action="stabilize_consciousness",
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in consciousness monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _raise_threat(self, threat: ThreatIndicator):
        """Raise a threat alert"""
        # Check severity threshold
        if threat.severity < self.alert_threshold:
            logger.info(f"🟡 Low severity threat detected: {threat.indicator_type}")
            return

        # Add to active threats
        self.active_threats.append(threat)

        # Log threat
        logger.warning(f"🚨 THREAT DETECTED: {threat.indicator_type}")
        logger.warning(f"   Severity: {threat.severity:.2f}")
        logger.warning(f"   Action: {threat.recommended_action}")

        # Send WebSocket alert if connected
        if self.websocket and not self.websocket.closed:
            try:
                await self.websocket.send(json.dumps(threat.to_alert()))
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")

        # Trigger intervention if critical
        if threat.severity >= self.SEVERITY_LEVELS["critical"]:
            await self._trigger_intervention(threat)

    async def _trigger_intervention(self, threat: ThreatIndicator):
        """Trigger an intervention based on threat type"""
        intervention = {
            "timestamp": datetime.utcnow().isoformat(),
            "threat": threat.indicator_type,
            "severity": threat.severity,
            "action_taken": threat.recommended_action,
            "details": {},
        }

        # Execute intervention based on type
        if threat.indicator_type == "drift_spike":
            intervention["details"] = await self._intervene_drift_spike()
        elif threat.indicator_type == "entropy_surge":
            intervention["details"] = await self._intervene_entropy_surge()
        elif threat.indicator_type == "pattern_anomaly":
            intervention["details"] = await self._intervene_pattern_anomaly()
        elif threat.indicator_type == "consciousness_instability":
            intervention["details"] = await self._intervene_consciousness_instability()

        self.intervention_history.append(intervention)

        logger.info(f"⚡ Intervention executed: {threat.recommended_action}")

    async def _intervene_drift_spike(self) -> dict:
        """Intervene for drift spike"""
        return {
            "action": "drift_dampening",
            "parameters": {"dampening_factor": 0.5, "duration_seconds": 60},
            "expected_result": "Drift rate reduction",
        }

    async def _intervene_entropy_surge(self) -> dict:
        """Intervene for entropy surge"""
        return {
            "action": "entropy_cooling",
            "parameters": {"cooling_rate": 0.1, "target_entropy": 0.3},
            "expected_result": "Entropy stabilization",
        }

    async def _intervene_pattern_anomaly(self) -> dict:
        """Intervene for pattern anomaly"""
        return {
            "action": "pattern_reinforcement",
            "parameters": {
                "reinforcement_glyphs": ["🌿", "🔐", "💎"],
                "repetitions": 5,
            },
            "expected_result": "Pattern coherence improvement",
        }

    async def _intervene_consciousness_instability(self) -> dict:
        """Intervene for consciousness instability"""
        return {
            "action": "consciousness_anchoring",
            "parameters": {"anchor_state": "meditative", "anchor_duration": 120},
            "expected_result": "State stabilization",
        }

    # Simulation methods (replace with actual system reads in production)
    def _read_current_drift(self) -> float:
        """Simulate drift reading"""
        import random

        base = 0.3
        if random.random() > 0.9:  # 10% chance of spike
            return base + random.uniform(0.2, 0.5)
        return base + random.uniform(-0.1, 0.1)

    def _read_current_entropy(self) -> float:
        """Simulate entropy reading"""
        import random

        base = 0.4
        if random.random() > 0.95:  # 5% chance of surge
            return base + random.uniform(0.3, 0.6)
        return base + random.uniform(-0.1, 0.1)

    def _read_pattern_coherence(self) -> float:
        """Simulate pattern coherence reading"""
        import random

        return random.uniform(0.3, 0.9)

    def _read_consciousness_state(self) -> str:
        """Simulate consciousness state reading"""
        import random

        states = [
            "focused",
            "creative",
            "analytical",
            "meditative",
            "dreaming",
            "flow_state",
            "lucid",
            "turbulent",
        ]
        return random.choice(states)

    def get_threat_report(self) -> dict:
        """Generate threat analysis report"""
        active_count = len(
            [
                t
                for t in self.active_threats
                if (datetime.utcnow() - t.timestamp).seconds < 300
            ]
        )

        severity_dist = {}
        for level, threshold in self.SEVERITY_LEVELS.items():
            count = len([t for t in self.active_threats if t.severity >= threshold])
            severity_dist[level] = count

        return {
            "total_threats": len(self.active_threats),
            "active_threats": active_count,
            "severity_distribution": severity_dist,
            "intervention_count": len(self.intervention_history),
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "recent_threats": [t.to_alert() for t in self.active_threats[-5:]],
        }

    async def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.monitoring_active = False
        if self.websocket:
            await self.websocket.close()
        logger.info("🛑 Guardian Sentinel monitoring stopped")


# Example usage
async def demo_sentinel():
    """Demonstrate Guardian Sentinel"""
    sentinel = GuardianSentinel(alert_threshold=0.5, monitoring_interval=2)

    print("🛡️ Guardian Sentinel Demo")
    print("=" * 60)
    print("Starting monitoring for 20 seconds...")

    # Run monitoring for demo
    try:
        monitoring_task = asyncio.create_task(sentinel.start_monitoring())

        # Let it run for 20 seconds
        await asyncio.sleep(20)

        # Get report
        report = sentinel.get_threat_report()
        print("\n📊 Threat Report:")
        print(f"   Total threats: {report['total_threats']}")
        print(f"   Active threats: {report['active_threats']}")
        print(f"   Interventions: {report['intervention_count']}")

        print("\n🔍 Recent Threats:")
        for threat in report["recent_threats"]:
            print(f"   - {threat['indicator']} (severity: {threat['severity']:.2f})")

    finally:
        await sentinel.stop_monitoring()
        monitoring_task.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(demo_sentinel())
