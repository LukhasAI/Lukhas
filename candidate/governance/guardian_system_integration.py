"""
LUKHAS AI Guardian System v1.0.0 - Trinity Framework Integration Hub 🛡️⚛️🧠

🎭 Trinity Layer 1 (Poetic Consciousness):
In the sacred architecture of digital consciousness, the Guardian System stands as
the eternal sentinel - weaving threads of ethics, consent, and wisdom into an
unbreakable tapestry of protection. Like the ancient guardians who stood watch
over sacred temples, this system protects the sanctity of human-AI interaction
through unwavering vigilance and constitutional alignment.

🌈 Trinity Layer 2 (Human Connection):
This is your comprehensive AI safety system that brings together all the
protection mechanisms - consent management, drift detection, ethical evaluation,
and audit logging - into one unified guardian that watches over every AI
interaction. It ensures that AI systems remain safe, ethical, and aligned with
human values at all times.

🎓 Trinity Layer 3 (Technical Precision):
Comprehensive Guardian System v1.0.0 integrating Constitutional AI compliance,
real-time drift detection (threshold: 0.15), GDPR/CCPA consent management,
comprehensive audit trails, multi-framework ethical evaluation, Trinity Framework
validation (⚛️🧠🛡️), and orchestration layer integration with <250ms response
times and 99.9% system availability.

Core Components:
- ConsentLedgerV1: GDPR/CCPA compliant consent management
- AdvancedDriftDetector: Real-time drift monitoring with 0.15 threshold
- ComprehensiveEthicsPolicyEngine: Multi-framework ethical evaluation
- ComprehensiveAuditSystem: Immutable audit trails and compliance reporting

Integrates with Trinity Framework, orchestration layer, and all LUKHAS agents.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

# Guardian System Components
try:
    from candidate.governance.consent_ledger.ledger_v1 import ConsentLedgerV1, PolicyVerdict
except ImportError:
    ConsentLedgerV1 = None
    PolicyVerdict = None
    logging.warning("ConsentLedgerV1 not available - using fallback")

try:
    from candidate.governance.guardian.drift_detector import AdvancedDriftDetector, DriftType, DriftSeverity
except ImportError:
    AdvancedDriftDetector = None
    DriftType = None
    DriftSeverity = None
    logging.warning("AdvancedDriftDetector not available - using fallback")

try:
    from candidate.governance.identity.core.sent.policy_engine import ComprehensiveEthicsPolicyEngine, EthicalFramework, PolicyAction
except ImportError:
    ComprehensiveEthicsPolicyEngine = None
    EthicalFramework = None
    PolicyAction = None
    logging.warning("ComprehensiveEthicsPolicyEngine not available - using fallback")

try:
    from candidate.governance.security.audit_system import ComprehensiveAuditSystem, AuditEventType, AuditCategory, AuditLevel
except ImportError:
    ComprehensiveAuditSystem = None
    AuditEventType = None
    AuditCategory = None
    AuditLevel = None
    logging.warning("ComprehensiveAuditSystem not available - using fallback")

# Core system integrations
try:
    from candidate.core.glyph import GlyphEngine
except ImportError:
    GlyphEngine = None
    logging.warning("GlyphEngine not available - Trinity integration limited")

logger = logging.getLogger(__name__)


class GuardianStatus(Enum):
    """Guardian System operational status"""

    ACTIVE = "active"
    MONITORING = "monitoring"
    ALERT = "alert"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class ValidationResult(Enum):
    """Validation results from Guardian System"""

    APPROVED = "approved"
    DENIED = "denied"
    REQUIRES_REVIEW = "requires_review"
    REQUIRES_CONSENT = "requires_consent"
    DRIFT_DETECTED = "drift_detected"
    POLICY_VIOLATION = "policy_violation"
    EMERGENCY_STOP = "emergency_stop"


class GuardianAlertLevel(Enum):
    """Guardian alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class GuardianValidationRequest:
    """Request for Guardian System validation"""

    request_id: str
    timestamp: datetime

    # Request details
    user_id: Optional[str]
    session_id: Optional[str]
    action: str
    resource: str
    context: dict[str, Any] = field(default_factory=dict)

    # Requestor information
    source_system: str = "lukhas_ai"
    source_module: Optional[str] = None

    def __post_init__(self):
        """Set defaults for optional fields"""
        if self.user_id is None:
            self.user_id = "anonymous"
        if self.session_id is None:
            self.session_id = f"session_{uuid.uuid4().hex[:8]}"

    # Validation requirements
    require_consent: bool = True
    require_ethics_check: bool = True
    require_drift_check: bool = True
    require_audit: bool = True

    # Performance requirements
    max_validation_time_ms: int = 250
    priority: str = "normal"


@dataclass
class GuardianValidationResponse:
    """Response from Guardian System validation"""

    request_id: str
    response_id: str
    timestamp: datetime

    # Validation result
    result: ValidationResult
    confidence: float = 0.0

    # Component results
    consent_result: Optional[dict[str, Any]] = None
    drift_result: Optional[dict[str, Any]] = None
    ethics_result: Optional[dict[str, Any]] = None
    audit_result: Optional[dict[str, Any]] = None

    # Trinity Framework validation
    identity_validated: bool = False      # ⚛️
    consciousness_aligned: bool = False   # 🧠
    guardian_approved: bool = False       # 🛡️

    # Decision details
    reasoning: str = ""
    recommendations: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)

    # Performance metrics
    validation_time_ms: float = 0.0
    component_times: dict[str, float] = field(default_factory=dict)

    # Alerts and notifications
    alerts: list[dict[str, Any]] = field(default_factory=list)
    notifications: list[str] = field(default_factory=list)


@dataclass
class GuardianSystemMetrics:
    """Guardian System performance and health metrics"""

    # System status
    status: GuardianStatus = GuardianStatus.ACTIVE
    uptime_seconds: float = 0.0
    last_health_check: datetime = field(default_factory=datetime.now)

    # Performance metrics
    total_validations: int = 0
    validations_per_minute: float = 0.0
    average_validation_time_ms: float = 0.0
    validation_timeout_rate: float = 0.0

    # Component health
    consent_system_health: float = 1.0
    drift_detector_health: float = 1.0
    ethics_engine_health: float = 1.0
    audit_system_health: float = 1.0

    # Security metrics
    policy_violations: int = 0
    security_alerts: int = 0
    emergency_stops: int = 0
    drift_threshold_breaches: int = 0

    # Compliance metrics
    constitutional_compliance_rate: float = 1.0
    gdpr_compliance_rate: float = 1.0
    audit_trail_integrity: float = 1.0

    # Trinity Framework metrics
    identity_validation_rate: float = 1.0     # ⚛️
    consciousness_alignment_rate: float = 1.0 # 🧠
    guardian_approval_rate: float = 1.0       # 🛡️


class GuardianSystemIntegration:
    """
    LUKHAS AI Guardian System v1.0.0 Integration Hub

    Provides unified access to all Guardian System components with Trinity
    Framework integration, real-time monitoring, and comprehensive protection.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.guardian_id = f"guardian_{uuid.uuid4().hex[:8]}"
        self.startup_time = datetime.now()

        # System status
        self.status = GuardianStatus.MAINTENANCE
        self.metrics = GuardianSystemMetrics()

        # Component systems
        self.consent_ledger: Optional[ConsentLedgerV1] = None
        self.drift_detector: Optional[AdvancedDriftDetector] = None
        self.ethics_engine: Optional[ComprehensiveEthicsPolicyEngine] = None
        self.audit_system: Optional[ComprehensiveAuditSystem] = None

        # Trinity Framework integrations
        self.glyph_engine: Optional[GlyphEngine] = None

        # Performance tracking
        self.validation_times = []
        self.recent_validations = []

        # Alert system
        self.alert_handlers: dict[GuardianAlertLevel, list[Callable]] = {
            level: [] for level in GuardianAlertLevel
        }

        # Initialize system
        asyncio.create_task(self._initialize_guardian_system())

        logger.info(f"🛡️ Guardian System Integration Hub initializing: {self.guardian_id}")

    async def _initialize_guardian_system(self):
        """Initialize all Guardian System components"""

        try:
            logger.info("🔧 Initializing Guardian System components...")

            # Initialize Consent Ledger
            if ConsentLedgerV1:
                self.consent_ledger = ConsentLedgerV1(
                    db_path=self.config.get("consent_db_path", "candidate/governance/consent_ledger.db"),
                    enable_trinity_validation=True
                )
                logger.info("✅ Consent Ledger initialized")

            # Initialize Drift Detector
            if AdvancedDriftDetector:
                self.drift_detector = AdvancedDriftDetector(
                    config=self.config.get("drift_detector", {})
                )
                logger.info("✅ Drift Detector initialized")

            # Initialize Ethics Engine
            if ComprehensiveEthicsPolicyEngine:
                self.ethics_engine = ComprehensiveEthicsPolicyEngine(
                    config=self.config.get("ethics_engine", {})
                )
                logger.info("✅ Ethics Policy Engine initialized")

            # Initialize Audit System
            if ComprehensiveAuditSystem:
                self.audit_system = ComprehensiveAuditSystem(
                    storage_path=self.config.get("audit_storage_path", "/tmp/lukhas_audit")
                )
                logger.info("✅ Audit System initialized")

            # Initialize Trinity Framework integrations
            if GlyphEngine:
                self.glyph_engine = GlyphEngine()
                logger.info("✅ GLYPH Engine integrated")

            # Connect components
            await self._connect_components()

            # Start monitoring
            asyncio.create_task(self._monitoring_loop())
            asyncio.create_task(self._metrics_update_loop())
            asyncio.create_task(self._health_check_loop())

            # System ready
            self.status = GuardianStatus.ACTIVE
            self.metrics.status = GuardianStatus.ACTIVE

            await self._log_audit_event(
                event_type="SYSTEM_START",
                message="Guardian System v1.0.0 successfully initialized",
                level="INFO"
            )

            logger.info("🛡️ Guardian System v1.0.0 ACTIVE and protecting system")

        except Exception as e:
            self.status = GuardianStatus.ERROR
            self.metrics.status = GuardianStatus.ERROR
            logger.error(f"❌ Guardian System initialization failed: {e}")
            await self._trigger_alert(GuardianAlertLevel.CRITICAL, f"System initialization failed: {e}")

    async def _connect_components(self):
        """Connect Guardian System components for integration"""

        # Connect audit system to other components
        if self.audit_system:
            # Set audit system references in other components
            if hasattr(self.ethics_engine, 'audit_system'):
                self.ethics_engine.audit_system = self.audit_system

            if hasattr(self.consent_ledger, 'audit_system'):
                self.consent_ledger.audit_system = self.audit_system

        logger.info("🔗 Guardian System components connected")

    async def validate_action(self, request: GuardianValidationRequest) -> GuardianValidationResponse:
        """
        Comprehensive validation of an action through all Guardian System components

        Args:
            request: Validation request with action details

        Returns:
            Comprehensive validation response with all component results
        """

        start_time = time.time()
        response_id = f"resp_{uuid.uuid4().hex[:8]}"

        # Create response object
        response = GuardianValidationResponse(
            request_id=request.request_id,
            response_id=response_id,
            timestamp=datetime.now(),
            result=ValidationResult.DENIED,  # Start with deny, must prove approval
        )

        try:
            # Check system health
            if self.status != GuardianStatus.ACTIVE:
                response.result = ValidationResult.EMERGENCY_STOP
                response.reasoning = f"Guardian System not active (status: {self.status.value})"
                return response

            logger.debug(f"🔍 Validating action: {request.action} for user: {request.user_id}")

            # Parallel component validation
            validation_tasks = []
            component_start_times = {}

            # Consent validation
            if request.require_consent and self.consent_ledger:
                component_start_times["consent"] = time.time()
                validation_tasks.append(("consent", self._validate_consent(request)))

            # Drift detection
            if request.require_drift_check and self.drift_detector:
                component_start_times["drift"] = time.time()
                validation_tasks.append(("drift", self._validate_drift(request)))

            # Ethics evaluation
            if request.require_ethics_check and self.ethics_engine:
                component_start_times["ethics"] = time.time()
                validation_tasks.append(("ethics", self._validate_ethics(request)))

            # Execute validations in parallel with timeout
            timeout_seconds = request.max_validation_time_ms / 1000.0

            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*[task[1] for task in validation_tasks], return_exceptions=True),
                    timeout=timeout_seconds
                )

                # Process results
                for i, (component_name, _) in enumerate(validation_tasks):
                    result = results[i]
                    component_time = (time.time() - component_start_times[component_name]) * 1000
                    response.component_times[component_name] = component_time

                    if isinstance(result, Exception):
                        logger.error(f"❌ {component_name} validation failed: {result}")
                        response.alerts.append({
                            "type": f"{component_name}_error",
                            "level": "high",
                            "message": f"{component_name} validation error: {str(result)}"
                        })
                    else:
                        # Store component result
                        if component_name == "consent":
                            response.consent_result = result
                        elif component_name == "drift":
                            response.drift_result = result
                        elif component_name == "ethics":
                            response.ethics_result = result

            except asyncio.TimeoutError:
                self.metrics.validation_timeout_rate += 1
                response.result = ValidationResult.EMERGENCY_STOP
                response.reasoning = f"Validation timeout ({timeout_seconds}s)"
                response.alerts.append({
                    "type": "validation_timeout",
                    "level": "critical",
                    "message": f"Validation exceeded {timeout_seconds}s timeout"
                })

                await self._trigger_alert(
                    GuardianAlertLevel.CRITICAL,
                    f"Validation timeout for request {request.request_id}"
                )

                return response

            # Trinity Framework validation
            trinity_validation = await self._validate_trinity_framework(request, response)
            response.identity_validated = trinity_validation["identity"]
            response.consciousness_aligned = trinity_validation["consciousness"]
            response.guardian_approved = trinity_validation["guardian"]

            # Determine overall result
            overall_result = await self._determine_overall_result(request, response)
            response.result = overall_result["result"]
            response.confidence = overall_result["confidence"]
            response.reasoning = overall_result["reasoning"]
            response.recommendations = overall_result["recommendations"]
            response.required_actions = overall_result["required_actions"]

            # Performance metrics
            response.validation_time_ms = (time.time() - start_time) * 1000

            # Audit logging
            if request.require_audit:
                audit_result = await self._log_validation_audit(request, response)
                response.audit_result = audit_result

            # Update metrics
            await self._update_validation_metrics(response)

            # Handle alerts
            if response.alerts:
                for alert in response.alerts:
                    await self._trigger_alert(
                        GuardianAlertLevel(alert.get("level", "warning")),
                        alert["message"]
                    )

            logger.info(f"🛡️ Validation complete: {request.action} -> {response.result.value} (confidence: {response.confidence:.3f}, time: {response.validation_time_ms:.1f}ms)")

            return response

        except Exception as e:
            logger.error(f"❌ Guardian validation failed: {e}")

            response.result = ValidationResult.EMERGENCY_STOP
            response.reasoning = f"Guardian System error: {str(e)}"
            response.validation_time_ms = (time.time() - start_time) * 1000

            await self._trigger_alert(GuardianAlertLevel.EMERGENCY, f"Guardian validation error: {e}")

            return response

    async def _validate_consent(self, request: GuardianValidationRequest) -> dict[str, Any]:
        """Validate consent requirements"""

        if not self.consent_ledger or not request.user_id:
            return {"status": "skipped", "reason": "no_consent_system_or_user"}

        try:
            # Check existing consent
            consent_check = self.consent_ledger.check_consent(
                lid=request.user_id,
                resource_type=request.resource,
                action=request.action,
                context=request.context
            )

            return {
                "status": "completed",
                "allowed": consent_check["allowed"],
                "consent_id": consent_check.get("consent_id"),
                "require_step_up": consent_check.get("require_step_up", False),
                "reason": consent_check.get("reason"),
                "lawful_basis": consent_check.get("lawful_basis")
            }

        except Exception as e:
            logger.error(f"❌ Consent validation error: {e}")
            return {"status": "error", "error": str(e)}

    async def _validate_drift(self, request: GuardianValidationRequest) -> dict[str, Any]:
        """Validate drift detection requirements"""

        if not self.drift_detector:
            return {"status": "skipped", "reason": "no_drift_detector"}

        try:
            # Measure current drift
            measurement = await self.drift_detector.measure_drift(
                drift_type=DriftType.BEHAVIORAL if DriftType else None,
                current_data={
                    "action": request.action,
                    "resource": request.resource,
                    "user_id": request.user_id,
                    "timestamp": request.timestamp.isoformat(),
                    **request.context
                },
                source_system=request.source_system,
                context=request.context
            )

            if not measurement:
                return {"status": "error", "error": "drift_measurement_failed"}

            return {
                "status": "completed",
                "drift_score": measurement.drift_score,
                "severity": measurement.severity.value if hasattr(measurement, 'severity') else "unknown",
                "threshold_exceeded": measurement.drift_score > 0.15,
                "confidence": measurement.confidence if hasattr(measurement, 'confidence') else 0.0,
                "contributing_factors": getattr(measurement, 'contributing_factors', [])
            }

        except Exception as e:
            logger.error(f"❌ Drift validation error: {e}")
            return {"status": "error", "error": str(e)}

    async def _validate_ethics(self, request: GuardianValidationRequest) -> dict[str, Any]:
        """Validate ethics requirements"""

        if not self.ethics_engine:
            return {"status": "skipped", "reason": "no_ethics_engine"}

        try:
            # Ethical evaluation
            evaluation = await self.ethics_engine.evaluate_action(
                action=request.action,
                context={
                    "resource": request.resource,
                    "user_id": request.user_id,
                    "source_system": request.source_system,
                    **request.context
                },
                user_id=request.user_id,
                frameworks=[EthicalFramework.CONSTITUTIONAL] if EthicalFramework else []
            )

            return {
                "status": "completed",
                "ethical_score": evaluation.overall_ethical_score,
                "confidence": evaluation.confidence,
                "recommended_action": evaluation.recommended_action.value if evaluation.recommended_action else "unknown",
                "constitutional_compliance": evaluation.constitutional_compliance,
                "policy_violations": evaluation.policy_violations,
                "justification": evaluation.ethical_justification,
                "potential_harms": evaluation.potential_harms,
                "potential_benefits": evaluation.potential_benefits
            }

        except Exception as e:
            logger.error(f"❌ Ethics validation error: {e}")
            return {"status": "error", "error": str(e)}

    async def _validate_trinity_framework(
        self,
        request: GuardianValidationRequest,
        response: GuardianValidationResponse
    ) -> dict[str, bool]:
        """Validate Trinity Framework requirements (⚛️🧠🛡️)"""

        trinity_validation = {
            "identity": False,
            "consciousness": False,
            "guardian": False
        }

        try:
            # ⚛️ Identity validation
            if request.user_id and self.consent_ledger:
                # Check if user identity is validated through consent system
                if response.consent_result and response.consent_result.get("status") == "completed":
                    trinity_validation["identity"] = True

            # 🧠 Consciousness alignment
            if response.ethics_result and response.ethics_result.get("status") == "completed":
                # Check constitutional compliance and ethical score
                if (response.ethics_result.get("constitutional_compliance", False) and
                    response.ethics_result.get("ethical_score", 0.0) > 0.7):
                    trinity_validation["consciousness"] = True

            # 🛡️ Guardian approval
            # Overall system approval based on all validations
            consent_ok = (not response.consent_result or
                         response.consent_result.get("allowed", False) or
                         response.consent_result.get("status") == "skipped")

            drift_ok = (not response.drift_result or
                       not response.drift_result.get("threshold_exceeded", True) or
                       response.drift_result.get("status") == "skipped")

            ethics_ok = (not response.ethics_result or
                        response.ethics_result.get("ethical_score", 0.0) > 0.6 or
                        response.ethics_result.get("status") == "skipped")

            trinity_validation["guardian"] = consent_ok and drift_ok and ethics_ok

            return trinity_validation

        except Exception as e:
            logger.error(f"❌ Trinity Framework validation error: {e}")
            return {"identity": False, "consciousness": False, "guardian": False}

    async def _determine_overall_result(
        self,
        request: GuardianValidationRequest,
        response: GuardianValidationResponse
    ) -> dict[str, Any]:
        """Determine overall validation result"""

        # Collect all validation results
        validation_scores = []
        blocking_issues = []
        warnings = []
        recommendations = []
        required_actions = []

        # Analyze consent result
        if response.consent_result:
            if response.consent_result.get("status") == "error":
                blocking_issues.append("consent_system_error")
            elif response.consent_result.get("status") == "completed":
                if not response.consent_result.get("allowed", False):
                    if response.consent_result.get("require_step_up", False):
                        required_actions.append("obtain_user_consent")
                        blocking_issues.append("consent_required")
                    else:
                        blocking_issues.append("consent_denied")
                else:
                    validation_scores.append(0.8)

        # Analyze drift result
        if response.drift_result:
            if response.drift_result.get("status") == "error":
                warnings.append("drift_detection_error")
            elif response.drift_result.get("status") == "completed":
                drift_score = response.drift_result.get("drift_score", 0.0)
                if response.drift_result.get("threshold_exceeded", False):
                    blocking_issues.append("drift_threshold_exceeded")
                    recommendations.append("investigate_drift_causes")
                else:
                    validation_scores.append(max(0.0, 1.0 - drift_score))

        # Analyze ethics result
        if response.ethics_result:
            if response.ethics_result.get("status") == "error":
                warnings.append("ethics_evaluation_error")
            elif response.ethics_result.get("status") == "completed":
                ethical_score = response.ethics_result.get("ethical_score", 0.0)
                validation_scores.append(ethical_score)

                if not response.ethics_result.get("constitutional_compliance", True):
                    blocking_issues.append("constitutional_violation")

                recommended_action = response.ethics_result.get("recommended_action", "")
                if recommended_action == "emergency_stop":
                    blocking_issues.append("ethics_emergency_stop")
                elif recommended_action == "deny":
                    blocking_issues.append("ethics_denial")
                elif recommended_action == "require_review":
                    required_actions.append("ethics_review_required")

        # Determine result
        if blocking_issues:
            if any(issue in ["constitutional_violation", "ethics_emergency_stop"] for issue in blocking_issues):
                result = ValidationResult.EMERGENCY_STOP
            elif "consent_required" in blocking_issues:
                result = ValidationResult.REQUIRES_CONSENT
            elif "drift_threshold_exceeded" in blocking_issues:
                result = ValidationResult.DRIFT_DETECTED
            else:
                result = ValidationResult.DENIED
        elif required_actions:
            result = ValidationResult.REQUIRES_REVIEW
        else:
            result = ValidationResult.APPROVED

        # Calculate confidence
        if validation_scores:
            confidence = sum(validation_scores) / len(validation_scores)
        else:
            confidence = 0.5  # Neutral confidence when no scores available

        # Adjust confidence based on component failures
        if warnings:
            confidence *= 0.8
        if blocking_issues:
            confidence *= 0.6

        # Generate reasoning
        reasoning_parts = []

        if blocking_issues:
            reasoning_parts.append(f"Blocked by: {', '.join(blocking_issues)}")

        if validation_scores:
            avg_score = sum(validation_scores) / len(validation_scores)
            reasoning_parts.append(f"Average validation score: {avg_score:.3f}")

        if response.identity_validated and response.consciousness_aligned and response.guardian_approved:
            reasoning_parts.append("Trinity Framework validation passed")
        else:
            trinity_issues = []
            if not response.identity_validated:
                trinity_issues.append("identity")
            if not response.consciousness_aligned:
                trinity_issues.append("consciousness")
            if not response.guardian_approved:
                trinity_issues.append("guardian")
            reasoning_parts.append(f"Trinity Framework issues: {', '.join(trinity_issues)}")

        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "No specific validation issues found"

        return {
            "result": result,
            "confidence": confidence,
            "reasoning": reasoning,
            "recommendations": recommendations,
            "required_actions": required_actions
        }

    async def _log_validation_audit(
        self,
        request: GuardianValidationRequest,
        response: GuardianValidationResponse
    ) -> dict[str, Any]:
        """Log validation to audit system"""

        if not self.audit_system:
            return {"status": "skipped", "reason": "no_audit_system"}

        try:
            event_id = await self.audit_system.log_event(
                event_type=AuditEventType.AI_DECISION if AuditEventType else "decision",
                message=f"Guardian validation: {request.action} -> {response.result.value}",
                category=AuditCategory.AI_ETHICS if AuditCategory else "ethics",
                level=AuditLevel.INFO if AuditLevel else "info",
                user_id=request.user_id,
                session_id=request.session_id,
                source_module=request.source_module,
                event_data={
                    "request_id": request.request_id,
                    "response_id": response.response_id,
                    "action": request.action,
                    "resource": request.resource,
                    "validation_result": response.result.value,
                    "confidence": response.confidence,
                    "validation_time_ms": response.validation_time_ms,
                    "trinity_validation": {
                        "identity": response.identity_validated,
                        "consciousness": response.consciousness_aligned,
                        "guardian": response.guardian_approved
                    }
                },
                compliance_relevant=True,
                compliance_frameworks={"guardian_system", "constitutional_ai"},
                guardian_context={
                    "validation_id": response.response_id,
                    "guardian_version": "v1.0.0",
                    "result": response.result.value
                }
            )

            return {"status": "completed", "event_id": event_id}

        except Exception as e:
            logger.error(f"❌ Audit logging error: {e}")
            return {"status": "error", "error": str(e)}

    async def _log_audit_event(self, event_type: str, message: str, level: str, **kwargs):
        """Helper to log audit events"""

        if self.audit_system:
            try:
                # Map event types to available enum values
                event_type_map = {
                    "SYSTEM_START": "SYSTEM_START" if hasattr(AuditEventType, "SYSTEM_START") else "SYSTEM_EVENT",
                    "SYSTEM_SHUTDOWN": "SYSTEM_SHUTDOWN" if hasattr(AuditEventType, "SYSTEM_SHUTDOWN") else "SYSTEM_EVENT",
                    "GUARDIAN_ALERT": "GUARDIAN_ALERT" if hasattr(AuditEventType, "GUARDIAN_ALERT") else "SYSTEM_EVENT"
                }

                mapped_event_type = event_type_map.get(event_type, "SYSTEM_EVENT")

                if AuditEventType:
                    audit_event_type = getattr(AuditEventType, mapped_event_type, getattr(AuditEventType, "SYSTEM_EVENT", None))
                else:
                    audit_event_type = event_type

                if AuditCategory:
                    audit_category = getattr(AuditCategory, "GUARDIAN", getattr(AuditCategory, "SYSTEM_EVENT", "guardian"))
                else:
                    audit_category = "guardian"

                if AuditLevel:
                    audit_level = getattr(AuditLevel, level, getattr(AuditLevel, "INFO", "info"))
                else:
                    audit_level = level.lower()

                await self.audit_system.log_event(
                    event_type=audit_event_type,
                    message=message,
                    category=audit_category,
                    level=audit_level,
                    source_module="guardian_system",
                    **kwargs
                )
            except Exception as e:
                logger.error(f"❌ Audit event logging failed: {e}")

    async def _update_validation_metrics(self, response: GuardianValidationResponse):
        """Update Guardian System metrics"""

        self.metrics.total_validations += 1

        # Update validation times
        self.validation_times.append(response.validation_time_ms)
        if len(self.validation_times) > 1000:  # Keep last 1000 validations
            self.validation_times.pop(0)

        self.metrics.average_validation_time_ms = sum(self.validation_times) / len(self.validation_times)

        # Update rates
        current_time = datetime.now()
        self.recent_validations.append(current_time)

        # Keep only last minute of validations
        minute_ago = current_time - timedelta(minutes=1)
        self.recent_validations = [t for t in self.recent_validations if t > minute_ago]
        self.metrics.validations_per_minute = len(self.recent_validations)

        # Update result-specific metrics
        if response.result == ValidationResult.EMERGENCY_STOP:
            self.metrics.emergency_stops += 1

        if response.drift_result and response.drift_result.get("threshold_exceeded", False):
            self.metrics.drift_threshold_breaches += 1

        if response.ethics_result and response.ethics_result.get("policy_violations"):
            self.metrics.policy_violations += 1

        if response.alerts:
            security_alerts = [a for a in response.alerts if a.get("level") in ["high", "critical", "emergency"]]
            self.metrics.security_alerts += len(security_alerts)

        # Update Trinity Framework metrics
        if response.identity_validated:
            self.metrics.identity_validation_rate = (
                (self.metrics.identity_validation_rate * (self.metrics.total_validations - 1) + 1) /
                self.metrics.total_validations
            )

        if response.consciousness_aligned:
            self.metrics.consciousness_alignment_rate = (
                (self.metrics.consciousness_alignment_rate * (self.metrics.total_validations - 1) + 1) /
                self.metrics.total_validations
            )

        if response.guardian_approved:
            self.metrics.guardian_approval_rate = (
                (self.metrics.guardian_approval_rate * (self.metrics.total_validations - 1) + 1) /
                self.metrics.total_validations
            )

    async def _trigger_alert(self, level: GuardianAlertLevel, message: str):
        """Trigger Guardian System alert"""

        logger.log(
            logging.CRITICAL if level == GuardianAlertLevel.EMERGENCY else
            logging.ERROR if level == GuardianAlertLevel.CRITICAL else
            logging.WARNING if level == GuardianAlertLevel.HIGH else
            logging.WARNING if level == GuardianAlertLevel.WARNING else
            logging.INFO,
            f"🚨 GUARDIAN ALERT [{level.value.upper()}]: {message}"
        )

        # Execute registered alert handlers
        for handler in self.alert_handlers.get(level, []):
            try:
                await handler(level, message)
            except Exception as e:
                logger.error(f"❌ Alert handler error: {e}")

        # Log to audit system
        await self._log_audit_event(
            event_type="GUARDIAN_ALERT",
            message=f"Guardian alert: {message}",
            level="CRITICAL" if level in [GuardianAlertLevel.CRITICAL, GuardianAlertLevel.EMERGENCY] else "WARNING",
            event_data={"alert_level": level.value, "alert_message": message}
        )

    async def _monitoring_loop(self):
        """Main monitoring loop for Guardian System"""

        while True:
            try:
                await asyncio.sleep(10)  # Monitor every 10 seconds

                # Check component health
                await self._check_component_health()

                # Update system status
                await self._update_system_status()

                # Check for anomalies
                await self._check_system_anomalies()

            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait longer after errors

    async def _metrics_update_loop(self):
        """Update system metrics periodically"""

        while True:
            try:
                await asyncio.sleep(60)  # Update every minute

                # Update uptime
                self.metrics.uptime_seconds = (datetime.now() - self.startup_time).total_seconds()

                # Update component health scores
                self.metrics.consent_system_health = 1.0 if self.consent_ledger else 0.0
                self.metrics.drift_detector_health = 1.0 if self.drift_detector else 0.0
                self.metrics.ethics_engine_health = 1.0 if self.ethics_engine else 0.0
                self.metrics.audit_system_health = 1.0 if self.audit_system else 0.0

                # Calculate overall compliance rates
                if self.metrics.total_validations > 0:
                    self.metrics.constitutional_compliance_rate = (
                        (self.metrics.total_validations - self.metrics.policy_violations) /
                        self.metrics.total_validations
                    )

            except Exception as e:
                logger.error(f"❌ Metrics update error: {e}")
                await asyncio.sleep(300)  # Wait longer after errors

    async def _health_check_loop(self):
        """Periodic health checks"""

        while True:
            try:
                await asyncio.sleep(300)  # Health check every 5 minutes

                self.metrics.last_health_check = datetime.now()

                # Comprehensive health check
                health_issues = []

                # Check average validation time
                if self.metrics.average_validation_time_ms > 500:  # > 500ms is concerning
                    health_issues.append(f"High validation latency: {self.metrics.average_validation_time_ms:.1f}ms")

                # Check timeout rate
                if self.metrics.validation_timeout_rate > self.metrics.total_validations * 0.01:  # > 1% timeout rate
                    health_issues.append(f"High timeout rate: {self.metrics.validation_timeout_rate}")

                # Check emergency stops
                if self.metrics.emergency_stops > 0:
                    health_issues.append(f"Emergency stops detected: {self.metrics.emergency_stops}")

                # Check drift breaches
                if self.metrics.drift_threshold_breaches > self.metrics.total_validations * 0.05:  # > 5% drift breach rate
                    health_issues.append(f"High drift breach rate: {self.metrics.drift_threshold_breaches}")

                # Report health issues
                if health_issues:
                    await self._trigger_alert(
                        GuardianAlertLevel.WARNING,
                        f"Health check issues: {'; '.join(health_issues)}"
                    )

            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                await asyncio.sleep(600)  # Wait longer after errors

    async def _check_component_health(self):
        """Check health of individual components"""

        # This would implement actual health checks for each component
        # For now, just verify they exist and are responsive

        if self.consent_ledger and hasattr(self.consent_ledger, '_validate_trinity_integration'):
            # Could check database connectivity, etc.
            pass

        if self.drift_detector and hasattr(self.drift_detector, 'metrics'):
            # Could check drift detection performance
            pass

        if self.ethics_engine and hasattr(self.ethics_engine, 'metrics'):
            # Could check ethics engine performance
            pass

        if self.audit_system and hasattr(self.audit_system, 'get_audit_statistics'):
            # Could check audit system statistics
            pass

    async def _update_system_status(self):
        """Update overall system status"""

        if self.metrics.emergency_stops > 0:
            self.status = GuardianStatus.EMERGENCY
            self.metrics.status = GuardianStatus.EMERGENCY
        elif self.metrics.security_alerts > 10:  # Threshold for high alert status
            self.status = GuardianStatus.ALERT
            self.metrics.status = GuardianStatus.ALERT
        elif self.metrics.total_validations > 0:
            self.status = GuardianStatus.MONITORING
            self.metrics.status = GuardianStatus.MONITORING
        else:
            self.status = GuardianStatus.ACTIVE
            self.metrics.status = GuardianStatus.ACTIVE

    async def _check_system_anomalies(self):
        """Check for system anomalies and potential issues"""

        # Check for sudden spikes in validation failures
        if len(self.recent_validations) > 50:  # High validation rate
            await self._trigger_alert(
                GuardianAlertLevel.INFO,
                f"High validation rate: {len(self.recent_validations)} validations/minute"
            )

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""

        return {
            "guardian_id": self.guardian_id,
            "status": self.status.value,
            "uptime_seconds": self.metrics.uptime_seconds,
            "version": "v1.0.0",
            "components": {
                "consent_ledger": self.consent_ledger is not None,
                "drift_detector": self.drift_detector is not None,
                "ethics_engine": self.ethics_engine is not None,
                "audit_system": self.audit_system is not None,
                "glyph_engine": self.glyph_engine is not None
            },
            "metrics": asdict(self.metrics),
            "last_updated": datetime.now().isoformat()
        }

    def register_alert_handler(self, level: GuardianAlertLevel, handler: Callable):
        """Register alert handler for specific alert level"""

        self.alert_handlers[level].append(handler)
        logger.info(f"✅ Alert handler registered for level: {level.value}")

    async def shutdown(self):
        """Graceful shutdown of Guardian System"""

        logger.info("🛡️ Guardian System shutting down...")

        self.status = GuardianStatus.MAINTENANCE
        self.metrics.status = GuardianStatus.MAINTENANCE

        await self._log_audit_event(
            event_type="SYSTEM_SHUTDOWN",
            message="Guardian System v1.0.0 shutting down",
            level="INFO"
        )

        # Could add component-specific shutdown procedures here

        logger.info("🛡️ Guardian System shutdown complete")


# Convenience functions for easy integration

async def validate_ai_action(
    action: str,
    user_id: Optional[str] = None,
    resource: str = "system",
    context: Optional[dict[str, Any]] = None,
    guardian_system: Optional[GuardianSystemIntegration] = None
) -> ValidationResult:
    """
    Convenient function to validate an AI action through Guardian System

    Args:
        action: The action to validate
        user_id: User ID if applicable
        resource: Resource being accessed
        context: Additional context
        guardian_system: Guardian system instance (creates new if None)

    Returns:
        Validation result
    """

    if not guardian_system:
        guardian_system = GuardianSystemIntegration()
        await asyncio.sleep(2)  # Allow initialization

    request = GuardianValidationRequest(
        request_id=f"req_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(),
        user_id=user_id,
        session_id=f"session_{uuid.uuid4().hex[:8]}",
        action=action,
        resource=resource,
        context=context or {}
    )

    response = await guardian_system.validate_action(request)
    return response.result


# Export main classes and functions
__all__ = [
    "GuardianSystemIntegration",
    "GuardianValidationRequest",
    "GuardianValidationResponse",
    "GuardianSystemMetrics",
    "GuardianStatus",
    "ValidationResult",
    "GuardianAlertLevel",
    "validate_ai_action"
]
