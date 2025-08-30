#!/usr/bin/env python3
"""
Advanced Ethics Export & Reporting Utility - ELEVATED VERSION
============================================================
Multi-format export system with dashboard data preparation,
audit trail generation, and governance integration.

Features:
- ✅ Multi-format export (JSON/YAML/CSV/HTML)
- ✅ Dashboard data preparation
- ✅ Audit trail generation with timestamps
- ✅ Compliance reporting formats
- ✅ Real-time alerting integration
- ✅ Governance board summaries
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml


class EthicsReportExporter:
    """Professional ethics reporting utility with multi-format support."""

    def __init__(self, output_base_dir: str = "ethics_reports"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different report types
        (self.output_base_dir / "json").mkdir(exist_ok=True)
        (self.output_base_dir / "yaml").mkdir(exist_ok=True)
        (self.output_base_dir / "csv").mkdir(exist_ok=True)
        (self.output_base_dir / "html").mkdir(exist_ok=True)
        (self.output_base_dir / "dashboard").mkdir(exist_ok=True)
        (self.output_base_dir / "audit").mkdir(exist_ok=True)

    def export_multi_format(
        self,
        result: dict[str, Any],
        formats: list[str] = None,
        base_filename: Optional[str] = None,
    ) -> dict[str, str]:
        """Export ethics report in multiple formats simultaneously."""

        if formats is None:
            formats = ["json", "yaml", "csv"]
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_index = result.get("trace_index", "unknown")
            base_filename = f"ethics_drift_{trace_index}_{timestamp}"

        exported_files = {}

        for format_type in formats:
            try:
                if format_type == "json":
                    filepath = self._export_json(result, base_filename)
                elif format_type == "yaml":
                    filepath = self._export_yaml(result, base_filename)
                elif format_type == "csv":
                    filepath = self._export_csv(result, base_filename)
                elif format_type == "html":
                    filepath = self._export_html(result, base_filename)
                else:
                    print(f"⚠️  Unsupported format: {format_type}")
                    continue

                exported_files[format_type] = filepath
                print(f"✅ {format_type.upper()} report exported: {filepath}")

            except Exception as e:
                print(f"❌ Failed to export {format_type}: {e}")

        return exported_files

    def _export_json(self, result: dict, base_filename: str) -> str:
        """Export comprehensive JSON report."""
        filepath = self.output_base_dir / "json" / f"{base_filename}.json"
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return str(filepath)

    def _export_yaml(self, result: dict, base_filename: str) -> str:
        """Export YAML format for configuration management."""
        filepath = self.output_base_dir / "yaml" / f"{base_filename}.yaml"
        with open(filepath, "w") as f:
            yaml.safe_dump(result, f, default_flow_style=False, allow_unicode=True)
        return str(filepath)

    def _export_csv(self, result: dict, base_filename: str) -> str:
        """Export CSV format for spreadsheet analysis."""
        filepath = self.output_base_dir / "csv" / f"{base_filename}.csv"

        # Extract violations for CSV format
        violations = result.get("violations", [])

        with open(filepath, "w", newline="") as f:
            if violations:
                fieldnames = [
                    "attribute",
                    "from_value",
                    "to_value",
                    "severity",
                    "tags",
                    "threshold_applied",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for violation in violations:
                    writer.writerow(
                        {
                            "attribute": violation.get("attribute", ""),
                            "from_value": str(violation.get("from", "")),
                            "to_value": str(violation.get("to", "")),
                            "severity": violation.get("severity", ""),
                            "tags": ", ".join(violation.get("tags", [])),
                            "threshold_applied": violation.get("threshold_applied", ""),
                        }
                    )
            else:
                # Write summary if no violations
                writer = csv.writer(f)
                writer.writerow(["Summary", "Value"])
                writer.writerow(["Drift Score", result.get("drift_score", 0)])
                writer.writerow(
                    [
                        "Status",
                        result.get("ethics_assessment", {}).get("status", "UNKNOWN"),
                    ]
                )
                writer.writerow(["Timestamp", result.get("timestamp", "")])

        return str(filepath)

    def _export_html(self, result: dict, base_filename: str) -> str:
        """Export HTML report for human-readable governance review."""
        filepath = self.output_base_dir / "html" / f"{base_filename}.html"

        html_content = self._generate_html_report(result)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(filepath)

    def _generate_html_report(self, result: dict) -> str:
        """Generate comprehensive HTML report."""
        ethics_assessment = result.get("ethics_assessment", {})
        escalation = result.get("escalation", {})
        violations = result.get("violations", [])

        status = ethics_assessment.get("status", "UNKNOWN")
        status_color = {
            "NORMAL": "#28a745",
            "WARNING": "#ffc107",
            "CRITICAL": "#dc3545",
        }.get(status, "#6c757d")

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Ethics Drift Report - {result.get("trace_index", "Unknown")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .status-badge {{ display: inline-block; background: {status_color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .metric-box {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .violation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 5px 0; }}
        .critical {{ border-left-color: #dc3545; background: #f8d7da; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 LUKHAS Ethics Drift Report</h1>
            <p><strong>Trace Index:</strong> {result.get("trace_index", "Unknown")}</p>
            <p><strong>Generated:</strong> {result.get("timestamp", "Unknown")}</p>
        </div>

        <div class="metric-box">
            <h2>Overall Assessment</h2>
            <p><strong>Status:</strong> <span class="status-badge">{status}</span></p>
            <p><strong>Drift Score:</strong> {result.get("drift_score", 0)}</p>
            <p><strong>Confidence:</strong> {ethics_assessment.get("confidence", "N/A")}</p>
            <p><strong>Recommendation:</strong> {ethics_assessment.get("recommendation", "No recommendation")}</p>
        </div>

        <div class="metric-box">
            <h2>Escalation Information</h2>
            <p><strong>Escalation Triggered:</strong> {"Yes" if escalation.get("escalation_triggered", False) else "No"}</p>
            <p><strong>Level:</strong> {escalation.get("escalation_level", "None")}</p>
            <p><strong>Actions Required:</strong> {", ".join(escalation.get("actions_required", []))}</p>
            <p><strong>Notifications:</strong> {", ".join(escalation.get("notifications", []))}</p>
        </div>
        """

        if violations:
            html += """
        <div class="metric-box">
            <h2>Violations Detected</h2>
            <table>
                <thead>
                    <tr>
                        <th>Attribute</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Severity</th>
                        <th>Tags</th>
                    </tr>
                </thead>
                <tbody>
            """

            for violation in violations:
                severity = violation.get("severity", "LOW")
                css_class = "critical" if severity in ["CRITICAL", "HIGH"] else "violation"
                html += f"""
                    <tr class="{css_class}">
                        <td>{violation.get("attribute", "")}</td>
                        <td>{violation.get("from", "")}</td>
                        <td>{violation.get("to", "")}</td>
                        <td>{severity}</td>
                        <td>{", ".join(violation.get("tags", []))}</td>
                    </tr>
                """

            html += """
                </tbody>
            </table>
        </div>
            """

        html += (
            """
        <div class="metric-box">
            <h2>System Information</h2>
            <p><strong>Version:</strong> """
            + str(result.get("system_info", {}).get("version", "Unknown"))
            + """</p>
            <p><strong>Agent:</strong> """
            + str(result.get("agent", "Unknown"))
            + """</p>
            <p><strong>Capabilities:</strong> """
            + str(", ".join(result.get("system_info", {}).get("capabilities", [])))
            + """</p>
        </div>
    </div>
</body>
</html>
        """
        )

        return html

    def generate_dashboard_data(self, result: dict) -> dict[str, Any]:
        """Generate dashboard-ready data structure."""
        dashboard_data = {
            "summary": {
                "drift_score": result.get("drift_score", 0),
                "status": result.get("ethics_assessment", {}).get("status", "UNKNOWN"),
                "violation_count": result.get("violation_count", 0),
                "escalation_triggered": result.get("escalation", {}).get(
                    "escalation_triggered", False
                ),
                "timestamp": result.get("timestamp", ""),
            },
            "metrics": {
                "confidence": result.get("ethics_assessment", {}).get("confidence", 0),
                "escalation_level": result.get("escalation", {}).get("escalation_level", "none"),
            },
            "violations_by_severity": self._group_violations_by_severity(
                result.get("violations", [])
            ),
            "violations_by_attribute": self._group_violations_by_attribute(
                result.get("violations", [])
            ),
            "trend_data": {
                "trace_index": result.get("trace_index", ""),
                "collapse_hash": result.get("collapse_hash", ""),
                "context_id": result.get("context_id", ""),
            },
        }

        # Export dashboard data
        dashboard_file = (
            self.output_base_dir
            / "dashboard"
            / f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(dashboard_file, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        print(f"📊 Dashboard data exported: {dashboard_file}")
        return dashboard_data

    def _group_violations_by_severity(self, violations: list[dict]) -> dict[str, int]:
        """Group violations by severity for dashboard charts."""
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for violation in violations:
            severity = violation.get("severity", "LOW")
            if severity in severity_counts:
                severity_counts[severity] += 1
        return severity_counts

    def _group_violations_by_attribute(self, violations: list[dict]) -> dict[str, int]:
        """Group violations by ethical attribute for analysis."""
        attribute_counts = {}
        for violation in violations:
            attribute = violation.get("attribute", "unknown")
            attribute_counts[attribute] = attribute_counts.get(attribute, 0) + 1
        return attribute_counts

    def generate_audit_trail(self, result: dict) -> str:
        """Generate comprehensive audit trail entry."""
        audit_entry = {
            "audit_id": hashlib.sha256(
                f"{result.get('trace_index', '')}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_index": result.get("trace_index", ""),
            "drift_score": result.get("drift_score", 0),
            "status": result.get("ethics_assessment", {}).get("status", "UNKNOWN"),
            "escalation_triggered": result.get("escalation", {}).get("escalation_triggered", False),
            "violation_count": result.get("violation_count", 0),
            "agent": result.get("agent", ""),
            "context_id": result.get("context_id", ""),
            "governance_compliance": {
                "reviewed": False,
                "approved_by": None,
                "compliance_notes": "",
            },
        }

        # Append to audit log
        audit_file = self.output_base_dir / "audit" / "ethics_audit_trail.jsonl"
        with open(audit_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\n")

        print(f"📋 Audit trail entry added: {audit_entry['audit_id']}")
        return audit_entry["audit_id"]

    def generate_governance_summary(self, results: list[dict]) -> dict[str, Any]:
        """Generate executive summary for governance board."""
        if not results:
            return {"error": "No results provided for governance summary"}

        total_reports = len(results)
        critical_incidents = sum(
            1 for r in results if r.get("ethics_assessment", {}).get("status") == "CRITICAL"
        )
        warning_incidents = sum(
            1 for r in results if r.get("ethics_assessment", {}).get("status") == "WARNING"
        )
        escalations = sum(
            1 for r in results if r.get("escalation", {}).get("escalation_triggered", False)
        )
        avg_drift_score = (
            sum(r.get("drift_score", 0) for r in results) / total_reports
            if total_reports > 0
            else 0
        )

        governance_summary = {
            "report_period": {
                "start": min(r.get("timestamp", "") for r in results),
                "end": max(r.get("timestamp", "") for r in results),
                "total_reports": total_reports,
            },
            "risk_assessment": {
                "critical_incidents": critical_incidents,
                "warning_incidents": warning_incidents,
                "normal_operations": total_reports - critical_incidents - warning_incidents,
                "escalations_triggered": escalations,
                "average_drift_score": round(avg_drift_score, 2),
            },
            "recommendations": self._generate_governance_recommendations(
                critical_incidents, warning_incidents, avg_drift_score
            ),
            "compliance_status": (
                "COMPLIANT"
                if critical_incidents == 0 and avg_drift_score < 3
                else "REVIEW_REQUIRED"
            ),
        }

        # Export governance summary
        governance_file = (
            self.output_base_dir
            / f"governance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(governance_file, "w") as f:
            json.dump(governance_summary, f, indent=2)

        print(f"🏛️  Governance summary exported: {governance_file}")
        return governance_summary

    def _generate_governance_recommendations(
        self, critical: int, warnings: int, avg_score: float
    ) -> list[str]:
        """Generate actionable recommendations for governance."""
        recommendations = []

        if critical > 0:
            recommendations.append(
                "IMMEDIATE: Review critical incidents and implement corrective measures"
            )
        if warnings > 5:
            recommendations.append(
                "ATTENTION: High number of warnings indicate systemic issues requiring review"
            )
        if avg_score > 3:
            recommendations.append(
                "POLICY: Consider updating ethical thresholds and monitoring protocols"
            )
        if critical == 0 and warnings < 3 and avg_score < 2:
            recommendations.append("NORMAL: Ethics monitoring within acceptable parameters")

        return recommendations


# Legacy compatibility function
def export_ethics_report(result: dict, filepath: str = "ethics_report.json"):
    """Legacy function for backward compatibility."""
    exporter = EthicsReportExporter()
    exported_files = exporter.export_multi_format(result, ["json"])
    if "json" in exported_files:
        print(f"✅ Ethics report exported to {exported_files['json']}")
        return exported_files["json"]
    return None


# Enhanced main export function
def export_comprehensive_ethics_report(
    result: dict[str, Any],
    formats: list[str] = None,
    include_dashboard: bool = True,
    include_audit: bool = True,
) -> dict[str, Any]:
    """
    Comprehensive ethics report export with all advanced features.

    Args:
        result: Ethics drift detection result
        formats: List of export formats (json, yaml, csv, html)
        include_dashboard: Generate dashboard data
        include_audit: Add audit trail entry

    Returns:
        Dictionary with export paths and metadata
    """
    if formats is None:
        formats = ["json", "yaml", "html"]
    exporter = EthicsReportExporter()

    export_info = {
        "exported_files": exporter.export_multi_format(result, formats),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if include_dashboard:
        export_info["dashboard_data"] = exporter.generate_dashboard_data(result)

    if include_audit:
        export_info["audit_id"] = exporter.generate_audit_trail(result)

    return export_info


if __name__ == "__main__":
    # Example usage demonstration
    sample_result = {
        "drift_score": 3.5,
        "violations": [
            {
                "attribute": "honesty",
                "from": True,
                "to": False,
                "severity": "HIGH",
                "tags": ["truth", "alignment"],
            }
        ],
        "violation_count": 1,
        "escalation": {
            "escalation_triggered": True,
            "escalation_level": "MEDIUM",
            "actions_required": ["HUMAN_REVIEW_REQUIRED"],
        },
        "trace_index": "eth_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ethics_assessment": {
            "status": "WARNING",
            "confidence": 0.95,
            "recommendation": "Human ethics review needed",
        },
    }

    print("🧠 Demonstrating Elevated Ethics Export System:")
    export_info = export_comprehensive_ethics_report(sample_result)
    print(json.dumps(export_info, indent=2))
