#!/usr/bin/env python3
"""
PromQL Alert Rules Unit Tests
============================

Unit tests for Prometheus alert rules using promtool validation.
Critical for T4/0.01% operational excellence.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml


class TestPromQLAlertRules:
    """Test suite for PromQL alert rule validation"""

    @pytest.fixture
    def alert_rules_path(self):
        """Get path to alert rules file"""
        return Path(__file__).parent.parent.parent / "monitoring" / "alert-rules.yml"

    @pytest.fixture
    def prometheus_config_path(self):
        """Get path to prometheus config file"""
        return Path(__file__).parent.parent.parent / "monitoring" / "prometheus-config.yml"

    def test_alert_rules_file_exists(self, alert_rules_path):
        """Verify alert rules file exists"""
        assert alert_rules_path.exists(), f"Alert rules file not found at {alert_rules_path}"

    def test_alert_rules_valid_yaml(self, alert_rules_path):
        """Verify alert rules file is valid YAML"""
        try:
            with open(alert_rules_path, 'r') as f:
                rules_data = yaml.safe_load(f)
            assert rules_data is not None, "Alert rules file is empty"
            assert isinstance(rules_data, dict), "Alert rules must be a dictionary"
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in alert rules: {e}")

    def test_alert_rules_structure(self, alert_rules_path):
        """Verify alert rules have correct structure"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        assert "groups" in rules_data, "Alert rules must have 'groups' key"
        assert isinstance(rules_data["groups"], list), "'groups' must be a list"
        assert len(rules_data["groups"]) > 0, "Must have at least one alert group"

        for i, group in enumerate(rules_data["groups"]):
            assert isinstance(group, dict), f"Group {i} must be a dictionary"
            assert "name" in group, f"Group {i} must have 'name'"
            assert "rules" in group, f"Group {i} must have 'rules'"
            assert isinstance(group["rules"], list), f"Group {i} 'rules' must be a list"

    def test_individual_alert_structure(self, alert_rules_path):
        """Verify each alert has required fields"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        required_fields = ["alert", "expr", "for", "labels", "annotations"]
        required_labels = ["severity"]
        required_annotations = ["summary", "description"]

        for group in rules_data["groups"]:
            for rule_idx, rule in enumerate(group["rules"]):
                rule_name = rule.get("alert", f"rule_{rule_idx}")

                # Check required fields
                for field in required_fields:
                    assert field in rule, f"Alert '{rule_name}' missing required field '{field}'"

                # Check labels
                labels = rule.get("labels", {})
                for label in required_labels:
                    assert label in labels, f"Alert '{rule_name}' missing required label '{label}'"

                # Check annotations
                annotations = rule.get("annotations", {})
                for annotation in required_annotations:
                    assert annotation in annotations, f"Alert '{rule_name}' missing required annotation '{annotation}'"

                # Check severity values
                severity = labels.get("severity")
                valid_severities = ["critical", "warning", "info"]
                assert severity in valid_severities, f"Alert '{rule_name}' has invalid severity '{severity}'"

    @pytest.mark.slow
    def test_promql_syntax_validation(self, alert_rules_path):
        """Validate PromQL expressions syntax using promtool"""
        # Check if promtool is available
        try:
            subprocess.run(["promtool", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("promtool not available for syntax validation")

        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        # Create temporary file for validation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            yaml.dump(rules_data, temp_file, default_flow_style=False)
            temp_path = temp_file.name

        try:
            # Run promtool check rules
            result = subprocess.run(
                ["promtool", "check", "rules", temp_path],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                pytest.fail(f"promtool validation failed:\n{result.stderr}")

        finally:
            os.unlink(temp_path)

    def test_critical_alert_coverage(self, alert_rules_path):
        """Verify we have alerts for critical system components"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        # Extract all alert names
        alert_names = []
        for group in rules_data["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    alert_names.append(rule["alert"])

        # Critical alerts that must exist
        required_critical_alerts = [
            "LUKHASServiceDown",
            "GuardianSystemFailure",
            "MemoryCascadeDetected",
            "HighErrorRate",
            "HighLatency"
        ]

        for critical_alert in required_critical_alerts:
            assert any(critical_alert in name for name in alert_names), \
                f"Missing critical alert: {critical_alert}"

    def test_alert_thresholds_reasonable(self, alert_rules_path):
        """Verify alert thresholds are reasonable for LUKHAS systems"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        threshold_checks = {
            "HighLatency": {
                "max_threshold": "1.0",  # 1 second max reasonable for high latency
                "metric_pattern": "histogram_quantile"
            },
            "HighErrorRate": {
                "max_threshold": "0.10",  # 10% max error rate
                "metric_pattern": "rate"
            }
        }

        for group in rules_data["groups"]:
            for rule in group["rules"]:
                alert_name = rule.get("alert", "")
                expr = rule.get("expr", "")

                for check_name, check_config in threshold_checks.items():
                    if check_name in alert_name:
                        # Extract threshold from expression (simplified)
                        if ">" in expr:
                            # This is a basic check - in practice you'd want more sophisticated parsing
                            parts = expr.split(">")
                            if len(parts) > 1:
                                threshold_part = parts[1].strip()
                                try:
                                    threshold_value = float(threshold_part)
                                    max_threshold = float(check_config["max_threshold"])
                                    assert threshold_value <= max_threshold, \
                                        f"Alert '{alert_name}' threshold {threshold_value} exceeds max {max_threshold}"
                                except ValueError:
                                    # Threshold might be a complex expression, skip this check
                                    pass

    def test_alert_for_duration_reasonable(self, alert_rules_path):
        """Verify alert 'for' duration is reasonable"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        duration_limits = {
            "critical": 300,  # 5 minutes max for critical
            "warning": 900,   # 15 minutes max for warning
            "info": 1800      # 30 minutes max for info
        }

        def parse_duration(duration_str):
            """Parse duration string like '5m', '2h' to seconds"""
            if duration_str.endswith('s'):
                return int(duration_str[:-1])
            elif duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            else:
                return int(duration_str)

        for group in rules_data["groups"]:
            for rule in group["rules"]:
                alert_name = rule.get("alert", "")
                for_duration = rule.get("for", "0s")
                severity = rule.get("labels", {}).get("severity", "info")

                duration_seconds = parse_duration(for_duration)
                max_duration = duration_limits.get(severity, 1800)

                assert duration_seconds <= max_duration, \
                    f"Alert '{alert_name}' 'for' duration {for_duration} exceeds max for {severity} alerts"

    def test_matriz_specific_alerts(self, alert_rules_path):
        """Verify MATRIZ-specific performance alerts exist"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        # Extract all expressions
        expressions = []
        for group in rules_data["groups"]:
            for rule in group["rules"]:
                if "expr" in rule:
                    expressions.append(rule["expr"])

        # Check for MATRIZ-specific metrics
        matriz_metrics = [
            "lukhas_matriz_pipeline_duration_seconds",
            "lukhas_matriz_stage_duration_seconds",
            "guardian_decision_duration_seconds",
            "memory_recall_duration_seconds"
        ]

        expr_text = " ".join(expressions)
        for metric in matriz_metrics:
            assert metric in expr_text, f"Missing alerts for MATRIZ metric: {metric}"

    def test_guardian_system_monitoring(self, alert_rules_path):
        """Verify Guardian system has comprehensive monitoring"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        guardian_alert_names = []
        for group in rules_data["groups"]:
            for rule in group["rules"]:
                alert_name = rule.get("alert", "")
                if "Guardian" in alert_name:
                    guardian_alert_names.append(alert_name)

        # Must have at least these Guardian alerts
        assert len(guardian_alert_names) >= 2, "Must have at least 2 Guardian-related alerts"

        # Check for specific Guardian alerts
        guardian_patterns = ["GuardianSystem", "Guardian"]
        found_guardian_alerts = any(
            any(pattern in alert for pattern in guardian_patterns)
            for alert in guardian_alert_names
        )
        assert found_guardian_alerts, "Must have Guardian system alerts"

    @pytest.mark.slow
    def test_prometheus_config_includes_rules(self, prometheus_config_path, alert_rules_path):
        """Verify Prometheus config references the alert rules"""
        if not prometheus_config_path.exists():
            pytest.skip("Prometheus config not found")

        with open(prometheus_config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        # Check if rule_files is configured
        rule_files = config_data.get("rule_files", [])

        # Should reference our alert rules file
        alert_rules_filename = alert_rules_path.name
        rule_files_str = str(rule_files)
        assert alert_rules_filename in rule_files_str or "alert-rules" in rule_files_str, \
            f"Prometheus config should reference alert rules file {alert_rules_filename}"

    def test_alertmanager_routing_labels(self, alert_rules_path):
        """Verify alerts have proper labels for Alertmanager routing"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)


        for group in rules_data["groups"]:
            for rule in group["rules"]:
                alert_name = rule.get("alert", "")
                labels = rule.get("labels", {})

                # Critical alerts should have component label
                if labels.get("severity") == "critical":
                    assert "component" in labels, \
                        f"Critical alert '{alert_name}' should have 'component' label"

    def test_no_duplicate_alert_names(self, alert_rules_path):
        """Verify no duplicate alert names exist"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        alert_names = []
        for group in rules_data["groups"]:
            for rule in group["rules"]:
                if "alert" in rule:
                    alert_names.append(rule["alert"])

        # Check for duplicates
        unique_names = set(alert_names)
        assert len(alert_names) == len(unique_names), \
            f"Duplicate alert names found: {[name for name in alert_names if alert_names.count(name) > 1]}"

    def test_alert_runbook_urls(self, alert_rules_path):
        """Verify critical alerts have runbook URLs"""
        with open(alert_rules_path, 'r') as f:
            rules_data = yaml.safe_load(f)

        for group in rules_data["groups"]:
            for rule in group["rules"]:
                alert_name = rule.get("alert", "")
                labels = rule.get("labels", {})
                annotations = rule.get("annotations", {})

                # Critical alerts should have runbook URLs
                if labels.get("severity") == "critical":
                    has_runbook = (
                        "runbook_url" in annotations or
                        "runbook" in annotations or
                        "runbook_url" in labels
                    )
                    assert has_runbook, \
                        f"Critical alert '{alert_name}' should have runbook URL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
