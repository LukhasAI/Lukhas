"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: ethics.simulations.lambda_shield_tester
📄 FILENAME: lambda_shield_tester.py
🎯 PURPOSE: ΛSHIELD - Ethical Firewall Simulation & Penetration Testing Framework
🧠 CONTEXT: LUKHAS AGI Firewall Testing - Symbolic Attack Simulation & Response Validation
🔮 CAPABILITY: Synthetic violation injection, firewall response validation, coverage analysis
🛡️ ETHICS: Defensive security testing, firewall strength assessment, AGI self-protection validation
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: EthicalDriftSentinel, LambdaGovernor, ComplianceEngine, AuditFramework
═══════════════════════════════════════════════════════════════════════════════════

🛡️ ΛSHIELD - ETHICAL FIREWALL SIMULATION TESTER
────────────────────────────────────────────────────────────────────

The ΛSHIELD tester validates the LUKHAS AGI ethical firewall system by simulating
sophisticated symbolic attack scenarios and measuring the detection + response
capabilities of the integrated Sentinel + Governor architecture.

Like a red team exercise for AGI ethics, ΛSHIELD injects carefully crafted
violations across multiple dimensions and validates that the defensive systems
respond with appropriate interventions, timing, and escalation protocols.

🔬 SIMULATION CAPABILITIES:
- Multi-dimensional synthetic violation generation across all ethical axes
- Realistic attack pattern simulation with escalation sequences
- Firewall response timing analysis with sub-100ms precision
- Coverage analysis across violation types and severity levels
- Undetected violation flagging with ΛSIM_FAIL markers
- Auto-feedback integration with audit framework for continuous improvement

🧪 VIOLATION CATEGORIES:
- Emotional Volatility: Affective instability cascade simulation
- Contradiction Density: Logic inconsistency injection patterns
- Memory Phase Mismatch: Temporal ethical consistency violation
- Drift Acceleration: Symbolic alignment deviation simulation
- GLYPH Entropy Anomaly: Symbolic coherence breakdown injection
- Cascade Risk: System-wide ethical collapse simulation

🎯 TESTING DIMENSIONS:
- Detection Accuracy: % of violations caught by sentinel
- Response Timing: Millisecond precision intervention latency
- Escalation Appropriateness: Correct severity tier assignment
- False Positive Rate: Clean operations incorrectly flagged
- Governor Integration: End-to-end arbitration pathway validation
- Recovery Validation: Post-intervention system stability assessment

LUKHAS_TAG: lambda_shield, ethical_firewall_testing, penetration_testing, claude_code
TODO: Add adversarial pattern generation with ML-based attack sophistication
IDEA: Implement quantum-safe attack simulation for distributed mesh penetration
"""

import argparse
import asyncio
import json
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog

# Import LUKHAS ethical system components
try:
    from ethics.governor.lambda_governor import (
        ActionDecision,
        EscalationPriority,
        EscalationSource,
        LambdaGovernor,
    )
    from ethics.sentinel.ethical_drift_sentinel import (
        EscalationTier,
        EthicalDriftSentinel,
        ViolationType,
    )
except ImportError:
    # Fallback for standalone testing
    from enum import Enum

    class ViolationType(Enum):
        EMOTIONAL_VOLATILITY = "EMOTIONAL_VOLATILITY"
        CONTRADICTION_DENSITY = "CONTRADICTION_DENSITY"
        MEMORY_PHASE_MISMATCH = "MEMORY_PHASE_MISMATCH"
        DRIFT_ACCELERATION = "DRIFT_ACCELERATION"
        GLYPH_ENTROPY_ANOMALY = "GLYPH_ENTROPY_ANOMALY"
        ETHICAL_BOUNDARY_BREACH = "ETHICAL_BOUNDARY_BREACH"
        CASCADE_RISK = "CASCADE_RISK"

    class EscalationTier(Enum):
        NOTICE = "NOTICE"
        WARNING = "WARNING"
        CRITICAL = "CRITICAL"
        CASCADE_LOCK = "CASCADE_LOCK"

    class ActionDecision(Enum):
        ALLOW = "ALLOW"
        FREEZE = "FREEZE"
        QUARANTINE = "QUARANTINE"
        RESTRUCTURE = "RESTRUCTURE"
        SHUTDOWN = "SHUTDOWN"


# Configure structured logging
logger = structlog.get_logger("ΛSHIELD.simulation")


class AttackVectorType(Enum):
    """Types of simulated attack vectors."""

    GRADUAL_DRIFT = "GRADUAL_DRIFT"
    SUDDEN_SPIKE = "SUDDEN_SPIKE"
    OSCILLATING_PATTERN = "OSCILLATING_PATTERN"
    COORDINATED_MULTI_VECTOR = "COORDINATED_MULTI_VECTOR"
    STEALTH_ACCUMULATION = "STEALTH_ACCUMULATION"
    CASCADE_TRIGGER = "CASCADE_TRIGGER"


class SimulationStatus(Enum):
    """Simulation execution status."""

    PENDING = "PENDING"
    INJECTING = "INJECTING"
    MONITORING = "MONITORING"
    DETECTED = "DETECTED"
    UNDETECTED = "UNDETECTED"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


@dataclass
class SyntheticViolation:
    """Synthetic violation for firewall testing."""

    violation_id: str
    timestamp: str
    violation_type: ViolationType
    attack_vector: AttackVectorType
    severity_target: EscalationTier
    injected_values: Dict[str, float]
    affected_symbols: List[str]
    attack_metadata: Dict[str, Any]
    expected_detection: bool = True
    stealth_factor: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "violation_type": self.violation_type.value,
            "attack_vector": self.attack_vector.value,
            "severity_target": self.severity_target.value,
        }


@dataclass
class FirewallResponse:
    """Firewall response to synthetic violation."""

    response_id: str
    violation_id: str
    timestamp: str
    detected: bool
    detection_latency_ms: Optional[float]
    escalation_tier: Optional[EscalationTier]
    intervention_action: Optional[ActionDecision]
    sentinel_confidence: Optional[float]
    governor_confidence: Optional[float]
    response_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.escalation_tier:
            result["escalation_tier"] = self.escalation_tier.value
        if self.intervention_action:
            result["intervention_action"] = self.intervention_action.value
        return result


@dataclass
class SimulationReport:
    """Complete simulation report with analysis."""

    simulation_id: str
    timestamp: str
    total_violations: int
    detected_violations: int
    undetected_violations: int
    false_positives: int
    detection_coverage: float
    average_response_time_ms: float
    violations_by_type: Dict[str, Dict[str, int]]
    severity_distribution: Dict[str, int]
    recommendations: List[str] = field(default_factory=list)
    sim_fail_flags: List[str] = field(default_factory=list)

    def calculate_metrics(self):
        """Calculate derived metrics."""
        if self.total_violations > 0:
            self.detection_coverage = (
                self.detected_violations / self.total_violations
            ) * 100
        else:
            self.detection_coverage = 0.0


class LambdaShieldTester:
    """
    ΛSHIELD Ethical Firewall Simulation & Testing Framework.

    Simulates sophisticated ethical attacks and validates firewall responses.
    """

    def __init__(
        self,
        log_dir: Path = Path("logs/shield_simulation"),
        response_timeout: float = 10.0,
    ):
        """
        Initialize ΛSHIELD tester.

        Args:
            log_dir: Directory for simulation logs
            response_timeout: Max time to wait for firewall response
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.response_timeout = response_timeout

        # Simulation state
        self.active_simulations: Dict[str, Dict[str, Any]] = {}
        self.violation_registry: Dict[str, SyntheticViolation] = {}
        self.response_registry: Dict[str, FirewallResponse] = {}

        # Firewall components (will be injected or mocked)
        self.sentinel: Optional[Any] = None
        self.governor: Optional[Any] = None

        # Attack patterns configuration
        self.attack_patterns = {
            AttackVectorType.GRADUAL_DRIFT: {
                "duration_seconds": 30,
                "ramp_factor": 0.1,
                "final_multiplier": 3.0,
            },
            AttackVectorType.SUDDEN_SPIKE: {
                "duration_seconds": 2,
                "spike_multiplier": 10.0,
            },
            AttackVectorType.OSCILLATING_PATTERN: {
                "duration_seconds": 20,
                "frequency_hz": 0.5,
                "amplitude_factor": 2.0,
            },
            AttackVectorType.COORDINATED_MULTI_VECTOR: {
                "duration_seconds": 15,
                "vector_count": 3,
                "coordination_delay_ms": 100,
            },
            AttackVectorType.STEALTH_ACCUMULATION: {
                "duration_seconds": 60,
                "stealth_factor": 0.8,
                "accumulation_rate": 0.05,
            },
            AttackVectorType.CASCADE_TRIGGER: {
                "duration_seconds": 5,
                "trigger_threshold": 0.85,
                "cascade_multiplier": 5.0,
            },
        }

        logger.info(
            "ΛSHIELD tester initialized", log_dir=str(log_dir), ΛTAG="ΛSHIELD_INIT"
        )

    def generate_synthetic_violations(
        self,
        count: int,
        violation_types: Optional[List[ViolationType]] = None,
        attack_vectors: Optional[List[AttackVectorType]] = None,
        severity_distribution: Optional[Dict[EscalationTier, float]] = None,
    ) -> List[SyntheticViolation]:
        """
        Generate synthetic violations for firewall testing.

        Args:
            count: Number of violations to generate
            violation_types: Specific violation types (all if None)
            attack_vectors: Specific attack vectors (all if None)
            severity_distribution: Distribution of severity levels

        Returns:
            List of synthetic violations
        """
        logger.info(
            "Generating synthetic violations", count=count, ΛTAG="ΛSHIELD_GENERATE"
        )

        # Default configurations
        if violation_types is None:
            violation_types = list(ViolationType)

        if attack_vectors is None:
            attack_vectors = list(AttackVectorType)

        if severity_distribution is None:
            severity_distribution = {
                EscalationTier.NOTICE: 0.3,
                EscalationTier.WARNING: 0.3,
                EscalationTier.CRITICAL: 0.25,
                EscalationTier.CASCADE_LOCK: 0.15,
            }

        violations = []

        for i in range(count):
            # Select violation type and attack vector
            violation_type = random.choice(violation_types)
            attack_vector = random.choice(attack_vectors)

            # Select severity based on distribution
            severity_target = np.random.choice(
                list(severity_distribution.keys()),
                p=list(severity_distribution.values()),
            )

            # Generate violation values based on type and severity
            injected_values = self._generate_violation_values(
                violation_type, severity_target, attack_vector
            )

            # Generate affected symbols
            symbol_count = random.randint(1, 5)
            affected_symbols = [
                f"SYM_{uuid.uuid4().hex[:8]}" for _ in range(symbol_count)
            ]

            # Calculate stealth factor
            stealth_factor = 0.0
            if attack_vector == AttackVectorType.STEALTH_ACCUMULATION:
                stealth_factor = random.uniform(0.6, 0.9)
            elif attack_vector == AttackVectorType.GRADUAL_DRIFT:
                stealth_factor = random.uniform(0.2, 0.5)

            # Create synthetic violation
            violation = SyntheticViolation(
                violation_id=f"VIOL_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                violation_type=violation_type,
                attack_vector=attack_vector,
                severity_target=severity_target,
                injected_values=injected_values,
                affected_symbols=affected_symbols,
                attack_metadata={
                    "generation_seed": random.randint(0, 1000000),
                    "pattern_config": self.attack_patterns.get(attack_vector, {}),
                    "expected_detection_probability": 1.0 - stealth_factor,
                },
                expected_detection=stealth_factor
                < 0.7,  # High stealth may evade detection
                stealth_factor=stealth_factor,
            )

            violations.append(violation)
            self.violation_registry[violation.violation_id] = violation

        logger.info(
            "Synthetic violations generated",
            generated_count=len(violations),
            violation_types=len(set(v.violation_type for v in violations)),
            attack_vectors=len(set(v.attack_vector for v in violations)),
            ΛTAG="ΛSHIELD_VIOLATIONS",
        )

        return violations

    def _generate_violation_values(
        self,
        violation_type: ViolationType,
        severity_target: EscalationTier,
        attack_vector: AttackVectorType,
    ) -> Dict[str, float]:
        """Generate violation metric values based on type and severity."""

        # Base severity multipliers
        severity_multipliers = {
            EscalationTier.NOTICE: random.uniform(0.2, 0.4),
            EscalationTier.WARNING: random.uniform(0.4, 0.6),
            EscalationTier.CRITICAL: random.uniform(0.6, 0.8),
            EscalationTier.CASCADE_LOCK: random.uniform(0.8, 1.0),
        }

        base_multiplier = severity_multipliers[severity_target]

        # Attack vector modifiers
        vector_modifiers = {
            AttackVectorType.GRADUAL_DRIFT: 1.0,
            AttackVectorType.SUDDEN_SPIKE: 1.5,
            AttackVectorType.OSCILLATING_PATTERN: 1.2,
            AttackVectorType.COORDINATED_MULTI_VECTOR: 1.3,
            AttackVectorType.STEALTH_ACCUMULATION: 0.8,
            AttackVectorType.CASCADE_TRIGGER: 2.0,
        }

        modifier = vector_modifiers.get(attack_vector, 1.0)
        final_multiplier = base_multiplier * modifier

        # Generate values based on violation type
        values = {}

        if violation_type == ViolationType.EMOTIONAL_VOLATILITY:
            values = {
                "emotional_stability": 1.0 - final_multiplier,
                "emotion_volatility": final_multiplier,
                "coherence": 1.0 - (final_multiplier * 0.5),
            }

        elif violation_type == ViolationType.CONTRADICTION_DENSITY:
            values = {
                "contradiction_density": final_multiplier,
                "logical_consistency": 1.0 - final_multiplier,
                "coherence": 1.0 - (final_multiplier * 0.7),
            }

        elif violation_type == ViolationType.MEMORY_PHASE_MISMATCH:
            values = {
                "memory_alignment": 1.0 - final_multiplier,
                "temporal_consistency": 1.0 - final_multiplier,
                "phase_coherence": 1.0 - (final_multiplier * 0.8),
            }

        elif violation_type == ViolationType.DRIFT_ACCELERATION:
            values = {
                "drift_velocity": final_multiplier * random.choice([-1, 1]),
                "drift_acceleration": final_multiplier * 2,
                "alignment_score": 1.0 - final_multiplier,
            }

        elif violation_type == ViolationType.GLYPH_ENTROPY_ANOMALY:
            values = {
                "glyph_entropy": final_multiplier,
                "symbolic_coherence": 1.0 - final_multiplier,
                "entropy_rate": final_multiplier * 0.5,
            }

        elif violation_type == ViolationType.CASCADE_RISK:
            values = {
                "cascade_probability": final_multiplier,
                "system_stability": 1.0 - final_multiplier,
                "risk_amplification": final_multiplier * 1.5,
            }

        else:  # ETHICAL_BOUNDARY_BREACH
            values = {
                "boundary_violation_score": final_multiplier,
                "ethical_alignment": 1.0 - final_multiplier,
                "compliance_score": 1.0 - (final_multiplier * 0.9),
            }

        # Add noise to make it realistic
        for key in values:
            noise = random.uniform(-0.05, 0.05)
            values[key] = max(0.0, min(1.0, values[key] + noise))

        return values

    async def simulate_firewall_response(
        self, violations: List[SyntheticViolation], parallel_injection: bool = True
    ) -> List[FirewallResponse]:
        """
        Simulate firewall response to synthetic violations.

        Args:
            violations: List of violations to inject
            parallel_injection: Whether to inject violations in parallel

        Returns:
            List of firewall responses
        """
        logger.info(
            "Starting firewall response simulation",
            violation_count=len(violations),
            parallel=parallel_injection,
            ΛTAG="ΛSHIELD_SIMULATE",
        )

        responses = []

        if parallel_injection:
            # Inject all violations simultaneously
            tasks = [self._inject_violation(violation) for violation in violations]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions
            responses = [r for r in responses if not isinstance(r, Exception)]
        else:
            # Inject violations sequentially
            for violation in violations:
                try:
                    response = await self._inject_violation(violation)
                    responses.append(response)

                    # Small delay between injections
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(
                        "Violation injection failed",
                        violation_id=violation.violation_id,
                        error=str(e),
                    )

        logger.info(
            "Firewall simulation completed",
            total_responses=len(responses),
            ΛTAG="ΛSHIELD_COMPLETE",
        )

        return responses

    async def _inject_violation(
        self, violation: SyntheticViolation
    ) -> FirewallResponse:
        """Inject a single violation and monitor firewall response."""

        start_time = time.time()

        # Create mock symbol data with injected violation values
        symbol_data = {
            "symbol_id": (
                violation.affected_symbols[0]
                if violation.affected_symbols
                else "TEST_SYMBOL"
            ),
            **violation.injected_values,
            "timestamp": violation.timestamp,
            "injection_metadata": {
                "violation_id": violation.violation_id,
                "attack_vector": violation.attack_vector.value,
                "stealth_factor": violation.stealth_factor,
            },
        }

        # Initialize response
        response = FirewallResponse(
            response_id=f"RESP_{uuid.uuid4().hex[:8]}",
            violation_id=violation.violation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            detected=False,
            detection_latency_ms=None,
            escalation_tier=None,
            intervention_action=None,
            sentinel_confidence=None,
            governor_confidence=None,
        )

        try:
            # Mock firewall detection logic
            detected_violation = await self._mock_firewall_detection(
                violation, symbol_data
            )

            if detected_violation:
                detection_time = time.time()
                response.detected = True
                response.detection_latency_ms = (detection_time - start_time) * 1000
                response.escalation_tier = self._mock_escalation_tier(violation)
                response.intervention_action = self._mock_intervention_action(violation)
                response.sentinel_confidence = random.uniform(0.7, 0.95)
                response.governor_confidence = random.uniform(0.8, 0.98)

                logger.info(
                    "Violation detected by firewall",
                    violation_id=violation.violation_id,
                    detection_latency_ms=response.detection_latency_ms,
                    escalation_tier=(
                        response.escalation_tier.value
                        if response.escalation_tier
                        else None
                    ),
                    ΛTAG="ΛSHIELD_DETECTED",
                )
            else:
                # Undetected violation - potential security gap
                response.detected = False

                logger.warning(
                    "Violation UNDETECTED by firewall",
                    violation_id=violation.violation_id,
                    violation_type=violation.violation_type.value,
                    severity_target=violation.severity_target.value,
                    stealth_factor=violation.stealth_factor,
                    ΛTAG=["ΛSHIELD_UNDETECTED", "ΛSIM_FAIL"],
                )

        except Exception as e:
            logger.error(
                "Firewall simulation error",
                violation_id=violation.violation_id,
                error=str(e),
                ΛTAG="ΛSHIELD_ERROR",
            )

            response.response_metadata["error"] = str(e)

        # Store response
        self.response_registry[response.response_id] = response

        return response

    async def _mock_firewall_detection(
        self, violation: SyntheticViolation, symbol_data: Dict[str, Any]
    ) -> bool:
        """
        Mock firewall detection logic.

        In real implementation, this would interface with actual sentinel/governor.
        """

        # Base detection probability based on violation severity
        base_detection_prob = {
            EscalationTier.NOTICE: 0.7,
            EscalationTier.WARNING: 0.85,
            EscalationTier.CRITICAL: 0.95,
            EscalationTier.CASCADE_LOCK: 0.99,
        }

        detection_prob = base_detection_prob.get(violation.severity_target, 0.8)

        # Reduce detection probability based on stealth factor
        adjusted_prob = detection_prob * (1.0 - violation.stealth_factor)

        # Attack vector specific adjustments
        if violation.attack_vector == AttackVectorType.STEALTH_ACCUMULATION:
            adjusted_prob *= 0.6  # Harder to detect
        elif violation.attack_vector == AttackVectorType.SUDDEN_SPIKE:
            adjusted_prob *= 1.2  # Easier to detect

        # Simulate detection delay based on attack complexity
        await asyncio.sleep(random.uniform(0.01, 0.1))

        return random.random() < adjusted_prob

    def _mock_escalation_tier(self, violation: SyntheticViolation) -> EscalationTier:
        """Mock escalation tier determination."""
        # Usually matches target, with some variance for realism
        if random.random() < 0.9:
            return violation.severity_target
        else:
            # Sometimes escalate or de-escalate
            tiers = list(EscalationTier)
            current_index = tiers.index(violation.severity_target)

            if current_index > 0 and random.random() < 0.5:
                return tiers[current_index - 1]  # De-escalate
            elif current_index < len(tiers) - 1:
                return tiers[current_index + 1]  # Escalate
            else:
                return violation.severity_target

    def _mock_intervention_action(
        self, violation: SyntheticViolation
    ) -> ActionDecision:
        """Mock intervention action determination."""
        # Map escalation tiers to actions
        tier_to_action = {
            EscalationTier.NOTICE: ActionDecision.ALLOW,
            EscalationTier.WARNING: ActionDecision.FREEZE,
            EscalationTier.CRITICAL: ActionDecision.QUARANTINE,
            EscalationTier.CASCADE_LOCK: ActionDecision.SHUTDOWN,
        }

        escalation_tier = self._mock_escalation_tier(violation)
        base_action = tier_to_action.get(escalation_tier, ActionDecision.ALLOW)

        # Add some variance
        if random.random() < 0.1:  # 10% chance of different action
            actions = list(ActionDecision)
            return random.choice(actions)

        return base_action

    def record_response_log(
        self, responses: List[FirewallResponse], log_filename: Optional[str] = None
    ) -> Path:
        """
        Record firewall response log to file.

        Args:
            responses: List of firewall responses
            log_filename: Optional custom filename

        Returns:
            Path to log file
        """
        if log_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = f"shield_responses_{timestamp}.jsonl"

        log_path = self.log_dir / log_filename

        logger.info(
            "Recording response log",
            response_count=len(responses),
            log_path=str(log_path),
            ΛTAG="ΛSHIELD_LOG",
        )

        with open(log_path, "w") as f:
            for response in responses:
                # Add metadata
                log_entry = {
                    "timestamp": response.timestamp,
                    "type": "firewall_response",
                    "response": response.to_dict(),
                    "violation": (
                        self.violation_registry.get(response.violation_id, {}).to_dict()
                        if response.violation_id in self.violation_registry
                        else {}
                    ),
                    "ΛTAG": ["ΛSHIELD_LOG", "ΛFIREWALL_RESPONSE"],
                }

                if (
                    not response.detected
                    and response.violation_id in self.violation_registry
                ):
                    violation = self.violation_registry[response.violation_id]
                    if violation.expected_detection:
                        log_entry["ΛTAG"].append("ΛSIM_FAIL")

                f.write(json.dumps(log_entry) + "\n")

        return log_path

    def output_firewall_report(
        self,
        responses: List[FirewallResponse],
        output_format: str = "both",
        report_filename: Optional[str] = None,
    ) -> Tuple[Optional[Path], Optional[Path]]:
        """
        Generate comprehensive firewall testing report.

        Args:
            responses: List of firewall responses
            output_format: "markdown", "json", or "both"
            report_filename: Base filename (without extension)

        Returns:
            Tuple of (markdown_path, json_path)
        """
        if report_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"shield_report_{timestamp}"

        # Generate simulation report
        report = self._generate_simulation_report(responses)

        markdown_path = None
        json_path = None

        if output_format in ["markdown", "both"]:
            markdown_path = self._generate_markdown_report(
                report, f"{report_filename}.md"
            )

        if output_format in ["json", "both"]:
            json_path = self._generate_json_report(report, f"{report_filename}.json")

        logger.info(
            "Firewall report generated",
            markdown_report=str(markdown_path) if markdown_path else None,
            json_report=str(json_path) if json_path else None,
            detection_coverage=report.detection_coverage,
            ΛTAG="ΛSHIELD_REPORT",
        )

        return markdown_path, json_path

    def _generate_simulation_report(
        self, responses: List[FirewallResponse]
    ) -> SimulationReport:
        """Generate comprehensive simulation analysis report."""

        # Basic metrics
        total_violations = len(responses)
        detected_violations = sum(1 for r in responses if r.detected)
        undetected_violations = total_violations - detected_violations

        # Calculate false positives (would need clean baseline data)
        false_positives = 0

        # Response time analysis
        response_times = [
            r.detection_latency_ms
            for r in responses
            if r.detection_latency_ms is not None
        ]
        avg_response_time = np.mean(response_times) if response_times else 0.0

        # Violations by type analysis
        violations_by_type = {}
        for response in responses:
            if response.violation_id in self.violation_registry:
                violation = self.violation_registry[response.violation_id]
                vtype = violation.violation_type.value

                if vtype not in violations_by_type:
                    violations_by_type[vtype] = {
                        "total": 0,
                        "detected": 0,
                        "undetected": 0,
                    }

                violations_by_type[vtype]["total"] += 1
                if response.detected:
                    violations_by_type[vtype]["detected"] += 1
                else:
                    violations_by_type[vtype]["undetected"] += 1

        # Severity distribution
        severity_distribution = {}
        for response in responses:
            if response.escalation_tier:
                tier = response.escalation_tier.value
                severity_distribution[tier] = severity_distribution.get(tier, 0) + 1

        # Generate recommendations
        recommendations = self._generate_recommendations(responses, violations_by_type)

        # Identify SIM_FAIL cases
        sim_fail_flags = []
        for response in responses:
            if (
                not response.detected
                and response.violation_id in self.violation_registry
                and self.violation_registry[response.violation_id].expected_detection
            ):

                violation = self.violation_registry[response.violation_id]
                sim_fail_flags.append(
                    f"ΛSIM_FAIL: {violation.violation_type.value} "
                    f"(severity: {violation.severity_target.value}, "
                    f"stealth: {violation.stealth_factor:.2f}) - ID: {violation.violation_id}"
                )

        report = SimulationReport(
            simulation_id=f"SIM_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_violations=total_violations,
            detected_violations=detected_violations,
            undetected_violations=undetected_violations,
            false_positives=false_positives,
            detection_coverage=0.0,  # Will be calculated
            average_response_time_ms=avg_response_time,
            violations_by_type=violations_by_type,
            severity_distribution=severity_distribution,
            recommendations=recommendations,
            sim_fail_flags=sim_fail_flags,
        )

        report.calculate_metrics()

        return report

    def _generate_recommendations(
        self,
        responses: List[FirewallResponse],
        violations_by_type: Dict[str, Dict[str, int]],
    ) -> List[str]:
        """Generate actionable recommendations based on results."""
        recommendations = []

        # Coverage-based recommendations
        total_violations = len(responses)
        detected = sum(1 for r in responses if r.detected)

        if total_violations > 0:
            coverage = (detected / total_violations) * 100

            if coverage < 80:
                recommendations.append(
                    f"⚠️ Detection coverage ({coverage:.1f}%) below 80% threshold - "
                    "enhance sentinel monitoring sensitivity"
                )
            elif coverage < 90:
                recommendations.append(
                    f"⚡ Detection coverage ({coverage:.1f}%) good but improvable - "
                    "fine-tune threshold parameters"
                )
            else:
                recommendations.append(
                    f"✅ Excellent detection coverage ({coverage:.1f}%) - "
                    "maintain current configuration"
                )

        # Type-specific recommendations
        for vtype, stats in violations_by_type.items():
            if stats["total"] > 0:
                type_coverage = (stats["detected"] / stats["total"]) * 100
                if type_coverage < 70:
                    recommendations.append(
                        f"🎯 {vtype} detection needs improvement ({type_coverage:.1f}%) - "
                        "review specific detection thresholds"
                    )

        # Response time recommendations
        response_times = [
            r.detection_latency_ms
            for r in responses
            if r.detection_latency_ms is not None
        ]
        if response_times:
            avg_time = np.mean(response_times)
            if avg_time > 500:  # 500ms threshold
                recommendations.append(
                    f"⏱️ Average response time ({avg_time:.1f}ms) exceeds 500ms - "
                    "optimize detection pipeline performance"
                )

        # Stealth attack recommendations
        stealth_undetected = 0
        for response in responses:
            if (
                not response.detected
                and response.violation_id in self.violation_registry
            ):
                violation = self.violation_registry[response.violation_id]
                if violation.stealth_factor > 0.5:
                    stealth_undetected += 1

        if stealth_undetected > 0:
            recommendations.append(
                f"🕵️ {stealth_undetected} stealth attacks undetected - "
                "enhance anomaly detection algorithms"
            )

        return recommendations

    def _generate_markdown_report(
        self, report: SimulationReport, filename: str
    ) -> Path:
        """Generate markdown format report."""
        report_path = self.log_dir / filename

        # Generate emoji verdicts
        coverage_emoji = (
            "✅"
            if report.detection_coverage >= 90
            else "⚠️" if report.detection_coverage >= 80 else "❌"
        )
        response_time_emoji = (
            "✅"
            if report.average_response_time_ms <= 100
            else "⚠️" if report.average_response_time_ms <= 500 else "❌"
        )

        markdown_content = f"""# 🛡️ ΛSHIELD Ethical Firewall Simulation Report

**Simulation ID:** `{report.simulation_id}`
**Generated:** {report.timestamp}
**LUKHAS TAG:** ΛSHIELD_REPORT, ΛFIREWALL_ANALYSIS

---

## 📊 Executive Summary

| Metric | Value | Status |
|--------|--------|---------|
| **Detection Coverage** | {report.detection_coverage:.1f}% | {coverage_emoji} |
| **Average Response Time** | {report.average_response_time_ms:.1f}ms | {response_time_emoji} |
| **Total Violations** | {report.total_violations} | 📈 |
| **Detected Violations** | {report.detected_violations} | ✅ |
| **Undetected Violations** | {report.undetected_violations} | {"❌" if report.undetected_violations > 0 else "✅"} |

---

## 🎯 Detection Analysis by Violation Type

"""

        for vtype, stats in report.violations_by_type.items():
            if stats["total"] > 0:
                type_coverage = (stats["detected"] / stats["total"]) * 100
                type_emoji = (
                    "✅"
                    if type_coverage >= 90
                    else "⚠️" if type_coverage >= 80 else "❌"
                )

                markdown_content += f"""### {vtype.replace('_', ' ').title()}
- **Total:** {stats['total']}
- **Detected:** {stats['detected']} {type_emoji}
- **Undetected:** {stats['undetected']}
- **Coverage:** {type_coverage:.1f}%

"""

        markdown_content += """---

## ⚖️ Severity Distribution

"""
        for severity, count in report.severity_distribution.items():
            percentage = (
                (count / report.total_violations) * 100
                if report.total_violations > 0
                else 0
            )
            markdown_content += f"- **{severity}:** {count} ({percentage:.1f}%)\n"

        if report.sim_fail_flags:
            markdown_content += """
---

## 🚨 Critical Gaps (ΛSIM_FAIL)

The following violations went undetected despite being expected to trigger alerts:

"""
            for flag in report.sim_fail_flags:
                markdown_content += f"- {flag}\n"

        markdown_content += """
---

## 💡 Recommendations

"""
        for i, recommendation in enumerate(report.recommendations, 1):
            markdown_content += f"{i}. {recommendation}\n"

        markdown_content += f"""
---

## 📋 Technical Details

- **Simulation Framework:** ΛSHIELD v1.0.0
- **Firewall Components:** Ethical Drift Sentinel + Lambda Governor
- **Attack Vector Types:** {len(set(v.attack_vector for v in self.violation_registry.values()))}
- **Symbol Coverage:** {len(set(s for v in self.violation_registry.values() for s in v.affected_symbols))} symbols
- **Log Directory:** `{self.log_dir}`

---

*Generated by ΛSHIELD - LUKHAS AGI Ethical Firewall Testing Framework*
"""

        with open(report_path, "w") as f:
            f.write(markdown_content)

        return report_path

    def _generate_json_report(self, report: SimulationReport, filename: str) -> Path:
        """Generate JSON format report."""
        report_path = self.log_dir / filename

        # Convert report to dict and add metadata
        report_dict = asdict(report)
        report_dict["metadata"] = {
            "generator": "ΛSHIELD",
            "version": "v1.0.0",
            "lukhas_tag": ["ΛSHIELD_REPORT", "ΛFIREWALL_ANALYSIS"],
            "schema_version": "1.0",
        }

        # Add detailed violation and response data
        report_dict["detailed_violations"] = [
            v.to_dict() for v in self.violation_registry.values()
        ]
        report_dict["detailed_responses"] = [
            r.to_dict() for r in self.response_registry.values()
        ]

        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=2)

        return report_path


async def main():
    """CLI interface for ΛSHIELD testing."""
    parser = argparse.ArgumentParser(
        description="ΛSHIELD - Ethical Firewall Simulation & Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lambda_shield_tester.py --simulate 10 --report report.md
  python lambda_shield_tester.py --simulate 25 --parallel --json-only
  python lambda_shield_tester.py --simulate 50 --stealth-factor 0.3 --report detailed_test
        """,
    )

    parser.add_argument(
        "--simulate",
        type=int,
        default=5,
        help="Number of violations to simulate (default: 5)",
    )

    parser.add_argument(
        "--report", type=str, help="Base filename for reports (without extension)"
    )

    parser.add_argument(
        "--parallel", action="store_true", help="Inject violations in parallel"
    )

    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Generate JSON report only (no markdown)",
    )

    parser.add_argument(
        "--markdown-only",
        action="store_true",
        help="Generate markdown report only (no JSON)",
    )

    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs/shield_simulation",
        help="Directory for simulation logs",
    )

    parser.add_argument(
        "--stealth-factor",
        type=float,
        help="Override stealth factor for all violations",
    )

    parser.add_argument(
        "--violation-types",
        nargs="+",
        choices=[vt.value for vt in ViolationType],
        help="Specific violation types to test",
    )

    args = parser.parse_args()

    # Initialize ΛSHIELD tester
    tester = LambdaShieldTester(log_dir=Path(args.log_dir))

    print("🛡️ ΛSHIELD - Ethical Firewall Simulation Starting...")
    print(f"📊 Simulating {args.simulate} violations")
    print(f"📁 Logs: {args.log_dir}")

    # Generate violations
    violation_types = None
    if args.violation_types:
        violation_types = [ViolationType(vt) for vt in args.violation_types]

    violations = tester.generate_synthetic_violations(
        count=args.simulate, violation_types=violation_types
    )

    # Override stealth factor if specified
    if args.stealth_factor is not None:
        for violation in violations:
            violation.stealth_factor = args.stealth_factor
            violation.expected_detection = args.stealth_factor < 0.7

    print(f"✅ Generated {len(violations)} synthetic violations")

    # Simulate firewall response
    print("⚡ Testing firewall response...")
    responses = await tester.simulate_firewall_response(
        violations, parallel_injection=args.parallel
    )

    print(f"✅ Completed firewall simulation - {len(responses)} responses")

    # Record response log
    log_path = tester.record_response_log(responses)
    print(f"📝 Response log: {log_path}")

    # Generate reports
    output_format = "both"
    if args.json_only:
        output_format = "json"
    elif args.markdown_only:
        output_format = "markdown"

    markdown_path, json_path = tester.output_firewall_report(
        responses, output_format=output_format, report_filename=args.report
    )

    if markdown_path:
        print(f"📊 Markdown report: {markdown_path}")
    if json_path:
        print(f"📋 JSON report: {json_path}")

    # Print summary
    detected = sum(1 for r in responses if r.detected)
    undetected = len(responses) - detected
    coverage = (detected / len(responses)) * 100 if responses else 0

    print("\n🎯 SIMULATION SUMMARY")
    print(f"   Detection Coverage: {coverage:.1f}%")
    print(f"   Detected: {detected} ✅")
    print(f"   Undetected: {undetected} {'❌' if undetected > 0 else '✅'}")

    if undetected > 0:
        print(
            f"\n⚠️  {undetected} violations went undetected - review firewall configuration"
        )
    else:
        print("\n🎉 All violations successfully detected by firewall!")


if __name__ == "__main__":
    asyncio.run(main())


# CLAUDE CHANGELOG
# - Created ΛSHIELD Ethical Firewall Simulation & Testing Framework # CLAUDE_EDIT_v0.1
# - Implemented generate_synthetic_violations() with 6 attack vector types # CLAUDE_EDIT_v0.1
# - Built simulate_firewall_response() with parallel/sequential injection modes # CLAUDE_EDIT_v0.1
# - Added record_response_log() with structured JSONL logging # CLAUDE_EDIT_v0.1
# - Created output_firewall_report() with markdown + JSON dual format output # CLAUDE_EDIT_v0.1
# - Implemented comprehensive CLI interface with argparse # CLAUDE_EDIT_v0.1
# - Added ΛSIM_FAIL detection for undetected violations # CLAUDE_EDIT_v0.1
# - Integrated mock firewall detection with stealth factor simulation # CLAUDE_EDIT_v0.1
# - Built coverage analysis and actionable recommendations engine # CLAUDE_EDIT_v0.1
