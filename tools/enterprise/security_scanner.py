#!/usr/bin/env python3
"""
LUKHAS Enterprise Security Scanner
Autonomous security vulnerability detection and remediation system
Combines best practices from ΛBot Security Healer with enterprise requirements
"""

import asyncio
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog
import yaml

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class SeverityLevel(str, Enum):
    """Security severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecretType(str, Enum):
    """Types of secrets to detect"""

    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"
    CERTIFICATE = "certificate"


@dataclass
class SecurityVulnerability:
    """Enhanced security vulnerability with validation"""

    package: str
    current_version: str
    vulnerable_versions: str
    fixed_version: str
    severity: SeverityLevel
    cve_id: Optional[str] = None
    description: str = ""
    affected_files: list[str] = field(default_factory=list)
    fix_confidence: float = 0.0
    auto_fixable: bool = False
    cvss_score: Optional[float] = None
    exploit_available: bool = False
    public_disclosure_date: Optional[datetime] = None

    def risk_score(self) -> float:
        """Calculate risk score based on multiple factors"""
        base_score = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 8.0,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.0,
            SeverityLevel.INFO: 0.5,
        }[self.severity]

        # Adjust for exploit availability
        if self.exploit_available:
            base_score *= 1.5

        # Adjust for age of vulnerability
        if self.public_disclosure_date:
            days_old = (datetime.utcnow() - self.public_disclosure_date).days
            if days_old > 90:
                base_score *= 1.2

        return min(base_score, 10.0)


@dataclass
class SecretDetection:
    """Detected secret in codebase"""

    file_path: str
    line_number: int
    secret_type: SecretType
    pattern_matched: str
    confidence: float
    hash_value: str  # SHA256 of the secret for tracking


class SecurityScanner:
    """
    Enterprise-grade security scanner with:
    - Multi-layer vulnerability detection
    - Secret scanning
    - License compliance
    - SBOM generation
    - Automated remediation
    - Audit logging
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.vulnerability_db = {}
        self.secret_patterns = self._compile_secret_patterns()
        self.fix_history = []
        self.scan_results = []

        # Security thresholds
        self.auto_fix_threshold = self.config.get("auto_fix_threshold", 0.8)
        self.critical_threshold = self.config.get("critical_threshold", 7.0)

        # Audit logger
        self.audit_logger = structlog.get_logger("security_audit")

    def _load_config(self, config_path: Optional[Path]) -> dict[str, Any]:
        """Load security scanner configuration"""
        default_config = {
            "scan_paths": ["."],
            "exclude_paths": [
                "__pycache__",
                ".git",
                "node_modules",
                "venv",
                ".env",
                ".pytest_cache",
            ],
            "secret_scanning": {"enabled": True, "custom_patterns": []},
            "vulnerability_scanning": {
                "python": True,
                "javascript": True,
                "docker": True,
                "system": False,
            },
            "auto_fix_threshold": 0.8,
            "critical_threshold": 7.0,
            "sbom_format": "cyclonedx",
        }

        if config_path and config_path.exists():
            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def _compile_secret_patterns(self) -> dict[SecretType, list[re.Pattern]]:
        """Compile regex patterns for secret detection"""
        patterns = {
            SecretType.API_KEY: [
                re.compile(
                    r'["\']?api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I
                ),
                re.compile(r'["\']?apikey["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
                re.compile(r"sk-[a-zA-Z0-9]{48}"),  # OpenAI
                re.compile(r"AIza[0-9A-Za-z\\-_]{35}"),  # Google
            ],
            SecretType.PASSWORD: [
                re.compile(r'["\']?password["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
                re.compile(r'["\']?pwd["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
                re.compile(r'["\']?pass["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
            ],
            SecretType.TOKEN: [
                re.compile(r'["\']?token["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I),
                re.compile(
                    r'["\']?auth[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I
                ),
                re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub personal token
                re.compile(r"gho_[a-zA-Z0-9]{36}"),  # GitHub OAuth token
            ],
            SecretType.PRIVATE_KEY: [
                re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
                re.compile(
                    r'["\']?private[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']', re.I
                ),
            ],
            SecretType.CONNECTION_STRING: [
                re.compile(r"mongodb(\+srv)?://[^\s]+"),
                re.compile(r"postgres(ql)?://[^\s]+"),
                re.compile(r"mysql://[^\s]+"),
                re.compile(r"redis://[^\s]+"),
            ],
        }

        # Add custom patterns from config
        custom_patterns = self.config.get("secret_scanning", {}).get(
            "custom_patterns", []
        )
        for pattern_config in custom_patterns:
            pattern_type = SecretType(pattern_config["type"])
            pattern = re.compile(
                pattern_config["pattern"],
                re.I if pattern_config.get("case_insensitive") else 0,
            )
            patterns.setdefault(pattern_type, []).append(pattern)

        return patterns

    async def scan_complete(self) -> dict[str, Any]:
        """
        Perform comprehensive security scan
        """
        start_time = time.time()
        logger.info(
            "security_scan_started",
            scan_id=self._generate_scan_id(),
            config=self.config,
        )

        results = {
            "scan_id": self._generate_scan_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "vulnerabilities": [],
            "secrets": [],
            "licenses": [],
            "sbom": None,
            "summary": {},
        }

        try:
            # Run all scans in parallel
            scan_tasks = []

            if self.config.get("vulnerability_scanning", {}).get("python"):
                scan_tasks.append(self._scan_python_vulnerabilities())

            if self.config.get("vulnerability_scanning", {}).get("javascript"):
                scan_tasks.append(self._scan_javascript_vulnerabilities())

            if self.config.get("secret_scanning", {}).get("enabled"):
                scan_tasks.append(self._scan_for_secrets())

            scan_tasks.append(self._scan_licenses())
            scan_tasks.append(self._generate_sbom())

            # Execute all scans
            scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)

            # Process results
            for result in scan_results:
                if isinstance(result, Exception):
                    logger.error("scan_task_failed", error=str(result))
                elif isinstance(result, list):
                    if result and isinstance(result[0], SecurityVulnerability):
                        results["vulnerabilities"].extend(result)
                    elif result and isinstance(result[0], SecretDetection):
                        results["secrets"].extend(result)
                elif isinstance(result, dict):
                    if "licenses" in result:
                        results["licenses"] = result["licenses"]
                    elif "sbom" in result:
                        results["sbom"] = result["sbom"]

            duration = time.time() - start_time
            # Generate summary
            results["summary"] = self._generate_summary(results, duration)

            # Audit log
            self.audit_logger.info(
                "security_scan_completed",
                scan_id=results["scan_id"],
                vulnerabilities_found=len(results["vulnerabilities"]),
                secrets_found=len(results["secrets"]),
            )

            # Save results
            self._save_results(results)

            return results

        except Exception as e:
            logger.error("security_scan_failed", error=str(e))
            raise

    async def _scan_python_vulnerabilities(self) -> list[SecurityVulnerability]:
        """Scan Python dependencies for vulnerabilities"""
        vulnerabilities = []

        try:
            # Use multiple tools for comprehensive scanning
            # 1. pip-audit
            pip_audit_vulns = await self._run_pip_audit()
            vulnerabilities.extend(pip_audit_vulns)

            # 2. safety check
            safety_vulns = await self._run_safety_check()
            vulnerabilities.extend(safety_vulns)

            # 3. Custom CVE database check
            cve_vulns = await self._check_cve_database("python")
            vulnerabilities.extend(cve_vulns)

            # Deduplicate findings
            unique_vulns = self._deduplicate_vulnerabilities(vulnerabilities)

            logger.info(
                "python_scan_completed", vulnerabilities_found=len(unique_vulns)
            )

            return unique_vulns

        except Exception as e:
            logger.error("python_scan_failed", error=str(e))
            return []

    async def _scan_for_secrets(self) -> list[SecretDetection]:
        """Scan codebase for hardcoded secrets"""
        secrets_found = []

        for scan_path in self.config["scan_paths"]:
            path = Path(scan_path)
            if not path.exists():
                continue

            for file_path in path.rglob("*"):
                # Skip excluded paths
                if any(
                    exclude in str(file_path)
                    for exclude in self.config["exclude_paths"]
                ):
                    continue

                # Skip binary files
                if file_path.is_file() and self._is_text_file(file_path):
                    file_secrets = await self._scan_file_for_secrets(file_path)
                    secrets_found.extend(file_secrets)

        logger.info("secret_scan_completed", secrets_found=len(secrets_found))

        return secrets_found

    async def _scan_file_for_secrets(self, file_path: Path) -> list[SecretDetection]:
        """Scan individual file for secrets"""
        secrets = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for secret_type, patterns in self.secret_patterns.items():
                        for pattern in patterns:
                            matches = pattern.finditer(line)
                            for match in matches:
                                # Calculate confidence based on context
                                confidence = self._calculate_secret_confidence(
                                    match.group(0), line, file_path
                                )

                                if confidence > 0.5:  # Only report high confidence
                                    secret_hash = hashlib.sha256(
                                        match.group(0).encode()
                                    ).hexdigest()

                                    secrets.append(
                                        SecretDetection(
                                            file_path=str(file_path),
                                            line_number=line_num,
                                            secret_type=secret_type,
                                            pattern_matched=pattern.pattern,
                                            confidence=confidence,
                                            hash_value=secret_hash,
                                        )
                                    )

        except Exception as e:
            logger.error("file_scan_failed", file=str(file_path), error=str(e))

        return secrets

    def _calculate_secret_confidence(
        self, match: str, line: str, file_path: Path
    ) -> float:
        """Calculate confidence that a match is actually a secret"""
        confidence = 0.8  # Base confidence

        # Reduce confidence for common false positives
        if "example" in match.lower() or "test" in match.lower():
            confidence *= 0.3

        if "placeholder" in match.lower() or "your_" in match.lower():
            confidence *= 0.2

        # Increase confidence for certain file types
        if file_path.suffix in [".env", ".ini", ".cfg", ".conf"]:
            confidence *= 1.2

        # Check if it's in a test file
        if "test" in str(file_path).lower():
            confidence *= 0.5

        return min(confidence, 1.0)

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".go",
            ".rb",
            ".php",
            ".cs",
            ".swift",
            ".kt",
            ".rs",
            ".scala",
            ".txt",
            ".md",
            ".yml",
            ".yaml",
            ".json",
            ".xml",
            ".html",
            ".css",
            ".scss",
            ".conf",
            ".cfg",
            ".ini",
            ".env",
            ".sh",
            ".bash",
            ".zsh",
            ".fish",
            ".ps1",
            ".bat",
            ".cmd",
        }

        return file_path.suffix.lower() in text_extensions

    async def _generate_sbom(self) -> dict[str, Any]:
        """Generate Software Bill of Materials"""
        sbom = {
            "format": self.config["sbom_format"],
            "timestamp": datetime.utcnow().isoformat(),
            "components": [],
        }

        # Collect Python packages
        python_packages = await self._collect_python_packages()
        sbom["components"].extend(python_packages)

        # Collect JavaScript packages
        js_packages = await self._collect_javascript_packages()
        sbom["components"].extend(js_packages)

        logger.info(
            "sbom_generated", components=len(sbom["components"]), format=sbom["format"]
        )

        return {"sbom": sbom}

    def _generate_summary(
        self, results: dict[str, Any], duration: float
    ) -> dict[str, Any]:
        """Generate scan summary with risk assessment"""
        critical_vulns = [
            v
            for v in results["vulnerabilities"]
            if v.severity == SeverityLevel.CRITICAL
        ]
        high_vulns = [
            v for v in results["vulnerabilities"] if v.severity == SeverityLevel.HIGH
        ]

        total_risk_score = sum(v.risk_score() for v in results["vulnerabilities"])

        return {
            "total_vulnerabilities": len(results["vulnerabilities"]),
            "critical_vulnerabilities": len(critical_vulns),
            "high_vulnerabilities": len(high_vulns),
            "secrets_found": len(results["secrets"]),
            "unique_licenses": len(
                {lic["name"] for lic in results.get("licenses", [])}
            ),
            "total_risk_score": round(total_risk_score, 2),
            "requires_immediate_action": len(critical_vulns) > 0
            or len(results["secrets"]) > 0,
            "scan_duration_seconds": round(duration, 2),
        }

    def _generate_scan_id(self) -> str:
        """Generate unique scan ID"""
        return (
            f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
        )

    def _save_results(self, results: dict[str, Any]):
        """Save scan results to file"""
        output_dir = Path("security_scans")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{results['scan_id']}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("results_saved", file=str(output_file))

    # Placeholder methods for additional scanners
    async def _run_pip_audit(self) -> list[SecurityVulnerability]:
        """Run pip-audit scanner"""
        # Implementation would call pip-audit CLI
        return []

    async def _run_safety_check(self) -> list[SecurityVulnerability]:
        """Run safety scanner"""
        # Implementation would call safety CLI
        return []

    async def _check_cve_database(self, ecosystem: str) -> list[SecurityVulnerability]:
        """Check CVE database for vulnerabilities"""
        # Implementation would query CVE APIs
        return []

    async def _scan_javascript_vulnerabilities(self) -> list[SecurityVulnerability]:
        """Scan JavaScript dependencies"""
        # Implementation would use npm audit or similar
        return []

    async def _scan_licenses(self) -> dict[str, list[dict[str, Any]]]:
        """Scan for license compliance"""
        # Implementation would analyze package licenses
        return {"licenses": []}

    async def _collect_python_packages(self) -> list[dict[str, Any]]:
        """Collect Python package information for SBOM"""
        # Implementation would parse requirements files
        return []

    async def _collect_javascript_packages(self) -> list[dict[str, Any]]:
        """Collect JavaScript package information for SBOM"""
        # Implementation would parse package.json files
        return []

    def _deduplicate_vulnerabilities(
        self, vulns: list[SecurityVulnerability]
    ) -> list[SecurityVulnerability]:
        """Remove duplicate vulnerability findings"""
        unique_vulns = {}
        for vuln in vulns:
            key = f"{vuln.package}_{vuln.cve_id or vuln.description[:50]}"
            if (
                key not in unique_vulns
                or vuln.risk_score() > unique_vulns[key].risk_score()
            ):
                unique_vulns[key] = vuln
        return list(unique_vulns.values())


async def main():
    """Example usage"""
    scanner = SecurityScanner()
    results = await scanner.scan_complete()

    print("\n🔍 Security Scan Complete")
    print(f"   Vulnerabilities: {results['summary']['total_vulnerabilities']}")
    print(f"   Critical: {results['summary']['critical_vulnerabilities']}")
    print(f"   Secrets Found: {results['summary']['secrets_found']}")
    print(f"   Risk Score: {results['summary']['total_risk_score']}")

    if results["summary"]["requires_immediate_action"]:
        print("\n⚠️  IMMEDIATE ACTION REQUIRED!")


if __name__ == "__main__":
    asyncio.run(main())
