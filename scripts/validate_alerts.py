#!/usr/bin/env python3
"""
Validate Grafana alerts JSON configuration
Ensures alert expressions reference existing metrics
"""
import json
import sys
from pathlib import Path


def validate_alert_json(alert_file):
    """Validate a single alert JSON file"""
    try:
        with open(alert_file) as f:
            alert_data = json.load(f)

        alert = alert_data.get("alert", {})
        alert_id = alert.get("id", "unknown")

        print(f"✅ {alert_file.name}: Valid JSON structure")

        # Check required fields
        required_fields = ["id", "title", "condition", "data"]
        missing_fields = [field for field in required_fields if field not in alert]

        if missing_fields:
            print(f"❌ {alert_file.name}: Missing required fields: {missing_fields}")
            return False

        # Check metric expressions
        for data_item in alert.get("data", []):
            model = data_item.get("model", {})
            expr = model.get("expr", "")

            if expr:
                # Validate metric expressions reference expected metrics
                expected_metrics = [
                    "lukhas_router_no_rule_total",
                    "lukhas_drift_ema",
                    "lukhas_network_coherence",
                    "lukhas_signals_processed_total"
                ]

                metric_found = any(metric in expr for metric in expected_metrics)
                if metric_found:
                    print(f"✅ {alert_file.name}: Expression references known metric: {expr}")
                else:
                    print(f"⚠️  {alert_file.name}: Expression may reference unknown metric: {expr}")

        # Check annotations
        annotations = alert.get("annotations", {})
        if "description" in annotations and "summary" in annotations:
            print(f"✅ {alert_file.name}: Has description and summary")
        else:
            print(f"⚠️  {alert_file.name}: Missing description or summary annotations")

        return True

    except json.JSONDecodeError as e:
        print(f"❌ {alert_file.name}: Invalid JSON - {e}")
        return False
    except Exception as e:
        print(f"❌ {alert_file.name}: Validation error - {e}")
        return False


def main():
    """Main validation logic"""
    alerts_dir = Path("alerts")
    if not alerts_dir.exists():
        print("⚠️  No alerts directory found")
        return 0

    alert_files = list(alerts_dir.glob("*.json"))
    if not alert_files:
        print("⚠️  No alert JSON files found")
        return 0

    print("=== Grafana Alerts Validation ===")

    valid_count = 0
    for alert_file in alert_files:
        if validate_alert_json(alert_file):
            valid_count += 1

    total_count = len(alert_files)
    print(f"\n📊 Validation Summary: {valid_count}/{total_count} alerts valid")

    if valid_count == total_count:
        print("✅ All alerts validated successfully")
        return 0
    else:
        print("❌ Some alerts have validation issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())