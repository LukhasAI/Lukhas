#!/usr/bin/env python3
"""
🛡️ LUKHAS Security Vulnerability Auto-Fixer
===========================================
Automatically fixes security vulnerabilities found in the Safety CLI scan.
Uses Ollama AI to provide intelligent fix suggestions and validates changes.

Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime, timezone  # ΛTAG: utc

import aiohttp
import click


class SecurityFixer:
    """Automated security vulnerability fixer with Ollama intelligence"""

    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "deepseek-coder:6.7b"
        self.vulnerabilities = []
        self.fixes_applied = []

    def get_known_vulnerabilities(self) -> dict:
        """Get the vulnerabilities we identified from the Safety CLI scan"""
        return {
            "fastapi": {
                "current": "0.104.1",
                "fixed": "0.116.1",
                "cve": "CVE-2024-24762",
                "severity": "HIGH",
                "files": [
                    "dashboard/backend/requirements.txt",
                    "qi/requirements.txt",
                    "tools/scripts/docker/requirements.txt",
                ],
            },
            "python-multipart": {
                "current": "0.0.6",
                "fixed": "0.0.20",
                "cve": "Multiple CVEs",
                "severity": "HIGH",
                "files": [
                    "dashboard/backend/requirements.txt",
                    "tools/scripts/docker/requirements.txt",
                ],
            },
            "python-jose": {
                "current": "3.3.0",
                "fixed": "No fix available",
                "cve": "Multiple CVEs",
                "severity": "HIGH",
                "files": ["dashboard/backend/requirements.txt"],
            },
            "black": {
                "current": "23.11.0",
                "fixed": "25.1.0",
                "cve": "ReDoS vulnerability",
                "severity": "MEDIUM",
                "files": ["dashboard/backend/requirements.txt"],
            },
            "aiohttp": {
                "current": "3.11.19",
                "fixed": "3.12.15",
                "cve": "CVE-2024-XXXX",
                "severity": "MEDIUM",
                "files": [
                    "config/requirements.txt",
                    "core/orchestration/brain/config/requirements.txt",
                ],
            },
            "setuptools": {
                "current": "75.6.0",
                "fixed": "80.9.0",
                "cve": "CVE-2025-47273",
                "severity": "HIGH",
                "files": [
                    "config/requirements.txt",
                    "core/orchestration/brain/config/requirements.txt",
                ],
            },
            "transformers": {
                "current": "4.52.0",
                "fixed": "4.55.3",
                "cve": "Multiple CVEs",
                "severity": "HIGH",
                "files": [
                    "config/requirements.txt",
                    "core/orchestration/brain/config/requirements.txt",
                ],
            },
            "scikit-learn": {
                "current": "1.3.2",
                "fixed": "1.7.1",
                "cve": "CVE-2024-5206",
                "severity": "MEDIUM",
                "files": ["tools/scripts/docker/requirements.txt"],
            },
            "orjson": {
                "current": "3.9.10",
                "fixed": "3.11.2",
                "cve": "Recursion vulnerability",
                "severity": "MEDIUM",
                "files": ["tools/scripts/docker/requirements.txt"],
            },
        }

    async def analyze_fix_with_ollama(self, package: str, vuln_info: dict) -> dict:
        """Get AI-powered analysis and fix recommendations"""
        prompt = f"""You are a Python security expert. Analyze this vulnerability and provide fix recommendations:

Package: {package}
Current Version: {vuln_info["current"]}
Fixed Version: {vuln_info["fixed"]}
CVE: {vuln_info["cve"]}
Severity: {vuln_info["severity"]}

Provide a JSON response with:
1. risk_assessment: Brief description of the risk (1-2 sentences)
2. fix_strategy: How to safely update this package
3. potential_issues: What could break when updating
4. test_commands: Commands to verify the fix works
5. rollback_plan: How to rollback if issues occur

Response must be valid JSON only."""

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                    timeout=45,
                ) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return json.loads(data.get("response", "{}"))
        except Exception as e:
            return {
                "risk_assessment": f"Failed to analyze: {e}",
                "fix_strategy": "Manual review required",
                "potential_issues": "Unknown",
                "test_commands": [],
                "rollback_plan": "Restore from backup",
            }

    def backup_requirements_files(self) -> str:
        """Create backup of all requirements files"""
        backup_dir = f".security_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"  # ΛTAG: utc
        os.makedirs(backup_dir, exist_ok=True)

        vulns = self.get_known_vulnerabilities()
        all_files = set()
        for vuln_info in vulns.values():
            all_files.update(vuln_info["files"])

        for req_file in all_files:
            if os.path.exists(req_file):
                backup_path = os.path.join(backup_dir, req_file.replace("/", "_"))
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                subprocess.run(["cp", req_file, backup_path], check=True)
                click.echo(f"  📁 Backed up {req_file} -> {backup_path}")

        return backup_dir

    def update_requirements_file(self, file_path: str, package: str, new_version: str) -> bool:
        """Update a specific package version in requirements file"""
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path) as f:
                lines = f.readlines()

            updated = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{package}==") or line.strip().startswith(f"{package}>="):
                    lines[i] = f"{package}=={new_version}\n"
                    updated = True
                    break

            if updated:
                with open(file_path, "w") as f:
                    f.writelines(lines)
                click.echo(f"    ✅ Updated {package}=={new_version} in {file_path}")
                return True

        except Exception as e:
            click.echo(f"    ❌ Failed to update {file_path}: {e}")

        return False

    def test_imports(self, packages: list[str]) -> tuple[bool, list[str]]:
        """Test if packages can be imported after updates"""
        failed_imports = []

        for package in packages:
            # Map package names to import names
            import_name = {
                "python-multipart": "multipart",
                "python-jose": "jose",
                "scikit-learn": "sklearn",
            }.get(package, package)

            try:
                result = subprocess.run(
                    [sys.executable, "-c", f"import {import_name}; print('{package} import OK')"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode != 0:
                    failed_imports.append(package)
                    click.echo(f"    ❌ Import test failed for {package}")
                else:
                    click.echo(f"    ✅ Import test passed for {package}")

            except subprocess.TimeoutExpired:
                failed_imports.append(package)
                click.echo(f"    ⏰ Import test timeout for {package}")
            except Exception as e:
                failed_imports.append(package)
                click.echo(f"    ❌ Import test error for {package}: {e}")

        return len(failed_imports) == 0, failed_imports

    async def fix_vulnerability(self, package: str, vuln_info: dict) -> bool:
        """Fix a specific vulnerability"""
        click.echo(f"\n🔧 Fixing {package} vulnerability...")
        click.echo(f"   Current: {vuln_info['current']} → Target: {vuln_info['fixed']}")

        if vuln_info["fixed"] == "No fix available":
            click.echo(f"   ⚠️ No fix available for {package}, manual review required")
            return False

        # Get AI analysis
        analysis = await self.analyze_fix_with_ollama(package, vuln_info)
        click.echo(f"   🤖 Risk Assessment: {analysis.get('risk_assessment', 'N/A')}")

        # Update requirements files
        updated_files = []
        for req_file in vuln_info["files"]:
            if self.update_requirements_file(req_file, package, vuln_info["fixed"]):
                updated_files.append(req_file)

        if not updated_files:
            click.echo(f"   ❌ No files were updated for {package}")
            return False

        # Test the fix
        success, _failed = self.test_imports([package])

        if success:
            self.fixes_applied.append(
                {
                    "package": package,
                    "old_version": vuln_info["current"],
                    "new_version": vuln_info["fixed"],
                    "files_updated": updated_files,
                    "analysis": analysis,
                }
            )
            click.echo(f"   ✅ Successfully fixed {package}")
            return True
        else:
            click.echo(f"   ❌ Fix verification failed for {package}")
            return False

    async def fix_all_vulnerabilities(self):
        """Fix all known vulnerabilities"""
        click.echo("🛡️ LUKHAS Security Vulnerability Auto-Fixer")
        click.echo("=" * 50)

        vulns = self.get_known_vulnerabilities()

        if not vulns:
            click.echo("✅ No vulnerabilities to fix!")
            return

        click.echo(f"📊 Found {len(vulns)} vulnerabilities to fix")

        # Create backup
        click.echo("\n📁 Creating backup of requirements files...")
        backup_dir = self.backup_requirements_files()
        click.echo(f"   Backup created in: {backup_dir}")

        # Fix each vulnerability
        total_fixed = 0
        for package, vuln_info in vulns.items():
            if await self.fix_vulnerability(package, vuln_info):
                total_fixed += 1

        # Generate report
        click.echo("\n📊 Security Fix Summary:")
        click.echo(f"   Total vulnerabilities: {len(vulns)}")
        click.echo(f"   Successfully fixed: {total_fixed}")
        click.echo(f"   Backup location: {backup_dir}")

        if self.fixes_applied:
            click.echo("\n✅ Applied fixes:")
            for fix in self.fixes_applied:
                click.echo(f"   • {fix['package']}: {fix['old_version']} → {fix['new_version']}")

        # Save detailed report
        report_file = f"security_fix_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"  # ΛTAG: utc
        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),  # ΛTAG: utc
                    "backup_dir": backup_dir,
                    "fixes_applied": self.fixes_applied,
                    "total_fixed": total_fixed,
                    "total_vulnerabilities": len(vulns),
                },
                f,
                indent=2,
            )

        click.echo(f"\n📄 Detailed report saved to: {report_file}")
        click.echo("\n🔄 Next steps:")
        click.echo("   1. Run 'pip install -r requirements.txt' to install updated packages")
        click.echo("   2. Run your test suite to verify everything works")
        click.echo("   3. Commit the fixed requirements files")


@click.command()
def fix():
    """Fix all security vulnerabilities"""
    fixer = SecurityFixer()
    asyncio.run(fixer.fix_all_vulnerabilities())


if __name__ == "__main__":
    fix()
