#!/usr/bin/env python3
"""
LUKHAS Cognitive AI Dream Analysis CLI
============================

Command-line interface for running symbolic anomaly analysis on dream sessions.
Part of the Jules-13 task implementation for dream pattern detection.
"""
import argparse
import sys
from pathlib import Path

from dream.tools.symbolic_anomaly_explorer import SymbolicAnomalyExplorer

# Add parent directories to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LUKHAS Cognitive AI Symbolic Anomaly Explorer - Jules-13",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sessions 10                   # Analyze 10 recent sessions
  %(prog)s --storage ./dream_data -n 5     # Use custom storage path
  %(prog)s --quiet --json-only            # Generate JSON report only
  %(prog)s --heatmap-only                 # Show only ASCII heatmap
        """,
    )

    parser.add_argument(
        "-n",
        "--sessions",
        type=int,
        default=10,
        help="Number of recent sessions to analyze (default: 10)",
    )

    parser.add_argument("--storage", type=str, help="Path to dream session storage directory")

    parser.add_argument("--no-json", action="store_true", help="Skip JSON report export")

    parser.add_argument("--no-markdown", action="store_true", help="Skip Markdown summary export")

    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Export JSON report only (no console output)",
    )

    parser.add_argument(
        "--markdown-only",
        action="store_true",
        help="Export Markdown summary only (no console output)",
    )

    parser.add_argument("--heatmap-only", action="store_true", help="Show ASCII heatmap only")

    parser.add_argument(
        "--output-dir",
        type=str,
        default="./",
        help="Output directory for reports (default: current directory)",
    )

    parser.add_argument(
        "--threshold",
        action="append",
        nargs=2,
        metavar=("NAME", "VALUE"),
        help="Custom threshold: --threshold emotional_dissonance 0.3",
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress console output")

    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    parser.add_argument(
        "--version",
        action="version",
        version="LUKHAS Cognitive AI Dream Analysis v1.0.0 (Jules-13)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.json_only and args.markdown_only:
        parser.error("Cannot specify both --json-only and --markdown-only")

    if args.heatmap_only and (args.json_only or args.markdown_only):
        parser.error("--heatmap-only cannot be combined with other output modes")

    try:
        # Initialize explorer
        explorer = SymbolicAnomalyExplorer(storage_path=args.storage, drift_integration=True)

        # Apply custom thresholds
        if args.threshold:
            custom_thresholds = {}
            for name, value in args.threshold:
                try:
                    custom_thresholds[name] = float(value)
                except ValueError:
                    parser.error(f"Invalid threshold value: {value} (must be float)")

            explorer.thresholds.update(custom_thresholds)
            if not args.quiet:
                print(f"Applied custom thresholds: {custom_thresholds}")

        if not args.quiet:
            print("🔍 LUKHAS Cognitive AI - Symbolic Anomaly Explorer (Jules-13)")
            print("=" * 60)
            print(f"Analyzing {args.sessions} recent dream sessions...")

        # Load and analyze dreams
        dreams = explorer.load_recent_dreams(args.sessions)

        if not args.quiet:
            print(f"✓ Loaded {len(dreams)} sessions")
            print("Detecting symbolic anomalies...")

        anomalies = explorer.detect_symbolic_anomalies(dreams)

        if not args.quiet:
            print(f"✓ Detected {len(anomalies)} anomalies")
            print("Generating comprehensive report...")

        report = explorer.generate_anomaly_report(anomalies)

        # Handle output modes
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.heatmap_only:
            # Show heatmap only
            print(explorer.display_ascii_heatmap(report))
            return

        if args.json_only:
            # JSON export only
            json_path = output_dir / f"anomaly_report_{report.report_id}.json"
            explorer.export_report_json(report, str(json_path))
            print(f"JSON report exported: {json_path}")
            return

        if args.markdown_only:
            # Markdown export only
            md_path = output_dir / f"top_5_anomalies_{report.report_id}.md"
            explorer.export_summary_markdown(report, str(md_path))
            print(f"Markdown summary exported: {md_path}")
            return

        # Full analysis output
        if not args.quiet:
            # Display ASCII heatmap
            print(explorer.display_ascii_heatmap(report))

            # Show summary
            print("\n📊 ANALYSIS SUMMARY")
            print("-" * 30)
            print(f"Sessions analyzed: {report.sessions_analyzed}")
            print(f"Anomalies detected: {len(report.anomalies_detected)}")
            print(f"Overall risk score: {report.overall_risk_score:.1%}")
            print(f"\n{report.summary}")

            # Show top anomalies
            if report.anomalies_detected:
                print("\n🚨 TOP ANOMALIES")
                print("-" * 30)

                top_anomalies = sorted(
                    report.anomalies_detected,
                    key=lambda a: (explorer._severity_rank(a.severity), a.confidence),
                    reverse=True,
                )[:5]

                for i, anomaly in enumerate(top_anomalies, 1):
                    severity_emoji = {
                        "minor": "🟢",
                        "moderate": "🟡",
                        "significant": "🟠",
                        "critical": "🔴",
                        "catastrophic": "⚫",
                    }

                    emoji = severity_emoji.get(anomaly.severity.value, "❓")
                    print(f"{i}. {emoji} {anomaly.anomaly_type.value.replace('_', ' ').title()}")
                    print(f"   Severity: {anomaly.severity.value.upper()}")
                    print(f"   Confidence: {anomaly.confidence:.1%}")
                    print(f"   Sessions: {len(anomaly.affected_sessions)}")
                    print(f"   {anomaly.description}")
                    print()

            # Show recommendations
            if report.recommendations:
                print("📋 RECOMMENDATIONS")
                print("-" * 30)
                for i, rec in enumerate(report.recommendations, 1):
                    print(f"{i}. {rec}")
                print()

            # Show symbolic trends
            if report.symbolic_trends:
                trends = report.symbolic_trends
                print("📈 SYMBOLIC TRENDS")
                print("-" * 30)
                print(f"Unique symbols: {trends.get('total_unique_tags', 'N/A')}")
                print(f"Average frequency: {trends.get('average_frequency', 'N/A'):.1f}")
                print(f"Average volatility: {trends.get('average_volatility', 'N/A'):.3f}")

                if trends.get("volatile_symbols"):
                    print(f"Most volatile: {', '.join(trends['volatile_symbols'][:3])}")

                if trends.get("frequent_symbols"):
                    print(f"Most frequent: {', '.join(trends['frequent_symbols'][:3])}")
                print()

        # Export files
        if not args.no_json:
            json_path = output_dir / f"anomaly_report_{report.report_id}.json"
            explorer.export_report_json(report, str(json_path))
            if not args.quiet:
                print(f"✓ JSON report: {json_path}")

        if not args.no_markdown:
            md_path = output_dir / f"top_5_anomalies_{report.report_id}.md"
            explorer.export_summary_markdown(report, str(md_path))
            if not args.quiet:
                print(f"✓ Markdown summary: {md_path}")

        if not args.quiet:
            print("=" * 60)
            print("Dream analysis complete.")

            # Exit with error code if critical anomalies found
            critical_count = sum(
                1 for a in report.anomalies_detected if a.severity.value in ["critical", "catastrophic"]
            )

            if critical_count > 0:
                print(f"⚠️  WARNING: {critical_count} critical anomalies detected!")
                sys.exit(2)  # Warning exit code

    except KeyboardInterrupt:
        if not args.quiet:
            print("\n❌ Analysis interrupted by user")
        sys.exit(130)  # SIGINT exit code

    except Exception as e:
        if args.verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
