"""
Tests for Global Institutional Compliance Framework

ΛTAG: test_global_compliance
"""

from typing import Any, Dict

import pytest

from orchestration_src.brain.GlobalInstitutionalFramework import (
    ComplianceLevel,
    DataCategory,
    GlobalComplianceConfig,
    GlobalConsentData,
    GlobalInstitutionalInput,
    GlobalInstitutionalModule,
    GlobalInstitutionalOutput,
    InstitutionalProcessingRecord,
    Jurisdiction,
    LegalBasis,
)


class MockGlobalReasoner:
    """Mock reasoner for testing"""

    def process(self, inputs: GlobalInstitutionalInput) -> Dict[str, Any]:
        """Mock processing"""
        return {"status": "processed", "compliance_score": 0.85, "data_quality": 0.95}

    def explain_decision(
        self, inputs: GlobalInstitutionalInput, results: Dict[str, Any]
    ) -> str:
        """Mock explanation"""
        return "Decision based on institutional compliance requirements across all applicable jurisdictions."

    def assess_bias(
        self, inputs: GlobalInstitutionalInput, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock bias assessment"""
        return {
            "bias_detected": False,
            "fairness_score": 0.96,
            "demographic_parity": True,
            "equalized_odds": True,
        }

    def validate_compliance(
        self, inputs: GlobalInstitutionalInput, results: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Mock compliance validation"""
        compliance = {}
        for jurisdiction in inputs.applicable_jurisdictions:
            compliance[jurisdiction.value] = {
                "compliant": True,
                "score": 0.9,
                "issues": [],
            }
        return compliance

    def get_confidence(self) -> float:
        """Mock confidence"""
        return 0.92


class TestGlobalModule(GlobalInstitutionalModule):
    """Test implementation of global institutional module"""

    def _get_module_type(self) -> str:
        return "test_global_module"

    def _evaluate_jurisdictional_compliance(
        self,
        jurisdiction: Jurisdiction,
        result: Dict[str, Any],
        inputs: GlobalInstitutionalInput,
    ) -> float:
        """Evaluate compliance for specific jurisdiction"""
        base_score = 85.0

        # Adjust based on jurisdiction
        if jurisdiction == Jurisdiction.EU:
            if inputs.consent.consent_given:
                base_score += 10.0
            if inputs.data_minimization_applied:
                base_score += 5.0

        elif jurisdiction == Jurisdiction.US:
            if inputs.consent.opt_out_available:
                base_score += 10.0
            if not inputs.consent.do_not_sell:
                base_score += 5.0

        elif jurisdiction == Jurisdiction.CN:
            # China has specific data localization requirements
            if not inputs.processing_record.cross_border_transfers:
                base_score += 10.0

        return min(base_score, 100.0)


class TestGlobalComplianceConfig:
    """Test global compliance configuration"""

    def test_default_config(self):
        """Test default configuration"""
        config = GlobalComplianceConfig()

        assert config.primary_jurisdiction == Jurisdiction.GLOBAL
        assert Jurisdiction.EU in config.applicable_jurisdictions
        assert Jurisdiction.US in config.applicable_jurisdictions

        assert config.data_protection_enabled is True
        assert config.cross_border_transfers is True
        assert config.ai_governance_enabled is True
        assert config.ai_transparency_required is True

        assert config.healthcare_mode is False
        assert config.financial_mode is False

        assert config.data_retention_days == 365
        assert config.audit_retention_years == 7

    def test_healthcare_config(self):
        """Test healthcare-specific configuration"""
        config = GlobalComplianceConfig(
            healthcare_mode=True,
            phi_protection=True,
            primary_jurisdiction=Jurisdiction.US,
        )

        assert config.healthcare_mode is True
        assert config.phi_protection is True
        assert config.primary_jurisdiction == Jurisdiction.US

    def test_financial_config(self):
        """Test financial-specific configuration"""
        config = GlobalComplianceConfig(
            financial_mode=True, sox_compliance=True, pci_dss_compliance=True
        )

        assert config.financial_mode is True
        assert config.sox_compliance is True
        assert config.pci_dss_compliance is True


class TestGlobalConsentData:
    """Test multi-jurisdictional consent management"""

    def test_multi_jurisdiction_consent(self):
        """Test consent across multiple jurisdictions"""
        consent = GlobalConsentData(
            data_subject_id="global_user_001",
            jurisdictions=[Jurisdiction.EU, Jurisdiction.US, Jurisdiction.CA],
            purposes=["service_provision", "analytics"],
            legal_basis=LegalBasis.CONSENT,
            consent_given=True,
            opt_out_available=True,  # US requirement
            do_not_sell=False,  # CCPA
            withdrawal_possible=True,  # EU requirement
            cross_border_consent=True,
        )

        assert len(consent.jurisdictions) == 3
        assert Jurisdiction.EU in consent.jurisdictions
        assert consent.opt_out_available is True
        assert consent.withdrawal_possible is True
        assert consent.cross_border_consent is True

    def test_us_specific_consent(self):
        """Test US-specific consent features"""
        consent = GlobalConsentData(
            data_subject_id="us_user_001",
            jurisdictions=[Jurisdiction.US],
            purposes=["marketing"],
            legal_basis=LegalBasis.BUSINESS_PURPOSE,
            consent_given=True,
            opt_out_available=True,
            do_not_sell=True,  # User opted out of data sale
        )

        assert consent.do_not_sell is True
        assert consent.legal_basis == LegalBasis.BUSINESS_PURPOSE


class TestInstitutionalProcessingRecord:
    """Test institutional processing records"""

    def test_multi_jurisdiction_processing(self):
        """Test processing record for multiple jurisdictions"""
        record = InstitutionalProcessingRecord(
            purposes=["global_analytics"],
            legal_basis=LegalBasis.LEGITIMATE_INTERESTS,
            data_categories=[DataCategory.PERSONAL_DATA, DataCategory.BEHAVIORAL_DATA],
            applicable_jurisdictions=[
                Jurisdiction.EU,
                Jurisdiction.US,
                Jurisdiction.UK,
            ],
            cross_border_transfers=["US", "UK"],
            adequacy_decisions=["UK", "CH"],
            security_classification="CONFIDENTIAL",
        )

        assert len(record.applicable_jurisdictions) == 3
        assert len(record.cross_border_transfers) == 2
        assert record.security_classification == "CONFIDENTIAL"
        assert "role_based_access" in record.access_controls

    def test_healthcare_processing(self):
        """Test healthcare-specific processing"""
        record = InstitutionalProcessingRecord(
            purposes=["patient_care", "medical_research"],
            legal_basis=LegalBasis.VITAL_INTERESTS,
            data_categories=[DataCategory.HEALTH_DATA],
            applicable_jurisdictions=[Jurisdiction.US],
            healthcare_phi=True,
            security_classification="HIGHLY_CONFIDENTIAL",
        )

        assert record.healthcare_phi is True
        assert DataCategory.HEALTH_DATA in record.data_categories
        assert record.security_classification == "HIGHLY_CONFIDENTIAL"


class TestGlobalInstitutionalModule:
    """Test global institutional module functionality"""

    @pytest.fixture
    def test_module(self):
        """Create test module instance"""
        reasoner = MockGlobalReasoner()
        config = GlobalComplianceConfig()
        return TestGlobalModule(reasoner, config)

    @pytest.fixture
    def global_input(self):
        """Create test input"""
        consent = GlobalConsentData(
            data_subject_id="global_test_001",
            jurisdictions=[Jurisdiction.EU, Jurisdiction.US],
            purposes=["service_provision"],
            legal_basis=LegalBasis.CONTRACT,
            consent_given=True,
            opt_out_available=True,
            withdrawal_possible=True,
        )

        processing_record = InstitutionalProcessingRecord(
            purposes=["service_provision"],
            legal_basis=LegalBasis.CONTRACT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.EU, Jurisdiction.US],
            cross_border_transfers=["US"],
            adequacy_decisions=["EU_SCCs"],
        )

        return GlobalInstitutionalInput(
            data_subject_id="global_test_001",
            consent=consent,
            processing_record=processing_record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[Jurisdiction.EU, Jurisdiction.US],
            data_minimization_applied=True,
            encryption_applied=True,
            context_data={"purpose": "testing"},
        )

    def test_module_initialization(self, test_module):
        """Test module initialization"""
        assert test_module.module_type == "test_global_module"
        assert Jurisdiction.EU in test_module.compliance_frameworks
        assert Jurisdiction.US in test_module.compliance_frameworks
        assert Jurisdiction.GLOBAL in test_module.compliance_frameworks

    def test_process_global_compliance(self, test_module, global_input):
        """Test global compliance processing"""
        output = test_module(global_input)

        assert isinstance(output, GlobalInstitutionalOutput)
        assert len(output.compliance_scores) == 2  # EU and US
        assert "EU" in output.compliance_scores
        assert "US" in output.compliance_scores
        assert output.overall_compliance_level in [
            ComplianceLevel.FULL_COMPLIANCE,
            ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
        ]

        # Check jurisdictional compliance
        assert "EU" in output.jurisdictional_compliance
        assert "US" in output.jurisdictional_compliance

        # Check AI governance
        assert output.ai_explanation["transparency_level"] == "institutional_grade"
        assert output.bias_assessment["bias_detected"] is False

        # Check data protection
        assert output.retention_compliance is True
        assert output.cross_border_transfer_compliant is True

        # Check institutional features
        assert output.security_classification == "CONFIDENTIAL"
        assert len(output.audit_trail) > 0
        assert output.processing_time_ms > 0

    def test_compliance_validation_failure(self, test_module):
        """Test compliance validation failure"""
        # Create input that violates EU GDPR
        consent = GlobalConsentData(
            data_subject_id="fail_test_001",
            jurisdictions=[Jurisdiction.EU],
            purposes=["marketing"],
            legal_basis=LegalBasis.CONSENT,
            consent_given=False,  # No consent for consent-based processing
            withdrawal_possible=True,
        )

        processing_record = InstitutionalProcessingRecord(
            purposes=["marketing"],
            legal_basis=LegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.EU],
        )

        invalid_input = GlobalInstitutionalInput(
            data_subject_id="fail_test_001",
            consent=consent,
            processing_record=processing_record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[Jurisdiction.EU],
        )

        with pytest.raises(ValueError, match="Institutional compliance violation"):
            test_module(invalid_input)


class TestJurisdictionalCompliance:
    """Test jurisdiction-specific compliance"""

    @pytest.fixture
    def test_module(self):
        """Create test module"""
        reasoner = MockGlobalReasoner()
        config = GlobalComplianceConfig()
        return TestGlobalModule(reasoner, config)

    def test_eu_compliance_scoring(self, test_module):
        """Test EU-specific compliance scoring"""
        consent = GlobalConsentData(
            data_subject_id="eu_test_001",
            jurisdictions=[Jurisdiction.EU],
            purposes=["analytics"],
            legal_basis=LegalBasis.CONSENT,
            consent_given=True,
            withdrawal_possible=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["analytics"],
            legal_basis=LegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.EU],
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="eu_test_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[Jurisdiction.EU],
            data_minimization_applied=True,  # EU requirement
        )

        output = test_module(input_data)

        # EU score should be high due to consent and data minimization
        assert output.compliance_scores["EU"] >= 95.0

    def test_us_compliance_scoring(self, test_module):
        """Test US-specific compliance scoring"""
        consent = GlobalConsentData(
            data_subject_id="us_test_001",
            jurisdictions=[Jurisdiction.US],
            purposes=["service_provision"],
            legal_basis=LegalBasis.BUSINESS_PURPOSE,
            consent_given=True,
            opt_out_available=True,  # CCPA requirement
            do_not_sell=False,  # User has not opted out
        )

        record = InstitutionalProcessingRecord(
            purposes=["service_provision"],
            legal_basis=LegalBasis.BUSINESS_PURPOSE,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.US],
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="us_test_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.US,
            applicable_jurisdictions=[Jurisdiction.US],
        )

        output = test_module(input_data)

        # US score should be high due to opt-out availability
        assert output.compliance_scores["US"] >= 95.0

    def test_china_compliance_scoring(self, test_module):
        """Test China-specific compliance scoring"""
        consent = GlobalConsentData(
            data_subject_id="cn_test_001",
            jurisdictions=[Jurisdiction.CN],
            purposes=["service_provision"],
            legal_basis=LegalBasis.CONSENT,
            consent_given=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["service_provision"],
            legal_basis=LegalBasis.CONSENT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.CN],
            cross_border_transfers=[],  # No cross-border transfers for China
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="cn_test_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.CN,
            applicable_jurisdictions=[Jurisdiction.CN],
        )

        output = test_module(input_data)

        # China score should be high due to no cross-border transfers
        assert output.compliance_scores["CN"] >= 95.0


class TestCrossBorderCompliance:
    """Test cross-border data transfer compliance"""

    @pytest.fixture
    def test_module(self):
        """Create test module"""
        reasoner = MockGlobalReasoner()
        config = GlobalComplianceConfig()
        return TestGlobalModule(reasoner, config)

    def test_adequacy_decision_transfers(self, test_module):
        """Test transfers to countries with adequacy decisions"""
        consent = GlobalConsentData(
            data_subject_id="transfer_test_001",
            jurisdictions=[Jurisdiction.EU],
            purposes=["global_service"],
            legal_basis=LegalBasis.CONTRACT,
            consent_given=True,
            cross_border_consent=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["global_service"],
            legal_basis=LegalBasis.CONTRACT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.EU],
            cross_border_transfers=["UK", "CH"],  # Countries with EU adequacy
            adequacy_decisions=["UK", "CH"],
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="transfer_test_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[Jurisdiction.EU],
        )

        output = test_module(input_data)

        assert output.cross_border_transfer_compliant is True

    def test_invalid_cross_border_transfer(self, test_module):
        """Test invalid cross-border transfer without consent"""
        consent = GlobalConsentData(
            data_subject_id="transfer_test_002",
            jurisdictions=[Jurisdiction.EU],
            purposes=["global_service"],
            legal_basis=LegalBasis.CONTRACT,
            consent_given=True,
            cross_border_consent=False,  # No consent for cross-border
        )

        record = InstitutionalProcessingRecord(
            purposes=["global_service"],
            legal_basis=LegalBasis.CONTRACT,
            data_categories=[DataCategory.PERSONAL_DATA],
            applicable_jurisdictions=[Jurisdiction.EU],
            cross_border_transfers=["US"],  # Transfer without consent
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="transfer_test_002",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[Jurisdiction.EU],
        )

        output = test_module(input_data)

        assert output.cross_border_transfer_compliant is False


class TestSectorSpecificCompliance:
    """Test sector-specific compliance (healthcare, financial)"""

    def test_healthcare_compliance(self):
        """Test healthcare-specific compliance (HIPAA)"""
        config = GlobalComplianceConfig(healthcare_mode=True, phi_protection=True)

        reasoner = MockGlobalReasoner()
        module = TestGlobalModule(reasoner, config)

        consent = GlobalConsentData(
            data_subject_id="patient_001",
            jurisdictions=[Jurisdiction.US],
            purposes=["treatment", "payment", "operations"],
            legal_basis=LegalBasis.VITAL_INTERESTS,
            consent_given=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["treatment"],
            legal_basis=LegalBasis.VITAL_INTERESTS,
            data_categories=[DataCategory.HEALTH_DATA],
            applicable_jurisdictions=[Jurisdiction.US],
            healthcare_phi=True,
            security_classification="HIGHLY_CONFIDENTIAL",
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="patient_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.US,
            applicable_jurisdictions=[Jurisdiction.US],
        )

        output = module(input_data)

        assert output.overall_compliance_level in [
            ComplianceLevel.FULL_COMPLIANCE,
            ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
        ]
        assert output.security_classification == "HIGHLY_CONFIDENTIAL"

    def test_financial_compliance(self):
        """Test financial-specific compliance (SOX, PCI-DSS)"""
        config = GlobalComplianceConfig(
            financial_mode=True, sox_compliance=True, pci_dss_compliance=True
        )

        reasoner = MockGlobalReasoner()
        module = TestGlobalModule(reasoner, config)

        consent = GlobalConsentData(
            data_subject_id="customer_001",
            jurisdictions=[Jurisdiction.US],
            purposes=["payment_processing", "fraud_detection"],
            legal_basis=LegalBasis.CONTRACT,
            consent_given=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["payment_processing"],
            legal_basis=LegalBasis.CONTRACT,
            data_categories=[DataCategory.FINANCIAL_DATA],
            applicable_jurisdictions=[Jurisdiction.US],
            financial_pii=True,
            security_classification="HIGHLY_CONFIDENTIAL",
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="customer_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.US,
            applicable_jurisdictions=[Jurisdiction.US],
        )

        output = module(input_data)

        assert output.overall_compliance_level in [
            ComplianceLevel.FULL_COMPLIANCE,
            ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
        ]
        assert output.institutional_certification["enterprise_grade"] is True
        assert output.institutional_certification["government_ready"] is True


@pytest.mark.integration
class TestGlobalIntegration:
    """Integration tests for global institutional framework"""

    def test_multi_jurisdiction_processing(self):
        """Test processing across multiple jurisdictions"""
        config = GlobalComplianceConfig(
            primary_jurisdiction=Jurisdiction.GLOBAL,
            applicable_jurisdictions=[
                Jurisdiction.EU,
                Jurisdiction.US,
                Jurisdiction.UK,
                Jurisdiction.CA,
            ],
        )

        reasoner = MockGlobalReasoner()
        module = TestGlobalModule(reasoner, config)

        # Create complex multi-jurisdiction scenario
        consent = GlobalConsentData(
            data_subject_id="global_customer_001",
            jurisdictions=[
                Jurisdiction.EU,
                Jurisdiction.US,
                Jurisdiction.UK,
                Jurisdiction.CA,
            ],
            purposes=["global_service_delivery", "analytics", "personalization"],
            legal_basis=LegalBasis.CONTRACT,
            consent_given=True,
            opt_out_available=True,  # US requirement
            do_not_sell=False,  # CCPA
            withdrawal_possible=True,  # EU requirement
            cross_border_consent=True,
        )

        record = InstitutionalProcessingRecord(
            purposes=["global_service_delivery"],
            legal_basis=LegalBasis.CONTRACT,
            data_categories=[
                DataCategory.PERSONAL_DATA,
                DataCategory.BEHAVIORAL_DATA,
                DataCategory.LOCATION_DATA,
            ],
            applicable_jurisdictions=[
                Jurisdiction.EU,
                Jurisdiction.US,
                Jurisdiction.UK,
                Jurisdiction.CA,
            ],
            cross_border_transfers=["US", "UK", "CA"],
            adequacy_decisions=["UK", "CA"],
            security_classification="CONFIDENTIAL",
        )

        input_data = GlobalInstitutionalInput(
            data_subject_id="global_customer_001",
            consent=consent,
            processing_record=record,
            primary_jurisdiction=Jurisdiction.EU,
            applicable_jurisdictions=[
                Jurisdiction.EU,
                Jurisdiction.US,
                Jurisdiction.UK,
                Jurisdiction.CA,
            ],
            data_minimization_applied=True,
            pseudonymization_applied=True,
            encryption_applied=True,
            context_data={
                "service": "global_platform",
                "user_location": "EU",
                "processing_location": "distributed",
            },
        )

        output = module(input_data)

        # Verify multi-jurisdiction compliance
        assert len(output.compliance_scores) == 4
        assert all(score >= 80.0 for score in output.compliance_scores.values())

        # Verify subject rights mapping
        assert "EU" in output.subject_rights_available
        assert "erasure" in output.subject_rights_available["EU"]
        assert "US" in output.subject_rights_available
        assert "opt_out" in output.subject_rights_available["US"]

        # Verify institutional certification
        assert output.institutional_certification["standards_met"] == [
            "ISO27001",
            "SOC2_Type2",
            "Multi_Jurisdictional",
        ]
        assert output.institutional_certification["audit_ready"] is True

        # Verify compliance attestation
        assert "institutional-grade compliance" in output.compliance_attestation
        assert "4 jurisdictions" in output.compliance_attestation


if __name__ == "__main__":
    print("Running Global Institutional Framework Compliance Tests...")
    pytest.main([__file__, "-v"])
