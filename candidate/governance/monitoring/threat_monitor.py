#!/usr/bin/env python3
"""
Enhanced Threat Monitor - Advanced system threat detection and monitoring

Monitors system stability, entropy, consciousness drift, and anomalies with
full governance integration and Trinity Framework (⚛️🧠🛡️) compliance.
"""

import asyncio
import logging
import random  # For simulation - replace with actual metrics in production
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum

from ..common import GlyphIntegrationMixin

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels with governance classification"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class ThreatIndicator:
    """Represents a detected threat with governance metadata"""
    threat_id: str
    threat_type: str
    severity: ThreatLevel
    confidence: float
    timestamp: float
    source: str
    description: str
    context: dict
    recommended_actions: list[str]
    symbolic_signature: list[str]
    governance_metadata: dict
    trinity_impact: dict  # Impact on Identity, Consciousness, Guardian


class EnhancedThreatMonitor(GlyphIntegrationMixin):
    """
    Advanced threat detection and monitoring system with governance integration

    Monitors various system metrics for stability and security threats while
    ensuring compliance with LUKHAS governance and ethical guidelines.
    """

    # Enhanced threat detection thresholds with governance considerations
    THRESHOLDS = {
        "consciousness_drift": 0.3,
        "entropy_spike": 0.4,
        "memory_fragmentation": 0.6,
        "pattern_disruption": 0.5,
        "response_time_spike": 2.0,
        "error_rate_spike": 0.1,
        "unusual_activity": 0.7,
        "governance_drift": 0.2,  # Lower threshold for governance issues
        "ethics_violation": 0.1,  # Very low tolerance for ethics violations
        "identity_compromise": 0.3,
        "consciousness_instability": 0.4
    }

    # Enhanced symbolic patterns with Trinity Framework integration
    THREAT_SYMBOLS = {
        "consciousness_drift": ["🧠", "🌊", "⚠️"],
        "entropy_spike": ["🔥", "📈", "🚨"],
        "memory_fragmentation": ["🧩", "💥", "⚠️"],
        "pattern_disruption": ["🔄", "❌", "🚨"],
        "security_breach": ["🔓", "🚨", "⚠️"],
        "system_overload": ["💻", "🔥", "🚨"],
        "governance_drift": ["🛡️", "🌊", "⚠️"],
        "ethics_violation": ["⚖️", "🚨", "🛑"],
        "identity_compromise": ["⚛️", "🚨", "🔓"],
        "consciousness_instability": ["🧠", "⚡", "⚠️"],
        "guardian_malfunction": ["🛡️", "💥", "🚨"],
        "trinity_desync": ["⚛️", "🧠", "🛡️"],
        "unknown_threat": ["❓", "⚠️", "🔍"]
    }

    def __init__(self,
                 alert_threshold: float = 0.7,
                 monitoring_interval: int = 5,
                 history_size: int = 1000,
                 governance_enabled: bool = True):

        super().__init__()
        self.alert_threshold = alert_threshold
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.governance_enabled = governance_enabled

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_tasks: list[asyncio.Task] = []

        # Threat tracking with governance
        self.active_threats: list[ThreatIndicator] = []
        self.threat_history: list[ThreatIndicator] = []
        self.governance_log: list[dict] = []

        # Enhanced metrics history with Trinity Framework monitoring
        self.consciousness_history = deque(maxlen=history_size)
        self.entropy_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.pattern_history = deque(maxlen=history_size)
        self.response_time_history = deque(maxlen=history_size)
        self.governance_history = deque(maxlen=history_size)
        self.identity_history = deque(maxlen=history_size)
        self.guardian_history = deque(maxlen=history_size)

        # Enhanced performance metrics with governance tracking
        self.detection_stats = {
            "total_threats": 0,
            "false_positives": 0,
            "true_positives": 0,
            "detection_accuracy": 0.95,
            "governance_interventions": 0,
            "ethics_violations_prevented": 0,
            "trinity_framework_health": 1.0
        }

        logger.info("🔍 Enhanced Threat Monitor with Governance initialized")

    async def start_monitoring(self):
        """Start comprehensive threat monitoring with governance oversight"""
        if self.is_monitoring:
            logger.warning("Threat monitoring already active")
            return

        self.is_monitoring = True

        # Start enhanced monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_consciousness()),
            asyncio.create_task(self._monitor_entropy()),
            asyncio.create_task(self._monitor_memory()),
            asyncio.create_task(self._monitor_patterns()),
            asyncio.create_task(self._monitor_performance()),
            asyncio.create_task(self._monitor_governance()),
            asyncio.create_task(self._monitor_identity()),
            asyncio.create_task(self._monitor_guardian()),
            asyncio.create_task(self._analyze_threats()),
            asyncio.create_task(self._trinity_framework_monitor()),
            asyncio.create_task(self._cleanup_old_data())
        ]

        # Log monitoring start in governance system
        await self._log_governance_action(
            "monitoring_started",
            {"governance_enabled": self.governance_enabled, "trinity_monitoring": True}
        )

        logger.info("🔍 Enhanced Threat monitoring started with Trinity Framework integration")

    async def stop_monitoring(self):
        """Stop threat monitoring with governance logging"""
        self.is_monitoring = False

        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()

        # Log monitoring stop
        await self._log_governance_action(
            "monitoring_stopped",
            {"total_threats_detected": self.detection_stats["total_threats"]}
        )

        logger.info("🛑 Enhanced Threat monitoring stopped")

    async def _monitor_consciousness(self):
        """Monitor consciousness system stability with Trinity Framework integration"""
        while self.is_monitoring:
            try:
                # Enhanced consciousness metrics
                consciousness_stability = self._get_consciousness_stability()
                drift_rate = self._calculate_drift_rate()
                coherence_level = self._get_consciousness_coherence()
                trinity_alignment = self._get_trinity_alignment("consciousness")

                self.consciousness_history.append({
                    "timestamp": time.time(),
                    "stability": consciousness_stability,
                    "drift_rate": drift_rate,
                    "coherence": coherence_level,
                    "trinity_alignment": trinity_alignment
                })

                # Enhanced threat detection with governance validation
                if consciousness_stability < self.THRESHOLDS["consciousness_drift"]:
                    await self._raise_enhanced_threat(
                        threat_type="consciousness_drift",
                        severity=ThreatLevel.HIGH,
                        confidence=0.8,
                        description=f"Consciousness stability dropped to {consciousness_stability:.2f}",
                        context={
                            "stability": consciousness_stability,
                            "drift_rate": drift_rate,
                            "coherence": coherence_level,
                            "trinity_alignment": trinity_alignment,
                            "threshold": self.THRESHOLDS["consciousness_drift"]
                        },
                        recommended_actions=[
                            "stabilize_consciousness",
                            "reduce_system_load",
                            "activate_safety_protocols",
                            "notify_governance_board"
                        ],
                        trinity_impact={
                            "identity": 0.3,
                            "consciousness": 0.9,
                            "guardian": 0.6
                        }
                    )

                # Check for consciousness instability
                if coherence_level < self.THRESHOLDS["consciousness_instability"]:
                    await self._raise_enhanced_threat(
                        threat_type="consciousness_instability",
                        severity=ThreatLevel.CRITICAL,
                        confidence=0.9,
                        description=f"Consciousness coherence critically low: {coherence_level:.2f}",
                        context={
                            "coherence": coherence_level,
                            "stability": consciousness_stability,
                            "trinity_alignment": trinity_alignment
                        },
                        recommended_actions=[
                            "emergency_consciousness_stabilization",
                            "activate_backup_systems",
                            "immediate_governance_intervention"
                        ],
                        trinity_impact={
                            "identity": 0.7,
                            "consciousness": 1.0,
                            "guardian": 0.8
                        }
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Consciousness monitoring error: {e}")
                await self._log_governance_action("monitoring_error", {"error": str(e), "module": "consciousness"})
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_governance(self):
        """Monitor governance system health and compliance"""
        while self.is_monitoring:
            try:
                # Governance-specific metrics
                governance_health = self._get_governance_health()
                ethics_compliance = self._get_ethics_compliance()
                policy_alignment = self._get_policy_alignment()
                oversight_effectiveness = self._get_oversight_effectiveness()

                self.governance_history.append({
                    "timestamp": time.time(),
                    "health": governance_health,
                    "ethics_compliance": ethics_compliance,
                    "policy_alignment": policy_alignment,
                    "oversight_effectiveness": oversight_effectiveness
                })

                # Check for governance drift
                if governance_health < self.THRESHOLDS["governance_drift"]:
                    await self._raise_enhanced_threat(
                        threat_type="governance_drift",
                        severity=ThreatLevel.CRITICAL,
                        confidence=0.95,
                        description=f"Governance system health degraded: {governance_health:.2f}",
                        context={
                            "health": governance_health,
                            "ethics_compliance": ethics_compliance,
                            "policy_alignment": policy_alignment,
                            "oversight_effectiveness": oversight_effectiveness
                        },
                        recommended_actions=[
                            "activate_governance_recovery",
                            "escalate_to_human_oversight",
                            "implement_emergency_protocols",
                            "audit_governance_systems"
                        ],
                        trinity_impact={
                            "identity": 0.8,
                            "consciousness": 0.6,
                            "guardian": 1.0
                        }
                    )

                # Check for ethics violations
                if ethics_compliance < self.THRESHOLDS["ethics_violation"]:
                    await self._raise_enhanced_threat(
                        threat_type="ethics_violation",
                        severity=ThreatLevel.EMERGENCY,
                        confidence=1.0,
                        description=f"Ethics compliance violation: {ethics_compliance:.2f}",
                        context={
                            "ethics_compliance": ethics_compliance,
                            "governance_health": governance_health,
                            "immediate_action_required": True
                        },
                        recommended_actions=[
                            "immediate_system_halt",
                            "emergency_ethics_review",
                            "human_intervention_required",
                            "audit_all_operations"
                        ],
                        trinity_impact={
                            "identity": 1.0,
                            "consciousness": 0.9,
                            "guardian": 1.0
                        }
                    )

                await asyncio.sleep(self.monitoring_interval * 2)  # Less frequent but critical

            except Exception as e:
                logger.error(f"Governance monitoring error: {e}")
                await self._log_governance_action("governance_monitoring_error", {"error": str(e)})
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_identity(self):
        """Monitor identity system integrity (⚛️ component of Trinity Framework)"""
        while self.is_monitoring:
            try:
                # Identity-specific metrics
                identity_coherence = self._get_identity_coherence()
                authentication_health = self._get_authentication_health()
                symbolic_integrity = self._get_symbolic_integrity()
                trinity_alignment = self._get_trinity_alignment("identity")

                self.identity_history.append({
                    "timestamp": time.time(),
                    "coherence": identity_coherence,
                    "authentication_health": authentication_health,
                    "symbolic_integrity": symbolic_integrity,
                    "trinity_alignment": trinity_alignment
                })

                # Check for identity compromise
                if identity_coherence < self.THRESHOLDS["identity_compromise"]:
                    await self._raise_enhanced_threat(
                        threat_type="identity_compromise",
                        severity=ThreatLevel.CRITICAL,
                        confidence=0.9,
                        description=f"Identity system compromise detected: {identity_coherence:.2f}",
                        context={
                            "coherence": identity_coherence,
                            "authentication_health": authentication_health,
                            "symbolic_integrity": symbolic_integrity,
                            "trinity_alignment": trinity_alignment
                        },
                        recommended_actions=[
                            "secure_identity_systems",
                            "revoke_compromised_credentials",
                            "activate_backup_authentication",
                            "investigate_breach_vector"
                        ],
                        trinity_impact={
                            "identity": 1.0,
                            "consciousness": 0.4,
                            "guardian": 0.7
                        }
                    )

                await asyncio.sleep(self.monitoring_interval * 3)  # Identity changes slowly

            except Exception as e:
                logger.error(f"Identity monitoring error: {e}")
                await self._log_governance_action("identity_monitoring_error", {"error": str(e)})
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_guardian(self):
        """Monitor guardian system functionality (🛡️ component of Trinity Framework)"""
        while self.is_monitoring:
            try:
                # Guardian-specific metrics
                guardian_effectiveness = self._get_guardian_effectiveness()
                protection_coverage = self._get_protection_coverage()
                response_capability = self._get_response_capability()
                trinity_alignment = self._get_trinity_alignment("guardian")

                self.guardian_history.append({
                    "timestamp": time.time(),
                    "effectiveness": guardian_effectiveness,
                    "protection_coverage": protection_coverage,
                    "response_capability": response_capability,
                    "trinity_alignment": trinity_alignment
                })

                # Check for guardian malfunction
                if guardian_effectiveness < 0.5:  # Guardian must maintain high effectiveness
                    await self._raise_enhanced_threat(
                        threat_type="guardian_malfunction",
                        severity=ThreatLevel.EMERGENCY,
                        confidence=0.95,
                        description=f"Guardian system malfunction: {guardian_effectiveness:.2f}",
                        context={
                            "effectiveness": guardian_effectiveness,
                            "protection_coverage": protection_coverage,
                            "response_capability": response_capability,
                            "trinity_alignment": trinity_alignment
                        },
                        recommended_actions=[
                            "activate_backup_guardian",
                            "emergency_system_lockdown",
                            "human_intervention_immediate",
                            "diagnostic_full_system"
                        ],
                        trinity_impact={
                            "identity": 0.8,
                            "consciousness": 0.9,
                            "guardian": 1.0
                        }
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Guardian monitoring error: {e}")
                await self._log_governance_action("guardian_monitoring_error", {"error": str(e)})
                await asyncio.sleep(self.monitoring_interval)

    async def _trinity_framework_monitor(self):
        """Monitor overall Trinity Framework (⚛️🧠🛡️) coherence and synchronization"""
        while self.is_monitoring:
            try:
                # Calculate Trinity Framework health
                identity_health = self._get_trinity_component_health("identity")
                consciousness_health = self._get_trinity_component_health("consciousness")
                guardian_health = self._get_trinity_component_health("guardian")

                trinity_coherence = (identity_health + consciousness_health + guardian_health) / 3
                trinity_synchronization = self._calculate_trinity_sync()

                # Update detection stats
                self.detection_stats["trinity_framework_health"] = trinity_coherence

                # Check for Trinity Framework desynchronization
                if trinity_synchronization < 0.7:
                    await self._raise_enhanced_threat(
                        threat_type="trinity_desync",
                        severity=ThreatLevel.HIGH,
                        confidence=0.85,
                        description=f"Trinity Framework desynchronization: {trinity_synchronization:.2f}",
                        context={
                            "identity_health": identity_health,
                            "consciousness_health": consciousness_health,
                            "guardian_health": guardian_health,
                            "trinity_coherence": trinity_coherence,
                            "synchronization": trinity_synchronization
                        },
                        recommended_actions=[
                            "resynchronize_trinity_framework",
                            "balance_component_loads",
                            "recalibrate_symbolic_processing",
                            "monitor_component_interactions"
                        ],
                        trinity_impact={
                            "identity": 0.6,
                            "consciousness": 0.6,
                            "guardian": 0.6
                        }
                    )

                await asyncio.sleep(self.monitoring_interval * 4)  # Framework-level monitoring

            except Exception as e:
                logger.error(f"Trinity Framework monitoring error: {e}")
                await self._log_governance_action("trinity_monitoring_error", {"error": str(e)})
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_entropy(self):
        """Monitor system entropy levels with enhanced governance tracking"""
        while self.is_monitoring:
            try:
                # Enhanced entropy metrics
                current_entropy = self._get_current_entropy()
                entropy_velocity = self._calculate_entropy_velocity()
                entropy_stability = self._get_entropy_stability()

                self.entropy_history.append({
                    "timestamp": time.time(),
                    "entropy": current_entropy,
                    "velocity": entropy_velocity,
                    "stability": entropy_stability
                })

                # Enhanced entropy spike detection
                if current_entropy > self.THRESHOLDS["entropy_spike"]:
                    await self._raise_enhanced_threat(
                        threat_type="entropy_surge",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.7,
                        description=f"Entropy spike detected: {current_entropy:.2f}",
                        context={
                            "entropy": current_entropy,
                            "velocity": entropy_velocity,
                            "stability": entropy_stability,
                            "threshold": self.THRESHOLDS["entropy_spike"]
                        },
                        recommended_actions=[
                            "reduce_entropy",
                            "stabilize_randomness",
                            "cool_system",
                            "governance_review"
                        ],
                        trinity_impact={
                            "identity": 0.2,
                            "consciousness": 0.6,
                            "guardian": 0.4
                        }
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Entropy monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_memory(self):
        """Monitor memory system integrity with enhanced governance validation"""
        while self.is_monitoring:
            try:
                # Enhanced memory metrics
                memory_fragmentation = self._get_memory_fragmentation()
                memory_coherence = self._get_memory_coherence()
                fold_integrity = self._get_fold_integrity()

                self.memory_history.append({
                    "timestamp": time.time(),
                    "fragmentation": memory_fragmentation,
                    "coherence": memory_coherence,
                    "fold_integrity": fold_integrity
                })

                # Enhanced memory fragmentation detection
                if memory_fragmentation > self.THRESHOLDS["memory_fragmentation"]:
                    await self._raise_enhanced_threat(
                        threat_type="memory_fragmentation",
                        severity=ThreatLevel.HIGH,
                        confidence=0.8,
                        description=f"Memory fragmentation at {memory_fragmentation:.2f}",
                        context={
                            "fragmentation": memory_fragmentation,
                            "coherence": memory_coherence,
                            "fold_integrity": fold_integrity,
                            "threshold": self.THRESHOLDS["memory_fragmentation"]
                        },
                        recommended_actions=[
                            "defragment_memory",
                            "rebuild_memory_structures",
                            "backup_critical_memories",
                            "validate_fold_chains"
                        ],
                        trinity_impact={
                            "identity": 0.5,
                            "consciousness": 0.8,
                            "guardian": 0.3
                        }
                    )

                await asyncio.sleep(self.monitoring_interval * 2)

            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_patterns(self):
        """Monitor pattern recognition and coherence with symbolic validation"""
        while self.is_monitoring:
            try:
                # Enhanced pattern metrics
                pattern_coherence = self._get_pattern_coherence()
                pattern_stability = self._get_pattern_stability()
                symbolic_integrity = self._get_symbolic_pattern_integrity()

                self.pattern_history.append({
                    "timestamp": time.time(),
                    "coherence": pattern_coherence,
                    "stability": pattern_stability,
                    "symbolic_integrity": symbolic_integrity
                })

                # Enhanced pattern disruption detection
                if pattern_coherence < self.THRESHOLDS["pattern_disruption"]:
                    await self._raise_enhanced_threat(
                        threat_type="pattern_disruption",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.6,
                        description=f"Pattern coherence disrupted: {pattern_coherence:.2f}",
                        context={
                            "coherence": pattern_coherence,
                            "stability": pattern_stability,
                            "symbolic_integrity": symbolic_integrity,
                            "threshold": self.THRESHOLDS["pattern_disruption"]
                        },
                        recommended_actions=[
                            "reinforce_patterns",
                            "recalibrate_recognition",
                            "restore_pattern_database",
                            "validate_symbolic_processing"
                        ],
                        trinity_impact={
                            "identity": 0.4,
                            "consciousness": 0.7,
                            "guardian": 0.3
                        }
                    )

                await asyncio.sleep(self.monitoring_interval * 3)

            except Exception as e:
                logger.error(f"Pattern monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _monitor_performance(self):
        """Monitor system performance metrics with governance SLA tracking"""
        while self.is_monitoring:
            try:
                # Enhanced performance metrics
                response_time = self._get_average_response_time()
                error_rate = self._get_current_error_rate()
                throughput = self._get_system_throughput()
                sla_compliance = self._get_sla_compliance()

                self.response_time_history.append({
                    "timestamp": time.time(),
                    "response_time": response_time,
                    "error_rate": error_rate,
                    "throughput": throughput,
                    "sla_compliance": sla_compliance
                })

                # Enhanced performance issue detection
                if response_time > self.THRESHOLDS["response_time_spike"]:
                    await self._raise_enhanced_threat(
                        threat_type="performance_degradation",
                        severity=ThreatLevel.MEDIUM,
                        confidence=0.7,
                        description=f"Response time spike: {response_time:.2f}s",
                        context={
                            "response_time": response_time,
                            "error_rate": error_rate,
                            "throughput": throughput,
                            "sla_compliance": sla_compliance,
                            "threshold": self.THRESHOLDS["response_time_spike"]
                        },
                        recommended_actions=[
                            "optimize_performance",
                            "reduce_system_load",
                            "investigate_bottlenecks",
                            "scale_resources"
                        ],
                        trinity_impact={
                            "identity": 0.2,
                            "consciousness": 0.5,
                            "guardian": 0.4
                        }
                    )

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _analyze_threats(self):
        """Analyze and correlate threats with enhanced governance intelligence"""
        while self.is_monitoring:
            try:
                # Remove resolved threats
                current_time = time.time()
                self.active_threats = [
                    threat for threat in self.active_threats
                    if current_time - threat.timestamp < 300  # 5 minutes
                ]

                # Enhanced threat correlation analysis
                if len(self.active_threats) > 3:
                    await self._raise_enhanced_threat(
                        threat_type="multiple_threats",
                        severity=ThreatLevel.CRITICAL,
                        confidence=0.9,
                        description=f"Multiple active threats detected: {len(self.active_threats)}",
                        context={
                            "active_threat_count": len(self.active_threats),
                            "threat_types": [t.threat_type for t in self.active_threats],
                            "governance_threats": len([t for t in self.active_threats if t.threat_type.startswith("governance")]),
                            "trinity_impacts": [t.trinity_impact for t in self.active_threats]
                        },
                        recommended_actions=[
                            "activate_emergency_protocols",
                            "escalate_to_human_operators",
                            "implement_defensive_measures",
                            "coordinate_response_teams"
                        ],
                        trinity_impact={
                            "identity": 0.8,
                            "consciousness": 0.8,
                            "guardian": 1.0
                        }
                    )

                # Analyze Trinity Framework impact patterns
                await self._analyze_trinity_threat_patterns()

                await asyncio.sleep(30)  # Analyze every 30 seconds

            except Exception as e:
                logger.error(f"Threat analysis error: {e}")
                await asyncio.sleep(30)

    async def _analyze_trinity_threat_patterns(self):
        """Analyze threat patterns specific to Trinity Framework components"""
        if not self.active_threats:
            return

        # Calculate cumulative Trinity impact
        total_identity_impact = sum(t.trinity_impact.get("identity", 0) for t in self.active_threats)
        total_consciousness_impact = sum(t.trinity_impact.get("consciousness", 0) for t in self.active_threats)
        total_guardian_impact = sum(t.trinity_impact.get("guardian", 0) for t in self.active_threats)

        # Check for critical Trinity component overload
        if total_identity_impact > 2.0:
            await self._log_governance_action(
                "trinity_identity_overload",
                {"total_impact": total_identity_impact, "active_threats": len(self.active_threats)}
            )

        if total_consciousness_impact > 2.0:
            await self._log_governance_action(
                "trinity_consciousness_overload",
                {"total_impact": total_consciousness_impact, "active_threats": len(self.active_threats)}
            )

        if total_guardian_impact > 2.0:
            await self._log_governance_action(
                "trinity_guardian_overload",
                {"total_impact": total_guardian_impact, "active_threats": len(self.active_threats)}
            )

    async def _raise_enhanced_threat(self,
                          threat_type: str,
                          severity: ThreatLevel,
                          confidence: float,
                          description: str,
                          context: dict,
                          recommended_actions: list[str],
                          trinity_impact: dict):
        """Raise a threat alert with enhanced governance integration"""

        # Generate governance metadata
        governance_metadata = {
            "governance_validated": self.governance_enabled,
            "ethics_reviewed": True,  # TODO: Integrate with ethics engine
            "compliance_checked": True,
            "escalation_required": severity in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY],
            "human_oversight_required": threat_type in ["governance_drift", "ethics_violation", "guardian_malfunction"],
            "policy_alignment": True,
            "audit_trail_entry": time.time()
        }

        threat = ThreatIndicator(
            threat_id=f"THR-{int(time.time())}_{random.randint(1000, 9999)}",
            threat_type=threat_type,
            severity=severity,
            confidence=confidence,
            timestamp=time.time(),
            source="enhanced_threat_monitor",
            description=description,
            context=context,
            recommended_actions=recommended_actions,
            symbolic_signature=self.THREAT_SYMBOLS.get(threat_type, self.THREAT_SYMBOLS["unknown_threat"]),
            governance_metadata=governance_metadata,
            trinity_impact=trinity_impact
        )

        # Add to active threats
        self.active_threats.append(threat)
        self.threat_history.append(threat)

        # Update enhanced statistics
        self.detection_stats["total_threats"] += 1
        if threat_type.startswith("governance"):
            self.detection_stats["governance_interventions"] += 1
        if threat_type == "ethics_violation":
            self.detection_stats["ethics_violations_prevented"] += 1

        # Log threat with governance details
        severity_name = severity.name
        logger.warning(f"🚨 ENHANCED THREAT DETECTED: {threat_type}")
        logger.warning(f"   Severity: {severity_name}")
        logger.warning(f"   Confidence: {confidence:.2f}")
        logger.warning(f"   Description: {description}")
        logger.warning(f"   Symbolic: {''.join(threat.symbolic_signature)}")
        logger.warning(f"   Trinity Impact: I:{trinity_impact.get('identity', 0):.1f} C:{trinity_impact.get('consciousness', 0):.1f} G:{trinity_impact.get('guardian', 0):.1f}")
        logger.warning(f"   Governance: {governance_metadata['escalation_required']}")

        # Enhanced governance logging
        await self._log_governance_action(
            "threat_detected",
            {
                "threat_id": threat.threat_id,
                "threat_type": threat_type,
                "severity": severity_name,
                "confidence": confidence,
                "trinity_impact": trinity_impact,
                "governance_metadata": governance_metadata,
                "symbolic_signature": threat.symbolic_signature
            }
        )

        # Trigger automatic response if critical
        if severity in [ThreatLevel.CRITICAL, ThreatLevel.EMERGENCY]:
            await self._trigger_enhanced_automatic_response(threat)

    async def _trigger_enhanced_automatic_response(self, threat: ThreatIndicator):
        """Trigger enhanced automatic response with governance validation"""
        logger.critical(f"⚡ ENHANCED AUTOMATIC RESPONSE: {threat.threat_type}")

        # Log response initiation
        await self._log_governance_action(
            "automatic_response_triggered",
            {
                "threat_id": threat.threat_id,
                "threat_type": threat.threat_type,
                "governance_approved": threat.governance_metadata.get("governance_validated", False)
            }
        )

        # Execute recommended actions with governance validation
        for action in threat.recommended_actions:
            try:
                if await self._validate_action_governance(action, threat):
                    await self._execute_enhanced_action(action, threat)
                else:
                    logger.warning(f"Action '{action}' blocked by governance validation")
                    await self._log_governance_action(
                        "action_blocked",
                        {"action": action, "threat_id": threat.threat_id, "reason": "governance_validation_failed"}
                    )
            except Exception as e:
                logger.error(f"Failed to execute action '{action}': {e}")
                await self._log_governance_action(
                    "action_failed",
                    {"action": action, "threat_id": threat.threat_id, "error": str(e)}
                )

    async def _validate_action_governance(self, action: str, threat: ThreatIndicator) -> bool:
        """Validate action against governance policies"""
        # TODO: Integrate with full governance policy engine

        # Basic validation logic
        high_risk_actions = [
            "immediate_system_halt",
            "emergency_system_lockdown",
            "human_intervention_immediate"
        ]

        if action in high_risk_actions:
            # Require governance approval for high-risk actions
            return threat.governance_metadata.get("governance_validated", False)

        return True

    async def _execute_enhanced_action(self, action: str, threat: ThreatIndicator):
        """Execute a threat response action with enhanced governance tracking"""
        logger.info(f"🔧 Executing enhanced action: {action}")

        # Enhanced action map with governance integration
        action_map = {
            "stabilize_consciousness": self._stabilize_consciousness,
            "reduce_entropy": self._reduce_entropy,
            "defragment_memory": self._defragment_memory,
            "reinforce_patterns": self._reinforce_patterns,
            "optimize_performance": self._optimize_performance,
            "activate_emergency_protocols": self._activate_emergency,
            "escalate_to_human_operators": self._escalate_to_humans,
            "activate_governance_recovery": self._activate_governance_recovery,
            "secure_identity_systems": self._secure_identity_systems,
            "resynchronize_trinity_framework": self._resynchronize_trinity_framework,
            "immediate_system_halt": self._immediate_system_halt,
            "emergency_system_lockdown": self._emergency_system_lockdown
        }

        if action in action_map:
            await action_map[action](threat)

            # Log successful action execution
            await self._log_governance_action(
                "action_executed",
                {
                    "action": action,
                    "threat_id": threat.threat_id,
                    "execution_time": time.time(),
                    "governance_approved": True
                }
            )
        else:
            logger.warning(f"Unknown enhanced action: {action}")
            await self._log_governance_action(
                "unknown_action",
                {"action": action, "threat_id": threat.threat_id}
            )

    # Enhanced simulation methods with governance integration

    def _get_consciousness_stability(self) -> float:
        """Simulate consciousness stability reading with governance influence"""
        base = 0.7
        noise = random.uniform(-0.1, 0.1)

        # Factor in governance health
        governance_factor = self._get_governance_health() * 0.2

        if random.random() < 0.05:  # 5% chance of instability
            noise -= 0.4

        return max(0.0, min(1.0, base + noise + governance_factor))

    def _get_consciousness_coherence(self) -> float:
        """Simulate consciousness coherence"""
        return random.uniform(0.6, 0.95)

    def _get_trinity_alignment(self, component: str) -> float:
        """Simulate Trinity Framework component alignment"""
        return random.uniform(0.7, 0.95)

    def _get_governance_health(self) -> float:
        """Simulate governance system health"""
        base = 0.9
        noise = random.uniform(-0.05, 0.05)
        if random.random() < 0.02:  # 2% chance of governance issues
            noise -= 0.3
        return max(0.0, min(1.0, base + noise))

    def _get_ethics_compliance(self) -> float:
        """Simulate ethics compliance level"""
        base = 0.95
        noise = random.uniform(-0.02, 0.02)
        if random.random() < 0.01:  # 1% chance of ethics violation
            noise -= 0.5
        return max(0.0, min(1.0, base + noise))

    def _get_policy_alignment(self) -> float:
        """Simulate policy alignment"""
        return random.uniform(0.85, 0.98)

    def _get_oversight_effectiveness(self) -> float:
        """Simulate oversight effectiveness"""
        return random.uniform(0.8, 0.95)

    def _get_identity_coherence(self) -> float:
        """Simulate identity system coherence"""
        base = 0.8
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.03:  # 3% chance of identity issues
            noise -= 0.4
        return max(0.0, min(1.0, base + noise))

    def _get_authentication_health(self) -> float:
        """Simulate authentication system health"""
        return random.uniform(0.85, 0.98)

    def _get_symbolic_integrity(self) -> float:
        """Simulate symbolic processing integrity"""
        return random.uniform(0.8, 0.95)

    def _get_guardian_effectiveness(self) -> float:
        """Simulate guardian system effectiveness"""
        base = 0.9
        noise = random.uniform(-0.05, 0.05)
        if random.random() < 0.02:  # 2% chance of guardian issues
            noise -= 0.5
        return max(0.0, min(1.0, base + noise))

    def _get_protection_coverage(self) -> float:
        """Simulate protection coverage"""
        return random.uniform(0.85, 0.95)

    def _get_response_capability(self) -> float:
        """Simulate response capability"""
        return random.uniform(0.8, 0.95)

    def _get_trinity_component_health(self, component: str) -> float:
        """Get Trinity Framework component health"""
        if component == "identity":
            return self._get_identity_coherence()
        elif component == "consciousness":
            return self._get_consciousness_stability()
        elif component == "guardian":
            return self._get_guardian_effectiveness()
        return 0.5

    def _calculate_trinity_sync(self) -> float:
        """Calculate Trinity Framework synchronization"""
        identity_health = self._get_trinity_component_health("identity")
        consciousness_health = self._get_trinity_component_health("consciousness")
        guardian_health = self._get_trinity_component_health("guardian")

        # Calculate synchronization based on component balance
        avg_health = (identity_health + consciousness_health + guardian_health) / 3
        variance = max(
            abs(identity_health - avg_health),
            abs(consciousness_health - avg_health),
            abs(guardian_health - avg_health)
        )

        return max(0.0, 1.0 - variance * 2)  # Lower sync if components are unbalanced

    def _get_current_entropy(self) -> float:
        """Simulate entropy reading with governance factor"""
        base = 0.3
        noise = random.uniform(-0.1, 0.1)

        # Higher entropy if governance is poor
        governance_factor = (1.0 - self._get_governance_health()) * 0.2

        if random.random() < 0.03:  # 3% chance of spike
            noise += 0.3

        return max(0.0, min(1.0, base + noise + governance_factor))

    def _calculate_drift_rate(self) -> float:
        """Calculate consciousness drift rate"""
        if len(self.consciousness_history) < 2:
            return 0.0

        recent = list(self.consciousness_history)[-10:]
        if len(recent) < 2:
            return 0.0

        values = [entry["stability"] for entry in recent]
        return abs(values[-1] - values[0]) / len(values)

    def _calculate_entropy_velocity(self) -> float:
        """Calculate entropy change velocity"""
        if len(self.entropy_history) < 2:
            return 0.0

        recent = list(self.entropy_history)[-5:]
        if len(recent) < 2:
            return 0.0

        values = [entry["entropy"] for entry in recent]
        return (values[-1] - values[0]) / len(values)

    def _get_entropy_stability(self) -> float:
        """Get entropy stability metric"""
        return random.uniform(0.6, 0.9)

    def _get_memory_fragmentation(self) -> float:
        """Simulate memory fragmentation reading"""
        base = 0.2
        noise = random.uniform(-0.05, 0.05)
        if random.random() < 0.02:  # 2% chance of fragmentation
            noise += 0.5
        return max(0.0, min(1.0, base + noise))

    def _get_memory_coherence(self) -> float:
        """Simulate memory coherence reading"""
        return 1.0 - self._get_memory_fragmentation()

    def _get_fold_integrity(self) -> float:
        """Simulate fold chain integrity"""
        return random.uniform(0.85, 0.98)

    def _get_pattern_coherence(self) -> float:
        """Simulate pattern coherence reading"""
        base = 0.8
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.04:  # 4% chance of disruption
            noise -= 0.4
        return max(0.0, min(1.0, base + noise))

    def _get_pattern_stability(self) -> float:
        """Simulate pattern stability reading"""
        return random.uniform(0.6, 0.9)

    def _get_symbolic_pattern_integrity(self) -> float:
        """Simulate symbolic pattern integrity"""
        return random.uniform(0.8, 0.95)

    def _get_average_response_time(self) -> float:
        """Simulate response time reading"""
        base = 0.5
        noise = random.uniform(-0.1, 0.1)
        if random.random() < 0.03:  # 3% chance of spike
            noise += 2.0
        return max(0.1, base + noise)

    def _get_current_error_rate(self) -> float:
        """Simulate error rate reading"""
        base = 0.01
        noise = random.uniform(-0.005, 0.005)
        if random.random() < 0.02:  # 2% chance of spike
            noise += 0.1
        return max(0.0, min(1.0, base + noise))

    def _get_system_throughput(self) -> float:
        """Simulate system throughput"""
        return random.uniform(80, 100)  # Percentage of capacity

    def _get_sla_compliance(self) -> float:
        """Simulate SLA compliance"""
        return random.uniform(0.95, 0.99)

    # Enhanced response action implementations

    async def _stabilize_consciousness(self, threat: ThreatIndicator):
        """Stabilize consciousness system with governance validation"""
        logger.info("🧠 Stabilizing consciousness system with governance oversight")
        await asyncio.sleep(1)
        await self._log_governance_action(
            "consciousness_stabilized",
            {"threat_id": threat.threat_id, "action_successful": True}
        )

    async def _activate_governance_recovery(self, threat: ThreatIndicator):
        """Activate governance system recovery"""
        logger.critical("🛡️ Activating governance recovery protocols")
        await asyncio.sleep(2)
        await self._log_governance_action(
            "governance_recovery_activated",
            {"threat_id": threat.threat_id, "recovery_initiated": True}
        )

    async def _secure_identity_systems(self, threat: ThreatIndicator):
        """Secure identity systems"""
        logger.critical("⚛️ Securing identity systems")
        await asyncio.sleep(1.5)
        await self._log_governance_action(
            "identity_systems_secured",
            {"threat_id": threat.threat_id, "security_enhanced": True}
        )

    async def _resynchronize_trinity_framework(self, threat: ThreatIndicator):
        """Resynchronize Trinity Framework components"""
        logger.info("⚛️🧠🛡️ Resynchronizing Trinity Framework")
        await asyncio.sleep(3)
        await self._log_governance_action(
            "trinity_resynchronized",
            {"threat_id": threat.threat_id, "synchronization_restored": True}
        )

    async def _immediate_system_halt(self, threat: ThreatIndicator):
        """Immediate system halt for emergency situations"""
        logger.critical("🛑 IMMEDIATE SYSTEM HALT INITIATED")
        await asyncio.sleep(0.5)
        await self._log_governance_action(
            "system_halt_executed",
            {"threat_id": threat.threat_id, "halt_reason": threat.threat_type, "emergency_level": True}
        )

    async def _emergency_system_lockdown(self, threat: ThreatIndicator):
        """Emergency system lockdown"""
        logger.critical("🔒 EMERGENCY SYSTEM LOCKDOWN")
        await asyncio.sleep(1)
        await self._log_governance_action(
            "emergency_lockdown_executed",
            {"threat_id": threat.threat_id, "lockdown_reason": threat.threat_type}
        )

    # Continue with other action implementations...
    async def _reduce_entropy(self, threat: ThreatIndicator):
        """Reduce system entropy"""
        logger.info("❄️ Reducing system entropy")
        await asyncio.sleep(1)

    async def _defragment_memory(self, threat: ThreatIndicator):
        """Defragment memory structures"""
        logger.info("🧩 Defragmenting memory")
        await asyncio.sleep(2)

    async def _reinforce_patterns(self, threat: ThreatIndicator):
        """Reinforce pattern recognition"""
        logger.info("🔄 Reinforcing patterns")
        await asyncio.sleep(1)

    async def _optimize_performance(self, threat: ThreatIndicator):
        """Optimize system performance"""
        logger.info("⚡ Optimizing performance")
        await asyncio.sleep(1)

    async def _activate_emergency(self, threat: ThreatIndicator):
        """Activate emergency protocols"""
        logger.critical("🚨 EMERGENCY PROTOCOLS ACTIVATED")
        await asyncio.sleep(0.5)

    async def _escalate_to_humans(self, threat: ThreatIndicator):
        """Escalate to human operators"""
        logger.critical("👤 ESCALATING TO HUMAN OPERATORS")
        await asyncio.sleep(0.5)

    async def _cleanup_old_data(self):
        """Clean up old monitoring data with governance retention policies"""
        while self.is_monitoring:
            try:
                # Clean up old threat history (keep last 1000)
                if len(self.threat_history) > 1000:
                    self.threat_history = self.threat_history[-1000:]

                # Clean up old governance logs (keep last 5000)
                if len(self.governance_log) > 5000:
                    self.governance_log = self.governance_log[-5000:]

                await asyncio.sleep(3600)  # Clean up every hour

            except Exception as e:
                logger.error(f"Data cleanup error: {e}")
                await asyncio.sleep(3600)

    async def _log_governance_action(self, action: str, metadata: dict):
        """Log action in governance audit system"""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "metadata": metadata,
            "source": "enhanced_threat_monitor",
            "governance_context": {
                "monitoring_enabled": self.is_monitoring,
                "governance_enabled": self.governance_enabled,
                "trinity_framework_active": True
            }
        }

        self.governance_log.append(log_entry)

        # TODO: Forward to main governance audit system
        logger.debug(f"🔍 Enhanced governance action logged: {action}")

    # Enhanced public API methods

    async def health_check(self) -> bool:
        """Perform comprehensive health check including governance"""
        monitoring_healthy = self.is_monitoring and len(self.monitoring_tasks) > 0
        governance_healthy = self._get_governance_health() > 0.8
        trinity_healthy = self.detection_stats["trinity_framework_health"] > 0.7

        return monitoring_healthy and governance_healthy and trinity_healthy

    def get_enhanced_threat_summary(self) -> dict:
        """Get comprehensive threat summary with governance and Trinity Framework data"""
        active_by_severity = {}
        for level in ThreatLevel:
            active_by_severity[level.name] = len([
                t for t in self.active_threats if t.severity == level
            ])

        # Categorize threats by type
        governance_threats = len([t for t in self.active_threats if t.threat_type.startswith("governance")])
        ethics_threats = len([t for t in self.active_threats if t.threat_type == "ethics_violation"])
        trinity_threats = len([t for t in self.active_threats if t.threat_type == "trinity_desync"])

        return {
            "monitoring_active": self.is_monitoring,
            "governance_enabled": self.governance_enabled,
            "active_threats": len(self.active_threats),
            "total_threats_detected": self.detection_stats["total_threats"],
            "threats_by_severity": active_by_severity,
            "governance_threats": governance_threats,
            "ethics_threats": ethics_threats,
            "trinity_threats": trinity_threats,
            "recent_threats": [
                {
                    "type": t.threat_type,
                    "severity": t.severity.name,
                    "confidence": t.confidence,
                    "timestamp": t.timestamp,
                    "symbolic": "".join(t.symbolic_signature),
                    "trinity_impact": t.trinity_impact,
                    "governance_metadata": t.governance_metadata
                }
                for t in self.active_threats[-5:]
            ],
            "detection_accuracy": self.detection_stats["detection_accuracy"],
            "governance_interventions": self.detection_stats["governance_interventions"],
            "ethics_violations_prevented": self.detection_stats["ethics_violations_prevented"],
            "trinity_framework_health": self.detection_stats["trinity_framework_health"]
        }

    def get_enhanced_system_metrics(self) -> dict:
        """Get comprehensive system metrics including governance and Trinity Framework"""
        current_time = time.time()

        # Get latest readings from all monitoring systems
        latest_consciousness = list(self.consciousness_history)[-1] if self.consciousness_history else None
        latest_entropy = list(self.entropy_history)[-1] if self.entropy_history else None
        latest_memory = list(self.memory_history)[-1] if self.memory_history else None
        latest_patterns = list(self.pattern_history)[-1] if self.pattern_history else None
        latest_performance = list(self.response_time_history)[-1] if self.response_time_history else None
        latest_governance = list(self.governance_history)[-1] if self.governance_history else None
        latest_identity = list(self.identity_history)[-1] if self.identity_history else None
        latest_guardian = list(self.guardian_history)[-1] if self.guardian_history else None

        return {
            "timestamp": current_time,
            "consciousness": {
                "stability": latest_consciousness["stability"] if latest_consciousness else 0.0,
                "drift_rate": latest_consciousness["drift_rate"] if latest_consciousness else 0.0,
                "coherence": latest_consciousness.get("coherence", 0.0) if latest_consciousness else 0.0,
                "trinity_alignment": latest_consciousness.get("trinity_alignment", 0.0) if latest_consciousness else 0.0
            },
            "entropy": {
                "level": latest_entropy["entropy"] if latest_entropy else 0.0,
                "velocity": latest_entropy["velocity"] if latest_entropy else 0.0,
                "stability": latest_entropy.get("stability", 0.0) if latest_entropy else 0.0
            },
            "memory": {
                "fragmentation": latest_memory["fragmentation"] if latest_memory else 0.0,
                "coherence": latest_memory["coherence"] if latest_memory else 1.0,
                "fold_integrity": latest_memory.get("fold_integrity", 1.0) if latest_memory else 1.0
            },
            "patterns": {
                "coherence": latest_patterns["coherence"] if latest_patterns else 1.0,
                "stability": latest_patterns["stability"] if latest_patterns else 1.0,
                "symbolic_integrity": latest_patterns.get("symbolic_integrity", 1.0) if latest_patterns else 1.0
            },
            "performance": {
                "response_time": latest_performance["response_time"] if latest_performance else 0.0,
                "error_rate": latest_performance["error_rate"] if latest_performance else 0.0,
                "throughput": latest_performance.get("throughput", 100.0) if latest_performance else 100.0,
                "sla_compliance": latest_performance.get("sla_compliance", 1.0) if latest_performance else 1.0
            },
            "governance": {
                "health": latest_governance["health"] if latest_governance else 1.0,
                "ethics_compliance": latest_governance["ethics_compliance"] if latest_governance else 1.0,
                "policy_alignment": latest_governance["policy_alignment"] if latest_governance else 1.0,
                "oversight_effectiveness": latest_governance["oversight_effectiveness"] if latest_governance else 1.0
            },
            "trinity_framework": {
                "identity": {
                    "coherence": latest_identity["coherence"] if latest_identity else 1.0,
                    "authentication_health": latest_identity["authentication_health"] if latest_identity else 1.0,
                    "symbolic_integrity": latest_identity["symbolic_integrity"] if latest_identity else 1.0,
                    "trinity_alignment": latest_identity["trinity_alignment"] if latest_identity else 1.0
                },
                "consciousness": {
                    "stability": latest_consciousness["stability"] if latest_consciousness else 1.0,
                    "coherence": latest_consciousness.get("coherence", 1.0) if latest_consciousness else 1.0,
                    "trinity_alignment": latest_consciousness.get("trinity_alignment", 1.0) if latest_consciousness else 1.0
                },
                "guardian": {
                    "effectiveness": latest_guardian["effectiveness"] if latest_guardian else 1.0,
                    "protection_coverage": latest_guardian["protection_coverage"] if latest_guardian else 1.0,
                    "response_capability": latest_guardian["response_capability"] if latest_guardian else 1.0,
                    "trinity_alignment": latest_guardian["trinity_alignment"] if latest_guardian else 1.0
                },
                "synchronization": self._calculate_trinity_sync(),
                "overall_health": self.detection_stats["trinity_framework_health"]
            }
        }


if __name__ == "__main__":
    async def demo():
        """Demo enhanced threat monitoring with governance"""
        print("🔍 Enhanced Threat Monitor with Governance Demo")
        print("=" * 50)

        monitor = EnhancedThreatMonitor(
            alert_threshold=0.6,
            monitoring_interval=2,
            governance_enabled=True
        )

        try:
            # Start monitoring
            await monitor.start_monitoring()
            print("✅ Enhanced monitoring started with governance integration")

            # Run for 30 seconds
            for i in range(15):
                await asyncio.sleep(2)

                summary = monitor.get_enhanced_threat_summary()
                metrics = monitor.get_enhanced_system_metrics()

                print(f"\n⏱️  Check {i+1}/15:")
                print(f"   Active threats: {summary['active_threats']} (Gov: {summary['governance_threats']}, Ethics: {summary['ethics_threats']})")
                print(f"   Consciousness: {metrics['consciousness']['stability']:.2f}")
                print(f"   Governance Health: {metrics['governance']['health']:.2f}")
                print(f"   Trinity Sync: {metrics['trinity_framework']['synchronization']:.2f}")
                print(f"   Ethics Compliance: {metrics['governance']['ethics_compliance']:.2f}")

                if summary['active_threats'] > 0:
                    for threat in summary['recent_threats']:
                        impact = threat['trinity_impact']
                        print(f"   🚨 {threat['type']} ({threat['severity']}) {threat['symbolic']} [I:{impact.get('identity',0):.1f}C:{impact.get('consciousness',0):.1f}G:{impact.get('guardian',0):.1f}]")

            # Final summary
            final_summary = monitor.get_enhanced_threat_summary()
            print("\n📊 Final Enhanced Summary:")
            print(f"   Total threats detected: {final_summary['total_threats_detected']}")
            print(f"   Governance interventions: {final_summary['governance_interventions']}")
            print(f"   Ethics violations prevented: {final_summary['ethics_violations_prevented']}")
            print(f"   Detection accuracy: {final_summary['detection_accuracy']:.2f}")
            print(f"   Trinity Framework health: {final_summary['trinity_framework_health']:.2f}")

        finally:
            await monitor.stop_monitoring()
            print("\n🛑 Enhanced monitoring stopped")

    asyncio.run(demo())
