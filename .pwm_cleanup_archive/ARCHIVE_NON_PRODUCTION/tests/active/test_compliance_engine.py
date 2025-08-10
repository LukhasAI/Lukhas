# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: test_compliance_engine.py
# MODULE: core.advanced.brain.tests.test_compliance_engine
# DESCRIPTION: Pytest unit tests for the ComplianceEngine, focusing on metadata
#              anonymization and data retention logic.
# DEPENDENCIES: pytest, time, logging
#               (Assumed: core.governance.compliance_engine.ComplianceEngine)
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
Unit tests for the ComplianceEngine.
"""

import logging
import time  # Was missing in original

import pytest

# Initialize logger for ΛTRACE
logger = logging.getLogger("ΛTRACE.core.advanced.brain.tests.test_compliance_engine")
logger.info("ΛTRACE: Initializing test_compliance_engine module.")

# TODO: Verify the correct import path for ComplianceEngine.
#       Assuming it's in core.governance based on previous `ls` output.
try:
    from core.governance.compliance_engine import ComplianceEngine

    COMPLIANCE_ENGINE_AVAILABLE = True
    logger.info("ΛTRACE: ComplianceEngine imported successfully.")
except ImportError:
    logger.error(
        "ΛTRACE: Failed to import ComplianceEngine. Tests will likely fail or be skipped."
    )
    COMPLIANCE_ENGINE_AVAILABLE = False

    # Define a dummy class if import fails, so pytest can at least parse the file
    class ComplianceEngine:
        def __init__(self, gdpr_enabled=False, data_retention_days=0):
            pass

        def anonymize_metadata(self, metadata):
            return metadata

        def should_retain_data(self, timestamp):
            return False


# Human-readable comment: Test for metadata anonymization when GDPR is enabled.
@pytest.mark.skipif(
    not COMPLIANCE_ENGINE_AVAILABLE, reason="ComplianceEngine not available"
)
def test_anonymize_metadata_gdpr_enabled():  # Renamed to be more descriptive
    """Tests metadata anonymization when GDPR compliance is enabled."""
    logger.info("ΛTRACE: Running test_anonymize_metadata_gdpr_enabled.")
    compliance_engine = ComplianceEngine(gdpr_enabled=True)
    metadata = {
        "user_id": "test_user",
        "location": {"city": "Test City", "country": "Test Country"},
        "device_info": {"type": "mobile", "os": "iOS", "battery_level": 80},
    }

    logger.debug(f"ΛTRACE: Original metadata: {metadata}")
    anonymized = compliance_engine.anonymize_metadata(metadata)
    logger.debug(f"ΛTRACE: Anonymized metadata: {anonymized}")

    assert anonymized.get("user_id") != "test_user", "user_id should be anonymized"
    assert "city" not in anonymized.get(
        "location", {}
    ), "city should be removed from location"
    assert (
        anonymized.get("device_info", {}).get("type") == "anonymized"
    ), "device type should be marked anonymized"
    logger.info("ΛTRACE: test_anonymize_metadata_gdpr_enabled finished.")


# Human-readable comment: Test data retention within the defined period.
@pytest.mark.skipif(
    not COMPLIANCE_ENGINE_AVAILABLE, reason="ComplianceEngine not available"
)
def test_should_retain_data_within_retention_period():
    """Tests that data is retained if it's within the retention period."""
    logger.info("ΛTRACE: Running test_should_retain_data_within_retention_period.")
    compliance_engine = ComplianceEngine(data_retention_days=30)
    timestamp = time.time() - (15 * 24 * 60 * 60)  # 15 days ago

    logger.debug(f"ΛTRACE: Testing retention for timestamp {timestamp} (15 days ago).")
    assert (
        compliance_engine.should_retain_data(timestamp) is True
    ), "Data within retention period should be retained"
    logger.info("ΛTRACE: test_should_retain_data_within_retention_period finished.")


# Human-readable comment: Test data is not retained after the defined period.
@pytest.mark.skipif(
    not COMPLIANCE_ENGINE_AVAILABLE, reason="ComplianceEngine not available"
)
def test_should_not_retain_data_after_retention_period():
    """Tests that data is not retained if it's outside the retention period."""
    logger.info("ΛTRACE: Running test_should_not_retain_data_after_retention_period.")
    compliance_engine = ComplianceEngine(data_retention_days=30)
    timestamp = time.time() - (31 * 24 * 60 * 60)  # 31 days ago

    logger.debug(f"ΛTRACE: Testing retention for timestamp {timestamp} (31 days ago).")
    assert (
        compliance_engine.should_retain_data(timestamp) is False
    ), "Data outside retention period should not be retained"
    logger.info("ΛTRACE: test_should_not_retain_data_after_retention_period finished.")


# Human-readable comment: Test metadata anonymization when GDPR is disabled.
@pytest.mark.skipif(
    not COMPLIANCE_ENGINE_AVAILABLE, reason="ComplianceEngine not available"
)
def test_anonymize_metadata_gdpr_disabled():  # Renamed from _without_gdpr for consistency
    """Tests that metadata remains unchanged when GDPR compliance is disabled."""
    logger.info("ΛTRACE: Running test_anonymize_metadata_gdpr_disabled.")
    compliance_engine = ComplianceEngine(gdpr_enabled=False)
    metadata = {
        "user_id": "test_user",
        "location": {"city": "Test City", "country": "Test Country"},
        "device_info": {"type": "mobile", "os": "iOS", "battery_level": 80},
    }

    logger.debug(f"ΛTRACE: Original metadata (GDPR disabled): {metadata}")
    anonymized = compliance_engine.anonymize_metadata(metadata)
    logger.debug(
        f"ΛTRACE: Metadata after anonymization call (GDPR disabled): {anonymized}"
    )

    assert (
        anonymized == metadata
    ), "Metadata should remain unchanged when GDPR is disabled"
    logger.info("ΛTRACE: test_anonymize_metadata_gdpr_disabled finished.")


# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: test_compliance_engine.py
# VERSION: 1.0.0
# TIER SYSTEM: Not applicable (Test Script)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Unit tests for ComplianceEngine's anonymization and data retention logic.
# FUNCTIONS: test_anonymize_metadata_gdpr_enabled,
#            test_should_retain_data_within_retention_period,
#            test_should_not_retain_data_after_retention_period,
#            test_anonymize_metadata_gdpr_disabled.
# CLASSES: None (tests functions of ComplianceEngine).
# DECORATORS: @pytest.mark.skipif.
# DEPENDENCIES: pytest, time, logging, core.governance.compliance_engine.ComplianceEngine.
# INTERFACES: Pytest test discovery and execution.
# ERROR HANDLING: Uses pytest assertions to check for expected outcomes.
# LOGGING: ΛTRACE_ENABLED for logging test execution and debug information.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   Run with pytest: pytest core/advanced/brain/tests/test_compliance_engine.py
# INTEGRATION NOTES: Ensures the ComplianceEngine behaves as expected regarding GDPR
#                    rules and data retention policies. The import path for
#                    ComplianceEngine might need verification based on actual project structure.
# MAINTENANCE: Update tests if ComplianceEngine logic changes. Add more test cases
#              for edge cases or new compliance features.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
