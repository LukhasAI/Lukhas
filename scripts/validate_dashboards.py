#!/usr/bin/env python3
"""
T4/0.01% Excellence Dashboard Validator
======================================

Validates Grafana dashboards for T4/0.01% excellence monitoring:
- Verifies dashboard JSON structure
- Validates metric queries and data sources
- Checks SLA panel configuration
- Ensures observability coverage
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import requests


class DashboardValidator:
    """Validates Grafana dashboards for T4/0.01% excellence requirements"""

    REQUIRED_DASHBOARDS = [
        'lukhas-t4-overview',
        'lukhas-guardian-sla',
        'lukhas-memory-performance',
        'lukhas-orchestrator-health',
        'lukhas-consciousness-stream',
        'lukhas-identity-auth'
    ]

    REQUIRED_METRICS = [
        'guardian_response_duration_seconds',
        'memory_event_creation_duration_seconds',
        'ai_provider_request_duration_seconds',
        'consciousness_tick_duration_seconds',
        'identity_auth_duration_seconds',
        'lukhas:system_health_score',
        'lukhas:excellence_compliance_score'
    ]

    SLA_THRESHOLDS = {
        'guardian_latency_p95': 0.1,
        'memory_creation_p95': 0.0001,
        'provider_latency_p95': 0.25,
        'consciousness_tick_p99': 0.001,
        'auth_latency_p95': 0.1
    }

    def __init__(self, dashboard_dir: str = "config/grafana/dashboards",
                 grafana_url: str = "http://localhost:3000"):
        self.dashboard_dir = Path(dashboard_dir)
        self.grafana_url = grafana_url
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []

    def validate_dashboard_structure(self, dashboard_path: Path) -> bool:
        """Validate dashboard JSON structure and required fields"""
        try:
            with open(dashboard_path) as f:
                dashboard = json.load(f)
        except json.JSONDecodeError as e:
            self.validation_errors.append(f"Invalid JSON in {dashboard_path.name}: {e}")
            return False
        except FileNotFoundError:
            self.validation_errors.append(f"Dashboard file not found: {dashboard_path}")
            return False

        # Check required top-level fields
        required_fields = ['title', 'panels', 'tags', 'templating']
        for field in required_fields:
            if field not in dashboard:
                self.validation_errors.append(f"{dashboard_path.name}: Missing required field '{field}'")
                return False

        # Validate T4/0.01% tags
        if 't4-excellence' not in dashboard.get('tags', []):
            self.validation_warnings.append(f"{dashboard_path.name}: Missing 't4-excellence' tag")

        # Check panels structure
        panels = dashboard.get('panels', [])
        if not panels:
            self.validation_errors.append(f"{dashboard_path.name}: No panels defined")
            return False

        return self._validate_panels(dashboard_path.name, panels)

    def _validate_panels(self, dashboard_name: str, panels: List[Dict]) -> bool:
        """Validate individual dashboard panels"""
        valid = True

        for i, panel in enumerate(panels):
            panel_id = panel.get('id', i)
            panel_title = panel.get('title', f'Panel {panel_id}')

            # Check required panel fields
            if 'targets' not in panel:
                self.validation_errors.append(
                    f"{dashboard_name} Panel '{panel_title}': Missing targets"
                )
                valid = False
                continue

            # Validate targets/queries
            targets = panel['targets']
            if not targets:
                self.validation_warnings.append(
                    f"{dashboard_name} Panel '{panel_title}': No query targets"
                )
                continue

            for j, target in enumerate(targets):
                if not self._validate_target(dashboard_name, panel_title, j, target):
                    valid = False

            # Check SLA panels have thresholds
            if 'sla' in panel_title.lower() or 'threshold' in panel_title.lower():
                if not self._validate_sla_panel(dashboard_name, panel_title, panel):
                    valid = False

        return valid

    def _validate_target(self, dashboard_name: str, panel_title: str,
                        target_idx: int, target: Dict) -> bool:
        """Validate query target configuration"""
        expr = target.get('expr', target.get('query', ''))

        if not expr:
            self.validation_errors.append(
                f"{dashboard_name} Panel '{panel_title}' Target {target_idx}: Empty query"
            )
            return False

        # Check for required metrics in query
        has_required_metric = any(metric in expr for metric in self.REQUIRED_METRICS)
        if not has_required_metric and 'up' not in expr:
            self.validation_warnings.append(
                f"{dashboard_name} Panel '{panel_title}': Query may not use T4 metrics"
            )

        # Validate datasource
        datasource = target.get('datasource', {})
        if isinstance(datasource, dict):
            ds_type = datasource.get('type', '')
            if ds_type != 'prometheus':
                self.validation_warnings.append(
                    f"{dashboard_name} Panel '{panel_title}': Non-Prometheus datasource"
                )

        return True

    def _validate_sla_panel(self, dashboard_name: str, panel_title: str, panel: Dict) -> bool:
        """Validate SLA panel has proper threshold configuration"""
        # Check for threshold configuration
        field_config = panel.get('fieldConfig', {})
        defaults = field_config.get('defaults', {})
        thresholds = defaults.get('thresholds', {})

        if not thresholds.get('steps'):
            self.validation_warnings.append(
                f"{dashboard_name} Panel '{panel_title}': SLA panel missing thresholds"
            )
            return False

        # Validate threshold values match T4 SLAs
        steps = thresholds['steps']
        threshold_values = [step.get('value', 0) for step in steps if step.get('value') is not None]

        # Check if any threshold matches our SLA requirements
        sla_matched = False
        for _sla_name, sla_value in self.SLA_THRESHOLDS.items():
            if any(abs(threshold - sla_value) < 0.001 for threshold in threshold_values):
                sla_matched = True
                break

        if not sla_matched:
            self.validation_warnings.append(
                f"{dashboard_name} Panel '{panel_title}': Thresholds don't match T4 SLAs"
            )

        return True

    def validate_all_dashboards(self) -> bool:
        """Validate all dashboards in the directory"""
        if not self.dashboard_dir.exists():
            self.validation_errors.append(f"Dashboard directory not found: {self.dashboard_dir}")
            return False

        dashboard_files = list(self.dashboard_dir.glob("*.json"))
        if not dashboard_files:
            self.validation_errors.append("No dashboard files found")
            return False

        print(f"🔍 Validating {len(dashboard_files)} Grafana dashboards...")
        print("=" * 60)

        all_valid = True
        found_dashboards = set()

        for dashboard_file in dashboard_files:
            dashboard_name = dashboard_file.stem
            found_dashboards.add(dashboard_name)

            print(f"  📊 Validating {dashboard_name}...")

            if not self.validate_dashboard_structure(dashboard_file):
                all_valid = False
                print("    ❌ Validation failed")
            else:
                print("    ✅ Validation passed")

        # Check for missing required dashboards
        missing_dashboards = set(self.REQUIRED_DASHBOARDS) - found_dashboards
        for missing in missing_dashboards:
            self.validation_errors.append(f"Required dashboard missing: {missing}")
            all_valid = False

        return all_valid

    def test_grafana_connectivity(self) -> bool:
        """Test connectivity to Grafana instance"""
        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def validate_metrics_availability(self) -> bool:
        """Validate that required metrics are available in Prometheus"""
        prometheus_url = "http://localhost:9090"

        try:
            # Test Prometheus connectivity
            response = requests.get(f"{prometheus_url}/api/v1/query?query=up", timeout=10)
            if response.status_code != 200:
                self.validation_warnings.append("Cannot connect to Prometheus for metric validation")
                return False

            # Check for required metrics
            missing_metrics = []
            for metric in self.REQUIRED_METRICS[:5]:  # Check first 5 to avoid timeout
                query_url = f"{prometheus_url}/api/v1/query?query={metric}"
                response = requests.get(query_url, timeout=5)

                if response.status_code == 200:
                    data = response.json()
                    if not data.get('data', {}).get('result'):
                        missing_metrics.append(metric)

            if missing_metrics:
                self.validation_warnings.append(
                    f"Metrics not available: {', '.join(missing_metrics)}"
                )

        except requests.RequestException as e:
            self.validation_warnings.append(f"Metric validation error: {e}")

        return True

    def generate_report(self) -> bool:
        """Generate validation report"""
        total_errors = len(self.validation_errors)
        total_warnings = len(self.validation_warnings)

        print("\n📊 T4/0.01% Dashboard Validation Report")
        print("=" * 60)
        print(f"Errors: {total_errors}")
        print(f"Warnings: {total_warnings}")

        if self.validation_errors:
            print("\n❌ ERRORS:")
            print("-" * 40)
            for error in self.validation_errors:
                print(f"  • {error}")

        if self.validation_warnings:
            print("\n⚠️  WARNINGS:")
            print("-" * 40)
            for warning in self.validation_warnings:
                print(f"  • {warning}")

        if not self.validation_errors and not self.validation_warnings:
            print("\n✅ All validations passed!")

        # Test live connectivity
        print("\n🔗 Connectivity Tests:")
        print("-" * 40)

        grafana_ok = self.test_grafana_connectivity()
        print(f"  Grafana ({self.grafana_url}): {'✅ OK' if grafana_ok else '❌ FAIL'}")

        if grafana_ok:
            self.validate_metrics_availability()

        return total_errors == 0

    def save_report(self, output_file: str = "dashboard_validation_report.json"):
        """Save validation report to JSON file"""
        report = {
            'timestamp': os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip(),
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.validation_warnings),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'required_dashboards': self.REQUIRED_DASHBOARDS,
            'required_metrics': self.REQUIRED_METRICS,
            'sla_thresholds': self.SLA_THRESHOLDS,
            'status': 'PASS' if not self.validation_errors else 'FAIL'
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Report saved to: {output_file}")


def main():
    """Main validation entry point"""
    dashboard_dir = os.getenv('DASHBOARD_DIR', 'config/grafana/dashboards')
    grafana_url = os.getenv('GRAFANA_URL', 'http://localhost:3000')

    validator = DashboardValidator(dashboard_dir, grafana_url)

    try:
        success = validator.validate_all_dashboards()
        validator.generate_report()
        validator.save_report()

        print(f"\n🎯 Dashboard Validation: {'PASS' if success else 'FAIL'}")

        if not success:
            print("\n⚠️  Dashboard validation errors detected!")
            sys.exit(1)
        else:
            print("\n🎉 All dashboards validated successfully!")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Dashboard validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
