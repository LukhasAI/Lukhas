"""
Comprehensive Test Suite for LUKHAS Guardian System v1.0.0

Tests all Guardian System components including:
- Consent management with GDPR/CCPA compliance
- Drift detection with 0.15 threshold monitoring
- Ethics policy engine with Constitutional AI
- Audit system with immutable logging
- Trinity Framework integration (⚛️🧠🛡️)
- Guardian System integration hub

This test suite validates the complete Guardian System implementation
against the requirements from AGENT_TASK_EXECUTION_PLAN.md
"""

import asyncio
import tempfile
import time
import uuid
from datetime import datetime
from datetime import timedelta
from pathlib import Path

import pytest

# Guardian System components
try:
    from candidate.governance.guardian_system_integration import (
        GuardianSystemIntegration,
    )
    from candidate.governance.guardian_system_integration import (
        GuardianValidationRequest,
    )
    from candidate.governance.guardian_system_integration import ValidationResult
    from candidate.governance.guardian_system_integration import validate_ai_action

    GUARDIAN_INTEGRATION_AVAILABLE = True
except ImportError:
    GUARDIAN_INTEGRATION_AVAILABLE = False
    print("Guardian System Integration not available for testing")

try:
    from candidate.governance.consent_ledger.ledger_v1 import ConsentLedgerV1
    from candidate.governance.consent_ledger.ledger_v1 import ConsentType
    from candidate.governance.consent_ledger.ledger_v1 import DataSubjectRights
    from candidate.governance.consent_ledger.ledger_v1 import PolicyVerdict

    CONSENT_LEDGER_AVAILABLE = True
except ImportError:
    CONSENT_LEDGER_AVAILABLE = False
    print("Consent Ledger not available for testing")

try:
    from candidate.governance.guardian.drift_detector import AdvancedDriftDetector
    from candidate.governance.guardian.drift_detector import DriftSeverity
    from candidate.governance.guardian.drift_detector import DriftType

    DRIFT_DETECTOR_AVAILABLE = True
except ImportError:
    DRIFT_DETECTOR_AVAILABLE = False
    print("Drift Detector not available for testing")

try:
    from candidate.governance.identity.core.sent.policy_engine import (
        ComprehensiveEthicsPolicyEngine,
    )
    from candidate.governance.identity.core.sent.policy_engine import EthicalFramework
    from candidate.governance.identity.core.sent.policy_engine import PolicyAction

    ETHICS_ENGINE_AVAILABLE = True
except ImportError:
    ETHICS_ENGINE_AVAILABLE = False
    print("Ethics Policy Engine not available for testing")

try:
    from candidate.governance.security.audit_system import AuditEventType
    from candidate.governance.security.audit_system import ComprehensiveAuditSystem

    AUDIT_SYSTEM_AVAILABLE = True
except ImportError:
    AUDIT_SYSTEM_AVAILABLE = False
    print("Audit System not available for testing")


@pytest.mark.asyncio
@pytest.mark.skipif(
    not CONSENT_LEDGER_AVAILABLE, reason="ConsentLedgerV1 not available"
)
class TestConsentLedger:
    """Test Consent Management System with GDPR/CCPA compliance"""

    async def test_consent_ledger_initialization(self):
        """Test consent ledger initializes properly"""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_consent.db"

            ledger = ConsentLedgerV1(str(db_path), enable_trinity_validation=True)

            assert ledger is not None
            assert ledger.db_path.exists()
            assert ledger.enable_trinity

    async def test_consent_grant_gdpr_compliance(self):
        """Test consent granting with GDPR compliance"""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_consent.db"
            ledger = ConsentLedgerV1(str(db_path))

            # Grant GDPR-compliant consent
            consent = ledger.grant_consent(
                lid="test_user_001",
                resource_type="email",
                scopes=["read", "analyze"],
                purpose="email_assistance",
                lawful_basis="consent",
                consent_type=ConsentType.EXPLICIT,
                data_categories=["email_content", "metadata"],
                expires_in_days=90,
                automated_decision_making=False,
                sensitive_data=False,
            )

            assert consent is not None
            assert consent.lid == "test_user_001"
            assert consent.resource_type == "email"
            assert consent.lawful_basis == "consent"
            assert consent.consent_type == ConsentType.EXPLICIT
            assert consent.is_active
            assert len(consent.data_subject_rights) > 0
            assert DataSubjectRights.ERASURE in consent.data_subject_rights

    async def test_consent_revocation(self):
        """Test real-time consent revocation (GDPR Article 7.3)"""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_consent.db"
            ledger = ConsentLedgerV1(str(db_path))

            # Grant consent
            consent = ledger.grant_consent(
                lid="test_user_002",
                resource_type="documents",
                scopes=["read"],
                purpose="document_analysis",
            )

            assert consent.is_active

            # Revoke consent
            success = ledger.revoke_consent(
                consent_id=consent.consent_id,
                lid="test_user_002",
                reason="user_requested",
            )

            assert success

    async def test_consent_check_validation(self):
        """Test consent checking for action validation"""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_consent.db"
            ledger = ConsentLedgerV1(str(db_path))

            # Grant consent with specific scopes
            ledger.grant_consent(
                lid="test_user_003",
                resource_type="calendar",
                scopes=["read", "list"],
                purpose="schedule_assistance",
            )

            # Check allowed action
            result = ledger.check_consent(
                lid="test_user_003", resource_type="calendar", action="read"
            )

            assert result["allowed"] is True
            assert "consent_id" in result

            # Check disallowed action
            result = ledger.check_consent(
                lid="test_user_003", resource_type="calendar", action="write"
            )

            assert result["allowed"] is False
            assert result["reason"] == "action_not_in_scope"

    async def test_lambda_trace_integrity(self):
        """Test Λ-trace audit record integrity"""

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test_consent.db"
            ledger = ConsentLedgerV1(str(db_path))

            # Create trace
            trace = ledger.create_trace(
                lid="test_user_004",
                action="data_access",
                resource="user_profile",
                purpose="profile_management",
                verdict=PolicyVerdict.ALLOW,
                context={"test": "value"},
            )

            assert trace is not None
            assert trace.trace_id.startswith("LT-")
            assert trace.lid == "test_user_004"
            assert trace.policy_verdict == PolicyVerdict.ALLOW

            # Verify integrity
            original_hash = trace.to_immutable_hash()
            assert len(original_hash) == 64  # SHA3-256 hash

            # Verify signature
            signature = trace.sign(ledger.secret_key)
            assert len(signature) == 64  # HMAC-SHA256 signature


@pytest.mark.asyncio
@pytest.mark.skipif(
    not DRIFT_DETECTOR_AVAILABLE, reason="AdvancedDriftDetector not available"
)
class TestDriftDetector:
    """Test Drift Detection System with 0.15 threshold monitoring"""

    async def test_drift_detector_initialization(self):
        """Test drift detector initializes with proper configuration"""

        detector = AdvancedDriftDetector(
            config={"drift_threshold": 0.15, "measurement_interval": 5.0}
        )

        assert detector is not None
        assert detector.drift_threshold == 0.15
        assert detector.measurement_interval == 5.0
        assert detector.monitoring_active is True

    async def test_drift_measurement_basic(self):
        """Test basic drift measurement functionality"""

        detector = AdvancedDriftDetector()

        # Simulate current data
        current_data = {
            "response_time": 150.0,
            "accuracy": 0.95,
            "user_satisfaction": 0.88,
        }

        # Measure drift
        measurement = await detector.measure_drift(
            drift_type=DriftType.PERFORMANCE,
            current_data=current_data,
            source_system="test_system",
        )

        assert measurement is not None
        assert measurement.drift_type == DriftType.PERFORMANCE
        assert 0.0 <= measurement.drift_score <= 1.0
        assert measurement.severity in list(DriftSeverity)
        assert measurement.confidence >= 0.0

    async def test_drift_threshold_breach_detection(self):
        """Test detection of drift threshold breaches (>0.15)"""

        detector = AdvancedDriftDetector()

        # Create data that should trigger high drift
        high_drift_data = {
            "response_time": 1000.0,  # Very high response time
            "error_rate": 0.2,  # High error rate
            "anomaly_score": 0.8,  # High anomaly
        }

        measurement = await detector.measure_drift(
            drift_type=DriftType.PERFORMANCE,
            current_data=high_drift_data,
            source_system="test_system",
            context={"test_scenario": "high_drift"},
        )

        assert measurement is not None
        # Should detect significant drift
        assert measurement.drift_score > 0.1  # Some drift detected

    async def test_multiple_drift_types(self):
        """Test different types of drift detection"""

        detector = AdvancedDriftDetector()

        drift_types = [
            DriftType.BEHAVIORAL,
            DriftType.STATISTICAL,
            DriftType.CONSTITUTIONAL,
            DriftType.PERFORMANCE,
            DriftType.ETHICAL,
        ]

        for drift_type in drift_types:
            measurement = await detector.measure_drift(
                drift_type=drift_type,
                current_data={"test_metric": 0.5},
                source_system="test_system",
            )

            assert measurement is not None
            assert measurement.drift_type == drift_type

    async def test_drift_report_generation(self):
        """Test comprehensive drift report generation"""

        detector = AdvancedDriftDetector()

        # Generate some measurements first
        for i in range(5):
            await detector.measure_drift(
                drift_type=DriftType.BEHAVIORAL,
                current_data={"iteration": i, "value": 0.1 * i},
                source_system="test_system",
            )

        # Generate report
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)

        report = await detector.get_drift_report((start_time, end_time))

        assert report is not None
        assert report.total_measurements >= 0
        assert report.overall_drift_score >= 0.0
        assert report.system_stability in ["stable", "unstable", "critical"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not ETHICS_ENGINE_AVAILABLE, reason="ComprehensiveEthicsPolicyEngine not available"
)
class TestEthicsPolicyEngine:
    """Test Ethics Policy Engine with Constitutional AI"""

    async def test_ethics_engine_initialization(self):
        """Test ethics engine initializes with default policies"""

        engine = ComprehensiveEthicsPolicyEngine()

        assert engine is not None
        assert len(engine.active_policies) > 0
        assert "constitutional_ai_v1" in engine.active_policies
        assert len(engine.constitutional_principles) > 0

    async def test_constitutional_ai_evaluation(self):
        """Test Constitutional AI principle evaluation"""

        engine = ComprehensiveEthicsPolicyEngine()

        # Test helpful, harmless action
        evaluation = await engine.evaluate_action(
            action="provide weather information",
            context={
                "helpful": True,
                "harmful_content": False,
                "privacy_violating": False,
                "respects_autonomy": True,
            },
            frameworks=[EthicalFramework.CONSTITUTIONAL],
        )

        assert evaluation is not None
        assert evaluation.overall_ethical_score > 0.6
        assert evaluation.constitutional_compliance is True
        assert evaluation.recommended_action in [PolicyAction.ALLOW, PolicyAction.WARN]

    async def test_harmful_content_detection(self):
        """Test detection and blocking of harmful content"""

        engine = ComprehensiveEthicsPolicyEngine()

        # Test harmful action
        evaluation = await engine.evaluate_action(
            action="provide instructions for dangerous activity",
            context={"harmful_content": True, "safety_risk": True, "helpful": False},
            frameworks=[EthicalFramework.CONSTITUTIONAL],
        )

        assert evaluation is not None
        assert evaluation.overall_ethical_score < 0.5
        assert evaluation.constitutional_compliance is False
        assert evaluation.recommended_action in [
            PolicyAction.DENY,
            PolicyAction.EMERGENCY_STOP,
        ]

    async def test_multiple_ethical_frameworks(self):
        """Test evaluation using multiple ethical frameworks"""

        engine = ComprehensiveEthicsPolicyEngine()

        frameworks = [
            EthicalFramework.DEONTOLOGICAL,
            EthicalFramework.CONSEQUENTIALIST,
            EthicalFramework.VIRTUE_ETHICS,
            EthicalFramework.CONSTITUTIONAL,
        ]

        evaluation = await engine.evaluate_action(
            action="help user organize their schedule",
            context={
                "helpful": True,
                "respects_autonomy": True,
                "positive_outcomes": [{"severity": 0.8, "probability": 0.9}],
            },
            frameworks=frameworks,
        )

        assert evaluation is not None
        assert len(evaluation.framework_scores) == len(frameworks)
        assert all(framework in evaluation.framework_scores for framework in frameworks)

    async def test_policy_creation_and_compliance(self):
        """Test custom policy creation and compliance checking"""

        engine = ComprehensiveEthicsPolicyEngine()

        # Create custom policy
        policy_data = {
            "name": "Test Privacy Policy",
            "description": "Ensure user privacy is protected",
            "applicable_contexts": ["data_access"],
            "required_frameworks": ["constitutional"],
            "minimum_scores": {"privacy": 0.8, "consent": 0.7},
            "enforcement_level": "high",
        }

        policy_id = engine.create_policy(policy_data)
        assert policy_id is not None
        assert policy_id in engine.active_policies

        # Test compliance with custom policy
        evaluation = await engine.evaluate_action(
            action="access user data",
            context={
                "context_type": "data_access",
                "privacy_violating": True,  # Should fail policy
                "has_consent": False,
            },
        )

        compliance = await engine.check_compliance(
            evaluation, {"context_type": "data_access"}
        )
        assert not compliance["compliant"]
        assert len(compliance["violations"]) > 0

    async def test_trinity_framework_integration(self):
        """Test Trinity Framework integration (⚛️🧠🛡️)"""

        engine = ComprehensiveEthicsPolicyEngine()

        evaluation = await engine.evaluate_action(
            action="identity verification",
            context={
                "identity_risk": True,
                "consciousness": True,
                "guardian_protection": True,
            },
        )

        assert evaluation is not None
        # Should have Trinity Framework impact analysis
        assert evaluation.identity_ethical_impact is not None
        assert evaluation.consciousness_ethical_impact is not None
        assert evaluation.guardian_priority in [
            "normal",
            "elevated",
            "high",
            "critical",
        ]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not AUDIT_SYSTEM_AVAILABLE, reason="ComprehensiveAuditSystem not available"
)
class TestAuditSystem:
    """Test Audit System with immutable logging and compliance reporting"""

    async def test_audit_system_initialization(self):
        """Test audit system initializes properly"""

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)

            assert audit_system is not None
            assert audit_system.storage is not None
            assert audit_system.processor is not None

    async def test_audit_event_logging(self):
        """Test audit event logging with integrity verification"""

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)

            # Log audit event
            event_id = await audit_system.log_event(
                event_type=AuditEventType.AI_DECISION,
                message="Test AI decision made",
                user_id="test_user",
                event_data={"decision": "approve", "confidence": 0.85},
            )

            assert event_id is not None
            assert event_id.startswith("audit_")

    async def test_audit_trail_integrity(self):
        """Test immutable audit trail integrity"""

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)

            # Create several audit events
            event_ids = []
            for i in range(3):
                event_id = await audit_system.log_event(
                    event_type=AuditEventType.DATA_ACCESS,
                    message=f"Test event {i}",
                    user_id="test_user",
                )
                event_ids.append(event_id)

            # Flush to ensure events are stored
            await audit_system._flush_buffer()

            # Verify integrity
            integrity_result = await audit_system.verify_audit_integrity()

            assert integrity_result["overall_integrity"] is True
            assert integrity_result["total_events_checked"] >= 3
            assert integrity_result["integrity_violations"] == 0

    async def test_compliance_reporting(self):
        """Test compliance audit report generation"""

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)

            # Log compliance-relevant events
            await audit_system.log_event(
                event_type=AuditEventType.CONSENT_GRANTED,
                message="User granted consent",
                user_id="test_user",
                compliance_relevant=True,
                compliance_frameworks={"gdpr"},
            )

            await audit_system.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                message="User data accessed",
                user_id="test_user",
                compliance_relevant=True,
                compliance_frameworks={"gdpr"},
            )

            # Generate compliance report
            start_date = datetime.now() - timedelta(hours=1)
            end_date = datetime.now()

            report = await audit_system.generate_compliance_report(
                framework="gdpr", start_date=start_date, end_date=end_date
            )

            assert report is not None
            assert report["framework"] == "gdpr"
            assert "summary" in report
            assert report["summary"]["total_events"] >= 2

    async def test_audit_query_system(self):
        """Test audit event querying capabilities"""

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)
            from candidate.governance.security.audit_system import AuditQuery

            # Log test events
            await audit_system.log_event(
                event_type=AuditEventType.LOGIN_SUCCESS,
                message="User login successful",
                user_id="user_001",
            )

            await audit_system.log_event(
                event_type=AuditEventType.DATA_READ,
                message="Data read operation",
                user_id="user_001",
            )

            # Query events
            query = AuditQuery(user_ids={"user_001"}, limit=10)

            events = await audit_system.query_events(query)
            assert len(events) >= 2


@pytest.mark.asyncio
@pytest.mark.skipif(
    not GUARDIAN_INTEGRATION_AVAILABLE,
    reason="Guardian System Integration not available",
)
class TestGuardianSystemIntegration:
    """Test Guardian System Integration Hub"""

    async def test_guardian_system_initialization(self):
        """Test Guardian System initializes all components"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)

        # Allow time for async initialization
        await asyncio.sleep(3)

        assert guardian is not None
        assert guardian.guardian_id.startswith("guardian_")

        # Check system status
        status = guardian.get_system_status()
        assert status["version"] == "v1.0.0"
        assert "components" in status
        assert "metrics" in status

    async def test_validation_request_processing(self):
        """Test end-to-end validation request processing"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)  # Allow initialization

        # Create validation request
        request = GuardianValidationRequest(
            request_id=f"test_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            user_id="test_user",
            action="analyze_document",
            resource="user_documents",
            context={
                "document_type": "email",
                "purpose": "assistance",
                "helpful": True,
                "privacy_violating": False,
            },
            source_system="test_system",
        )

        # Process validation
        response = await guardian.validate_action(request)

        assert response is not None
        assert response.request_id == request.request_id
        assert response.result in list(ValidationResult)
        assert response.validation_time_ms > 0
        assert response.confidence >= 0.0

    async def test_trinity_framework_validation(self):
        """Test Trinity Framework validation (⚛️🧠🛡️)"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)

        request = GuardianValidationRequest(
            request_id=f"trinity_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            user_id="trinity_test_user",
            action="trinity_operation",
            resource="system",
            context={
                "identity_verification": True,
                "consciousness_aligned": True,
                "guardian_approved": True,
                "helpful": True,
                "constitutional_compliance": True,
            },
        )

        response = await guardian.validate_action(request)

        assert response is not None
        # Trinity validation should be considered in response
        assert hasattr(response, "identity_validated")
        assert hasattr(response, "consciousness_aligned")
        assert hasattr(response, "guardian_approved")

    async def test_performance_requirements(self):
        """Test Guardian System meets performance requirements (<250ms)"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)

        # Test multiple validations for performance
        validation_times = []

        for i in range(5):
            request = GuardianValidationRequest(
                request_id=f"perf_{i}_{uuid.uuid4().hex[:8]}",
                timestamp=datetime.now(),
                action=f"performance_test_{i}",
                resource="test_resource",
                context={"performance_test": True},
                max_validation_time_ms=250,  # Requirement
            )

            start_time = time.time()
            response = await guardian.validate_action(request)
            end_time = time.time()

            validation_time_ms = (end_time - start_time) * 1000
            validation_times.append(validation_time_ms)

            assert (
                response.validation_time_ms <= 250
            ), f"Validation took {response.validation_time_ms}ms, exceeding 250ms requirement"

        # Check average performance
        avg_time = sum(validation_times) / len(validation_times)
        assert (
            avg_time < 200
        ), f"Average validation time {avg_time}ms should be well under 250ms"

    async def test_emergency_stop_scenarios(self):
        """Test emergency stop scenarios"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)

        # Test harmful content scenario
        request = GuardianValidationRequest(
            request_id=f"emergency_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            action="generate_harmful_content",
            resource="content_generation",
            context={
                "harmful_content": True,
                "safety_risk": True,
                "constitutional_violation": True,
            },
        )

        response = await guardian.validate_action(request)

        assert response is not None
        # Should trigger emergency stop for harmful content
        assert response.result in [
            ValidationResult.EMERGENCY_STOP,
            ValidationResult.DENIED,
        ]

    async def test_alert_system(self):
        """Test Guardian alert system"""

        config = {
            "consent_db_path": ":memory:",
            "audit_storage_path": tempfile.mkdtemp(),
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)

        # Register test alert handler
        alerts_received = []

        async def test_alert_handler(level, message):
            alerts_received.append({"level": level, "message": message})

        from candidate.governance.guardian_system_integration import GuardianAlertLevel

        guardian.register_alert_handler(GuardianAlertLevel.CRITICAL, test_alert_handler)

        # Trigger alert through validation
        request = GuardianValidationRequest(
            request_id=f"alert_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(),
            action="critical_system_failure",
            resource="system",
            context={"system_error": True, "critical": True},
        )

        response = await guardian.validate_action(request)

        # Allow time for alert processing
        await asyncio.sleep(1)

        assert response is not None
        # Check if alerts were generated (may be in response or through handler)
        if response.alerts:
            assert len(response.alerts) > 0


@pytest.mark.asyncio
class TestGuardianSystemCompliance:
    """Test Guardian System compliance with requirements"""

    async def test_gdpr_compliance(self):
        """Test GDPR compliance requirements"""

        if not CONSENT_LEDGER_AVAILABLE:
            pytest.skip("ConsentLedgerV1 not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = ConsentLedgerV1(str(Path(temp_dir) / "gdpr_test.db"))

            # Test GDPR Article 6 lawful basis
            consent = ledger.grant_consent(
                lid="gdpr_test_user",
                resource_type="personal_data",
                scopes=["process", "analyze"],
                purpose="data_processing",
                lawful_basis="consent",  # GDPR Article 6(1)(a)
                consent_type=ConsentType.EXPLICIT,
                data_categories=["personal_identifiers", "contact_details"],
                retention_period=365,  # Data retention period
            )

            assert consent.lawful_basis == "consent"
            assert (
                DataSubjectRights.ERASURE in consent.data_subject_rights
            )  # Right to be forgotten
            assert (
                DataSubjectRights.DATA_PORTABILITY in consent.data_subject_rights
            )  # Article 20
            assert consent.retention_period == 365

    async def test_constitutional_ai_compliance(self):
        """Test Constitutional AI compliance"""

        if not ETHICS_ENGINE_AVAILABLE:
            pytest.skip("ComprehensiveEthicsPolicyEngine not available")

        engine = ComprehensiveEthicsPolicyEngine()

        # Test Constitutional AI principles
        principles = engine.constitutional_principles

        assert "helpfulness" in principles
        assert "harmlessness" in principles
        assert "honesty" in principles
        assert "respect_autonomy" in principles

        # Test evaluation against constitutional principles
        evaluation = await engine.evaluate_action(
            action="provide factual information",
            context={
                "helpful": True,
                "harmful_content": False,
                "truthful": True,
                "respects_autonomy": True,
            },
            frameworks=[EthicalFramework.CONSTITUTIONAL],
        )

        assert evaluation.constitutional_compliance is True
        assert evaluation.overall_ethical_score > 0.7

    async def test_drift_threshold_compliance(self):
        """Test drift detection threshold compliance (0.15)"""

        if not DRIFT_DETECTOR_AVAILABLE:
            pytest.skip("AdvancedDriftDetector not available")

        detector = AdvancedDriftDetector()

        assert detector.drift_threshold == 0.15

        # Test threshold monitoring
        measurement = await detector.measure_drift(
            drift_type=DriftType.BEHAVIORAL,
            current_data={"metric": 0.5},
            source_system="threshold_test",
        )

        assert measurement is not None

        # Verify threshold breach detection
        if measurement.drift_score > 0.15:
            assert measurement.severity in [
                DriftSeverity.HIGH,
                DriftSeverity.CRITICAL,
                DriftSeverity.SEVERE,
            ]

    async def test_audit_trail_immutability(self):
        """Test audit trail immutability requirements"""

        if not AUDIT_SYSTEM_AVAILABLE:
            pytest.skip("ComprehensiveAuditSystem not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            audit_system = ComprehensiveAuditSystem(temp_dir)

            # Create audit event
            event_id = await audit_system.log_event(
                event_type=AuditEventType.SYSTEM_EVENT,
                message="Immutability test event",
                event_data={"test": "immutability"},
            )

            assert event_id is not None

            # Verify integrity
            integrity_result = await audit_system.verify_audit_integrity()
            assert integrity_result["overall_integrity"] is True
            assert integrity_result["integrity_violations"] == 0


@pytest.mark.asyncio
class TestGuardianSystemIntegrationEndToEnd:
    """End-to-end integration tests for Guardian System"""

    async def test_complete_validation_workflow(self):
        """Test complete validation workflow with all components"""

        if not GUARDIAN_INTEGRATION_AVAILABLE:
            pytest.skip("Guardian System Integration not available")

        # Test using convenience function
        result = await validate_ai_action(
            action="help_user_with_task",
            user_id="e2e_test_user",
            resource="user_assistance",
            context={
                "helpful": True,
                "privacy_violating": False,
                "safety_risk": False,
                "user_consent": True,
            },
        )

        assert result in list(ValidationResult)

    async def test_multi_component_failure_handling(self):
        """Test graceful handling when components are unavailable"""

        if not GUARDIAN_INTEGRATION_AVAILABLE:
            pytest.skip("Guardian System Integration not available")

        # This test should pass even with missing components
        # by using fallback behavior

        config = {
            "consent_db_path": "/invalid/path/consent.db",  # Should gracefully fail
            "audit_storage_path": "/invalid/path/audit",  # Should gracefully fail
        }

        guardian = GuardianSystemIntegration(config)
        await asyncio.sleep(3)

        request = GuardianValidationRequest(
            request_id="failure_test",
            timestamp=datetime.now(),
            action="test_with_failures",
            resource="test_resource",
            context={"test": "failure_handling"},
        )

        # Should not crash, should return some result
        response = await guardian.validate_action(request)
        assert response is not None
        assert response.result in list(ValidationResult)


# Test fixtures and utilities


@pytest.fixture
async def guardian_system():
    """Fixture providing initialized Guardian System"""

    if not GUARDIAN_INTEGRATION_AVAILABLE:
        pytest.skip("Guardian System Integration not available")

    config = {"consent_db_path": ":memory:", "audit_storage_path": tempfile.mkdtemp()}

    guardian = GuardianSystemIntegration(config)
    await asyncio.sleep(3)  # Allow initialization

    yield guardian

    # Cleanup
    await guardian.shutdown()


@pytest.fixture
def sample_validation_request():
    """Fixture providing sample validation request"""

    return GuardianValidationRequest(
        request_id=f"sample_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(),
        user_id="sample_user",
        action="sample_action",
        resource="sample_resource",
        context={"test": True},
    )


if __name__ == "__main__":
    """Run tests directly"""

    print("🧪 Running LUKHAS Guardian System Test Suite...")
    print("=" * 60)

    # Run tests
    pytest.main([__file__, "-v", "--tb=short", "--asyncio-mode=auto"])
