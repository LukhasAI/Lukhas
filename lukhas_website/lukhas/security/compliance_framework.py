#!/usr/bin/env python3
"""
LUKHAS Security - Compliance Framework
=====================================

Comprehensive compliance management system supporting SOC2, ISO27001, NIST, and other standards.
Provides automated compliance validation, audit trail management, and reporting with T4/0.01% excellence.

Key Features:
- SOC 2 Type II compliance validation
- ISO 27001 information security management
- NIST Cybersecurity Framework alignment
- GDPR/CCPA privacy compliance
- Automated control testing
- Continuous compliance monitoring
- Audit trail preservation
- Risk assessment and management
- Evidence collection and management
- Compliance dashboard and reporting

Constellation Framework: 🛡️ Guardian Excellence - Compliance Management
"""

import hashlib
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Supported compliance standards."""
    SOC2_TYPE2 = "soc2_type2"
    ISO27001 = "iso27001"
    NIST_CSF = "nist_csf"
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"

class ControlStatus(Enum):
    """Control implementation status."""
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    VERIFIED = "verified"
    NON_COMPLIANT = "non_compliant"

class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EvidenceType(Enum):
    """Types of compliance evidence."""
    POLICY_DOCUMENT = "policy_document"
    PROCEDURE = "procedure"
    LOG_FILE = "log_file"
    AUDIT_REPORT = "audit_report"
    CONFIGURATION = "configuration"
    TRAINING_RECORD = "training_record"
    ASSESSMENT_RESULT = "assessment_result"
    SCREENSHOT = "screenshot"
    CERTIFICATE = "certificate"

@dataclass
class ComplianceControl:
    """Individual compliance control definition."""
    id: str
    name: str
    description: str
    standard: ComplianceStandard
    category: str  # e.g., "Access Control", "Data Protection"
    requirements: List[str] = field(default_factory=list)
    implementation_guidance: str = ""
    testing_procedures: List[str] = field(default_factory=list)
    automation_possible: bool = False
    frequency: str = "annual"  # daily, weekly, monthly, quarterly, annual
    risk_level: RiskLevel = RiskLevel.MEDIUM
    owner: Optional[str] = None
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    last_tested: Optional[datetime] = None
    next_test_due: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceEvidence:
    """Evidence for compliance control."""
    id: str
    control_id: str
    type: EvidenceType
    title: str
    description: str
    file_path: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    hash_sha256: Optional[str] = None
    collected_by: Optional[str] = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceAssessment:
    """Compliance assessment result."""
    id: str
    control_id: str
    assessment_type: str  # "automated", "manual", "walkthrough"
    result: ControlStatus
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    assessed_by: Optional[str] = None
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    next_assessment: Optional[datetime] = None
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskAssessment:
    """Risk assessment for compliance."""
    id: str
    title: str
    description: str
    risk_category: str
    likelihood: RiskLevel
    impact: RiskLevel
    inherent_risk: RiskLevel
    residual_risk: RiskLevel
    risk_owner: Optional[str] = None
    mitigation_controls: List[str] = field(default_factory=list)
    treatment_plan: Optional[str] = None
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    review_date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceReport:
    """Compliance status report."""
    id: str
    standard: ComplianceStandard
    reporting_period: Tuple[datetime, datetime]
    overall_status: str
    controls_summary: Dict[str, int] = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    risk_summary: Dict[str, int] = field(default_factory=dict)
    evidence_count: int = 0
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ComplianceFramework:
    """Comprehensive compliance management system."""

    def __init__(self,
                 evidence_path: str = "./compliance_evidence",
                 guardian_integration: bool = True):

        self.evidence_path = evidence_path
        self.guardian_integration = guardian_integration

        # Core data stores
        self.controls: Dict[str, ComplianceControl] = {}
        self.evidence: Dict[str, ComplianceEvidence] = {}
        self.assessments: Dict[str, ComplianceAssessment] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}

        # Compliance frameworks
        self.standards: Dict[ComplianceStandard, Dict[str, Any]] = {}

        # Automation handlers
        self.automation_handlers: Dict[str, callable] = {}

        # Performance tracking
        self.assessment_count = 0
        self.automation_count = 0

        # Ensure evidence directory exists
        os.makedirs(evidence_path, exist_ok=True)

        # Initialize compliance standards
        self._initialize_standards()

        logger.info("Compliance Framework initialized")

    def _initialize_standards(self):
        """Initialize compliance standards and controls."""

        # SOC 2 Type II Controls
        self._initialize_soc2_controls()

        # ISO 27001 Controls
        self._initialize_iso27001_controls()

        # NIST Cybersecurity Framework
        self._initialize_nist_csf_controls()

        # GDPR Controls
        self._initialize_gdpr_controls()

    def _initialize_soc2_controls(self):
        """Initialize SOC 2 Type II controls."""
        soc2_controls = [
            ComplianceControl(
                id="CC1.1",
                name="Management's Philosophy and Operating Style",
                description="The entity demonstrates a commitment to integrity and ethical values",
                standard=ComplianceStandard.SOC2_TYPE2,
                category="Common Criteria - Control Environment",
                requirements=[
                    "Code of conduct established and communicated",
                    "Management demonstrates integrity and ethical values",
                    "Policies for conflicts of interest exist"
                ],
                implementation_guidance="Establish and communicate code of conduct, demonstrate leadership commitment",
                testing_procedures=[
                    "Review code of conduct documentation",
                    "Interview management about ethics policies",
                    "Test communication of ethical standards"
                ],
                automation_possible=False,
                frequency="annual"
            ),
            ComplianceControl(
                id="CC2.1",
                name="Communication and Information",
                description="Information systems facilitate the design and operation of internal controls",
                standard=ComplianceStandard.SOC2_TYPE2,
                category="Common Criteria - Communication",
                requirements=[
                    "Information systems support control activities",
                    "Information quality is maintained",
                    "Communication channels are established"
                ],
                implementation_guidance="Implement information systems that support control objectives",
                testing_procedures=[
                    "Review information system architecture",
                    "Test data quality controls",
                    "Verify communication processes"
                ],
                automation_possible=True,
                frequency="quarterly"
            ),
            ComplianceControl(
                id="CC6.1",
                name="Logical and Physical Access Controls",
                description="Entity implements access controls to protect system resources",
                standard=ComplianceStandard.SOC2_TYPE2,
                category="Common Criteria - Logical Access",
                requirements=[
                    "User access provisioning and deprovisioning",
                    "Strong authentication mechanisms",
                    "Access review processes",
                    "Physical access controls"
                ],
                implementation_guidance="Implement comprehensive access control system with RBAC",
                testing_procedures=[
                    "Test user provisioning process",
                    "Review access control configurations",
                    "Test authentication mechanisms",
                    "Validate access reviews"
                ],
                automation_possible=True,
                frequency="monthly"
            ),
            ComplianceControl(
                id="CC7.1",
                name="System Operations",
                description="Entity monitors system capacity and utilization",
                standard=ComplianceStandard.SOC2_TYPE2,
                category="Common Criteria - System Operations",
                requirements=[
                    "Capacity monitoring and management",
                    "Performance monitoring",
                    "Incident response procedures",
                    "Change management processes"
                ],
                implementation_guidance="Implement comprehensive system monitoring and management",
                testing_procedures=[
                    "Review monitoring configurations",
                    "Test incident response procedures",
                    "Validate change management process"
                ],
                automation_possible=True,
                frequency="monthly"
            )
        ]

        for control in soc2_controls:
            self.controls[control.id] = control

    def _initialize_iso27001_controls(self):
        """Initialize ISO 27001 controls."""
        iso27001_controls = [
            ComplianceControl(
                id="A.5.1.1",
                name="Information Security Policy",
                description="Information security policy shall be defined and approved by management",
                standard=ComplianceStandard.ISO27001,
                category="Information Security Policies",
                requirements=[
                    "Information security policy documented",
                    "Policy approved by management",
                    "Policy communicated to all personnel",
                    "Policy reviewed regularly"
                ],
                implementation_guidance="Develop comprehensive information security policy",
                testing_procedures=[
                    "Review policy documentation",
                    "Verify management approval",
                    "Test policy communication"
                ],
                automation_possible=False,
                frequency="annual"
            ),
            ComplianceControl(
                id="A.9.1.1",
                name="Access Control Policy",
                description="Access control policy shall be established and reviewed",
                standard=ComplianceStandard.ISO27001,
                category="Access Control",
                requirements=[
                    "Access control policy documented",
                    "Role-based access controls implemented",
                    "Regular access reviews conducted",
                    "Privileged access managed"
                ],
                implementation_guidance="Implement comprehensive access control framework",
                testing_procedures=[
                    "Review access control policies",
                    "Test RBAC implementation",
                    "Validate access review process"
                ],
                automation_possible=True,
                frequency="monthly"
            ),
            ComplianceControl(
                id="A.12.6.1",
                name="Management of Technical Vulnerabilities",
                description="Information about technical vulnerabilities shall be obtained",
                standard=ComplianceStandard.ISO27001,
                category="Operations Security",
                requirements=[
                    "Vulnerability management process established",
                    "Regular vulnerability assessments conducted",
                    "Patches and updates managed",
                    "Vulnerability remediation tracking"
                ],
                implementation_guidance="Implement comprehensive vulnerability management program",
                testing_procedures=[
                    "Review vulnerability management process",
                    "Test vulnerability scanning procedures",
                    "Validate patch management process"
                ],
                automation_possible=True,
                frequency="monthly"
            )
        ]

        for control in iso27001_controls:
            self.controls[control.id] = control

    def _initialize_nist_csf_controls(self):
        """Initialize NIST Cybersecurity Framework controls."""
        nist_controls = [
            ComplianceControl(
                id="ID.AM-1",
                name="Asset Inventory",
                description="Physical devices and systems are inventoried",
                standard=ComplianceStandard.NIST_CSF,
                category="Identify - Asset Management",
                requirements=[
                    "Hardware asset inventory maintained",
                    "Software asset inventory maintained",
                    "Asset criticality classification",
                    "Asset ownership documented"
                ],
                implementation_guidance="Maintain comprehensive asset inventory with automated discovery",
                testing_procedures=[
                    "Review asset inventory completeness",
                    "Test automated discovery tools",
                    "Validate asset classifications"
                ],
                automation_possible=True,
                frequency="monthly"
            ),
            ComplianceControl(
                id="PR.AC-1",
                name="Identity and Credential Management",
                description="Identities and credentials are issued and managed",
                standard=ComplianceStandard.NIST_CSF,
                category="Protect - Access Control",
                requirements=[
                    "Identity lifecycle management",
                    "Credential management processes",
                    "Multi-factor authentication",
                    "Privileged account management"
                ],
                implementation_guidance="Implement comprehensive identity and access management",
                testing_procedures=[
                    "Test identity provisioning process",
                    "Validate credential management",
                    "Review MFA implementation"
                ],
                automation_possible=True,
                frequency="monthly"
            ),
            ComplianceControl(
                id="DE.CM-1",
                name="Security Monitoring",
                description="Network is monitored to detect potential cybersecurity events",
                standard=ComplianceStandard.NIST_CSF,
                category="Detect - Security Continuous Monitoring",
                requirements=[
                    "Network monitoring implemented",
                    "Security event correlation",
                    "Threat intelligence integration",
                    "Baseline behavior established"
                ],
                implementation_guidance="Deploy comprehensive security monitoring and SIEM",
                testing_procedures=[
                    "Test monitoring coverage",
                    "Validate event correlation",
                    "Review threat intelligence feeds"
                ],
                automation_possible=True,
                frequency="continuous"
            )
        ]

        for control in nist_controls:
            self.controls[control.id] = control

    def _initialize_gdpr_controls(self):
        """Initialize GDPR compliance controls."""
        gdpr_controls = [
            ComplianceControl(
                id="GDPR.7",
                name="Consent Management",
                description="Lawful basis for processing personal data established",
                standard=ComplianceStandard.GDPR,
                category="Lawfulness of Processing",
                requirements=[
                    "Lawful basis documented for each processing activity",
                    "Consent mechanisms implemented",
                    "Consent withdrawal capabilities",
                    "Processing records maintained"
                ],
                implementation_guidance="Implement comprehensive consent management system",
                testing_procedures=[
                    "Review consent collection mechanisms",
                    "Test consent withdrawal process",
                    "Validate processing records"
                ],
                automation_possible=True,
                frequency="monthly"
            ),
            ComplianceControl(
                id="GDPR.25",
                name="Data Protection by Design",
                description="Data protection measures built into processing systems",
                standard=ComplianceStandard.GDPR,
                category="Data Protection by Design and by Default",
                requirements=[
                    "Privacy impact assessments conducted",
                    "Data minimization implemented",
                    "Purpose limitation enforced",
                    "Privacy-enhancing technologies used"
                ],
                implementation_guidance="Integrate privacy controls into system design",
                testing_procedures=[
                    "Review privacy impact assessments",
                    "Test data minimization controls",
                    "Validate purpose limitation"
                ],
                automation_possible=True,
                frequency="quarterly"
            ),
            ComplianceControl(
                id="GDPR.32",
                name="Security of Processing",
                description="Appropriate technical and organizational measures for security",
                standard=ComplianceStandard.GDPR,
                category="Security of Processing",
                requirements=[
                    "Encryption of personal data",
                    "Integrity and confidentiality measures",
                    "Availability and resilience controls",
                    "Regular security testing"
                ],
                implementation_guidance="Implement comprehensive data security measures",
                testing_procedures=[
                    "Test encryption implementation",
                    "Validate integrity controls",
                    "Review security testing results"
                ],
                automation_possible=True,
                frequency="monthly"
            )
        ]

        for control in gdpr_controls:
            self.controls[control.id] = control

    def register_automation_handler(self, control_id: str, handler: callable):
        """Register automation handler for control testing."""
        self.automation_handlers[control_id] = handler
        logger.info(f"Registered automation handler for control {control_id}")

    def assess_control(self,
                      control_id: str,
                      assessment_type: str = "automated",
                      assessor: Optional[str] = None) -> ComplianceAssessment:
        """
        Assess compliance control implementation.

        Args:
            control_id: Control identifier
            assessment_type: Type of assessment (automated, manual, walkthrough)
            assessor: Person conducting assessment

        Returns:
            ComplianceAssessment result
        """
        if control_id not in self.controls:
            raise ValueError(f"Control {control_id} not found")

        control = self.controls[control_id]
        assessment_id = f"ASS-{control_id}-{int(time.time())}"

        logger.info(f"Assessing control {control_id} ({assessment_type})")

        # Perform assessment based on type
        if assessment_type == "automated" and control_id in self.automation_handlers:
            result = self._run_automated_assessment(control, assessment_id)
        else:
            result = self._run_manual_assessment(control, assessment_id, assessor)

        # Store assessment
        self.assessments[assessment_id] = result
        self.assessment_count += 1

        # Update control status
        control.status = result.result
        control.last_tested = result.assessed_at

        # Calculate next assessment date
        if control.frequency == "continuous" or control.frequency == "daily":
            control.next_test_due = datetime.now(timezone.utc) + timedelta(days=1)
        elif control.frequency == "weekly":
            control.next_test_due = datetime.now(timezone.utc) + timedelta(weeks=1)
        elif control.frequency == "monthly":
            control.next_test_due = datetime.now(timezone.utc) + timedelta(days=30)
        elif control.frequency == "quarterly":
            control.next_test_due = datetime.now(timezone.utc) + timedelta(days=90)
        elif control.frequency == "annual":
            control.next_test_due = datetime.now(timezone.utc) + timedelta(days=365)

        logger.info(f"Assessment completed: {control_id} - {result.result.value}")
        return result

    def _run_automated_assessment(self, control: ComplianceControl, assessment_id: str) -> ComplianceAssessment:
        """Run automated control assessment."""
        handler = self.automation_handlers[control.id]

        try:
            # Execute automation handler
            handler_result = handler(control)

            # Parse handler result
            if isinstance(handler_result, dict):
                result_status = ControlStatus(handler_result.get("status", "implemented"))
                findings = handler_result.get("findings", [])
                recommendations = handler_result.get("recommendations", [])
                confidence = handler_result.get("confidence", 1.0)
                metadata = handler_result.get("metadata", {})
            else:
                # Boolean result
                result_status = ControlStatus.IMPLEMENTED if handler_result else ControlStatus.NON_COMPLIANT
                findings = [] if handler_result else ["Automated test failed"]
                recommendations = [] if handler_result else ["Review control implementation"]
                confidence = 1.0
                metadata = {}

            self.automation_count += 1

        except Exception as e:
            logger.exception(f"Automated assessment failed for {control.id}: {e}")
            result_status = ControlStatus.NON_COMPLIANT
            findings = [f"Assessment automation failed: {e!s}"]
            recommendations = ["Review automation handler and control implementation"]
            confidence = 0.5
            metadata = {"error": str(e)}

        return ComplianceAssessment(
            id=assessment_id,
            control_id=control.id,
            assessment_type="automated",
            result=result_status,
            findings=findings,
            recommendations=recommendations,
            assessed_by="automation_system",
            confidence_score=confidence,
            metadata=metadata
        )

    def _run_manual_assessment(self, control: ComplianceControl, assessment_id: str, assessor: Optional[str]) -> ComplianceAssessment:
        """Run manual control assessment (placeholder)."""
        # In a real implementation, this would integrate with assessment workflows
        # For now, return a placeholder result

        return ComplianceAssessment(
            id=assessment_id,
            control_id=control.id,
            assessment_type="manual",
            result=ControlStatus.PARTIALLY_IMPLEMENTED,
            findings=["Manual assessment required"],
            recommendations=["Complete manual assessment procedures"],
            assessed_by=assessor or "manual_assessor",
            confidence_score=0.7,
            metadata={"manual_assessment": True}
        )

    def collect_evidence(self,
                        control_id: str,
                        evidence_type: EvidenceType,
                        title: str,
                        description: str,
                        file_path: Optional[str] = None,
                        content: Optional[str] = None,
                        url: Optional[str] = None,
                        collector: Optional[str] = None) -> str:
        """
        Collect compliance evidence for a control.

        Args:
            control_id: Control identifier
            evidence_type: Type of evidence
            title: Evidence title
            description: Evidence description
            file_path: Path to evidence file
            content: Text content of evidence
            url: URL reference for evidence
            collector: Person collecting evidence

        Returns:
            Evidence ID
        """
        evidence_id = f"EVD-{control_id}-{int(time.time())}"

        # Calculate hash if file provided
        file_hash = None
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

        # Create evidence record
        evidence = ComplianceEvidence(
            id=evidence_id,
            control_id=control_id,
            type=evidence_type,
            title=title,
            description=description,
            file_path=file_path,
            url=url,
            content=content,
            hash_sha256=file_hash,
            collected_by=collector
        )

        self.evidence[evidence_id] = evidence

        logger.info(f"Evidence collected for {control_id}: {title}")
        return evidence_id

    def run_risk_assessment(self,
                          title: str,
                          description: str,
                          risk_category: str,
                          likelihood: RiskLevel,
                          impact: RiskLevel,
                          assessor: Optional[str] = None) -> str:
        """
        Run risk assessment.

        Args:
            title: Risk title
            description: Risk description
            risk_category: Category of risk
            likelihood: Likelihood level
            impact: Impact level
            assessor: Risk assessor

        Returns:
            Risk assessment ID
        """
        risk_id = f"RISK-{int(time.time())}-{str(uuid.uuid4())[:8]}"

        # Calculate inherent risk (likelihood × impact)
        risk_matrix = {
            (RiskLevel.LOW, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.LOW, RiskLevel.MEDIUM): RiskLevel.LOW,
            (RiskLevel.LOW, RiskLevel.HIGH): RiskLevel.MEDIUM,
            (RiskLevel.LOW, RiskLevel.CRITICAL): RiskLevel.MEDIUM,
            (RiskLevel.MEDIUM, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.MEDIUM, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.MEDIUM, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.MEDIUM, RiskLevel.CRITICAL): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.LOW): RiskLevel.MEDIUM,
            (RiskLevel.HIGH, RiskLevel.MEDIUM): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.LOW): RiskLevel.MEDIUM,
            (RiskLevel.CRITICAL, RiskLevel.MEDIUM): RiskLevel.HIGH,
            (RiskLevel.CRITICAL, RiskLevel.HIGH): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
        }

        inherent_risk = risk_matrix.get((likelihood, impact), RiskLevel.MEDIUM)

        # For now, assume residual risk same as inherent (would be calculated based on controls)
        residual_risk = inherent_risk

        risk_assessment = RiskAssessment(
            id=risk_id,
            title=title,
            description=description,
            risk_category=risk_category,
            likelihood=likelihood,
            impact=impact,
            inherent_risk=inherent_risk,
            residual_risk=residual_risk,
            risk_owner=assessor
        )

        self.risk_assessments[risk_id] = risk_assessment

        logger.info(f"Risk assessment completed: {title} - {inherent_risk.value} risk")
        return risk_id

    def generate_compliance_report(self,
                                 standard: ComplianceStandard,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None,
                                 generator: Optional[str] = None) -> ComplianceReport:
        """
        Generate compliance status report.

        Args:
            standard: Compliance standard to report on
            start_date: Report period start
            end_date: Report period end
            generator: Person generating report

        Returns:
            ComplianceReport
        """
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=90)  # 90-day report by default

        report_id = f"RPT-{standard.value}-{int(end_date.timestamp())}"

        # Get controls for this standard
        standard_controls = [c for c in self.controls.values() if c.standard == standard]

        # Calculate controls summary
        controls_summary = {
            "total": len(standard_controls),
            "implemented": len([c for c in standard_controls if c.status == ControlStatus.IMPLEMENTED]),
            "verified": len([c for c in standard_controls if c.status == ControlStatus.VERIFIED]),
            "partially_implemented": len([c for c in standard_controls if c.status == ControlStatus.PARTIALLY_IMPLEMENTED]),
            "not_implemented": len([c for c in standard_controls if c.status == ControlStatus.NOT_IMPLEMENTED]),
            "non_compliant": len([c for c in standard_controls if c.status == ControlStatus.NON_COMPLIANT])
        }

        # Calculate overall status
        compliance_percentage = (controls_summary["implemented"] + controls_summary["verified"]) / controls_summary["total"]

        if compliance_percentage >= 0.95:
            overall_status = "Fully Compliant"
        elif compliance_percentage >= 0.80:
            overall_status = "Substantially Compliant"
        elif compliance_percentage >= 0.60:
            overall_status = "Partially Compliant"
        else:
            overall_status = "Non-Compliant"

        # Gather findings and recommendations
        findings = []
        recommendations = []

        for control in standard_controls:
            if control.status in [ControlStatus.NON_COMPLIANT, ControlStatus.PARTIALLY_IMPLEMENTED]:
                findings.append(f"Control {control.id} ({control.name}) requires attention")

            if control.status == ControlStatus.NOT_IMPLEMENTED:
                recommendations.append(f"Implement control {control.id}: {control.name}")

        # Risk summary
        all_risks = list(self.risk_assessments.values())
        risk_summary = {
            "total": len(all_risks),
            "low": len([r for r in all_risks if r.residual_risk == RiskLevel.LOW]),
            "medium": len([r for r in all_risks if r.residual_risk == RiskLevel.MEDIUM]),
            "high": len([r for r in all_risks if r.residual_risk == RiskLevel.HIGH]),
            "critical": len([r for r in all_risks if r.residual_risk == RiskLevel.CRITICAL])
        }

        # Evidence count
        standard_evidence = [e for e in self.evidence.values()
                           if e.control_id in [c.id for c in standard_controls]]

        report = ComplianceReport(
            id=report_id,
            standard=standard,
            reporting_period=(start_date, end_date),
            overall_status=overall_status,
            controls_summary=controls_summary,
            findings=findings,
            recommendations=recommendations,
            risk_summary=risk_summary,
            evidence_count=len(standard_evidence),
            generated_by=generator
        )

        logger.info(f"Compliance report generated: {report_id} - {overall_status}")
        return report

    def get_controls_by_standard(self, standard: ComplianceStandard) -> List[ComplianceControl]:
        """Get all controls for a specific standard."""
        return [c for c in self.controls.values() if c.standard == standard]

    def get_overdue_controls(self) -> List[ComplianceControl]:
        """Get controls that are overdue for testing."""
        now = datetime.now(timezone.utc)
        return [c for c in self.controls.values()
                if c.next_test_due and c.next_test_due < now]

    def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Get data for compliance dashboard."""
        datetime.now(timezone.utc)

        # Overall statistics
        total_controls = len(self.controls)
        implemented_controls = len([c for c in self.controls.values()
                                  if c.status in [ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED]])

        # By standard
        by_standard = {}
        for standard in ComplianceStandard:
            standard_controls = self.get_controls_by_standard(standard)
            if standard_controls:
                by_standard[standard.value] = {
                    "total": len(standard_controls),
                    "implemented": len([c for c in standard_controls
                                     if c.status in [ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED]]),
                    "compliance_percentage": len([c for c in standard_controls
                                               if c.status in [ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED]]) / len(standard_controls)
                }

        # Overdue controls
        overdue_controls = self.get_overdue_controls()

        # Recent assessments
        recent_assessments = sorted(self.assessments.values(),
                                  key=lambda a: a.assessed_at, reverse=True)[:10]

        return {
            "overall_compliance": implemented_controls / total_controls if total_controls > 0 else 0,
            "total_controls": total_controls,
            "implemented_controls": implemented_controls,
            "by_standard": by_standard,
            "overdue_controls": len(overdue_controls),
            "overdue_control_list": [{"id": c.id, "name": c.name, "due_date": c.next_test_due}
                                   for c in overdue_controls[:10]],
            "recent_assessments": [{"id": a.id, "control_id": a.control_id,
                                  "result": a.result.value, "date": a.assessed_at}
                                 for a in recent_assessments],
            "total_evidence": len(self.evidence),
            "total_risks": len(self.risk_assessments),
            "high_risks": len([r for r in self.risk_assessments.values()
                             if r.residual_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]]),
            "assessment_count": self.assessment_count,
            "automation_count": self.automation_count
        }

# Factory function
def create_compliance_framework(config: Optional[Dict[str, Any]] = None) -> ComplianceFramework:
    """Create compliance framework with configuration."""
    config = config or {}

    return ComplianceFramework(
        evidence_path=config.get("evidence_path", "./compliance_evidence"),
        guardian_integration=config.get("guardian_integration", True)
    )

# Example automation handlers
def example_access_control_handler(control: ComplianceControl) -> Dict[str, Any]:
    """Example automation handler for access control testing."""
    # This would integrate with actual access control systems
    # For demonstration, return mock results

    findings = []

    # Mock checks
    has_rbac = True  # Would check actual RBAC implementation
    has_mfa = True   # Would check MFA configuration
    has_reviews = False  # Would check access review processes

    if not has_rbac:
        findings.append("Role-based access control not implemented")

    if not has_mfa:
        findings.append("Multi-factor authentication not enforced")

    if not has_reviews:
        findings.append("Regular access reviews not conducted")

    status = "implemented" if len(findings) == 0 else "partially_implemented"
    recommendations = ["Implement regular access reviews"] if not has_reviews else []

    return {
        "status": status,
        "findings": findings,
        "recommendations": recommendations,
        "confidence": 0.9,
        "metadata": {
            "rbac_enabled": has_rbac,
            "mfa_enabled": has_mfa,
            "access_reviews": has_reviews
        }
    }

if __name__ == "__main__":
    # Example usage and testing
    framework = create_compliance_framework()

    # Register example automation handler
    framework.register_automation_handler("CC6.1", example_access_control_handler)

    print("Compliance Framework Test")
    print("=" * 40)

    # Test control assessment
    print("\n1. Testing Control Assessment:")
    result = framework.assess_control("CC6.1", "automated", "test_assessor")
    print(f"Assessment result: {result.result.value}")
    print(f"Findings: {result.findings}")

    # Test evidence collection
    print("\n2. Testing Evidence Collection:")
    evidence_id = framework.collect_evidence(
        control_id="CC6.1",
        evidence_type=EvidenceType.CONFIGURATION,
        title="Access Control Configuration",
        description="Current access control system configuration",
        content="RBAC enabled: True\nMFA required: True",
        collector="test_user"
    )
    print(f"Evidence collected: {evidence_id}")

    # Test risk assessment
    print("\n3. Testing Risk Assessment:")
    risk_id = framework.run_risk_assessment(
        title="Unauthorized Access Risk",
        description="Risk of unauthorized access to sensitive systems",
        risk_category="Access Control",
        likelihood=RiskLevel.MEDIUM,
        impact=RiskLevel.HIGH,
        assessor="risk_assessor"
    )
    print(f"Risk assessment: {risk_id}")

    # Test compliance reporting
    print("\n4. Testing Compliance Reporting:")
    report = framework.generate_compliance_report(
        standard=ComplianceStandard.SOC2_TYPE2,
        generator="test_generator"
    )
    print(f"Report generated: {report.id}")
    print(f"Overall status: {report.overall_status}")
    print(f"Controls summary: {report.controls_summary}")

    # Test dashboard data
    print("\n5. Testing Dashboard Data:")
    dashboard = framework.get_compliance_dashboard_data()
    print(f"Overall compliance: {dashboard['overall_compliance']:.2%}")
    print(f"Total controls: {dashboard['total_controls']}")
    print(f"Overdue controls: {dashboard['overdue_controls']}")

    print("\nCompliance Framework test completed")
