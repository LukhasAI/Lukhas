"""Privacy Statement Generator for multi-jurisdiction compliance.

Generates privacy statements compliant with GDPR, CCPA, PIPEDA, and LGPD.
Supports both HTML and plain text output formats.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class Jurisdiction(str, Enum):
    """Supported privacy jurisdictions."""

    GDPR = "GDPR"
    CCPA = "CCPA"
    PIPEDA = "PIPEDA"
    LGPD = "LGPD"


class OutputFormat(str, Enum):
    """Supported output formats."""

    HTML = "html"
    PLAIN_TEXT = "plain_text"


@dataclass
class OrganizationInfo:
    """Organization details for privacy statement."""

    name: str
    address: str
    email: str
    phone: str | None = None
    dpo_name: str | None = None
    dpo_email: str | None = None
    website: str | None = None


@dataclass
class PrivacyStatement:
    """Generated privacy statement with metadata."""

    jurisdiction: Jurisdiction
    content: str
    format: OutputFormat
    organization: OrganizationInfo
    data_types: list[str]
    last_updated: datetime
    version: str = "1.0"
    language: str = "en"


class PrivacyStatementGenerator:
    """Generate privacy statements for multiple jurisdictions."""

    def __init__(self) -> None:
        """Initialize the generator with templates."""
        self._templates = {
            Jurisdiction.GDPR: self._gdpr_template,
            Jurisdiction.CCPA: self._ccpa_template,
            Jurisdiction.PIPEDA: self._pipeda_template,
            Jurisdiction.LGPD: self._lgpd_template,
        }

    def generate(
        self,
        jurisdiction: str | Jurisdiction,
        data_types: list[str],
        organization: OrganizationInfo,
        output_format: str | OutputFormat = OutputFormat.PLAIN_TEXT,
        purposes: list[str] | None = None,
        retention_period: str = "as long as necessary for stated purposes",
        legal_basis: str | None = None,
    ) -> PrivacyStatement:
        """Generate a privacy statement for the specified jurisdiction.

        Args:
            jurisdiction: The privacy jurisdiction (GDPR, CCPA, PIPEDA, LGPD)
            data_types: List of data types collected
            organization: Organization information
            output_format: Output format (html or plain_text)
            purposes: Purpose of data processing (optional)
            retention_period: How long data is retained
            legal_basis: Legal basis for processing (GDPR/LGPD)

        Returns:
            PrivacyStatement object with generated content

        Raises:
            ValueError: If jurisdiction is not supported
        """
        # Normalize inputs
        if isinstance(jurisdiction, str):
            try:
                jurisdiction = Jurisdiction(jurisdiction.upper())
            except ValueError:
                raise ValueError(
                    f"Unsupported jurisdiction: {jurisdiction}. "
                    f"Supported: {', '.join(j.value for j in Jurisdiction)}"
                )

        if isinstance(output_format, str):
            output_format = OutputFormat(output_format.lower())

        # Get template function
        template_func = self._templates.get(jurisdiction)
        if not template_func:
            raise ValueError(f"No template found for jurisdiction: {jurisdiction}")

        # Generate content
        context = {
            "organization": organization,
            "data_types": data_types,
            "purposes": purposes or self._default_purposes(),
            "retention_period": retention_period,
            "legal_basis": legal_basis or self._default_legal_basis(jurisdiction),
            "last_updated": datetime.now(),
        }

        content = template_func(context, output_format)

        last_updated: datetime = context["last_updated"]  # type: ignore[assignment]

        return PrivacyStatement(
            jurisdiction=jurisdiction,
            content=content,
            format=output_format,
            organization=organization,
            data_types=data_types,
            last_updated=last_updated,
        )

    @staticmethod
    def _default_purposes() -> list[str]:
        """Return default data processing purposes."""
        return [
            "Providing and maintaining our service",
            "Processing transactions and managing user accounts",
            "Communicating with users about service updates",
            "Improving our services and user experience",
            "Ensuring security and preventing fraud",
        ]

    @staticmethod
    def _default_legal_basis(jurisdiction: Jurisdiction) -> str:
        """Return default legal basis for jurisdiction."""
        if jurisdiction in (Jurisdiction.GDPR, Jurisdiction.LGPD):
            return "consent, contractual necessity, and legitimate interest"
        return "as required by applicable law"

    # Template methods for each jurisdiction

    def _gdpr_template(self, context: dict[str, Any], output_format: OutputFormat) -> str:
        """Generate GDPR-compliant privacy statement."""
        org = context["organization"]
        data_types = context["data_types"]
        purposes = context["purposes"]
        retention_period = context["retention_period"]
        legal_basis = context["legal_basis"]
        last_updated = context["last_updated"]

        if output_format == OutputFormat.HTML:
            return self._gdpr_html_template(
                org, data_types, purposes, retention_period, legal_basis, last_updated
            )
        return self._gdpr_plain_template(
            org, data_types, purposes, retention_period, legal_basis, last_updated
        )

    def _gdpr_plain_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        legal_basis: str,
        last_updated: datetime,
    ) -> str:
        """GDPR plain text template."""
        data_list = "\n".join(f"  - {dt}" for dt in data_types)
        purpose_list = "\n".join(f"  - {p}" for p in purposes)

        return f"""PRIVACY STATEMENT
(GDPR - European Union)

Last Updated: {last_updated.strftime('%B %d, %Y')}

1. DATA CONTROLLER

{org.name}
{org.address}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Website: {org.website}' if org.website else ''}

{f'''2. DATA PROTECTION OFFICER

{org.dpo_name}
Email: {org.dpo_email}
''' if org.dpo_email else ''}

3. DATA WE COLLECT

We collect and process the following categories of personal data:
{data_list}

4. PURPOSE OF PROCESSING

We process your personal data for the following purposes:
{purpose_list}

5. LEGAL BASIS FOR PROCESSING

We process your personal data based on: {legal_basis}

6. DATA RETENTION

We retain your personal data for: {retention_period}

7. YOUR RIGHTS UNDER GDPR

You have the following rights regarding your personal data:

  - Right of Access: Request copies of your personal data
  - Right to Rectification: Request correction of inaccurate data
  - Right to Erasure: Request deletion of your data ("right to be forgotten")
  - Right to Restriction: Request limitation of processing
  - Right to Data Portability: Receive your data in a machine-readable format
  - Right to Object: Object to processing based on legitimate interest
  - Right to Withdraw Consent: Withdraw consent at any time (where applicable)
  - Right to Lodge a Complaint: File a complaint with your supervisory authority

To exercise these rights, contact us at: {org.email}

8. INTERNATIONAL DATA TRANSFERS

If we transfer your data outside the European Economic Area (EEA), we ensure
appropriate safeguards are in place, such as Standard Contractual Clauses or
adequacy decisions by the European Commission.

9. DATA SHARING

We may share your data with:
  - Service providers who assist in our operations
  - Legal authorities when required by law
  - Business partners with your explicit consent

We do not sell your personal data to third parties.

10. COOKIES AND TRACKING

We use cookies and similar tracking technologies. You can control cookie
preferences through your browser settings. For more information, see our
Cookie Policy.

11. DATA SECURITY

We implement appropriate technical and organizational measures to protect
your personal data against unauthorized access, alteration, disclosure,
or destruction.

12. CHILDREN'S PRIVACY

Our services are not directed to children under 16. We do not knowingly
collect data from children without parental consent.

13. UPDATES TO THIS PRIVACY STATEMENT

We may update this statement from time to time. The "Last Updated" date
indicates the most recent revision. Continued use of our services after
changes constitutes acceptance.

14. CONTACT US

For questions about this privacy statement or our data practices:

{org.name}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Data Protection Officer: {org.dpo_email}' if org.dpo_email else ''}
"""

    def _gdpr_html_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        legal_basis: str,
        last_updated: datetime,
    ) -> str:
        """GDPR HTML template."""
        data_list = "\n".join(f"        <li>{dt}</li>" for dt in data_types)
        purpose_list = "\n".join(f"        <li>{p}</li>" for p in purposes)

        dpo_section = ""
        if org.dpo_email:
            dpo_section = f"""
    <section id="dpo">
      <h2>2. Data Protection Officer</h2>
      <p>
        {org.dpo_name}<br>
        Email: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>
      </p>
    </section>
"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Statement - {org.name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    .last-updated {{ color: #7f8c8d; font-style: italic; }}
    ul {{ padding-left: 25px; }}
    .contact {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
  </style>
</head>
<body>
  <h1>Privacy Statement</h1>
  <p class="last-updated">GDPR - European Union<br>Last Updated: {last_updated.strftime('%B %d, %Y')}</p>

  <section id="controller">
    <h2>1. Data Controller</h2>
    <div class="contact">
      <strong>{org.name}</strong><br>
      {org.address}<br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Website: <a href="{org.website}">{org.website}</a>' if org.website else ''}
    </div>
  </section>
{dpo_section}
  <section id="data-collected">
    <h2>3. Data We Collect</h2>
    <p>We collect and process the following categories of personal data:</p>
    <ul>
{data_list}
    </ul>
  </section>

  <section id="purpose">
    <h2>4. Purpose of Processing</h2>
    <p>We process your personal data for the following purposes:</p>
    <ul>
{purpose_list}
    </ul>
  </section>

  <section id="legal-basis">
    <h2>5. Legal Basis for Processing</h2>
    <p>We process your personal data based on: <strong>{legal_basis}</strong></p>
  </section>

  <section id="retention">
    <h2>6. Data Retention</h2>
    <p>We retain your personal data for: <strong>{retention_period}</strong></p>
  </section>

  <section id="rights">
    <h2>7. Your Rights Under GDPR</h2>
    <p>You have the following rights regarding your personal data:</p>
    <ul>
      <li><strong>Right of Access:</strong> Request copies of your personal data</li>
      <li><strong>Right to Rectification:</strong> Request correction of inaccurate data</li>
      <li><strong>Right to Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
      <li><strong>Right to Restriction:</strong> Request limitation of processing</li>
      <li><strong>Right to Data Portability:</strong> Receive your data in a machine-readable format</li>
      <li><strong>Right to Object:</strong> Object to processing based on legitimate interest</li>
      <li><strong>Right to Withdraw Consent:</strong> Withdraw consent at any time (where applicable)</li>
      <li><strong>Right to Lodge a Complaint:</strong> File a complaint with your supervisory authority</li>
    </ul>
    <p>To exercise these rights, contact us at: <a href="mailto:{org.email}">{org.email}</a></p>
  </section>

  <section id="transfers">
    <h2>8. International Data Transfers</h2>
    <p>If we transfer your data outside the European Economic Area (EEA), we ensure appropriate safeguards are in place, such as Standard Contractual Clauses or adequacy decisions by the European Commission.</p>
  </section>

  <section id="sharing">
    <h2>9. Data Sharing</h2>
    <p>We may share your data with:</p>
    <ul>
      <li>Service providers who assist in our operations</li>
      <li>Legal authorities when required by law</li>
      <li>Business partners with your explicit consent</li>
    </ul>
    <p><strong>We do not sell your personal data to third parties.</strong></p>
  </section>

  <section id="cookies">
    <h2>10. Cookies and Tracking</h2>
    <p>We use cookies and similar tracking technologies. You can control cookie preferences through your browser settings. For more information, see our Cookie Policy.</p>
  </section>

  <section id="security">
    <h2>11. Data Security</h2>
    <p>We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, alteration, disclosure, or destruction.</p>
  </section>

  <section id="children">
    <h2>12. Children's Privacy</h2>
    <p>Our services are not directed to children under 16. We do not knowingly collect data from children without parental consent.</p>
  </section>

  <section id="updates">
    <h2>13. Updates to This Privacy Statement</h2>
    <p>We may update this statement from time to time. The "Last Updated" date indicates the most recent revision. Continued use of our services after changes constitutes acceptance.</p>
  </section>

  <section id="contact">
    <h2>14. Contact Us</h2>
    <div class="contact">
      <p>For questions about this privacy statement or our data practices:</p>
      <strong>{org.name}</strong><br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Data Protection Officer: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>' if org.dpo_email else ''}
    </div>
  </section>
</body>
</html>
"""

    def _ccpa_template(self, context: dict[str, Any], output_format: OutputFormat) -> str:
        """Generate CCPA-compliant privacy statement."""
        org = context["organization"]
        data_types = context["data_types"]
        purposes = context["purposes"]
        retention_period = context["retention_period"]
        last_updated = context["last_updated"]

        if output_format == OutputFormat.HTML:
            return self._ccpa_html_template(org, data_types, purposes, retention_period, last_updated)
        return self._ccpa_plain_template(org, data_types, purposes, retention_period, last_updated)

    def _ccpa_plain_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        last_updated: datetime,
    ) -> str:
        """CCPA plain text template."""
        data_list = "\n".join(f"  - {dt}" for dt in data_types)
        purpose_list = "\n".join(f"  - {p}" for p in purposes)

        return f"""PRIVACY NOTICE FOR CALIFORNIA RESIDENTS
(CCPA - California Consumer Privacy Act)

Last Updated: {last_updated.strftime('%B %d, %Y')}

This Privacy Notice supplements our general privacy statement and applies
solely to California residents.

1. BUSINESS INFORMATION

{org.name}
{org.address}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Website: {org.website}' if org.website else ''}

2. CATEGORIES OF PERSONAL INFORMATION COLLECTED

We collect the following categories of personal information:
{data_list}

3. PURPOSES FOR COLLECTION AND USE

We collect and use personal information for the following business purposes:
{purpose_list}

4. RETENTION PERIOD

We retain personal information for: {retention_period}

5. YOUR CALIFORNIA PRIVACY RIGHTS

California residents have the following rights:

  A. Right to Know
     You have the right to request:
     - Categories of personal information collected
     - Categories of sources from which information was collected
     - Business or commercial purpose for collecting information
     - Categories of third parties with whom we share information
     - Specific pieces of personal information collected about you

  B. Right to Delete
     You have the right to request deletion of personal information we
     collected from you, subject to certain exceptions.

  C. Right to Opt-Out of Sale
     California residents have the right to opt-out of the "sale" of
     personal information.

     WE DO NOT SELL YOUR PERSONAL INFORMATION.

  D. Right to Non-Discrimination
     You have the right not to receive discriminatory treatment for
     exercising your CCPA rights.

6. HOW TO EXERCISE YOUR RIGHTS

To exercise your rights, you may:
  - Email us at: {org.email}
  {f'- Call us at: {org.phone}' if org.phone else ''}
  - Submit a request through our website

We will verify your identity before processing requests. You may designate
an authorized agent to make requests on your behalf.

7. VERIFICATION PROCESS

To verify your identity, we may request:
  - Email address or phone number associated with your account
  - Recent transaction or account information
  - Government-issued identification (for sensitive requests)

8. CATEGORIES OF SOURCES

We collect personal information from:
  - Directly from you (account registration, forms, communications)
  - Automatically (cookies, log files, device information)
  - From third parties (business partners, service providers)

9. DISCLOSURE OF PERSONAL INFORMATION

In the preceding 12 months, we may have disclosed the following categories
of personal information for business purposes:
{data_list}

We disclose information to:
  - Service providers and vendors
  - Legal authorities (when required)
  - Business partners (with your consent)

10. SALE OF PERSONAL INFORMATION

WE DO NOT SELL PERSONAL INFORMATION. If this changes, we will update this
notice and provide an opt-out mechanism as required by law.

11. SHINE THE LIGHT LAW

California Civil Code Section 1798.83 permits California residents to
request certain information about disclosure of personal information to
third parties for direct marketing purposes. We do not share personal
information with third parties for their direct marketing purposes.

12. DO NOT TRACK SIGNALS

Some browsers transmit "Do Not Track" signals. We currently do not respond
to these signals, as there is no industry standard for their interpretation.

13. MINORS UNDER 16

We do not knowingly sell personal information of minors under 16 years old.

14. UPDATES TO THIS NOTICE

We may update this notice annually or as required by law. The "Last Updated"
date indicates the most recent revision.

15. CONTACT US

For questions about this privacy notice:

{org.name}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
"""

    def _ccpa_html_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        last_updated: datetime,
    ) -> str:
        """CCPA HTML template."""
        data_list = "\n".join(f"        <li>{dt}</li>" for dt in data_types)
        purpose_list = "\n".join(f"        <li>{p}</li>" for p in purposes)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>California Privacy Notice - {org.name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
    h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    h3 {{ color: #7f8c8d; }}
    .last-updated {{ color: #7f8c8d; font-style: italic; }}
    ul {{ padding-left: 25px; }}
    .contact {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
    .highlight {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0; }}
  </style>
</head>
<body>
  <h1>Privacy Notice for California Residents</h1>
  <p class="last-updated">CCPA - California Consumer Privacy Act<br>Last Updated: {last_updated.strftime('%B %d, %Y')}</p>

  <p>This Privacy Notice supplements our general privacy statement and applies solely to California residents.</p>

  <section id="business-info">
    <h2>1. Business Information</h2>
    <div class="contact">
      <strong>{org.name}</strong><br>
      {org.address}<br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Website: <a href="{org.website}">{org.website}</a>' if org.website else ''}
    </div>
  </section>

  <section id="categories">
    <h2>2. Categories of Personal Information Collected</h2>
    <p>We collect the following categories of personal information:</p>
    <ul>
{data_list}
    </ul>
  </section>

  <section id="purposes">
    <h2>3. Purposes for Collection and Use</h2>
    <p>We collect and use personal information for the following business purposes:</p>
    <ul>
{purpose_list}
    </ul>
  </section>

  <section id="retention">
    <h2>4. Retention Period</h2>
    <p>We retain personal information for: <strong>{retention_period}</strong></p>
  </section>

  <section id="rights">
    <h2>5. Your California Privacy Rights</h2>
    <p>California residents have the following rights:</p>

    <h3>A. Right to Know</h3>
    <p>You have the right to request:</p>
    <ul>
      <li>Categories of personal information collected</li>
      <li>Categories of sources from which information was collected</li>
      <li>Business or commercial purpose for collecting information</li>
      <li>Categories of third parties with whom we share information</li>
      <li>Specific pieces of personal information collected about you</li>
    </ul>

    <h3>B. Right to Delete</h3>
    <p>You have the right to request deletion of personal information we collected from you, subject to certain exceptions.</p>

    <h3>C. Right to Opt-Out of Sale</h3>
    <p>California residents have the right to opt-out of the "sale" of personal information.</p>
    <div class="highlight">
      <strong>WE DO NOT SELL YOUR PERSONAL INFORMATION.</strong>
    </div>

    <h3>D. Right to Non-Discrimination</h3>
    <p>You have the right not to receive discriminatory treatment for exercising your CCPA rights.</p>
  </section>

  <section id="exercise-rights">
    <h2>6. How to Exercise Your Rights</h2>
    <p>To exercise your rights, you may:</p>
    <ul>
      <li>Email us at: <a href="mailto:{org.email}">{org.email}</a></li>
      {f'<li>Call us at: {org.phone}</li>' if org.phone else ''}
      <li>Submit a request through our website</li>
    </ul>
    <p>We will verify your identity before processing requests. You may designate an authorized agent to make requests on your behalf.</p>
  </section>

  <section id="verification">
    <h2>7. Verification Process</h2>
    <p>To verify your identity, we may request:</p>
    <ul>
      <li>Email address or phone number associated with your account</li>
      <li>Recent transaction or account information</li>
      <li>Government-issued identification (for sensitive requests)</li>
    </ul>
  </section>

  <section id="sources">
    <h2>8. Categories of Sources</h2>
    <p>We collect personal information from:</p>
    <ul>
      <li>Directly from you (account registration, forms, communications)</li>
      <li>Automatically (cookies, log files, device information)</li>
      <li>From third parties (business partners, service providers)</li>
    </ul>
  </section>

  <section id="disclosure">
    <h2>9. Disclosure of Personal Information</h2>
    <p>In the preceding 12 months, we may have disclosed the following categories of personal information for business purposes:</p>
    <ul>
{data_list}
    </ul>
    <p>We disclose information to:</p>
    <ul>
      <li>Service providers and vendors</li>
      <li>Legal authorities (when required)</li>
      <li>Business partners (with your consent)</li>
    </ul>
  </section>

  <section id="sale">
    <h2>10. Sale of Personal Information</h2>
    <div class="highlight">
      <strong>WE DO NOT SELL PERSONAL INFORMATION.</strong> If this changes, we will update this notice and provide an opt-out mechanism as required by law.
    </div>
  </section>

  <section id="shine">
    <h2>11. Shine the Light Law</h2>
    <p>California Civil Code Section 1798.83 permits California residents to request certain information about disclosure of personal information to third parties for direct marketing purposes. We do not share personal information with third parties for their direct marketing purposes.</p>
  </section>

  <section id="dnt">
    <h2>12. Do Not Track Signals</h2>
    <p>Some browsers transmit "Do Not Track" signals. We currently do not respond to these signals, as there is no industry standard for their interpretation.</p>
  </section>

  <section id="minors">
    <h2>13. Minors Under 16</h2>
    <p>We do not knowingly sell personal information of minors under 16 years old.</p>
  </section>

  <section id="updates">
    <h2>14. Updates to This Notice</h2>
    <p>We may update this notice annually or as required by law. The "Last Updated" date indicates the most recent revision.</p>
  </section>

  <section id="contact">
    <h2>15. Contact Us</h2>
    <div class="contact">
      <p>For questions about this privacy notice:</p>
      <strong>{org.name}</strong><br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}' if org.phone else ''}
    </div>
  </section>
</body>
</html>
"""

    def _pipeda_template(self, context: dict[str, Any], output_format: OutputFormat) -> str:
        """Generate PIPEDA-compliant privacy statement."""
        org = context["organization"]
        data_types = context["data_types"]
        purposes = context["purposes"]
        retention_period = context["retention_period"]
        last_updated = context["last_updated"]

        if output_format == OutputFormat.HTML:
            return self._pipeda_html_template(org, data_types, purposes, retention_period, last_updated)
        return self._pipeda_plain_template(org, data_types, purposes, retention_period, last_updated)

    def _pipeda_plain_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        last_updated: datetime,
    ) -> str:
        """PIPEDA plain text template."""
        data_list = "\n".join(f"  - {dt}" for dt in data_types)
        purpose_list = "\n".join(f"  - {p}" for p in purposes)

        return f"""PRIVACY POLICY
(PIPEDA - Canada)

Last Updated: {last_updated.strftime('%B %d, %Y')}

This privacy policy is provided in accordance with the Personal Information
Protection and Electronic Documents Act (PIPEDA) and applicable provincial
privacy legislation.

1. ORGANIZATION INFORMATION

{org.name}
{org.address}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Website: {org.website}' if org.website else ''}

{f'''2. PRIVACY OFFICER

{org.dpo_name}
Email: {org.dpo_email}
''' if org.dpo_email else ''}

3. PERSONAL INFORMATION WE COLLECT

We collect the following types of personal information:
{data_list}

4. PURPOSE FOR COLLECTION

We collect personal information for the following purposes:
{purpose_list}

We will not use your personal information for any other purpose without
obtaining your consent.

5. CONSENT

We obtain your consent before or at the time of collecting personal
information. The form of consent we seek may vary depending on the
sensitivity of the information and reasonable expectations.

You may withdraw consent at any time, subject to legal or contractual
restrictions and reasonable notice. We will inform you of the implications
of withdrawing consent.

6. LIMITING COLLECTION

We limit the collection of personal information to what is necessary for
the purposes we have identified. We collect information by fair and lawful
means.

7. RETENTION AND DISPOSAL

We retain personal information for: {retention_period}

When personal information is no longer needed, we destroy, erase, or
anonymize it using secure methods appropriate to the sensitivity of the
information.

8. ACCURACY

We make reasonable efforts to ensure personal information is accurate,
complete, and up-to-date as necessary for the purposes for which it is used.

You may challenge the accuracy and completeness of your information and
request amendments as appropriate.

9. SAFEGUARDS

We protect personal information using security safeguards appropriate to
the sensitivity of the information, including:
  - Physical measures (secure facilities, locked filing cabinets)
  - Organizational measures (security clearances, access on need-to-know basis)
  - Technological measures (encryption, firewalls, passwords)

10. OPENNESS

We make information about our policies and practices readily available. This
includes:
  - The types of personal information we collect
  - How we use personal information
  - How to access your personal information
  - Our Privacy Officer contact information

11. INDIVIDUAL ACCESS

Upon written request and authentication of identity, you have the right to:
  - Access your personal information
  - Information about how your information is used
  - Information about disclosures to third parties

We will respond to access requests within 30 days or provide notice if
additional time is needed. In certain circumstances, we may not be able to
provide access (e.g., information contains references to other individuals,
legal privilege applies).

12. CHALLENGING COMPLIANCE

You may challenge our compliance with PIPEDA principles by contacting our
Privacy Officer at: {org.dpo_email if org.dpo_email else org.email}

We will:
  - Record the date the complaint was received
  - Notify you that the complaint has been received
  - Investigate the complaint
  - Take appropriate measures including amending policies and practices
  - Inform you of the outcome

If you are not satisfied with our response, you may contact the Office of
the Privacy Commissioner of Canada:
  - Website: www.priv.gc.ca
  - Toll-free: 1-800-282-1376

13. DISCLOSURE TO THIRD PARTIES

We may disclose personal information:
  - To service providers who assist in our operations (under confidentiality agreements)
  - When required or permitted by law
  - With your express consent

We do not sell personal information to third parties.

14. INTERNATIONAL TRANSFERS

If we transfer personal information outside Canada, we ensure comparable
privacy protection through contractual or other means as required by PIPEDA.

15. COOKIES AND ONLINE TRACKING

We use cookies and similar technologies to enhance user experience. You can
control cookie settings through your browser preferences.

16. UPDATES TO THIS POLICY

We may update this policy from time to time. The "Last Updated" date
indicates the most recent revision. Material changes will be communicated
through prominent notice on our website or direct communication.

17. CONTACT US

For questions about this privacy policy or our information practices:

{org.name}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Privacy Officer: {org.dpo_email}' if org.dpo_email else ''}
"""

    def _pipeda_html_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        last_updated: datetime,
    ) -> str:
        """PIPEDA HTML template."""
        data_list = "\n".join(f"        <li>{dt}</li>" for dt in data_types)
        purpose_list = "\n".join(f"        <li>{p}</li>" for p in purposes)

        dpo_section = ""
        if org.dpo_email:
            dpo_section = f"""
  <section id="privacy-officer">
    <h2>2. Privacy Officer</h2>
    <p>
      {org.dpo_name}<br>
      Email: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>
    </p>
  </section>
"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Privacy Policy - {org.name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
    h1 {{ color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    .last-updated {{ color: #7f8c8d; font-style: italic; }}
    ul {{ padding-left: 25px; }}
    .contact {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
    .highlight {{ background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin: 15px 0; }}
  </style>
</head>
<body>
  <h1>Privacy Policy</h1>
  <p class="last-updated">PIPEDA - Canada<br>Last Updated: {last_updated.strftime('%B %d, %Y')}</p>

  <p>This privacy policy is provided in accordance with the Personal Information Protection and Electronic Documents Act (PIPEDA) and applicable provincial privacy legislation.</p>

  <section id="organization">
    <h2>1. Organization Information</h2>
    <div class="contact">
      <strong>{org.name}</strong><br>
      {org.address}<br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Website: <a href="{org.website}">{org.website}</a>' if org.website else ''}
    </div>
  </section>
{dpo_section}
  <section id="collection">
    <h2>3. Personal Information We Collect</h2>
    <p>We collect the following types of personal information:</p>
    <ul>
{data_list}
    </ul>
  </section>

  <section id="purpose">
    <h2>4. Purpose for Collection</h2>
    <p>We collect personal information for the following purposes:</p>
    <ul>
{purpose_list}
    </ul>
    <p>We will not use your personal information for any other purpose without obtaining your consent.</p>
  </section>

  <section id="consent">
    <h2>5. Consent</h2>
    <p>We obtain your consent before or at the time of collecting personal information. The form of consent we seek may vary depending on the sensitivity of the information and reasonable expectations.</p>
    <p>You may withdraw consent at any time, subject to legal or contractual restrictions and reasonable notice. We will inform you of the implications of withdrawing consent.</p>
  </section>

  <section id="limiting">
    <h2>6. Limiting Collection</h2>
    <p>We limit the collection of personal information to what is necessary for the purposes we have identified. We collect information by fair and lawful means.</p>
  </section>

  <section id="retention">
    <h2>7. Retention and Disposal</h2>
    <p>We retain personal information for: <strong>{retention_period}</strong></p>
    <p>When personal information is no longer needed, we destroy, erase, or anonymize it using secure methods appropriate to the sensitivity of the information.</p>
  </section>

  <section id="accuracy">
    <h2>8. Accuracy</h2>
    <p>We make reasonable efforts to ensure personal information is accurate, complete, and up-to-date as necessary for the purposes for which it is used.</p>
    <p>You may challenge the accuracy and completeness of your information and request amendments as appropriate.</p>
  </section>

  <section id="safeguards">
    <h2>9. Safeguards</h2>
    <p>We protect personal information using security safeguards appropriate to the sensitivity of the information, including:</p>
    <ul>
      <li>Physical measures (secure facilities, locked filing cabinets)</li>
      <li>Organizational measures (security clearances, access on need-to-know basis)</li>
      <li>Technological measures (encryption, firewalls, passwords)</li>
    </ul>
  </section>

  <section id="openness">
    <h2>10. Openness</h2>
    <p>We make information about our policies and practices readily available. This includes:</p>
    <ul>
      <li>The types of personal information we collect</li>
      <li>How we use personal information</li>
      <li>How to access your personal information</li>
      <li>Our Privacy Officer contact information</li>
    </ul>
  </section>

  <section id="access">
    <h2>11. Individual Access</h2>
    <p>Upon written request and authentication of identity, you have the right to:</p>
    <ul>
      <li>Access your personal information</li>
      <li>Information about how your information is used</li>
      <li>Information about disclosures to third parties</li>
    </ul>
    <p>We will respond to access requests within 30 days or provide notice if additional time is needed. In certain circumstances, we may not be able to provide access (e.g., information contains references to other individuals, legal privilege applies).</p>
  </section>

  <section id="challenging">
    <h2>12. Challenging Compliance</h2>
    <p>You may challenge our compliance with PIPEDA principles by contacting our Privacy Officer at: <a href="mailto:{org.dpo_email if org.dpo_email else org.email}">{org.dpo_email if org.dpo_email else org.email}</a></p>
    <p>We will:</p>
    <ul>
      <li>Record the date the complaint was received</li>
      <li>Notify you that the complaint has been received</li>
      <li>Investigate the complaint</li>
      <li>Take appropriate measures including amending policies and practices</li>
      <li>Inform you of the outcome</li>
    </ul>
    <div class="highlight">
      <p>If you are not satisfied with our response, you may contact the Office of the Privacy Commissioner of Canada:</p>
      <ul>
        <li>Website: <a href="https://www.priv.gc.ca" target="_blank">www.priv.gc.ca</a></li>
        <li>Toll-free: 1-800-282-1376</li>
      </ul>
    </div>
  </section>

  <section id="disclosure">
    <h2>13. Disclosure to Third Parties</h2>
    <p>We may disclose personal information:</p>
    <ul>
      <li>To service providers who assist in our operations (under confidentiality agreements)</li>
      <li>When required or permitted by law</li>
      <li>With your express consent</li>
    </ul>
    <p><strong>We do not sell personal information to third parties.</strong></p>
  </section>

  <section id="transfers">
    <h2>14. International Transfers</h2>
    <p>If we transfer personal information outside Canada, we ensure comparable privacy protection through contractual or other means as required by PIPEDA.</p>
  </section>

  <section id="cookies">
    <h2>15. Cookies and Online Tracking</h2>
    <p>We use cookies and similar technologies to enhance user experience. You can control cookie settings through your browser preferences.</p>
  </section>

  <section id="updates">
    <h2>16. Updates to This Policy</h2>
    <p>We may update this policy from time to time. The "Last Updated" date indicates the most recent revision. Material changes will be communicated through prominent notice on our website or direct communication.</p>
  </section>

  <section id="contact">
    <h2>17. Contact Us</h2>
    <div class="contact">
      <p>For questions about this privacy policy or our information practices:</p>
      <strong>{org.name}</strong><br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Privacy Officer: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>' if org.dpo_email else ''}
    </div>
  </section>
</body>
</html>
"""

    def _lgpd_template(self, context: dict[str, Any], output_format: OutputFormat) -> str:
        """Generate LGPD-compliant privacy statement."""
        org = context["organization"]
        data_types = context["data_types"]
        purposes = context["purposes"]
        retention_period = context["retention_period"]
        legal_basis = context["legal_basis"]
        last_updated = context["last_updated"]

        if output_format == OutputFormat.HTML:
            return self._lgpd_html_template(
                org, data_types, purposes, retention_period, legal_basis, last_updated
            )
        return self._lgpd_plain_template(
            org, data_types, purposes, retention_period, legal_basis, last_updated
        )

    def _lgpd_plain_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        legal_basis: str,
        last_updated: datetime,
    ) -> str:
        """LGPD plain text template."""
        data_list = "\n".join(f"  - {dt}" for dt in data_types)
        purpose_list = "\n".join(f"  - {p}" for p in purposes)

        return f"""POLÍTICA DE PRIVACIDADE
(LGPD - Lei Geral de Proteção de Dados - Brazil)

PRIVACY POLICY
(LGPD - General Data Protection Law - Brazil)

Last Updated: {last_updated.strftime('%B %d, %Y')}

1. DATA CONTROLLER / CONTROLADOR DE DADOS

{org.name}
{org.address}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Website: {org.website}' if org.website else ''}

{f'''2. DATA PROTECTION OFFICER / ENCARREGADO DE DADOS

{org.dpo_name}
Email: {org.dpo_email}
''' if org.dpo_email else ''}

3. PERSONAL DATA COLLECTED / DADOS PESSOAIS COLETADOS

We collect and process the following categories of personal data:
Coletamos e processamos as seguintes categorias de dados pessoais:

{data_list}

4. PURPOSE OF PROCESSING / FINALIDADE DO TRATAMENTO

We process your personal data for the following purposes:
Processamos seus dados pessoais para as seguintes finalidades:

{purpose_list}

5. LEGAL BASIS / BASE LEGAL

We process your personal data based on: {legal_basis}
Processamos seus dados pessoais com base em: {legal_basis}

Under LGPD Article 7, processing may be based on:
Conforme Artigo 7 da LGPD, o tratamento pode ser baseado em:
  - Consent / Consentimento
  - Compliance with legal obligation / Cumprimento de obrigação legal
  - Execution of contract / Execução de contrato
  - Legitimate interest / Interesse legítimo
  - Protection of life / Proteção da vida
  - Health procedures / Procedimentos de saúde

6. DATA RETENTION / RETENÇÃO DE DADOS

We retain your personal data for: {retention_period}
Retemos seus dados pessoais por: {retention_period}

Data is retained only for the period necessary to fulfill processing purposes,
unless otherwise required by law.

Os dados são retidos apenas pelo período necessário para cumprir as
finalidades do tratamento, salvo se exigido por lei.

7. YOUR RIGHTS UNDER LGPD / SEUS DIREITOS SOB A LGPD

You have the following rights regarding your personal data:
Você tem os seguintes direitos sobre seus dados pessoais:

  - Confirmation of processing / Confirmação de tratamento
  - Access to data / Acesso aos dados
  - Correction of incomplete, inaccurate data / Correção de dados incompletos ou inexatos
  - Anonymization, blocking, or deletion / Anonimização, bloqueio ou eliminação
  - Data portability / Portabilidade dos dados
  - Deletion of data processed with consent / Eliminação de dados tratados com consentimento
  - Information about sharing / Informação sobre compartilhamento
  - Information about possibility of not providing consent / Informação sobre não consentimento
  - Revocation of consent / Revogação do consentimento

To exercise these rights, contact us at: {org.email}
Para exercer esses direitos, entre em contato: {org.email}

8. DATA SHARING / COMPARTILHAMENTO DE DADOS

We may share your data with:
Podemos compartilhar seus dados com:

  - Service providers who assist in operations / Prestadores de serviço
  - Legal authorities when required by law / Autoridades legais quando exigido
  - Business partners with your consent / Parceiros comerciais com seu consentimento

We do not sell your personal data to third parties.
Não vendemos seus dados pessoais a terceiros.

9. INTERNATIONAL DATA TRANSFERS / TRANSFERÊNCIAS INTERNACIONAIS

If we transfer your data outside Brazil, we ensure adequate protection as
required by LGPD, including:
Se transferirmos seus dados para fora do Brasil, garantimos proteção adequada
conforme exigido pela LGPD, incluindo:

  - Countries with adequate protection / Países com proteção adequada
  - Standard contractual clauses / Cláusulas contratuais padrão
  - Binding corporate rules / Normas corporativas vinculantes
  - Your explicit consent / Seu consentimento explícito

10. DATA SECURITY / SEGURANÇA DOS DADOS

We implement technical and administrative measures to protect personal data
against unauthorized access, accidental or unlawful destruction, loss,
alteration, or improper disclosure.

Implementamos medidas técnicas e administrativas para proteger dados pessoais
contra acesso não autorizado, destruição acidental ou ilícita, perda,
alteração ou divulgação inadequada.

11. CHILDREN'S DATA / DADOS DE CRIANÇAS

Processing of children's and adolescents' data (under 18) is done with
parental/guardian consent and in their best interest, as required by LGPD
Article 14.

O tratamento de dados de crianças e adolescentes (menores de 18 anos) é
realizado com consentimento dos pais/responsáveis e no melhor interesse
deles, conforme Artigo 14 da LGPD.

12. COOKIES AND TRACKING / COOKIES E RASTREAMENTO

We use cookies and similar technologies. You can control preferences through
browser settings. See our Cookie Policy for details.

Usamos cookies e tecnologias similares. Você pode controlar preferências nas
configurações do navegador. Veja nossa Política de Cookies para detalhes.

13. DATA BREACH NOTIFICATION / NOTIFICAÇÃO DE INCIDENTES

In case of a security incident that may create risk or significant damage to
you, we will notify you and ANPD (National Data Protection Authority) within
a reasonable timeframe as required by law.

Em caso de incidente de segurança que possa criar risco ou dano relevante,
notificaremos você e a ANPD (Autoridade Nacional de Proteção de Dados) em
prazo razoável conforme exigido por lei.

14. NATIONAL DATA PROTECTION AUTHORITY / AUTORIDADE NACIONAL

If you are not satisfied with our response, you may contact ANPD:
Se não estiver satisfeito com nossa resposta, pode contatar a ANPD:

  Website: www.gov.br/anpd
  Email: anpd@anpd.gov.br

15. UPDATES TO THIS POLICY / ATUALIZAÇÕES DESTA POLÍTICA

We may update this policy from time to time. The "Last Updated" date
indicates the most recent revision.

Podemos atualizar esta política periodicamente. A data "Last Updated"
indica a revisão mais recente.

16. CONTACT US / ENTRE EM CONTATO

For questions about this privacy policy:
Para dúvidas sobre esta política de privacidade:

{org.name}
Email: {org.email}
{f'Phone: {org.phone}' if org.phone else ''}
{f'Data Protection Officer: {org.dpo_email}' if org.dpo_email else ''}
"""

    def _lgpd_html_template(
        self,
        org: OrganizationInfo,
        data_types: list[str],
        purposes: list[str],
        retention_period: str,
        legal_basis: str,
        last_updated: datetime,
    ) -> str:
        """LGPD HTML template."""
        data_list = "\n".join(f"        <li>{dt}</li>" for dt in data_types)
        purpose_list = "\n".join(f"        <li>{p}</li>" for p in purposes)

        dpo_section = ""
        if org.dpo_email:
            dpo_section = f"""
  <section id="dpo">
    <h2>2. Data Protection Officer / Encarregado de Dados</h2>
    <p>
      {org.dpo_name}<br>
      Email: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>
    </p>
  </section>
"""

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Política de Privacidade - {org.name}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
    h1 {{ color: #2c3e50; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    .last-updated {{ color: #7f8c8d; font-style: italic; }}
    ul {{ padding-left: 25px; }}
    .contact {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
    .bilingual {{ background: #e8f5e9; padding: 10px; border-left: 4px solid #27ae60; margin: 15px 0; }}
  </style>
</head>
<body>
  <h1>Política de Privacidade / Privacy Policy</h1>
  <p class="last-updated">LGPD - Lei Geral de Proteção de Dados (Brazil)<br>Last Updated: {last_updated.strftime('%B %d, %Y')}</p>

  <section id="controller">
    <h2>1. Data Controller / Controlador de Dados</h2>
    <div class="contact">
      <strong>{org.name}</strong><br>
      {org.address}<br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Website: <a href="{org.website}">{org.website}</a>' if org.website else ''}
    </div>
  </section>
{dpo_section}
  <section id="data-collected">
    <h2>3. Personal Data Collected / Dados Pessoais Coletados</h2>
    <p>We collect and process the following categories of personal data:<br>
    <em>Coletamos e processamos as seguintes categorias de dados pessoais:</em></p>
    <ul>
{data_list}
    </ul>
  </section>

  <section id="purpose">
    <h2>4. Purpose of Processing / Finalidade do Tratamento</h2>
    <p>We process your personal data for the following purposes:<br>
    <em>Processamos seus dados pessoais para as seguintes finalidades:</em></p>
    <ul>
{purpose_list}
    </ul>
  </section>

  <section id="legal-basis">
    <h2>5. Legal Basis / Base Legal</h2>
    <p>We process your personal data based on: <strong>{legal_basis}</strong><br>
    <em>Processamos seus dados pessoais com base em: <strong>{legal_basis}</strong></em></p>

    <div class="bilingual">
      <p>Under LGPD Article 7, processing may be based on:<br>
      <em>Conforme Artigo 7 da LGPD, o tratamento pode ser baseado em:</em></p>
      <ul>
        <li>Consent / Consentimento</li>
        <li>Compliance with legal obligation / Cumprimento de obrigação legal</li>
        <li>Execution of contract / Execução de contrato</li>
        <li>Legitimate interest / Interesse legítimo</li>
        <li>Protection of life / Proteção da vida</li>
        <li>Health procedures / Procedimentos de saúde</li>
      </ul>
    </div>
  </section>

  <section id="retention">
    <h2>6. Data Retention / Retenção de Dados</h2>
    <p>We retain your personal data for: <strong>{retention_period}</strong><br>
    <em>Retemos seus dados pessoais por: <strong>{retention_period}</strong></em></p>
    <p>Data is retained only for the period necessary to fulfill processing purposes, unless otherwise required by law.<br>
    <em>Os dados são retidos apenas pelo período necessário para cumprir as finalidades do tratamento, salvo se exigido por lei.</em></p>
  </section>

  <section id="rights">
    <h2>7. Your Rights Under LGPD / Seus Direitos sob a LGPD</h2>
    <p>You have the following rights regarding your personal data:<br>
    <em>Você tem os seguintes direitos sobre seus dados pessoais:</em></p>
    <ul>
      <li>Confirmation of processing / Confirmação de tratamento</li>
      <li>Access to data / Acesso aos dados</li>
      <li>Correction of incomplete, inaccurate data / Correção de dados incompletos ou inexatos</li>
      <li>Anonymization, blocking, or deletion / Anonimização, bloqueio ou eliminação</li>
      <li>Data portability / Portabilidade dos dados</li>
      <li>Deletion of data processed with consent / Eliminação de dados tratados com consentimento</li>
      <li>Information about sharing / Informação sobre compartilhamento</li>
      <li>Information about possibility of not providing consent / Informação sobre não consentimento</li>
      <li>Revocation of consent / Revogação do consentimento</li>
    </ul>
    <p>To exercise these rights, contact us at: <a href="mailto:{org.email}">{org.email}</a><br>
    <em>Para exercer esses direitos, entre em contato: <a href="mailto:{org.email}">{org.email}</a></em></p>
  </section>

  <section id="sharing">
    <h2>8. Data Sharing / Compartilhamento de Dados</h2>
    <p>We may share your data with:<br>
    <em>Podemos compartilhar seus dados com:</em></p>
    <ul>
      <li>Service providers who assist in operations / Prestadores de serviço</li>
      <li>Legal authorities when required by law / Autoridades legais quando exigido</li>
      <li>Business partners with your consent / Parceiros comerciais com seu consentimento</li>
    </ul>
    <p><strong>We do not sell your personal data to third parties.<br>
    <em>Não vendemos seus dados pessoais a terceiros.</em></strong></p>
  </section>

  <section id="transfers">
    <h2>9. International Data Transfers / Transferências Internacionais</h2>
    <p>If we transfer your data outside Brazil, we ensure adequate protection as required by LGPD, including:<br>
    <em>Se transferirmos seus dados para fora do Brasil, garantimos proteção adequada conforme exigido pela LGPD, incluindo:</em></p>
    <ul>
      <li>Countries with adequate protection / Países com proteção adequada</li>
      <li>Standard contractual clauses / Cláusulas contratuais padrão</li>
      <li>Binding corporate rules / Normas corporativas vinculantes</li>
      <li>Your explicit consent / Seu consentimento explícito</li>
    </ul>
  </section>

  <section id="security">
    <h2>10. Data Security / Segurança dos Dados</h2>
    <p>We implement technical and administrative measures to protect personal data against unauthorized access, accidental or unlawful destruction, loss, alteration, or improper disclosure.<br>
    <em>Implementamos medidas técnicas e administrativas para proteger dados pessoais contra acesso não autorizado, destruição acidental ou ilícita, perda, alteração ou divulgação inadequada.</em></p>
  </section>

  <section id="children">
    <h2>11. Children's Data / Dados de Crianças</h2>
    <p>Processing of children's and adolescents' data (under 18) is done with parental/guardian consent and in their best interest, as required by LGPD Article 14.<br>
    <em>O tratamento de dados de crianças e adolescentes (menores de 18 anos) é realizado com consentimento dos pais/responsáveis e no melhor interesse deles, conforme Artigo 14 da LGPD.</em></p>
  </section>

  <section id="cookies">
    <h2>12. Cookies and Tracking / Cookies e Rastreamento</h2>
    <p>We use cookies and similar technologies. You can control preferences through browser settings. See our Cookie Policy for details.<br>
    <em>Usamos cookies e tecnologias similares. Você pode controlar preferências nas configurações do navegador. Veja nossa Política de Cookies para detalhes.</em></p>
  </section>

  <section id="breach">
    <h2>13. Data Breach Notification / Notificação de Incidentes</h2>
    <p>In case of a security incident that may create risk or significant damage to you, we will notify you and ANPD (National Data Protection Authority) within a reasonable timeframe as required by law.<br>
    <em>Em caso de incidente de segurança que possa criar risco ou dano relevante, notificaremos você e a ANPD (Autoridade Nacional de Proteção de Dados) em prazo razoável conforme exigido por lei.</em></p>
  </section>

  <section id="authority">
    <h2>14. National Data Protection Authority / Autoridade Nacional</h2>
    <div class="bilingual">
      <p>If you are not satisfied with our response, you may contact ANPD:<br>
      <em>Se não estiver satisfeito com nossa resposta, pode contatar a ANPD:</em></p>
      <ul>
        <li>Website: <a href="https://www.gov.br/anpd" target="_blank">www.gov.br/anpd</a></li>
        <li>Email: anpd@anpd.gov.br</li>
      </ul>
    </div>
  </section>

  <section id="updates">
    <h2>15. Updates to This Policy / Atualizações desta Política</h2>
    <p>We may update this policy from time to time. The "Last Updated" date indicates the most recent revision.<br>
    <em>Podemos atualizar esta política periodicamente. A data "Last Updated" indica a revisão mais recente.</em></p>
  </section>

  <section id="contact">
    <h2>16. Contact Us / Entre em Contato</h2>
    <div class="contact">
      <p>For questions about this privacy policy:<br>
      <em>Para dúvidas sobre esta política de privacidade:</em></p>
      <strong>{org.name}</strong><br>
      Email: <a href="mailto:{org.email}">{org.email}</a><br>
      {f'Phone: {org.phone}<br>' if org.phone else ''}
      {f'Data Protection Officer: <a href="mailto:{org.dpo_email}">{org.dpo_email}</a>' if org.dpo_email else ''}
    </div>
  </section>
</body>
</html>
"""


__all__ = [
    "Jurisdiction",
    "OrganizationInfo",
    "OutputFormat",
    "PrivacyStatement",
    "PrivacyStatementGenerator",
]
