#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🔮 LUKHAS AI - SYMBOLIC DRIFT ANALYZER CLI
║ Command-line interface for monitoring symbolic drift in dream sequences
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: drift_analyzer_cli.py
║ Path: lukhas/tools/cli/drift_analyzer_cli.py
║ Version: 1.0.0 | Created: 2025-07-27 | Modified: 2025-07-27
║ Authors: Claude (Anthropic AI Assistant)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ CLI interface for the Symbolic Drift Analyzer with features:
║ - Real-time monitoring dashboard
║ - One-time analysis reports
║ - Export functionality
║ - Alert notifications
║ - Configuration management
╚══════════════════════════════════════════════════════════════════════════════════
"""

import argparse
import asyncio
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add LUKHAS root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")

from core.symbolic_drift_analyzer import (
    DriftAlertLevel,
    PatternTrend,
    SymbolicDriftAnalyzer,
)

# Console for output
console = Console() if HAS_RICH else None


class DriftAnalyzerCLI:
    """CLI interface for Symbolic Drift Analyzer"""

    def __init__(self):
        self.analyzer = None
        self.console = console
        self._shutdown = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self._shutdown = True
        if self.console:
            self.console.print("\n[yellow]Shutting down gracefully...[/yellow]")

    async def monitor(self, config_path: Path = None, interval: float = 60.0):
        """Run continuous monitoring with live dashboard"""
        # Load configuration
        config = self._load_config(config_path)
        if interval:
            config["analysis_interval"] = interval

        # Initialize analyzer
        self.analyzer = SymbolicDriftAnalyzer(config=config)

        # Setup alert handler
        if self.console:

            def alert_handler(alert):
                color = {
                    DriftAlertLevel.INFO: "blue",
                    DriftAlertLevel.WARNING: "yellow",
                    DriftAlertLevel.CRITICAL: "red",
                    DriftAlertLevel.EMERGENCY: "bold red on white",
                }.get(alert.level, "white")

                self.console.print(
                    f"\n[{color}]🚨 {alert.level.name}: {alert.message}[/{color}]"
                )

                if alert.remediation_suggestions:
                    self.console.print("   [dim]Suggestions:[/dim]")
                    for suggestion in alert.remediation_suggestions:
                        self.console.print(f"   [dim]• {suggestion}[/dim]")

            self.analyzer.register_alert_callback(alert_handler)

        # Start monitoring
        await self.analyzer.start_monitoring()

        if HAS_RICH:
            await self._run_rich_dashboard()
        else:
            await self._run_simple_dashboard()

    async def _run_rich_dashboard(self):
        """Run rich terminal dashboard"""
        layout = Layout()

        # Create layout sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="metrics", ratio=2), Layout(name="alerts", ratio=1)
        )

        with Live(layout, refresh_per_second=1, console=self.console) as live:
            while not self._shutdown:
                # Update header
                layout["header"].update(
                    Panel(
                        f"[bold cyan]LUKHAS Symbolic Drift Analyzer[/bold cyan]\n"
                        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
                        style="white on blue",
                    )
                )

                # Update metrics
                metrics_panel = self._create_metrics_panel()
                layout["metrics"].update(metrics_panel)

                # Update alerts
                alerts_panel = self._create_alerts_panel()
                layout["alerts"].update(alerts_panel)

                # Update footer
                layout["footer"].update(
                    Panel(
                        "[dim]Press Ctrl+C to exit | 's' to save report | 'p' to pause[/dim]",
                        style="white on grey23",
                    )
                )

                await asyncio.sleep(1)

        await self.analyzer.stop_monitoring()

    async def _run_simple_dashboard(self):
        """Run simple text dashboard"""
        while not self._shutdown:
            # Clear screen
            print("\033[2J\033[H")

            # Print summary
            print(self.analyzer.generate_cli_summary())
            print("\nPress Ctrl+C to exit")

            await asyncio.sleep(5)

        await self.analyzer.stop_monitoring()

    def _create_metrics_panel(self) -> Panel:
        """Create metrics display panel"""
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white", width=15)
        table.add_column("Status", width=10)
        table.add_column("Trend", width=10)

        # Get latest metrics
        if self.analyzer.entropy_history:
            latest = self.analyzer.entropy_history[-1]
            thresholds = self.analyzer.config["thresholds"]

            # Calculate trends
            if len(self.analyzer.entropy_history) >= 2:
                prev = self.analyzer.entropy_history[-2]
                trends = {
                    "total": (
                        "↗️"
                        if latest.total_entropy > prev.total_entropy
                        else "↘️" if latest.total_entropy < prev.total_entropy else "→"
                    ),
                    "shannon": (
                        "↗️"
                        if latest.shannon_entropy > prev.shannon_entropy
                        else (
                            "↘️"
                            if latest.shannon_entropy < prev.shannon_entropy
                            else "→"
                        )
                    ),
                    "tag": (
                        "↗️"
                        if latest.tag_entropy > prev.tag_entropy
                        else "↘️" if latest.tag_entropy < prev.tag_entropy else "→"
                    ),
                    "temporal": (
                        "↗️"
                        if latest.temporal_entropy > prev.temporal_entropy
                        else (
                            "↘️"
                            if latest.temporal_entropy < prev.temporal_entropy
                            else "→"
                        )
                    ),
                    "semantic": (
                        "↗️"
                        if latest.semantic_entropy > prev.semantic_entropy
                        else (
                            "↘️"
                            if latest.semantic_entropy < prev.semantic_entropy
                            else "→"
                        )
                    ),
                }
            else:
                trends = dict.fromkeys(
                    ["total", "shannon", "tag", "temporal", "semantic"], "→"
                )

            # Add rows
            table.add_row(
                "Total Entropy",
                f"{latest.total_entropy:.3f}",
                self._get_status_indicator(
                    latest.total_entropy,
                    thresholds["entropy_warning"],
                    thresholds["entropy_critical"],
                ),
                trends["total"],
            )
            table.add_row(
                "Shannon Entropy",
                f"{latest.shannon_entropy:.3f}",
                "📊",
                trends["shannon"],
            )
            table.add_row(
                "Tag Entropy", f"{latest.tag_entropy:.3f}", "🏷️", trends["tag"]
            )
            table.add_row(
                "Temporal Entropy",
                f"{latest.temporal_entropy:.3f}",
                "⏰",
                trends["temporal"],
            )
            table.add_row(
                "Semantic Entropy",
                f"{latest.semantic_entropy:.3f}",
                "🧠",
                trends["semantic"],
            )

            # Add separator
            table.add_row("", "", "", "")

            # Add drift phase
            table.add_row(
                "Drift Phase",
                self.analyzer.current_drift_phase.value,
                self._get_phase_indicator(self.analyzer.current_drift_phase),
                "",
            )

            # Add pattern trend
            if self.analyzer.pattern_trends:
                trend = self.analyzer.pattern_trends[-1]
                table.add_row(
                    "Pattern Trend", trend.name, self._get_trend_indicator(trend), ""
                )

            # Add dreams analyzed
            table.add_row(
                "Dreams Analyzed", str(self.analyzer.total_dreams_analyzed), "📊", ""
            )

        return Panel(table, title="[bold]Drift Metrics[/bold]", border_style="cyan")

    def _create_alerts_panel(self) -> Panel:
        """Create alerts display panel"""
        content = []

        # Get recent alerts
        recent_alerts = list(self.analyzer.alerts)[-10:]  # Last 10 alerts

        if recent_alerts:
            for alert in reversed(recent_alerts):
                color = {
                    DriftAlertLevel.INFO: "blue",
                    DriftAlertLevel.WARNING: "yellow",
                    DriftAlertLevel.CRITICAL: "red",
                    DriftAlertLevel.EMERGENCY: "bold red",
                }.get(alert.level, "white")

                time_str = alert.timestamp.strftime("%H:%M:%S")
                content.append(f"[{color}]{time_str} {alert.level.name}[/{color}]")
                content.append(f"[dim]{alert.message}[/dim]")
                content.append("")
        else:
            content.append("[green]No alerts[/green]")

        return Panel(
            "\n".join(content),
            title="[bold]Recent Alerts[/bold]",
            border_style="yellow",
        )

    def _get_status_indicator(
        self, value: float, warning: float, critical: float
    ) -> str:
        """Get status indicator emoji"""
        if value >= critical:
            return "🔴"
        elif value >= warning:
            return "🟡"
        else:
            return "🟢"

    def _get_phase_indicator(self, phase) -> str:
        """Get phase indicator"""
        indicators = {"EARLY": "🌱", "MIDDLE": "🌿", "LATE": "🍂", "CASCADE": "🌪️"}
        return indicators.get(phase.value, "❓")

    def _get_trend_indicator(self, trend: PatternTrend) -> str:
        """Get trend indicator"""
        indicators = {
            PatternTrend.CONVERGING: "↘️",
            PatternTrend.STABLE: "➡️",
            PatternTrend.DIVERGING: "↗️",
            PatternTrend.OSCILLATING: "〰️",
            PatternTrend.CHAOTIC: "🌀",
        }
        return indicators.get(trend, "❓")

    async def analyze(self, config_path: Path = None, output_path: Path = None):
        """Run one-time analysis and generate report"""
        # Load configuration
        config = self._load_config(config_path)

        # Initialize analyzer
        self.analyzer = SymbolicDriftAnalyzer(config=config)

        # Perform analysis
        if self.console:
            self.console.print("[cyan]Performing drift analysis...[/cyan]")

        results = await self.analyzer.analyze_dreams()

        # Display results
        if self.console:
            self._display_analysis_results(results)
        else:
            print(json.dumps(results, indent=2))

        # Export if requested
        if output_path:
            self.analyzer.export_analysis_report(output_path)
            if self.console:
                self.console.print(f"[green]✓ Report exported to {output_path}[/green]")
            else:
                print(f"Report exported to {output_path}")

    def _display_analysis_results(self, results: dict):
        """Display analysis results with rich formatting"""
        # Status
        self.console.print(f"\n[bold]Analysis Status:[/bold] {results['status']}")
        self.console.print(f"[bold]Timestamp:[/bold] {results.get('timestamp', 'N/A')}")
        self.console.print(
            f"[bold]Dreams Analyzed:[/bold] {results.get('dreams_analyzed', 0)}"
        )

        # Drift phase and trend
        self.console.print(
            f"\n[bold]Current Drift Phase:[/bold] {results.get('current_drift_phase', 'Unknown')}"
        )
        self.console.print(
            f"[bold]Pattern Trend:[/bold] {results.get('pattern_trend', 'Unknown')}"
        )

        # Entropy metrics
        if "entropy_metrics" in results:
            self.console.print("\n[bold cyan]Entropy Metrics:[/bold cyan]")
            metrics = results["entropy_metrics"]

            table = Table(show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")

            for key, value in metrics.items():
                if isinstance(value, float):
                    table.add_row(key.replace("_", " ").title(), f"{value:.3f}")

            self.console.print(table)

        # Tag variance
        if "tag_variance" in results:
            variance = results["tag_variance"]
            self.console.print("\n[bold cyan]Tag Variance:[/bold cyan]")
            self.console.print(f"Unique Tags: {variance.get('unique_tags', 0)}")
            self.console.print(
                f"Evolution Rate: {variance.get('tag_evolution_rate', 0):.3f}"
            )

            if variance.get("dominant_tags"):
                self.console.print("\n[bold]Dominant Tags:[/bold]")
                for tag, count in variance["dominant_tags"][:5]:
                    self.console.print(f"  • {tag}: {count}")

        # Ethical drift
        if "ethical_drift" in results:
            ethical = results["ethical_drift"]
            score = ethical.get("score", 0)
            color = "red" if score > 0.6 else "yellow" if score > 0.3 else "green"
            self.console.print(
                f"\n[bold cyan]Ethical Drift:[/bold cyan] [{color}]{score:.3f}[/{color}]"
            )

            if ethical.get("violations"):
                self.console.print("[bold red]Violations:[/bold red]")
                for violation in ethical["violations"]:
                    self.console.print(f"  • {violation}")

        # Alerts
        if results.get("alerts"):
            self.console.print(
                f"\n[bold yellow]Alerts ({len(results['alerts'])}):[/bold yellow]"
            )
            for alert in results["alerts"][:5]:
                level_color = {
                    "INFO": "blue",
                    "WARNING": "yellow",
                    "CRITICAL": "red",
                    "EMERGENCY": "bold red",
                }.get(alert.get("level", "INFO"), "white")

                self.console.print(
                    f"[{level_color}]• {alert.get('message', 'Unknown alert')}[/{level_color}]"
                )

        # Recommendations
        if results.get("recommendations"):
            self.console.print("\n[bold green]Recommendations:[/bold green]")
            for rec in results["recommendations"]:
                self.console.print(f"  • {rec}")

    def _load_config(self, config_path: Path = None) -> dict:
        """Load configuration from file or use defaults"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}

    def show_config(self):
        """Display current configuration"""
        default_config = {
            "entropy_window_size": 100,
            "tag_history_size": 1000,
            "analysis_interval": 60.0,
            "alert_retention": 1000,
            "thresholds": {
                "entropy_warning": 0.7,
                "entropy_critical": 0.85,
                "tag_variance_warning": 0.6,
                "tag_variance_critical": 0.8,
                "ethical_drift_warning": 0.5,
                "ethical_drift_critical": 0.75,
                "pattern_divergence_rate": 0.3,
            },
            "weights": {"shannon": 0.3, "tag": 0.3, "temporal": 0.2, "semantic": 0.2},
        }

        if self.console and HAS_RICH:
            # Display with syntax highlighting
            json_str = json.dumps(default_config, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai")
            self.console.print(
                Panel(syntax, title="[bold]Default Configuration[/bold]")
            )
        else:
            print(json.dumps(default_config, indent=2))


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LUKHAS Symbolic Drift Analyzer - Monitor entropy and ethical drift in dream sequences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run continuous monitoring
  %(prog)s monitor

  # Monitor with custom interval (30 seconds)
  %(prog)s monitor --interval 30

  # One-time analysis with report export
  %(prog)s analyze --output drift_report.json

  # Show default configuration
  %(prog)s config

  # Use custom configuration
  %(prog)s monitor --config my_config.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Monitor command
    monitor_parser = subparsers.add_parser(
        "monitor", help="Run continuous drift monitoring with live dashboard"
    )
    monitor_parser.add_argument(
        "--config", type=Path, help="Path to configuration file"
    )
    monitor_parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Analysis interval in seconds (default: 60)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Run one-time analysis and generate report"
    )
    analyze_parser.add_argument(
        "--config", type=Path, help="Path to configuration file"
    )
    analyze_parser.add_argument(
        "--output", type=Path, help="Path to export analysis report"
    )

    # Config command
    config_parser = subparsers.add_parser("config", help="Show default configuration")

    args = parser.parse_args()

    # Create CLI instance
    cli = DriftAnalyzerCLI()

    # Execute command
    if args.command == "monitor":
        asyncio.run(cli.monitor(args.config, args.interval))
    elif args.command == "analyze":
        asyncio.run(cli.analyze(args.config, args.output))
    elif args.command == "config":
        cli.show_config()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
