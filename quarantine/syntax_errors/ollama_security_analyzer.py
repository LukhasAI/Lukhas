#!/usr/bin/env python3
"""
LUKHAS Ollama Security Analyzer
Automated vulnerability analysis and fixing using local Ollama models
Constellation Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiohttp
import click


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""

    package: str
    current_version: str
    affected_versions: str
    severity: str
    description: str
    cve: Optional[str] = None
    fix_version: Optional[str] = None


class OllamaSecurityAnalyzer:
    """
    Uses Ollama to analyze and suggest fixes for security vulnerabilities
    """

    def __init__(self, ollama_host: str = "http://localhost:11434", timezone):
        self.ollama_host = ollama_host
        self.model = "deepseek-coder:6.7b"  # Best for code analysis
        self.vulnerabilities: list[Vulnerability] = []
        self.fixes: dict[str, str] = {}

    async def check_ollama_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama is running
                async with session.get(f"{self.ollama_host}/api/tags", timeout=5) as resp:
                    if resp.status != 200:
                        return False

                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]

                    # Check if our preferred model is available
                    if self.model not in models:
                        click.echo(f"⚠️ Model {self.model} not found. Pulling it now...")
                        await self.pull_model()

                    return True
        except Exception as e:
            click.echo(f"❌ Ollama not available: {e}")
            return False

    async def pull_model(self):
        """Pull the required model"""
        try:
            subprocess.run(["ollama", "pull", self.model], check=True)
            click.echo(f"✅ Model {self.model} pulled successfully")
        except subprocess.CalledProcessError:
            click.echo(f"❌ Failed to pull model {self.model}")

    def scan_vulnerabilities(self) -> list[Vulnerability]:
        """Scan for vulnerabilities using pip-audit and safety"""
        vulnerabilities = []

        # Run pip-audit
        try:
            result = subprocess.run(["pip-audit", "--format", "json"], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("dependencies", []):
                    for v in vuln.get("vulns", []):
                        vulnerabilities.append(
                            Vulnerability(
                                package=vuln["name"],
                                current_version=vuln.get("version", "unknown"),
                                affected_versions=v.get("affected_versions", ""),
                                severity=v.get("fix_versions", [""])[0] if v.get("fix_versions") else "unknown",
                                description=v.get("description", ""),
                                cve=v.get("id"),
                                fix_version=v.get("fix_versions", [""])[0] if v.get("fix_versions") else None,
                            )
                        )
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            click.echo("⚠️ pip-audit not available or failed")

        # Run safety check
        try:
            result = subprocess.run(["safety", "check", "--json"], capture_output=True, text=True)
            if result.stdout:
                safety_data = json.loads(result.stdout)
                for vuln in safety_data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln.get("package_name", ""),
                            current_version=vuln.get("analyzed_version", ""),
                            affected_versions=vuln.get("vulnerable_spec", ""),
                            severity=vuln.get("severity", "unknown"),
                            description=vuln.get("advisory", ""),
                            cve=vuln.get("cve"),
                            fix_version=vuln.get("more_info_url", None),
                        )
                    )
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            click.echo("⚠️ safety not available or failed")

        self.vulnerabilities = vulnerabilities
        return vulnerabilities

    async def analyze_with_ollama(self, vulnerability: Vulnerability) -> str:
        """Use Ollama to analyze a vulnerability and suggest a fix"""
        prompt = f"""You are a security expert analyzing Python package vulnerabilities.

Vulnerability Details:
- Package: {vulnerability.package}
- Current Version: {vulnerability.current_version}
- Severity: {vulnerability.severity}
- CVE: {vulnerability.cve or 'N/A'}
- Description: {vulnerability.description}
- Affected Versions: {vulnerability.affected_versions}
- Fix Version: {vulnerability.fix_version or 'Unknown'}

Please provide:
1. A brief risk assessment (1-2 sentences)
2. The exact pip command to fix this vulnerability
3. Any potential breaking changes to watch for
4. Alternative packages if the fix might cause issues

Format your response as JSON with keys: risk_assessment, fix_command, breaking_changes, alternatives"""

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "format": "json"},
                    timeout=30,
                ) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
        except Exception as e:
            return f"Error analyzing: {e}"

    async def generate_fix_script(self) -> str:
        """Generate a complete fix script based on all vulnerabilities"""
        if not self.vulnerabilities:
            return ""

        vuln_summary = "\n".join(
            [
                f"- {v.package} ({v.severity}): {v.cve or 'No CVE'}"
                for v in self.vulnerabilities[:10]  # Limit to prevent token overflow
            ]
        )

        prompt = f"""You are a Python security expert. Generate a safe bash script to fix these vulnerabilities:

{vuln_summary}

The script should:
1. Create a backup of requirements.txt
2. Update vulnerable packages safely
3. Test that the updates don't break imports
4. Rollback if there are issues

Return ONLY the bash script, no explanations."""

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=60,
                ) as resp,
            ):
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("response", "")
        except Exception as e:
            # Gracefully surface generation errors without leaking internal state
            return f"Error generating script: {e}"

    async def analyze_all(self) -> dict:
        """Analyze all vulnerabilities and generate report"""
        if not await self.check_ollama_available():
            return {"error": "Ollama not available"}

        vulnerabilities = self.scan_vulnerabilities()

        if not vulnerabilities:
            return {"status": "secure", "message": "No vulnerabilities found!", "count": 0}

        click.echo(f"\n🔍 Found {len(vulnerabilities)} vulnerabilities. Analyzing with Ollama...")

        analyses = {}
        for i, vuln in enumerate(vulnerabilities[:5], 1):  # Limit to 5 for speed
            click.echo(f"  Analyzing {i}/{min(5, len(vulnerabilities}: {vuln.package}...")
            analysis = await self.analyze_with_ollama(vuln)
            try:
                analyses[vuln.package] = json.loads(analysis)
            except json.JSONDecodeError:
                analyses[vuln.package] = {"raw": analysis}

        fix_script = await self.generate_fix_script()

        return {
            "status": "vulnerable",
            "count": len(vulnerabilities),
            "critical": len([v for v in vulnerabilities if "critical" in v.severity.lower()]),
            "high": len([v for v in vulnerabilities if "high" in v.severity.lower()]),
            "analyses": analyses,
            "fix_script": fix_script,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@click.group()
def cli():
    """LUKHAS Ollama Security Analyzer"""
    pass


@cli.command()
@click.option("--json-output", is_flag=True, help="Output as JSON")
@click.option("--save-report", help="Save report to file")
def scan(json_output=False, save_report=None):
    """Scan for vulnerabilities and analyze with Ollama"""
    analyzer = OllamaSecurityAnalyzer()

    click.echo("🛡️ LUKHAS Security Analyzer (Ollama-powered)")
    click.echo("=" * 50)

    report = asyncio.run(analyzer.analyze_all())

    if report.get("status") == "secure":
        click.echo("\n✅ " + report["message"])
        return

    if "error" in report:
        click.echo(f"\n❌ {report['error']}")
        click.echo("\n💡 To fix: brew install ollama && ollama serve")
        return

    # Display results
    click.echo(f"\n⚠️ Found {report['count']} vulnerabilities:")
    click.echo(f"  🔴 Critical: {report.get('critical', 0}")
    click.echo(f"  🟠 High: {report.get('high', 0}")

    if report.get("analyses"):
        click.echo("\n📋 Ollama Analysis Results:")
        for pkg, analysis in report["analyses"].items():
            click.echo(f"\n  📦 {pkg}:")
            if isinstance(analysis, dict) and "risk_assessment" in analysis:
                click.echo(f"    Risk: {analysis.get('risk_assessment', 'N/A'}")
                click.echo(f"    Fix: {analysis.get('fix_command', 'N/A'}")
            else:
                click.echo(f"    {analysis}")

    if save_report:
        report_path = Path(save_report)
        report_path.write_text(json.dumps(report, indent=2))
        click.echo(f"\n💾 Report saved to {save_report}")

    if report.get("fix_script"):
        script_path = Path("fix_vulnerabilities.sh")
        script_path.write_text(report["fix_script"])
        script_path.chmod(0o755)
        click.echo("\n🔧 Fix script generated: ./fix_vulnerabilities.sh")
        click.echo("   Review and run: bash fix_vulnerabilities.sh")


@cli.command()
def fix():
    """Automatically fix vulnerabilities using Ollama recommendations"""
    analyzer = OllamaSecurityAnalyzer()

    click.echo("🔧 Auto-fixing vulnerabilities with Ollama...")

    report = asyncio.run(analyzer.analyze_all())

    if report.get("status") == "secure":
        click.echo("✅ No vulnerabilities to fix!")
        return

    if "error" in report:
        click.echo(f"❌ {report['error']}")
        return

    # Execute fix commands
    if report.get("analyses"):
        for pkg, analysis in report["analyses"].items():
            if isinstance(analysis, dict) and "fix_command" in analysis:
                fix_cmd = analysis["fix_command"]
                if fix_cmd and fix_cmd.startswith("pip install"):
                    click.echo(f"\n🔧 Fixing {pkg}: {fix_cmd}")
                    if click.confirm("Execute this command?"):
                        subprocess.run(fix_cmd, shell=True)

    click.echo("\n✅ Fix attempt complete. Run 'make security-scan' to verify.")


@cli.command()
def pre_commit():
    """Pre-commit hook mode - quick security check"""
    analyzer = OllamaSecurityAnalyzer()

    # Quick scan without detailed analysis
    vulnerabilities = analyzer.scan_vulnerabilities()

    if vulnerabilities:
        critical = [v for v in vulnerabilities if "critical" in v.severity.lower()]
        high = [v for v in vulnerabilities if "high" in v.severity.lower()]

        if critical:
            click.echo("\n🔴 CRITICAL vulnerabilities found! Commit blocked.")
            for v in critical:
                click.echo(f"  - {v.package}: {v.cve or v.description[:50]}")
            click.echo("\nRun 'make security-ollama-fix' to fix automatically")
            sys.exit(1)

        if high:
            click.echo("\n🟠 HIGH severity vulnerabilities found:")
            for v in high[:3]:
                click.echo(f"  - {v.package}: {v.cve or v.description[:50]}")
            click.echo("\nConsider running 'make security-ollama' before pushing")

    click.echo("✅ Security check passed")
    sys.exit(0)


if __name__ == "__main__":
    cli()