#!/usr/bin/env python3
"""
Diagnostic Continuous Monitor
============================
Continuous monitoring system for diagnostic health and error trends.
Integrates with nightly autofix pipeline to provide alerts and metrics.

Features:
- Error trend tracking
- Automated alerting for new error categories
- Performance metrics collection
- Integration with Slack/email notifications
- Historical diagnostic comparison
"""

import hashlib
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = ROOT / "reports" / "deep_search"
MONITORING_DIR = ROOT / "reports" / "monitoring"
ALERT_CONFIG = ROOT / "config" / "monitoring_alerts.json"


class DiagnosticTrendAnalyzer:
    """Analyzes diagnostic trends over time"""

    def __init__(self):
        self.trend_data = self.load_historical_data()

    def load_historical_data(self) -> dict:
        """Load historical diagnostic data"""
        history_file = MONITORING_DIR / "diagnostic_history.json"

        if not history_file.exists():
            return {"entries": [], "last_update": None}

        try:
            return json.loads(history_file.read_text())
        except Exception as e:
            logger.warning(f"Could not load historical data: {e}")
            return {"entries": [], "last_update": None}

    def save_historical_data(self):
        """Save updated historical data"""
        MONITORING_DIR.mkdir(parents=True, exist_ok=True)
        history_file = MONITORING_DIR / "diagnostic_history.json"

        self.trend_data["last_update"] = datetime.now(timezone.utc).isoformat()
        history_file.write_text(json.dumps(self.trend_data, indent=2))

    def parse_current_diagnostic(self) -> Optional[dict]:
        """Parse current diagnostic report"""
        diagnostic_file = DIAGNOSTIC_DIR / "DIAGNOSTIC_REPORT.md"

        if not diagnostic_file.exists():
            return None

        try:
            content = diagnostic_file.read_text()

            # Extract error counts from report
            errors = {}

            # Look for error category sections
            lines = content.split("\n")
            for _i, line in enumerate(lines):
                if "occurrences" in line.lower() and "% of errors" in line.lower():
                    # Parse error count from format like "### 1. SyntaxError (7 occurrences - 21% of errors)"
                    if "SyntaxError" in line:
                        errors["syntax"] = self.extract_count(line)
                    elif "ImportError" in line:
                        errors["import"] = self.extract_count(line)
                    elif "Collection Warning" in line:
                        errors["collection"] = self.extract_count(line)
                    elif "Configuration" in line:
                        errors["config"] = self.extract_count(line)

            # Get total test count if available
            test_count = self.extract_test_metrics(content)

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "errors": errors,
                "test_metrics": test_count,
                "report_hash": hashlib.md5(content.encode()).hexdigest()[:8],
            }

        except Exception as e:
            logger.error(f"Failed to parse diagnostic report: {e}")
            return None

    def extract_count(self, line: str) -> int:
        """Extract error count from diagnostic line"""
        import re

        match = re.search(r"\((\d+) occurrences", line)
        return int(match.group(1)) if match else 0

    def extract_test_metrics(self, content: str) -> dict:
        """Extract test metrics from diagnostic report"""
        metrics = {"total_collected": 0, "collection_rate": 0.0}

        # Look for test collection info
        for line in content.split("\n"):
            if "tests collected" in line.lower():
                import re

                match = re.search(r"(\d+)\s+tests?\s+collected", line)
                if match:
                    metrics["total_collected"] = int(match.group(1))
            elif "collection success" in line.lower():
                match = re.search(r"(\d+(?:\.\d+)?)\%", line)
                if match:
                    metrics["collection_rate"] = float(match.group(1))

        return metrics

    def analyze_trends(self, current_data: dict) -> dict:
        """Analyze error trends compared to historical data"""
        if not self.trend_data["entries"]:
            return {"trend": "new_baseline", "alerts": [], "summary": "Establishing baseline metrics"}

        # Get previous entry
        prev_data = self.trend_data["entries"][-1]

        alerts = []
        trends = {}

        # Analyze error count changes
        current_errors = current_data.get("errors", {})
        prev_errors = prev_data.get("errors", {})

        for error_type in set(current_errors.keys()) | set(prev_errors.keys()):
            current_count = current_errors.get(error_type, 0)
            prev_count = prev_errors.get(error_type, 0)

            if current_count > prev_count:
                change = current_count - prev_count
                trends[error_type] = f"increased by {change}"
                if change > 5:  # Alert on significant increases
                    alerts.append(
                        {
                            "type": "error_increase",
                            "category": error_type,
                            "change": change,
                            "current": current_count,
                            "severity": "high" if change > 10 else "medium",
                        }
                    )
            elif current_count < prev_count:
                change = prev_count - current_count
                trends[error_type] = f"decreased by {change}"
            else:
                trends[error_type] = "stable"

        # Check for new error types
        new_types = set(current_errors.keys()) - set(prev_errors.keys())
        for new_type in new_types:
            alerts.append(
                {
                    "type": "new_error_category",
                    "category": new_type,
                    "count": current_errors[new_type],
                    "severity": "medium",
                }
            )

        # Analyze test collection trends
        current_collection = current_data.get("test_metrics", {}).get("collection_rate", 0)
        prev_collection = prev_data.get("test_metrics", {}).get("collection_rate", 0)

        if current_collection < prev_collection - 5:  # 5% drop threshold
            alerts.append(
                {
                    "type": "collection_degradation",
                    "change": current_collection - prev_collection,
                    "current_rate": current_collection,
                    "severity": "high" if current_collection < 90 else "medium",
                }
            )

        return {
            "trend": "analyzed",
            "error_trends": trends,
            "alerts": alerts,
            "summary": f"Found {len(alerts)} alerts across {len(trends)} error categories",
        }

    def add_current_entry(self, data: dict):
        """Add current diagnostic data to historical tracking"""
        self.trend_data["entries"].append(data)

        # Keep only last 30 entries (30 days if run daily)
        if len(self.trend_data["entries"]) > 30:
            self.trend_data["entries"] = self.trend_data["entries"][-30:]

        self.save_historical_data()


class AlertManager:
    """Manages diagnostic monitoring alerts"""

    def __init__(self):
        self.config = self.load_alert_config()

    def load_alert_config(self) -> dict:
        """Load alert configuration"""
        if ALERT_CONFIG.exists():
            try:
                return json.loads(ALERT_CONFIG.read_text())
            except Exception as e:
                logger.warning(f"Could not load alert config: {e}")

        # Default configuration
        return {
            "enabled": True,
            "channels": {
                "slack": {"enabled": False, "webhook_url": ""},
                "email": {"enabled": False, "recipients": []},
                "log": {"enabled": True, "level": "INFO"},
            },
            "thresholds": {"error_increase": 5, "collection_drop": 5.0, "new_category_threshold": 1},
        }

    def should_alert(self, alert: dict) -> bool:
        """Determine if alert should be sent based on configuration"""
        if not self.config.get("enabled", True):
            return False

        severity = alert.get("severity", "low")
        alert_type = alert.get("type", "")

        # Check severity thresholds
        if severity == "high":
            return True
        elif severity == "medium":
            # Check specific thresholds
            if alert_type == "error_increase":
                threshold = self.config.get("thresholds", {}).get("error_increase", 5)
                return alert.get("change", 0) >= threshold

        return False

    def send_alert(self, alert: dict, context: Optional[dict] = None):
        """Send alert through configured channels"""
        if not self.should_alert(alert):
            return

        message = self.format_alert_message(alert, context)

        # Log alert
        if self.config.get("channels", {}).get("log", {}).get("enabled", True):
            logger.warning(f"DIAGNOSTIC ALERT: {message}")

        # Slack notification (placeholder)
        slack_config = self.config.get("channels", {}).get("slack", {})
        if slack_config.get("enabled", False):
            self.send_slack_alert(message, slack_config)

        # Email notification (placeholder)
        email_config = self.config.get("channels", {}).get("email", {})
        if email_config.get("enabled", False):
            self.send_email_alert(message, email_config)

    def format_alert_message(self, alert: dict, context: Optional[dict] = None) -> str:
        """Format alert message for human consumption"""
        alert_type = alert.get("type", "unknown")
        severity = alert.get("severity", "low").upper()

        if alert_type == "error_increase":
            return (
                f"[{severity}] {alert['category']} errors increased by "
                f"{alert['change']} (now {alert['current']} total)"
            )

        elif alert_type == "new_error_category":
            return f"[{severity}] New error category detected: " f"{alert['category']} ({alert['count']} occurrences)"

        elif alert_type == "collection_degradation":
            return (
                f"[{severity}] Test collection rate dropped by "
                f"{abs(alert['change']):.1f}% (now {alert['current_rate']:.1f}%)"
            )

        return f"[{severity}] Unknown alert: {alert}"

    def send_slack_alert(self, message: str, config: dict):
        """Send Slack alert (placeholder implementation)"""
        # In a real implementation, this would use requests to post to Slack webhook
        logger.info(f"SLACK ALERT: {message}")

    def send_email_alert(self, message: str, config: dict):
        """Send email alert (placeholder implementation)"""
        # In a real implementation, this would use SMTP
        logger.info(f"EMAIL ALERT: {message}")


class DiagnosticMonitor:
    """Main diagnostic monitoring system"""

    def __init__(self):
        self.analyzer = DiagnosticTrendAnalyzer()
        self.alert_manager = AlertManager()

    def run_monitoring_cycle(self) -> dict:
        """Run complete monitoring cycle"""
        logger.info("🔍 Starting diagnostic monitoring cycle")

        # Parse current diagnostic state
        current_data = self.analyzer.parse_current_diagnostic()

        if not current_data:
            logger.warning("No current diagnostic data available")
            return {"status": "no_data"}

        # Analyze trends
        trend_analysis = self.analyzer.analyze_trends(current_data)

        # Process alerts
        for alert in trend_analysis.get("alerts", []):
            self.alert_manager.send_alert(alert, current_data)

        # Add to historical tracking
        self.analyzer.add_current_entry(current_data)

        # Generate monitoring report
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_state": current_data,
            "trend_analysis": trend_analysis,
            "alert_count": len(trend_analysis.get("alerts", [])),
            "status": "completed",
        }

        # Save monitoring report
        self.save_monitoring_report(report)

        logger.info(f"🔍 Monitoring cycle complete: {report['alert_count']} alerts")
        return report

    def save_monitoring_report(self, report: dict):
        """Save monitoring report"""
        MONITORING_DIR.mkdir(parents=True, exist_ok=True)

        # Save latest report
        latest_report = MONITORING_DIR / "latest_monitoring_report.json"
        latest_report.write_text(json.dumps(report, indent=2))

        # Save timestamped report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_report = MONITORING_DIR / f"monitoring_{timestamp}.json"
        timestamped_report.write_text(json.dumps(report, indent=2))


def main():
    """CLI interface for diagnostic monitor"""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnostic continuous monitor")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    monitor = DiagnosticMonitor()
    report = monitor.run_monitoring_cycle()

    # Print summary
    print("\n🔍 DIAGNOSTIC MONITORING RESULTS")
    print("===============================")
    print(f"Status: {report.get('status', 'unknown')}")
    print(f"Alerts generated: {report.get('alert_count', 0)}")

    if report.get("current_state"):
        current = report["current_state"]
        total_errors = sum(current.get("errors", {}).values())
        print(f"Current error count: {total_errors}")

        test_metrics = current.get("test_metrics", {})
        if test_metrics.get("collection_rate"):
            print(f"Test collection rate: {test_metrics['collection_rate']:.1f}%")

    trend_analysis = report.get("trend_analysis", {})
    if trend_analysis.get("error_trends"):
        print(f"Error trends: {len(trend_analysis['error_trends'])} categories monitored")

    return 0 if report.get("alert_count", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
