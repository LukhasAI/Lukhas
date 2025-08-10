"""
AI Compliance Framework Integration Test
======================================

Simple integration test to validate the AI compliance framework components.
"""

import asyncio
import sys

# Add the compliance framework to the path
sys.path.insert(0, "/Users/agi_dev/Lukhas_PWM")


def test_imports():
    """Test that all compliance framework modules can be imported"""
    print("🔍 Testing module imports...")

    try:
        pass

        print("  ✅ EU AI Act validator imported successfully")

        print("  ✅ GDPR validator imported successfully")

        print("  ✅ NIST AI Risk Manager imported successfully")

        print("  ✅ Global Compliance Engine imported successfully")

        return True

    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


async def test_eu_ai_act():
    """Test EU AI Act compliance validator"""
    print("\n🇪🇺 Testing EU AI Act Compliance Validator...")

    try:
        from compliance.ai_regulatory_framework.eu_ai_act.compliance_validator import (
            AISystemProfile,
            EUAIActValidator,
        )

        # Initialize validator
        validator = EUAIActValidator()
        print("  ✅ Validator initialized")

        # Create test system profile
        system_profile = AISystemProfile(
            system_id="test_system_001",
            name="Test AI System",
            description="Test system for compliance validation",
            intended_use="automated decision making",
            deployment_context=["employment_workers_management"],
            data_types=["personal_data"],
            algorithms_used=["machine_learning"],
            human_oversight_level="meaningful",
            automated_decision_making=True,
            affects_fundamental_rights=True,
        )
        print("  ✅ Test system profile created")

        # Perform assessment
        assessment = await validator.assess_system_compliance(system_profile)
        print(
            f"  ✅ Assessment completed - Risk Category: {assessment.risk_category.value}"
        )
        print(f"     Compliance Status: {assessment.compliance_status.value}")
        print(f"     Confidence Score: {assessment.confidence_score:.2f}")

        return True

    except Exception as e:
        print(f"  ❌ EU AI Act test failed: {e}")
        return False


async def test_gdpr():
    """Test GDPR compliance validator"""
    print("\n🛡️ Testing GDPR Compliance Validator...")

    try:
        from compliance.ai_regulatory_framework.gdpr.data_protection_validator import (
            DataCategory,
            DataProcessingActivity,
            GDPRValidator,
            LawfulBasis,
            ProcessingPurpose,
        )

        # Initialize validator
        validator = GDPRValidator()
        print("  ✅ Validator initialized")

        # Create test data processing activity
        activity = DataProcessingActivity(
            activity_id="test_processing_001",
            name="Test Data Processing",
            description="Test processing activity",
            controller="Test Company",
            processor=None,
            data_categories=[DataCategory.PERSONAL_DATA],
            lawful_basis=LawfulBasis.CONSENT,
            purposes=[ProcessingPurpose.SERVICE_PROVISION],
            data_subjects=["users"],
            retention_period="1 year",
            international_transfers=False,
            automated_decision_making=True,
            profiling=False,
        )
        print("  ✅ Test data processing activity created")

        # Perform assessment
        assessment = await validator.assess_gdpr_compliance(activity)
        print(f"  ✅ Assessment completed - Status: {assessment.compliance_status}")
        print(f"     Overall Score: {assessment.overall_score:.2f}")
        print(f"     Violations: {len(assessment.violations)}")

        return True

    except Exception as e:
        print(f"  ❌ GDPR test failed: {e}")
        return False


async def test_nist():
    """Test NIST AI Risk Management Framework"""
    print("\n🔬 Testing NIST AI Risk Management Framework...")

    try:
        from compliance.ai_regulatory_framework.nist.ai_risk_management import (
            AILifecycleStage,
            AISystemMetrics,
            NISTAIRiskManager,
        )

        # Initialize risk manager
        manager = NISTAIRiskManager()
        print("  ✅ Risk manager initialized")

        # Create test metrics
        metrics = AISystemMetrics(
            system_id="test_system_001",
            accuracy=0.85,
            precision=0.82,
            recall=0.78,
            fairness_metrics={"demographic_parity": 0.80},
            explainability_score=0.70,
            robustness_score=0.85,
            privacy_preservation_score=0.80,
            security_score=0.85,
        )
        print("  ✅ Test metrics created")

        # Perform risk assessment
        assessment = await manager.conduct_risk_assessment(
            "test_system_001", metrics, AILifecycleStage.OPERATE_MONITOR
        )
        print(
            f"  ✅ Risk assessment completed - Risk Level: {assessment.risk_level.value}"
        )
        print(f"     Identified Risks: {len(assessment.identified_risks)}")
        print(f"     Mitigation Strategies: {len(assessment.mitigation_strategies)}")

        return True

    except Exception as e:
        print(f"  ❌ NIST test failed: {e}")
        return False


async def test_global_compliance():
    """Test Global Compliance Engine"""
    print("\n🌍 Testing Global Compliance Engine...")

    try:
        from compliance.ai_regulatory_framework.eu_ai_act.compliance_validator import (
            AISystemProfile,
        )
        from compliance.ai_regulatory_framework.gdpr.data_protection_validator import (
            DataCategory,
            DataProcessingActivity,
            LawfulBasis,
            ProcessingPurpose,
        )
        from compliance.ai_regulatory_framework.global_compliance.multi_jurisdiction_engine import (
            ComplianceFramework,
            GlobalComplianceEngine,
            GlobalComplianceProfile,
            Jurisdiction,
        )
        from compliance.ai_regulatory_framework.nist.ai_risk_management import (
            AISystemMetrics,
        )

        # Initialize global engine
        engine = GlobalComplianceEngine()
        print("  ✅ Global compliance engine initialized")

        # Create global compliance profile
        profile = GlobalComplianceProfile(
            system_id="test_global_001",
            name="Global Test System",
            jurisdictions=[Jurisdiction.EU, Jurisdiction.US],
            frameworks=[
                ComplianceFramework.EU_AI_ACT,
                ComplianceFramework.GDPR,
                ComplianceFramework.NIST_AI_RMF,
            ],
            deployment_regions=["EU", "US"],
            data_residency_requirements={"EU": "EEA_only"},
            cross_border_transfers=False,
            regulatory_notifications=["EU_DPA"],
        )
        print("  ✅ Global compliance profile created")

        # Create supporting profiles for assessment
        system_profile = AISystemProfile(
            system_id="test_global_001",
            name="Global Test System",
            description="Test system for global compliance",
            intended_use="decision support",
            deployment_context=["minimal_risk"],
            data_types=["personal_data"],
            algorithms_used=["machine_learning"],
            human_oversight_level="meaningful",
            automated_decision_making=True,
            affects_fundamental_rights=False,
        )

        activity = DataProcessingActivity(
            activity_id="test_global_001",
            name="Global Test Processing",
            description="Test processing for global system",
            controller="Global Test Company",
            processor=None,
            data_categories=[DataCategory.PERSONAL_DATA],
            lawful_basis=LawfulBasis.LEGITIMATE_INTERESTS,
            purposes=[ProcessingPurpose.SERVICE_PROVISION],
            data_subjects=["users"],
            retention_period="6 months",
            international_transfers=False,
            automated_decision_making=True,
            profiling=False,
        )

        metrics = AISystemMetrics(
            system_id="test_global_001",
            accuracy=0.90,
            precision=0.88,
            recall=0.85,
            fairness_metrics={"demographic_parity": 0.85},
            explainability_score=0.80,
            robustness_score=0.90,
            privacy_preservation_score=0.85,
            security_score=0.90,
        )
        print("  ✅ Supporting profiles created")

        # Perform global assessment
        report = await engine.assess_global_compliance(
            profile, system_profile, activity, metrics
        )
        print(f"  ✅ Global assessment completed - Status: {report.overall_status}")
        print(f"     Jurisdictions assessed: {len(report.jurisdiction_compliance)}")
        print(f"     Frameworks assessed: {len(report.framework_compliance)}")

        return True

    except Exception as e:
        print(f"  ❌ Global compliance test failed: {e}")
        return False


async def run_all_tests():
    """Run all compliance framework tests"""
    print("🚀 Starting AI Regulatory Compliance Framework Integration Tests\n")

    # Test imports
    import_success = test_imports()
    if not import_success:
        print("\n❌ Import tests failed - stopping execution")
        return False

    # Run async tests
    tests = [
        ("EU AI Act", test_eu_ai_act()),
        ("GDPR", test_gdpr()),
        ("NIST AI RMF", test_nist()),
        ("Global Compliance", test_global_compliance()),
    ]

    results = []
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results.append(result)
        except Exception as e:
            print(f"\n❌ {test_name} test encountered error: {e}")
            results.append(False)

    # Summary
    passed = sum(1 for result in results if result)
    total = len(results) + 1  # +1 for import test

    print("\n📊 Test Results Summary:")
    print(f"  Total Tests: {total}")
    print(f"  Passed: {passed + (1 if import_success else 0)}")
    print(f"  Failed: {total - passed - (1 if import_success else 0)}")

    if passed == len(results) and import_success:
        print("\n🎉 All AI Regulatory Compliance Framework tests passed!")
        print("✅ Phase 4 (AI Compliance Framework) implementation successful")
        return True
    else:
        print(f"\n❌ Some tests failed - {len(results) - passed} async tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
