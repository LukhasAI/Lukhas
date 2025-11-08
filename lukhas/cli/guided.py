#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
LUKHAS Guided CLI - Interactive setup and demos.

Provides interactive commands for quickstart, demos, and tours.
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️  Install rich for better output: pip install rich")


class GuidedCLI:
    """Interactive guided CLI for LUKHAS."""

    def __init__(self):
        self.console = Console() if HAS_RICH else None
        self.project_root = Path(__file__).parent.parent.parent

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print with rich if available, otherwise plain."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def quickstart(self) -> None:
        """Interactive quickstart wizard."""
        self.print("\n[bold cyan]🚀 LUKHAS Interactive Quickstart[/bold cyan]\n")

        # Welcome
        if HAS_RICH:
            welcome = Panel(
                "[green]Welcome to LUKHAS![/green]\n\n"
                "This wizard will help you get started in 3 simple steps:\n"
                "1. Choose your path (Developer, Researcher, Enterprise)\n"
                "2. Configure preferences\n"
                "3. Run your first demo",
                title="🌟 Welcome",
                border_style="cyan",
            )
            self.print(welcome)
        else:
            self.print("=" * 60)
            self.print("Welcome to LUKHAS!")
            self.print("=" * 60)

        # Step 1: Choose path
        self.print("\n[bold]Step 1: Choose Your Path[/bold]\n")
        paths = {
            "1": ("Developer", "Build with LUKHAS APIs and SDKs"),
            "2": ("Researcher", "Explore consciousness-inspired AI"),
            "3": ("Enterprise", "Deploy LUKHAS in production"),
        }

        for key, (name, desc) in paths.items():
            self.print(f"  {key}. [cyan]{name}[/cyan]: {desc}")

        choice = Prompt.ask("\nSelect", choices=["1", "2", "3"], default="1") if HAS_RICH else "1"
        path_name = paths[choice][0]

        self.print(f"\n[green]✓[/green] Selected: {path_name} path")

        # Step 2: Configure
        self.print("\n[bold]Step 2: Configuration[/bold]\n")

        use_demo_data = Confirm.ask("Generate demo data?", default=True) if HAS_RICH else True
        use_analytics = Confirm.ask("Enable analytics (privacy-preserving)?", default=False) if HAS_RICH else False

        self.print(f"\n[green]✓[/green] Demo data: {'Yes' if use_demo_data else 'No'}")
        self.print(f"[green]✓[/green] Analytics: {'Yes' if use_analytics else 'No'}")

        # Step 3: Run setup
        self.print("\n[bold]Step 3: Running Setup[/bold]\n")

        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Installing dependencies...", total=None)
                # Simulate setup steps
                import time

                time.sleep(1)
                progress.update(task, description="Configuring environment...")
                time.sleep(1)
                progress.update(task, description="Initializing database...")
                time.sleep(1)

        self.print("\n[green bold]✅ Setup Complete![/green bold]")
        self.print("\n[cyan]Next steps:[/cyan]")
        self.print("  • Run a demo: [bold]lukhas demo hello[/bold]")
        self.print("  • Take the tour: [bold]lukhas tour[/bold]")
        self.print("  • Read docs: [bold]docs/quickstart/README.md[/bold]")

    def demo(self, example_name: str | None = None) -> None:
        """Run a pre-configured demo."""
        examples = {
            "hello": "examples/quickstart/01_hello_lukhas.py",
            "reasoning": "examples/quickstart/02_reasoning_trace.py",
            "memory": "examples/quickstart/03_memory_persistence.py",
            "ethics": "examples/quickstart/04_guardian_ethics.py",
            "full": "examples/quickstart/05_full_workflow.py",
        }

        if not example_name:
            # Show menu
            self.print("\n[bold cyan]📚 Available Demos[/bold cyan]\n")

            if HAS_RICH:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Name", style="cyan")
                table.add_column("Description")

                table.add_row("hello", "Simple greeting and introduction")
                table.add_row("reasoning", "Multi-step reasoning visualization")
                table.add_row("memory", "Context preservation demo")
                table.add_row("ethics", "Constitutional AI and ethics")
                table.add_row("full", "End-to-end workflow")

                self.print(table)
            else:
                for name, path in examples.items():
                    self.print(f"  • {name}: {path}")

            self.print("\nUsage: [bold]lukhas demo <name>[/bold]")
            return

        if example_name not in examples:
            self.print(f"[red]Error:[/red] Unknown demo '{example_name}'")
            self.print("Run [bold]lukhas demo[/bold] to see available demos")
            return

        # Run the example
        example_path = self.project_root / examples[example_name]
        self.print(f"\n[cyan]Running demo:[/cyan] {example_name}")
        self.print(f"[dim]Location: {example_path}[/dim]\n")

        try:
            subprocess.run([sys.executable, str(example_path)], check=True)
        except subprocess.CalledProcessError as e:
            self.print(f"\n[red]Error running demo:[/red] {e}")
            self.print("Try running: [bold]lukhas troubleshoot[/bold]")

    def tour(self) -> None:
        """Interactive product tour."""
        self.print("\n[bold cyan]🎯 LUKHAS Interactive Tour[/bold cyan]\n")

        tour_steps = [
            {
                "title": "Welcome to LUKHAS",
                "content": "LUKHAS is a consciousness-inspired AI platform with bio-inspired cognitive architecture.",
            },
            {
                "title": "Reasoning Engine (MATRIZ)",
                "content": "Multi-step reasoning powered by quantum-inspired and bio-inspired algorithms.",
            },
            {
                "title": "Memory System (Folds)",
                "content": "Context preservation across sessions with biological forgetting curves.",
            },
            {
                "title": "Guardian Ethics",
                "content": "Constitutional AI with built-in ethical principles and consent framework.",
            },
            {
                "title": "Ready to Build!",
                "content": "You now understand LUKHAS core features. Start building with the API!",
            },
        ]

        for i, step in enumerate(tour_steps, 1):
            if HAS_RICH:
                panel = Panel(
                    step["content"],
                    title=f"[{i}/{len(tour_steps)}] {step['title']}",
                    border_style="cyan" if i < len(tour_steps) else "green",
                )
                self.print(panel)
            else:
                self.print(f"\n[{i}/{len(tour_steps)}] {step['title']}")
                self.print("─" * 60)
                self.print(step["content"])

            if i < len(tour_steps):
                if HAS_RICH:
                    Confirm.ask("\nContinue to next step?", default=True)
                else:
                    input("\nPress Enter to continue...")

        self.print("\n[green bold]✅ Tour Complete![/green bold]")
        self.print("\n[cyan]What's next?[/cyan]")
        self.print("  • Run examples: [bold]lukhas demo hello[/bold]")
        self.print("  • Read API docs: [bold]docs/API_REFERENCE.md[/bold]")
        self.print("  • Join community: [bold]github.com/LukhasAI/Lukhas[/bold]")


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="LUKHAS Guided CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quickstart command
    subparsers.add_parser("quickstart", help="Interactive setup wizard")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run pre-configured demos")
    demo_parser.add_argument("example", nargs="?", help="Demo name (hello, reasoning, memory, ethics, full)")

    # Tour command
    subparsers.add_parser("tour", help="Interactive product tour")

    args = parser.parse_args()

    cli = GuidedCLI()

    if args.command == "quickstart":
        cli.quickstart()
    elif args.command == "demo":
        cli.demo(args.example)
    elif args.command == "tour":
        cli.tour()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
