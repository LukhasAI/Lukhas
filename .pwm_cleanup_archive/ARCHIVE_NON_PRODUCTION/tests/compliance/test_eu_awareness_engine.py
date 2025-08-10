"""
Tests for EU Awareness Engine - GDPR & AI Act Compliance

ΛTAG: test_eu_compliance
"""

from datetime import datetime, timezone

import pytest

from orchestration_src.brain.EUAwarenessEngine import (
    AIRiskLevel,
    ComplianceStatus,
    ConsentData,
    DataCategory,
    DataProcessingRecord,
    DataSubjectRights,
    EUAwarenessEngine,
    EUAwarenessInput,
    EUAwarenessOutput,
    EUConfig,
    GDPRLegalBasis,
)


class TestEUConfig:
    """Test EU configuration settings"""

    def test_default_config(self):
        """Test default EU configuration"""
        config = EUConfig()

        assert config.gdpr_enabled is True
        assert config.data_retention_days == 365
        assert config.anonymization_enabled is True
        assert config.pseudonymization_enabled is True
        assert config.consent_required is True

        assert config.ai_act_compliance is True
        assert config.ai_risk_level == AIRiskLevel.LIMITED_RISK
        assert config.algorithmic_transparency is True
        assert config.bias_monitoring is True

        assert config.encryption_at_rest is True
        assert config.encryption_in_transit is True
        assert config.data_minimization is True
        assert config.purpose_limitation is True

    def test_custom_config(self):
        """Test custom EU configuration"""
        config = EUConfig(
            data_retention_days=180,
            ai_risk_level=AIRiskLevel.HIGH_RISK,
            dpo_contact="dpo@test.eu",
        )

        assert config.data_retention_days == 180
        assert config.ai_risk_level == AIRiskLevel.HIGH_RISK
        assert config.dpo_contact == "dpo@test.eu"


class TestConsentManagement:
    """Test GDPR consent management"""

    def test_consent_creation(self):
        """Test consent data creation"""
        consent = ConsentData(
            data_subject_id="eu_citizen_001",
            purposes=["analytics", "personalization"],
            legal_basis=GDPRLegalBasis.CONSENT,
            consent_given=True,
        )

        assert consent.data_subject_id == "eu_citizen_001"
        assert len(consent.purposes) == 2
        assert consent.legal_basis == GDPRLegalBasis.CONSENT
        assert consent.consent_given is True
        assert consent.withdrawal_possible is True
        assert consent.consent_version == "1.0"

    def test_consent_withdrawal(self):
        """Test consent withdrawal scenario"""
        consent = ConsentData(
            data_subject_id="eu_citizen_002",
            purposes=["marketing"],
            legal_basis=GDPRLegalBasis.CONSENT,
            consent_given=False,  # Withdrawn
        )

        assert consent.consent_given is False
        assert consent.withdrawal_possible is True


class TestDataProcessingRecord:
    """Test GDPR Article 30 processing records"""

    def test_processing_record_creation(self):
        """Test processing record creation"""
        record = DataProcessingRecord(
            purposes=["service_provision"],
            legal_basis=GDPRLegalBasis.CONTRACT,
            data_categories=[DataCategory.PERSONAL_DATA],
            retention_period=730,
        )

        assert record.controller == "Lukhas_AI_Systems_EU"
        assert record.processor == "EU_Awareness_Engine"
        assert "service_provision" in record.purposes
        assert record.legal_basis == GDPRLegalBasis.CONTRACT
        assert DataCategory.PERSONAL_DATA in record.data_categories
        assert record.retention_period == 730
        assert "encryption" in record.security_measures


class TestEUAwarenessEngine:
    """Test main EU Awareness Engine"""

    @pytest.fixture
    def eu_engine(self):
        """Create EU Awareness Engine instance"""
        config = EUConfig(
            gdpr_enabled=True, ai_act_compliance=True, dpo_contact="dpo@lukhas-test.eu"
        )
        return EUAwarenessEngine(config)

    @pytest.fixture
    def valid_eu_input(self):
        """Create valid EU input"""
        consent = ConsentData(
            data_subject_id="test_subject_001",
            purposes=["environmental_monitoring"],
            legal_basis=GDPRLegalBasis.CONSENT,
            consent_given=True,
        )

        processing_record = DataProcessingRecord(
            purposes=["environmental_monitoring"],
            legal_basis=GDPRLegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA],
            retention_period=365,
        )

        return EUAwarenessInput(
            data_subject_id="test_subject_001",
            consent=consent,
            processing_record=processing_record,
            eu_member_state="DE",
            context_data={"temperature": 22.0, "location_type": "office"},
        )

    def test_engine_initialization(self, eu_engine):
        """Test engine initialization"""
        assert eu_engine.config.gdpr_enabled is True
        assert eu_engine.config.ai_act_compliance is True
        assert "environmental" in eu_engine.modules
        assert len(eu_engine.processing_registry["processing_activities"]) == 0

    def test_process_awareness_success(self, eu_engine, valid_eu_input):
        """Test successful awareness processing"""
        output = eu_engine.process_awareness("environmental", valid_eu_input)

        assert isinstance(output, EUAwarenessOutput)
        assert output.compliance_score >= 0.0
        assert output.compliance_score <= 100.0
        assert output.processing_lawfulness is True
        assert output.erasure_possible is True
        assert output.portability_format == "JSON"
        assert output.automated_decision_making is False

    def test_process_awareness_without_consent(self, eu_engine):
        """Test processing without consent"""
        consent = ConsentData(
            data_subject_id="test_subject_002",
            purposes=["analytics"],
            legal_basis=GDPRLegalBasis.CONSENT,
            consent_given=False,  # No consent given
        )

        processing_record = DataProcessingRecord(
            purposes=["analytics"],
            legal_basis=GDPRLegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA],
        )

        invalid_input = EUAwarenessInput(
            data_subject_id="test_subject_002",
            consent=consent,
            processing_record=processing_record,
            eu_member_state="FR",
        )

        with pytest.raises(ValueError, match="GDPR violation"):
            eu_engine.process_awareness("environmental", invalid_input)

    def test_legitimate_interest_processing(self, eu_engine):
        """Test processing under legitimate interest"""
        consent = ConsentData(
            data_subject_id="test_subject_003",
            purposes=["security_monitoring"],
            legal_basis=GDPRLegalBasis.LEGITIMATE_INTERESTS,
            consent_given=True,  # Not required for legitimate interest
        )

        processing_record = DataProcessingRecord(
            purposes=["security_monitoring"],
            legal_basis=GDPRLegalBasis.LEGITIMATE_INTERESTS,
            data_categories=[DataCategory.PERSONAL_DATA],
        )

        input_data = EUAwarenessInput(
            data_subject_id="test_subject_003",
            consent=consent,
            processing_record=processing_record,
            eu_member_state="ES",
        )

        output = eu_engine.process_awareness("environmental", input_data)
        assert output.processing_lawfulness is True
        assert output.compliance_status == ComplianceStatus.COMPLIANT


class TestDataSubjectRights:
    """Test GDPR data subject rights implementation"""

    @pytest.fixture
    def eu_engine_with_data(self):
        """Create engine with some processing data"""
        engine = EUAwarenessEngine()

        # Add some processing activities
        for i in range(3):
            activity = {
                "id": f"activity_{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "module_type": "environmental",
                "data_subject_id": "test_subject_001",
                "purposes": ["environmental_monitoring"],
                "legal_basis": "consent",
                "data_categories": ["personal_data"],
            }
            engine.processing_registry["processing_activities"].append(activity)

        # Add consent record
        engine.processing_registry["consent_records"]["test_subject_001"] = {
            "consent_given": True,
            "purposes": ["environmental_monitoring"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return engine

    def test_access_request(self, eu_engine_with_data):
        """Test GDPR Article 15 access request"""
        result = eu_engine_with_data.exercise_data_subject_rights(
            DataSubjectRights.ACCESS, "test_subject_001"
        )

        assert result["status"] == "completed"
        assert result["data_subject_id"] == "test_subject_001"
        assert len(result["processing_activities"]) == 3
        assert "rights_information" in result
        assert result["rights_information"]["erasure"] == "available"

    def test_erasure_request(self, eu_engine_with_data):
        """Test GDPR Article 17 erasure request (Right to be forgotten)"""
        # Verify data exists
        initial_count = len(
            eu_engine_with_data.processing_registry["processing_activities"]
        )
        assert initial_count == 3

        # Exercise right to erasure
        result = eu_engine_with_data.exercise_data_subject_rights(
            DataSubjectRights.ERASURE, "test_subject_001"
        )

        assert result["status"] == "completed"
        assert result["erasure_scope"] == "complete"

        # Verify data was erased
        remaining_activities = [
            a
            for a in eu_engine_with_data.processing_registry["processing_activities"]
            if a.get("data_subject_id") == "test_subject_001"
        ]
        assert len(remaining_activities) == 0
        assert (
            "test_subject_001"
            not in eu_engine_with_data.processing_registry["consent_records"]
        )

    def test_data_portability_request(self, eu_engine_with_data):
        """Test GDPR Article 20 data portability request"""
        result = eu_engine_with_data.exercise_data_subject_rights(
            DataSubjectRights.DATA_PORTABILITY, "test_subject_001"
        )

        assert result["status"] == "completed"
        assert result["format"] == "JSON"
        assert "data" in result
        assert result["data"]["data_subject_id"] == "test_subject_001"
        assert result["transmission_method"] == "secure_download"


class TestComplianceReporting:
    """Test compliance reporting functionality"""

    def test_compliance_report_generation(self):
        """Test comprehensive compliance report"""
        config = EUConfig(
            gdpr_enabled=True,
            ai_act_compliance=True,
            ai_risk_level=AIRiskLevel.HIGH_RISK,
            data_retention_days=180,
            dpo_contact="dpo@lukhas-test.eu",
        )

        engine = EUAwarenessEngine(config)
        report = engine.get_compliance_report()

        assert "gdpr_compliance" in report
        assert report["gdpr_compliance"]["lawfulness_check"] == "passed"
        assert report["gdpr_compliance"]["consent_management"] == "active"
        assert report["gdpr_compliance"]["data_minimization"] is True
        assert report["gdpr_compliance"]["retention_policy"] == "180 days"

        assert "ai_act_compliance" in report
        assert report["ai_act_compliance"]["risk_level"] == "high_risk"
        assert report["ai_act_compliance"]["transparency"] is True
        assert report["ai_act_compliance"]["bias_monitoring"] is True
        assert report["ai_act_compliance"]["conformity_assessment"] == "completed"

        assert "processing_statistics" in report
        assert report["compliance_officer"] == "dpo@lukhas-test.eu"


class TestAIActCompliance:
    """Test EU AI Act specific compliance"""

    def test_high_risk_ai_system(self):
        """Test high-risk AI system compliance"""
        config = EUConfig(
            ai_risk_level=AIRiskLevel.HIGH_RISK,
            algorithmic_transparency=True,
            bias_monitoring=True,
        )

        engine = EUAwarenessEngine(config)

        # Create test input
        consent = ConsentData(
            data_subject_id="test_ai_001",
            purposes=["ai_decision_making"],
            legal_basis=GDPRLegalBasis.CONTRACT,
            consent_given=True,
        )

        processing_record = DataProcessingRecord(
            purposes=["ai_decision_making"],
            legal_basis=GDPRLegalBasis.CONTRACT,
            data_categories=[DataCategory.PERSONAL_DATA],
        )

        input_data = EUAwarenessInput(
            data_subject_id="test_ai_001",
            consent=consent,
            processing_record=processing_record,
            eu_member_state="BE",
        )

        output = engine.process_awareness("environmental", input_data)

        # Verify AI Act compliance features
        assert "decision_logic" in output.ai_explanation
        assert "reasoning_process" in output.ai_explanation
        assert "bias_assessment" in output.ai_explanation
        assert output.ai_risk_assessment["risk_level"] == "high_risk"
        assert len(output.ai_risk_assessment["mitigation_measures"]) > 0
        assert output.ai_risk_assessment["monitoring_required"] is True

    def test_minimal_risk_ai_system(self):
        """Test minimal risk AI system compliance"""
        config = EUConfig(ai_risk_level=AIRiskLevel.MINIMAL_RISK)
        engine = EUAwarenessEngine(config)

        report = engine.get_compliance_report()
        assert report["ai_act_compliance"]["risk_level"] == "minimal_risk"
        assert report["ai_act_compliance"]["conformity_assessment"] == "not_required"


@pytest.mark.integration
class TestIntegration:
    """Integration tests for EU Awareness Engine"""

    def test_full_processing_pipeline(self):
        """Test complete processing pipeline with all features"""
        # Initialize engine with full configuration
        config = EUConfig(
            gdpr_enabled=True,
            ai_act_compliance=True,
            ai_risk_level=AIRiskLevel.LIMITED_RISK,
            data_retention_days=365,
            anonymization_enabled=True,
            pseudonymization_enabled=True,
            encryption_at_rest=True,
            encryption_in_transit=True,
            data_minimization=True,
            audit_logging=True,
            dpo_contact="dpo@lukhas-test.eu",
        )

        engine = EUAwarenessEngine(config)

        # Create comprehensive input
        consent = ConsentData(
            data_subject_id="integration_test_001",
            purposes=["environmental_monitoring", "wellness_optimization"],
            legal_basis=GDPRLegalBasis.CONSENT,
            consent_given=True,
        )

        processing_record = DataProcessingRecord(
            purposes=["environmental_monitoring", "wellness_optimization"],
            legal_basis=GDPRLegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA, DataCategory.LOCATION_DATA],
            recipients=["internal_analytics_team"],
            retention_period=365,
            security_measures=[
                "encryption",
                "pseudonymization",
                "access_controls",
                "audit_logging",
            ],
        )

        input_data = EUAwarenessInput(
            data_subject_id="integration_test_001",
            consent=consent,
            processing_record=processing_record,
            eu_member_state="DE",
            data_minimization_applied=True,
            pseudonymization_applied=True,
            context_data={
                "temperature": 23.5,
                "humidity": 45.0,
                "location_type": "office",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Process awareness
        output = engine.process_awareness("environmental", input_data)

        # Comprehensive assertions
        assert output.compliance_score >= 80.0  # Should have high compliance
        assert output.compliance_status in [
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.MINOR_ISSUE,
        ]
        assert output.processing_lawfulness is True
        assert output.data_accuracy_score >= 0.9
        assert output.retention_compliance is True

        # AI transparency
        assert output.algorithmic_decision_logic != ""
        assert output.bias_detection_results["bias_detected"] is False
        assert output.bias_detection_results["fairness_score"] >= 0.9

        # Audit trail
        assert len(output.audit_trail) >= 3
        assert output.processing_time_ms > 0

        # Test data subject rights on this data
        access_result = engine.exercise_data_subject_rights(
            DataSubjectRights.ACCESS, "integration_test_001"
        )
        assert access_result["status"] == "completed"
        assert len(access_result["processing_activities"]) > 0

        # Test compliance report
        report = engine.get_compliance_report()
        assert report["processing_statistics"]["total_activities"] > 0
        assert report["gdpr_compliance"]["lawfulness_check"] == "passed"
        assert report["ai_act_compliance"]["transparency"] is True


if __name__ == "__main__":
    print("Running EU Awareness Engine Compliance Tests...")
    pytest.main([__file__, "-v"])
