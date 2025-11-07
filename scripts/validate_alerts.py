#!/usr/bin/env python3
"""
LUKHAS Alert Validation Script
Production Schema v1.0.0

Validates Prometheus alerting rules for correctness and coverage of new metrics.
Tests PromQL queries for syntax and logic errors with T4/0.01% compliance.
"""

import json
import logging
import re
import sys
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Expected metrics from LUKHAS system (updated for T4/0.01%)
EXPECTED_METRICS = {
    # Main API metrics
    'lukhas_api_requests_total',
    'lukhas_api_request_duration_seconds',
    'lukhas_api_active_connections',

    # WebAuthn metrics
    'lukhas_webauthn_api_requests_total',
    'lukhas_webauthn_api_latency_seconds',

    # Orchestration metrics
    'lukhas_orchestration_api_requests_total',
    'lukhas_orchestration_api_latency_seconds',
    'lukhas_multi_ai_requests_total',
    'lukhas_multi_ai_latency_seconds',

    # Legacy metrics (for backward compatibility)
    'lukhas_router_no_rule_total',
    'lukhas_network_coherence',
    'lukhas_signals_processed_total',

    # Memory metrics
    'memory_operations_total',
    'memory_recall_latency_seconds',
    'active_folds',

    # Guardian/Security metrics
    'guardian_policy_violations_total',
    'guardian_lockdown_active',
    'rate_limit_violations_total',
    'token_replay_attempts_total',

    # Drift detection
    'lukhas_drift_ema',

    # System metrics
    'up',
}

class PrometheusAlertValidator:
    """Enhanced Prometheus alert validator with T4/0.01% compliance checking"""

    def __init__(self):
        self.metrics_covered = set()
        self.validation_results = {
            'total_alerts': 0,
            'valid_alerts': 0,
            'invalid_alerts': 0,
            'promql_errors': [],
            'missing_metrics': [],
            'coverage_percentage': 0.0
        }

    def extract_metrics_from_promql(self, expr: str) -> set[str]:
        """Extract metric names from PromQL expression"""
        metric_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*[\{\(]?'
        metrics = set()

        for match in re.finditer(metric_pattern, expr):
            metric_name = match.group(1)
            # Filter out PromQL functions
            if metric_name not in ['rate', 'histogram_quantile', 'sum', 'avg', 'max', 'min',
                                 'count', 'by', 'without', 'increase', 'delta', 'absent']:
                metrics.add(metric_name)

        return metrics

    def validate_promql_syntax(self, expr: str, alert_name: str) -> bool:
        """Basic PromQL syntax validation"""
        try:
            # Check balanced parentheses
            if expr.count('(') != expr.count(')'):
                error_msg = f"Unbalanced parentheses in {alert_name}: {expr}"
                self.validation_results['promql_errors'].append(error_msg)
                logger.warning(f"⚠️ {error_msg}")
                return False

            # Check for basic PromQL structure
            if not re.search(r'[a-zA-Z_][a-zA-Z0-9_]*', expr):
                error_msg = f"No valid metric name found in {alert_name}: {expr}"
                self.validation_results['promql_errors'].append(error_msg)
                logger.warning(f"⚠️ {error_msg}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating PromQL for {alert_name}: {e}")
            return False

    def validate_yaml_alert_file(self, alert_file: Path) -> bool:
        """Validate a Prometheus YAML alert file"""
        try:
            with open(alert_file) as f:
                content = yaml.safe_load(f)

            logger.info(f"✅ {alert_file.name}: Valid YAML structure")

            if 'groups' not in content:
                logger.warning(f"⚠️ {alert_file.name}: No groups found")
                return True  # Not necessarily invalid

            for group in content['groups']:
                if 'rules' not in group:
                    continue

                for rule in group['rules']:
                    if 'alert' not in rule:
                        continue

                    self.validation_results['total_alerts'] += 1
                    alert_name = rule.get('alert', 'unknown')
                    expr = rule.get('expr', '')

                    # Validate PromQL syntax
                    if self.validate_promql_syntax(expr, alert_name):
                        self.validation_results['valid_alerts'] += 1
                    else:
                        self.validation_results['invalid_alerts'] += 1

                    # Extract and track metrics
                    metrics_in_alert = self.extract_metrics_from_promql(expr)
                    self.metrics_covered.update(metrics_in_alert)

                    # Check for expected metrics
                    known_metrics = metrics_in_alert.intersection(EXPECTED_METRICS)
                    if known_metrics:
                        logger.info(f"✅ {alert_file.name}: {alert_name} uses known metrics: {list(known_metrics)}")
                    else:
                        logger.warning(f"⚠️ {alert_file.name}: {alert_name} may use unknown metrics: {expr}")

                    # Check annotations
                    annotations = rule.get('annotations', {})
                    if 'description' in annotations and 'summary' in annotations:
                        logger.debug(f"✅ {alert_file.name}: {alert_name} has complete annotations")
                    else:
                        logger.warning(f"⚠️ {alert_file.name}: {alert_name} missing description or summary")

            return True

        except yaml.YAMLError as e:
            logger.error(f"❌ {alert_file.name}: Invalid YAML - {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {alert_file.name}: Validation error - {e}")
            return False

    def validate_json_alert_file(self, alert_file: Path) -> bool:
        """Validate legacy JSON alert format"""
        try:
            with open(alert_file) as f:
                alert_data = json.load(f)

            alert = alert_data.get("alert", {})
            logger.info(f"✅ {alert_file.name}: Valid JSON structure")

            # Check required fields
            required_fields = ["id", "title", "condition", "data"]
            missing_fields = [field for field in required_fields if field not in alert]

            if missing_fields:
                logger.error(f"❌ {alert_file.name}: Missing required fields: {missing_fields}")
                return False

            # Check metric expressions
            for data_item in alert.get("data", []):
                model = data_item.get("model", {})
                expr = model.get("expr", "")

                if expr:
                    self.validation_results['total_alerts'] += 1

                    # Extract metrics
                    metrics_in_alert = self.extract_metrics_from_promql(expr)
                    self.metrics_covered.update(metrics_in_alert)

                    # Check for expected metrics
                    known_metrics = metrics_in_alert.intersection(EXPECTED_METRICS)
                    if known_metrics:
                        logger.info(f"✅ {alert_file.name}: Expression uses known metrics: {list(known_metrics)}")
                        self.validation_results['valid_alerts'] += 1
                    else:
                        logger.warning(f"⚠️ {alert_file.name}: Expression may use unknown metrics: {expr}")

            return True

        except json.JSONDecodeError as e:
            logger.error(f"❌ {alert_file.name}: Invalid JSON - {e}")
            return False
        except Exception as e:
            logger.error(f"❌ {alert_file.name}: Validation error - {e}")
            return False

    def analyze_metric_coverage(self):
        """Analyze metric coverage and generate missing metrics list"""
        covered = self.metrics_covered.intersection(EXPECTED_METRICS)
        missing = EXPECTED_METRICS - self.metrics_covered

        self.validation_results['missing_metrics'] = list(missing)
        self.validation_results['coverage_percentage'] = (len(covered) / len(EXPECTED_METRICS)) * 100

        logger.info(f"📊 Metric coverage: {len(covered)}/{len(EXPECTED_METRICS)} ({self.validation_results['coverage_percentage']:.1f}%)")

        if missing:
            logger.warning(f"⚠️ Missing alerts for metrics: {list(missing)}")

    def generate_summary(self):
        """Generate validation summary"""
        results = self.validation_results

        logger.info("=" * 60)
        logger.info("🎯 LUKHAS Alert Validation Summary")
        logger.info("=" * 60)
        logger.info(f"Total Alerts: {results['total_alerts']}")
        logger.info(f"Valid Alerts: {results['valid_alerts']}")
        logger.info(f"Invalid Alerts: {results['invalid_alerts']}")
        logger.info(f"Metric Coverage: {results['coverage_percentage']:.1f}%")
        logger.info(f"PromQL Errors: {len(results['promql_errors'])}")

        # T4/0.01% compliance check
        t4_compliant = (
            results['invalid_alerts'] == 0 and
            results['coverage_percentage'] >= 80 and  # At least 80% coverage
            len(results['promql_errors']) == 0
        )

        if t4_compliant:
            logger.info("✅ T4/0.01% COMPLIANCE: PASSED")
        else:
            logger.warning("❌ T4/0.01% COMPLIANCE: FAILED")

        logger.info("=" * 60)


def main():
    """Main validation logic"""
    import argparse
    parser = argparse.ArgumentParser(description='Validate LUKHAS Prometheus alerts')
    parser.add_argument('--alerts-dir', type=Path, default=Path("monitoring/alerts"),
                       help='Path to alerts directory')
    parser.add_argument('--fail-on-error', action='store_true',
                       help='Exit with error code on validation failures')

    args = parser.parse_args()

    # Check for both YAML (Prometheus) and JSON (Grafana) alert files
    alerts_dir = args.alerts_dir
    if not alerts_dir.exists():
        # Try relative path from script location
        alerts_dir = Path(__file__).parent.parent / "monitoring" / "alerts"
        if not alerts_dir.exists():
            logger.warning("⚠️ No alerts directory found")
            return 0

    yaml_files = list(alerts_dir.glob("*.yml")) + list(alerts_dir.glob("*.yaml"))
    json_files = list(alerts_dir.glob("*.json"))

    if not yaml_files and not json_files:
        logger.warning("⚠️ No alert files found")
        return 0

    logger.info("=== LUKHAS T4/0.01% Alert Validation ===")

    validator = PrometheusAlertValidator()
    all_valid = True

    # Validate YAML files (Prometheus format)
    for alert_file in yaml_files:
        if not validator.validate_yaml_alert_file(alert_file):
            all_valid = False

    # Validate JSON files (legacy Grafana format)
    for alert_file in json_files:
        if not validator.validate_json_alert_file(alert_file):
            all_valid = False

    # Analyze metric coverage
    validator.analyze_metric_coverage()

    # Generate summary
    validator.generate_summary()

    # Save results
    results_file = Path(__file__).parent.parent / "artifacts" / "alert_validation_results.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(validator.validation_results, f, indent=2)
    logger.info(f"💾 Results saved to: {results_file}")

    # Check if we should fail on errors
    if args.fail_on_error:
        t4_compliant = (
            validator.validation_results['invalid_alerts'] == 0 and
            validator.validation_results['coverage_percentage'] >= 80 and
            len(validator.validation_results['promql_errors']) == 0
        )

        if not t4_compliant:
            logger.error("❌ T4/0.01% compliance failed - exiting with error")
            return 1

    if all_valid:
        logger.info("✅ All alerts validated successfully")
        return 0
    else:
        logger.warning("⚠️ Some alerts have validation issues")
        return 1 if args.fail_on_error else 0


if __name__ == "__main__":
    sys.exit(main())
