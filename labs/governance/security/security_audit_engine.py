"""
🛡️ LUKHAS AI Security Audit Engine
=================================

Comprehensive security scanning and audit system for Phase 5 security enhancements.
Integrates with Guardian System for real-time threat detection and policy enforcement.

Constellation Framework: ⚛️🧠🛡️
- ⚛️ Identity: Secure authentication and authorization auditing
- 🧠 Consciousness: Intelligent threat pattern recognition
- 🛡️ Guardian: Real-time security policy enforcement

Author: LUKHAS AI Security Team
Version: 1.0.0
"""
from __future__ import annotations


import asyncio
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Security-specific imports
try:
    import secrets
    import ssl

    import jwt
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as e:
    print(f"Warning: Missing security dependencies: {e}")

# LUKHAS imports
try:
    from ...core.glyph import SymbolicGlyph
    from ..audit_logger import AuditLogger
    from ..guardian_system import GuardianSystem
except ImportError:
    print("Warning: Could not import Guardian System components")
    GuardianSystem = None
    AuditLogger = None
    SymbolicGlyph = None


class SecurityLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities"""

    SECRET_EXPOSURE = "secret_exposure"
    DEPENDENCY_VULN = "dependency_vulnerability"
    CODE_INJECTION = "code_injection"
    ACCESS_CONTROL = "access_control"
    CRYPTO_WEAKNESS = "crypto_weakness"
    PII_EXPOSURE = "pii_exposure"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityFinding:
    """Individual security finding"""

    id: str
    type: VulnerabilityType
    level: SecurityLevel
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    evidence: Optional[str] = None
    recommendation: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class SecurityAuditReport:
    """Complete security audit report"""

    audit_id: str
    timestamp: str
    findings: list[SecurityFinding]
    summary: dict[str, int]
    guardian_status: dict[str, Any]
    recommendations: list[str]
    compliance_status: dict[str, bool]


class SecretDetector:
    """Detects secrets, API keys, and sensitive data"""

    def __init__(self):
        self.patterns = {
            "api_key": [
                r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                r'(?i)apikey["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
            ],
            "password": [
                r'(?i)password["\']?\s*[:=]\s*["\']?([^"\'\s]{8,})',
                r'(?i)passwd["\']?\s*[:=]\s*["\']?([^"\'\s]{8,})',
            ],
            "token": [
                r'(?i)token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                r"(?i)bearer\s+([a-zA-Z0-9_-]{20,})",
            ],
            "aws_key": [
                r"AKIA[0-9A-Z]{16}",
                r'aws_access_key_id["\']?\s*[:=]\s*["\']?([A-Z0-9]{20})',
            ],
            "github_token": [
                r"ghp_[0-9a-zA-Z]{36}",
                r"github_pat_[0-9a-zA-Z_]{82}",
            ],
            "openai_key": [
                r"sk-[a-zA-Z0-9]{48}",
                r'(?i)openai[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?(sk-[a-zA-Z0-9]{48})',
            ],
            "anthropic_key": [
                r"sk-ant-[a-zA-Z0-9-_]{95,}",
                r'(?i)anthropic[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?(sk-ant-[a-zA-Z0-9-_]{95,})',
            ],
            "jwt_token": [
                r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
            ],
            "private_key": [
                r"-----BEGIN " + r"PRIVATE KEY-----",  # nosec
                r"-----BEGIN " + r"RSA PRIVATE KEY-----",  # nosec
                r"-----BEGIN OPENSSH PRIVATE KEY-----",
            ],
        }

        self.whitelist_patterns = [
            r"example\.com",
            r"test[_-]?key",
            r"dummy[_-]?token",
            r"placeholder",
            r"<[A-Z_]+>",  # Template variables
        ]

    def scan_content(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Scan content for secrets"""
        findings = []

        for secret_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)

                for match in matches:
                    # Check if it's whitelisted
                    if self._is_whitelisted(match.group(0)):
                        continue

                    line_num = content[: match.start()].count("\n") + 1

                    finding = SecurityFinding(
                        id=f"secret_{hashlib.md5(f'{file_path}:{line_num}:{secret_type)}'.encode()).hexdigest()[:12]}",
                        type=VulnerabilityType.SECRET_EXPOSURE,
                        level=(
                            SecurityLevel.HIGH
                            if secret_type in ["private_key", "aws_key"]
                            else SecurityLevel.MEDIUM
                        ),
                        title=f"Potential {secret_type.replace('_', ' ').title()} Exposure",
                        description=f"Detected potential {secret_type} in file",
                        file_path=file_path,
                        line_number=line_num,
                        evidence=(
                            match.group(0)[:50] + "..."
                            if len(match.group(0)) > 50
                            else match.group(0)
                        ),
                        recommendation=f"Remove or properly secure the {secret_type}",
                    )
                    findings.append(finding)

        return findings

    def _is_whitelisted(self, content: str) -> bool:
        """Check if content matches whitelist patterns"""
        for pattern in self.whitelist_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False


class DependencyScanner:
    """Scans dependencies for known vulnerabilities"""

    def __init__(self):
        self.known_vulnerabilities = {
            "requests": ["2.25.1", "2.26.0"],  # Example vulnerable versions
            "urllib3": ["1.26.5"],
            "pillow": ["8.2.0", "8.3.1"],
        }

    async def scan_requirements(self, requirements_file: str) -> list[SecurityFinding]:
        """Scan requirements file for vulnerable dependencies"""
        findings = []

        if not os.path.exists(requirements_file):
            return findings

        try:
            with open(requirements_file) as f:
                content = f.read()

            # Parse requirements
            for line in content.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Extract package name and version
                match = re.match(r"([a-zA-Z0-9_-]+)([>=<~!]+)([0-9.]+)", line)
                if not match:
                    continue

                package, operator, version = match.groups()

                if package.lower() in self.known_vulnerabilities:
                    vulnerable_versions = self.known_vulnerabilities[package.lower()]
                    if version in vulnerable_versions:
                        finding = SecurityFinding(
                            id=f"dep_{hashlib.md5(f'{package}:{version)}'.encode()).hexdigest()[:12]}",
                            type=VulnerabilityType.DEPENDENCY_VULN,
                            level=SecurityLevel.HIGH,
                            title=f"Vulnerable Dependency: {package}",
                            description=f"Package {package} version {version} has known vulnerabilities",
                            file_path=requirements_file,
                            evidence=line,
                            recommendation=f"Update {package} to a secure version",
                        )
                        findings.append(finding)

        except Exception as e:
            print(f"Error scanning requirements file {requirements_file}: {e}")

        return findings


class CodeSecurityScanner:
    """Scans code for security vulnerabilities"""

    def __init__(self):
        self.dangerous_patterns = {
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r"cursor\.execute\s*\([^)]*%[^)]*\)",
            ],
            "command_injection": [
                r"os\.system\s*\([^)]*\+[^)]*\)",
                r"subprocess\.call\s*\([^)]*\+[^)]*\)",
                r"eval\s*\([^)]*\)",
                r"exec\s*\([^)]*\)",
            ],
            "path_traversal": [
                r"open\s*\([^)]*\.\./[^)]*\)",
                r"file\s*\([^)]*\.\./[^)]*\)",
            ],
            "weak_crypto": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"DES\s*\(",
            ],
        }

    def scan_file(self, file_path: str) -> list[SecurityFinding]:
        """Scan a single file for security issues"""
        findings = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            for vuln_type, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(
                        pattern, content, re.IGNORECASE | re.MULTILINE
                    )

                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        finding = SecurityFinding(
                            id=f"code_{hashlib.md5(f'{file_path}:{line_num}:{vuln_type)}'.encode()).hexdigest()[:12]}",
                            type=(
                                VulnerabilityType.CODE_INJECTION
                                if "injection" in vuln_type
                                else VulnerabilityType.CRYPTO_WEAKNESS
                            ),
                            level=SecurityLevel.HIGH,
                            title=f"Potential {vuln_type.replace('_', ' ').title()}",
                            description=f"Detected potential {vuln_type} vulnerability",
                            file_path=file_path,
                            line_number=line_num,
                            evidence=match.group(0),
                            recommendation=f"Review and secure {vuln_type} vulnerability",
                        )
                        findings.append(finding)

        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")

        return findings


class AdapterSecurityAuditor:
    """🛡️ Adapter-specific security auditor for Canary Pack 4"""

    def __init__(self):
        self.audit_patterns = {
            "capability_bypass": [
                r"(?i)bypass[_\s]+capability",
                r"(?i)skip[_\s]+auth",
                r"(?i)disable[_\s]+security",
            ],
            "consent_violations": [
                r"(?i)force[_\s]+consent",
                r"(?i)ignore[_\s]+consent",
                r"consent[_\s]*=[_\s]*(?:false|False|0)",
            ],
            "dangerous_operations": [
                r"(?i)bulk[_\s]+delete",
                r"(?i)mass[_\s]+delete",
                r"(?i)delete[_\s]+all",
                r"(?i)drop[_\s]+table",
                r"(?i)truncate[_\s]+table",
            ],
            "privilege_escalation": [
                r"(?i)sudo[_\s]+",
                r"(?i)admin[_\s]*=[_\s]*(?:true|True|1)",
                r"(?i)root[_\s]+access",
                r"(?i)superuser[_\s]*=[_\s]*(?:true|True|1)",
            ],
        }

    async def audit_adapter_security(self, adapter_path: str) -> list[SecurityFinding]:
        """Audit specific adapter for security issues"""
        findings = []

        try:
            with open(adapter_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check for capability token validation
            if "validate_capability_token" not in content:
                findings.append(
                    SecurityFinding(
                        id=f"adapter_missing_capability_{hashlib.md5(adapter_path.encode()).hexdigest()[:8]}",
                        type=VulnerabilityType.ACCESS_CONTROL,
                        level=SecurityLevel.HIGH,
                        title="Missing Capability Token Validation",
                        description="Adapter does not validate capability tokens",
                        file_path=adapter_path,
                        recommendation="Implement capability token validation in all adapter methods",
                    )
                )

            # Check for consent verification
            if "check_consent" not in content:
                findings.append(
                    SecurityFinding(
                        id=f"adapter_missing_consent_{hashlib.md5(adapter_path.encode()).hexdigest(}[:8])}",
                        type=VulnerabilityType.POLICY_VIOLATION,
                        level=SecurityLevel.HIGH,
                        title="Missing Consent Verification",
                        description="Adapter does not verify user consent before operations",
                        file_path=adapter_path,
                        recommendation="Implement consent verification using Guardian System",
                    )
                )

            # Check for audit trail logging
            if "audit_trail" not in content and "telemetry" not in content:
                findings.append(
                    SecurityFinding(
                        id=f"adapter_missing_audit_{hashlib.md5(adapter_path.encode()).hexdigest(}[:8])}",
                        type=VulnerabilityType.POLICY_VIOLATION,
                        level=SecurityLevel.MEDIUM,
                        title="Missing Audit Trail Logging",
                        description="Adapter does not implement comprehensive audit trail logging",
                        file_path=adapter_path,
                        recommendation="Implement Λ-trace audit logging for all operations",
                    )
                )

            # Scan for dangerous patterns
            for pattern_type, patterns in self.audit_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(
                        pattern, content, re.IGNORECASE | re.MULTILINE
                    )

                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        findings.append(
                            SecurityFinding(
                                id=f"adapter_{pattern_type}_{hashlib.md5(f'{adapter_path}:{line_num)}'.encode()).hexdigest()[:12]}",
                                type=VulnerabilityType.POLICY_VIOLATION,
                                level=(
                                    SecurityLevel.HIGH
                                    if pattern_type
                                    in ["dangerous_operations", "privilege_escalation"]
                                    else SecurityLevel.MEDIUM
                                ),
                                title=f"Potential {pattern_type.replace('_', ' ').title(}",
                                description=f"Detected potential {pattern_type)} in adapter code",
                                file_path=adapter_path,
                                line_number=line_num,
                                evidence=match.group(0),
                                recommendation=f"Review and secure {pattern_type} implementation",
                            )
                        )

        except Exception as e:
            print(f"Error auditing adapter {adapter_path}: {e}")

        return findings


class SecurityAuditEngine:
    """Main security audit engine with enhanced adapter security auditing"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.secret_detector = SecretDetector()
        self.dependency_scanner = DependencyScanner()
        self.code_scanner = CodeSecurityScanner()
        self.adapter_auditor = AdapterSecurityAuditor()  # New adapter-specific auditor

        # Initialize Guardian System integration
        self.guardian_system = GuardianSystem() if GuardianSystem else None
        self.audit_logger = AuditLogger() if AuditLogger else None

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def run_comprehensive_audit(self) -> SecurityAuditReport:
        """Run comprehensive security audit"""
        audit_id = f"audit_{int(time.time())}_{secrets.token_hex(4)}"
        timestamp = datetime.now(timezone.utc).isoformat()

        self.logger.info(f"Starting comprehensive security audit: {audit_id}")

        findings = []

        # 1. Secret detection scan
        self.logger.info("Running secret detection scan...")
        secret_findings = await self._scan_for_secrets()
        findings.extend(secret_findings)

        # 2. Dependency vulnerability scan
        self.logger.info("Running dependency vulnerability scan...")
        dep_findings = await self._scan_dependencies()
        findings.extend(dep_findings)

        # 3. Code security scan
        self.logger.info("Running code security scan...")
        code_findings = await self._scan_code_security()
        findings.extend(code_findings)

        # 4. Access control audit
        self.logger.info("Running access control audit...")
        access_findings = await self._audit_access_controls()
        findings.extend(access_findings)

        # 5. Adapter security audit (Canary Pack 4)
        self.logger.info("Running adapter security audit...")
        adapter_findings = await self._audit_adapter_security()
        findings.extend(adapter_findings)

        # 6. Guardian System status check
        guardian_status = await self._check_guardian_status()

        # Generate summary
        summary = self._generate_summary(findings)

        # Generate recommendations
        recommendations = self._generate_recommendations(findings)

        # Check compliance status
        compliance_status = self._check_compliance_status(findings)

        # Log audit completion
        if self.audit_logger:
            await self.audit_logger.log_security_audit(audit_id, findings)

        report = SecurityAuditReport(
            audit_id=audit_id,
            timestamp=timestamp,
            findings=findings,
            summary=summary,
            guardian_status=guardian_status,
            recommendations=recommendations,
            compliance_status=compliance_status,
        )

        self.logger.info(f"Security audit completed: {len(findings)} findings")
        return report

    async def _scan_for_secrets(self) -> list[SecurityFinding]:
        """Scan for exposed secrets"""
        findings = []

        # File extensions to scan
        scan_extensions = {
            ".py",
            ".js",
            ".ts",
            ".json",
            ".yaml",
            ".yml",
            ".env",
            ".config",}
        }

        # Directories to skip
        skip_dirs = {
            ".git",
            "__pycache__",
            "node_modules",
            ".venv",
            "venv",
            "dist",
            "build",}
        }

        for root, dirs, files in os.walk(self.project_root):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for file in files:
                file_path = Path(root) / file

                if file_path.suffix.lower() in scan_extensions:
                    try:
                        with open(
                            file_path, encoding="utf-8", errors="ignore"
                        ) as f:
                            content = f.read()

                        file_findings = self.secret_detector.scan_content(
                            content, str(file_path)
                        )
                        findings.extend(file_findings)

                    except Exception as e:
                        self.logger.warning(f"Could not scan file {file_path}: {e}")

        return findings

    async def _scan_dependencies(self) -> list[SecurityFinding]:
        """Scan for dependency vulnerabilities"""
        findings = []

        # Look for requirements files
        requirements_files = [
            "requirements.txt",
            "requirements-test.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "poetry.lock",
            "Pipfile",
            "Pipfile.lock",
        ]

        for req_file in requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                file_findings = await self.dependency_scanner.scan_requirements(
                    str(req_path)
                )
                findings.extend(file_findings)

        return findings

    async def _scan_code_security(self) -> list[SecurityFinding]:
        """Scan code for security vulnerabilities"""
        findings = []

        # Scan Python files
        for py_file in self.project_root.rglob("*.py"):
            if ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue

            file_findings = self.code_scanner.scan_file(str(py_file))
            findings.extend(file_findings)

        return findings

    async def _audit_access_controls(self) -> list[SecurityFinding]:
        """Audit access control configurations"""
        findings = []

        # Check for identity configurations
        identity_configs = (
            list(self.project_root.rglob("*identity*.yaml"))
            + list(self.project_root.rglob("*auth*.json"))
            + list(self.project_root.rglob("*permissions*.json"))
        )

        for config_file in identity_configs:
            try:
                with open(config_file) as f:
                    content = f.read()

                # Check for overly permissive configurations
                if "admin: true" in content or "superuser: true" in content:
                    finding = SecurityFinding(
                        id=f"access_{hashlib.md5(str(config_file).encode()).hexdigest(}[:8])}",
                        type=VulnerabilityType.ACCESS_CONTROL,
                        level=SecurityLevel.MEDIUM,
                        title="Potentially Overly Permissive Access Control",
                        description="Found admin or superuser permissions in configuration",
                        file_path=str(config_file),
                        evidence=content[:200],
                        recommendation="Review and restrict access permissions",
                    )
                    findings.append(finding)

            except Exception as e:
                self.logger.warning(
                    f"Could not audit access control file {config_file}: {e}"
                )

        return findings

    async def _audit_adapter_security(self) -> list[SecurityFinding]:
        """Audit adapter security configurations (Canary Pack 4)"""
        findings = []

        # Find all adapter files
        adapter_patterns = [
            "**/adapters/**/*.py",
            "**/bridge/adapters/*.py",
            "**/*_adapter.py",
            "**/*adapter*.py",
        ]

        adapter_files = set()
        for pattern in adapter_patterns:
            adapter_files.update(self.project_root.glob(pattern))

        # Audit each adapter
        for adapter_file in adapter_files:
            if ".git" in str(adapter_file) or "__pycache__" in str(adapter_file):
                continue

            adapter_findings = await self.adapter_auditor.audit_adapter_security(
                str(adapter_file)
            )
            findings.extend(adapter_findings)

        return findings

    async def _check_guardian_status(self) -> dict[str, Any]:
        """Check Guardian System status"""
        if not self.guardian_system:
            return {
                "status": "unavailable",
                "reason": "Guardian System not initialized",}
            }

        try:
            status = self.guardian_system.get_status()
            return {
                "status": "active" if status["active"] else "inactive",
                "components": status["components"],
                "availability": status,}
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def _generate_summary(self, findings: list[SecurityFinding]) -> dict[str, int]:
        """Generate summary statistics"""
        summary = {
            "total_findings": len(findings),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,}
        }

        for finding in findings:
            summary[finding.level.value] += 1

        # Add type breakdown
        for vuln_type in VulnerabilityType:
            type_count = sum(1 for f in findings if f.type == vuln_type)
            summary[vuln_type.value] = type_count

        return summary

    def _generate_recommendations(self, findings: list[SecurityFinding]) -> list[str]:
        """Generate security recommendations"""
        recommendations = []

        # Count findings by type
        type_counts = {}
        for finding in findings:
            type_counts[finding.type] = type_counts.get(finding.type, 0) + 1

        # Generate recommendations based on findings
        if VulnerabilityType.SECRET_EXPOSURE in type_counts:
            recommendations.append(
                f"🔑 Found {type_counts[VulnerabilityType.SECRET_EXPOSURE]} potential secret exposures. "
                "Implement proper secret management using environment variables or secret managers."
            )

        if VulnerabilityType.DEPENDENCY_VULN in type_counts:
            recommendations.append(
                f"📦 Found {type_counts[VulnerabilityType.DEPENDENCY_VULN]} vulnerable dependencies. "
                "Update packages to secure versions and implement dependency scanning in CI/CD."
            )

        if VulnerabilityType.CODE_INJECTION in type_counts:
            recommendations.append(
                f"💉 Found {type_counts[VulnerabilityType.CODE_INJECTION]} potential code injection vulnerabilities. "
                "Implement proper input validation and parameterized queries."
            )

        if VulnerabilityType.ACCESS_CONTROL in type_counts:
            recommendations.append(
                f"🛡️ Found {type_counts[VulnerabilityType.ACCESS_CONTROL]} access control issues. "
                "Review and implement principle of least privilege."
            )

        if VulnerabilityType.POLICY_VIOLATION in type_counts:
            recommendations.append(
                f"📋 Found {type_counts[VulnerabilityType.POLICY_VIOLATION]} policy violations. "
                "Ensure all adapters implement proper consent verification and audit trails."
            )

        # General recommendations
        recommendations.extend(
            [
                "🔍 Implement regular security audits and vulnerability scanning",
                "📋 Establish security policies and procedures",
                "🚨 Set up security monitoring and alerting",
                "🎓 Provide security training for development team",
                "🔐 Implement multi-factor authentication where applicable",
            ]
        )

        return recommendations

    def _check_compliance_status(
        self, findings: list[SecurityFinding]
    ) -> dict[str, bool]:
        """Check compliance with security standards"""
        compliance = {
            "gdpr_data_protection": True,
            "secure_coding_practices": True,
            "access_control_standards": True,
            "audit_trail_requirements": True,
            "encryption_standards": True,}
        }

        # Check for compliance violations
        for finding in findings:
            if finding.type == VulnerabilityType.PII_EXPOSURE:
                compliance["gdpr_data_protection"] = False

            if finding.type == VulnerabilityType.CODE_INJECTION:
                compliance["secure_coding_practices"] = False

            if finding.type == VulnerabilityType.ACCESS_CONTROL:
                compliance["access_control_standards"] = False

            if finding.type == VulnerabilityType.CRYPTO_WEAKNESS:
                compliance["encryption_standards"] = False

        return compliance

    async def save_report(self, report: SecurityAuditReport, output_path: str = None):
        """Save audit report to file"""
        if output_path is None:
            output_path = f"security_audit_report_{report.audit_id}.json"

        report_dict = asdict(report)

        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2, default=str)

        self.logger.info(f"Security audit report saved to: {output_path}")


# CLI interface for security audits
async def main():
    """Main entry point for security audit CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AI Security Audit Engine")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run security audit
    engine = SecurityAuditEngine(args.project_root)
    report = await engine.run_comprehensive_audit()

    # Save report
    await engine.save_report(report, args.output)

    # Print summary
    print(f"\n🛡️ Security Audit Complete - ID: {report.audit_id}")
    print(f"📊 Total Findings: {report.summary['total_findings']}")
    print(f"🚨 Critical: {report.summary['critical']}")
    print(f"⚠️  High: {report.summary['high']}")
    print(f"📋 Medium: {report.summary['medium']}")
    print(f"ℹ️  Low: {report.summary['low']}")

    if report.summary["critical"] > 0 or report.summary["high"] > 0:
        print("\n🚨 High-priority security issues found! Review report for details.")
        return 1

    return 0


if __name__ == "__main__":
    asyncio.run(main())