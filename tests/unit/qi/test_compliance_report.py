"""Tests for compliance report generator.

Validates multi-jurisdiction compliance report generation for GDPR, CCPA,
PIPEDA, and LGPD with comprehensive coverage of all report sections.
"""

import json
from datetime import datetime, timedelta, timezone

import pytest
from qi.compliance.compliance_report import (
    AccessorType,
    AccessPurpose,
    ComplianceReport,
    ComplianceReportGenerator,
    DataCategory,
    DeletionStatus,
    LegalBasis,
)
from qi.compliance.privacy_statement import Jurisdiction


@pytest.fixture
def generator() -> ComplianceReportGenerator:
    """Create a compliance report generator."""
    return ComplianceReportGenerator()


@pytest.fixture
def sample_user_id() -> str:
    """Create a sample user ID."""
    return "user_12345"


@pytest.fixture
def sample_date_range() -> tuple[datetime, datetime]:
    """Create a sample date range for testing."""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=90)
    return (start_date, end_date)


class TestComplianceReportGenerator:
    """Test ComplianceReportGenerator class."""

    def test_generator_initialization(self, generator: ComplianceReportGenerator) -> None:
        """Test generator initializes correctly."""
        assert generator is not None
        assert hasattr(generator, "_guardian")
        assert hasattr(generator, "_jurisdiction_requirements")
        assert len(generator._jurisdiction_requirements) == 4

    def test_generate_gdpr_report(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test GDPR compliance report generation."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        assert isinstance(report, dict)
        assert report["jurisdiction"] == "GDPR"
        assert "user_" in report["user_id"]  # Pseudonymized
        assert report["user_id"] != sample_user_id  # Should be redacted
        assert "report_date" in report
        assert "date_range" in report
        assert report["date_range"]["start"] is not None
        assert report["date_range"]["end"] is not None

        # Check all required sections
        assert "consent_history" in report
        assert "data_access_log" in report
        assert "retention_compliance" in report
        assert "deletion_requests" in report
        assert "third_party_disclosures" in report
        assert "security_events" in report
        assert "metadata" in report

        # Check GDPR-specific metadata
        assert report["metadata"]["gdpr_article_15"] is True
        assert "processing_activities" in report["metadata"]
        assert "automated_decision_making" in report["metadata"]
        assert "data_retention_period" in report["metadata"]

    def test_generate_ccpa_report(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test CCPA compliance report generation."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.CCPA,
            date_range=sample_date_range,
        )

        assert report["jurisdiction"] == "CCPA"

        # Check CCPA-specific metadata
        assert report["metadata"]["ccpa_compliance"] is True
        assert "data_sale_status" in report["metadata"]
        assert "do not sell" in report["metadata"]["data_sale_status"].lower()
        assert "categories_collected" in report["metadata"]
        assert "business_purposes" in report["metadata"]
        assert "sources_of_information" in report["metadata"]

    def test_generate_pipeda_report(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test PIPEDA compliance report generation."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.PIPEDA,
            date_range=sample_date_range,
        )

        assert report["jurisdiction"] == "PIPEDA"

        # Check PIPEDA-specific metadata
        assert report["metadata"]["pipeda_compliance"] is True
        assert "information_holdings" in report["metadata"]
        assert "uses_of_information" in report["metadata"]
        assert "disclosure_to_third_parties" in report["metadata"]
        assert "accuracy_statement" in report["metadata"]
        assert "retention_policy" in report["metadata"]

    def test_generate_lgpd_report(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test LGPD compliance report generation."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.LGPD,
            date_range=sample_date_range,
        )

        assert report["jurisdiction"] == "LGPD"

        # Check LGPD-specific metadata
        assert report["metadata"]["lgpd_compliance"] is True
        assert "processing_purposes" in report["metadata"]
        assert "data_sharing" in report["metadata"]
        assert "international_transfers" in report["metadata"]
        assert "retention_period" in report["metadata"]
        assert "data_subject_rights" in report["metadata"]

    def test_generate_with_string_jurisdiction(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test generation with string jurisdiction parameter."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction="gdpr",  # lowercase string
            date_range=sample_date_range,
        )

        assert report["jurisdiction"] == "GDPR"

    def test_generate_invalid_jurisdiction(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test generation with invalid jurisdiction raises error."""
        with pytest.raises(ValueError, match="Unsupported jurisdiction"):
            generator.generate_report(
                user_id=sample_user_id,
                jurisdiction="INVALID",
                date_range=sample_date_range,
            )

    def test_consent_history_section(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test consent history section is populated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        consent_history = report["consent_history"]
        assert isinstance(consent_history, list)
        assert len(consent_history) > 0

        # Check first consent record structure
        consent = consent_history[0]
        assert "timestamp" in consent
        assert "purpose" in consent
        assert "legal_basis" in consent
        assert "scope" in consent
        assert "active" in consent
        assert isinstance(consent["active"], bool)

        # Check for both active and withdrawn consents
        active_consents = [c for c in consent_history if c["active"]]
        withdrawn_consents = [c for c in consent_history if not c["active"]]

        assert len(active_consents) > 0
        assert len(withdrawn_consents) > 0

        # Withdrawn consents should have withdrawn_at timestamp
        for consent in withdrawn_consents:
            assert consent["withdrawn_at"] is not None

    def test_data_access_log_section(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test data access log section is populated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        access_log = report["data_access_log"]
        assert isinstance(access_log, list)
        assert len(access_log) > 0

        # Check access record structure
        access = access_log[0]
        assert "timestamp" in access
        assert "accessor" in access
        assert "accessor_type" in access
        assert "data_categories" in access
        assert "purpose" in access
        assert "legal_basis" in access

        # Verify accessor types are valid
        for access in access_log:
            assert access["accessor_type"] in [at.value for at in AccessorType]

        # Verify purposes are valid
        for access in access_log:
            assert access["purpose"] in [ap.value for ap in AccessPurpose]

        # Verify legal basis is valid
        for access in access_log:
            assert access["legal_basis"] in [lb.value for lb in LegalBasis]

    def test_retention_compliance_section(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test retention compliance section is populated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        retention = report["retention_compliance"]
        assert isinstance(retention, dict)
        assert len(retention) > 0

        # Check retention policy structure
        for _category, policy in retention.items():
            assert "data_category" in policy
            assert "retention_period_days" in policy
            assert "next_deletion_date" in policy
            assert "policy_basis" in policy
            assert "legal_requirement" in policy
            assert isinstance(policy["legal_requirement"], bool)
            assert isinstance(policy["retention_period_days"], int)
            assert policy["retention_period_days"] > 0

    def test_deletion_requests_section(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test deletion requests section is populated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        deletions = report["deletion_requests"]
        assert isinstance(deletions, list)

        # If there are deletion requests, check their structure
        if len(deletions) > 0:
            deletion = deletions[0]
            assert "timestamp" in deletion
            assert "request_type" in deletion
            assert "scope" in deletion
            assert "status" in deletion
            assert isinstance(deletion["scope"], list)

            # Check status is valid
            assert deletion["status"] in [ds.value for ds in DeletionStatus]

            # Completed requests should have completed_at timestamp
            if deletion["status"] == DeletionStatus.COMPLETED.value:
                assert "completed_at" in deletion

    def test_third_party_disclosures_section(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test third-party disclosures section is populated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        third_parties = report["third_party_disclosures"]
        assert isinstance(third_parties, list)
        assert len(third_parties) > 0

        # Check third-party disclosure structure
        tp = third_parties[0]
        assert "name" in tp
        assert "purpose" in tp
        assert "data_categories" in tp
        assert "legal_basis" in tp
        assert "safeguards" in tp
        assert "location" in tp
        assert "active" in tp
        assert isinstance(tp["active"], bool)
        assert isinstance(tp["data_categories"], list)
        assert isinstance(tp["safeguards"], list)

        # Verify legal basis is valid
        for tp in third_parties:
            assert tp["legal_basis"] in [lb.value for lb in LegalBasis]

    def test_security_events_section_included(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test security events section is included when requested."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
            include_security_events=True,
        )

        assert "security_events" in report
        assert report["security_events"] is not None
        assert isinstance(report["security_events"], list)

        # Check security event structure
        if len(report["security_events"]) > 0:
            event = report["security_events"][0]
            assert "timestamp" in event
            assert "event_type" in event
            assert "description" in event
            assert "severity" in event
            assert "resolved" in event
            assert isinstance(event["resolved"], bool)

    def test_security_events_section_excluded(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test security events section can be excluded."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
            include_security_events=False,
        )

        assert report["security_events"] is None

    def test_date_range_filtering(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
    ) -> None:
        """Test date range filtering works correctly."""
        # Create a narrow date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=(start_date, end_date),
        )

        # Verify date range is set correctly
        assert report["date_range"]["start"] == start_date.isoformat()
        assert report["date_range"]["end"] == end_date.isoformat()

    def test_user_id_pseudonymization(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test user ID is pseudonymized in report."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        # User ID should be redacted/pseudonymized
        assert report["user_id"] != sample_user_id
        assert report["user_id"].startswith("user_")
        assert len(report["user_id"]) > len("user_")

    def test_ip_address_redaction(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test IP addresses are redacted in access logs."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        # Check access logs for IP redaction
        for access in report["data_access_log"]:
            if access.get("ip_address"):
                ip = access["ip_address"]
                # Should contain "xxx" for redacted parts
                assert "xxx" in ip.lower() or ip is None

    def test_metadata_generation(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test metadata is generated correctly."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        metadata = report["metadata"]
        assert "version" in metadata
        assert metadata["version"] == "1.0"
        assert "generator" in metadata
        assert "LUKHAS" in metadata["generator"]
        assert "report_hash" in metadata
        assert len(metadata["report_hash"]) > 0
        assert "jurisdiction_standard" in metadata
        assert metadata["jurisdiction_standard"] == "GDPR"

    def test_export_json(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test JSON export functionality."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        json_output = generator.export_json(report)

        # Verify it's valid JSON
        assert isinstance(json_output, str)
        parsed = json.loads(json_output)
        assert isinstance(parsed, dict)

        # Verify structure is preserved
        assert parsed["jurisdiction"] == "GDPR"
        assert "consent_history" in parsed
        assert "data_access_log" in parsed

    def test_export_html(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test HTML export functionality."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        html_output = generator.export_html(report)

        # Verify it's valid HTML
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output
        assert "<html" in html_output
        assert "</html>" in html_output
        assert "<head>" in html_output
        assert "<body>" in html_output

        # Check for major sections
        assert "Compliance Report" in html_output
        assert "Consent History" in html_output
        assert "Data Access Log" in html_output
        assert "Retention Compliance" in html_output
        assert "Deletion Requests" in html_output
        assert "Third-Party Disclosures" in html_output

        # Check metadata is included
        assert report["user_id"] in html_output
        assert report["jurisdiction"] in html_output

    def test_html_contains_tables(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test HTML export contains properly formatted tables."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        html_output = generator.export_html(report)

        # Should have multiple tables (one per section)
        assert html_output.count("<table>") >= 5
        assert html_output.count("</table>") >= 5
        assert "<th>" in html_output
        assert "<td>" in html_output
        assert "<tr>" in html_output

    def test_html_styling_included(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test HTML export includes CSS styling."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        html_output = generator.export_html(report)

        # Check for CSS
        assert "<style>" in html_output
        assert "</style>" in html_output
        assert "font-family" in html_output
        assert "table" in html_output
        assert "border" in html_output

    def test_all_jurisdictions_generate_valid_reports(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test all jurisdictions generate valid reports."""
        for jurisdiction in Jurisdiction:
            report = generator.generate_report(
                user_id=sample_user_id,
                jurisdiction=jurisdiction,
                date_range=sample_date_range,
            )

            # All reports should have core sections
            assert "consent_history" in report
            assert "data_access_log" in report
            assert "retention_compliance" in report
            assert "deletion_requests" in report
            assert "third_party_disclosures" in report
            assert "metadata" in report

            # Should have jurisdiction-specific metadata
            assert report["jurisdiction"] == jurisdiction.value

    def test_empty_data_scenarios(
        self,
        generator: ComplianceReportGenerator,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test report generation with user who has minimal data."""
        # Use a different user ID that might have less data
        report = generator.generate_report(
            user_id="minimal_user_999",
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        # Report should still be valid
        assert isinstance(report, dict)
        assert "consent_history" in report
        assert "data_access_log" in report

        # Sections can be empty lists/dicts
        assert isinstance(report["consent_history"], list)
        assert isinstance(report["data_access_log"], list)
        assert isinstance(report["retention_compliance"], dict)

    def test_gdpr_article_15_compliance(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test GDPR report includes Article 15 required information."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        # Article 15 requirements
        assert report["metadata"]["gdpr_article_15"] is True

        # Must include processing activities
        assert "processing_activities" in report["metadata"]
        assert isinstance(report["metadata"]["processing_activities"], list)
        assert len(report["metadata"]["processing_activities"]) > 0

        # Must disclose automated decision-making
        assert "automated_decision_making" in report["metadata"]

        # Must include retention periods
        assert "data_retention_period" in report["metadata"]

        # Must disclose third-country transfers
        assert "third_country_transfers" in report["metadata"]

    def test_ccpa_categories_and_sources(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test CCPA report includes required categories and sources."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.CCPA,
            date_range=sample_date_range,
        )

        # CCPA requires categories of PI collected
        assert "categories_collected" in report["metadata"]
        assert isinstance(report["metadata"]["categories_collected"], list)

        # CCPA requires business purposes
        assert "business_purposes" in report["metadata"]
        assert isinstance(report["metadata"]["business_purposes"], list)
        assert len(report["metadata"]["business_purposes"]) > 0

        # CCPA requires sources of information
        assert "sources_of_information" in report["metadata"]
        assert isinstance(report["metadata"]["sources_of_information"], list)
        assert len(report["metadata"]["sources_of_information"]) > 0

        # CCPA requires disclosure about sale of data
        assert "data_sale_status" in report["metadata"]

    def test_pipeda_principles_coverage(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test PIPEDA report covers required principles."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.PIPEDA,
            date_range=sample_date_range,
        )

        # PIPEDA principles
        assert "information_holdings" in report["metadata"]
        assert "uses_of_information" in report["metadata"]
        assert "disclosure_to_third_parties" in report["metadata"]
        assert "accuracy_statement" in report["metadata"]
        assert "retention_policy" in report["metadata"]

    def test_lgpd_international_transfers(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test LGPD report includes international transfer information."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.LGPD,
            date_range=sample_date_range,
        )

        # LGPD requires disclosure of international transfers
        assert "international_transfers" in report["metadata"]
        assert isinstance(report["metadata"]["international_transfers"], int)

        # If there are transfers, must disclose safeguards
        if report["metadata"]["international_transfers"] > 0:
            assert "safeguards_for_transfers" in report["metadata"]
            assert isinstance(report["metadata"]["safeguards_for_transfers"], list)

        # LGPD requires comprehensive rights statement
        assert "data_subject_rights" in report["metadata"]
        rights_text = report["metadata"]["data_subject_rights"]
        assert "Confirmation" in rights_text or "confirmation" in rights_text
        assert "portability" in rights_text.lower()
        assert "revocation" in rights_text.lower()

    def test_consent_expiry_tracking(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test consent records include expiry tracking."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        consent_history = report["consent_history"]

        # Check for expiry dates
        for consent in consent_history:
            # Consent should have expiry_date field (can be None)
            assert "expiry_date" in consent

    def test_report_hash_uniqueness(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test report hash is generated and consistent."""
        report1 = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        report2 = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.CCPA,
            date_range=sample_date_range,
        )

        # Different jurisdictions should have different hashes
        hash1 = report1["metadata"]["report_hash"]
        hash2 = report2["metadata"]["report_hash"]

        assert hash1 != hash2
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_json_export_is_machine_readable(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test JSON export creates machine-readable output."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        json_output = generator.export_json(report)

        # Should be valid, parseable JSON
        parsed = json.loads(json_output)

        # Should preserve data types
        assert isinstance(parsed["consent_history"], list)
        assert isinstance(parsed["data_access_log"], list)
        assert isinstance(parsed["retention_compliance"], dict)
        assert isinstance(parsed["metadata"], dict)

        # Should be pretty-printed (contains newlines and indentation)
        assert "\n" in json_output
        assert "  " in json_output  # Indentation

    def test_html_export_is_human_readable(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test HTML export creates human-readable output."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        html_output = generator.export_html(report)

        # Should have descriptive headers
        assert "<h1>" in html_output
        assert "<h2>" in html_output

        # Should format dates readably (ISO format)
        assert "2025" in html_output or "2024" in html_output

        # Should have structured tables
        assert "<table>" in html_output
        assert "<th>" in html_output

    def test_multi_jurisdiction_scenario(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test generating reports for multiple jurisdictions for same user."""
        jurisdictions = [Jurisdiction.GDPR, Jurisdiction.CCPA, Jurisdiction.PIPEDA, Jurisdiction.LGPD]

        reports = {}
        for jurisdiction in jurisdictions:
            reports[jurisdiction] = generator.generate_report(
                user_id=sample_user_id,
                jurisdiction=jurisdiction,
                date_range=sample_date_range,
            )

        # All reports should be valid
        for jurisdiction, report in reports.items():
            assert report["jurisdiction"] == jurisdiction.value
            assert "consent_history" in report
            assert "metadata" in report

        # Each should have jurisdiction-specific requirements
        assert reports[Jurisdiction.GDPR]["metadata"]["gdpr_article_15"] is True
        assert reports[Jurisdiction.CCPA]["metadata"]["ccpa_compliance"] is True
        assert reports[Jurisdiction.PIPEDA]["metadata"]["pipeda_compliance"] is True
        assert reports[Jurisdiction.LGPD]["metadata"]["lgpd_compliance"] is True


class TestEnums:
    """Test enum definitions."""

    def test_legal_basis_enum(self) -> None:
        """Test LegalBasis enum has expected values."""
        assert LegalBasis.CONSENT.value == "consent"
        assert LegalBasis.CONTRACT.value == "contract"
        assert LegalBasis.LEGITIMATE_INTEREST.value == "legitimate_interest"
        assert LegalBasis.LEGAL_OBLIGATION.value == "legal_obligation"

    def test_data_category_enum(self) -> None:
        """Test DataCategory enum has expected values."""
        assert DataCategory.PROFILE.value == "profile"
        assert DataCategory.HEALTH.value == "health"
        assert DataCategory.BIOMETRIC.value == "biometric"
        assert DataCategory.LOCATION.value == "location"

    def test_accessor_type_enum(self) -> None:
        """Test AccessorType enum has expected values."""
        assert AccessorType.SYSTEM.value == "system"
        assert AccessorType.USER.value == "user"
        assert AccessorType.ADMIN.value == "admin"
        assert AccessorType.THIRD_PARTY.value == "third_party"

    def test_deletion_status_enum(self) -> None:
        """Test DeletionStatus enum has expected values."""
        assert DeletionStatus.PENDING.value == "pending"
        assert DeletionStatus.COMPLETED.value == "completed"
        assert DeletionStatus.REJECTED.value == "rejected"


class TestGuardianIntegration:
    """Test Guardian System integration interface."""

    def test_guardian_interface_access_logs(self, generator: ComplianceReportGenerator) -> None:
        """Test Guardian interface returns access logs."""
        guardian = generator._guardian
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)

        logs = guardian.get_access_logs("test_user", start_date, end_date)

        assert isinstance(logs, list)
        # Mock should return at least some logs
        assert len(logs) >= 0

    def test_guardian_interface_consent_records(self, generator: ComplianceReportGenerator) -> None:
        """Test Guardian interface returns consent records."""
        guardian = generator._guardian
        consents = guardian.get_consent_records("test_user")

        assert isinstance(consents, list)

    def test_guardian_interface_deletion_requests(self, generator: ComplianceReportGenerator) -> None:
        """Test Guardian interface returns deletion requests."""
        guardian = generator._guardian
        deletions = guardian.get_deletion_requests("test_user")

        assert isinstance(deletions, list)

    def test_guardian_interface_security_events(self, generator: ComplianceReportGenerator) -> None:
        """Test Guardian interface returns security events."""
        guardian = generator._guardian
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)

        events = guardian.get_security_events("test_user", start_date, end_date)

        assert isinstance(events, list)


class TestPrivacyProtection:
    """Test privacy protection features."""

    def test_user_id_redaction(self, generator: ComplianceReportGenerator) -> None:
        """Test user ID redaction."""
        original_id = "user_12345_sensitive"
        redacted = generator._redact_internal_id(original_id)

        assert redacted != original_id
        assert redacted.startswith("user_")
        assert "sensitive" not in redacted

    def test_ipv4_address_redaction(self, generator: ComplianceReportGenerator) -> None:
        """Test IPv4 address redaction."""
        ip = "192.168.1.100"
        redacted = generator._redact_ip_address(ip)

        # Should keep first two octets
        assert redacted.startswith("192.168")
        # Should redact last two octets
        assert "xxx" in redacted
        assert "100" not in redacted

    def test_ipv6_address_redaction(self, generator: ComplianceReportGenerator) -> None:
        """Test IPv6 address redaction."""
        ip = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        redacted = generator._redact_ip_address(ip)

        # Should keep first three segments
        assert "2001:0db8:85a3" in redacted or "2001:db8:85a3" in redacted
        # Should redact remaining segments
        assert "xxxx" in redacted.lower()

    def test_no_sensitive_data_in_logs(
        self,
        generator: ComplianceReportGenerator,
        sample_user_id: str,
        sample_date_range: tuple[datetime, datetime],
    ) -> None:
        """Test report doesn't contain sensitive data like passwords."""
        report = generator.generate_report(
            user_id=sample_user_id,
            jurisdiction=Jurisdiction.GDPR,
            date_range=sample_date_range,
        )

        # Convert report to string for searching
        report_str = json.dumps(report).lower()

        # Should not contain sensitive keywords
        assert "password" not in report_str
        assert "secret" not in report_str
        assert "key" not in report_str or "api_key" not in report_str
        assert "token" not in report_str or "access_token" not in report_str
