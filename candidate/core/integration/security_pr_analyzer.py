#!/usr/bin/env python3
"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

ΛBot Security & PR Analyzer
===========================
Comprehensive security scanning and pull request analysis for GitHub repositories

Created: 2025-06-29
Status: ACTIVE DEPLOYMENT ✅
"""

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from safe_subprocess_executor import safe_subprocess_run


@dataclass
class SecurityIssue:
    """Security issue found in repository"""

    type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    file: str
    line: int
    description: str
    recommendation: str


@dataclass
class PRAnalysis:
    """Pull request analysis result"""

    number: int
    title: str
    state: str
    author: str
    created_at: str
    security_risk: str  # LOW, MEDIUM, HIGH
    code_quality_score: float
    issues_found: list[str]


class SecurityScanner:
    """Advanced security scanner for repositories"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update(
                {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )

    def scan_repository(self, repo_path: str, repo_info: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Comprehensive security scan of repository"""

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo_path": repo_path,
            "security_issues": [],
            "dependency_vulnerabilities": [],
            "secrets_found": [],
            "permission_issues": [],
            "github_security_alerts": [],
            "code_quality_issues": [],
            "overall_security_score": 0,
            "risk_level": "UNKNOWN",
        }

        try:
            print(f"🔒 Starting comprehensive security scan of {repo_path}...")

            # 1. Scan for hardcoded secrets
            secrets = self._scan_secrets(repo_path)
            results["secrets_found"] = secrets

            # 2. Check dependencies for vulnerabilities
            dependencies = self._scan_dependencies(repo_path)
            results["dependency_vulnerabilities"] = dependencies

            # 3. Check file permissions
            permissions = self._check_permissions(repo_path)
            results["permission_issues"] = permissions

            # 4. GitHub security alerts (if repo_info provided)
            if repo_info and self.github_token:
                github_alerts = self._get_github_security_alerts(repo_info)
                results["github_security_alerts"] = github_alerts

            # 5. Code quality issues
            code_quality = self._scan_code_quality(repo_path)
            results["code_quality_issues"] = code_quality

            # 6. Calculate overall security score
            score, risk = self._calculate_security_score(results)
            results["overall_security_score"] = score
            results["risk_level"] = risk

            print(f"✅ Security scan complete. Score: {score}/100, Risk: {risk}")

        except Exception as e:
            print(f"❌ Security scan failed: {e}")
            results["error"] = str(e)

        return results

    def _scan_secrets(self, repo_path: str) -> list[SecurityIssue]:
        """Scan for hardcoded secrets and credentials"""
        secrets = []

        # Patterns for different types of secrets
        secret_patterns = [
            (
                r'password\s*=\s*["\']([^"\']{8,})["\']',
                "Hardcoded Password",
                "HIGH",
            ),
            (r'api[_-]?key\s*=\s*["\']([^"\']{20,})["\']', "API Key", "HIGH"),
            (
                r'secret[_-]?key\s*=\s*["\']([^"\']{20,})["\']',
                "Secret Key",
                "HIGH",
            ),
            (
                r'github[_-]?token\s*=\s*["\']([^"\']{30,})["\']',
                "GitHub Token",
                "CRITICAL",
            ),
            (
                r'aws[_-]?access[_-]?key\s*=\s*["\']([^"\']{20,})["\']',
                "AWS Access Key",
                "CRITICAL",
            ),
            (
                r'openai[_-]?api[_-]?key\s*=\s*["\']([^"\']{30,})["\']',
                "OpenAI API Key",
                "HIGH",
            ),
            (
                r'anthropic[_-]?api[_-]?key\s*=\s*["\']([^"\']{30,})["\']',
                "Anthropic API Key",
                "HIGH",
            ),
            (
                r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
                "Private Key",
                "CRITICAL",
            ),
            (r"sk-[a-zA-Z0-9]{48}", "OpenAI Secret Key", "CRITICAL"),
            (
                r"xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}",
                "Slack Bot Token",
                "HIGH",
            ),
        ]

        for root, dirs, files in os.walk(repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules", ".venv", "venv"]]

            for file in files:
                # Skip binary files and common non-code files
                if file.endswith((".pyc", ".jpg", ".png", ".gif", ".pdf", ".zip", ".tar.gz")):
                    continue

                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        for pattern, desc, severity in secret_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                secrets.append(
                                    SecurityIssue(
                                        type="SECRET",
                                        severity=severity,
                                        file=str(file_path.relative_to(repo_path)),
                                        line=i,
                                        description=f"{desc} found in code",
                                        recommendation=f"Remove {desc.lower()} and use environment variables or secure storage",
                                    )
                                )

                except Exception:
                    continue

        return secrets

    def _scan_dependencies(self, repo_path: str) -> list[SecurityIssue]:
        """Scan dependencies for known vulnerabilities"""
        vulnerabilities = []

        # Check Python dependencies
        requirements_files = [
            Path(repo_path) / "requirements.txt",
            Path(repo_path) / "requirements-compatible.txt",
            Path(repo_path) / "pyproject.toml",
        ]

        for req_file in requirements_files:
            if req_file.exists():
                try:
                    # Try using safety for Python dependencies
                    result = safe_subprocess_run(
                        [
                            "python",
                            "-m",
                            "safety",
                            "check",
                            "-r",
                            str(req_file),
                            "--json",
                        ],
                        timeout=60,
                    )

                    if result["success"] and result["stdout"]:
                        try:
                            safety_data = json.loads(result["stdout"])
                            for vuln in safety_data:
                                vulnerabilities.append(
                                    SecurityIssue(
                                        type="DEPENDENCY",
                                        severity=(
                                            "HIGH" if vuln.get("severity", "medium").lower() == "high" else "MEDIUM"
                                        ),
                                        file=str(req_file.relative_to(repo_path)),
                                        line=0,
                                        description=f"Vulnerable dependency: {vuln.get('package_name')} {vuln.get('installed_version')}",
                                        recommendation=f"Update to version {vuln.get('safe_version', 'latest')}",
                                    )
                                )
                        except json.JSONDecodeError:
                            # Safety might output plain text
                            if "vulnerabilities found" in result["stdout"]:
                                vulnerabilities.append(
                                    SecurityIssue(
                                        type="DEPENDENCY",
                                        severity="MEDIUM",
                                        file=str(req_file.relative_to(repo_path)),
                                        line=0,
                                        description="Dependency vulnerabilities found",
                                        recommendation="Run 'safety check' for details and update vulnerable packages",
                                    )
                                )

                except Exception as e:
                    print(f"⚠️ Could not scan {req_file} with safety: {e}")

        # Check package.json for Node.js dependencies
        package_json = Path(repo_path) / "package.json"
        if package_json.exists():
            try:
                result = safe_subprocess_run(["npm", "audit", "--json"], cwd=repo_path, timeout=60)

                if result["success"] and result["stdout"]:
                    try:
                        audit_data = json.loads(result["stdout"])
                        for vuln in audit_data.get("vulnerabilities", {}).values():
                            severity = vuln.get("severity", "medium").upper()
                            vulnerabilities.append(
                                SecurityIssue(
                                    type="DEPENDENCY",
                                    severity=severity,
                                    file="package.json",
                                    line=0,
                                    description=f"Vulnerable npm package: {vuln.get('module_name')}",
                                    recommendation="Run 'npm audit fix' to resolve",
                                )
                            )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"⚠️ Could not scan package.json: {e}")

        return vulnerabilities

    def _check_permissions(self, repo_path: str) -> list[SecurityIssue]:
        """Check for insecure file permissions"""
        permission_issues = []

        sensitive_patterns = [
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",
            ".env",
            ".secret",
            "id_rsa",
            "id_dsa",
            "private*",
            "secret*",
        ]

        for root, _dirs, files in os.walk(repo_path):
            for file in files:
                file_path = Path(root) / file

                # Check if file matches sensitive patterns
                is_sensitive = any(
                    file.lower().endswith(pattern.replace("*", "")) or pattern.replace("*", "") in file.lower()
                    for pattern in sensitive_patterns
                )

                if is_sensitive:
                    try:
                        stat = file_path.stat()
                        # Check if readable by group or others
                        if stat.st_mode & 0o044:
                            permission_issues.append(
                                SecurityIssue(
                                    type="PERMISSION",
                                    severity="HIGH",
                                    file=str(file_path.relative_to(repo_path)),
                                    line=0,
                                    description="Sensitive file readable by others",
                                    recommendation="Change permissions to 600 (owner read/write only)",
                                )
                            )
                    except Exception:
                        continue

        return permission_issues

    def _get_github_security_alerts(self, repo_info: dict[str, Any]) -> list[SecurityIssue]:
        """Get GitHub security alerts for repository"""
        alerts = []

        if not self.github_token:
            return alerts

        try:
            # Get Dependabot alerts
            url = f"https://api.github.com/repos/{repo_info['full_name']}/dependabot/alerts"
            response = self.session.get(url)

            if response.status_code == 200:
                dependabot_alerts = response.json()
                for alert in dependabot_alerts:
                    if alert["state"] == "open":
                        severity = alert["security_advisory"]["severity"].upper()
                        alerts.append(
                            SecurityIssue(
                                type="GITHUB_ALERT",
                                severity=severity,
                                file=alert["dependency"]["manifest_path"],
                                line=0,
                                description=f"GitHub Dependabot Alert: {alert['security_advisory']['summary']}",
                                recommendation="Update the vulnerable dependency",
                            )
                        )

            # Get Code scanning alerts
            url = f"https://api.github.com/repos/{repo_info['full_name']}/code-scanning/alerts"
            response = self.session.get(url)

            if response.status_code == 200:
                code_alerts = response.json()
                for alert in code_alerts:
                    if alert["state"] == "open":
                        severity = (
                            alert["rule"]["security_severity_level"].upper()
                            if alert["rule"].get("security_severity_level")
                            else "MEDIUM"
                        )
                        alerts.append(
                            SecurityIssue(
                                type="CODE_SCANNING",
                                severity=severity,
                                file=alert["most_recent_instance"]["location"]["path"],
                                line=alert["most_recent_instance"]["location"]["start_line"],
                                description=f"Code Scanning Alert: {alert['rule']['description']}",
                                recommendation="Review and fix the identified security issue",
                            )
                        )

        except Exception as e:
            print(f"⚠️ Could not fetch GitHub security alerts: {e}")

        return alerts

    def _scan_code_quality(self, repo_path: str) -> list[SecurityIssue]:
        """Scan for code quality issues that might affect security"""
        issues = []

        # Python-specific checks
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in [".git", "__pycache__", "node_modules"]]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        lines = content.split("\n")

                        for i, line in enumerate(lines, 1):
                            # Check for dangerous functions
                            if re.search(r"\beval\s*\(", line):
                                issues.append(
                                    SecurityIssue(
                                        type="CODE_QUALITY",
                                        severity="HIGH",
                                        file=str(file_path.relative_to(repo_path)),
                                        line=i,
                                        description="Use of eval() function (code injection risk)",
                                        recommendation="Replace eval() with safer alternatives like ast.literal_eval()",
                                    )
                                )

                            if re.search(r"\bexec\s*\(", line):
                                issues.append(
                                    SecurityIssue(
                                        type="CODE_QUALITY",
                                        severity="HIGH",
                                        file=str(file_path.relative_to(repo_path)),
                                        line=i,
                                        description="Use of exec() function (code injection risk)",
                                        recommendation="Avoid exec() or use safer alternatives",
                                    )
                                )

                            # Check for SQL injection patterns
                            if re.search(r"execute\s*\([^)]*%\s*[^)]*\)", line):
                                issues.append(
                                    SecurityIssue(
                                        type="CODE_QUALITY",
                                        severity="MEDIUM",
                                        file=str(file_path.relative_to(repo_path)),
                                        line=i,
                                        description="Potential SQL injection vulnerability",
                                        recommendation="Use parameterized queries instead of string formatting",
                                    )
                                )

                    except Exception:
                        continue

        return issues

    def _calculate_security_score(self, results: dict[str, Any]) -> tuple:
        """Calculate overall security score and risk level"""
        score = 100

        # Deduct points for issues
        for secret in results["secrets_found"]:
            if secret.severity == "CRITICAL":
                score -= 25
            elif secret.severity == "HIGH":
                score -= 15
            elif secret.severity == "MEDIUM":
                score -= 10
            else:
                score -= 5

        for vuln in results["dependency_vulnerabilities"]:
            if vuln.severity == "CRITICAL":
                score -= 20
            elif vuln.severity == "HIGH":
                score -= 15
            elif vuln.severity == "MEDIUM":
                score -= 10
            else:
                score -= 5

        for _perm in results["permission_issues"]:
            score -= 10

        for alert in results["github_security_alerts"]:
            if alert.severity == "CRITICAL":
                score -= 20
            elif alert.severity == "HIGH":
                score -= 15
            else:
                score -= 10

        for issue in results["code_quality_issues"]:
            if issue.severity == "HIGH":
                score -= 10
            else:
                score -= 5

        score = max(0, score)

        # Determine risk level
        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        elif score >= 50:
            risk = "HIGH"
        else:
            risk = "CRITICAL"

        return score, risk


class PRAnalyzer:
    """Analyze pull requests for security and quality issues"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update(
                {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )

    def analyze_repository_prs(self, repo_info: dict[str, Any], days_back: int = 30) -> dict[str, Any]:
        """Analyze pull requests in repository"""

        if not self.github_token:
            return {"error": "GitHub token required for PR analysis"}

        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repository": repo_info["full_name"],
            "analysis_period_days": days_back,
            "total_prs": 0,
            "open_prs": 0,
            "high_risk_prs": 0,
            "pr_analyses": [],
            "recommendations": [],
        }

        try:
            # Get recent PRs
            since_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
            url = f"https://api.github.com/repos/{repo_info['full_name']}/pulls"

            params = {"state": "all", "sort": "updated", "per_page": 100}

            response = self.session.get(url, params=params)

            if response.status_code != 200:
                return {"error": f"Failed to fetch PRs: {response.status_code}"}

            prs = response.json()
            recent_prs = [pr for pr in prs if pr["updated_at"] >= since_date]

            results["total_prs"] = len(recent_prs)
            results["open_prs"] = len([pr for pr in recent_prs if pr["state"] == "open"])

            # Analyze each PR
            for pr in recent_prs:
                analysis = self._analyze_single_pr(repo_info["full_name"], pr)
                results["pr_analyses"].append(analysis)

                if analysis.security_risk == "HIGH":
                    results["high_risk_prs"] += 1

            # Generate recommendations
            results["recommendations"] = self._generate_pr_recommendations(results)

        except Exception as e:
            results["error"] = str(e)

        return results

    def _analyze_single_pr(self, repo_full_name: str, pr: dict[str, Any]) -> PRAnalysis:
        """Analyze a single pull request"""

        analysis = PRAnalysis(
            number=pr["number"],
            title=pr["title"],
            state=pr["state"],
            author=pr["user"]["login"],
            created_at=pr["created_at"],
            security_risk="LOW",
            code_quality_score=85.0,
            issues_found=[],
        )

        try:
            # Get PR files
            files_url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr['number']}/files"
            response = self.session.get(files_url)

            if response.status_code == 200:
                files = response.json()

                # Analyze changed files
                for file in files:
                    # Check for sensitive file changes
                    if any(
                        pattern in file["filename"].lower()
                        for pattern in [
                            ".env",
                            "config",
                            "secret",
                            "key",
                            "password",
                            "token",
                        ]
                    ):
                        analysis.issues_found.append(f"Changes to sensitive file: {file['filename']}")
                        analysis.security_risk = "HIGH"

                    # Check patch content for security issues
                    if "patch" in file:
                        patch = file["patch"]

                        # Look for added secrets
                        if re.search(
                            r'\+.*(?:password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
                            patch,
                            re.IGNORECASE,
                        ):
                            analysis.issues_found.append("Potential secret in code changes")
                            analysis.security_risk = "HIGH"

                        # Look for dangerous functions
                        if re.search(r"\+.*\b(?:eval|exec)\s*\(", patch):
                            analysis.issues_found.append("Use of dangerous functions (eval/exec)")
                            analysis.security_risk = (
                                "MEDIUM" if analysis.security_risk == "LOW" else analysis.security_risk
                            )

                        # Check for SQL injection patterns
                        if re.search(r"\+.*execute\s*\([^)]*%[^)]*\)", patch):
                            analysis.issues_found.append("Potential SQL injection pattern")
                            analysis.security_risk = (
                                "MEDIUM" if analysis.security_risk == "LOW" else analysis.security_risk
                            )

                # Calculate code quality score
                analysis.code_quality_score = self._calculate_pr_quality_score(files, analysis.issues_found)

        except Exception as e:
            analysis.issues_found.append(f"Analysis error: {e!s}")

        return analysis

    def _calculate_pr_quality_score(self, files: list[dict], issues: list[str]) -> float:
        """Calculate code quality score for PR"""
        score = 100.0

        # Deduct for issues found
        score -= len(issues) * 10

        # Check file patterns
        for file in files:
            if file["additions"] > 500:  # Very large changes
                score -= 5

            if file.get("deletions", 0) > file.get("additions", 0) * 2:  # Mostly deletions
                score += 5  # Good, removing code

        return max(0.0, min(100.0, score))

    def _generate_pr_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on PR analysis"""
        recommendations = []

        if results["high_risk_prs"] > 0:
            recommendations.append(f"🚨 {results['high_risk_prs']} high-risk PRs require immediate security review")

        if results["open_prs"] > 10:
            recommendations.append("📊 Consider reducing the number of open PRs to improve review quality")

        # Analyze PR patterns
        pr_analyses = results["pr_analyses"]
        avg_quality = sum(pr.code_quality_score for pr in pr_analyses) / len(pr_analyses) if pr_analyses else 0

        if avg_quality < 70:
            recommendations.append("📈 Consider implementing stricter code review processes")

        secret_issues = sum(1 for pr in pr_analyses if any("secret" in issue.lower() for issue in pr.issues_found))
        if secret_issues > 0:
            recommendations.append("🔐 Implement pre-commit hooks to prevent secrets in code")

        return recommendations


def main():
    """Main function for security and PR analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="ΛBot Security & PR Analyzer")
    parser.add_argument("--repo", required=True, help="Repository URL or path")
    parser.add_argument("--security-only", action="store_true", help="Run security scan only")
    parser.add_argument("--pr-only", action="store_true", help="Run PR analysis only")
    parser.add_argument("--days", type=int, default=30, help="Days back for PR analysis")

    args = parser.parse_args()

    print("🔒 ΛBot Security & PR Analyzer")
    print("=" * 50)

    # Initialize scanners
    security_scanner = SecurityScanner()
    pr_analyzer = PRAnalyzer()

    # Extract repo info
    if args.repo.startswith("http"):
        # GitHub URL
        repo_parts = args.repo.split("/")
        repo_info = {
            "full_name": f"{repo_parts[-2]}/{repo_parts[-1].replace('.git', '')}",
            "html_url": args.repo,
        }
        repo_path = f"./{repo_parts[-1].replace('.git', '')}"
    else:
        # Local path
        repo_path = args.repo
        repo_info = None

    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": repo_info["full_name"] if repo_info else repo_path,
    }

    # Run security scan
    if not args.pr_only:
        print("\n🔍 Running security scan...")
        security_results = security_scanner.scan_repository(repo_path, repo_info)
        results["security"] = security_results

        print("\n📊 Security Results:")
        print(f"   Score: {security_results['overall_security_score']}/100")
        print(f"   Risk Level: {security_results['risk_level']}")
        print(f"   Secrets Found: {len(security_results['secrets_found'])}")
        print(f"   Vulnerabilities: {len(security_results['dependency_vulnerabilities'])}")

    # Run PR analysis
    if not args.security_only and repo_info:
        print(f"\n📋 Running PR analysis ({args.days} days)...")
        pr_results = pr_analyzer.analyze_repository_prs(repo_info, args.days)
        results["pull_requests"] = pr_results

        if "error" not in pr_results:
            print("\n📊 PR Results:")
            print(f"   Total PRs: {pr_results['total_prs']}")
            print(f"   Open PRs: {pr_results['open_prs']}")
            print(f"   High Risk PRs: {pr_results['high_risk_prs']}")

    # Save results
    output_file = f"security_pr_analysis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
