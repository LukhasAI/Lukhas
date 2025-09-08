#!/usr/bin/env python3
import logging
import streamlit as st
import random
logger = logging.getLogger(__name__)
"""
LUKHAS Enterprise Security Automation
Comprehensive automated security scanning, monitoring, and remediation

This module implements enterprise-grade security automation that maintains
the <0.15 constitutional drift threshold while ensuring zero security vulnerabilities.
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Import production security modules
try:
    from lukhas.governance.ethics.constitutional_ai import (
        ConstitutionalFramework,
        SafetyLevel,
    )
    from lukhas.governance.identity.auth_backend.audit_logger import (
        AuditEventType,
        AuditLogger,
        AuditSeverity,
    )
    from lukhas.governance.security.access_control import (
        AccessControlEngine,
        AccessTier,
    )

    PRODUCTION_MODULES_AVAILABLE = True
except ImportError:
    PRODUCTION_MODULES_AVAILABLE = False

from lukhas.core.common.logger import get_logger

logger = get_logger(__name__)


class SecuritySeverity(Enum):
    """Security vulnerability severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityCategory(Enum):
    """Security vulnerability categories"""

    HARDCODED_SECRETS = "hardcoded_secrets"
    BANNED_IMPORTS = "banned_imports"
    SQL_INJECTION = "sql_injection"
    XSS_VULNERABILITY = "xss_vulnerability"
    PATH_TRAVERSAL = "path_traversal"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CRYPTOGRAPHIC = "cryptographic"
    CONSTITUTIONAL_DRIFT = "constitutional_drift"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"


@dataclass
class SecurityFinding:
    """Security vulnerability finding"""

    finding_id: str
    category: SecurityCategory
    severity: SecuritySeverity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None

    # Remediation information
    remediation: str = ""
    auto_fixable: bool = False
    fix_confidence: float = 0.0

    # Context
    evidence: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)

    # Tracking
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "open"
    assigned_to: Optional[str] = None

    # Constitutional AI integration
    constitutional_impact: Optional[float] = None
    drift_contribution: Optional[float] = None


@dataclass
class SecurityScanResult:
    """Complete security scan result"""

    scan_id: str
    scan_type: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    # Results
    findings: list[SecurityFinding] = field(default_factory=list)
    files_scanned: int = 0
    lines_scanned: int = 0

    # Summary statistics
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Remediation
    auto_fixed_count: int = 0
    fix_success_rate: float = 0.0

    # Constitutional compliance
    constitutional_drift_score: float = 0.0
    compliance_status: str = "compliant"


class EnterprisSecurityScanner:
    """Enterprise security scanner with constitutional AI integration"""

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Core configuration
        self.project_root = Path(self.config.get("project_root", "."))
        self.scan_patterns = self.config.get("scan_patterns", ["*.py", "*.js", "*.ts", "*.yaml", "*.yml", "*.json"])
        self.excluded_paths = self.config.get(
            "excluded_paths",
            [
                ".git",
                "__pycache__",
                "node_modules",
                ".venv",
                "venv",
                "dist",
                "build",
                ".pytest_cache",
            ],
        )

        # Security rules
        self.security_rules = self._initialize_security_rules()

        # Banned imports for lane architecture
        self.banned_imports = {
            "lukhas": [
                "candidate.",  # Production code cannot import from candidate/
                "from candidate",
                "import candidate",
            ],
            "candidate": [],  # candidate/ can import anything
        }

        # Constitutional AI integration
        self.constitutional_framework = None
        self.access_control = None
        self.audit_logger = None

        if PRODUCTION_MODULES_AVAILABLE:
            self.constitutional_framework = ConstitutionalFramework()
            self.access_control = AccessControlEngine()
            self.audit_logger = AuditLogger()

        # Scan history
        self.scan_history: list[SecurityScanResult] = []

        # Metrics
        self.scan_metrics = {
            "total_scans": 0,
            "total_findings": 0,
            "auto_fixes_applied": 0,
            "constitutional_violations": 0,
            "avg_scan_time_seconds": 0.0,
        }

        logger.info("🛡️ Enterprise Security Scanner initialized")

    def _initialize_security_rules(self) -> dict[str, dict[str, Any]]:
        """Initialize comprehensive security rules"""

        return {
            "hardcoded_secrets": {
                "patterns": [
                    r"password\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[^'\"]{3,}['\"]",
                    r"api_key\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[^'\"]{8,}['\"]",
                    r"secret\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[^'\"]{8,}['\"]",
                    r"token\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[^'\"]{8,}['\"]",
                    r"key\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[A-Za-z0-9+/]{20,}['\"]",
                    r"auth\s*=\s*['\"](?!.*\$\{|.*ENV|.*CONFIG)[^'\"]{8,}['\"]",
                ],
                "severity": SecuritySeverity.CRITICAL,
                "category": SecurityCategory.HARDCODED_SECRETS,
                "auto_fixable": True,
            },
            "sql_injection": {
                "patterns": [
                    r"execute\(.*%.*\)}",
                    r"query\(.*\+.*\)",
                    r"cursor\.execute\([^?]*%",
                    r"sql\s*=.*\+.*",
                    r"SELECT.*\+.*FROM",
                    r"INSERT.*\+.*VALUES",
                ],
                "severity": SecuritySeverity.HIGH,
                "category": SecurityCategory.SQL_INJECTION,
                "auto_fixable": False,
            },
            "xss_vulnerability": {
                "patterns": [
                    r"innerHTML\s*=.*\+",
                    r"document\.write\(",
                    r"eval\(",
                    r"Function\(",
                    r"setTimeout\(.*\+",
                    r"setInterval\(.*\+",
                ],
                "severity": SecuritySeverity.HIGH,
                "category": SecurityCategory.XSS_VULNERABILITY,
                "auto_fixable": False,
            },
            "path_traversal": {
                "patterns": [
                    r"open\([^)]*\.\./",
                    r"file\([^)]*\.\./",
                    r"read\([^)]*\.\./",
                    r"include[^)]*\.\./",
                    r"require[^)]*\.\./",
                ],
                "severity": SecuritySeverity.HIGH,
                "category": SecurityCategory.PATH_TRAVERSAL,
                "auto_fixable": False,
            },
            "weak_cryptography": {
                "patterns": [
                    r"md5\(",
                    r"sha1\(",
                    r"hashlib\.md5",
                    r"hashlib\.sha1",
                    r"DES\(",
                    r"RC4\(",
                    r"random\.random\(",
                ],
                "severity": SecuritySeverity.MEDIUM,
                "category": SecurityCategory.CRYPTOGRAPHIC,
                "auto_fixable": True,
            },
            "authentication_bypass": {
                "patterns": [
                    r"auth\s*=\s*(True|true)}",
                    r"authenticated\s*=\s*(True|true)",
                    r"bypass.*auth",
                    r"skip.*auth",
                    r"no.*auth.*required",
                ],
                "severity": SecuritySeverity.CRITICAL,
                "category": SecurityCategory.AUTHENTICATION,
                "auto_fixable": False,
            },
        }

    async def run_comprehensive_scan(
        self, scan_type: str = "full", target_paths: Optional[list[str]] = None
    ) -> SecurityScanResult:
        """Run comprehensive security scan"""

        scan_id = f"scan_{int(time.time())}"
        started_at = datetime.now(timezone.utc)

        logger.info(f"🔍 Starting comprehensive security scan: {scan_id}")

        # Initialize scan result
        result = SecurityScanResult(scan_id=scan_id, scan_type=scan_type, started_at=started_at)

        try:
            # Determine files to scan
            files_to_scan = await self._get_files_to_scan(target_paths)

            # Run security checks
            findings = []

            # 1. Static code analysis
            static_findings = await self._run_static_analysis(files_to_scan)
            findings.extend(static_findings)

            # 2. Banned imports check
            import_findings = await self._check_banned_imports(files_to_scan)
            findings.extend(import_findings)

            # 3. Secret detection
            secret_findings = await self._detect_hardcoded_secrets(files_to_scan)
            findings.extend(secret_findings)

            # 4. Constitutional AI compliance check
            if self.constitutional_framework:
                constitutional_findings = await self._check_constitutional_compliance(files_to_scan)
                findings.extend(constitutional_findings)

            # 5. Dependency vulnerability scan
            dependency_findings = await self._scan_dependencies()
            findings.extend(dependency_findings)

            # Populate scan result
            result.findings = findings
            result.files_scanned = len(files_to_scan)
            result.lines_scanned = sum(await self._count_lines(f) for f in files_to_scan)

            # Calculate severity counts
            result.critical_count = len([f for f in findings if f.severity == SecuritySeverity.CRITICAL])
            result.high_count = len([f for f in findings if f.severity == SecuritySeverity.HIGH])
            result.medium_count = len([f for f in findings if f.severity == SecuritySeverity.MEDIUM])
            result.low_count = len([f for f in findings if f.severity == SecuritySeverity.LOW])

            # Calculate constitutional drift score
            if self.constitutional_framework:
                result.constitutional_drift_score = await self._calculate_overall_drift_score(findings)
                result.compliance_status = "non_compliant" if result.constitutional_drift_score >= 0.15 else "compliant"

            # Auto-fix attempts
            if self.config.get("auto_fix_enabled", True):
                fix_results = await self._attempt_auto_fixes(findings)
                result.auto_fixed_count = fix_results["fixed_count"]
                result.fix_success_rate = fix_results["success_rate"]

            result.completed_at = datetime.now(timezone.utc)

            # Store scan result
            self.scan_history.append(result)

            # Update metrics
            await self._update_scan_metrics(result)

            # Log audit event
            if self.audit_logger:
                await self.audit_logger.log_event(
                    event_type=(
                        AuditEventType.SECURITY_INCIDENT
                        if result.critical_count > 0
                        else AuditEventType.SYSTEM_OPERATION
                    ),
                    action="security_scan_complete",
                    outcome="completed",
                    severity=AuditSeverity.CRITICAL if result.critical_count > 0 else AuditSeverity.INFO,
                    details={
                        "scan_id": scan_id,
                        "findings": len(findings),
                        "critical": result.critical_count,
                        "high": result.high_count,
                        "constitutional_drift": result.constitutional_drift_score,
                    },
                )

            logger.info(f"✅ Security scan complete: {len(findings)} findings, {result.auto_fixed_count} auto-fixed")

            return result

        except Exception as e:
            logger.error(f"❌ Security scan failed: {e}")
            result.completed_at = datetime.now(timezone.utc)
            raise

    async def _get_files_to_scan(self, target_paths: Optional[list[str]]) -> list[Path]:
        """Get list of files to scan"""

        files_to_scan = []

        if target_paths:
            # Scan specific paths
            for target in target_paths:
                target_path = Path(target)
                if target_path.is_file():
                    files_to_scan.append(target_path)
                elif target_path.is_dir():
                    files_to_scan.extend(self._find_files_in_directory(target_path))
        else:
            # Scan entire project
            files_to_scan.extend(self._find_files_in_directory(self.project_root))

        # Filter out excluded paths
        filtered_files = []
        for file_path in files_to_scan:
            if not any(excluded in str(file_path) for excluded in self.excluded_paths):
                filtered_files.append(file_path)

        return filtered_files

    def _find_files_in_directory(self, directory: Path) -> list[Path]:
        """Find files matching scan patterns in directory"""

        files = []

        for pattern in self.scan_patterns:
            files.extend(directory.rglob(pattern))

        return files

    async def _run_static_analysis(self, files: list[Path]) -> list[SecurityFinding]:
        """Run static code analysis"""

        findings = []

        for file_path in files:
            try:
                content = await self._read_file_content(file_path)
                if not content:
                    continue

                lines = content.split("\n")

                for rule_name, rule_config in self.security_rules.items():
                    for pattern in rule_config["patterns"]:
                        for line_num, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                finding = SecurityFinding(
                                    finding_id=f"{file_path.name}_{line_num}_{rule_name}",
                                    category=rule_config["category"],
                                    severity=rule_config["severity"],
                                    title=f"{rule_name.replace('_', ' ').title()} Detected",
                                    description=f"Potential {rule_name.replace('_', ' ')} found in {file_path}",
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    code_snippet=line.strip(),
                                    auto_fixable=rule_config.get("auto_fixable", False),
                                    evidence=[f"Pattern matched: {pattern}"],
                                )

                                findings.append(finding)

            except Exception as e:
                logger.warning(f"Failed to analyze {file_path}: {e}")

        return findings

    async def _check_banned_imports(self, files: list[Path]) -> list[SecurityFinding]:
        """Check for banned imports that violate lane architecture"""

        findings = []

        for file_path in files:
            try:
                content = await self._read_file_content(file_path)
                if not content:
                    continue

                # Determine which lane this file is in
                file_lane = "lukhas" if "lukhas/" in str(file_path) else "candidate"

                banned_patterns = self.banned_imports.get(file_lane, [])

                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for banned_pattern in banned_patterns:
                        if banned_pattern in line and line.strip().startswith(("import ", "from ")):
                            finding = SecurityFinding(
                                finding_id=f"{file_path.name}_{line_num}_banned_import",
                                category=SecurityCategory.BANNED_IMPORTS,
                                severity=SecuritySeverity.CRITICAL,
                                title="Banned Import Violation",
                                description=f"Production code in {file_lane}/ lane importing from candidate/ lane",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                auto_fixable=True,
                                fix_confidence=0.8,
                                evidence=[f"Banned pattern: {banned_pattern}"],
                                remediation="Replace with production-ready lukhas/ import or create production equivalent",
                            )

                            findings.append(finding)

            except Exception as e:
                logger.warning(f"Failed to check imports in {file_path}: {e}")

        return findings

    async def _detect_hardcoded_secrets(self, files: list[Path]) -> list[SecurityFinding]:
        """Detect hardcoded secrets and credentials"""

        findings = []

        # High-entropy string patterns that might be secrets
        secret_patterns = [
            r'["\'][A-Za-z0-9+/]{40,}[=]{0,2}["\']',  # Base64-like strings
            r'["\'][A-Fa-f0-9]{32,}["\']',  # Hex strings
            r"sk_live_[A-Za-z0-9]{24,}",  # Stripe live keys
            r"sk_test_[A-Za-z0-9]{24,}",  # Stripe test keys
            r"pk_live_[A-Za-z0-9]{24,}",  # Stripe publishable keys
            r"AKIA[A-Z0-9]{16}",  # AWS Access Keys
            r"ya29\.[A-Za-z0-9_-]+",  # Google OAuth tokens
            r'["\']ghp_[A-Za-z0-9]{36}["\']',  # GitHub personal access tokens
        ]

        for file_path in files:
            try:
                content = await self._read_file_content(file_path)
                if not content:
                    continue

                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern in secret_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            # Skip if it looks like a test or example
                            if any(
                                indicator in line.lower() for indicator in ["test", "example", "demo", "fake", "mock"]
                            ):
                                continue

                            finding = SecurityFinding(
                                finding_id=f"{file_path.name}_{line_num}_secret",
                                category=SecurityCategory.HARDCODED_SECRETS,
                                severity=SecuritySeverity.CRITICAL,
                                title="Hardcoded Secret Detected",
                                description="Potential hardcoded secret or API key found",
                                file_path=str(file_path),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                auto_fixable=True,
                                fix_confidence=0.9,
                                evidence=[f"High-entropy string: {match.group()[:10]}..."],
                                remediation="Replace with environment variable or secure configuration",
                            )

                            findings.append(finding)

            except Exception as e:
                logger.warning(f"Failed to detect secrets in {file_path}: {e}")

        return findings

    async def _check_constitutional_compliance(self, files: list[Path]) -> list[SecurityFinding]:
        """Check constitutional AI compliance"""

        if not self.constitutional_framework:
            return []

        findings = []

        for file_path in files:
            try:
                content = await self._read_file_content(file_path)
                if not content:
                    continue

                # Assess constitutional compliance of file content
                assessment = await self.constitutional_framework.assess_constitutional_compliance(
                    content=content, context={"file_path": str(file_path), "scan_context": True}
                )

                # Check drift threshold
                if assessment.drift_score >= 0.15:  # LUKHAS constitutional drift threshold
                    finding = SecurityFinding(
                        finding_id=f"{file_path.name}_constitutional_drift",
                        category=SecurityCategory.CONSTITUTIONAL_DRIFT,
                        severity=SecuritySeverity.CRITICAL,
                        title="Constitutional Drift Threshold Exceeded",
                        description=f"File exceeds constitutional drift threshold: {assessment.drift_score:.4f}",
                        file_path=str(file_path),
                        auto_fixable=False,
                        constitutional_impact=assessment.drift_score,
                        drift_contribution=assessment.drift_score,
                        evidence=assessment.risk_factors,
                        remediation="; ".join(assessment.recommendations),
                    )

                    findings.append(finding)

                # Check safety level
                if assessment.safety_level in [SafetyLevel.DANGER, SafetyLevel.CRITICAL]:
                    finding = SecurityFinding(
                        finding_id=f"{file_path.name}_safety_violation",
                        category=SecurityCategory.CONSTITUTIONAL_DRIFT,
                        severity=SecuritySeverity.HIGH,
                        title=f"Constitutional Safety Violation: {assessment.safety_level.value}",
                        description="File contains content that violates constitutional AI safety principles",
                        file_path=str(file_path),
                        auto_fixable=False,
                        constitutional_impact=1.0 - assessment.ethical_score,
                        evidence=assessment.constitutional_violations,
                        remediation="; ".join(assessment.mitigation_strategies),
                    )

                    findings.append(finding)

            except Exception as e:
                logger.warning(f"Failed to check constitutional compliance for {file_path}: {e}")

        return findings

    async def _scan_dependencies(self) -> list[SecurityFinding]:
        """Scan dependencies for known vulnerabilities"""

        findings = []

        try:
            # Check for requirements.txt
            req_files = [
                "requirements.txt",
                "requirements-test.txt",
                "pyproject.toml",
                "package.json",
            ]

            for req_file in req_files:
                req_path = self.project_root / req_file
                if req_path.exists():
                    # This would integrate with vulnerability databases in production
                    # For now, we'll do basic pattern matching for known vulnerable packages

                    content = await self._read_file_content(req_path)
                    if not content:
                        continue

                    # Known vulnerable patterns (simplified)
                    vulnerable_patterns = [
                        r"django==1\.[0-9]",  # Old Django versions
                        r"flask==0\.[0-9]",  # Old Flask versions
                        r"requests==2\.[0-9]\.",  # Old requests versions
                        r"urllib3==1\.[0-9]",  # Old urllib3 versions
                    ]

                    for line_num, line in enumerate(content.split("\n"), 1):
                        for pattern in vulnerable_patterns:
                            if re.search(pattern, line):
                                finding = SecurityFinding(
                                    finding_id=f"{req_file}_{line_num}_vuln_dep",
                                    category=SecurityCategory.DEPENDENCY_VULNERABILITY,
                                    severity=SecuritySeverity.HIGH,
                                    title="Vulnerable Dependency",
                                    description=f"Potentially vulnerable dependency: {line.strip()}",
                                    file_path=str(req_path),
                                    line_number=line_num,
                                    code_snippet=line.strip(),
                                    auto_fixable=True,
                                    remediation="Update to latest secure version",
                                )

                                findings.append(finding)

        except Exception as e:
            logger.warning(f"Failed to scan dependencies: {e}")

        return findings

    async def _attempt_auto_fixes(self, findings: list[SecurityFinding]) -> dict[str, Any]:
        """Attempt to automatically fix security issues"""

        fixed_count = 0
        total_fixable = len([f for f in findings if f.auto_fixable])

        for finding in findings:
            if not finding.auto_fixable:
                continue

            try:
                if await self._apply_auto_fix(finding):
                    fixed_count += 1
                    finding.status = "fixed"

                    # Log fix
                    if self.audit_logger:
                        await self.audit_logger.log_event(
                            event_type=AuditEventType.SYSTEM_OPERATION,
                            action="auto_fix_applied",
                            outcome="success",
                            severity=AuditSeverity.INFO,
                            details={
                                "finding_id": finding.finding_id,
                                "category": finding.category.value,
                                "file_path": finding.file_path,
                            },
                        )

            except Exception as e:
                logger.warning(f"Auto-fix failed for {finding.finding_id}: {e}")
                finding.status = "fix_failed"

        success_rate = fixed_count / total_fixable if total_fixable > 0 else 0.0

        return {
            "fixed_count": fixed_count,
            "total_fixable": total_fixable,
            "success_rate": success_rate,
        }

    async def _apply_auto_fix(self, finding: SecurityFinding) -> bool:
        """Apply automatic fix for a specific finding"""

        if finding.category == SecurityCategory.HARDCODED_SECRETS:
            return await self._fix_hardcoded_secret(finding)
        elif finding.category == SecurityCategory.BANNED_IMPORTS:
            return await self._fix_banned_import(finding)
        elif finding.category == SecurityCategory.CRYPTOGRAPHIC:
            return await self._fix_weak_crypto(finding)

        return False

    async def _fix_hardcoded_secret(self, finding: SecurityFinding) -> bool:
        """Fix hardcoded secret by replacing with environment variable"""

        try:
            file_path = Path(finding.file_path)
            content = await self._read_file_content(file_path)

            lines = content.split("\n")
            if finding.line_number and finding.line_number <= len(lines):
                line = lines[finding.line_number - 1]

                # Replace hardcoded secret with env var
                if "password" in line.lower():
                    fixed_line = re.sub(
                        r'password\s*=\s*["\'][^"\']+["\']',
                        'password = os.getenv("PASSWORD")',
                        line,
                    )
                elif "api_key" in line.lower():
                    fixed_line = re.sub(r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = os.getenv("API_KEY")', line)
                else:
                    # Generic secret replacement
                    fixed_line = re.sub(r'(\w+)\s*=\s*["\'][^"\']+["\']', r'\1 = os.getenv("\1".upper())', line)

                lines[finding.line_number - 1] = fixed_line

                # Write fixed content back
                fixed_content = "\n".join(lines)
                await self._write_file_content(file_path, fixed_content)

                return True

        except Exception as e:
            logger.error(f"Failed to fix hardcoded secret: {e}")

        return False

    async def _fix_banned_import(self, finding: SecurityFinding) -> bool:
        """Fix banned import by removing or commenting out"""

        try:
            file_path = Path(finding.file_path)
            content = await self._read_file_content(file_path)

            lines = content.split("\n")
            if finding.line_number and finding.line_number <= len(lines):
                # Comment out the banned import
                lines[finding.line_number - 1] = "# SECURITY FIX: " + lines[finding.line_number - 1]

                # Add comment explaining the fix
                comment = "# SECURITY: Banned import removed - replace with production equivalent"
                lines.insert(finding.line_number - 1, comment)

                # Write fixed content back
                fixed_content = "\n".join(lines)
                await self._write_file_content(file_path, fixed_content)

                return True

        except Exception as e:
            logger.error(f"Failed to fix banned import: {e}")

        return False

    async def _fix_weak_crypto(self, finding: SecurityFinding) -> bool:
        """Fix weak cryptography by suggesting stronger alternatives"""

        try:
            file_path = Path(finding.file_path)
            content = await self._read_file_content(file_path)

            lines = content.split("\n")
            if finding.line_number and finding.line_number <= len(lines):
                line = lines[finding.line_number - 1]

                # Replace weak crypto with strong alternatives
                fixed_line = line
                fixed_line = re.sub(r"hashlib\.md5", "hashlib.sha256", fixed_line)
                fixed_line = re.sub(r"hashlib\.sha1", "hashlib.sha256", fixed_line)
                fixed_line = re.sub(r"md5\(", "hashlib.sha256(", fixed_line)
                fixed_line = re.sub(r"random\.random\(\)", "secrets.SystemRandom()", fixed_line)

                lines[finding.line_number - 1] = fixed_line

                # Write fixed content back
                fixed_content = "\n".join(lines)
                await self._write_file_content(file_path, fixed_content)

                return True

        except Exception as e:
            logger.error(f"Failed to fix weak crypto: {e}")

        return False

    async def _calculate_overall_drift_score(self, findings: list[SecurityFinding]) -> float:
        """Calculate overall constitutional drift score from findings"""

        if not findings:
            return 0.0

        # Weight different categories differently
        category_weights = {
            SecurityCategory.CONSTITUTIONAL_DRIFT: 1.0,
            SecurityCategory.HARDCODED_SECRETS: 0.3,
            SecurityCategory.BANNED_IMPORTS: 0.2,
            SecurityCategory.AUTHENTICATION: 0.4,
            SecurityCategory.CRYPTOGRAPHIC: 0.2,
        }

        total_drift = 0.0
        total_weight = 0.0

        for finding in findings:
            weight = category_weights.get(finding.category, 0.1)

            # Convert severity to drift contribution
            severity_drift = {
                SecuritySeverity.CRITICAL: 0.2,
                SecuritySeverity.HIGH: 0.1,
                SecuritySeverity.MEDIUM: 0.05,
                SecuritySeverity.LOW: 0.01,
            }.get(finding.severity, 0.01)

            # Use constitutional impact if available
            if finding.constitutional_impact is not None:
                drift_contribution = finding.constitutional_impact
            else:
                drift_contribution = severity_drift

            total_drift += drift_contribution * weight
            total_weight += weight

        return min(1.0, total_drift / total_weight if total_weight > 0 else 0.0)

    async def _read_file_content(self, file_path: Path) -> Optional[str]:
        """Read file content safely"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return None

    async def _write_file_content(self, file_path: Path, content: str) -> bool:
        """Write file content safely"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Could not write {file_path}: {e}")
            return False

    async def _count_lines(self, file_path: Path) -> int:
        """Count lines in file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                return len(f.readlines())
        except Exception:
            return 0

    async def _update_scan_metrics(self, result: SecurityScanResult):
        """Update scan metrics"""
        self.scan_metrics["total_scans"] += 1
        self.scan_metrics["total_findings"] += len(result.findings)
        self.scan_metrics["auto_fixes_applied"] += result.auto_fixed_count

        # Constitutional violations
        constitutional_violations = len(
            [f for f in result.findings if f.category == SecurityCategory.CONSTITUTIONAL_DRIFT]
        )
        self.scan_metrics["constitutional_violations"] += constitutional_violations

        # Average scan time
        if result.completed_at:
            scan_time = (result.completed_at - result.started_at).total_seconds()
            current_avg = self.scan_metrics["avg_scan_time_seconds"]
            total_scans = self.scan_metrics["total_scans"]

            self.scan_metrics["avg_scan_time_seconds"] = (current_avg * (total_scans - 1) + scan_time) / total_scans

    def get_scan_summary(self) -> dict[str, Any]:
        """Get comprehensive scan summary"""

        recent_scans = self.scan_history[-10:]  # Last 10 scans

        if not recent_scans:
            return {"message": "No scans performed yet"}

        latest_scan = recent_scans[-1]

        return {
            "latest_scan": {
                "scan_id": latest_scan.scan_id,
                "completed_at": latest_scan.completed_at.isoformat() if latest_scan.completed_at else None,
                "total_findings": len(latest_scan.findings),
                "critical": latest_scan.critical_count,
                "high": latest_scan.high_count,
                "medium": latest_scan.medium_count,
                "low": latest_scan.low_count,
                "constitutional_drift_score": latest_scan.constitutional_drift_score,
                "compliance_status": latest_scan.compliance_status,
                "auto_fixed": latest_scan.auto_fixed_count,
            },
            "metrics": self.scan_metrics,
            "total_scans": len(self.scan_history),
            "constitutional_drift_status": "CRITICAL" if latest_scan.constitutional_drift_score >= 0.15 else "NORMAL",
        }


async def run_enterprise_security_scan():
    """Run enterprise security scan - main entry point"""

    scanner = EnterprisSecurityScanner(
        {
            "project_root": ".",
            "auto_fix_enabled": True,
            "scan_patterns": ["*.py", "*.js", "*.ts", "*.yaml", "*.yml"],
        }
    )

    # Run comprehensive scan
    result = await scanner.run_comprehensive_scan("full")

    # Print results
    print("\n🛡️ LUKHAS Enterprise Security Scan Results")
    print("=" * 50)
    print(f"Scan ID: {result.scan_id}")
    print(f"Files Scanned: {result.files_scanned}")
    print(f"Total Findings: {len(result.findings)}")
    print(f"  - Critical: {result.critical_count}")
    print(f"  - High: {result.high_count}")
    print(f"  - Medium: {result.medium_count}")
    print(f"  - Low: {result.low_count}")
    print(f"Constitutional Drift Score: {result.constitutional_drift_score:.4f}")
    print(f"Compliance Status: {result.compliance_status}")
    print(f"Auto-Fixed Issues: {result.auto_fixed_count}")

    # Show critical findings
    critical_findings = [f for f in result.findings if f.severity == SecuritySeverity.CRITICAL]
    if critical_findings:
        print("\n🚨 Critical Findings:")
        for finding in critical_findings[:5]:  # Show first 5
            print(f"  - {finding.title}: {finding.file_path}:{finding.line_number}")

    return result


if __name__ == "__main__":
    asyncio.run(run_enterprise_security_scan())