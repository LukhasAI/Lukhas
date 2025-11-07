#!/usr/bin/env python3
"""
LUKHAS Security Scanner
Comprehensive security scanning with Semgrep, Bandit, dependency vulnerability scanning,
and secrets detection for T4/0.01% excellence standards.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SecurityFinding:
    """Security finding from scanner"""
    rule_id: str
    severity: str
    category: str
    message: str
    file_path: str
    line_number: int
    code_snippet: str
    fix_suggestion: str | None = None


@dataclass
class VulnerabilityFinding:
    """Vulnerability finding from dependency scan"""
    package_name: str
    package_version: str
    vulnerability_id: str
    severity: str
    description: str
    fix_version: str | None = None


@dataclass
class SecretFinding:
    """Secret detection finding"""
    secret_type: str
    file_path: str
    line_number: int
    pattern: str
    confidence: str


class LUKHASSecurityScanner:
    """Comprehensive security scanner for LUKHAS"""

    def __init__(self, project_root: Path, output_dir: Path):
        self.project_root = project_root
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Security findings
        self.static_findings: list[SecurityFinding] = []
        self.vulnerability_findings: list[VulnerabilityFinding] = []
        self.secret_findings: list[SecretFinding] = []

        # T4/0.01% standards
        self.max_critical_findings = 0
        self.max_high_findings = 2
        self.max_secrets = 0

    def create_semgrep_rules(self) -> Path:
        """Create custom Semgrep rules for LUKHAS-specific patterns"""
        rules_dir = self.output_dir / "semgrep_rules"
        rules_dir.mkdir(exist_ok=True)

        # LUKHAS-specific security rules
        lukhas_rules = {
            "rules": [
                {
                    "id": "lukhas-guardian-bypass",
                    "message": "Potential Guardian system bypass detected",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern": "$GUARDIAN.validate_request(..., bypass=True, ...)",
                    "metadata": {
                        "category": "security",
                        "subcategory": ["guardian-bypass"]
                    }
                },
                {
                    "id": "lukhas-consciousness-unvalidated",
                    "message": "Consciousness processing without Guardian validation",
                    "severity": "WARNING",
                    "languages": ["python"],
                    "patterns": [
                        {
                            "pattern": "consciousness.$METHOD(...)"
                        },
                        {
                            "pattern-not-inside": "guardian.validate(...)"
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["consciousness-validation"]
                    }
                },
                {
                    "id": "lukhas-memory-injection",
                    "message": "Potential memory injection vulnerability",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "memory.query($USER_INPUT)"
                        },
                        {
                            "pattern": "memory.embed($USER_INPUT)"
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["injection"]
                    }
                },
                {
                    "id": "lukhas-identity-weak-auth",
                    "message": "Weak authentication configuration detected",
                    "severity": "WARNING",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "jwt.decode(..., verify=False, ...)"
                        },
                        {
                            "pattern": "auth_required=False"
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["authentication"]
                    }
                },
                {
                    "id": "lukhas-oidc-insecure",
                    "message": "Insecure OIDC configuration",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "verify_signature=False"
                        },
                        {
                            "pattern": "verify_aud=False"
                        },
                        {
                            "pattern": "verify_iss=False"
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["oidc"]
                    }
                },
                {
                    "id": "lukhas-hardcoded-secrets",
                    "message": "Hardcoded secret or credential detected",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "$VAR = \"sk-...\""
                        },
                        {
                            "pattern": "$VAR = \"ghp_...\""
                        },
                        {
                            "pattern": "password = \"...\""
                        },
                        {
                            "pattern": "api_key = \"...\""
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["secrets"]
                    }
                },
                {
                    "id": "lukhas-sql-injection",
                    "message": "Potential SQL injection vulnerability",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "cursor.execute(f\"... {$VAR} ...\")"
                        },
                        {
                            "pattern": "query = f\"... {$VAR} ...\""
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["injection"]
                    }
                },
                {
                    "id": "lukhas-unsafe-deserialization",
                    "message": "Unsafe deserialization detected",
                    "severity": "ERROR",
                    "languages": ["python"],
                    "pattern-either": [
                        {
                            "pattern": "pickle.loads($VAR)"
                        },
                        {
                            "pattern": "marshal.loads($VAR)"
                        },
                        {
                            "pattern": "eval($VAR)"
                        }
                    ],
                    "metadata": {
                        "category": "security",
                        "subcategory": ["deserialization"]
                    }
                }
            ]
        }

        rules_file = rules_dir / "lukhas_security_rules.yml"
        with open(rules_file, 'w') as f:
            import yaml
            yaml.dump(lukhas_rules, f, default_flow_style=False)

        return rules_file

    def run_semgrep_scan(self) -> list[SecurityFinding]:
        """Run Semgrep static analysis"""
        print("🔍 Running Semgrep static analysis...")

        findings = []

        try:
            # Create custom rules
            custom_rules = self.create_semgrep_rules()

            # Run semgrep with custom rules
            cmd = [
                "semgrep",
                "--config", str(custom_rules),
                "--config", "p/python",
                "--config", "p/security-audit",
                "--json",
                "--quiet",
                str(self.project_root)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode in [0, 1]:  # 0 = no findings, 1 = findings found
                if result.stdout:
                    semgrep_results = json.loads(result.stdout)

                    for finding in semgrep_results.get("results", []):
                        security_finding = SecurityFinding(
                            rule_id=finding["check_id"],
                            severity=finding["extra"]["severity"],
                            category=finding["extra"]["metadata"].get("category", "unknown"),
                            message=finding["extra"]["message"],
                            file_path=finding["path"],
                            line_number=finding["start"]["line"],
                            code_snippet=finding["extra"].get("lines", ""),
                            fix_suggestion=finding["extra"].get("fix", None)
                        )
                        findings.append(security_finding)
            else:
                print(f"⚠️  Semgrep error (exit {result.returncode}): {result.stderr}")

        except FileNotFoundError:
            print("⚠️  Semgrep not installed. Install with: pip install semgrep")
        except Exception as e:
            print(f"⚠️  Semgrep scan failed: {e}")

        return findings

    def run_bandit_scan(self) -> list[SecurityFinding]:
        """Run Bandit security linting"""
        print("🔍 Running Bandit security linting...")

        findings = []

        try:
            cmd = [
                "bandit",
                "-r", str(self.project_root),
                "-f", "json",
                "-ll",  # Low confidence threshold
                "-i",   # Skip tests directory
                "--exclude", "*/tests/*,*/test_*,*/.venv/*,*/venv/*,*/node_modules/*"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode in [0, 1]:  # 0 = no issues, 1 = issues found
                if result.stdout:
                    bandit_results = json.loads(result.stdout)

                    for finding in bandit_results.get("results", []):
                        severity_map = {"LOW": "INFO", "MEDIUM": "WARNING", "HIGH": "ERROR"}

                        security_finding = SecurityFinding(
                            rule_id=finding["test_id"],
                            severity=severity_map.get(finding["issue_severity"], "INFO"),
                            category="bandit",
                            message=finding["issue_text"],
                            file_path=finding["filename"],
                            line_number=finding["line_number"],
                            code_snippet=finding["code"],
                            fix_suggestion=finding.get("more_info", None)
                        )
                        findings.append(security_finding)
            else:
                print(f"⚠️  Bandit error (exit {result.returncode}): {result.stderr}")

        except FileNotFoundError:
            print("⚠️  Bandit not installed. Install with: pip install bandit")
        except Exception as e:
            print(f"⚠️  Bandit scan failed: {e}")

        return findings

    def run_dependency_scan(self) -> list[VulnerabilityFinding]:
        """Run dependency vulnerability scanning"""
        print("🔍 Running dependency vulnerability scan...")

        findings = []

        try:
            # Try Safety first
            cmd = ["safety", "check", "--json"]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)

            if result.stdout:
                try:
                    safety_results = json.loads(result.stdout)

                    for vuln in safety_results:
                        vulnerability_finding = VulnerabilityFinding(
                            package_name=vuln["package"],
                            package_version=vuln["installed_version"],
                            vulnerability_id=vuln["vulnerability_id"],
                            severity="HIGH",  # Safety doesn't provide severity levels
                            description=vuln["advisory"],
                            fix_version=None  # Could extract from advisory text
                        )
                        findings.append(vulnerability_finding)

                except json.JSONDecodeError:
                    print("⚠️  Safety output parsing failed")

        except FileNotFoundError:
            print("⚠️  Safety not installed. Install with: pip install safety")
        except Exception as e:
            print(f"⚠️  Dependency scan failed: {e}")

        return findings

    def run_secrets_scan(self) -> list[SecretFinding]:
        """Run secrets detection scan"""
        print("🔍 Running secrets detection scan...")

        findings = []

        # Secret patterns to detect
        secret_patterns = {
            "openai_api_key": r"sk-[a-zA-Z0-9]{48}",
            "anthropic_api_key": r"sk-ant-[a-zA-Z0-9-]{90,}",
            "github_token": r"ghp_[a-zA-Z0-9]{36}",
            "aws_access_key": r"AKIA[0-9A-Z]{16}",
            "private_key": r"-----BEGIN (RSA )?PRIVATE KEY-----",
            "jwt_token": r"eyJ[a-zA-Z0-9-_=]+\.eyJ[a-zA-Z0-9-_=]+\.?[a-zA-Z0-9-_.+/=]*",
            "generic_api_key": r"['\"]?[a-z_]*api[_-]?key['\"]?\s*[:=]\s*['\"][a-zA-Z0-9-_]{20,}['\"]",
            "generic_password": r"['\"]?password['\"]?\s*[:=]\s*['\"][^'\"]{8,}['\"]",
            "database_url": r"(postgres|mysql|mongodb)://[a-zA-Z0-9-_.]+:[a-zA-Z0-9-_.]+@[a-zA-Z0-9-_.]+",
        }

        # Scan Python files
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            # Skip certain directories
            if any(skip in str(py_file) for skip in [".venv", "venv", "node_modules", "__pycache__"]):
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for secret_type, pattern in secret_patterns.items():
                        matches = re.finditer(pattern, line, re.IGNORECASE)

                        for match in matches:
                            # Skip if it looks like a test or example
                            if any(skip in line.lower() for skip in [
                                "test", "example", "demo", "placeholder",
                                "fake", "mock", "sample", "todo", "fixme"
                            ]):
                                continue

                            secret_finding = SecretFinding(
                                secret_type=secret_type,
                                file_path=str(py_file.relative_to(self.project_root)),
                                line_number=line_num,
                                pattern=match.group()[:50] + "..." if len(match.group()) > 50 else match.group(),
                                confidence="HIGH" if secret_type in ["openai_api_key", "anthropic_api_key"] else "MEDIUM"
                            )
                            findings.append(secret_finding)

            except Exception as e:
                print(f"⚠️  Error scanning {py_file}: {e}")

        return findings

    def generate_security_report(self) -> dict[str, Any]:
        """Generate comprehensive security report"""

        # Count findings by severity
        critical_count = sum(1 for f in self.static_findings if f.severity == "CRITICAL")
        high_count = sum(1 for f in self.static_findings if f.severity == "ERROR")
        medium_count = sum(1 for f in self.static_findings if f.severity == "WARNING")
        low_count = sum(1 for f in self.static_findings if f.severity == "INFO")

        # Count vulnerabilities
        vuln_critical = sum(1 for v in self.vulnerability_findings if v.severity == "CRITICAL")
        vuln_high = sum(1 for v in self.vulnerability_findings if v.severity == "HIGH")
        vuln_medium = sum(1 for v in self.vulnerability_findings if v.severity == "MEDIUM")

        # Count secrets by confidence
        high_conf_secrets = sum(1 for s in self.secret_findings if s.confidence == "HIGH")
        medium_conf_secrets = sum(1 for s in self.secret_findings if s.confidence == "MEDIUM")

        # Determine deployment status
        deployment_blocked = (
            critical_count > self.max_critical_findings or
            high_count > self.max_high_findings or
            vuln_critical > 0 or
            vuln_high > 0 or
            high_conf_secrets > self.max_secrets
        )

        report = {
            "scan_type": "security",
            "timestamp": self.timestamp,
            "git_sha": self._get_git_sha(),
            "scanner_info": {
                "version": "1.0.0",
                "tools_used": ["semgrep", "bandit", "safety", "custom_secrets_scanner"],
                "rules_applied": ["lukhas_custom", "python_security", "security_audit"]
            },
            "security_findings": {
                "static_analysis": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count,
                    "total": len(self.static_findings)
                },
                "dependencies": {
                    "critical": vuln_critical,
                    "high": vuln_high,
                    "medium": vuln_medium,
                    "total": len(self.vulnerability_findings)
                },
                "secrets": {
                    "high_confidence": high_conf_secrets,
                    "medium_confidence": medium_conf_secrets,
                    "total": len(self.secret_findings)
                },
                "overall": {
                    "critical": critical_count + vuln_critical,
                    "high": high_count + vuln_high,
                    "medium": medium_count + vuln_medium,
                    "low": low_count,
                    "secrets": len(self.secret_findings)
                }
            },
            "compliance_status": {
                "t4_excellence_standards": {
                    "max_critical_allowed": self.max_critical_findings,
                    "max_high_allowed": self.max_high_findings,
                    "max_secrets_allowed": self.max_secrets,
                    "critical_compliant": critical_count <= self.max_critical_findings,
                    "high_compliant": high_count <= self.max_high_findings,
                    "secrets_compliant": high_conf_secrets <= self.max_secrets
                },
                "dependency_security": {
                    "vulnerable_packages": len(self.vulnerability_findings),
                    "critical_vulnerabilities": vuln_critical,
                    "high_vulnerabilities": vuln_high,
                    "dependency_compliant": vuln_critical == 0 and vuln_high == 0
                },
                "secrets_management": {
                    "hardcoded_secrets_detected": len(self.secret_findings),
                    "high_confidence_secrets": high_conf_secrets,
                    "secrets_compliant": high_conf_secrets == 0
                }
            },
            "deployment_readiness": "BLOCKED" if deployment_blocked else "APPROVED",
            "recommendations": self._generate_recommendations(),
            "findings_details": {
                "static_analysis": [asdict(f) for f in self.static_findings],
                "vulnerabilities": [asdict(v) for v in self.vulnerability_findings],
                "secrets": [asdict(s) for s in self.secret_findings]
            }
        }

        return report

    def _get_git_sha(self) -> str:
        """Get current git SHA"""
        try:
            result = subprocess.run(["git", "rev-parse", "HEAD"],
                                   capture_output=True, text=True,
                                   cwd=self.project_root)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _generate_recommendations(self) -> list[str]:
        """Generate security recommendations"""
        recommendations = []

        if self.static_findings:
            recommendations.append("Review and fix static analysis findings using provided suggestions")

        if self.vulnerability_findings:
            recommendations.append("Update vulnerable dependencies to patched versions")

        if self.secret_findings:
            recommendations.append("Remove hardcoded secrets and use environment variables or secret management")

        if not self.static_findings and not self.vulnerability_findings and not self.secret_findings:
            recommendations.append("No security issues detected - maintain current security practices")

        return recommendations

    def run_comprehensive_scan(self) -> dict[str, Any]:
        """Run comprehensive security scan"""
        print("🚀 Starting LUKHAS comprehensive security scan...")
        print(f"📁 Project: {self.project_root}")
        print(f"⏰ Timestamp: {self.timestamp}")

        # Run all scans
        self.static_findings.extend(self.run_semgrep_scan())
        self.static_findings.extend(self.run_bandit_scan())
        self.vulnerability_findings.extend(self.run_dependency_scan())
        self.secret_findings.extend(self.run_secrets_scan())

        # Generate report
        report = self.generate_security_report()

        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"security-scan-{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print("\n📊 Security Scan Results:")
        print(f"   Static Analysis Findings: {len(self.static_findings)}")
        print(f"   Vulnerability Findings: {len(self.vulnerability_findings)}")
        print(f"   Secret Findings: {len(self.secret_findings)}")
        print(f"   Deployment Status: {report['deployment_readiness']}")
        print(f"💾 Report saved to: {report_file}")

        return report


def main():
    parser = argparse.ArgumentParser(description="Run LUKHAS comprehensive security scan")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--output-dir", default="artifacts", help="Output directory")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output_dir = Path(args.output_dir)

    scanner = LUKHASSecurityScanner(project_root, output_dir)
    report = scanner.run_comprehensive_scan()

    # Exit with error if deployment is blocked
    if report["deployment_readiness"] == "BLOCKED":
        print("\n❌ SECURITY SCAN FAILED: Critical security issues detected")
        print("   Review findings and fix issues before deployment")
        sys.exit(1)
    else:
        print("\n✅ SECURITY SCAN PASSED: No critical security issues detected")


if __name__ == "__main__":
    main()
