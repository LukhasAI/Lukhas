#!/usr/bin/env python3
"""
Test Coverage Metrics and Reporting System
==========================================
Comprehensive test coverage analysis, metrics collection, and reporting
for LUKHAS AI infrastructure with advanced analytics and trend analysis.

Features:
- Multi-level coverage analysis (unit, integration, system, end-to-end)
- Code quality metrics integration
- Performance impact analysis
- Coverage trend analysis and forecasting
- Automated reporting with visualizations
- CI/CD pipeline integration
- Risk assessment based on coverage gaps
"""

import json
import logging
import sqlite3
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CoverageMetrics:
    """Coverage metrics for a module or package"""
    module_name: str
    statements: int
    missing: int
    excluded: int
    coverage_percent: float
    lines_covered: List[int] = field(default_factory=list)
    lines_missing: List[int] = field(default_factory=list)
    lines_excluded: List[int] = field(default_factory=list)
    complexity_score: float = 0.0
    risk_level: str = "unknown"
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TestSuiteMetrics:
    """Metrics for a complete test suite run"""
    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    execution_time: float
    coverage_overall: float
    coverage_by_module: Dict[str, CoverageMetrics] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class QualityGates:
    """Quality gate thresholds for coverage"""
    minimum_coverage: float = 80.0
    target_coverage: float = 90.0
    critical_modules_min: float = 95.0
    new_code_min: float = 85.0
    complexity_threshold: float = 10.0
    performance_regression_threshold: float = 10.0  # percent


class CoverageMetricsSystem:
    """Comprehensive test coverage metrics and reporting system"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.quality_gates = QualityGates(**self.config.get('quality_gates', {}))

        # Database for storing metrics history
        self.db_path = Path(self.config.get('database_path', 'reports/testing/coverage_metrics.db'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Reports directory
        self.reports_dir = Path(self.config.get('reports_dir', 'reports/testing/coverage'))
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info("Coverage metrics system initialized")

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration for coverage system"""
        default_config = {
            'coverage_tools': {
                'python': 'coverage',
                'javascript': 'nyc',
                'typescript': 'nyc',
            },
            'critical_modules': [
                'lukhas/consciousness',
                'lukhas/memory',
                'lukhas/identity',
                'lukhas/governance',
                'candidate/consciousness',
                'candidate/memory',
                'candidate/identity'
            ],
            'exclude_patterns': [
                '*/tests/*',
                '*/test_*',
                '*/__pycache__/*',
                '*/migrations/*',
                '*/venv/*',
                '*/node_modules/*'
            ],
            'quality_gates': {},
            'reports_dir': 'reports/testing/coverage',
            'database_path': 'reports/testing/coverage_metrics.db'
        }

        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config {config_path}: {e}")

        return default_config

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS coverage_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    suite_name TEXT NOT NULL,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    skipped_tests INTEGER,
                    error_tests INTEGER,
                    execution_time REAL,
                    coverage_overall REAL,
                    git_commit TEXT,
                    git_branch TEXT
                );

                CREATE TABLE IF NOT EXISTS module_coverage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    statements INTEGER,
                    missing INTEGER,
                    excluded INTEGER,
                    coverage_percent REAL,
                    complexity_score REAL,
                    risk_level TEXT,
                    FOREIGN KEY (run_id) REFERENCES coverage_runs(run_id)
                );

                CREATE TABLE IF NOT EXISTS quality_gate_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    gate_name TEXT NOT NULL,
                    gate_type TEXT NOT NULL,
                    threshold REAL,
                    actual_value REAL,
                    passed BOOLEAN,
                    FOREIGN KEY (run_id) REFERENCES coverage_runs(run_id)
                );

                CREATE INDEX IF NOT EXISTS idx_coverage_runs_timestamp ON coverage_runs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_module_coverage_run_id ON module_coverage(run_id);
                CREATE INDEX IF NOT EXISTS idx_quality_gate_run_id ON quality_gate_results(run_id);
            """)

    def run_coverage_analysis(self, test_suite: str = "all", include_complexity: bool = True) -> TestSuiteMetrics:
        """Run comprehensive coverage analysis"""
        logger.info(f"Starting coverage analysis for test suite: {test_suite}")

        run_id = f"run_{int(time.time())}_{test_suite}"
        start_time = time.time()

        try:
            # Run tests with coverage
            test_results = self._run_tests_with_coverage(test_suite)

            # Parse coverage results
            coverage_data = self._parse_coverage_results()

            # Calculate complexity metrics if requested
            if include_complexity:
                coverage_data = self._add_complexity_metrics(coverage_data)

            # Assess risk levels
            coverage_data = self._assess_risk_levels(coverage_data)

            # Create test suite metrics
            execution_time = time.time() - start_time
            suite_metrics = TestSuiteMetrics(
                suite_name=test_suite,
                total_tests=test_results.get('total', 0),
                passed_tests=test_results.get('passed', 0),
                failed_tests=test_results.get('failed', 0),
                skipped_tests=test_results.get('skipped', 0),
                error_tests=test_results.get('errors', 0),
                execution_time=execution_time,
                coverage_overall=self._calculate_overall_coverage(coverage_data),
                coverage_by_module=coverage_data
            )

            # Store results in database
            self._store_metrics(run_id, suite_metrics)

            # Evaluate quality gates
            gate_results = self._evaluate_quality_gates(suite_metrics)
            self._store_quality_gate_results(run_id, gate_results)

            logger.info(f"Coverage analysis completed in {execution_time:.2f}s")
            logger.info(f"Overall coverage: {suite_metrics.coverage_overall:.2f}%")

            return suite_metrics

        except Exception as e:
            logger.error(f"Coverage analysis failed: {e}")
            raise

    def _run_tests_with_coverage(self, test_suite: str) -> Dict[str, int]:
        """Run tests with coverage measurement"""
        logger.info("Running tests with coverage measurement")

        # Prepare test command
        if test_suite == "all":
            test_paths = ["tests/"]
        elif test_suite == "unit":
            test_paths = ["tests/unit/"]
        elif test_suite == "integration":
            test_paths = ["tests/integration/"]
        elif test_suite == "smoke":
            test_paths = ["tests/smoke/"]
        else:
            test_paths = [f"tests/{test_suite}/"]

        # Build coverage command
        cmd = [sys.executable, '-m', 'coverage', 'run', '--source=.', '--omit=' + ','.join(self.config['exclude_patterns']), '-m', 'pytest', '-v', '--tb=short', '--junitxml=reports/testing/junit.xml', *test_paths]

        try:
            # Run tests with coverage
            result = subprocess.run(
                cmd,
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )

            # Parse pytest results
            test_results = self._parse_pytest_output(result.stdout)

            # Generate coverage report
            subprocess.run([
                sys.executable, "-m", "coverage", "xml",
                "-o", "reports/testing/coverage.xml"
            ], cwd=ROOT, check=True)

            subprocess.run([
                sys.executable, "-m", "coverage", "html",
                "-d", "reports/testing/htmlcov"
            ], cwd=ROOT, check=True)

            return test_results

        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out")
            return {'total': 0, 'passed': 0, 'failed': 1, 'skipped': 0, 'errors': 0}
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {'total': 0, 'passed': 0, 'failed': 1, 'skipped': 0, 'errors': 0}

    def _parse_pytest_output(self, output: str) -> Dict[str, int]:
        """Parse pytest output to extract test results"""
        results = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 0}

        # Try to parse from JUnit XML first
        junit_path = ROOT / "reports/testing/junit.xml"
        if junit_path.exists():
            try:
                tree = ET.parse(junit_path)
                root = tree.getroot()

                for testsuite in root.findall('.//testsuite'):
                    results['total'] += int(testsuite.get('tests', 0))
                    results['failed'] += int(testsuite.get('failures', 0))
                    results['errors'] += int(testsuite.get('errors', 0))
                    results['skipped'] += int(testsuite.get('skipped', 0))

                results['passed'] = results['total'] - results['failed'] - results['errors'] - results['skipped']
                return results
            except Exception as e:
                logger.warning(f"Failed to parse JUnit XML: {e}")

        # Fallback to text parsing
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line and 'failed' in line:
                # Try to extract numbers from summary line
                import re
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 2:
                    results['passed'] = int(numbers[0])
                    results['failed'] = int(numbers[1])
                    results['total'] = results['passed'] + results['failed']

        return results

    def _parse_coverage_results(self) -> Dict[str, CoverageMetrics]:
        """Parse coverage XML results"""
        coverage_file = ROOT / "reports/testing/coverage.xml"

        if not coverage_file.exists():
            logger.warning("Coverage XML file not found")
            return {}

        coverage_data = {}

        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            for package in root.findall('.//package'):
                package.get('name', '')

                for class_elem in package.findall('.//class'):
                    filename = class_elem.get('filename', '')

                    # Extract module name from filename
                    module_name = self._filename_to_module(filename)

                    # Parse line coverage
                    lines = class_elem.findall('.//line')
                    total_lines = len(lines)
                    covered_lines = len([line for line in lines if line.get('hits', '0') != '0'])

                    if total_lines > 0:
                        coverage_percent = (covered_lines / total_lines) * 100

                        # Get line numbers
                        lines_covered = [
                            int(line.get('number', 0))
                            for line in lines
                            if line.get('hits', '0') != '0'
                        ]
                        lines_missing = [
                            int(line.get('number', 0))
                            for line in lines
                            if line.get('hits', '0') == '0'
                        ]

                        coverage_data[module_name] = CoverageMetrics(
                            module_name=module_name,
                            statements=total_lines,
                            missing=total_lines - covered_lines,
                            excluded=0,  # Will be calculated later
                            coverage_percent=coverage_percent,
                            lines_covered=lines_covered,
                            lines_missing=lines_missing
                        )

        except Exception as e:
            logger.error(f"Failed to parse coverage XML: {e}")

        return coverage_data

    def _filename_to_module(self, filename: str) -> str:
        """Convert filename to module name"""
        # Remove common path prefixes and convert to module notation
        module = filename.replace('/', '.').replace('\\', '.')

        # Remove file extension
        if module.endswith('.py'):
            module = module[:-3]

        # Remove common prefixes
        for prefix in ['src.', 'lib.', '']:
            if module.startswith(prefix):
                module = module[len(prefix):]
                break

        return module

    def _add_complexity_metrics(self, coverage_data: Dict[str, CoverageMetrics]) -> Dict[str, CoverageMetrics]:
        """Add complexity metrics using radon or similar tools"""
        logger.info("Calculating complexity metrics")

        try:
            # Use radon to calculate complexity
            for module_name, metrics in coverage_data.items():
                # Convert module name back to file path
                file_path = self._module_to_filepath(module_name)

                if file_path and file_path.exists():
                    complexity = self._calculate_file_complexity(file_path)
                    metrics.complexity_score = complexity

        except Exception as e:
            logger.warning(f"Failed to calculate complexity metrics: {e}")

        return coverage_data

    def _module_to_filepath(self, module_name: str) -> Optional[Path]:
        """Convert module name to file path"""
        # Convert module notation to file path
        file_path = module_name.replace('.', '/') + '.py'
        full_path = ROOT / file_path

        if full_path.exists():
            return full_path

        # Try alternative paths
        for alt_root in ['src', 'lib', 'lukhas', 'labs']:
            alt_path = ROOT / alt_root / file_path
            if alt_path.exists():
                return alt_path

        return None

    def _calculate_file_complexity(self, file_path: Path) -> float:
        """Calculate cyclomatic complexity for a file"""
        try:
            # Use radon to calculate complexity
            result = subprocess.run([
                sys.executable, "-m", "radon", "cc", str(file_path), "--json"
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                data = json.loads(result.stdout)
                complexities = []

                for file_data in data.values():
                    for item in file_data:
                        if isinstance(item, dict) and 'complexity' in item:
                            complexities.append(item['complexity'])

                return sum(complexities) / len(complexities) if complexities else 0.0

        except Exception as e:
            logger.debug(f"Failed to calculate complexity for {file_path}: {e}")

        return 0.0

    def _assess_risk_levels(self, coverage_data: Dict[str, CoverageMetrics]) -> Dict[str, CoverageMetrics]:
        """Assess risk levels based on coverage and complexity"""
        for metrics in coverage_data.values():
            # Determine risk level
            if metrics.coverage_percent < 50:
                risk = "critical"
            elif metrics.coverage_percent < 70:
                risk = "high"
            elif metrics.coverage_percent < 85:
                risk = "medium"
            else:
                risk = "low"

            # Adjust for complexity
            if metrics.complexity_score > self.quality_gates.complexity_threshold:
                if risk == "low":
                    risk = "medium"
                elif risk == "medium":
                    risk = "high"

            # Adjust for critical modules
            if any(critical in metrics.module_name for critical in self.config['critical_modules']):
                if risk in ["medium", "high"]:
                    risk = "critical"

            metrics.risk_level = risk

        return coverage_data

    def _calculate_overall_coverage(self, coverage_data: Dict[str, CoverageMetrics]) -> float:
        """Calculate overall coverage percentage"""
        if not coverage_data:
            return 0.0

        total_statements = sum(m.statements for m in coverage_data.values())
        total_missing = sum(m.missing for m in coverage_data.values())

        if total_statements == 0:
            return 0.0

        return ((total_statements - total_missing) / total_statements) * 100

    def _evaluate_quality_gates(self, metrics: TestSuiteMetrics) -> Dict[str, Dict[str, Any]]:
        """Evaluate quality gates against metrics"""
        gates = {}

        # Overall coverage gate
        gates['overall_coverage'] = {
            'type': 'coverage',
            'threshold': self.quality_gates.minimum_coverage,
            'actual': metrics.coverage_overall,
            'passed': metrics.coverage_overall >= self.quality_gates.minimum_coverage
        }

        # Critical modules coverage
        critical_coverages = []
        for module_name, module_metrics in metrics.coverage_by_module.items():
            if any(critical in module_name for critical in self.config['critical_modules']):
                critical_coverages.append(module_metrics.coverage_percent)

        if critical_coverages:
            min_critical_coverage = min(critical_coverages)
            gates['critical_modules'] = {
                'type': 'coverage',
                'threshold': self.quality_gates.critical_modules_min,
                'actual': min_critical_coverage,
                'passed': min_critical_coverage >= self.quality_gates.critical_modules_min
            }

        # Test success rate
        if metrics.total_tests > 0:
            success_rate = (metrics.passed_tests / metrics.total_tests) * 100
            gates['test_success_rate'] = {
                'type': 'test_success',
                'threshold': 100.0,
                'actual': success_rate,
                'passed': success_rate == 100.0
            }

        # High-risk modules
        high_risk_modules = [
            name for name, module_metrics in metrics.coverage_by_module.items()
            if module_metrics.risk_level in ['critical', 'high']
        ]

        gates['high_risk_modules'] = {
            'type': 'risk',
            'threshold': 0,
            'actual': len(high_risk_modules),
            'passed': len(high_risk_modules) == 0
        }

        return gates

    def _store_metrics(self, run_id: str, metrics: TestSuiteMetrics):
        """Store metrics in database"""
        git_info = self._get_git_info()

        with sqlite3.connect(self.db_path) as conn:
            # Store run data
            conn.execute("""
                INSERT OR REPLACE INTO coverage_runs (
                    run_id, timestamp, suite_name, total_tests, passed_tests,
                    failed_tests, skipped_tests, error_tests, execution_time,
                    coverage_overall, git_commit, git_branch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, metrics.timestamp, metrics.suite_name,
                metrics.total_tests, metrics.passed_tests, metrics.failed_tests,
                metrics.skipped_tests, metrics.error_tests, metrics.execution_time,
                metrics.coverage_overall, git_info['commit'], git_info['branch']
            ))

            # Store module coverage data
            for module_metrics in metrics.coverage_by_module.values():
                conn.execute("""
                    INSERT INTO module_coverage (
                        run_id, module_name, statements, missing, excluded,
                        coverage_percent, complexity_score, risk_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id, module_metrics.module_name, module_metrics.statements,
                    module_metrics.missing, module_metrics.excluded,
                    module_metrics.coverage_percent, module_metrics.complexity_score,
                    module_metrics.risk_level
                ))

    def _store_quality_gate_results(self, run_id: str, gate_results: Dict[str, Dict[str, Any]]):
        """Store quality gate results in database"""
        with sqlite3.connect(self.db_path) as conn:
            for gate_name, result in gate_results.items():
                conn.execute("""
                    INSERT INTO quality_gate_results (
                        run_id, gate_name, gate_type, threshold, actual_value, passed
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    run_id, gate_name, result['type'], result['threshold'],
                    result['actual'], result['passed']
                ))

    def _get_git_info(self) -> Dict[str, str]:
        """Get current git commit and branch"""
        try:
            commit = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, cwd=ROOT
            ).stdout.strip()

            branch = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True, text=True, cwd=ROOT
            ).stdout.strip()

            return {'commit': commit, 'branch': branch}
        except Exception:
            return {'commit': 'unknown', 'branch': 'unknown'}

    def generate_coverage_report(self, format_type: str = "html", days_back: int = 30) -> Path:
        """Generate comprehensive coverage report"""
        logger.info(f"Generating {format_type} coverage report for last {days_back} days")

        # Get historical data
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Get run history
            runs = conn.execute("""
                SELECT * FROM coverage_runs
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since_date,)).fetchall()

            # Get latest module coverage
            latest_run = runs[0] if runs else None
            if latest_run:
                modules = conn.execute("""
                    SELECT * FROM module_coverage
                    WHERE run_id = ?
                    ORDER BY coverage_percent ASC
                """, (latest_run[1],)).fetchall()  # run_id is at index 1
            else:
                modules = []

        if format_type == "html":
            return self._generate_html_report(runs, modules)
        elif format_type == "json":
            return self._generate_json_report(runs, modules)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _generate_html_report(self, runs: List, modules: List) -> Path:
        """Generate HTML coverage report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LUKHAS AI Coverage Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; border-radius: 5px; }}
                .metric-good {{ background: #d4edda; }}
                .metric-warning {{ background: #fff3cd; }}
                .metric-danger {{ background: #f8d7da; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f8f9fa; }}
                .risk-critical {{ color: #dc3545; font-weight: bold; }}
                .risk-high {{ color: #fd7e14; }}
                .risk-medium {{ color: #ffc107; }}
                .risk-low {{ color: #28a745; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>LUKHAS AI Test Coverage Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        """

        # Latest metrics
        if runs:
            latest = runs[0]
            coverage = latest[10]  # coverage_overall

            coverage_class = "metric-good" if coverage >= 80 else "metric-warning" if coverage >= 60 else "metric-danger"

            html_content += f"""
            <h2>Latest Results</h2>
            <div class="metric {coverage_class}">
                <h3>Overall Coverage</h3>
                <p>{coverage:.1f}%</p>
            </div>
            <div class="metric">
                <h3>Total Tests</h3>
                <p>{latest[4]}</p>
            </div>
            <div class="metric">
                <h3>Success Rate</h3>
                <p>{(latest[5]/latest[4]*100) if latest[4] > 0 else 0:.1f}%</p>
            </div>
            """

        # Module breakdown
        if modules:
            html_content += """
            <h2>Module Coverage Breakdown</h2>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Coverage</th>
                    <th>Statements</th>
                    <th>Missing</th>
                    <th>Complexity</th>
                    <th>Risk Level</th>
                </tr>
            """

            for module in modules:
                risk_class = f"risk-{module[8]}"  # risk_level
                html_content += f"""
                <tr>
                    <td>{module[2]}</td>
                    <td>{module[6]:.1f}%</td>
                    <td>{module[3]}</td>
                    <td>{module[4]}</td>
                    <td>{module[7]:.1f}</td>
                    <td class="{risk_class}">{module[8].upper()}</td>
                </tr>
                """

            html_content += "</table>"

        # Trend chart (simplified)
        if len(runs) > 1:
            html_content += """
            <h2>Coverage Trend</h2>
            <p>Recent coverage percentages:</p>
            <ul>
            """

            for run in runs[:10]:  # Last 10 runs
                timestamp = datetime.fromisoformat(run[2]).strftime('%m-%d %H:%M')
                html_content += f"<li>{timestamp}: {run[10]:.1f}%</li>"

            html_content += "</ul>"

        html_content += """
        </body>
        </html>
        """

        # Save report
        report_path = self.reports_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_path.write_text(html_content)

        logger.info(f"HTML report generated: {report_path}")
        return report_path

    def _generate_json_report(self, runs: List, modules: List) -> Path:
        """Generate JSON coverage report"""
        report_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_runs": len(runs),
                "latest_coverage": runs[0][10] if runs else 0,
                "total_modules": len(modules)
            },
            "latest_run": dict(zip([
                "id", "run_id", "timestamp", "suite_name", "total_tests",
                "passed_tests", "failed_tests", "skipped_tests", "error_tests",
                "execution_time", "coverage_overall", "git_commit", "git_branch"
            ], runs[0])) if runs else {},
            "modules": [
                dict(zip([
                    "id", "run_id", "module_name", "statements", "missing",
                    "excluded", "coverage_percent", "complexity_score", "risk_level"
                ], module)) for module in modules
            ],
            "recent_runs": [
                dict(zip([
                    "id", "run_id", "timestamp", "suite_name", "total_tests",
                    "passed_tests", "failed_tests", "skipped_tests", "error_tests",
                    "execution_time", "coverage_overall", "git_commit", "git_branch"
                ], run)) for run in runs[:10]
            ]
        }

        # Save report
        report_path = self.reports_dir / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"JSON report generated: {report_path}")
        return report_path

    def get_coverage_trends(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze coverage trends over time"""
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            runs = conn.execute("""
                SELECT timestamp, coverage_overall, total_tests, passed_tests
                FROM coverage_runs
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            """, (since_date,)).fetchall()

        if len(runs) < 2:
            return {"trend": "insufficient_data", "runs": len(runs)}

        # Calculate trend
        coverages = [run[1] for run in runs]
        start_coverage = coverages[0]
        end_coverage = coverages[-1]

        trend_direction = "improving" if end_coverage > start_coverage else "declining" if end_coverage < start_coverage else "stable"
        trend_magnitude = abs(end_coverage - start_coverage)

        # Calculate average test success rate
        success_rates = [(run[3] / run[2] * 100) if run[2] > 0 else 0 for run in runs]
        avg_success_rate = sum(success_rates) / len(success_rates)

        return {
            "trend": trend_direction,
            "trend_magnitude": trend_magnitude,
            "start_coverage": start_coverage,
            "end_coverage": end_coverage,
            "runs_analyzed": len(runs),
            "avg_success_rate": avg_success_rate,
            "coverage_variance": max(coverages) - min(coverages)
        }


def main():
    """CLI interface for coverage metrics system"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Coverage Metrics System")
    parser.add_argument("--suite", choices=["all", "unit", "integration", "smoke"],
                       default="all", help="Test suite to analyze")
    parser.add_argument("--report-format", choices=["html", "json"],
                       default="html", help="Report format")
    parser.add_argument("--days-back", type=int, default=30,
                       help="Days of history for reports")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--no-complexity", action="store_true",
                       help="Skip complexity analysis")

    args = parser.parse_args()

    # Initialize system
    system = CoverageMetricsSystem(args.config)

    print("🧪 LUKHAS Coverage Metrics System")
    print("=" * 40)

    # Run coverage analysis
    print(f"Running coverage analysis for {args.suite} tests...")
    metrics = system.run_coverage_analysis(
        test_suite=args.suite,
        include_complexity=not args.no_complexity
    )

    print("✅ Analysis complete!")
    print(f"Overall coverage: {metrics.coverage_overall:.2f}%")
    print(f"Total tests: {metrics.total_tests}")
    print(f"Execution time: {metrics.execution_time:.2f}s")

    # Generate report
    print(f"\nGenerating {args.report_format} report...")
    report_path = system.generate_coverage_report(
        format_type=args.report_format,
        days_back=args.days_back
    )
    print(f"📊 Report saved: {report_path}")

    # Show trends
    trends = system.get_coverage_trends(days_back=args.days_back)
    print(f"\n📈 Coverage trends: {trends['trend']}")
    if trends['trend'] != "insufficient_data":
        print(f"   Magnitude: {trends['trend_magnitude']:.2f}%")
        print(f"   Average success rate: {trends['avg_success_rate']:.1f}%")


if __name__ == "__main__":
    main()
