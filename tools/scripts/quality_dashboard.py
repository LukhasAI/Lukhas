#!/usr/bin/env python3
"""
Code Quality Dashboard Generator
Creates an HTML dashboard with real-time code quality metrics
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class QualityDashboard:

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.metrics = {}
        self.history_file = self.project_root / "test_results" / "quality_history.json"
        self.dashboard_file = (
            self.project_root / "test_results" / "quality_dashboard.html"
        )

    def run_command(self, cmd: list[str]) -> tuple:
        """Run command and return output"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def collect_metrics(self) -> dict[str, Any]:
        """Collect all code quality metrics"""
        print("📊 Collecting metrics...")

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "flake8": self.get_flake8_metrics(),
            "ruff": self.get_ruff_metrics(),
            "mypy": self.get_mypy_metrics(),
            "coverage": self.get_coverage_metrics(),
            "complexity": self.get_complexity_metrics(),
            "loc": self.get_loc_metrics(),
            "security": self.get_security_metrics(),
        }

        # Calculate overall health score
        metrics["health_score"] = self.calculate_health_score(metrics)

        return metrics

    def get_flake8_metrics(self) -> dict:
        """Get Flake8 metrics"""
        code, out, _ = self.run_command(
            [
                "flake8",
                ".",
                "--count",
                "--exit-zero",
                "--max-line-length=79",
                "--statistics",
            ]
        )

        lines = out.strip().split("\n")
        total = 0
        by_type = {}

        for line in lines:
            if line and not line.startswith("# ":
                parts = line.split()
                if len(parts) >= 2 and parts[0].isdigit():
                    count = int(parts[0])
                    error_code = parts[1]
                    total += count
                    by_type[error_code] = count

        return {"total": total, "by_type": by_type}

    def get_ruff_metrics(self) -> dict:
        """Get Ruff metrics"""
        code, out, _ = self.run_command(["ruff", "check", ".", "--exit-zero"])

        issues = out.strip().split("\n") if out else []
        total = len([i for i in issues if i])

        return {"total": total}

    def get_mypy_metrics(self) -> dict:
        """Get MyPy metrics"""
        code, out, _ = self.run_command(
            ["mypy", ".", "--ignore-missing-imports", "--no-error-summary"]
        )

        errors = len([l for l in out.split("\n") if ": error:" in l])
        warnings = len([l for l in out.split("\n") if ": warning:" in l])
        notes = len([l for l in out.split("\n") if ": note:" in l])

        return {
            "errors": errors,
            "warnings": warnings,
            "notes": notes,
            "total": errors + warnings,
        }

    def get_coverage_metrics(self) -> dict:
        """Get test coverage metrics"""
        code, out, _ = self.run_command(["pytest", "--co", "-q"])

        # Count test files and functions
        test_count = len([l for l in out.split("\n") if "test_" in l])

        # Try to get actual coverage if available
        coverage_file = self.project_root / ".coverage"
        coverage_percent = 0

        if coverage_file.exists():
            code, out, _ = self.run_command(["coverage", "report", "--format=total"])
            try:
                coverage_percent = float(out.strip())
            except BaseException:
                coverage_percent = 0

        return {"test_count": test_count, "coverage_percent": coverage_percent}

    def get_complexity_metrics(self) -> dict:
        """Get code complexity metrics"""
        code, out, _ = self.run_command(
            [
                "flake8",
                ".",
                "--exit-zero",
                "--max-complexity=10",
                "--select=C901",
            ]
        )

        complex_functions = len(out.strip().split("\n")) if out else 0

        return {"complex_functions": complex_functions}

    def get_loc_metrics(self) -> dict:
        """Get lines of code metrics"""
        py_files = list(self.project_root.rglob("*.py"))

        total_lines = 0
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        for file in py_files:
            if "venv" in str(file) or "__pycache__" in str(file):
                continue

            try:
                with open(file, encoding="utf-8") as f:
                    for line in f:
                        total_lines += 1
                        stripped = line.strip()
                        if not stripped:
                            blank_lines += 1
                        elif stripped.startswith("# ":
                            comment_lines += 1
                        else:
                            code_lines += 1
            except BaseException:
                pass

        return {
            "total": total_lines,
            "code": code_lines,
            "comments": comment_lines,
            "blank": blank_lines,
            "files": len(py_files),
        }

    def get_security_metrics(self) -> dict:
        """Get security metrics from Bandit"""
        code, out, _ = self.run_command(
            [
                "bandit",
                "-r",
                "lukhas",
                "bridge",
                "core",
                "serve",
                "-f",
                "json",
                "-ll",
            ]
        )

        try:
            data = json.loads(out)
            return {
                "high": len(
                    [
                        i
                        for i in data.get("results", [])
                        if i.get("issue_severity") == "HIGH"
                    ]
                ),
                "medium": len(
                    [
                        i
                        for i in data.get("results", [])
                        if i.get("issue_severity") == "MEDIUM"
                    ]
                ),
                "low": len(
                    [
                        i
                        for i in data.get("results", [])
                        if i.get("issue_severity") == "LOW"
                    ]
                ),
            }
        except BaseException:
            return {"high": 0, "medium": 0, "low": 0}

    def calculate_health_score(self, metrics: dict) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0

        # Deduct for linting issues
        score -= min(metrics["flake8"]["total"] * 0.1, 20)
        score -= min(metrics["ruff"]["total"] * 0.1, 20)

        # Deduct for type errors
        score -= min(metrics["mypy"]["errors"] * 0.5, 15)

        # Deduct for low coverage
        coverage = metrics["coverage"]["coverage_percent"]
        if coverage < 80:
            score -= (80 - coverage) * 0.3

        # Deduct for complexity
        score -= min(metrics["complexity"]["complex_functions"] * 0.5, 10)

        # Deduct for security issues
        score -= metrics["security"]["high"] * 5
        score -= metrics["security"]["medium"] * 2
        score -= metrics["security"]["low"] * 0.5

        return max(0, min(100, score))

    def save_history(self, metrics: dict):
        """Save metrics to history"""
        history = []

        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    history = json.load(f)
            except BaseException:
                pass

        history.append(metrics)

        # Keep last 30 entries
        history = history[-30:]

        self.history_file.parent.mkdir(exist_ok=True)
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    def generate_html_dashboard(self, metrics: dict):
        """Generate HTML dashboard"""
        health_color = (
            "green"
            if metrics["health_score"] >= 80
            else "orange" if metrics["health_score"] >= 60 else "red"
        )

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHAS  - Code Quality Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .timestamp {{
            text-align: center;
            color: rgba(255,255,255,0.9);
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .card h2 {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #667eea;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .metric-label {{
            font-weight: 500;
        }}
        .metric-value {{
            font-weight: bold;
        }}
        .health-score {{
            text-align: center;
            padding: 30px;
            background: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .score-circle {{
            width: 150px;
            height: 150px;
            margin: 0 auto;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3em;
            font-weight: bold;
            color: white;
            background: {health_color};
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }}
        .good {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 40px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 LUKHAS  - Code Quality Dashboard</h1>
        <div class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="health-score">
            <h2>Overall Health Score</h2>
            <div class="score-circle">{metrics['health_score']:.0f}%</div>
            <p style="margin-top: 15px; color: #666;">
                Based on linting, type checking, coverage, complexity, and security metrics
            </p>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📝 Linting</h2>
                <div class="metric">
                    <span class="metric-label">Flake8 Issues:</span>
                    <span class="metric-value {('error' if metrics['flake8']['total'] > 100 else 'warning' if metrics['flake8']['total'] > 50 else 'good')}">{metrics['flake8']['total']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Ruff Issues:</span>
                    <span class="metric-value {('error' if metrics['ruff']['total'] > 100 else 'warning' if metrics['ruff']['total'] > 50 else 'good')}">{metrics['ruff']['total']}</span>
                </div>
            </div>

            <div class="card">
                <h2>🔍 Type Checking</h2>
                <div class="metric">
                    <span class="metric-label">Type Errors:</span>
                    <span class="metric-value {('error' if metrics['mypy']['errors'] > 0 else 'good')}">{metrics['mypy']['errors']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Type Warnings:</span>
                    <span class="metric-value {('warning' if metrics['mypy']['warnings'] > 10 else 'good')}">{metrics['mypy']['warnings']}</span>
                </div>
            </div>

            <div class="card">
                <h2>🧪 Testing</h2>
                <div class="metric">
                    <span class="metric-label">Test Count:</span>
                    <span class="metric-value">{metrics['coverage']['test_count']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Coverage:</span>
                    <span class="metric-value {('error' if metrics['coverage']['coverage_percent'] < 60 else 'warning' if metrics['coverage']['coverage_percent'] < 80 else 'good')}">{metrics['coverage']['coverage_percent']:.1f}%</span>
                </div>
            </div>

            <div class="card">
                <h2>📊 Code Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Total Lines:</span>
                    <span class="metric-value">{metrics['loc']['total']:,}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Code Lines:</span>
                    <span class="metric-value">{metrics['loc']['code']:,}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Python Files:</span>
                    <span class="metric-value">{metrics['loc']['files']}</span>
                </div>
            </div>

            <div class="card">
                <h2>🔐 Security</h2>
                <div class="metric">
                    <span class="metric-label">High Severity:</span>
                    <span class="metric-value {('error' if metrics['security']['high'] > 0 else 'good')}">{metrics['security']['high']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Medium Severity:</span>
                    <span class="metric-value {('warning' if metrics['security']['medium'] > 5 else 'good')}">{metrics['security']['medium']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Low Severity:</span>
                    <span class="metric-value">{metrics['security']['low']}</span>
                </div>
            </div>

            <div class="card">
                <h2>🎯 Complexity</h2>
                <div class="metric">
                    <span class="metric-label">Complex Functions:</span>
                    <span class="metric-value {('error' if metrics['complexity']['complex_functions'] > 20 else 'warning' if metrics['complexity']['complex_functions'] > 10 else 'good')}">{metrics['complexity']['complex_functions']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Recommendation:</span>
                    <span class="metric-value">{'Refactor' if metrics['complexity']['complex_functions'] > 10 else 'Good'}</span>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🧠 LUKHAS  - Automated Code Quality Monitoring</p>
            <p>Run <code>make monitor</code> to update metrics</p>
        </div>
    </div>
</body>
</html>
"""

        self.dashboard_file.parent.mkdir(exist_ok=True)
        with open(self.dashboard_file, "w") as f:
            f.write(html_content)

    def generate_dashboard(self):
        """Main method to generate the dashboard"""
        print("🚀 Generating Code Quality Dashboard...")

        # Collect metrics
        metrics = self.collect_metrics()

        # Save to history
        self.save_history(metrics)

        # Generate HTML
        self.generate_html_dashboard(metrics)

        # Print summary
        print("\n" + "=" * 60)
        print("📊 CODE QUALITY SUMMARY")
        print("=" * 60)
        print(f"🎯 Health Score: {metrics['health_score']:.1f}%")
        print(
            f"📝 Linting Issues: {metrics['flake8']['total'] + metrics['ruff']['total']}"
        )
        print(f"🔍 Type Errors: {metrics['mypy']['errors']}")
        print(f"🧪 Test Coverage: {metrics['coverage']['coverage_percent']:.1f}%")
        print(f"🔐 Security Issues: {sum(metrics['security'].values())}")
        print(f"📊 Lines of Code: {metrics['loc']['code']:,}")
        print("=" * 60)
        print(f"\n✅ Dashboard saved to: {self.dashboard_file}")
        print(f"📈 History saved to: {self.history_file}")

        return metrics


if __name__ == "__main__":
    dashboard = QualityDashboard()
    dashboard.generate_dashboard()
