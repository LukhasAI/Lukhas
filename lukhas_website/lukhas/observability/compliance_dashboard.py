#!/usr/bin/env python3
"""
LUKHAS Compliance Dashboard
Regulatory audit trail visualization and compliance monitoring dashboard.

Features:
- Real-time compliance status monitoring
- Regulatory audit trail visualization
- Evidence integrity verification dashboard
- Compliance violation tracking and remediation
- GDPR/CCPA/SOX/HIPAA compliance reporting
- Executive compliance summary reports
- Interactive compliance analytics
"""

import asyncio
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

try:
    import pandas as pd  # noqa: F401  # TODO: pandas; consider using importl...
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-GUI backend
    import matplotlib.pyplot as plt
    import seaborn as sns  # noqa: F401  # TODO: seaborn; consider using import...
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

from .advanced_metrics import get_advanced_metrics
from .evidence_collection import ComplianceRegime, EvidenceType, get_evidence_engine
from .intelligent_alerting import get_alerting_system


@dataclass
class ComplianceStatus:
    """Current compliance status for a regulation"""
    regulation: ComplianceRegime
    overall_compliance_score: float  # 0.0 to 100.0
    total_evidence_records: int
    verified_evidence_records: int
    compliance_violations: int
    last_violation_date: Optional[datetime]
    audit_trail_completeness: float  # Percentage
    retention_compliance: bool
    data_integrity_score: float
    last_assessment: datetime
    critical_findings: List[str] = field(default_factory=list)
    remediation_actions: List[str] = field(default_factory=list)


@dataclass
class ComplianceMetric:
    """Individual compliance metric tracking"""
    metric_name: str
    regulation: ComplianceRegime
    current_value: float
    target_value: float
    tolerance: float
    last_updated: datetime
    trend_direction: str  # "improving", "degrading", "stable"
    historical_values: List[Tuple[datetime, float]] = field(default_factory=list)


@dataclass
class AuditReport:
    """Generated compliance audit report"""
    report_id: str
    regulation: ComplianceRegime
    report_type: str  # "daily", "weekly", "monthly", "quarterly", "annual"
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    compliance_score: float
    total_evidence_examined: int
    violations_found: int
    critical_issues: List[str]
    recommendations: List[str]
    report_data: Dict[str, Any]
    report_file_path: Optional[str] = None


class ComplianceDashboard:
    """
    Comprehensive compliance dashboard for regulatory audit trail visualization.
    Provides real-time monitoring and reporting for GDPR, CCPA, SOX, and other regulations.
    """

    def __init__(
        self,
        dashboard_config_path: str = "./config/compliance_dashboard.json",
        reports_output_path: str = "./artifacts/compliance_reports",
        enable_automated_reports: bool = True,
        report_retention_days: int = 2555,  # 7 years
    ):
        """
        Initialize compliance dashboard.

        Args:
            dashboard_config_path: Path to dashboard configuration
            reports_output_path: Path for generated compliance reports
            enable_automated_reports: Enable automated report generation
            report_retention_days: Days to retain compliance reports
        """
        self.config_path = Path(dashboard_config_path)
        self.reports_path = Path(reports_output_path)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.enable_automated_reports = enable_automated_reports
        self.report_retention_days = report_retention_days

        # Integration with observability systems
        self.evidence_engine = get_evidence_engine()
        self.advanced_metrics = get_advanced_metrics()
        self.alerting_system = get_alerting_system()

        # Compliance state
        self.compliance_statuses: Dict[ComplianceRegime, ComplianceStatus] = {}
        self.compliance_metrics: Dict[str, ComplianceMetric] = {}
        self.audit_reports: List[AuditReport] = []

        # Dashboard configuration
        self.dashboard_config = self._load_dashboard_config()

        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._reporting_task: Optional[asyncio.Task] = None

        # Initialize compliance tracking
        self._initialize_compliance_tracking()
        self._start_background_tasks()

    def _load_dashboard_config(self) -> Dict[str, Any]:
        """Load dashboard configuration"""
        default_config = {
            "regulations": ["GDPR", "CCPA", "SOX", "INTERNAL"],
            "metrics": {
                "evidence_integrity_threshold": 99.99,
                "audit_trail_completeness_threshold": 100.0,
                "retention_compliance_grace_days": 30,
                "violation_escalation_threshold": 5,
            },
            "reporting": {
                "daily_reports": True,
                "weekly_reports": True,
                "monthly_reports": True,
                "quarterly_reports": True,
                "annual_reports": True,
                "executive_summary": True,
            },
            "alerting": {
                "compliance_violation_alert": True,
                "retention_violation_alert": True,
                "integrity_failure_alert": True,
                "audit_trail_gap_alert": True,
            }
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                print(f"Warning: Failed to load dashboard config: {e}")

        # Save default config
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _initialize_compliance_tracking(self):
        """Initialize compliance status tracking for all regulations"""
        for regulation_name in self.dashboard_config["regulations"]:
            try:
                regulation = ComplianceRegime(regulation_name.lower())
                self.compliance_statuses[regulation] = ComplianceStatus(
                    regulation=regulation,
                    overall_compliance_score=100.0,
                    total_evidence_records=0,
                    verified_evidence_records=0,
                    compliance_violations=0,
                    last_violation_date=None,
                    audit_trail_completeness=100.0,
                    retention_compliance=True,
                    data_integrity_score=100.0,
                    last_assessment=datetime.now(timezone.utc),
                )
            except ValueError:
                print(f"Warning: Unknown compliance regime: {regulation_name}")

        # Initialize compliance metrics
        self._initialize_compliance_metrics()

    def _initialize_compliance_metrics(self):
        """Initialize specific compliance metrics for monitoring"""
        metrics_config = [
            {
                "name": "evidence_integrity_rate",
                "regulation": ComplianceRegime.SOX,
                "target": 99.99,
                "tolerance": 0.01,
            },
            {
                "name": "audit_trail_completeness",
                "regulation": ComplianceRegime.SOX,
                "target": 100.0,
                "tolerance": 0.0,
            },
            {
                "name": "gdpr_retention_compliance",
                "regulation": ComplianceRegime.GDPR,
                "target": 100.0,
                "tolerance": 5.0,  # 5% tolerance for retention
            },
            {
                "name": "ccpa_response_time_compliance",
                "regulation": ComplianceRegime.CCPA,
                "target": 95.0,  # 95% of requests within time limit
                "tolerance": 5.0,
            },
            {
                "name": "data_breach_notification_compliance",
                "regulation": ComplianceRegime.GDPR,
                "target": 100.0,
                "tolerance": 0.0,
            },
        ]

        for metric_config in metrics_config:
            metric = ComplianceMetric(
                metric_name=metric_config["name"],
                regulation=metric_config["regulation"],
                current_value=metric_config["target"],
                target_value=metric_config["target"],
                tolerance=metric_config["tolerance"],
                last_updated=datetime.now(timezone.utc),
                trend_direction="stable",
            )
            self.compliance_metrics[metric_config["name"]] = metric

    async def assess_compliance_status(self, regulation: ComplianceRegime) -> ComplianceStatus:
        """
        Perform comprehensive compliance assessment for a regulation.

        Args:
            regulation: Compliance regime to assess

        Returns:
            Current compliance status
        """
        status = self.compliance_statuses.get(regulation)
        if not status:
            return None

        # Assess evidence integrity and completeness
        evidence_stats = await self._assess_evidence_integrity(regulation)
        audit_completeness = await self._assess_audit_trail_completeness(regulation)
        retention_compliance = await self._assess_retention_compliance(regulation)
        violation_count = await self._count_compliance_violations(regulation)

        # Calculate overall compliance score
        overall_score = self._calculate_compliance_score(
            evidence_stats["integrity_score"],
            audit_completeness,
            retention_compliance,
            violation_count
        )

        # Update status
        status.overall_compliance_score = overall_score
        status.total_evidence_records = evidence_stats["total_records"]
        status.verified_evidence_records = evidence_stats["verified_records"]
        status.compliance_violations = violation_count
        status.audit_trail_completeness = audit_completeness
        status.retention_compliance = retention_compliance > 95.0
        status.data_integrity_score = evidence_stats["integrity_score"]
        status.last_assessment = datetime.now(timezone.utc)

        # Update critical findings and remediation actions
        await self._update_compliance_findings(status)

        self.compliance_statuses[regulation] = status
        return status

    async def _assess_evidence_integrity(self, regulation: ComplianceRegime) -> Dict[str, Any]:
        """Assess evidence integrity for a specific regulation"""
        total_records = 0
        verified_records = 0
        integrity_failures = 0

        # Query evidence records for this regulation
        async for evidence in self.evidence_engine.query_evidence(
            start_time=datetime.now(timezone.utc) - timedelta(days=30),  # Last 30 days
            limit=10000
        ):
            if regulation in evidence.compliance_regimes:
                total_records += 1

                # Verify evidence integrity
                if self.evidence_engine.verify_evidence(evidence):
                    verified_records += 1
                else:
                    integrity_failures += 1

        integrity_score = (verified_records / total_records * 100) if total_records > 0 else 100.0

        return {
            "total_records": total_records,
            "verified_records": verified_records,
            "integrity_failures": integrity_failures,
            "integrity_score": integrity_score,
        }

    async def _assess_audit_trail_completeness(self, regulation: ComplianceRegime) -> float:
        """Assess audit trail completeness"""
        # This is a simplified assessment - in practice would check for gaps
        # in the audit trail, missing mandatory events, etc.

        # Check for critical system events
        critical_events = [
            "authentication",
            "data_access",
            "ai_decision",
            "user_interaction",
        ]

        completeness_scores = []
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)  # Last week

        for event_type in critical_events:
            try:
                evidence_type = EvidenceType(event_type)
                count = 0
                async for evidence in self.evidence_engine.query_evidence(
                    evidence_type=evidence_type,
                    start_time=start_time,
                    end_time=end_time,
                    limit=1000
                ):
                    if regulation in evidence.compliance_regimes:
                        count += 1

                # Simple scoring: if we have evidence, it's complete
                completeness_scores.append(100.0 if count > 0 else 0.0)

            except ValueError:
                # Skip invalid evidence types
                continue

        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 100.0

    async def _assess_retention_compliance(self, regulation: ComplianceRegime) -> float:
        """Assess data retention compliance"""
        # Check if any evidence is being retained beyond regulation requirements
        violations = 0
        total_checked = 0

        # Define retention limits by regulation
        retention_limits = {
            ComplianceRegime.GDPR: timedelta(days=2555),  # 7 years max
            ComplianceRegime.CCPA: timedelta(days=1095),  # 3 years typical
            ComplianceRegime.SOX: timedelta(days=2555),   # 7 years
            ComplianceRegime.INTERNAL: timedelta(days=365),  # 1 year default
        }

        limit = retention_limits.get(regulation, timedelta(days=365))
        cutoff_date = datetime.now(timezone.utc) - limit

        async for evidence in self.evidence_engine.query_evidence(
            end_time=cutoff_date,
            limit=1000
        ):
            if regulation in evidence.compliance_regimes:
                total_checked += 1
                # If evidence is still present beyond retention period, it's a violation
                violations += 1

        compliance_rate = ((total_checked - violations) / total_checked * 100) if total_checked > 0 else 100.0
        return compliance_rate

    async def _count_compliance_violations(self, regulation: ComplianceRegime) -> int:
        """Count recent compliance violations"""
        violation_count = 0

        # Check for violations in evidence records
        async for evidence in self.evidence_engine.query_evidence(
            evidence_type=EvidenceType.REGULATORY_EVENT,
            start_time=datetime.now(timezone.utc) - timedelta(days=30),
            limit=1000
        ):
            if (regulation in evidence.compliance_regimes and
                evidence.operation == "compliance_violation"):
                violation_count += 1

        return violation_count

    def _calculate_compliance_score(
        self,
        integrity_score: float,
        audit_completeness: float,
        retention_compliance: float,
        violation_count: int,
    ) -> float:
        """Calculate overall compliance score"""
        # Weighted scoring
        base_score = (
            integrity_score * 0.4 +
            audit_completeness * 0.3 +
            retention_compliance * 0.3
        )

        # Penalty for violations
        violation_penalty = min(violation_count * 5, 50)  # Max 50 point penalty

        final_score = max(0, base_score - violation_penalty)
        return final_score

    async def _update_compliance_findings(self, status: ComplianceStatus):
        """Update critical findings and remediation actions"""
        status.critical_findings.clear()
        status.remediation_actions.clear()

        # Check for critical issues
        if status.overall_compliance_score < 95:
            status.critical_findings.append("Overall compliance score below 95%")
            status.remediation_actions.append("Conduct immediate compliance review and remediation")

        if status.data_integrity_score < 99:
            status.critical_findings.append("Evidence integrity issues detected")
            status.remediation_actions.append("Investigate and repair evidence integrity failures")

        if status.compliance_violations > 5:
            status.critical_findings.append(f"{status.compliance_violations} compliance violations in recent period")
            status.remediation_actions.append("Implement process improvements to prevent violations")

        if status.audit_trail_completeness < 100:
            status.critical_findings.append("Audit trail gaps identified")
            status.remediation_actions.append("Review and enhance audit logging coverage")

        if not status.retention_compliance:
            status.critical_findings.append("Data retention policy violations")
            status.remediation_actions.append("Implement automated data retention management")

    async def generate_compliance_report(
        self,
        regulation: ComplianceRegime,
        report_type: str = "monthly",
        custom_period: Optional[Tuple[datetime, datetime]] = None,
    ) -> AuditReport:
        """
        Generate comprehensive compliance audit report.

        Args:
            regulation: Compliance regime for the report
            report_type: Type of report (daily, weekly, monthly, quarterly, annual)
            custom_period: Custom reporting period (start, end)

        Returns:
            Generated audit report
        """
        # Determine reporting period
        if custom_period:
            period_start, period_end = custom_period
        else:
            period_end = datetime.now(timezone.utc)
            if report_type == "daily":
                period_start = period_end - timedelta(days=1)
            elif report_type == "weekly":
                period_start = period_end - timedelta(days=7)
            elif report_type == "monthly":
                period_start = period_end - timedelta(days=30)
            elif report_type == "quarterly":
                period_start = period_end - timedelta(days=90)
            elif report_type == "annual":
                period_start = period_end - timedelta(days=365)
            else:
                period_start = period_end - timedelta(days=30)

        # Assess current compliance status
        compliance_status = await self.assess_compliance_status(regulation)

        # Collect evidence statistics for the period
        evidence_stats = await self._collect_evidence_statistics(
            regulation, period_start, period_end
        )

        # Generate report data
        report_data = {
            "regulation": regulation.value,
            "compliance_score": compliance_status.overall_compliance_score,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "evidence_statistics": evidence_stats,
            "compliance_status": asdict(compliance_status),
            "key_metrics": self._get_key_metrics_for_period(regulation, period_start, period_end),
            "trend_analysis": await self._generate_trend_analysis(regulation, period_start, period_end),
            "risk_assessment": self._assess_compliance_risks(compliance_status),
        }

        # Create audit report
        report = AuditReport(
            report_id=str(uuid4()),
            regulation=regulation,
            report_type=report_type,
            generated_at=datetime.now(timezone.utc),
            period_start=period_start,
            period_end=period_end,
            compliance_score=compliance_status.overall_compliance_score,
            total_evidence_examined=evidence_stats.get("total_evidence", 0),
            violations_found=compliance_status.compliance_violations,
            critical_issues=compliance_status.critical_findings.copy(),
            recommendations=compliance_status.remediation_actions.copy(),
            report_data=report_data,
        )

        # Generate report file
        report_file = await self._generate_report_file(report)
        report.report_file_path = str(report_file) if report_file else None

        self.audit_reports.append(report)
        return report

    async def _collect_evidence_statistics(
        self,
        regulation: ComplianceRegime,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, Any]:
        """Collect evidence statistics for reporting period"""
        stats = {
            "total_evidence": 0,
            "by_type": defaultdict(int),
            "by_component": defaultdict(int),
            "integrity_verified": 0,
            "integrity_failed": 0,
            "user_interactions": 0,
            "ai_decisions": 0,
            "data_access_events": 0,
            "system_events": 0,
        }

        async for evidence in self.evidence_engine.query_evidence(
            start_time=start_time,
            end_time=end_time,
            limit=50000
        ):
            if regulation in evidence.compliance_regimes:
                stats["total_evidence"] += 1
                stats["by_type"][evidence.evidence_type.value] += 1
                stats["by_component"][evidence.source_component] += 1

                # Verify integrity
                if self.evidence_engine.verify_evidence(evidence):
                    stats["integrity_verified"] += 1
                else:
                    stats["integrity_failed"] += 1

                # Count specific event types
                if evidence.evidence_type == EvidenceType.USER_INTERACTION:
                    stats["user_interactions"] += 1
                elif evidence.evidence_type == EvidenceType.AI_DECISION:
                    stats["ai_decisions"] += 1
                elif evidence.evidence_type == EvidenceType.DATA_ACCESS:
                    stats["data_access_events"] += 1
                elif evidence.evidence_type == EvidenceType.SYSTEM_EVENT:
                    stats["system_events"] += 1

        return dict(stats)

    def _get_key_metrics_for_period(
        self,
        regulation: ComplianceRegime,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, float]:
        """Get key compliance metrics for the reporting period"""
        metrics = {}

        for metric_name, metric in self.compliance_metrics.items():
            if metric.regulation == regulation:
                # Get metric value for the period (simplified - use current value)
                metrics[metric_name] = {
                    "current_value": metric.current_value,
                    "target_value": metric.target_value,
                    "compliance": metric.current_value >= (metric.target_value - metric.tolerance),
                    "trend": metric.trend_direction,
                }

        return metrics

    async def _generate_trend_analysis(
        self,
        regulation: ComplianceRegime,
        start_time: datetime,
        end_time: datetime,
    ) -> Dict[str, Any]:
        """Generate trend analysis for compliance metrics"""
        # This is a simplified trend analysis
        # In practice, would analyze historical compliance data

        compliance_status = self.compliance_statuses.get(regulation)
        if not compliance_status:
            return {}

        return {
            "compliance_score_trend": "stable",  # Would calculate from historical data
            "violation_trend": "improving" if compliance_status.compliance_violations < 5 else "degrading",
            "evidence_integrity_trend": "stable",
            "key_observations": [
                f"Current compliance score: {compliance_status.overall_compliance_score:.2f}%",
                f"Evidence integrity rate: {compliance_status.data_integrity_score:.2f}%",
                f"Recent violations: {compliance_status.compliance_violations}",
            ],
        }

    def _assess_compliance_risks(self, status: ComplianceStatus) -> Dict[str, Any]:
        """Assess compliance risks and provide risk ratings"""
        risks = {
            "overall_risk": "low",
            "risk_factors": [],
            "mitigation_priority": "normal",
        }

        # Risk assessment based on compliance score
        if status.overall_compliance_score < 90:
            risks["overall_risk"] = "high"
            risks["risk_factors"].append("Low overall compliance score")
            risks["mitigation_priority"] = "urgent"
        elif status.overall_compliance_score < 95:
            risks["overall_risk"] = "medium"
            risks["risk_factors"].append("Below-target compliance score")
            risks["mitigation_priority"] = "high"

        # Additional risk factors
        if status.compliance_violations > 10:
            risks["risk_factors"].append("High violation count")
            risks["mitigation_priority"] = "urgent"

        if status.data_integrity_score < 99:
            risks["risk_factors"].append("Evidence integrity concerns")
            if risks["overall_risk"] == "low":
                risks["overall_risk"] = "medium"

        if not status.retention_compliance:
            risks["risk_factors"].append("Retention policy violations")
            risks["mitigation_priority"] = "high"

        return risks

    async def _generate_report_file(self, report: AuditReport) -> Optional[Path]:
        """Generate physical report file (JSON and optionally PDF)"""
        try:
            # Create report directory
            report_dir = self.reports_path / report.regulation.value / report.report_type
            report_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = f"compliance_report_{report.regulation.value}_{report.report_type}_{report.generated_at.strftime('%Y%m%d_%H%M%S')}"

            # Save JSON report
            json_file = report_dir / f"{filename}.json"
            with open(json_file, 'w') as f:
                json.dump(asdict(report), f, indent=2, default=str)

            # Generate charts if plotting is available
            if PLOTTING_AVAILABLE:
                await self._generate_report_charts(report, report_dir / f"{filename}_charts")

            return json_file

        except Exception as e:
            print(f"Error generating report file: {e}")
            return None

    async def _generate_report_charts(self, report: AuditReport, chart_dir: Path):
        """Generate compliance report charts"""
        if not PLOTTING_AVAILABLE:
            return

        chart_dir.mkdir(exist_ok=True)

        try:
            # Compliance score gauge
            fig, ax = plt.subplots(figsize=(8, 6))
            score = report.compliance_score
            colors = ['red' if score < 90 else 'orange' if score < 95 else 'green']

            ax.pie([score, 100-score], startangle=90, colors=colors + ['lightgray'],
                  labels=[f'Compliant\n{score:.1f}%', f'Non-compliant\n{100-score:.1f}%'])
            ax.set_title(f'{report.regulation.value} Compliance Score')
            plt.savefig(chart_dir / 'compliance_score.png', dpi=150, bbox_inches='tight')
            plt.close()

            # Evidence statistics
            if 'evidence_statistics' in report.report_data:
                stats = report.report_data['evidence_statistics']

                if stats.get('by_type'):
                    fig, ax = plt.subplots(figsize=(10, 6))
                    types = list(stats['by_type'].keys())
                    counts = list(stats['by_type'].values())

                    ax.bar(types, counts)
                    ax.set_title('Evidence by Type')
                    ax.set_ylabel('Count')
                    plt.xticks(rotation=45)
                    plt.savefig(chart_dir / 'evidence_by_type.png', dpi=150, bbox_inches='tight')
                    plt.close()

        except Exception as e:
            print(f"Error generating charts: {e}")

    def get_compliance_dashboard_data(self) -> Dict[str, Any]:
        """Get current compliance dashboard data"""
        dashboard_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": {},
            "regulations": {},
            "key_metrics": {},
            "recent_violations": [],
            "critical_alerts": [],
        }

        # Overall compliance summary
        if self.compliance_statuses:
            scores = [status.overall_compliance_score for status in self.compliance_statuses.values()]
            dashboard_data["overall_status"] = {
                "average_compliance_score": sum(scores) / len(scores),
                "lowest_compliance_score": min(scores),
                "total_regulations_monitored": len(self.compliance_statuses),
                "regulations_at_risk": len([s for s in scores if s < 95]),
            }

        # Per-regulation status
        for regulation, status in self.compliance_statuses.items():
            dashboard_data["regulations"][regulation.value] = {
                "compliance_score": status.overall_compliance_score,
                "violations": status.compliance_violations,
                "last_assessment": status.last_assessment.isoformat(),
                "critical_findings": len(status.critical_findings),
                "risk_level": "high" if status.overall_compliance_score < 90 else
                            "medium" if status.overall_compliance_score < 95 else "low",
            }

        # Key metrics
        for metric_name, metric in self.compliance_metrics.items():
            dashboard_data["key_metrics"][metric_name] = {
                "regulation": metric.regulation.value,
                "current_value": metric.current_value,
                "target_value": metric.target_value,
                "status": "compliant" if metric.current_value >= (metric.target_value - metric.tolerance) else "non_compliant",
                "trend": metric.trend_direction,
            }

        return dashboard_data

    def _start_background_tasks(self):
        """Start background monitoring and reporting tasks"""
        async def monitoring_worker():
            while True:
                try:
                    # Assess compliance for all regulations
                    for regulation in self.compliance_statuses:
                        await self.assess_compliance_status(regulation)

                    await asyncio.sleep(300)  # Every 5 minutes
                except Exception as e:
                    print(f"Compliance monitoring error: {e}")
                    await asyncio.sleep(300)

        async def reporting_worker():
            while True:
                try:
                    if self.enable_automated_reports:
                        await self._generate_scheduled_reports()

                    await asyncio.sleep(3600)  # Check hourly for scheduled reports
                except Exception as e:
                    print(f"Compliance reporting error: {e}")
                    await asyncio.sleep(3600)

        # Start background tasks if event loop is available
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._monitoring_task = loop.create_task(monitoring_worker())
                self._reporting_task = loop.create_task(reporting_worker())
        except RuntimeError:
            # No event loop running
            pass

    async def _generate_scheduled_reports(self):
        """Generate scheduled compliance reports"""
        now = datetime.now(timezone.utc)

        # Generate daily reports at midnight
        if now.hour == 0 and now.minute < 10:
            for regulation in self.compliance_statuses:
                if self.dashboard_config["reporting"]["daily_reports"]:
                    await self.generate_compliance_report(regulation, "daily")

        # Generate weekly reports on Sundays
        if now.weekday() == 6 and now.hour == 1 and now.minute < 10:
            for regulation in self.compliance_statuses:
                if self.dashboard_config["reporting"]["weekly_reports"]:
                    await self.generate_compliance_report(regulation, "weekly")

        # Generate monthly reports on the 1st of each month
        if now.day == 1 and now.hour == 2 and now.minute < 10:
            for regulation in self.compliance_statuses:
                if self.dashboard_config["reporting"]["monthly_reports"]:
                    await self.generate_compliance_report(regulation, "monthly")

    async def shutdown(self):
        """Shutdown compliance dashboard"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._reporting_task:
            self._reporting_task.cancel()


# Global instance
_compliance_dashboard: Optional[ComplianceDashboard] = None


def initialize_compliance_dashboard(**kwargs) -> ComplianceDashboard:
    """Initialize global compliance dashboard"""
    global _compliance_dashboard
    _compliance_dashboard = ComplianceDashboard(**kwargs)
    return _compliance_dashboard


def get_compliance_dashboard() -> ComplianceDashboard:
    """Get or create global compliance dashboard"""
    global _compliance_dashboard
    if _compliance_dashboard is None:
        _compliance_dashboard = initialize_compliance_dashboard()
    return _compliance_dashboard


async def shutdown_compliance_dashboard():
    """Shutdown global compliance dashboard"""
    global _compliance_dashboard
    if _compliance_dashboard:
        await _compliance_dashboard.shutdown()
        _compliance_dashboard = None
