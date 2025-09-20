#!/usr/bin/env python3
"""
Guardian Sentinel - Enhanced system health monitoring and threat detection

Monitors system stability, detects threats, and triggers interventions with
full governance integration and Constellation Framework (⚛️🧠🛡️) awareness.
"""
import streamlit as st
from datetime import timezone

import asyncio
import json
import logging
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import websockets

from ..common import GlyphIntegrationMixin

logger = logging.getLogger(__name__)


@dataclass
class ThreatIndicator:
    """Enhanced threat indicator with governance and Constellation Framework context"""

    indicator_type: str  # drift_spike, entropy_surge, pattern_anomaly, governance_drift, trinity_desync
    severity: float  # 0.0 to 1.0
    source: str
    timestamp: datetime
    details: dict
    recommended_action: str
    governance_escalation: bool = False
    trinity_impact: dict[str, float] = None
    symbolic_signature: list[str] = None

    def __post_init__(self):
        if self.trinity_impact is None:
            self.trinity_impact = {
                "identity": 0.0,
                "consciousness": 0.0,
                "guardian": 0.0,
            }
        if self.symbolic_signature is None:
            self.symbolic_signature = ["⚠️", "🔍", "🛡️"]

    def to_alert(self) -> dict:
        """Convert to enhanced WebSocket alert format"""
        return {
            "type": "guardian_alert",
            "indicator": self.indicator_type,
            "severity": self.severity,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "action": self.recommended_action,
            "governance_escalation": self.governance_escalation,
            "trinity_impact": self.trinity_impact,
            "symbolic_signature": self.symbolic_signature,
        }


class GuardianSentinel(GlyphIntegrationMixin):
    """
    Enhanced Guardian Sentinel with governance integration and Constellation Framework monitoring

    Monitors system health, detects threats to stability, and triggers interventions
    with comprehensive governance oversight and Constellation Framework awareness.
    """

    # Enhanced severity thresholds with governance considerations
    SEVERITY_LEVELS = {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.9,
        "governance_critical": 0.85,
        "trinity_critical": 0.95,
    }

    # Enhanced monitoring thresholds with Constellation Framework awareness
    THRESHOLDS = {
        "drift_rate": 0.1,  # Max drift change per minute
        "entropy_spike": 0.3,  # Max entropy increase
        "pattern_disruption": 0.5,  # Pattern coherence threshold
        "memory_fragmentation": 0.7,  # Memory coherence threshold
        "consciousness_instability": 0.4,  # State change frequency
        "governance_drift": 0.2,  # Governance system health threshold
        "trinity_desync": 0.3,  # Constellation Framework synchronization threshold
        "identity_compromise": 0.25,  # Identity system integrity threshold
        "guardian_malfunction": 0.15,  # Guardian system effectiveness threshold
    }

    # Enhanced symbolic patterns for threats
    THREAT_SYMBOLS = {
        "drift_spike": ["🌪️", "📈", "⚠️"],
        "entropy_surge": ["🔥", "📊", "🚨"],
        "pattern_anomaly": ["❌", "🔄", "⚠️"],
        "consciousness_instability": ["🧠", "⚡", "⚠️"],
        "memory_fragmentation": ["🧩", "💥", "⚠️"],
        "governance_drift": ["🛡️", "🌊", "🚨"],
        "trinity_desync": ["⚛️", "🧠", "🔀"],
        "identity_compromise": ["⚛️", "🚨", "🔓"],
        "guardian_malfunction": ["🛡️", "💥", "🚨"],
        "system_overload": ["💻", "🔥", "🚨"],
    }

    def __init__(
        self,
        websocket_url: str = "ws://localhost:8765",
        alert_threshold: float = 0.5,
        monitoring_interval: int = 5,
        governance_enabled: bool = True,
    ):
        super().__init__()
        self.websocket_url = websocket_url
        self.alert_threshold = alert_threshold
        self.monitoring_interval = monitoring_interval
        self.governance_enabled = governance_enabled

        # Enhanced monitoring windows with Constellation Framework components
        self.drift_history = deque(maxlen=100)
        self.entropy_history = deque(maxlen=100)
        self.pattern_history = deque(maxlen=50)
        self.consciousness_history = deque(maxlen=50)
        self.governance_history = deque(maxlen=75)
        self.trinity_sync_history = deque(maxlen=50)
        self.identity_health_history = deque(maxlen=50)
        self.guardian_health_history = deque(maxlen=50)

        # Enhanced threat tracking with governance
        self.active_threats: list[ThreatIndicator] = []
        self.intervention_history: list[dict] = []
        self.governance_escalations: list[dict] = []

        # System state with governance integration
        self.monitoring_active = False
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.governance_log: list[dict] = []

        # Constellation Framework monitoring state
        self.trinity_components = {
            "identity": {"health": 1.0, "last_check": time.time()},
            "consciousness": {"health": 1.0, "last_check": time.time()},
            "guardian": {"health": 1.0, "last_check": time.time()},
        }

        logger.info("🛡️ Enhanced Guardian Sentinel initialized")
        logger.info(f"   Alert threshold: {alert_threshold}")
        logger.info(f"   Monitoring interval: {monitoring_interval}s")
        logger.info(f"   Governance enabled: {governance_enabled}")

    async def start_monitoring(self):
        """Start the enhanced monitoring loop with governance integration"""
        self.monitoring_active = True

        # Connect to WebSocket for alerts
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info("📡 Connected to WebSocket for enhanced alerts")
        except Exception as e:
            logger.warning(f"Could not connect to WebSocket: {e}")
            self.websocket = None

        # Log monitoring start in governance
        if self.governance_enabled:
            await self._log_governance_action(
                "monitoring_started",
                {"alert_threshold": self.alert_threshold, "trinity_monitoring": True},
            )

        # Start enhanced monitoring tasks
        await asyncio.gather(
            self._monitor_drift(),
            self._monitor_entropy(),
            self._monitor_patterns(),
            self._monitor_consciousness(),
            self._monitor_governance(),
            self._monitor_trinity_framework(),
            self._monitor_identity_health(),
            self._monitor_guardian_health(),
        )

    async def _monitor_drift(self):
        """Monitor drift rate changes with governance validation"""
        while self.monitoring_active:
            try:
                # Enhanced drift reading with governance context
                current_drift = self._read_current_drift()
                governance_factor = self._get_governance_influence_on_drift()
                adjusted_drift = current_drift * (1.0 + governance_factor)

                self.drift_history.append(
                    {
                        "value": adjusted_drift,
                        "raw_value": current_drift,
                        "governance_factor": governance_factor,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Enhanced spike detection
                if len(self.drift_history) >= 2:
                    recent = [d["value"] for d in list(self.drift_history)[-10:]]
                    drift_rate = max(recent) - min(recent)

                    if drift_rate > self.THRESHOLDS["drift_rate"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="drift_spike",
                                severity=min(drift_rate / 0.5, 1.0),
                                source="drift_monitor",
                                timestamp=datetime.now(timezone.utc),
                                details={
                                    "drift_rate": drift_rate,
                                    "current_drift": adjusted_drift,
                                    "governance_factor": governance_factor,
                                    "recent_values": recent[-5:],
                                },
                                recommended_action="stabilize_drift",
                                governance_escalation=drift_rate > 0.3,
                                trinity_impact={
                                    "identity": 0.3,
                                    "consciousness": 0.7,
                                    "guardian": 0.5,
                                },
                                symbolic_signature=self.THREAT_SYMBOLS["drift_spike"],
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in enhanced drift monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_entropy(self):
        """Monitor entropy spikes with Constellation Framework awareness"""
        while self.monitoring_active:
            try:
                # Enhanced entropy reading with Trinity context
                current_entropy = self._read_current_entropy()
                trinity_entropy_factor = self._calculate_trinity_entropy_factor()
                adjusted_entropy = current_entropy * (1.0 + trinity_entropy_factor)

                self.entropy_history.append(
                    {
                        "value": adjusted_entropy,
                        "raw_value": current_entropy,
                        "trinity_factor": trinity_entropy_factor,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Enhanced surge detection
                if len(self.entropy_history) >= 2:
                    prev_entropy = self.entropy_history[-2]["value"]
                    entropy_spike = adjusted_entropy - prev_entropy

                    if entropy_spike > self.THRESHOLDS["entropy_spike"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="entropy_surge",
                                severity=min(entropy_spike / 0.5, 1.0),
                                source="entropy_monitor",
                                timestamp=datetime.now(timezone.utc),
                                details={
                                    "entropy_spike": entropy_spike,
                                    "current_entropy": adjusted_entropy,
                                    "previous_entropy": prev_entropy,
                                    "trinity_factor": trinity_entropy_factor,
                                },
                                recommended_action="reduce_entropy",
                                governance_escalation=entropy_spike > 0.5,
                                trinity_impact={
                                    "identity": 0.2,
                                    "consciousness": 0.8,
                                    "guardian": 0.4,
                                },
                                symbolic_signature=self.THREAT_SYMBOLS["entropy_surge"],
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in enhanced entropy monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_patterns(self):
        """Monitor pattern disruption with enhanced detection"""
        while self.monitoring_active:
            try:
                # Enhanced pattern coherence reading
                pattern_coherence = self._read_pattern_coherence()
                symbolic_integrity = self._assess_symbolic_integrity()
                combined_coherence = (pattern_coherence + symbolic_integrity) / 2

                self.pattern_history.append(
                    {
                        "coherence": combined_coherence,
                        "pattern_coherence": pattern_coherence,
                        "symbolic_integrity": symbolic_integrity,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Enhanced disruption detection
                if combined_coherence < self.THRESHOLDS["pattern_disruption"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="pattern_anomaly",
                            severity=(1.0 - combined_coherence),
                            source="pattern_monitor",
                            timestamp=datetime.now(timezone.utc),
                            details={
                                "pattern_coherence": pattern_coherence,
                                "symbolic_integrity": symbolic_integrity,
                                "combined_coherence": combined_coherence,
                                "threshold": self.THRESHOLDS["pattern_disruption"],
                            },
                            recommended_action="reinforce_patterns",
                            governance_escalation=combined_coherence < 0.3,
                            trinity_impact={
                                "identity": 0.4,
                                "consciousness": 0.7,
                                "guardian": 0.3,
                            },
                            symbolic_signature=self.THREAT_SYMBOLS["pattern_anomaly"],
                        )
                    )

                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"Error in enhanced pattern monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_consciousness(self):
        """Monitor consciousness state stability with Constellation integration"""
        while self.monitoring_active:
            try:
                # Enhanced consciousness state reading
                current_state = self._read_consciousness_state()
                coherence_level = self._assess_consciousness_coherence()
                trinity_alignment = self._check_consciousness_trinity_alignment()

                self.consciousness_history.append(
                    {
                        "state": current_state,
                        "coherence": coherence_level,
                        "trinity_alignment": trinity_alignment,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Enhanced instability detection
                if len(self.consciousness_history) >= 10:
                    recent_states = [h["state"] for h in list(self.consciousness_history)[-10:]]
                    unique_states = len(set(recent_states))
                    instability = unique_states / 10.0

                    # Factor in coherence and Trinity alignment
                    adjusted_instability = instability * (2.0 - coherence_level) * (2.0 - trinity_alignment)

                    if adjusted_instability > self.THRESHOLDS["consciousness_instability"]:
                        await self._raise_threat(
                            ThreatIndicator(
                                indicator_type="consciousness_instability",
                                severity=min(adjusted_instability, 1.0),
                                source="consciousness_monitor",
                                timestamp=datetime.now(timezone.utc),
                                details={
                                    "unique_states": unique_states,
                                    "recent_states": recent_states[-5:],
                                    "instability_score": adjusted_instability,
                                    "coherence_level": coherence_level,
                                    "trinity_alignment": trinity_alignment,
                                },
                                recommended_action="stabilize_consciousness",
                                governance_escalation=adjusted_instability > 0.7,
                                trinity_impact={
                                    "identity": 0.3,
                                    "consciousness": 1.0,
                                    "guardian": 0.6,
                                },
                                symbolic_signature=self.THREAT_SYMBOLS["consciousness_instability"],
                            )
                        )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in enhanced consciousness monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_governance(self):
        """Monitor governance system health and compliance"""
        while self.monitoring_active:
            try:
                if not self.governance_enabled:
                    await asyncio.sleep(self.monitoring_interval * 4)
                    continue

                # Governance health metrics
                governance_health = self._assess_governance_health()
                policy_compliance = self._check_policy_compliance()
                escalation_efficiency = self._calculate_escalation_efficiency()

                self.governance_history.append(
                    {
                        "health": governance_health,
                        "policy_compliance": policy_compliance,
                        "escalation_efficiency": escalation_efficiency,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Governance drift detection
                if governance_health < self.THRESHOLDS["governance_drift"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="governance_drift",
                            severity=1.0 - governance_health,
                            source="governance_monitor",
                            timestamp=datetime.now(timezone.utc),
                            details={
                                "governance_health": governance_health,
                                "policy_compliance": policy_compliance,
                                "escalation_efficiency": escalation_efficiency,
                                "threshold": self.THRESHOLDS["governance_drift"],
                            },
                            recommended_action="restore_governance",
                            governance_escalation=True,
                            trinity_impact={
                                "identity": 0.8,
                                "consciousness": 0.6,
                                "guardian": 1.0,
                            },
                            symbolic_signature=self.THREAT_SYMBOLS["governance_drift"],
                        )
                    )

                await asyncio.sleep(self.monitoring_interval * 3)

            except Exception as e:
                logger.error(f"Error in governance monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_trinity_framework(self):
        """Monitor Constellation Framework synchronization and health"""
        while self.monitoring_active:
            try:
                # Constellation Framework synchronization metrics
                sync_level = self._calculate_trinity_sync_level()
                component_health = self._get_trinity_component_health()
                cross_impact = self._assess_trinity_cross_impact()

                self.trinity_sync_history.append(
                    {
                        "sync_level": sync_level,
                        "component_health": component_health,
                        "cross_impact": cross_impact,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Trinity desynchronization detection
                if sync_level < self.THRESHOLDS["trinity_desync"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="trinity_desync",
                            severity=1.0 - sync_level,
                            source="trinity_monitor",
                            timestamp=datetime.now(timezone.utc),
                            details={
                                "sync_level": sync_level,
                                "component_health": component_health,
                                "cross_impact": cross_impact,
                                "threshold": self.THRESHOLDS["trinity_desync"],
                            },
                            recommended_action="resync_trinity_framework",
                            governance_escalation=True,
                            trinity_impact={
                                "identity": 0.8,
                                "consciousness": 0.8,
                                "guardian": 0.8,
                            },
                            symbolic_signature=self.THREAT_SYMBOLS["trinity_desync"],
                        )
                    )

                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"Error in Constellation Framework monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_identity_health(self):
        """Monitor Identity component (⚛️) health"""
        while self.monitoring_active:
            try:
                # Identity-specific health metrics
                identity_integrity = self._assess_identity_integrity()
                auth_system_health = self._check_auth_system_health()
                identity_coherence = self._calculate_identity_coherence()

                self.identity_health_history.append(
                    {
                        "integrity": identity_integrity,
                        "auth_health": auth_system_health,
                        "coherence": identity_coherence,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Update Constellation component status
                overall_identity_health = (identity_integrity + auth_system_health + identity_coherence) / 3
                self.trinity_components["identity"]["health"] = overall_identity_health
                self.trinity_components["identity"]["last_check"] = time.time()

                # Identity compromise detection
                if overall_identity_health < self.THRESHOLDS["identity_compromise"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="identity_compromise",
                            severity=1.0 - overall_identity_health,
                            source="identity_monitor",
                            timestamp=datetime.now(timezone.utc),
                            details={
                                "identity_integrity": identity_integrity,
                                "auth_health": auth_system_health,
                                "coherence": identity_coherence,
                                "overall_health": overall_identity_health,
                            },
                            recommended_action="secure_identity_systems",
                            governance_escalation=True,
                            trinity_impact={
                                "identity": 1.0,
                                "consciousness": 0.4,
                                "guardian": 0.7,
                            },
                            symbolic_signature=self.THREAT_SYMBOLS["identity_compromise"],
                        )
                    )

                await asyncio.sleep(self.monitoring_interval * 3)

            except Exception as e:
                logger.error(f"Error in identity health monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_guardian_health(self):
        """Monitor Guardian component (🛡️) health"""
        while self.monitoring_active:
            try:
                # Guardian-specific health metrics
                guardian_effectiveness = self._assess_guardian_effectiveness()
                protection_coverage = self._calculate_protection_coverage()
                response_capability = self._check_response_capability()

                self.guardian_health_history.append(
                    {
                        "effectiveness": guardian_effectiveness,
                        "coverage": protection_coverage,
                        "response": response_capability,
                        "timestamp": datetime.now(timezone.utc),
                    }
                )

                # Update Constellation component status
                overall_guardian_health = (guardian_effectiveness + protection_coverage + response_capability) / 3
                self.trinity_components["guardian"]["health"] = overall_guardian_health
                self.trinity_components["guardian"]["last_check"] = time.time()

                # Guardian malfunction detection
                if overall_guardian_health < self.THRESHOLDS["guardian_malfunction"]:
                    await self._raise_threat(
                        ThreatIndicator(
                            indicator_type="guardian_malfunction",
                            severity=1.0 - overall_guardian_health,
                            source="guardian_monitor",
                            timestamp=datetime.now(timezone.utc),
                            details={
                                "effectiveness": guardian_effectiveness,
                                "coverage": protection_coverage,
                                "response": response_capability,
                                "overall_health": overall_guardian_health,
                            },
                            recommended_action="restore_guardian_systems",
                            governance_escalation=True,
                            trinity_impact={
                                "identity": 0.8,
                                "consciousness": 0.9,
                                "guardian": 1.0,
                            },
                            symbolic_signature=self.THREAT_SYMBOLS["guardian_malfunction"],
                        )
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in guardian health monitoring: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _raise_threat(self, threat: ThreatIndicator):
        """Raise a threat alert with enhanced governance and Constellation Framework processing"""
        # Check severity threshold
        if threat.severity < self.alert_threshold:
            logger.info(f"🟡 Low severity threat detected: {threat.indicator_type}")
            return

        # Add to active threats
        self.active_threats.append(threat)

        # Enhanced threat logging
        logger.warning(f"🚨 ENHANCED THREAT DETECTED: {threat.indicator_type}")
        logger.warning(f"   Severity: {threat.severity:.2f}")
        logger.warning(f"   Action: {threat.recommended_action}")
        logger.warning(f"   Governance escalation: {threat.governance_escalation}")
        logger.warning(
            f"   Trinity impact: I:{threat.trinity_impact['identity']:.1f} C:{threat.trinity_impact['consciousness']:.1f} G:{threat.trinity_impact['guardian']:.1f}"
        )
        logger.warning(f"   Symbols: {'→'.join(threat.symbolic_signature)}")

        # Send enhanced WebSocket alert if connected
        if self.websocket and not self.websocket.closed:
            try:
                await self.websocket.send(json.dumps(threat.to_alert()))
            except Exception as e:
                logger.error(f"Failed to send enhanced alert: {e}")

        # Governance escalation handling
        if threat.governance_escalation and self.governance_enabled:
            await self._handle_governance_escalation(threat)

        # Constellation Framework specific handling
        if max(threat.trinity_impact.values()) > 0.8:
            await self._handle_trinity_critical_threat(threat)

        # Trigger intervention if critical
        if (
            threat.severity >= self.SEVERITY_LEVELS["critical"]
            or (threat.severity >= self.SEVERITY_LEVELS["governance_critical"] and threat.governance_escalation)
            or (
                threat.severity >= self.SEVERITY_LEVELS["trinity_critical"]
                and max(threat.trinity_impact.values()) > 0.8
            )
        ):
            await self._trigger_intervention(threat)

    async def _handle_governance_escalation(self, threat: ThreatIndicator):
        """Handle governance-specific threat escalation"""
        escalation = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "threat_id": f"GOV-{int(time.time())",
            "threat_type": threat.indicator_type,
            "severity": threat.severity,
            "escalation_reason": "governance_threshold_exceeded",
            "trinity_impact": threat.trinity_impact,
            "symbolic_signature": threat.symbolic_signature,
        }

        self.governance_escalations.append(escalation)

        # Log in governance system
        await self._log_governance_action(
            "threat_escalation",
            {
                "threat_type": threat.indicator_type,
                "severity": threat.severity,
                "trinity_impact": threat.trinity_impact,
            },
        )

        logger.critical(f"🛡️ GOVERNANCE ESCALATION: {threat.indicator_type}")

    async def _handle_trinity_critical_threat(self, threat: ThreatIndicator):
        """Handle Constellation Framework critical threats"""
        critical_components = [comp for comp, impact in threat.trinity_impact.items() if impact > 0.8]

        logger.critical(f"⚛️🧠🛡️ TRINITY CRITICAL THREAT: {threat.indicator_type}")
        logger.critical(f"   Critical components: {', '.join(critical_components)}")

        # Log Trinity-specific intervention
        await self._log_governance_action(
            "trinity_critical_threat",
            {
                "threat_type": threat.indicator_type,
                "critical_components": critical_components,
                "severity": threat.severity,
            },
        )

    async def _trigger_intervention(self, threat: ThreatIndicator):
        """Trigger enhanced intervention with governance validation"""
        intervention = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "threat": threat.indicator_type,
            "severity": threat.severity,
            "action_taken": threat.recommended_action,
            "governance_approved": self.governance_enabled,
            "trinity_impact": threat.trinity_impact,
            "details": {},
        }

        # Execute intervention based on type with governance validation
        if threat.indicator_type == "drift_spike":
            intervention["details"] = await self._intervene_drift_spike(threat)
        elif threat.indicator_type == "entropy_surge":
            intervention["details"] = await self._intervene_entropy_surge(threat)
        elif threat.indicator_type == "pattern_anomaly":
            intervention["details"] = await self._intervene_pattern_anomaly(threat)
        elif threat.indicator_type == "consciousness_instability":
            intervention["details"] = await self._intervene_consciousness_instability(threat)
        elif threat.indicator_type == "governance_drift":
            intervention["details"] = await self._intervene_governance_drift(threat)
        elif threat.indicator_type == "trinity_desync":
            intervention["details"] = await self._intervene_trinity_desync(threat)
        elif threat.indicator_type == "identity_compromise":
            intervention["details"] = await self._intervene_identity_compromise(threat)
        elif threat.indicator_type == "guardian_malfunction":
            intervention["details"] = await self._intervene_guardian_malfunction(threat)

        self.intervention_history.append(intervention)

        # Log intervention in governance system
        if self.governance_enabled:
            await self._log_governance_action(
                "intervention_executed",
                {
                    "threat_type": threat.indicator_type,
                    "intervention_action": threat.recommended_action,
                    "trinity_impact": threat.trinity_impact,
                },
            )

        logger.info(f"⚡ Enhanced intervention executed: {threat.recommended_action}")

    # Enhanced intervention methods

    async def _intervene_drift_spike(self, threat: ThreatIndicator) -> dict:
        """Intervene for drift spike with governance validation"""
        return {
            "action": "drift_dampening",
            "parameters": {"dampening_factor": 0.5, "duration_seconds": 60},
            "expected_result": "Drift rate reduction",
            "governance_approved": self.governance_enabled,
            "trinity_adjustments": {comp: max(0.1, 1.0 - impact) for comp, impact in threat.trinity_impact.items()},
        }

    async def _intervene_entropy_surge(self, threat: ThreatIndicator) -> dict:
        """Intervene for entropy surge with Constellation Framework consideration"""
        return {
            "action": "entropy_cooling",
            "parameters": {"cooling_rate": 0.1, "target_entropy": 0.3},
            "expected_result": "Entropy stabilization",
            "trinity_protection": max(threat.trinity_impact.values()) > 0.5,
            "symbolic_reinforcement": threat.symbolic_signature,
        }

    async def _intervene_pattern_anomaly(self, threat: ThreatIndicator) -> dict:
        """Intervene for pattern anomaly with enhanced symbolic processing"""
        return {
            "action": "pattern_reinforcement",
            "parameters": {
                "reinforcement_glyphs": ["🌿", "🔐", "💎"],
                "repetitions": 5,
                "trinity_alignment": True,
            },
            "expected_result": "Pattern coherence improvement",
            "symbolic_signature": threat.symbolic_signature,
        }

    async def _intervene_consciousness_instability(self, threat: ThreatIndicator) -> dict:
        """Intervene for consciousness instability with Constellation integration"""
        return {
            "action": "consciousness_anchoring",
            "parameters": {"anchor_state": "meditative", "anchor_duration": 120},
            "expected_result": "State stabilization",
            "trinity_synchronization": True,
            "consciousness_protection": threat.trinity_impact.get("consciousness", 0) > 0.7,
        }

    async def _intervene_governance_drift(self, threat: ThreatIndicator) -> dict:
        """Intervene for governance drift"""
        return {
            "action": "governance_restoration",
            "parameters": {"restore_policies": True, "validate_compliance": True},
            "expected_result": "Governance system restoration",
            "escalation_required": True,
            "human_oversight_required": True,
        }

    async def _intervene_trinity_desync(self, threat: ThreatIndicator) -> dict:
        """Intervene for Constellation Framework desynchronization"""
        return {
            "action": "trinity_resynchronization",
            "parameters": {"sync_all_components": True, "deep_alignment": True},
            "expected_result": "Constellation Framework synchronization restored",
            "component_specific_actions": {
                "identity": "validate_identity_coherence",
                "consciousness": "stabilize_consciousness_state",
                "guardian": "reinforce_protection_systems",
            },
        }

    async def _intervene_identity_compromise(self, threat: ThreatIndicator) -> dict:
        """Intervene for identity compromise"""
        return {
            "action": "identity_security_lockdown",
            "parameters": {"lockdown_level": "high", "audit_all_access": True},
            "expected_result": "Identity systems secured",
            "emergency_protocols": True,
            "trinity_protection": True,
        }

    async def _intervene_guardian_malfunction(self, threat: ThreatIndicator) -> dict:
        """Intervene for guardian malfunction"""
        return {
            "action": "guardian_system_restoration",
            "parameters": {
                "restore_all_functions": True,
                "validate_effectiveness": True,
            },
            "expected_result": "Guardian systems fully operational",
            "backup_guardian_activation": True,
            "trinity_critical_protection": True,
        }

    # Enhanced simulation methods with Constellation Framework context

    def _read_current_drift(self) -> float:
        """Enhanced drift reading with governance influence"""
        import random

        base = 0.3
        if random.random() > 0.9:  # 10% chance of spike
            return base + random.uniform(0.2, 0.5)
        return base + random.uniform(-0.1, 0.1)

    def _get_governance_influence_on_drift(self) -> float:
        """Calculate governance system influence on drift"""
        if not self.governance_enabled:
            return 0.0
        # Simulate governance influence (-0.2 to 0.3)
        import random

        return random.uniform(-0.2, 0.3)

    def _read_current_entropy(self) -> float:
        """Enhanced entropy reading"""
        import random

        base = 0.4
        if random.random() > 0.95:  # 5% chance of surge
            return base + random.uniform(0.3, 0.6)
        return base + random.uniform(-0.1, 0.1)

    def _calculate_trinity_entropy_factor(self) -> float:
        """Calculate Constellation Framework entropy factor"""
        # Factor based on Constellation component health
        avg_health = sum(comp["health"] for comp in self.trinity_components.values()) / 3
        return (1.0 - avg_health) * 0.3

    def _read_pattern_coherence(self) -> float:
        """Enhanced pattern coherence reading"""
        import random

        return random.uniform(0.3, 0.9)

    def _assess_symbolic_integrity(self) -> float:
        """Assess symbolic processing integrity"""
        import random

        return random.uniform(0.4, 0.95)

    def _read_consciousness_state(self) -> str:
        """Enhanced consciousness state reading"""
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
            "trinity_aligned",
            "governance_aware",
        ]
        return random.choice(states)

    def _assess_consciousness_coherence(self) -> float:
        """Assess consciousness coherence level"""
        import random

        return random.uniform(0.5, 1.0)

    def _check_consciousness_trinity_alignment(self) -> float:
        """Check consciousness alignment with Constellation Framework"""
        import random

        return random.uniform(0.6, 1.0)

    def _assess_governance_health(self) -> float:
        """Assess governance system health"""
        if not self.governance_enabled:
            return 1.0
        import random

        base = 0.8
        if random.random() > 0.95:  # 5% chance of governance issues
            return base - random.uniform(0.3, 0.6)
        return base + random.uniform(-0.1, 0.2)

    def _check_policy_compliance(self) -> float:
        """Check policy compliance rate"""
        import random

        return random.uniform(0.85, 1.0)

    def _calculate_escalation_efficiency(self) -> float:
        """Calculate escalation system efficiency"""
        import random

        return random.uniform(0.8, 1.0)

    def _calculate_trinity_sync_level(self) -> float:
        """Calculate Constellation Framework synchronization level"""
        # Based on component health variance
        healths = [comp["health"] for comp in self.trinity_components.values()]
        avg_health = sum(healths) / len(healths)
        variance = sum((h - avg_health) ** 2 for h in healths) / len(healths)
        return max(0.0, 1.0 - variance * 4)  # Higher variance = lower sync

    def _get_trinity_component_health(self) -> dict[str, float]:
        """Get current Constellation component health"""
        return {comp: data["health"] for comp, data in self.trinity_components.items()}

    def _assess_trinity_cross_impact(self) -> float:
        """Assess cross-impact between Constellation components"""
        import random

        return random.uniform(0.7, 1.0)

    def _assess_identity_integrity(self) -> float:
        """Assess identity system integrity"""
        import random

        base = 0.9
        if random.random() > 0.97:  # 3% chance of compromise
            return base - random.uniform(0.4, 0.7)
        return base + random.uniform(-0.05, 0.1)

    def _check_auth_system_health(self) -> float:
        """Check authentication system health"""
        import random

        return random.uniform(0.85, 1.0)

    def _calculate_identity_coherence(self) -> float:
        """Calculate identity coherence"""
        import random

        return random.uniform(0.8, 1.0)

    def _assess_guardian_effectiveness(self) -> float:
        """Assess guardian system effectiveness"""
        import random

        base = 0.9
        if random.random() > 0.98:  # 2% chance of malfunction
            return base - random.uniform(0.5, 0.8)
        return base + random.uniform(-0.05, 0.1)

    def _calculate_protection_coverage(self) -> float:
        """Calculate protection system coverage"""
        import random

        return random.uniform(0.9, 1.0)

    def _check_response_capability(self) -> float:
        """Check response system capability"""
        import random

        return random.uniform(0.85, 1.0)

    async def _log_governance_action(self, action: str, metadata: dict):
        """Log action in governance audit system"""
        if not self.governance_enabled:
            return

        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "metadata": metadata,
            "source": "guardian_sentinel",
            "symbolic_signature": self.generate_governance_glyph(action, metadata),
        }

        self.governance_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.governance_log) > 1000:
            self.governance_log = self.governance_log[-1000:]

        logger.debug(f"🔍 Guardian Sentinel governance action logged: {action}")

    def get_enhanced_threat_report(self) -> dict:
        """Generate enhanced threat analysis report with governance and Trinity metrics"""
        active_count = len([t for t in self.active_threats if (datetime.now(timezone.utc) - t.timestamp).seconds < 300])

        # Enhanced severity distribution
        severity_dist = {}
        governance_threats = 0
        trinity_threats = 0

        for level, threshold in self.SEVERITY_LEVELS.items():
            count = len([t for t in self.active_threats if t.severity >= threshold])
            severity_dist[level] = count

        for threat in self.active_threats:
            if threat.governance_escalation:
                governance_threats += 1
            if max(threat.trinity_impact.values()) > 0.7:
                trinity_threats += 1

        # Constellation Framework component health
        trinity_health = {comp: data["health"] for comp, data in self.trinity_components.items()}

        return {
            "total_threats": len(self.active_threats),
            "active_threats": active_count,
            "severity_distribution": severity_dist,
            "governance_threats": governance_threats,
            "trinity_critical_threats": trinity_threats,
            "intervention_count": len(self.intervention_history),
            "governance_escalations": len(self.governance_escalations),
            "monitoring_status": "active" if self.monitoring_active else "inactive",
            "trinity_component_health": trinity_health,
            "trinity_sync_level": self._calculate_trinity_sync_level(),
            "governance_enabled": self.governance_enabled,
            "recent_threats": [t.to_alert() for t in self.active_threats[-5:]],
            "governance_log_entries": len(self.governance_log),
        }

    async def stop_monitoring(self):
        """Stop the enhanced monitoring loop with governance logging"""
        self.monitoring_active = False
        if self.websocket:
            await self.websocket.close()

        # Log monitoring stop in governance
        if self.governance_enabled:
            await self._log_governance_action(
                "monitoring_stopped",
                {
                    "total_threats": len(self.active_threats),
                    "interventions": len(self.intervention_history),
                },
            )

        logger.info("🛑 Enhanced Guardian Sentinel monitoring stopped")


# Enhanced demo function
async def demo_enhanced_sentinel():
    """Demonstrate Enhanced Guardian Sentinel with governance and Constellation Framework"""
    sentinel = GuardianSentinel(alert_threshold=0.5, monitoring_interval=2, governance_enabled=True)

    print("🛡️ Enhanced Guardian Sentinel Demo")
    print("=" * 70)
    print("Starting enhanced monitoring with governance and Constellation Framework...")
    print("⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian")

    # Run monitoring for demo
    try:
        monitoring_task = asyncio.create_task(sentinel.start_monitoring())

        # Let it run for 30 seconds
        await asyncio.sleep(30)

        # Get enhanced report
        report = sentinel.get_enhanced_threat_report()
        print("\n📊 Enhanced Threat Report:")
        print(f"   Total threats: {report['total_threats']}")
        print(f"   Active threats: {report['active_threats']}")
        print(f"   Governance threats: {report['governance_threats']}")
        print(f"   Trinity critical: {report['trinity_critical_threats']}")
        print(f"   Interventions: {report['intervention_count']}")
        print(f"   Governance escalations: {report['governance_escalations']}")

        print("\n⚛️🧠🛡️ Trinity Component Health:")
        for comp, health in report["trinity_component_health"].items():
            status = "✅" if health > 0.8 else "⚠️" if health > 0.6 else "🚨"
            print(f"   {status} {comp.capitalize()}: {health:.2f}")

        print(f"\n🔄 Trinity Sync Level: {report['trinity_sync_level']:.2f}")
        print(f"🛡️ Governance Enabled: {report['governance_enabled']}")
        print(f"📝 Governance Log Entries: {report['governance_log_entries']}")

        print("\n🔍 Recent Threats:")
        for threat in report["recent_threats"]:
            trinity_str = f"I:{threat['trinity_impact']['identity']:.1f} C:{threat['trinity_impact']['consciousness']:.1f} G:{threat['trinity_impact']['guardian']:.1f}"
            gov_indicator = "🛡️" if threat["governance_escalation"] else ""
            print(
                f"   - {threat['indicator']} {gov_indicator} (severity: {threat['severity']:.2f}) [{trinity_str}] {'→'.join(threat['symbolic_signature'])}"
            )

    finally:
        await sentinel.stop_monitoring()
        monitoring_task.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(demo_enhanced_sentinel())