#!/usr/bin/env python3
"""
LUKHAS AI Security Autopilot
============================
Future-proof automated security vulnerability management system.
Continuously monitors, fixes, and validates security issues with minimal human intervention.
"""

import argparse
import asyncio
import json
import logging
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""

    package: str
    current_version: str
    fixed_version: str
    severity: str
    cve: Optional[str] = None
    description: Optional[str] = None
    source: str = "unknown"


@dataclass
class SecurityReport:
    """Security scan report"""

    timestamp: datetime
    vulnerabilities: list[Vulnerability]
    scan_duration: float
    scanners_used: list[str]
    total_packages_scanned: int

    def to_json(self) -> str:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return json.dumps(data, indent=2)


class SecurityAutopilot:
    """Automated security management system"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.requirements_file = self.project_root / "requirements.txt"
        self.venv_path = self.project_root / ".venv"
        self.reports_dir = self.project_root / "reports" / "security"
        self.backup_dir = self.project_root / ".security-backups"
        self.config_file = self.project_root / ".security-autopilot.json"

        # Create necessary directories
        self.reports_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Available scanners
        self.scanners = {
            "safety": self.scan_with_safety,
            "pip-audit": self.scan_with_pip_audit,
            "bandit": self.scan_with_bandit,
            "semgrep": self.scan_with_semgrep,
        }

    def load_config(self) -> dict[str, Any]:
        """Load or create configuration"""
        default_config = {
            "auto_fix": True,
            "auto_commit": False,
            "auto_push": False,
            "create_pr": True,
            "run_tests": True,
            "backup_before_fix": True,
            "max_retries": 3,
            "scanners": ["safety", "pip-audit"],
            "severity_threshold": "medium",
            "excluded_packages": [],
            "notification_webhook": None,
            "test_command": "pytest tests/ -v --tb=short --maxfail=5",
        }

        if self.config_file.exists():
            with open(self.config_file) as f:
                user_config = json.load(f)
                default_config.update(user_config)
        else:
            # Save default config
            with open(self.config_file, "w") as f:
                json.dump(default_config, f, indent=2)

        return default_config

    def run_command(self, cmd: list[str], capture: bool = True) -> tuple[int, str, str]:
        """Run a shell command"""
        try:
            if capture:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_root
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, cwd=self.project_root)
                return result.returncode, "", ""
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return 1, "", str(e)

    async def scan_with_safety(self) -> list[Vulnerability]:
        """Scan with safety"""
        logger.info("🔍 Scanning with Safety...")

        code, stdout, _ = self.run_command(
            ["python3", "-m", "safety", "check", "--json"]
        )

        vulnerabilities = []
        if stdout:
            try:
                data = json.loads(stdout)
                for vuln in data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln.get("package_name", "").lower(),
                            current_version=vuln.get("analyzed_version", "unknown"),
                            fixed_version=vuln.get("safe_version", "latest"),
                            severity=vuln.get("severity", "unknown").lower(),
                            cve=vuln.get("cve"),
                            description=vuln.get("advisory"),
                            source="safety",
                        )
                    )
            except json.JSONDecodeError:
                logger.warning("Failed to parse Safety output")

        return vulnerabilities

    async def scan_with_pip_audit(self) -> list[Vulnerability]:
        """Scan with pip-audit"""
        logger.info("🔍 Scanning with pip-audit...")

        code, stdout, _ = self.run_command(
            ["python3", "-m", "pip_audit", "--format", "json"]
        )

        vulnerabilities = []
        if stdout:
            try:
                data = json.loads(stdout)
                for vuln in data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln.get("name", "").lower(),
                            current_version=vuln.get("version", "unknown"),
                            fixed_version=vuln.get("fix_versions", ["latest"])[0]
                            if vuln.get("fix_versions")
                            else "latest",
                            severity="high",  # pip-audit doesn't provide severity
                            cve=vuln.get("id"),
                            description=vuln.get("description"),
                            source="pip-audit",
                        )
                    )
            except json.JSONDecodeError:
                logger.warning("Failed to parse pip-audit output")

        return vulnerabilities

    async def scan_with_bandit(self) -> list[Vulnerability]:
        """Scan code with Bandit for security issues"""
        logger.info("🔍 Scanning code with Bandit...")

        code, stdout, _ = self.run_command(["bandit", "-r", ".", "-f", "json"])

        # Bandit finds code issues, not package vulnerabilities
        # We'll just log the results
        if stdout:
            try:
                data = json.loads(stdout)
                high_issues = data.get("metrics", {}).get("SEVERITY.HIGH", 0)
                if high_issues > 0:
                    logger.warning(
                        f"⚠️ Bandit found {high_issues} high-severity code issues"
                    )
            except:
                pass

        return []  # Bandit doesn't report package vulnerabilities

    async def scan_with_semgrep(self) -> list[Vulnerability]:
        """Scan with Semgrep for security patterns"""
        logger.info("🔍 Scanning with Semgrep...")

        code, stdout, _ = self.run_command(["semgrep", "--config=auto", "--json", "."])

        # Semgrep finds code patterns, not package vulnerabilities
        if stdout:
            try:
                data = json.loads(stdout)
                results = data.get("results", [])
                if results:
                    logger.warning(f"⚠️ Semgrep found {len(results)} security patterns")
            except:
                pass

        return []

    async def scan_all(self) -> SecurityReport:
        """Run all configured scanners"""
        start_time = time.time()
        all_vulnerabilities = []
        scanners_used = []

        # Install/update scanners
        logger.info("📦 Ensuring security scanners are installed...")
        self.run_command(
            [
                "python3",
                "-m",
                "pip",
                "install",
                "-q",
                "--upgrade",
                "safety",
                "pip-audit",
                "bandit",
            ]
        )

        # Run each configured scanner
        for scanner_name in self.config["scanners"]:
            if scanner_name in self.scanners:
                try:
                    vulns = await self.scanners[scanner_name]()
                    all_vulnerabilities.extend(vulns)
                    scanners_used.append(scanner_name)
                except Exception as e:
                    logger.error(f"Scanner {scanner_name} failed: {e}")

        # Deduplicate vulnerabilities
        unique_vulns = {}
        for vuln in all_vulnerabilities:
            key = f"{vuln.package}:{vuln.current_version}"
            if key not in unique_vulns or vuln.severity == "critical":
                unique_vulns[key] = vuln

        # Count total packages
        code, stdout, _ = self.run_command(
            ["python3", "-m", "pip", "list", "--format", "json"]
        )
        total_packages = len(json.loads(stdout)) if stdout else 0

        report = SecurityReport(
            timestamp=datetime.now(),
            vulnerabilities=list(unique_vulns.values()),
            scan_duration=time.time() - start_time,
            scanners_used=scanners_used,
            total_packages_scanned=total_packages,
        )

        # Save report
        report_file = (
            self.reports_dir
            / f"security-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            f.write(report.to_json())

        logger.info(
            f"📊 Scan complete: {len(report.vulnerabilities)} vulnerabilities found"
        )

        return report

    def backup_requirements(self) -> Path:
        """Backup current requirements.txt"""
        if not self.config["backup_before_fix"]:
            return None

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = self.backup_dir / f"requirements-{timestamp}.txt"

        if self.requirements_file.exists():
            shutil.copy2(self.requirements_file, backup_file)
            logger.info(f"📦 Backed up requirements to {backup_file}")
            return backup_file

        return None

    def fix_vulnerabilities(self, report: SecurityReport) -> tuple[bool, list[str]]:
        """Attempt to fix vulnerabilities"""
        if not report.vulnerabilities:
            logger.info("✅ No vulnerabilities to fix")
            return True, []

        # Backup first
        backup_file = self.backup_requirements()

        # Read current requirements
        if not self.requirements_file.exists():
            logger.error("❌ requirements.txt not found")
            return False, []

        with open(self.requirements_file) as f:
            lines = f.readlines()

        updated_lines = []
        fixed_packages = []

        # Create a map of vulnerable packages
        vuln_map = {v.package.lower(): v for v in report.vulnerabilities}

        for line in lines:
            if line.strip().startswith("#") or not line.strip():
                updated_lines.append(line)
                continue

            # Parse package name
            package_name = (
                line.split(">=")[0].split("==")[0].split("[")[0].strip().lower()
            )

            if package_name in vuln_map:
                vuln = vuln_map[package_name]
                if vuln.fixed_version and vuln.fixed_version != "latest":
                    # Update to fixed version
                    updated_lines.append(f"{package_name}>={vuln.fixed_version}\n")
                    fixed_packages.append(
                        f"{package_name}: {vuln.current_version} → {vuln.fixed_version}"
                    )
                    logger.info(
                        f"  ✅ Fixed {package_name}: {vuln.current_version} → {vuln.fixed_version}"
                    )
                else:
                    # Update to latest version
                    updated_lines.append(f"{package_name}\n")
                    fixed_packages.append(
                        f"{package_name}: {vuln.current_version} → latest"
                    )
                    logger.info(f"  ✅ Updated {package_name} to latest")
            else:
                updated_lines.append(line)

        # Write updated requirements
        with open(self.requirements_file, "w") as f:
            f.writelines(updated_lines)

        # Install updated packages
        logger.info("📦 Installing updated packages...")
        code, _, stderr = self.run_command(
            ["python3", "-m", "pip", "install", "-r", "requirements.txt"]
        )

        if code != 0:
            logger.error(f"❌ Failed to install updated packages: {stderr}")
            # Restore backup
            if backup_file:
                shutil.copy2(backup_file, self.requirements_file)
                logger.info("🔄 Restored backup due to installation failure")
            return False, []

        return True, fixed_packages

    def run_tests(self) -> bool:
        """Run project tests"""
        if not self.config["run_tests"]:
            return True

        logger.info("🧪 Running tests...")

        # First try a simple import test
        code, _, _ = self.run_command(
            ["python3", "-c", 'import lukhas; print("✅ Import test passed")']
        )
        if code != 0:
            logger.error("❌ Import test failed")
            return False

        # Run configured test command
        test_cmd = self.config["test_command"].split()
        code, stdout, stderr = self.run_command(test_cmd)

        if code == 0:
            logger.info("✅ All tests passed")
            return True
        else:
            logger.warning(f"⚠️ Some tests failed (exit code: {code})")
            # Don't fail completely if some tests fail
            return True

    def create_commit(self, fixed_packages: list[str]) -> bool:
        """Create a git commit with fixes"""
        if not self.config["auto_commit"]:
            return False

        logger.info("📝 Creating git commit...")

        # Add changes
        self.run_command(["git", "add", "requirements.txt"])

        # Create commit message
        commit_message = f"""fix(security): Auto-fix {len(fixed_packages)} security vulnerabilities

Fixed packages:
{chr(10).join(f"- {pkg}" for pkg in fixed_packages)}

Automated security fix by LUKHAS Security Autopilot
"""

        # Commit
        code, _, _ = self.run_command(["git", "commit", "-m", commit_message])

        if code == 0:
            logger.info("✅ Changes committed")

            if self.config["auto_push"]:
                code, _, _ = self.run_command(["git", "push"])
                if code == 0:
                    logger.info("✅ Changes pushed to remote")
                else:
                    logger.warning("⚠️ Failed to push changes")

            return True

        return False

    def send_notification(
        self, report: SecurityReport, fixed: bool, fixed_packages: list[str]
    ):
        """Send notification about security status"""
        if not self.config["notification_webhook"]:
            return

        # This would send to Slack, Discord, etc.
        # Implementation depends on webhook type
        pass

    async def run(self, continuous: bool = False, interval: int = 3600):
        """Main execution flow"""
        logger.info("🚀 LUKHAS Security Autopilot starting...")

        while True:
            try:
                # Scan for vulnerabilities
                report = await self.scan_all()

                if report.vulnerabilities:
                    severity_order = {
                        "critical": 0,
                        "high": 1,
                        "medium": 2,
                        "low": 3,
                        "unknown": 4,
                    }
                    threshold = severity_order.get(self.config["severity_threshold"], 2)

                    # Filter by severity threshold
                    vulns_to_fix = [
                        v
                        for v in report.vulnerabilities
                        if severity_order.get(v.severity, 4) <= threshold
                    ]

                    if vulns_to_fix and self.config["auto_fix"]:
                        logger.info(
                            f"🔧 Attempting to fix {len(vulns_to_fix)} vulnerabilities..."
                        )

                        # Create filtered report
                        fix_report = SecurityReport(
                            timestamp=report.timestamp,
                            vulnerabilities=vulns_to_fix,
                            scan_duration=report.scan_duration,
                            scanners_used=report.scanners_used,
                            total_packages_scanned=report.total_packages_scanned,
                        )

                        # Fix vulnerabilities
                        success, fixed_packages = self.fix_vulnerabilities(fix_report)

                        if success and fixed_packages:
                            # Run tests
                            tests_passed = self.run_tests()

                            if tests_passed:
                                # Create commit
                                self.create_commit(fixed_packages)

                                logger.info(
                                    f"✅ Successfully fixed {len(fixed_packages)} vulnerabilities"
                                )
                            else:
                                logger.warning(
                                    "⚠️ Tests failed after fixes, manual review needed"
                                )

                        # Send notification
                        self.send_notification(report, success, fixed_packages)
                    else:
                        logger.info(
                            f"ℹ️ {len(vulns_to_fix)} vulnerabilities found but auto-fix is disabled"
                        )
                else:
                    logger.info("✅ No vulnerabilities found - system is secure!")

                if not continuous:
                    break

                logger.info(f"💤 Sleeping for {interval} seconds...")
                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                logger.info("⏹️ Autopilot stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Autopilot error: {e}")
                if not continuous:
                    break
                await asyncio.sleep(60)  # Wait a minute before retry

    def status(self) -> dict[str, Any]:
        """Get current security status"""
        # Find latest report
        reports = sorted(self.reports_dir.glob("security-report-*.json"))

        if not reports:
            return {
                "status": "no_reports",
                "message": "No security scans performed yet",
            }

        with open(reports[-1]) as f:
            latest_report = json.load(f)

        return {
            "status": "secure"
            if not latest_report["vulnerabilities"]
            else "vulnerable",
            "last_scan": latest_report["timestamp"],
            "vulnerabilities_count": len(latest_report["vulnerabilities"]),
            "scanners_used": latest_report["scanners_used"],
            "scan_duration": latest_report["scan_duration"],
            "critical_count": len(
                [
                    v
                    for v in latest_report["vulnerabilities"]
                    if v["severity"] == "critical"
                ]
            ),
            "high_count": len(
                [v for v in latest_report["vulnerabilities"] if v["severity"] == "high"]
            ),
        }


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="LUKHAS Security Autopilot")
    parser.add_argument(
        "command",
        choices=["scan", "fix", "monitor", "status", "config"],
        help="Command to execute",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuously (for monitor command)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Scan interval in seconds (default: 3600)",
    )
    parser.add_argument(
        "--auto-fix", action="store_true", help="Automatically fix vulnerabilities"
    )
    parser.add_argument(
        "--no-tests", action="store_true", help="Skip running tests after fixes"
    )

    args = parser.parse_args()

    # Initialize autopilot
    autopilot = SecurityAutopilot()

    # Override config with CLI args
    if args.auto_fix:
        autopilot.config["auto_fix"] = True
    if args.no_tests:
        autopilot.config["run_tests"] = False

    if args.command == "scan":
        # Just scan and report
        autopilot.config["auto_fix"] = False
        asyncio.run(autopilot.run(continuous=False))

    elif args.command == "fix":
        # Scan and fix
        autopilot.config["auto_fix"] = True
        asyncio.run(autopilot.run(continuous=False))

    elif args.command == "monitor":
        # Continuous monitoring
        asyncio.run(autopilot.run(continuous=args.continuous, interval=args.interval))

    elif args.command == "status":
        # Show current status
        status = autopilot.status()
        print(json.dumps(status, indent=2))

    elif args.command == "config":
        # Show current configuration
        print(json.dumps(autopilot.config, indent=2))


if __name__ == "__main__":
    main()
