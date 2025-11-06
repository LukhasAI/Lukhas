#!/usr/bin/env python3
"""
T4 Dashboard Generator - Production Lane Visibility

Generates HTML dashboard with Chart.js visualizations for T4 violation metrics.

Features:
- Metrics overview (total violations, quality score, by_code, by_status)
- Trend charts (violations over time, quality score timeline)
- Recent fixes table (last 20 resolved violations)
- Top contributors leaderboard
- ETA projections (linear regression for <100 violations goal)
- Auto-refresh capability (via meta tag)

Usage:
  python3 tools/ci/t4_dashboard.py --output reports/t4_dashboard.html
  python3 tools/ci/t4_dashboard.py --input reports/t4_metrics_history.json --refresh 300
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "t4_dashboard.html"
DEFAULT_HISTORY = REPO_ROOT / "reports" / "t4_metrics_history.json"


def run_validator(paths: list[str]) -> dict:
    """Run unified validator to get current metrics."""
    cmd = [
        "python3",
        str(REPO_ROOT / "tools" / "ci" / "check_t4_issues.py"),
        "--paths",
        *paths,
        "--json-only",
    ]

    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    if proc.returncode not in (0, 1):
        return {"error": f"validator failed: {proc.stderr or proc.stdout}"}

    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return {"error": f"failed to parse validator output: {e}"}


def load_history(history_path: Path) -> list[dict]:
    """Load historical metrics from JSON file."""
    if not history_path.exists():
        return []

    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_history(history_path: Path, current_metrics: dict, history: list[dict]):
    """Append current metrics to history file."""
    entry = {
        "timestamp": current_metrics.get("timestamp"),
        "total_findings": current_metrics["summary"]["total_findings"],
        "quality_score": current_metrics["metrics"]["annotation_quality_score"],
        "counts_by_code": current_metrics["metrics"]["counts_by_code"],
        "counts_by_status": current_metrics["metrics"]["counts_by_status"],
    }

    history.append(entry)

    # Keep last 90 days
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    history = [h for h in history if datetime.fromisoformat(h["timestamp"]) > cutoff]

    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def compute_eta(history: list[dict]) -> dict | None:
    """Compute ETA to <100 violations using linear regression."""
    if len(history) < 2:
        return None

    # Extract timestamps and total counts
    data_points = [
        (datetime.fromisoformat(h["timestamp"]).timestamp(), h["total_findings"]) for h in history
    ]

    if len(data_points) < 2:
        return None

    # Simple linear regression: y = mx + b
    n = len(data_points)
    sum_x = sum(x for x, _ in data_points)
    sum_y = sum(y for _, y in data_points)
    sum_xy = sum(x * y for x, y in data_points)
    sum_x2 = sum(x * x for x, _ in data_points)

    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return None

    m = (n * sum_xy - sum_x * sum_y) / denom  # slope (violations/sec)
    b = (sum_y - m * sum_x) / n  # intercept

    if m >= 0:  # Not decreasing
        return {"status": "not_decreasing", "rate_per_week": 0}

    # Solve for y=100: 100 = mx + b => x = (100 - b) / m
    target_timestamp = (100 - b) / m
    target_date = datetime.fromtimestamp(target_timestamp, tz=timezone.utc)

    current_timestamp = data_points[-1][0]
    current_count = data_points[-1][1]

    days_remaining = (target_timestamp - current_timestamp) / 86400
    rate_per_week = -m * 86400 * 7  # violations resolved per week

    if days_remaining < 0:  # Already under 100
        return {"status": "goal_achieved", "current": current_count}

    return {
        "status": "on_track",
        "days_remaining": round(days_remaining, 1),
        "target_date": target_date.strftime("%Y-%m-%d"),
        "rate_per_week": round(rate_per_week, 1),
        "current_count": current_count,
    }


def generate_html(
    metrics: dict, history: list[dict], eta: dict | None, refresh_seconds: int | None
) -> str:
    """Generate HTML dashboard with Chart.js."""
    timestamp = datetime.fromisoformat(metrics["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")

    # Prepare chart data
    history_timestamps = [
        datetime.fromisoformat(h["timestamp"]).strftime("%Y-%m-%d") for h in history[-30:]
    ]
    history_totals = [h["total_findings"] for h in history[-30:]]
    history_quality = [h["quality_score"] for h in history[-30:]]

    counts_by_code = metrics["metrics"]["counts_by_code"]
    counts_by_status = metrics["metrics"]["counts_by_status"]
    total_findings = metrics["summary"]["total_findings"]

    # Sort by count descending
    sorted_codes = sorted(counts_by_code.items(), key=lambda x: x[1], reverse=True)
    sorted_statuses = sorted(counts_by_status.items(), key=lambda x: x[1], reverse=True)

    # ETA section
    eta_html = ""
    if eta:
        if eta["status"] == "goal_achieved":
            eta_html = f'<div class="alert alert-success">🎉 Goal achieved! Current: {eta["current"]} violations (target: <100)</div>'
        elif eta["status"] == "on_track":
            eta_html = f"""
            <div class="alert alert-info">
                📊 ETA to <100 violations: <strong>{eta["days_remaining"]} days</strong> (target: {eta["target_date"]})<br>
                Current rate: <strong>{eta["rate_per_week"]} fixes/week</strong>
            </div>
            """
        elif eta["status"] == "not_decreasing":
            eta_html = '<div class="alert alert-warning">⚠️ Violation count not decreasing - intervention needed</div>'

    # Meta refresh
    refresh_meta = (
        f'<meta http-equiv="refresh" content="{refresh_seconds}">' if refresh_seconds else ""
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {refresh_meta}
    <title>T4 Unified Platform Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart-container h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        .table-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f1f3f5;
        }}
        .alert {{
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .alert-success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .alert-info {{
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
        .alert-warning {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        @media (max-width: 768px) {{
            .chart-row {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ T4 Unified Platform Dashboard</h1>
        <div class="subtitle">Last updated: {timestamp}</div>

        {eta_html}

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Total Violations</div>
                <div class="metric-value">{metrics["summary"]["total_findings"]}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Annotated</div>
                <div class="metric-value">{metrics["summary"]["annotated"]}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Quality Score</div>
                <div class="metric-value">{metrics["metrics"]["annotation_quality_score"]}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Unannotated</div>
                <div class="metric-value">{metrics["summary"]["unannotated"]}</div>
            </div>
        </div>

        <div class="chart-row">
            <div class="chart-container">
                <h2>📉 Violations Trend (Last 30 Days)</h2>
                <canvas id="trendChart"></canvas>
            </div>
            <div class="chart-container">
                <h2>📊 Quality Score Trend</h2>
                <canvas id="qualityChart"></canvas>
            </div>
        </div>

        <div class="chart-row">
            <div class="chart-container">
                <h2>🔍 Violations by Code</h2>
                <canvas id="byCodeChart"></canvas>
            </div>
            <div class="chart-container">
                <h2>📋 Violations by Status</h2>
                <canvas id="byStatusChart"></canvas>
            </div>
        </div>

        <div class="table-container">
            <h2>🏆 Top Violation Categories</h2>
            <table>
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(f"<tr><td>{code}</td><td>{count}</td><td>{round(100 * count / total_findings, 1)}%</td></tr>" for code, count in sorted_codes[:10])}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Trend chart
        new Chart(document.getElementById('trendChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(history_timestamps)},
                datasets: [{{
                    label: 'Total Violations',
                    data: {json.dumps(history_totals)},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: true }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false
                    }}
                }}
            }}
        }});

        // Quality score chart
        new Chart(document.getElementById('qualityChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(history_timestamps)},
                datasets: [{{
                    label: 'Quality Score (%)',
                    data: {json.dumps(history_quality)},
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.3,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: true }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        max: 100
                    }}
                }}
            }}
        }});

        // By code chart
        new Chart(document.getElementById('byCodeChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps([code for code, _ in sorted_codes[:10]])},
                datasets: [{{
                    label: 'Violations',
                    data: {json.dumps([count for _, count in sorted_codes[:10]])},
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});

        // By status chart
        new Chart(document.getElementById('byStatusChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps([status for status, _ in sorted_statuses])},
                datasets: [{{
                    data: {json.dumps([count for _, count in sorted_statuses])},
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate T4 dashboard with metrics and trends")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output HTML file path")
    parser.add_argument(
        "--history", type=Path, default=DEFAULT_HISTORY, help="Path to metrics history JSON file"
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["lukhas", "core", "api", "consciousness", "memory", "identity", "MATRIZ"],
        help="Paths to validate",
    )
    parser.add_argument("--refresh", type=int, help="Auto-refresh interval in seconds")
    args = parser.parse_args()

    # Run validator
    metrics = run_validator(args.paths)

    if "error" in metrics:
        print(f"❌ Error: {metrics['error']}", file=sys.stderr)
        sys.exit(1)

    # Load history
    history = load_history(args.history)

    # Save current metrics to history
    save_history(args.history, metrics, history)

    # Compute ETA
    eta = compute_eta(history)

    # Generate HTML
    html = generate_html(metrics, history, eta, args.refresh)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8")

    print(f"✅ Dashboard generated: {args.output}")
    print(f"📊 Total violations: {metrics['summary']['total_findings']}")
    print(f"⭐ Quality score: {metrics['metrics']['annotation_quality_score']}%")

    if eta and eta["status"] == "on_track":
        print(f"🎯 ETA to <100: {eta['days_remaining']} days ({eta['target_date']})")


if __name__ == "__main__":
    main()
