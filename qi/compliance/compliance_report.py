"""Compliance Report Generator for multi-jurisdiction audit trails.

Generates comprehensive compliance reports for GDPR, CCPA, PIPEDA, and LGPD
covering consent history, data access logs, retention compliance, deletion
requests, and third-party disclosures.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from .privacy_statement import Jurisdiction


class LegalBasis(str, Enum):
    """Legal basis for data processing."""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGITIMATE_INTEREST = "legitimate_interest"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"


class DataCategory(str, Enum):
    """Categories of personal data."""

    PROFILE = "profile"
    CONTACT = "contact"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SPECIAL_CATEGORY = "special_category"


class AccessPurpose(str, Enum):
    """Purpose of data access."""

    AUTHENTICATION = "authentication"
    ANALYTICS = "analytics"
    SUPPORT = "support"
    PROCESSING = "processing"
    BACKUP = "backup"
    AUDIT = "audit"
    RESEARCH = "research"
    MARKETING = "marketing"


class AccessorType(str, Enum):
    """Type of entity accessing data."""

    SYSTEM = "system"
    USER = "user"
    ADMIN = "admin"
    THIRD_PARTY = "third_party"
    PROCESSOR = "processor"
    CONTROLLER = "controller"


class DeletionStatus(str, Enum):
    """Status of deletion requests."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PARTIAL = "partial"


class ConsentRecord(TypedDict):
    """Consent history record."""

    timestamp: str
    purpose: str
    legal_basis: str
    scope: List[str]
    active: bool
    withdrawn_at: Optional[str]
    expiry_date: Optional[str]


class AccessRecord(TypedDict):
    """Data access log record."""

    timestamp: str
    accessor: str
    accessor_type: str
    data_categories: List[str]
    purpose: str
    legal_basis: str
    ip_address: Optional[str]


class RetentionPolicy(TypedDict):
    """Data retention policy record."""

    data_category: str
    retention_period_days: int
    next_deletion_date: str
    policy_basis: str
    legal_requirement: bool


class DeletionRecord(TypedDict):
    """Deletion request record."""

    timestamp: str
    request_type: str
    scope: List[str]
    status: str
    completed_at: Optional[str]
    retention_exception: Optional[str]


class ThirdPartyDisclosure(TypedDict):
    """Third-party data sharing record."""

    name: str
    purpose: str
    data_categories: List[str]
    legal_basis: str
    safeguards: List[str]
    location: str
    active: bool


class SecurityEvent(TypedDict):
    """Security event record."""

    timestamp: str
    event_type: str
    description: str
    severity: str
    resolved: bool


class ComplianceReport(TypedDict):
    """Complete compliance report structure."""

    user_id: str
    jurisdiction: str
    report_date: str
    date_range: Dict[str, str]
    consent_history: List[ConsentRecord]
    data_access_log: List[AccessRecord]
    retention_compliance: Dict[str, RetentionPolicy]
    deletion_requests: List[DeletionRecord]
    third_party_disclosures: List[ThirdPartyDisclosure]
    security_events: Optional[List[SecurityEvent]]
    metadata: Dict[str, Any]


@dataclass
class GuardianAuditInterface:
    """Mock interface to Guardian System audit trails."""

    def get_access_logs(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[AccessRecord]:
        """Retrieve access logs from Guardian System.

        In production, this would query the actual Guardian audit trail.
        For now, returns mock data demonstrating the interface.
        """
        # Mock data - in production would query governance/guardian/
        return [
            {
                "timestamp": "2025-10-01T10:30:00Z",
                "accessor": "lukhas_api_v1",
                "accessor_type": AccessorType.SYSTEM.value,
                "data_categories": [DataCategory.PROFILE.value, DataCategory.TECHNICAL.value],
                "purpose": AccessPurpose.AUTHENTICATION.value,
                "legal_basis": LegalBasis.CONTRACT.value,
                "ip_address": None,
            },
            {
                "timestamp": "2025-10-15T14:22:00Z",
                "accessor": "admin_user_42",
                "accessor_type": AccessorType.ADMIN.value,
                "data_categories": [DataCategory.PROFILE.value],
                "purpose": AccessPurpose.SUPPORT.value,
                "legal_basis": LegalBasis.LEGITIMATE_INTEREST.value,
                "ip_address": "192.168.1.100",
            },
        ]

    def get_consent_records(self, user_id: str) -> List[ConsentRecord]:
        """Retrieve consent records from privacy system.

        In production, this would query qi/privacy/ consent management.
        """
        return [
            {
                "timestamp": "2025-09-01T08:00:00Z",
                "purpose": "Service provision and account management",
                "legal_basis": LegalBasis.CONSENT.value,
                "scope": ["profile", "contact", "technical"],
                "active": True,
                "withdrawn_at": None,
                "expiry_date": "2027-09-01T08:00:00Z",
            },
            {
                "timestamp": "2025-09-15T12:30:00Z",
                "purpose": "Marketing communications",
                "legal_basis": LegalBasis.CONSENT.value,
                "scope": ["contact"],
                "active": False,
                "withdrawn_at": "2025-10-01T09:00:00Z",
                "expiry_date": None,
            },
        ]

    def get_deletion_requests(self, user_id: str) -> List[DeletionRecord]:
        """Retrieve deletion requests from identity system."""
        return [
            {
                "timestamp": "2025-10-01T09:00:00Z",
                "request_type": "consent_withdrawal",
                "scope": ["marketing_preferences"],
                "status": DeletionStatus.COMPLETED.value,
                "completed_at": "2025-10-01T10:00:00Z",
                "retention_exception": None,
            }
        ]

    def get_security_events(self, user_id: str, start_date: datetime, end_date: datetime) -> List[SecurityEvent]:
        """Retrieve security events for user."""
        return [
            {
                "timestamp": "2025-09-20T16:45:00Z",
                "event_type": "password_change",
                "description": "User changed account password",
                "severity": "info",
                "resolved": True,
            },
            {
                "timestamp": "2025-10-05T11:30:00Z",
                "event_type": "failed_login",
                "description": "Failed login attempt from unusual location",
                "severity": "warning",
                "resolved": True,
            },
        ]


class ComplianceReportGenerator:
    """Generate compliance reports for multi-jurisdiction audit requirements."""

    def __init__(self) -> None:
        """Initialize compliance report generator."""
        self._guardian = GuardianAuditInterface()
        self._jurisdiction_requirements = {
            Jurisdiction.GDPR: self._gdpr_requirements,
            Jurisdiction.CCPA: self._ccpa_requirements,
            Jurisdiction.PIPEDA: self._pipeda_requirements,
            Jurisdiction.LGPD: self._lgpd_requirements,
        }

    def generate_report(
        self,
        user_id: str,
        jurisdiction: str | Jurisdiction,
        date_range: tuple[datetime, datetime],
        include_security_events: bool = True,
    ) -> ComplianceReport:
        """Generate a comprehensive compliance report.

        Args:
            user_id: User identifier for the report
            jurisdiction: Privacy jurisdiction (GDPR, CCPA, PIPEDA, LGPD)
            date_range: Tuple of (start_date, end_date) for the report period
            include_security_events: Whether to include security events section

        Returns:
            ComplianceReport with all required sections

        Raises:
            ValueError: If jurisdiction is not supported
        """
        # Normalize jurisdiction
        if isinstance(jurisdiction, str):
            try:
                jurisdiction = Jurisdiction(jurisdiction.upper())
            except ValueError:
                raise ValueError(
                    f"Unsupported jurisdiction: {jurisdiction}. "
                    f"Supported: {', '.join(j.value for j in Jurisdiction)}"
                )

        start_date, end_date = date_range

        # Gather all data
        consent_history = self._get_consent_history(user_id)
        data_access_log = self._get_access_log(user_id, start_date, end_date)
        retention_compliance = self._get_retention_compliance(user_id)
        deletion_requests = self._get_deletion_requests(user_id)
        third_party_disclosures = self._get_third_party_disclosures(user_id)

        security_events = None
        if include_security_events:
            security_events = self._get_security_events(user_id, start_date, end_date)

        # Build report
        report: ComplianceReport = {
            "user_id": self._redact_internal_id(user_id),
            "jurisdiction": jurisdiction.value,
            "report_date": datetime.now(timezone.utc).isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "consent_history": consent_history,
            "data_access_log": data_access_log,
            "retention_compliance": retention_compliance,
            "deletion_requests": deletion_requests,
            "third_party_disclosures": third_party_disclosures,
            "security_events": security_events,
            "metadata": self._generate_metadata(jurisdiction, len(data_access_log)),
        }

        # Apply jurisdiction-specific requirements
        requirements_func = self._jurisdiction_requirements.get(jurisdiction)
        if requirements_func:
            report = requirements_func(report)

        return report

    def export_json(self, report: ComplianceReport) -> str:
        """Export report to JSON format.

        Args:
            report: ComplianceReport to export

        Returns:
            JSON string representation
        """
        return json.dumps(report, indent=2, ensure_ascii=False)

    def export_html(self, report: ComplianceReport) -> str:
        """Export report to HTML format.

        Args:
            report: ComplianceReport to export

        Returns:
            HTML string representation
        """
        # Build HTML report
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"  <title>Compliance Report - {report['jurisdiction']}</title>",
            "  <style>",
            "    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }",
            "    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }",
            "    h2 { color: #34495e; margin-top: 30px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }",
            "    h3 { color: #7f8c8d; }",
            "    .metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }",
            "    .section { margin-bottom: 30px; }",
            "    table { width: 100%; border-collapse: collapse; margin: 15px 0; }",
            "    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }",
            "    th { background-color: #3498db; color: white; }",
            "    tr:hover { background-color: #f5f5f5; }",
            "    .active { color: #27ae60; font-weight: bold; }",
            "    .inactive { color: #e74c3c; font-weight: bold; }",
            "    .badge { padding: 3px 8px; border-radius: 3px; font-size: 0.9em; }",
            "    .badge-success { background: #d4edda; color: #155724; }",
            "    .badge-warning { background: #fff3cd; color: #856404; }",
            "    .badge-danger { background: #f8d7da; color: #721c24; }",
            "  </style>",
            "</head>",
            "<body>",
            f'  <h1>Compliance Report - {report["jurisdiction"]}</h1>',
            '  <div class="metadata">',
            f'    <p><strong>Report Date:</strong> {report["report_date"]}</p>',
            f'    <p><strong>User ID:</strong> {report["user_id"]}</p>',
            f'    <p><strong>Reporting Period:</strong> {report["date_range"]["start"]} to {report["date_range"]["end"]}</p>',
            f'    <p><strong>Report Hash:</strong> {report["metadata"].get("report_hash", "N/A")}</p>',
            "  </div>",
        ]

        # Consent History section
        html_parts.extend(self._render_consent_history_html(report["consent_history"]))

        # Data Access Log section
        html_parts.extend(self._render_access_log_html(report["data_access_log"]))

        # Retention Compliance section
        html_parts.extend(self._render_retention_html(report["retention_compliance"]))

        # Deletion Requests section
        html_parts.extend(self._render_deletions_html(report["deletion_requests"]))

        # Third-Party Disclosures section
        html_parts.extend(self._render_third_party_html(report["third_party_disclosures"]))

        # Security Events section (optional)
        if report.get("security_events"):
            html_parts.extend(self._render_security_events_html(report["security_events"]))

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)

    # Helper methods

    def _get_consent_history(self, user_id: str) -> List[ConsentRecord]:
        """Retrieve consent history for user."""
        return self._guardian.get_consent_records(user_id)

    def _get_access_log(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[AccessRecord]:
        """Retrieve data access log for user within date range."""
        all_logs = self._guardian.get_access_logs(user_id, start_date, end_date)

        # Filter by date range and redact sensitive fields
        filtered_logs = []
        for log in all_logs:
            log_time = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            if start_date <= log_time <= end_date:
                # Redact IP addresses in logs
                if log.get("ip_address"):
                    log["ip_address"] = self._redact_ip_address(log["ip_address"])
                filtered_logs.append(log)

        return filtered_logs

    def _get_retention_compliance(self, user_id: str) -> Dict[str, RetentionPolicy]:
        """Calculate retention compliance for all data categories."""
        # Mock retention policies - in production would query actual policies
        policies: Dict[str, RetentionPolicy] = {
            "profile": {
                "data_category": "profile",
                "retention_period_days": 2555,  # 7 years
                "next_deletion_date": "2032-09-01T00:00:00Z",
                "policy_basis": "Regulatory requirement (financial records)",
                "legal_requirement": True,
            },
            "contact": {
                "data_category": "contact",
                "retention_period_days": 730,  # 2 years
                "next_deletion_date": "2027-09-01T00:00:00Z",
                "policy_basis": "Contract requirement",
                "legal_requirement": False,
            },
            "technical": {
                "data_category": "technical",
                "retention_period_days": 90,
                "next_deletion_date": "2025-12-30T00:00:00Z",
                "policy_basis": "Security and fraud prevention",
                "legal_requirement": False,
            },
        }
        return policies

    def _get_deletion_requests(self, user_id: str) -> List[DeletionRecord]:
        """Retrieve deletion requests for user."""
        return self._guardian.get_deletion_requests(user_id)

    def _get_third_party_disclosures(self, user_id: str) -> List[ThirdPartyDisclosure]:
        """Retrieve third-party data sharing information."""
        # Mock third-party disclosures - in production would query actual data
        return [
            {
                "name": "Cloud Storage Provider Inc.",
                "purpose": "Data backup and storage",
                "data_categories": ["profile", "technical"],
                "legal_basis": LegalBasis.CONTRACT.value,
                "safeguards": ["Standard Contractual Clauses (SCCs)", "Encryption in transit and at rest"],
                "location": "European Union",
                "active": True,
            },
            {
                "name": "Analytics Service Ltd.",
                "purpose": "Usage analytics and service improvement",
                "data_categories": ["behavioral", "technical"],
                "legal_basis": LegalBasis.LEGITIMATE_INTEREST.value,
                "safeguards": ["Data Processing Agreement (DPA)", "Pseudonymization"],
                "location": "United States (Privacy Shield equivalent)",
                "active": True,
            },
        ]

    def _get_security_events(
        self, user_id: str, start_date: datetime, end_date: datetime
    ) -> List[SecurityEvent]:
        """Retrieve security events for user within date range."""
        all_events = self._guardian.get_security_events(user_id, start_date, end_date)

        # Filter by date range
        filtered_events = []
        for event in all_events:
            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
            if start_date <= event_time <= end_date:
                filtered_events.append(event)

        return filtered_events

    def _redact_internal_id(self, user_id: str) -> str:
        """Pseudonymize internal user ID for privacy."""
        # Use first 8 chars of hash for pseudonymization
        hashed = hashlib.sha256(user_id.encode()).hexdigest()
        return f"user_{hashed[:8]}"

    def _redact_ip_address(self, ip_address: str) -> str:
        """Redact IP address for privacy (keep first two octets for IPv4)."""
        if "." in ip_address:  # IPv4
            parts = ip_address.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.xxx.xxx"
        elif ":" in ip_address:  # IPv6
            parts = ip_address.split(":")
            if len(parts) >= 3:
                return f"{parts[0]}:{parts[1]}:{parts[2]}:xxxx:xxxx:xxxx:xxxx:xxxx"
        return "xxx.xxx.xxx.xxx"

    def _generate_metadata(self, jurisdiction: Jurisdiction, access_count: int) -> Dict[str, Any]:
        """Generate report metadata."""
        report_data = f"{jurisdiction.value}_{access_count}_{datetime.now(timezone.utc).isoformat()}"
        report_hash = hashlib.sha256(report_data.encode()).hexdigest()[:16]

        return {
            "version": "1.0",
            "generator": "LUKHAS ComplianceReportGenerator",
            "report_hash": report_hash,
            "jurisdiction_standard": jurisdiction.value,
            "total_access_records": access_count,
        }

    # Jurisdiction-specific requirement methods

    def _gdpr_requirements(self, report: ComplianceReport) -> ComplianceReport:
        """Apply GDPR Article 15 (Right of Access) requirements."""
        # GDPR requires disclosure of processing activities
        if "metadata" not in report:
            report["metadata"] = {}

        report["metadata"]["gdpr_article_15"] = True
        report["metadata"]["processing_activities"] = [
            "Account authentication and management",
            "Service provision and improvement",
            "Security and fraud prevention",
        ]
        report["metadata"]["automated_decision_making"] = "No automated decision-making or profiling is performed"
        report["metadata"]["data_retention_period"] = "Varies by data category (see Retention Compliance section)"

        # Add third-country transfer info
        non_eu_transfers = [
            tp for tp in report["third_party_disclosures"]
            if "European Union" not in tp.get("location", "")
        ]
        report["metadata"]["third_country_transfers"] = len(non_eu_transfers)

        return report

    def _ccpa_requirements(self, report: ComplianceReport) -> ComplianceReport:
        """Apply CCPA requirements."""
        if "metadata" not in report:
            report["metadata"] = {}

        # CCPA requires categories and sources
        report["metadata"]["ccpa_compliance"] = True
        report["metadata"]["data_sale_status"] = "We do not sell your personal information"
        report["metadata"]["categories_collected"] = list(
            set(cat for record in report["data_access_log"] for cat in record["data_categories"])
        )
        report["metadata"]["business_purposes"] = [
            "Providing services as requested",
            "Security and fraud prevention",
            "Service improvement and analytics",
        ]
        report["metadata"]["sources_of_information"] = [
            "Directly from you (account registration, usage)",
            "Automatically (device information, logs)",
        ]

        return report

    def _pipeda_requirements(self, report: ComplianceReport) -> ComplianceReport:
        """Apply PIPEDA requirements."""
        if "metadata" not in report:
            report["metadata"] = {}

        report["metadata"]["pipeda_compliance"] = True
        report["metadata"]["information_holdings"] = "See Data Access Log and Retention Compliance sections"
        report["metadata"]["uses_of_information"] = "See Consent History for all approved uses"
        report["metadata"]["disclosure_to_third_parties"] = f"{len(report['third_party_disclosures'])} third parties"
        report["metadata"]["accuracy_statement"] = "You may request corrections to your personal information"
        report["metadata"]["retention_policy"] = "See Retention Compliance section for specific periods"

        return report

    def _lgpd_requirements(self, report: ComplianceReport) -> ComplianceReport:
        """Apply LGPD requirements."""
        if "metadata" not in report:
            report["metadata"] = {}

        report["metadata"]["lgpd_compliance"] = True
        report["metadata"]["processing_purposes"] = "See Consent History for all processing purposes"
        report["metadata"]["data_sharing"] = f"{len(report['third_party_disclosures'])} third-party recipients"

        # International transfers
        international_transfers = [
            tp for tp in report["third_party_disclosures"]
            if "Brazil" not in tp.get("location", "")
        ]
        report["metadata"]["international_transfers"] = len(international_transfers)
        report["metadata"]["safeguards_for_transfers"] = [
            tp["safeguards"] for tp in international_transfers
        ] if international_transfers else []

        report["metadata"]["retention_period"] = "See Retention Compliance section"
        report["metadata"]["data_subject_rights"] = (
            "Confirmation, access, correction, anonymization, blocking, "
            "deletion, portability, information about sharing, "
            "right to not provide consent, and revocation of consent"
        )

        return report

    # HTML rendering helpers

    def _render_consent_history_html(self, consents: List[ConsentRecord]) -> List[str]:
        """Render consent history section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>A. Consent History</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Timestamp</th>",
            "        <th>Purpose</th>",
            "        <th>Legal Basis</th>",
            "        <th>Scope</th>",
            "        <th>Status</th>",
            "      </tr>",
        ]

        for consent in consents:
            status_class = "active" if consent["active"] else "inactive"
            status_text = "Active" if consent["active"] else f"Withdrawn ({consent.get('withdrawn_at', 'N/A')})"
            scope_text = ", ".join(consent["scope"])

            html.extend([
                "      <tr>",
                f'        <td>{consent["timestamp"]}</td>',
                f'        <td>{consent["purpose"]}</td>',
                f'        <td>{consent["legal_basis"]}</td>',
                f'        <td>{scope_text}</td>',
                f'        <td class="{status_class}">{status_text}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _render_access_log_html(self, accesses: List[AccessRecord]) -> List[str]:
        """Render data access log section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>B. Data Access Log</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Timestamp</th>",
            "        <th>Accessor</th>",
            "        <th>Type</th>",
            "        <th>Data Categories</th>",
            "        <th>Purpose</th>",
            "        <th>Legal Basis</th>",
            "      </tr>",
        ]

        for access in accesses:
            categories_text = ", ".join(access["data_categories"])

            html.extend([
                "      <tr>",
                f'        <td>{access["timestamp"]}</td>',
                f'        <td>{access["accessor"]}</td>',
                f'        <td>{access["accessor_type"]}</td>',
                f'        <td>{categories_text}</td>',
                f'        <td>{access["purpose"]}</td>',
                f'        <td>{access["legal_basis"]}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _render_retention_html(self, retention: Dict[str, RetentionPolicy]) -> List[str]:
        """Render retention compliance section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>C. Retention Compliance</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Data Category</th>",
            "        <th>Retention Period</th>",
            "        <th>Next Deletion Date</th>",
            "        <th>Policy Basis</th>",
            "      </tr>",
        ]

        for policy in retention.values():
            days = policy["retention_period_days"]
            years = days // 365
            period_text = f"{years} years" if years > 0 else f"{days} days"

            html.extend([
                "      <tr>",
                f'        <td>{policy["data_category"]}</td>',
                f'        <td>{period_text} ({days} days)</td>',
                f'        <td>{policy["next_deletion_date"]}</td>',
                f'        <td>{policy["policy_basis"]}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _render_deletions_html(self, deletions: List[DeletionRecord]) -> List[str]:
        """Render deletion requests section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>D. Deletion Requests</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Timestamp</th>",
            "        <th>Request Type</th>",
            "        <th>Scope</th>",
            "        <th>Status</th>",
            "        <th>Completed</th>",
            "      </tr>",
        ]

        for deletion in deletions:
            scope_text = ", ".join(deletion["scope"])
            status_badge = self._get_status_badge(deletion["status"])

            html.extend([
                "      <tr>",
                f'        <td>{deletion["timestamp"]}</td>',
                f'        <td>{deletion["request_type"]}</td>',
                f'        <td>{scope_text}</td>',
                f'        <td>{status_badge}</td>',
                f'        <td>{deletion.get("completed_at", "N/A")}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _render_third_party_html(self, third_parties: List[ThirdPartyDisclosure]) -> List[str]:
        """Render third-party disclosures section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>E. Third-Party Disclosures</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Third Party</th>",
            "        <th>Purpose</th>",
            "        <th>Data Categories</th>",
            "        <th>Legal Basis</th>",
            "        <th>Safeguards</th>",
            "        <th>Location</th>",
            "      </tr>",
        ]

        for tp in third_parties:
            categories_text = ", ".join(tp["data_categories"])
            safeguards_text = ", ".join(tp["safeguards"])

            html.extend([
                "      <tr>",
                f'        <td>{tp["name"]}</td>',
                f'        <td>{tp["purpose"]}</td>',
                f'        <td>{categories_text}</td>',
                f'        <td>{tp["legal_basis"]}</td>',
                f'        <td>{safeguards_text}</td>',
                f'        <td>{tp["location"]}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _render_security_events_html(self, events: List[SecurityEvent]) -> List[str]:
        """Render security events section as HTML."""
        html = [
            '  <div class="section">',
            "    <h2>F. Security Events</h2>",
            "    <table>",
            "      <tr>",
            "        <th>Timestamp</th>",
            "        <th>Event Type</th>",
            "        <th>Description</th>",
            "        <th>Severity</th>",
            "        <th>Resolved</th>",
            "      </tr>",
        ]

        for event in events:
            severity_badge = self._get_severity_badge(event["severity"])
            resolved_text = "Yes" if event["resolved"] else "No"

            html.extend([
                "      <tr>",
                f'        <td>{event["timestamp"]}</td>',
                f'        <td>{event["event_type"]}</td>',
                f'        <td>{event["description"]}</td>',
                f'        <td>{severity_badge}</td>',
                f'        <td>{resolved_text}</td>',
                "      </tr>",
            ])

        html.extend(["    </table>", "  </div>"])
        return html

    def _get_status_badge(self, status: str) -> str:
        """Get HTML badge for deletion status."""
        badge_class = {
            "completed": "badge-success",
            "in_progress": "badge-warning",
            "pending": "badge-warning",
            "rejected": "badge-danger",
            "partial": "badge-warning",
        }.get(status.lower(), "badge-warning")

        return f'<span class="badge {badge_class}">{status}</span>'

    def _get_severity_badge(self, severity: str) -> str:
        """Get HTML badge for security event severity."""
        badge_class = {
            "info": "badge-success",
            "warning": "badge-warning",
            "error": "badge-danger",
            "critical": "badge-danger",
        }.get(severity.lower(), "badge-warning")

        return f'<span class="badge {badge_class}">{severity}</span>'


__all__ = [
    "ComplianceReportGenerator",
    "ComplianceReport",
    "ConsentRecord",
    "AccessRecord",
    "RetentionPolicy",
    "DeletionRecord",
    "ThirdPartyDisclosure",
    "SecurityEvent",
    "LegalBasis",
    "DataCategory",
    "AccessPurpose",
    "AccessorType",
    "DeletionStatus",
]
