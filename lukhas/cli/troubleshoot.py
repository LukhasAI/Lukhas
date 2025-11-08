#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
LUKHAS Troubleshooting Assistant.

Auto-detects common issues and suggests fixes.
"""

from __future__ import annotations

import sys
import shutil
import subprocess
import socket
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class TroubleshootAssistant:
    """Auto-diagnose and suggest fixes for common issues."""

    def __init__(self):
        self.console = Console() if HAS_RICH else None
        self.project_root = Path(__file__).parent.parent.parent
        self.issues_found: list[dict[str, Any]] = []

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print with rich if available."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def check_python_version(self) -> None:
        """Check if Python version is compatible."""
        version = sys.version_info
        required = (3, 9)

        if version >= required:
            self.print(f"[green]✓[/green] Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.issues_found.append(
                {
                    "severity": "error",
                    "issue": f"Python {version.major}.{version.minor} found, 3.9+ required",
                    "fix": "Install Python 3.9 or higher",
                    "command": "# Visit https://www.python.org/downloads/",
                }
            )

    def check_dependencies(self) -> None:
        """Check if required dependencies are installed."""
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.print("[yellow]⚠[/yellow] requirements.txt not found")
            return

        self.print("[cyan]Checking dependencies...[/cyan]")

        # Check if venv exists
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            self.issues_found.append(
                {
                    "severity": "warning",
                    "issue": "Virtual environment not found",
                    "fix": "Create and activate virtual environment",
                    "command": "python3 -m venv venv && source venv/bin/activate",
                }
            )
        else:
            self.print("[green]✓[/green] Virtual environment exists")

    def check_port_conflicts(self) -> None:
        """Check for port conflicts on common ports."""
        ports_to_check = {
            8000: "LUKHAS API server",
            5432: "PostgreSQL",
            6379: "Redis",
        }

        for port, service in ports_to_check.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(("localhost", port))
            sock.close()

            if result == 0:
                if port == 8000:
                    self.issues_found.append(
                        {
                            "severity": "error",
                            "issue": f"Port {port} already in use (needed for {service})",
                            "fix": "Stop the process using this port",
                            "command": f"lsof -ti:{port} | xargs kill -9",
                        }
                    )
                else:
                    # Other ports being in use might be expected
                    self.print(f"[cyan]ℹ[/cyan] Port {port} in use ({service})")
            else:
                self.print(f"[green]✓[/green] Port {port} available ({service})")

    def check_docker(self) -> None:
        """Check if Docker is available and running."""
        if not shutil.which("docker"):
            self.print("[yellow]⚠[/yellow] Docker not found (optional)")
            return

        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                self.print("[green]✓[/green] Docker is running")
            else:
                self.issues_found.append(
                    {
                        "severity": "warning",
                        "issue": "Docker installed but not running",
                        "fix": "Start Docker daemon",
                        "command": "# Start Docker Desktop or: sudo systemctl start docker",
                    }
                )
        except subprocess.TimeoutExpired:
            self.print("[yellow]⚠[/yellow] Docker check timed out")
        except Exception as e:
            self.print(f"[yellow]⚠[/yellow] Docker check failed: {e}")

    def check_env_file(self) -> None:
        """Check if .env file exists and has required variables."""
        env_file = self.project_root / ".env"

        if not env_file.exists():
            self.issues_found.append(
                {
                    "severity": "error",
                    "issue": ".env file not found",
                    "fix": "Run quickstart script to create .env",
                    "command": "bash scripts/quickstart.sh",
                }
            )
        else:
            self.print("[green]✓[/green] .env file exists")

            # Check for critical variables
            env_content = env_file.read_text()
            required_vars = ["DATABASE_URL", "SECRET_KEY"]

            for var in required_vars:
                if var not in env_content:
                    self.issues_found.append(
                        {
                            "severity": "warning",
                            "issue": f"Missing environment variable: {var}",
                            "fix": "Add to .env file",
                            "command": f"echo '{var}=your-value-here' >> .env",
                        }
                    )

    def check_database(self) -> None:
        """Check if database is accessible."""
        db_file = self.project_root / "lukhas_dev.db"

        if db_file.exists():
            self.print("[green]✓[/green] Database file exists")
        else:
            self.print("[yellow]⚠[/yellow] Database not initialized")
            self.print("[cyan]ℹ[/cyan] Run quickstart to initialize")

    def run_diagnostics(self) -> None:
        """Run all diagnostic checks."""
        self.print("\n[bold cyan]🔍 LUKHAS Troubleshooting Assistant[/bold cyan]\n")

        checks = [
            ("Python Version", self.check_python_version),
            ("Dependencies", self.check_dependencies),
            ("Port Availability", self.check_port_conflicts),
            ("Docker", self.check_docker),
            ("Environment", self.check_env_file),
            ("Database", self.check_database),
        ]

        for check_name, check_func in checks:
            self.print(f"\n[bold]{check_name}[/bold]")
            try:
                check_func()
            except Exception as e:
                self.print(f"[red]Error during {check_name} check: {e}[/red]")

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print diagnostic summary with suggested fixes."""
        self.print("\n" + "=" * 60)

        if not self.issues_found:
            self.print("\n[green bold]✅ No issues detected![/green bold]")
            self.print("\nYour LUKHAS setup looks good. If you're still experiencing")
            self.print("problems, please open an issue at:")
            self.print("[cyan]https://github.com/LukhasAI/Lukhas/issues[/cyan]")
            return

        # Categorize issues
        errors = [i for i in self.issues_found if i["severity"] == "error"]
        warnings = [i for i in self.issues_found if i["severity"] == "warning"]

        if errors:
            self.print(f"\n[red bold]❌ {len(errors)} Error(s) Found[/red bold]\n")
            for i, issue in enumerate(errors, 1):
                self.print_issue(i, issue)

        if warnings:
            self.print(f"\n[yellow bold]⚠️  {len(warnings)} Warning(s) Found[/yellow bold]\n")
            for i, issue in enumerate(warnings, 1):
                self.print_issue(i, issue)

        self.print("\n[cyan]💡 Suggested Actions:[/cyan]")
        self.print("   1. Fix errors first (blocking issues)")
        self.print("   2. Address warnings if issues persist")
        self.print("   3. Re-run: [bold]lukhas troubleshoot[/bold]")
        self.print("   4. Still stuck? Open an issue on GitHub")

    def print_issue(self, num: int, issue: dict[str, Any]) -> None:
        """Print a single issue with fix suggestions."""
        severity_color = "red" if issue["severity"] == "error" else "yellow"

        if HAS_RICH:
            content = (
                f"[{severity_color}]Issue:[/{severity_color}] {issue['issue']}\n"
                f"[green]Fix:[/green] {issue['fix']}\n"
                f"[cyan]Command:[/cyan] [dim]{issue['command']}[/dim]"
            )

            panel = Panel(content, title=f"Issue #{num}", border_style=severity_color)
            self.print(panel)
        else:
            self.print(f"\nIssue #{num}:")
            self.print(f"  Problem: {issue['issue']}")
            self.print(f"  Fix: {issue['fix']}")
            self.print(f"  Command: {issue['command']}")


def main() -> None:
    """Main entry point."""
    assistant = TroubleshootAssistant()
    assistant.run_diagnostics()


if __name__ == "__main__":
    main()
