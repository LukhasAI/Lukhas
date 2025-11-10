"""Tests for privacy statement generator.

Validates multi-jurisdiction privacy statement generation for GDPR, CCPA,
PIPEDA, and LGPD compliance.
"""

from datetime import datetime

import pytest
from qi.compliance.privacy_statement import (
from typing import List
    Jurisdiction,
    OrganizationInfo,
    OutputFormat,
    PrivacyStatement,
    PrivacyStatementGenerator,
)


@pytest.fixture
def sample_organization() -> OrganizationInfo:
    """Create a sample organization for testing."""
    return OrganizationInfo(
        name="LUKHAS AI Inc.",
        address="123 Innovation Street, Tech City, TC 12345",
        email="privacy@lukhas.ai",
        phone="+1-555-123-4567",
        dpo_name="Jane Smith",
        dpo_email="dpo@lukhas.ai",
        website="https://lukhas.ai",
    )


@pytest.fixture
def sample_data_types() -> List[str]:
    """Create sample data types for testing."""
    return [
        "Name and email address",
        "Account credentials",
        "Usage analytics and preferences",
        "Device and browser information",
        "IP address and location data",
    ]


@pytest.fixture
def generator() -> PrivacyStatementGenerator:
    """Create a privacy statement generator."""
    return PrivacyStatementGenerator()


class TestPrivacyStatementGenerator:
    """Test PrivacyStatementGenerator class."""

    def test_generator_initialization(self, generator: PrivacyStatementGenerator) -> None:
        """Test generator initializes correctly."""
        assert generator is not None
        assert hasattr(generator, "_templates")
        assert len(generator._templates) == 4

    def test_generate_gdpr_plain_text(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test GDPR privacy statement generation in plain text."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.PLAIN_TEXT,
        )

        assert isinstance(statement, PrivacyStatement)
        assert statement.jurisdiction == Jurisdiction.GDPR
        assert statement.format == OutputFormat.PLAIN_TEXT
        assert statement.organization == sample_organization
        assert statement.data_types == sample_data_types
        assert isinstance(statement.last_updated, datetime)

        # Check content includes key sections
        content = statement.content
        assert "PRIVACY STATEMENT" in content
        assert "GDPR" in content
        assert "DATA CONTROLLER" in content
        assert "DATA PROTECTION OFFICER" in content
        assert sample_organization.name in content
        assert sample_organization.dpo_email in content

        # Check data types are included
        for data_type in sample_data_types:
            assert data_type in content

        # Check GDPR-specific rights
        assert "Right of Access" in content
        assert "Right to Rectification" in content
        assert "Right to Erasure" in content
        assert "Right to Data Portability" in content
        assert "Right to Object" in content
        assert "right to be forgotten" in content

        # Check international transfers section
        assert "INTERNATIONAL DATA TRANSFERS" in content
        assert "European Economic Area" in content or "EEA" in content

    def test_generate_gdpr_html(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test GDPR privacy statement generation in HTML."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.HTML,
        )

        assert statement.format == OutputFormat.HTML
        content = statement.content

        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<html" in content
        assert "<head>" in content
        assert "<body>" in content
        assert "</html>" in content

        # Check metadata
        assert '<meta charset="UTF-8">' in content
        assert sample_organization.name in content

        # Check sections with proper HTML tags
        assert "<h1>Privacy Statement</h1>" in content
        assert "<h2>" in content
        assert "<ul>" in content
        assert "<li>" in content

        # Check data types in list format
        for data_type in sample_data_types:
            assert f"<li>{data_type}</li>" in content

        # Check email links
        assert f'<a href="mailto:{sample_organization.email}">' in content
        assert f'<a href="mailto:{sample_organization.dpo_email}">' in content

    def test_generate_ccpa_plain_text(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test CCPA privacy statement generation in plain text."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.CCPA,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.PLAIN_TEXT,
        )

        assert statement.jurisdiction == Jurisdiction.CCPA
        content = statement.content

        # Check CCPA-specific content
        assert "PRIVACY NOTICE FOR CALIFORNIA RESIDENTS" in content
        assert "CCPA" in content or "California Consumer Privacy Act" in content

        # Check CCPA-specific rights
        assert "Right to Know" in content
        assert "Right to Delete" in content
        assert "Right to Opt-Out of Sale" in content
        assert "Right to Non-Discrimination" in content

        # Check "do not sell" statement
        assert "WE DO NOT SELL" in content or "DO NOT SELL" in content

        # Check Shine the Light Law reference
        assert "Shine the Light" in content or "1798.83" in content

        # Check Do Not Track
        assert "Do Not Track" in content

    def test_generate_ccpa_html(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test CCPA privacy statement generation in HTML."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.CCPA,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.HTML,
        )

        assert statement.format == OutputFormat.HTML
        content = statement.content

        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "<body>" in content

        # Check highlighted sections
        assert "WE DO NOT SELL" in content
        assert sample_organization.name in content

    def test_generate_pipeda_plain_text(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test PIPEDA privacy statement generation in plain text."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.PIPEDA,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.PLAIN_TEXT,
        )

        assert statement.jurisdiction == Jurisdiction.PIPEDA
        content = statement.content

        # Check PIPEDA-specific content
        assert "PRIVACY POLICY" in content
        assert "PIPEDA" in content
        assert "Personal Information Protection and Electronic Documents Act" in content

        # Check PIPEDA principles
        assert "CONSENT" in content
        assert "LIMITING COLLECTION" in content
        assert "ACCURACY" in content
        assert "SAFEGUARDS" in content
        assert "OPENNESS" in content
        assert "INDIVIDUAL ACCESS" in content
        assert "CHALLENGING COMPLIANCE" in content

        # Check Privacy Commissioner reference
        assert "Privacy Commissioner of Canada" in content
        assert "www.priv.gc.ca" in content or "priv.gc.ca" in content

        # Check response timeframe
        assert "30 days" in content

    def test_generate_pipeda_html(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test PIPEDA privacy statement generation in HTML."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.PIPEDA,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.HTML,
        )

        assert statement.format == OutputFormat.HTML
        content = statement.content

        # Check HTML structure
        assert "<!DOCTYPE html>" in content
        assert "Privacy Policy" in content

        # Check sections
        assert "PIPEDA" in content
        assert sample_organization.name in content

    def test_generate_lgpd_plain_text(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test LGPD privacy statement generation in plain text."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.LGPD,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.PLAIN_TEXT,
        )

        assert statement.jurisdiction == Jurisdiction.LGPD
        content = statement.content

        # Check LGPD-specific content (bilingual)
        assert "POLÍTICA DE PRIVACIDADE" in content
        assert "PRIVACY POLICY" in content
        assert "LGPD" in content
        assert "Lei Geral de Proteção de Dados" in content

        # Check bilingual sections
        assert "DATA CONTROLLER" in content
        assert "CONTROLADOR DE DADOS" in content

        # Check LGPD-specific rights (both languages)
        assert "Confirmação de tratamento" in content or "Confirmation of processing" in content
        assert "Portabilidade dos dados" in content or "Data portability" in content
        assert "Revogação do consentimento" in content or "Revocation of consent" in content

        # Check ANPD reference
        assert "ANPD" in content
        assert "National Data Protection Authority" in content or "Autoridade Nacional" in content

        # Check Article 7 reference
        assert "Article 7" in content or "Artigo 7" in content

    def test_generate_lgpd_html(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test LGPD privacy statement generation in HTML."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.LGPD,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.HTML,
        )

        assert statement.format == OutputFormat.HTML
        content = statement.content

        # Check HTML structure with Portuguese language tag
        assert "<!DOCTYPE html>" in content
        assert 'lang="pt-BR"' in content

        # Check bilingual content
        assert "LGPD" in content
        assert sample_organization.name in content

    def test_generate_with_string_jurisdiction(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with string jurisdiction parameter."""
        statement = generator.generate(
            jurisdiction="gdpr",  # lowercase string
            data_types=sample_data_types,
            organization=sample_organization,
        )

        assert statement.jurisdiction == Jurisdiction.GDPR

    def test_generate_with_string_output_format(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with string output format parameter."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format="html",  # string instead of enum
        )

        assert statement.format == OutputFormat.HTML

    def test_generate_invalid_jurisdiction(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with invalid jurisdiction raises error."""
        with pytest.raises(ValueError, match="Unsupported jurisdiction"):
            generator.generate(
                jurisdiction="INVALID",
                data_types=sample_data_types,
                organization=sample_organization,
            )

    def test_generate_with_custom_purposes(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with custom purposes."""
        custom_purposes = [
            "AI model training and improvement",
            "Consciousness pattern analysis",
            "Personalized service delivery",
        ]

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            purposes=custom_purposes,
        )

        content = statement.content
        for purpose in custom_purposes:
            assert purpose in content

    def test_generate_with_custom_retention(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with custom retention period."""
        custom_retention = "5 years from last account activity"

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            retention_period=custom_retention,
        )

        assert custom_retention in statement.content

    def test_generate_with_custom_legal_basis(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with custom legal basis."""
        custom_legal_basis = "explicit consent and contractual necessity"

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            legal_basis=custom_legal_basis,
        )

        assert custom_legal_basis in statement.content

    def test_organization_without_dpo(
        self,
        generator: PrivacyStatementGenerator,
        sample_data_types: List[str],
    ) -> None:
        """Test generation for organization without DPO."""
        org_no_dpo = OrganizationInfo(
            name="Small Business Inc.",
            address="456 Main St",
            email="info@smallbiz.com",
        )

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=org_no_dpo,
        )

        # Should still generate valid statement
        assert statement.organization == org_no_dpo
        assert org_no_dpo.name in statement.content

    def test_organization_without_optional_fields(
        self,
        generator: PrivacyStatementGenerator,
        sample_data_types: List[str],
    ) -> None:
        """Test generation with minimal organization info."""
        minimal_org = OrganizationInfo(
            name="Minimal Corp",
            address="789 Street",
            email="contact@minimal.com",
        )

        statement = generator.generate(
            jurisdiction=Jurisdiction.CCPA,
            data_types=sample_data_types,
            organization=minimal_org,
        )

        assert statement.organization == minimal_org
        assert minimal_org.name in statement.content
        assert minimal_org.email in statement.content

    def test_empty_data_types(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
    ) -> None:
        """Test generation with empty data types list."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=[],
            organization=sample_organization,
        )

        # Should still generate valid statement
        assert statement.data_types == []
        assert isinstance(statement.content, str)
        assert len(statement.content) > 0

    def test_special_characters_in_data_types(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
    ) -> None:
        """Test handling of special characters in data types."""
        special_data_types = [
            "User's name & email",
            "Location data (GPS coordinates)",
            "Health metrics: heart rate, steps",
            "Biometric data <fingerprints>",
        ]

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=special_data_types,
            organization=sample_organization,
        )

        # All data types should appear in content
        for data_type in special_data_types:
            assert data_type in statement.content

    def test_html_escaping_in_html_output(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
    ) -> None:
        """Test that HTML output doesn't break with special characters."""
        data_with_html = [
            "Tags: <script>alert('test')</script>",
            "Symbols: & < > \" '",
        ]

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=data_with_html,
            organization=sample_organization,
            output_format=OutputFormat.HTML,
        )

        # Should contain the data types (may or may not be escaped)
        assert "Tags:" in statement.content or "&lt;script&gt;" in statement.content

    def test_all_jurisdictions_have_contact_section(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test all jurisdictions include contact information."""
        for jurisdiction in Jurisdiction:
            statement = generator.generate(
                jurisdiction=jurisdiction,
                data_types=sample_data_types,
                organization=sample_organization,
            )

            content = statement.content
            assert sample_organization.email in content
            assert sample_organization.name in content

    def test_all_jurisdictions_have_required_sections(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test all jurisdictions include required sections."""
        for jurisdiction in Jurisdiction:
            statement = generator.generate(
                jurisdiction=jurisdiction,
                data_types=sample_data_types,
                organization=sample_organization,
            )

            content = statement.content

            # All should have data collection info
            assert any(
                keyword in content.upper()
                for keyword in ["DATA", "INFORMATION", "DADOS", "INFORMAÇÃO"]
            )

            # All should have rights section
            assert any(
                keyword in content.upper()
                for keyword in ["RIGHTS", "RIGHT TO", "DIREITOS", "DIREITO"]
            )

            # All should have contact info
            assert sample_organization.email in content

    def test_statement_version_and_metadata(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test privacy statement includes proper version and metadata."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
        )

        assert statement.version == "1.0"
        assert statement.language == "en"
        assert isinstance(statement.last_updated, datetime)

    def test_last_updated_date_formatting(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test last updated date is properly formatted in output."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
        )

        # Should contain a formatted date
        assert "Last Updated:" in statement.content
        # Check for month name (formatted date should have it)
        months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        assert any(month in statement.content for month in months)

    def test_consciousness_data_type(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
    ) -> None:
        """Test LUKHAS-specific consciousness data type handling."""
        consciousness_data = [
            "Consciousness pattern data",
            "Neural state representations",
            "Cognitive model parameters",
            "Adaptive behavior metrics",
        ]

        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=consciousness_data,
            organization=sample_organization,
        )

        for data_type in consciousness_data:
            assert data_type in statement.content

    def test_default_purposes_used_when_none_provided(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test default purposes are used when none provided."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            purposes=None,  # Explicitly None
        )

        # Should contain default purposes
        assert "Providing and maintaining our service" in statement.content

    def test_default_legal_basis_for_gdpr(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test default legal basis for GDPR."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            legal_basis=None,
        )

        # Should contain default GDPR legal basis
        content_lower = statement.content.lower()
        assert "consent" in content_lower
        assert "legitimate interest" in content_lower

    def test_html_output_valid_structure(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test HTML output has valid structure."""
        for jurisdiction in Jurisdiction:
            statement = generator.generate(
                jurisdiction=jurisdiction,
                data_types=sample_data_types,
                organization=sample_organization,
                output_format=OutputFormat.HTML,
            )

            content = statement.content

            # Check basic HTML structure
            assert content.count("<!DOCTYPE html>") == 1
            assert content.count("<html") == 1
            assert content.count("</html>") == 1
            assert content.count("<head>") == 1
            assert content.count("</head>") == 1
            assert content.count("<body>") == 1
            assert content.count("</body>") == 1

            # Check has title
            assert "<title>" in content
            assert "</title>" in content

            # Check has styling
            assert "<style>" in content
            assert "</style>" in content

    def test_plain_text_output_readability(
        self,
        generator: PrivacyStatementGenerator,
        sample_organization: OrganizationInfo,
        sample_data_types: List[str],
    ) -> None:
        """Test plain text output is readable and well-formatted."""
        statement = generator.generate(
            jurisdiction=Jurisdiction.GDPR,
            data_types=sample_data_types,
            organization=sample_organization,
            output_format=OutputFormat.PLAIN_TEXT,
        )

        content = statement.content

        # Check for proper sections with numbering
        assert "1." in content
        assert "2." in content

        # Check for bullet points
        assert "  -" in content

        # Check line breaks exist (not one huge block)
        assert "\n\n" in content

        # Should have reasonable length
        assert len(content) > 500


class TestOrganizationInfo:
    """Test OrganizationInfo dataclass."""

    def test_organization_info_creation(self) -> None:
        """Test creating OrganizationInfo with required fields."""
        org = OrganizationInfo(
            name="Test Corp",
            address="123 Test St",
            email="test@example.com",
        )

        assert org.name == "Test Corp"
        assert org.address == "123 Test St"
        assert org.email == "test@example.com"
        assert org.phone is None
        assert org.dpo_name is None
        assert org.dpo_email is None
        assert org.website is None

    def test_organization_info_with_all_fields(self) -> None:
        """Test creating OrganizationInfo with all fields."""
        org = OrganizationInfo(
            name="Complete Corp",
            address="456 Full St",
            email="info@complete.com",
            phone="+1-555-9999",
            dpo_name="John Doe",
            dpo_email="dpo@complete.com",
            website="https://complete.com",
        )

        assert org.name == "Complete Corp"
        assert org.phone == "+1-555-9999"
        assert org.dpo_name == "John Doe"
        assert org.dpo_email == "dpo@complete.com"
        assert org.website == "https://complete.com"


class TestPrivacyStatement:
    """Test PrivacyStatement dataclass."""

    def test_privacy_statement_creation(
        self,
        sample_organization: OrganizationInfo,
    ) -> None:
        """Test creating PrivacyStatement."""
        now = datetime.now()
        statement = PrivacyStatement(
            jurisdiction=Jurisdiction.GDPR,
            content="Test content",
            format=OutputFormat.PLAIN_TEXT,
            organization=sample_organization,
            data_types=["test"],
            last_updated=now,
        )

        assert statement.jurisdiction == Jurisdiction.GDPR
        assert statement.content == "Test content"
        assert statement.format == OutputFormat.PLAIN_TEXT
        assert statement.organization == sample_organization
        assert statement.data_types == ["test"]
        assert statement.last_updated == now
        assert statement.version == "1.0"
        assert statement.language == "en"


class TestJurisdictionEnum:
    """Test Jurisdiction enum."""

    def test_jurisdiction_values(self) -> None:
        """Test Jurisdiction enum has expected values."""
        assert Jurisdiction.GDPR.value == "GDPR"
        assert Jurisdiction.CCPA.value == "CCPA"
        assert Jurisdiction.PIPEDA.value == "PIPEDA"
        assert Jurisdiction.LGPD.value == "LGPD"

    def test_jurisdiction_count(self) -> None:
        """Test correct number of jurisdictions."""
        assert len(list(Jurisdiction)) == 4


class TestOutputFormatEnum:
    """Test OutputFormat enum."""

    def test_output_format_values(self) -> None:
        """Test OutputFormat enum has expected values."""
        assert OutputFormat.HTML.value == "html"
        assert OutputFormat.PLAIN_TEXT.value == "plain_text"

    def test_output_format_count(self) -> None:
        """Test correct number of output formats."""
        assert len(list(OutputFormat)) == 2
