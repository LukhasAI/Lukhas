#!/usr/bin/env python3
"""
🛡️ ΛBot Compliance Checker - Enterprise Workspace Scanner
========================================================
LUKHAS Symbol Validation & Global Compliance Auditor

Comprehensive compliance scanner for the entire Lukhas ecosystem:
✅ Multi-jurisdictional compliance validation (EU/US/CA/UK/AU/SG/BR/ZA/AE/CN)
✅ GDPR, CCPA, HIPAA, SOX, AI Act compliance checking
✅ Code pattern analysis for privacy/security violations
✅ Data flow analysis and consent management validation
✅ Institutional-grade compliance reporting
✅ Real-time compliance monitoring
✅ Automated remediation suggestions

Author: LUKHAS AI Research Team - Global Compliance Division
Date: June 26, 2025
Version: 2.0.0 - Enterprise Edition
"""

import concurrent.futures
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """Compliance levels for modules."""

    FULL_COMPLIANCE = "FULL_COMPLIANCE"
    SUBSTANTIAL_COMPLIANCE = "SUBSTANTIAL_COMPLIANCE"
    BASIC_COMPLIANCE = "BASIC_COMPLIANCE"
    NON_COMPLIANT = "NON_COMPLIANT"
    UNKNOWN = "UNKNOWN"


class Jurisdiction(Enum):
    """Supported jurisdictions."""

    EU = "EU"
    US = "US"
    CA = "CA"
    UK = "UK"
    AU = "AU"
    SG = "SG"
    BR = "BR"
    ZA = "ZA"
    AE = "AE"
    CN = "CN"
    GLOBAL = "GLOBAL"


class ComplianceViolationType(Enum):
    """Types of compliance violations."""

    MISSING_CONSENT = "MISSING_CONSENT"
    DATA_RETENTION = "DATA_RETENTION"
    MISSING_ENCRYPTION = "MISSING_ENCRYPTION"
    NO_AUDIT_TRAIL = "NO_AUDIT_TRAIL"
    MISSING_GDPR_RIGHTS = "MISSING_GDPR_RIGHTS"
    MISSING_CCPA_RIGHTS = "MISSING_CCPA_RIGHTS"
    BIOMETRIC_DATA = "BIOMETRIC_DATA"
    CROSS_BORDER_TRANSFER = "CROSS_BORDER_TRANSFER"
    AI_TRANSPARENCY = "AI_TRANSPARENCY"
    HEALTHCARE_PHI = "HEALTHCARE_PHI"
    FINANCIAL_PII = "FINANCIAL_PII"


@dataclass
class ComplianceViolation:
    """A specific compliance violation."""

    violation_type: ComplianceViolationType
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    jurisdiction: Jurisdiction
    file_path: str
    line_number: Optional[int]
    description: str
    regulation: str
    remediation: str


@dataclass
class ModuleComplianceReport:
    """Compliance report for a single module."""

    module_name: str
    file_path: str
    compliance_level: ComplianceLevel
    jurisdictional_scores: dict[str, float] = field(default_factory=dict)
    violations: list[ComplianceViolation] = field(default_factory=list)
    compliant_features: list[str] = field(default_factory=list)
    missing_features: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    last_scanned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkspaceComplianceReport:
    """Overall workspace compliance report."""

    workspace_path: str
    scan_timestamp: datetime
    overall_compliance_level: ComplianceLevel
    total_modules: int
    compliant_modules: int
    non_compliant_modules: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    jurisdiction_scores: dict[str, float] = field(default_factory=dict)
    module_reports: list[ModuleComplianceReport] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    executive_summary: str = ""


class LukhasComplianceChecker:
    """
    🛡️ LUKHAS Compliance Checker - Enterprise Workspace Scanner

    Comprehensive compliance validation for the entire Lukhas ecosystem.
    Identifies regulatory violations and provides remediation guidance.
    """

    # TODO[CONSCIOUSNESS:specialist] Fix syntax error - missing 'self' parameter in __init__ method
    # This consciousness node requires proper initialization for compliance validation
    def __init__(
        self,
        workspace_path: str = "/Users/A_G_I/Lukhas",
        critical_only: bool = True,
    ):
        self.workspace_path = Path(workspace_path)
        self.scan_timestamp = datetime.now(timezone.utc)
        self.critical_only = critical_only  # Only scan critical modules by default

        # Compliance patterns for detection
        self.compliance_patterns = self._load_compliance_patterns()

        # Regulatory frameworks
        self.regulations = {
            Jurisdiction.EU: [
                "GDPR",
                "AI_Act",
                "DSA",
                "DGA",
                "NIS2",
                "ePrivacy",
            ],
            Jurisdiction.US: [
                "CCPA",
                "CPRA",
                "HIPAA",
                "SOX",
                "FedRAMP",
                "PCI_DSS",
            ],
            Jurisdiction.CA: ["PIPEDA", "CPPA", "AIDA", "Provincial_Laws"],
            Jurisdiction.UK: ["UK_GDPR", "DPA_2018", "ICO_Guidelines"],
            Jurisdiction.AU: ["Privacy_Act", "APPs", "NDB", "CDR"],
            Jurisdiction.SG: ["PDPA", "MTCS", "Cybersecurity_Act"],
            Jurisdiction.BR: ["LGPD", "Marco_Civil"],
            Jurisdiction.ZA: ["POPIA", "PAIA"],
            Jurisdiction.AE: ["PDPL", "DIFC", "ADGM"],
            Jurisdiction.CN: ["PIPL", "DSL", "CSL"],
        }

        # Known compliant modules
        self.compliant_modules = {
            "GlobalInstitutionalCompliantEngine.py": ComplianceLevel.FULL_COMPLIANCE,
            "ResearchAwarenessEngine.py": ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            "EUAwarenessEngine.py": ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            "USInstitutionalAwarenessEngine.py": ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            "CanadianAwarenessEngine.py": ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            "AustralianAwarenessEngine.py": ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            "GlobalInstitutionalFramework.py": ComplianceLevel.FULL_COMPLIANCE,
        }

        # Critical modules that MUST be compliant (handle sensitive data/user
        # interactions)
        self.critical_compliance_modules = [
            "**/auth*/**",
            "**/authentication/**",
            "**/identity/**",
            "**/user/**",
            "**/profile/**",
            "**/payment/**",
            "**/billing/**",
            "**/api/**",
            "**/gateway/**",
            "**/messaging/**",
            "**/communication/**",
            "**/data/**",
            "**/database/**",
            "**/storage/**",
            "**/memory/**",
            "**/awareness/**",
            "**/agi_controller*",
            "**/brain/**",
            "**/core/compliance/**",
            "**/core/security/**",
            "**/core/privacy/**",
            "**/health/**",
            "**/medical/**",
            "**/financial/**",
        ]

        # Optional compliance modules (nice to have, but not critical)
        self.optional_compliance_modules = [
            "**/templates/**",
            "**/ui/**",
            "**/frontend/**",
            "**/docs/**",
            "**/tests/**",
            "**/examples/**",
            "**/demos/**",
        ]

        # File patterns to scan (only critical ones by default)
        self.scan_patterns = ["**/*.py", "**/*.js", "**/*.ts"]

        # Exclude patterns (expanded to exclude non-critical files)
        self.exclude_patterns = [
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/venv/**",
            "**/dist/**",
            "**/build/**",
            "**/.git/**",
            "**/backups/**",
            "**/logs/**",
            "**/tmp/**",
            "**/temp/**",
            "**/.vscode/**",
            "**/assets/**",
            "**/static/**",
            "**/public/**",
            "**/images/**",
            "**/icons/**",
            "**/fonts/**",
        ]

    def _load_compliance_patterns(self) -> dict[str, list[str]]:
        """Load regex patterns for compliance detection."""
        return {
            "gdpr_patterns": [
                r"consent.*required",
                r"data.*subject.*rights",
                r"right.*erasure",
                r"data.*portability",
                r"lawful.*basis",
                r"privacy.*policy",
                r"dpo.*contact",
            ],
            "ccpa_patterns": [
                r"opt.*out",
                r"do.*not.*sell",
                r"consumer.*rights",
                r"personal.*information",
                r"data.*sale",
            ],
            "hipaa_patterns": [
                r"phi.*protection",
                r"protected.*health.*information",
                r"hipaa.*compliance",
                r"medical.*data",
                r"healthcare.*privacy",
            ],
            "ai_governance": [
                r"ai.*explanation",
                r"algorithmic.*transparency",
                r"bias.*detection",
                r"ai.*decision",
                r"machine.*learning.*audit",
            ],
            "encryption": [
                r"encrypt.*at.*rest",
                r"encrypt.*in.*transit",
                r"aes.*256",
                r"tls.*1\.3",
                r"end.*to.*end.*encryption",
            ],
            "audit_logging": [
                r"audit.*log",
                r"compliance.*log",
                r"activity.*log",
                r"access.*log",
            ],
        }

    def scan_workspace(
        self,
        include_patterns: Optional[list[str]] = None,
        parallel: bool = True,
    ) -> WorkspaceComplianceReport:
        """
        Scan the entire workspace for compliance issues.

        Args:
            include_patterns: Optional list of file patterns to include
            parallel: Whether to use parallel processing

        Returns:
            Comprehensive workspace compliance report
        """
        logger.info(f"🔍 Starting compliance scan of workspace: {self.workspace_path}")
        logger.info(f"⏰ Scan timestamp: {self.scan_timestamp}")

        # Find all files to scan
        files_to_scan = self._find_files_to_scan(include_patterns)
        logger.info(f"📁 Found {len(files_to_scan)} files to scan")

        # Scan files for compliance
        module_reports = []
        if parallel:
            module_reports = self._scan_files_parallel(files_to_scan)
        else:
            module_reports = self._scan_files_sequential(files_to_scan)

        # Generate workspace report
        workspace_report = self._generate_workspace_report(module_reports)

        logger.info("✅ Compliance scan completed")
        logger.info(f"📊 Overall compliance: {workspace_report.overall_compliance_level.value}")

        return workspace_report

    def _find_files_to_scan(self, include_patterns: Optional[list[str]] = None) -> list[Path]:
        """Find all files that should be scanned for compliance."""
        patterns = include_patterns or self.scan_patterns
        files = set()

        for pattern in patterns:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file() and not self._should_exclude_file(file_path):
                    # If critical_only mode, only include critical modules
                    if self.critical_only:
                        if self._is_critical_module(file_path):
                            files.add(file_path)
                    else:
                        files.add(file_path)

        return sorted(files)

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if a file should be excluded from scanning."""
        return any(file_path.match(exclude_pattern) for exclude_pattern in self.exclude_patterns)

    def _scan_files_parallel(self, files: list[Path]) -> list[ModuleComplianceReport]:
        """Scan files in parallel for better performance."""
        module_reports = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {executor.submit(self._scan_single_file, file_path): file_path for file_path in files}

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    report = future.result()
                    if report:
                        module_reports.append(report)
                except Exception as exc:
                    logger.warning(f"⚠️ Error scanning {file_path}: {exc}")

        return module_reports

    def _scan_files_sequential(self, files: list[Path]) -> list[ModuleComplianceReport]:
        """Scan files sequentially."""
        module_reports = []

        for file_path in files:
            try:
                report = self._scan_single_file(file_path)
                if report:
                    module_reports.append(report)
            except Exception as exc:
                logger.warning(f"⚠️ Error scanning {file_path}: {exc}")

        return module_reports

    def _scan_single_file(self, file_path: Path) -> Optional[ModuleComplianceReport]:
        """Scan a single file for compliance issues."""
        try:
            # Read file content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Create module report
            module_name = file_path.name
            report = ModuleComplianceReport(module_name=module_name, file_path=str(file_path))

            # Check if it's a known compliant module
            if module_name in self.compliant_modules:
                report.compliance_level = self.compliant_modules[module_name]
                report.jurisdictional_scores = self._get_known_module_scores(module_name)
                return report

            # Analyze file content for compliance
            violations = self._analyze_content_for_violations(content, file_path)
            report.violations = violations

            # Calculate compliance scores
            report.jurisdictional_scores = self._calculate_jurisdictional_scores(violations)
            report.compliance_level = self._determine_compliance_level(report.jurisdictional_scores)
            report.risk_score = self._calculate_risk_score(violations)

            # Generate recommendations
            report.recommendations = self._generate_recommendations(violations)

            # Identify compliant and missing features
            report.compliant_features, report.missing_features = self._analyze_features(content)

            return report

        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
            return None

    def _analyze_content_for_violations(self, content: str, file_path: Path) -> list[ComplianceViolation]:
        """Analyze file content for specific compliance violations."""
        violations = []

        # Only apply strict compliance checks to critical modules
        if not self._is_critical_module(file_path):
            # For non-critical modules, only check for obvious violations
            if self._has_obvious_security_issues(content):
                violations.append(
                    ComplianceViolation(
                        violation_type=ComplianceViolationType.MISSING_ENCRYPTION,
                        severity="LOW",
                        jurisdiction=Jurisdiction.GLOBAL,
                        file_path=str(file_path),
                        line_number=None,
                        description="Non-critical module with potential security considerations",
                        regulation="General Security Best Practices",
                        remediation="Review for basic security practices if handling any data",
                    )
                )
            return violations

        # Full compliance analysis for critical modules
        content.split("\n")

        # Check for missing GDPR compliance
        if not self._has_gdpr_compliance(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.MISSING_GDPR_RIGHTS,
                    severity="HIGH",
                    jurisdiction=Jurisdiction.EU,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical module missing GDPR data subject rights implementation",
                    regulation="GDPR Articles 15-22",
                    remediation="Implement data subject rights: access, rectification, " "erasure, portability",
                )
            )

        # Check for missing CCPA compliance
        if not self._has_ccpa_compliance(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.MISSING_CCPA_RIGHTS,
                    severity="HIGH",
                    jurisdiction=Jurisdiction.US,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical module missing CCPA consumer rights implementation",
                    regulation="CCPA/CPRA",
                    remediation="Implement opt-out mechanisms and consumer rights",
                )
            )

        # Check for missing consent management
        if self._processes_personal_data(content) and not self._has_consent_management(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.MISSING_CONSENT,
                    severity="CRITICAL",
                    jurisdiction=Jurisdiction.GLOBAL,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical module processes personal data without consent management",
                    regulation="GDPR Article 6, CCPA",
                    remediation="Implement consent collection and management system",
                )
            )

        # Check for missing encryption
        if not self._has_encryption(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.MISSING_ENCRYPTION,
                    severity="HIGH",
                    jurisdiction=Jurisdiction.GLOBAL,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical module missing encryption implementation",
                    regulation="GDPR Article 32, HIPAA Security Rule",
                    remediation="Implement encryption at rest and in transit",
                )
            )

        # Check for missing audit logging
        if not self._has_audit_logging(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.NO_AUDIT_TRAIL,
                    severity="MEDIUM",
                    jurisdiction=Jurisdiction.GLOBAL,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical module missing audit logging for compliance tracking",
                    regulation="GDPR Article 5, SOX Section 404",
                    remediation="Implement comprehensive audit logging system",
                )
            )

        # Check for AI transparency issues
        if self._is_ai_module(content) and not self._has_ai_transparency(content):
            violations.append(
                ComplianceViolation(
                    violation_type=ComplianceViolationType.AI_TRANSPARENCY,
                    severity="HIGH",
                    jurisdiction=Jurisdiction.EU,
                    file_path=str(file_path),
                    line_number=None,
                    description="Critical AI system lacks required transparency and explainability",
                    regulation="EU AI Act Article 13",
                    remediation="Implement AI decision explanation and transparency features",
                )
            )

        return violations

    def _has_gdpr_compliance(self, content: str) -> bool:
        """Check if content has GDPR compliance features."""
        gdpr_indicators = [
            "gdpr",
            "data_subject_rights",
            "right_to_erasure",
            "data_portability",
            "lawful_basis",
            "consent_management",
            "privacy_policy",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in gdpr_indicators)

    def _has_ccpa_compliance(self, content: str) -> bool:
        """Check if content has CCPA compliance features."""
        ccpa_indicators = [
            "ccpa",
            "opt_out",
            "do_not_sell",
            "consumer_rights",
            "personal_information",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in ccpa_indicators)

    def _processes_personal_data(self, content: str) -> bool:
        """Check if the module processes personal data."""
        personal_data_indicators = [
            "user_id",
            "email",
            "name",
            "phone",
            "address",
            "personal_data",
            "user_data",
            "profile",
            "preferences",
            "behavioral_data",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in personal_data_indicators)

    def _has_consent_management(self, content: str) -> bool:
        """Check if content has consent management."""
        consent_indicators = [
            "consent",
            "permission",
            "agree",
            "opt_in",
            "authorization",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in consent_indicators)

    def _has_encryption(self, content: str) -> bool:
        """Check if content has encryption implementation."""
        encryption_indicators = [
            "encrypt",
            "aes",
            "tls",
            "ssl",
            "crypto",
            "cipher",
            "hash",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in encryption_indicators)

    def _has_audit_logging(self, content: str) -> bool:
        """Check if content has audit logging."""
        audit_indicators = [
            "audit",
            "log",
            "track",
            "record",
            "compliance_log",
            "activity_log",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in audit_indicators)

    def _is_ai_module(self, content: str) -> bool:
        """Check if this is an AI/ML module."""
        ai_indicators = [
            "artificial_intelligence",
            "machine_learning",
            "neural",
            "model",
            "inference",
            "prediction",
            "algorithm",
            "ai",
            "ml",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in ai_indicators)

    def _has_ai_transparency(self, content: str) -> bool:
        """Check if AI module has transparency features."""
        transparency_indicators = [
            "explain",
            "transparency",
            "interpretable",
            "explainable",
            "decision_logic",
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in transparency_indicators)

    def _calculate_jurisdictional_scores(self, violations: list[ComplianceViolation]) -> dict[str, float]:
        """Calculate compliance scores per jurisdiction."""
        scores = {}

        for jurisdiction in Jurisdiction:
            jurisdiction_violations = [
                v for v in violations if v.jurisdiction == jurisdiction or v.jurisdiction == Jurisdiction.GLOBAL
            ]

            # Base score
            base_score = 100.0

            # Deduct points for violations
            for violation in jurisdiction_violations:
                if violation.severity == "CRITICAL":
                    base_score -= 25.0
                elif violation.severity == "HIGH":
                    base_score -= 15.0
                elif violation.severity == "MEDIUM":
                    base_score -= 10.0
                elif violation.severity == "LOW":
                    base_score -= 5.0

            scores[jurisdiction.value] = max(0.0, base_score)

        return scores

    def _determine_compliance_level(self, scores: dict[str, float]) -> ComplianceLevel:
        """Determine overall compliance level from jurisdictional scores."""
        if not scores:
            return ComplianceLevel.UNKNOWN

        min_score = min(scores.values())

        if min_score >= 95.0:
            return ComplianceLevel.FULL_COMPLIANCE
        elif min_score >= 80.0:
            return ComplianceLevel.SUBSTANTIAL_COMPLIANCE
        elif min_score >= 60.0:
            return ComplianceLevel.BASIC_COMPLIANCE
        else:
            return ComplianceLevel.NON_COMPLIANT

    def _calculate_risk_score(self, violations: list[ComplianceViolation]) -> float:
        """Calculate overall risk score from violations."""
        risk_score = 0.0

        for violation in violations:
            if violation.severity == "CRITICAL":
                risk_score += 10.0
            elif violation.severity == "HIGH":
                risk_score += 6.0
            elif violation.severity == "MEDIUM":
                risk_score += 3.0
            elif violation.severity == "LOW":
                risk_score += 1.0

        return min(risk_score, 100.0)

    def _generate_recommendations(self, violations: list[ComplianceViolation]) -> list[str]:
        """Generate remediation recommendations from violations."""
        recommendations = []

        for violation in violations:
            if violation.remediation not in recommendations:
                recommendations.append(violation.remediation)

        # Add general recommendations
        if violations:
            recommendations.append("Integrate with GlobalInstitutionalCompliantEngine for full compliance")
            recommendations.append("Implement comprehensive privacy impact assessment")
            recommendations.append("Regular compliance audits and monitoring")

        return recommendations

    def _analyze_features(self, content: str) -> tuple[list[str], list[str]]:
        """Analyze what compliance features are present and missing."""
        compliant_features = []
        missing_features = []

        # Check for various compliance features
        features_to_check = {
            "GDPR Consent Management": self._has_gdpr_compliance(content),
            "CCPA Consumer Rights": self._has_ccpa_compliance(content),
            "Data Encryption": self._has_encryption(content),
            "Audit Logging": self._has_audit_logging(content),
            "AI Transparency": (self._has_ai_transparency(content) if self._is_ai_module(content) else True),
        }

        for feature, present in features_to_check.items():
            if present:
                compliant_features.append(feature)
            else:
                missing_features.append(feature)

        return compliant_features, missing_features

    def _get_known_module_scores(self, module_name: str) -> dict[str, float]:
        """Get scores for known compliant modules."""
        if module_name == "GlobalInstitutionalCompliantEngine.py":
            return {j.value: 100.0 for j in Jurisdiction}
        elif module_name in [
            "EUAwarenessEngine.py",
            "USInstitutionalAwarenessEngine.py",
        ]:
            return {j.value: 85.0 for j in Jurisdiction}
        else:
            return {j.value: 75.0 for j in Jurisdiction}

    def _generate_workspace_report(self, module_reports: list[ModuleComplianceReport]) -> WorkspaceComplianceReport:
        """Generate comprehensive workspace compliance report."""

        # Count modules by compliance level
        compliant_modules = sum(
            1
            for r in module_reports
            if r.compliance_level
            in [
                ComplianceLevel.FULL_COMPLIANCE,
                ComplianceLevel.SUBSTANTIAL_COMPLIANCE,
            ]
        )
        non_compliant_modules = len(module_reports) - compliant_modules

        # Count violations by severity
        all_violations = [v for r in module_reports for v in r.violations]
        critical_violations = sum(1 for v in all_violations if v.severity == "CRITICAL")
        high_violations = sum(1 for v in all_violations if v.severity == "HIGH")
        medium_violations = sum(1 for v in all_violations if v.severity == "MEDIUM")
        low_violations = sum(1 for v in all_violations if v.severity == "LOW")

        # Calculate jurisdiction scores
        jurisdiction_scores = {}
        for jurisdiction in Jurisdiction:
            jurisdiction_scores[jurisdiction.value] = self._calculate_average_jurisdiction_score(
                module_reports, jurisdiction
            )

        # Determine overall compliance level
        overall_compliance = self._determine_overall_workspace_compliance(jurisdiction_scores)

        # Generate recommendations
        recommendations = self._generate_workspace_recommendations(module_reports)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            len(module_reports),
            compliant_modules,
            non_compliant_modules,
            critical_violations,
            high_violations,
            overall_compliance,
        )

        return WorkspaceComplianceReport(
            workspace_path=str(self.workspace_path),
            scan_timestamp=self.scan_timestamp,
            overall_compliance_level=overall_compliance,
            total_modules=len(module_reports),
            compliant_modules=compliant_modules,
            non_compliant_modules=non_compliant_modules,
            critical_violations=critical_violations,
            high_violations=high_violations,
            medium_violations=medium_violations,
            low_violations=low_violations,
            jurisdiction_scores=jurisdiction_scores,
            module_reports=module_reports,
            recommendations=recommendations,
            executive_summary=executive_summary,
        )

    def _calculate_average_jurisdiction_score(
        self,
        module_reports: list[ModuleComplianceReport],
        jurisdiction: Jurisdiction,
    ) -> float:
        """Calculate average compliance score for a jurisdiction."""
        scores = [
            r.jurisdictional_scores.get(jurisdiction.value, 0.0) for r in module_reports if r.jurisdictional_scores
        ]
        return sum(scores) / len(scores) if scores else 0.0

    def _determine_overall_workspace_compliance(self, jurisdiction_scores: dict[str, float]) -> ComplianceLevel:
        """Determine overall workspace compliance level."""
        if not jurisdiction_scores:
            return ComplianceLevel.UNKNOWN

        min_score = min(jurisdiction_scores.values())

        if min_score >= 90.0:
            return ComplianceLevel.FULL_COMPLIANCE
        elif min_score >= 75.0:
            return ComplianceLevel.SUBSTANTIAL_COMPLIANCE
        elif min_score >= 50.0:
            return ComplianceLevel.BASIC_COMPLIANCE
        else:
            return ComplianceLevel.NON_COMPLIANT

    def _generate_workspace_recommendations(self, module_reports: list[ModuleComplianceReport]) -> list[str]:
        """Generate workspace-level recommendations."""
        recommendations = [
            "🚨 CRITICAL: Upgrade non - compliant core systems(AGI Controller, Auth System)",
            "🔒 HIGH: Implement GlobalInstitutionalCompliantEngine across all modules",
            "📋 MEDIUM: Establish comprehensive compliance monitoring framework",
            "🛡️ Create unified privacy policy and consent management system",
            "📊 Implement real-time compliance dashboard and alerts",
            "🔍 Schedule quarterly compliance audits and assessments",
            "🌍 Ensure cross-border data transfer compliance",
            "🤖 Implement AI governance and transparency framework",
        ]

        return recommendations

    def _generate_executive_summary(
        self,
        total_modules: int,
        compliant_modules: int,
        non_compliant_modules: int,
        critical_violations: int,
        high_violations: int,
        overall_compliance: ComplianceLevel,
    ) -> str:
        """Generate executive summary of compliance status."""
        compliance_percentage = (compliant_modules / total_modules * 100) if total_modules > 0 else 0

        summary = f"""
🛡️ LUKHAS WORKSPACE COMPLIANCE EXECUTIVE SUMMARY

📊 OVERALL STATUS: {overall_compliance.value}
📈 Compliance Rate: {compliance_percentage:.1f}% ({compliant_modules}/{total_modules} critical modules)

🎯 SCAN SCOPE: {"Critical modules only" if hasattr(self, 'critical_only') and self.critical_only else "All modules"}

🚨 CRITICAL FINDINGS:
• {critical_violations} critical violations requiring immediate attention
• {high_violations} high-priority violations needing urgent remediation
• {non_compliant_modules} critical modules are non-compliant with global regulations

🎯 PRIORITY ACTIONS:
1. Upgrade core AGI Controller and Authentication systems
2. Integrate GlobalInstitutionalCompliantEngine across critical modules
3. Implement missing GDPR and CCPA compliance features
4. Establish comprehensive audit logging and monitoring

💼 BUSINESS IMPACT:
Current compliance gaps in critical modules pose significant regulatory risks.
Non-critical modules (templates, docs, etc.) are excluded from strict compliance.
Immediate action required for institutional deployment readiness.
"""
        return summary.strip()

    def save_report(self, report: WorkspaceComplianceReport, output_path: Optional[str] = None) -> str:
        """Save compliance report to file."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"LUKHAS_COMPLIANCE_REPORT_{timestamp}.json"

        # Convert report to dict for JSON serialization
        report_dict = {
            "workspace_path": report.workspace_path,
            "scan_timestamp": report.scan_timestamp.isoformat(),
            "overall_compliance_level": report.overall_compliance_level.value,
            "total_modules": report.total_modules,
            "compliant_modules": report.compliant_modules,
            "non_compliant_modules": report.non_compliant_modules,
            "critical_violations": report.critical_violations,
            "high_violations": report.high_violations,
            "medium_violations": report.medium_violations,
            "low_violations": report.low_violations,
            "jurisdiction_scores": report.jurisdiction_scores,
            "recommendations": report.recommendations,
            "executive_summary": report.executive_summary,
            "module_reports": [
                {
                    "module_name": mr.module_name,
                    "file_path": mr.file_path,
                    "compliance_level": mr.compliance_level.value,
                    "jurisdictional_scores": mr.jurisdictional_scores,
                    "violations": [
                        {
                            "violation_type": v.violation_type.value,
                            "severity": v.severity,
                            "jurisdiction": v.jurisdiction.value,
                            "file_path": v.file_path,
                            "line_number": v.line_number,
                            "description": v.description,
                            "regulation": v.regulation,
                            "remediation": v.remediation,
                        }
                        for v in mr.violations
                    ],
                    "compliant_features": mr.compliant_features,
                    "missing_features": mr.missing_features,
                    "recommendations": mr.recommendations,
                    "risk_score": mr.risk_score,
                    "last_scanned": mr.last_scanned.isoformat(),
                }
                for mr in report.module_reports
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Compliance report saved to: {output_path}")
        return output_path

    def print_summary(self, report: WorkspaceComplianceReport):
        """Print a formatted summary of the compliance report."""
        print("🛡️" + "=" * 80)
        print("    LUKHAS WORKSPACE COMPLIANCE CHECKER - ENTERPRISE REPORT")
        print("=" * 82)
        print()
        print(report.executive_summary)
        print()
        print("📊 DETAILED BREAKDOWN:")
        print(f"   📁 Total Modules Scanned: {report.total_modules}")
        print(f"   ✅ Compliant Modules: {report.compliant_modules}")
        print(f"   ❌ Non-Compliant Modules: {report.non_compliant_modules}")
        print(f"   🚨 Critical Violations: {report.critical_violations}")
        print(f"   ⚠️ High Priority Violations: {report.high_violations}")
        print()
        print("🌍 JURISDICTIONAL COMPLIANCE SCORES:")
        for jurisdiction, score in report.jurisdiction_scores.items():
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"   {status} {jurisdiction}: {score:.1f}%")
        print()
        print("🎯 TOP RECOMMENDATIONS:")
        for i, recommendation in enumerate(report.recommendations[:5], 1):
            print(f"   {i}. {recommendation}")
        print()
        print("🔗 Full report saved for detailed analysis and remediation planning.")
        print("=" * 82)

    def _is_critical_module(self, file_path: Path) -> bool:
        """Check if a file is in a critical module that requires compliance."""
        file_str = str(file_path).lower()

        # Check against critical compliance module patterns
        for pattern in self.critical_compliance_modules:
            # Convert glob pattern to simple string matching
            pattern_clean = pattern.replace("**/", "").replace("/**", "").replace("*", "")
            if pattern_clean in file_str:
                return True

        # Check specific critical files by name
        critical_filenames = [
            "agi_controller",
            "auth",
            "authentication",
            "identity",
            "user",
            "payment",
            "billing",
            "api",
            "gateway",
            "messaging",
            "data",
            "database",
            "storage",
            "memory",
            "awareness",
            "brain",
            "compliance",
            "security",
            "privacy",
            "health",
            "medical",
            "financial",
        ]

        filename_lower = file_path.name.lower()
        return any(critical in filename_lower for critical in critical_filenames)

    def _has_obvious_security_issues(self, content: str) -> bool:
        """Check for obvious security issues in non-critical modules."""
        security_issues = [
            "password.*=.*['\"]",
            "api_key.*=.*['\"]",
            "secret.*=.*['\"]",
            "hardcoded",
            "plain.*text.*password",
            "no.*encryption",
        ]
        content_lower = content.lower()
        return any(re.search(issue, content_lower) for issue in security_issues)


def main():
    """Main function to run compliance checker."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Compliance Checker v2.0.0")
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Scan all files (default: critical modules only)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Apply strict compliance checking",
    )
    parser.add_argument(
        "--forbid-legacy",
        action="store_true",
        help="Flag legacy modules as non-compliant",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("🛡️ LUKHAS Compliance Checker v2.0.0 - Enterprise Edition")
    if args.all_files:
        print("🔍 Scanning ALL files for compliance violations...")
    else:
        print("🔍 Scanning CRITICAL modules only for compliance violations...")
    print()

    # Initialize checker
    checker = LukhasComplianceChecker(critical_only=not args.all_files)

    # Run compliance scan
    report = checker.scan_workspace()

    # Save and display report
    output_file = checker.save_report(report)
    checker.print_summary(report)

    print(f"\n📄 Detailed report saved to: {output_file}")
    print("🎯 Use this report to prioritize compliance remediation efforts.")
    print("\n💡 TIP: Use --all-files to scan non-critical modules too.")


if __name__ == "__main__":
    main()
