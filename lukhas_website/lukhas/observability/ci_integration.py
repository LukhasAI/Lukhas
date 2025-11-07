"""
CI/CD Observability Integration
==============================

P0-3 OBS-BURN: CI/CD pipeline integration for observability,
SLO monitoring, and deployment safety gates.

Features:
- Deployment safety checks based on SLO burn rates
- Pre/post-deployment SLO validation
- Automated rollback triggers
- Performance regression detection
- Integration with GitHub Actions, GitLab CI
- Observability evidence collection
"""
from __future__ import annotations

import asyncio
import json
import logging
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .burn_rate_alerts import BurnRateAlertManager, CIPipelineIntegration
from .service_metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class DeploymentStage(Enum):
    """Deployment pipeline stages"""
    PRE_DEPLOYMENT = "pre_deployment"
    DEPLOYMENT = "deployment"
    POST_DEPLOYMENT = "post_deployment"
    VALIDATION = "validation"
    ROLLBACK = "rollback"


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentContext:
    """Deployment context information"""
    service: str
    version: str
    environment: str
    deployment_id: str
    commit_sha: str
    branch: str
    initiated_by: str
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SLOValidationResult:
    """SLO validation result"""
    slo_name: str
    target_met: bool
    actual_value: float
    target_value: float
    measurement_window: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentReport:
    """Comprehensive deployment report"""
    context: DeploymentContext
    stage: DeploymentStage
    status: DeploymentStatus
    duration_seconds: float | None
    slo_validations: list[SLOValidationResult] = field(default_factory=list)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    safety_checks: dict[str, bool] = field(default_factory=dict)
    rollback_triggers: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class ObservabilityCIIntegration:
    """
    CI/CD pipeline integration for observability-driven deployments.

    Provides deployment safety gates, SLO validation, and automated
    rollback based on observability signals.
    """

    def __init__(self, alert_manager: BurnRateAlertManager):
        self.alert_manager = alert_manager
        self.pipeline_integration = CIPipelineIntegration(alert_manager)
        self.metrics_collector = get_metrics_collector()

        # Deployment tracking
        self.active_deployments: dict[str, DeploymentReport] = {}
        self.deployment_history: list[DeploymentReport] = []

        # Configuration
        self.config = self._load_config()

        logger.info("ObservabilityCIIntegration initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load CI integration configuration"""
        return {
            'slo_validation_window': '10m',
            'performance_baseline_window': '1h',
            'rollback_threshold_error_rate': 0.05,  # 5% error rate triggers rollback
            'rollback_threshold_latency_p95': 500,   # 500ms p95 triggers rollback
            'validation_timeout_minutes': 30,
            'artifact_retention_days': 30,
            'enable_auto_rollback': True
        }

    async def pre_deployment_check(self, context: DeploymentContext) -> DeploymentReport:
        """
        Execute pre-deployment safety checks.

        Validates:
        - Current SLO burn rates
        - Error budget availability
        - System health status
        - Recent deployment stability
        """
        logger.info(f"Starting pre-deployment check for {context.service}")

        report = DeploymentReport(
            context=context,
            stage=DeploymentStage.PRE_DEPLOYMENT,
            status=DeploymentStatus.RUNNING,
            duration_seconds=None
        )

        start_time = datetime.now(timezone.utc)

        try:
            # Check deployment safety
            is_safe, reason, details = self.pipeline_integration.check_deployment_safety(context.service)
            report.safety_checks['deployment_safe'] = is_safe

            if not is_safe:
                report.status = DeploymentStatus.FAILED
                report.recommendations.append(f"Deployment blocked: {reason}")
                report.recommendations.extend(details.get('recommendation', []))
                return report

            # Validate current SLOs
            slo_results = await self._validate_current_slos(context.service)
            report.slo_validations = slo_results

            # Check if any SLOs are failing
            failing_slos = [r for r in slo_results if not r.target_met]
            if failing_slos:
                report.safety_checks['slos_healthy'] = False
                report.recommendations.append(f"SLO violations detected: {[s.slo_name for s in failing_slos]}")
            else:
                report.safety_checks['slos_healthy'] = True

            # Check system health
            health_summary = self.metrics_collector.get_service_health_summary()
            service_health = health_summary.get(context.service, {})

            health_score = service_health.get('health_score', 0.0)
            report.safety_checks['system_healthy'] = health_score > 0.8

            if health_score <= 0.8:
                report.recommendations.append(f"System health degraded: {health_score:.2f}")

            # Check recent deployment history
            recent_deployments = self._get_recent_deployments(context.service, hours=24)
            failed_recent = [d for d in recent_deployments if d.status == DeploymentStatus.FAILED]

            report.safety_checks['recent_stability'] = len(failed_recent) == 0
            if failed_recent:
                report.recommendations.append(f"Recent deployment failures: {len(failed_recent)} in 24h")

            # Determine overall status
            all_checks_passed = all(report.safety_checks.values())
            report.status = DeploymentStatus.SUCCESS if all_checks_passed else DeploymentStatus.FAILED

            if not all_checks_passed:
                report.recommendations.append("Fix issues before proceeding with deployment")
            else:
                report.recommendations.append("Pre-deployment checks passed - safe to deploy")

        except Exception as e:
            logger.error(f"Pre-deployment check failed: {e}")
            report.status = DeploymentStatus.FAILED
            report.recommendations.append(f"Pre-deployment check error: {e}")

        finally:
            report.duration_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return report

    async def post_deployment_validation(self, context: DeploymentContext) -> DeploymentReport:
        """
        Execute post-deployment validation.

        Validates:
        - Service health after deployment
        - Performance regression detection
        - SLO compliance validation
        - Error rate monitoring
        """
        logger.info(f"Starting post-deployment validation for {context.service}")

        report = DeploymentReport(
            context=context,
            stage=DeploymentStage.POST_DEPLOYMENT,
            status=DeploymentStatus.RUNNING,
            duration_seconds=None
        )

        start_time = datetime.now(timezone.utc)

        try:
            # Wait for deployment to stabilize
            await asyncio.sleep(30)  # 30 second warmup period

            # Collect baseline metrics (before deployment)
            baseline_metrics = await self._collect_baseline_metrics(context.service)

            # Wait for measurement window
            measurement_window_minutes = int(self.config['slo_validation_window'][:-1])
            logger.info(f"Measuring post-deployment metrics for {measurement_window_minutes} minutes")

            await asyncio.sleep(measurement_window_minutes * 60)

            # Collect post-deployment metrics
            current_metrics = await self._collect_current_metrics(context.service)

            # Validate SLOs
            slo_results = await self._validate_current_slos(context.service)
            report.slo_validations = slo_results

            # Performance regression analysis
            regression_analysis = await self._analyze_performance_regression(
                baseline_metrics, current_metrics
            )
            report.performance_metrics = regression_analysis

            # Check for rollback triggers
            rollback_triggers = await self._check_rollback_triggers(
                context.service, current_metrics, slo_results
            )
            report.rollback_triggers = rollback_triggers

            # Determine status
            slo_failures = [r for r in slo_results if not r.target_met]
            has_regressions = regression_analysis.get('regressions_detected', False)
            needs_rollback = len(rollback_triggers) > 0

            if needs_rollback:
                report.status = DeploymentStatus.FAILED
                report.recommendations.append("Automatic rollback triggered")

                if self.config['enable_auto_rollback']:
                    await self._trigger_automatic_rollback(context)

            elif slo_failures or has_regressions:
                report.status = DeploymentStatus.FAILED
                report.recommendations.append("Manual intervention required")

            else:
                report.status = DeploymentStatus.SUCCESS
                report.recommendations.append("Post-deployment validation passed")

        except Exception as e:
            logger.error(f"Post-deployment validation failed: {e}")
            report.status = DeploymentStatus.FAILED
            report.recommendations.append(f"Validation error: {e}")

        finally:
            report.duration_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()

        return report

    async def _validate_current_slos(self, service: str) -> list[SLOValidationResult]:
        """Validate current SLOs for service"""
        results = []

        # Get SLOs for this service
        service_slos = {
            name: slo for name, slo in self.alert_manager.slos.items()
            if slo.service == service
        }

        for slo_name, slo in service_slos.items():
            try:
                # This would normally query actual metrics
                # For now, we'll use mock data

                if 'availability' in slo_name:
                    # Mock availability check
                    actual_availability = 0.998  # 99.8%
                    target_met = actual_availability >= slo.target

                    results.append(SLOValidationResult(
                        slo_name=slo_name,
                        target_met=target_met,
                        actual_value=actual_availability,
                        target_value=slo.target,
                        measurement_window=self.config['slo_validation_window'],
                        details={'measurement_type': 'availability'}
                    ))

                elif 'latency' in slo_name:
                    # Mock latency check
                    actual_p95 = 45.0  # 45ms p95
                    target_p95 = 50.0  # Target <50ms
                    target_met = actual_p95 <= target_p95

                    results.append(SLOValidationResult(
                        slo_name=slo_name,
                        target_met=target_met,
                        actual_value=actual_p95,
                        target_value=target_p95,
                        measurement_window=self.config['slo_validation_window'],
                        details={'measurement_type': 'latency_p95', 'unit': 'ms'}
                    ))

            except Exception as e:
                logger.error(f"SLO validation failed for {slo_name}: {e}")

                results.append(SLOValidationResult(
                    slo_name=slo_name,
                    target_met=False,
                    actual_value=0.0,
                    target_value=slo.target,
                    measurement_window=self.config['slo_validation_window'],
                    details={'error': str(e)}
                ))

        return results

    async def _collect_baseline_metrics(self, service: str) -> dict[str, Any]:
        """Collect baseline metrics before deployment"""
        # This would query metrics from Prometheus/other systems
        # Mock implementation for now

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': service,
            'metrics': {
                'request_rate': 100.0,
                'error_rate': 0.01,
                'latency_p95': 45.0,
                'latency_p99': 85.0,
                'cpu_usage': 45.0,
                'memory_usage': 60.0
            }
        }

    async def _collect_current_metrics(self, service: str) -> dict[str, Any]:
        """Collect current metrics after deployment"""
        # Mock implementation - would query actual metrics

        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'service': service,
            'metrics': {
                'request_rate': 105.0,
                'error_rate': 0.008,  # Slight improvement
                'latency_p95': 43.0,  # Slight improvement
                'latency_p99': 82.0,  # Slight improvement
                'cpu_usage': 47.0,    # Slight increase
                'memory_usage': 62.0  # Slight increase
            }
        }

    async def _analyze_performance_regression(self,
                                           baseline: dict[str, Any],
                                           current: dict[str, Any]) -> dict[str, Any]:
        """Analyze performance regression between baseline and current"""

        baseline_metrics = baseline['metrics']
        current_metrics = current['metrics']

        analysis = {
            'regressions_detected': False,
            'improvements_detected': False,
            'comparisons': {}
        }

        # Define regression thresholds
        regression_thresholds = {
            'error_rate': 0.02,      # 2% increase is regression
            'latency_p95': 0.20,     # 20% increase is regression
            'latency_p99': 0.25,     # 25% increase is regression
            'cpu_usage': 0.30,       # 30% increase is regression
            'memory_usage': 0.30     # 30% increase is regression
        }

        for metric, current_value in current_metrics.items():
            if metric not in baseline_metrics:
                continue

            baseline_value = baseline_metrics[metric]
            if baseline_value == 0:
                continue

            change_percent = (current_value - baseline_value) / baseline_value

            comparison = {
                'baseline': baseline_value,
                'current': current_value,
                'change_percent': change_percent,
                'regression': False,
                'improvement': False
            }

            # Check for regression
            if metric in regression_thresholds:
                threshold = regression_thresholds[metric]

                if change_percent > threshold:
                    comparison['regression'] = True
                    analysis['regressions_detected'] = True

                elif change_percent < -0.05:  # 5% improvement
                    comparison['improvement'] = True
                    analysis['improvements_detected'] = True

            analysis['comparisons'][metric] = comparison

        return analysis

    async def _check_rollback_triggers(self,
                                     service: str,
                                     current_metrics: dict[str, Any],
                                     slo_results: list[SLOValidationResult]) -> list[str]:
        """Check for automatic rollback triggers"""

        triggers = []
        metrics = current_metrics['metrics']

        # Error rate trigger
        if metrics.get('error_rate', 0) > self.config['rollback_threshold_error_rate']:
            triggers.append(f"High error rate: {metrics['error_rate']:.3f}")

        # Latency trigger
        if metrics.get('latency_p95', 0) > self.config['rollback_threshold_latency_p95']:
            triggers.append(f"High latency p95: {metrics['latency_p95']:.1f}ms")

        # SLO failure trigger
        failed_slos = [r for r in slo_results if not r.target_met]
        critical_slo_failures = [r for r in failed_slos if 'availability' in r.slo_name]

        if critical_slo_failures:
            triggers.append(f"Critical SLO failures: {[r.slo_name for r in critical_slo_failures]}")

        # Burn rate trigger
        active_alerts = self.alert_manager.get_active_alerts()
        service_critical_alerts = [
            a for a in active_alerts
            if a.slo.service == service and a.severity.value == 'critical'
        ]

        if service_critical_alerts:
            triggers.append(f"Critical burn rate alerts: {len(service_critical_alerts)}")

        return triggers

    async def _trigger_automatic_rollback(self, context: DeploymentContext):
        """Trigger automatic rollback"""
        logger.critical(f"Triggering automatic rollback for {context.service} v{context.version}")

        # This would integrate with actual deployment system
        # For now, just log the rollback
        rollback_context = {
            'original_deployment': context.deployment_id,
            'service': context.service,
            'rollback_reason': 'Observability-triggered automatic rollback',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Rollback context: {rollback_context}")

        # In real implementation, would:
        # 1. Call deployment system rollback API
        # 2. Update deployment status
        # 3. Send notifications
        # 4. Create incident ticket

    def _get_recent_deployments(self, service: str, hours: int = 24) -> list[DeploymentReport]:
        """Get recent deployments for service"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        return [
            deployment for deployment in self.deployment_history
            if (deployment.context.service == service and
                deployment.context.timestamp >= cutoff_time)
        ]

    def generate_observability_report(self, context: DeploymentContext) -> dict[str, Any]:
        """Generate comprehensive observability report for deployment"""

        service_health = self.metrics_collector.get_service_health_summary()
        burn_rate_status = self.alert_manager.get_burn_rate_status()
        active_alerts = self.alert_manager.get_active_alerts()

        report = {
            'deployment': {
                'service': context.service,
                'version': context.version,
                'environment': context.environment,
                'deployment_id': context.deployment_id,
                'timestamp': context.timestamp.isoformat()
            },
            'observability_status': {
                'service_health': service_health.get(context.service, {}),
                'burn_rates': {
                    k: v for k, v in burn_rate_status.items()
                    if v['service'] == context.service
                },
                'active_alerts': [
                    {
                        'alert_id': alert.alert_id,
                        'severity': alert.severity.value,
                        'message': alert.message
                    }
                    for alert in active_alerts
                    if alert.slo.service == context.service
                ]
            },
            'recommendations': self._generate_deployment_recommendations(context),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }

        return report

    def _generate_deployment_recommendations(self, context: DeploymentContext) -> list[str]:
        """Generate deployment recommendations based on observability"""

        recommendations = []

        # Check service health
        health_summary = self.metrics_collector.get_service_health_summary()
        service_health = health_summary.get(context.service, {})

        health_score = service_health.get('health_score', 0.0)

        if health_score < 0.5:
            recommendations.append("Service health critical - avoid deployment")
        elif health_score < 0.8:
            recommendations.append("Service health degraded - proceed with caution")
        else:
            recommendations.append("Service health good - safe to deploy")

        # Check burn rates
        burn_rate_status = self.alert_manager.get_burn_rate_status()
        service_burn_rates = {
            k: v for k, v in burn_rate_status.items()
            if v['service'] == context.service
        }

        critical_burns = [v for v in service_burn_rates.values() if v['alert_level'] == 'critical']
        if critical_burns:
            recommendations.append("Critical burn rates detected - block deployment")

        # Check recent deployment success rate
        recent_deployments = self._get_recent_deployments(context.service, hours=168)  # 7 days
        if recent_deployments:
            success_rate = len([d for d in recent_deployments if d.status == DeploymentStatus.SUCCESS]) / len(recent_deployments)

            if success_rate < 0.7:
                recommendations.append(f"Recent deployment success rate low: {success_rate:.1%}")
            else:
                recommendations.append(f"Recent deployment success rate good: {success_rate:.1%}")

        return recommendations

    def export_ci_artifacts(self, report: DeploymentReport) -> list[str]:
        """Export CI artifacts for deployment report"""

        artifacts = []

        try:
            # Create artifacts directory
            artifacts_dir = Path(tempfile.mkdtemp(prefix="lukhas_deploy_"))

            # Export deployment report
            report_file = artifacts_dir / f"deployment_report_{report.context.deployment_id}.json"
            with open(report_file, 'w') as f:
                # Convert report to JSON-serializable format
                report_dict = {
                    'context': {
                        'service': report.context.service,
                        'version': report.context.version,
                        'environment': report.context.environment,
                        'deployment_id': report.context.deployment_id,
                        'timestamp': report.context.timestamp.isoformat()
                    },
                    'stage': report.stage.value,
                    'status': report.status.value,
                    'duration_seconds': report.duration_seconds,
                    'slo_validations': [
                        {
                            'slo_name': v.slo_name,
                            'target_met': v.target_met,
                            'actual_value': v.actual_value,
                            'target_value': v.target_value
                        }
                        for v in report.slo_validations
                    ],
                    'safety_checks': report.safety_checks,
                    'recommendations': report.recommendations
                }

                json.dump(report_dict, f, indent=2)

            artifacts.append(str(report_file))

            # Export observability metrics snapshot
            metrics_file = artifacts_dir / f"metrics_snapshot_{report.context.deployment_id}.json"
            observability_report = self.generate_observability_report(report.context)

            with open(metrics_file, 'w') as f:
                json.dump(observability_report, f, indent=2)

            artifacts.append(str(metrics_file))

            logger.info(f"CI artifacts exported: {artifacts}")

        except Exception as e:
            logger.error(f"Failed to export CI artifacts: {e}")

        return artifacts


# GitHub Actions integration helpers
def create_github_action_summary(report: DeploymentReport) -> str:
    """Create GitHub Actions job summary"""

    status_emoji = {
        DeploymentStatus.SUCCESS: "✅",
        DeploymentStatus.FAILED: "❌",
        DeploymentStatus.PENDING: "⏳",
        DeploymentStatus.RUNNING: "🔄"
    }

    emoji = status_emoji.get(report.status, "❓")

    summary = f"""
# {emoji} Deployment Observability Report

**Service:** {report.context.service}
**Version:** {report.context.version}
**Environment:** {report.context.environment}
**Status:** {report.status.value}

## SLO Validation Results

| SLO | Target Met | Actual | Target |
|-----|------------|--------|--------|
"""

    for slo in report.slo_validations:
        status_icon = "✅" if slo.target_met else "❌"
        summary += f"| {slo.slo_name} | {status_icon} | {slo.actual_value:.3f} | {slo.target_value:.3f} |\n"

    summary += "\n## Safety Checks\n\n"

    for check, passed in report.safety_checks.items():
        status_icon = "✅" if passed else "❌"
        summary += f"- {status_icon} {check.replace('_', ' ').title()}\n"

    if report.recommendations:
        summary += "\n## Recommendations\n\n"
        for rec in report.recommendations:
            summary += f"- {rec}\n"

    return summary
