#!/usr/bin/env python3
"""
Automated Security Update Script for LUKHAS

This script automatically updates dependencies with known security vulnerabilities
and creates a pull request with the changes.
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
from datetime import datetime

class SecurityUpdater:
    """Handles automated security updates for Python dependencies"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.vulnerabilities = []
        self.updates_applied = []
        self.project_root = Path(__file__).parent.parent
        
    def run_command(self, cmd: List[str]) -> Tuple[int, str, str]:
        """Run a shell command and return the result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def check_vulnerabilities(self) -> List[Dict]:
        """Check for security vulnerabilities using multiple tools"""
        print("🔍 Scanning for security vulnerabilities...")
        vulnerabilities = []
        
        # Check with pip-audit
        print("  Running pip-audit...")
        code, stdout, stderr = self.run_command(
            ["python3", "-m", "pip_audit", "--desc", "--format", "json"]
        )
        if code == 0 and stdout:
            try:
                audit_results = json.loads(stdout)
                for vuln in audit_results.get("vulnerabilities", []):
                    vulnerabilities.append({
                        "package": vuln.get("name"),
                        "current_version": vuln.get("version"),
                        "vulnerability": vuln.get("id"),
                        "description": vuln.get("description"),
                        "fix_version": vuln.get("fix_versions", ["latest"])[0],
                        "severity": "high"  # pip-audit doesn't provide severity
                    })
            except json.JSONDecodeError:
                pass
        
        # Check with safety
        print("  Running safety check...")
        code, stdout, stderr = self.run_command(
            ["python3", "-m", "safety", "check", "--json"]
        )
        if stdout:
            try:
                safety_results = json.loads(stdout)
                for vuln in safety_results.get("vulnerabilities", []):
                    package_name = vuln.get("package_name", "").lower()
                    # Avoid duplicates
                    if not any(v["package"] == package_name for v in vulnerabilities):
                        vulnerabilities.append({
                            "package": package_name,
                            "current_version": vuln.get("analyzed_version"),
                            "vulnerability": vuln.get("vulnerability_id"),
                            "description": vuln.get("advisory"),
                            "fix_version": vuln.get("safe_version", "latest"),
                            "severity": vuln.get("severity", "medium").lower()
                        })
            except json.JSONDecodeError:
                pass
        
        self.vulnerabilities = vulnerabilities
        return vulnerabilities
    
    def prioritize_updates(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Prioritize vulnerabilities by severity"""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}
        return sorted(
            vulnerabilities,
            key=lambda x: severity_order.get(x.get("severity", "unknown"), 4)
        )
    
    def update_package(self, package: str, version: str = None) -> bool:
        """Update a specific package"""
        if version and version != "latest":
            cmd = ["pip", "install", "--upgrade", f"{package}=={version}"]
        else:
            cmd = ["pip", "install", "--upgrade", package]
        
        if self.dry_run:
            print(f"  [DRY RUN] Would run: {' '.join(cmd)}")
            return True
        
        print(f"  Updating {package}...")
        code, stdout, stderr = self.run_command(cmd)
        
        if code == 0:
            self.updates_applied.append(package)
            return True
        else:
            print(f"    ❌ Failed to update {package}: {stderr}")
            return False
    
    def update_requirements(self) -> bool:
        """Update requirements.txt with new versions"""
        print("\n📝 Updating requirements.txt...")
        
        if self.dry_run:
            print("  [DRY RUN] Would update requirements.txt")
            return True
        
        # Get current installed versions
        code, stdout, stderr = self.run_command(["pip", "freeze"])
        if code != 0:
            print(f"  ❌ Failed to get installed packages: {stderr}")
            return False
        
        installed = {}
        for line in stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==')
                installed[name.lower()] = version
        
        # Read current requirements
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            print("  ❌ requirements.txt not found")
            return False
        
        lines = req_file.read_text().split('\n')
        updated_lines = []
        
        for line in lines:
            # Skip comments and empty lines
            if line.strip().startswith('#') or not line.strip():
                updated_lines.append(line)
                continue
            
            # Parse package requirement
            package_name = line.split('>=')[0].split('==')[0].split('[')[0].strip().lower()
            
            # Check if this package was updated
            if package_name in [p.lower() for p in self.updates_applied]:
                if package_name in installed:
                    # Update to new version with >= constraint
                    updated_lines.append(f"{package_name}>={installed[package_name]}")
                    print(f"  Updated {package_name} to >={installed[package_name]}")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        # Write updated requirements
        req_file.write_text('\n'.join(updated_lines))
        return True
    
    def run_tests(self) -> bool:
        """Run tests to ensure updates don't break functionality"""
        print("\n🧪 Running tests...")
        
        if self.dry_run:
            print("  [DRY RUN] Would run tests")
            return True
        
        # Run pytest
        code, stdout, stderr = self.run_command(
            ["pytest", "tests/", "-v", "--tb=short", "-q"]
        )
        
        if code == 0:
            print("  ✅ All tests passed")
            return True
        else:
            print(f"  ⚠️ Some tests failed. Review output:\n{stdout}")
            return False
    
    def create_branch_and_commit(self) -> bool:
        """Create a new branch and commit changes"""
        if self.dry_run:
            print("\n[DRY RUN] Would create branch and commit")
            return True
        
        print("\n🌿 Creating branch and committing changes...")
        
        # Create branch name with timestamp
        branch_name = f"security-updates-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create and checkout new branch
        code, _, _ = self.run_command(["git", "checkout", "-b", branch_name])
        if code != 0:
            print(f"  ❌ Failed to create branch {branch_name}")
            return False
        
        # Add changes
        code, _, _ = self.run_command(["git", "add", "requirements.txt"])
        if code != 0:
            print("  ❌ Failed to stage changes")
            return False
        
        # Create commit message
        commit_message = f"""fix(security): Update vulnerable dependencies

Updated the following packages to fix security vulnerabilities:
{chr(10).join(f'- {pkg}' for pkg in self.updates_applied)}

Vulnerabilities fixed: {len(self.vulnerabilities)}
Automated security update by security-update.py
"""
        
        # Commit changes
        code, _, _ = self.run_command(["git", "commit", "-m", commit_message])
        if code != 0:
            print("  ❌ Failed to commit changes")
            return False
        
        print(f"  ✅ Created branch: {branch_name}")
        return True
    
    def generate_report(self) -> str:
        """Generate a security update report"""
        report = []
        report.append("# Security Update Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"\nVulnerabilities found: {len(self.vulnerabilities)}")
        report.append(f"Packages updated: {len(self.updates_applied)}")
        
        if self.vulnerabilities:
            report.append("\n## Vulnerabilities Detected\n")
            for vuln in self.prioritize_updates(self.vulnerabilities):
                report.append(f"### {vuln['package']}")
                report.append(f"- **Severity**: {vuln.get('severity', 'unknown')}")
                report.append(f"- **Current Version**: {vuln.get('current_version', 'unknown')}")
                report.append(f"- **Vulnerability**: {vuln.get('vulnerability', 'unknown')}")
                report.append(f"- **Fix Version**: {vuln.get('fix_version', 'latest')}")
                if vuln.get('description'):
                    report.append(f"- **Description**: {vuln['description'][:200]}...")
                report.append("")
        
        if self.updates_applied:
            report.append("\n## Updates Applied\n")
            for package in self.updates_applied:
                report.append(f"- ✅ {package}")
        
        return "\n".join(report)
    
    def run(self, auto_update: bool = False, test: bool = True) -> bool:
        """Main execution flow"""
        print("🔒 LUKHAS Security Update Tool")
        print("=" * 50)
        
        # Check for vulnerabilities
        vulnerabilities = self.check_vulnerabilities()
        
        if not vulnerabilities:
            print("\n✅ No security vulnerabilities detected!")
            return True
        
        print(f"\n⚠️ Found {len(vulnerabilities)} security vulnerabilities")
        
        # Prioritize updates
        prioritized = self.prioritize_updates(vulnerabilities)
        
        # Show vulnerabilities
        for vuln in prioritized[:5]:  # Show top 5
            print(f"\n  📦 {vuln['package']}")
            print(f"     Severity: {vuln.get('severity', 'unknown')}")
            print(f"     Current: {vuln.get('current_version', 'unknown')}")
            print(f"     Fix: {vuln.get('fix_version', 'latest')}")
        
        if len(prioritized) > 5:
            print(f"\n  ... and {len(prioritized) - 5} more")
        
        if not auto_update and not self.dry_run:
            response = input("\n💡 Apply security updates? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return False
        
        # Apply updates
        print("\n🔧 Applying security updates...")
        for vuln in prioritized:
            if vuln.get("severity") in ["critical", "high"] or auto_update:
                self.update_package(
                    vuln["package"],
                    vuln.get("fix_version")
                )
        
        if self.updates_applied:
            # Update requirements.txt
            self.update_requirements()
            
            # Run tests if requested
            if test:
                test_passed = self.run_tests()
                if not test_passed and not auto_update:
                    response = input("\n⚠️ Tests failed. Continue? (y/n): ")
                    if response.lower() != 'y':
                        print("Reverting changes...")
                        self.run_command(["git", "checkout", "requirements.txt"])
                        return False
            
            # Create commit
            if not self.dry_run:
                self.create_branch_and_commit()
        
        # Generate report
        report = self.generate_report()
        report_file = self.project_root / "security-update-report.md"
        report_file.write_text(report)
        print(f"\n📊 Report saved to: {report_file}")
        
        if self.updates_applied:
            print("\n✅ Security updates completed successfully!")
            print("\n📋 Next steps:")
            print("  1. Review the changes")
            print("  2. Push the branch: git push origin HEAD")
            print("  3. Create a pull request")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="LUKHAS Security Update Tool")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically update without prompting"
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="Skip running tests after updates"
    )
    
    args = parser.parse_args()
    
    # Check for required tools
    required_tools = [("pip_audit", "pip-audit"), ("safety", "safety")]
    missing_tools = []
    
    for module_name, package_name in required_tools:
        result = subprocess.run(
            ["python3", "-c", f"import {module_name}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            missing_tools.append(package_name)
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing_tools)}")
        sys.exit(1)
    
    # Run the updater
    updater = SecurityUpdater(dry_run=args.dry_run)
    success = updater.run(auto_update=args.auto, test=not args.no_test)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()