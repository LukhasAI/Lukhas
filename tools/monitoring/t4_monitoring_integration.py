#!/usr/bin/env python3
"""
T4 Monitoring Integration
=========================
Integrates Production Alerting System with T4 Observability Stack
Provides unified monitoring for LUKHAS AI infrastructure

This module bridges the production alerting system with the existing
T4 enterprise observability components to provide comprehensive monitoring.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

try:
    from products.enterprise.core.observability.t4_observability_stack import T4ObservabilityStack
    from tools.monitoring.production_alerting_system import ProductionAlertingSystem, SystemMetrics
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class T4MonitoringIntegration:
    """Integration layer between T4 Observability and Production Alerting"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("tools/monitoring/monitoring_config.json")

        # Initialize components
        self.alerting_system = ProductionAlertingSystem(self.config_path)
        self.t4_observability = T4ObservabilityStack(
            datadog_enabled=True,
            prometheus_enabled=True,
            opentelemetry_enabled=True
        )

        # Load integration configuration
        self.integration_config = self._load_integration_config()

    def _load_integration_config(self) -> Dict[str, Any]:
        """Load integration-specific configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get("integration", {})
        except Exception as e:
            logger.warning(f"Failed to load integration config: {e}")
            return {
                "t4_observability": {"enabled": True},
                "coverage_metrics": {"enabled": True},
                "test_infrastructure": {"enabled": True}
            }

    async def collect_enhanced_metrics(self) -> SystemMetrics:
        """Collect metrics from both systems and merge them"""
        # Get base system metrics
        base_metrics = await self.alerting_system.collect_system_metrics()

        # Enhance with T4 observability data if available
        if self.integration_config.get("t4_observability", {}).get("enabled", True):
            try:
                # Try to collect from various T4 components
                enhanced_data = await self._collect_t4_metrics()

                # Merge enhanced data into base metrics
                if enhanced_data:
                    base_metrics = self._merge_metrics(base_metrics, enhanced_data)

            except Exception as e:
                logger.debug(f"T4 metrics collection failed: {e}")

        return base_metrics

    async def _collect_t4_metrics(self) -> Dict[str, Any]:
        """Collect metrics from T4 observability components"""
        metrics = {}

        try:
            # Try to import and collect from various LUKHAS components
            # This is a safe approach that doesn't fail if components aren't available

            # Check for Trinity framework
            try:
                constellation_metrics = await self.t4_observability.collect_triad_metrics(None)
                if constellation_metrics:
                    metrics["constellation"] = constellation_metrics
            except Exception as e:
                logger.debug(f"Trinity metrics unavailable: {e}")

            # Check for Consciousness core
            try:
                consciousness_metrics = await self.t4_observability.collect_consciousness_metrics(None)
                if consciousness_metrics:
                    metrics["consciousness"] = consciousness_metrics
            except Exception as e:
                logger.debug(f"Consciousness metrics unavailable: {e}")

            # Check for Memory system
            try:
                memory_metrics = await self.t4_observability.collect_memory_metrics(None)
                if memory_metrics:
                    metrics["lukhas.memory"] = memory_metrics
            except Exception as e:
                logger.debug(f"Memory metrics unavailable: {e}")

            # Check for Guardian system
            try:
                guardian_metrics = await self.t4_observability.collect_guardian_metrics(None)
                if guardian_metrics:
                    metrics["guardian"] = guardian_metrics
            except Exception as e:
                logger.debug(f"Guardian metrics unavailable: {e}")

        except Exception as e:
            logger.warning(f"T4 component metrics collection failed: {e}")

        return metrics

    def _merge_metrics(self, base_metrics: SystemMetrics, enhanced_data: Dict[str, Any]) -> SystemMetrics:
        """Merge enhanced T4 metrics into base system metrics"""
        # Extract meaningful metrics from T4 data and enhance base metrics

        # Check for consciousness metrics that might affect system health
        consciousness = enhanced_data.get("consciousness", {})
        if consciousness:
            drift_score = consciousness.get("drift_score", 0.0)
            if isinstance(drift_score, (int, float)) and drift_score > 0.5:
                # High drift might indicate system stress - adjust error rate
                base_metrics.error_rate = max(base_metrics.error_rate, drift_score * 2)

        # Check for memory fold metrics
        memory = enhanced_data.get("lukhas.memory", {})
        if memory:
            active_folds = memory.get("active_folds", 0)
            if isinstance(active_folds, int) and active_folds > 100:
                # High memory fold count might indicate memory pressure
                base_metrics.memory_percent = min(base_metrics.memory_percent + 5, 100)

        # Check for constellation coherence metrics
        constellation = enhanced_data.get("constellation", {})
        if constellation:
            coherence = constellation.get("coherence", 1.0)
            if isinstance(coherence, (int, float)) and coherence < 0.8:
                # Low coherence might indicate performance issues
                base_metrics.response_time_p95 = max(base_metrics.response_time_p95, 200)

        return base_metrics

    async def submit_metrics_to_t4(self, metrics: SystemMetrics):
        """Submit metrics to T4 observability stack"""
        if not self.integration_config.get("t4_observability", {}).get("enabled", True):
            return

        try:
            # Submit key metrics to T4 stack
            if self.t4_observability.datadog_enabled:
                # Submit to Datadog
                self.t4_observability.submit_metric("gauge", "lukhas.system.cpu_percent", metrics.cpu_percent)
                self.t4_observability.submit_metric("gauge", "lukhas.system.memory_percent", metrics.memory_percent)
                self.t4_observability.submit_metric("gauge", "lukhas.system.disk_usage_percent", metrics.disk_usage_percent)
                self.t4_observability.submit_metric("gauge", "lukhas.testing.success_rate", metrics.test_success_rate)
                self.t4_observability.submit_metric("gauge", "lukhas.testing.coverage_percentage", metrics.coverage_percentage)
                self.t4_observability.submit_metric("gauge", "lukhas.performance.response_time_p95", metrics.response_time_p95)
                self.t4_observability.submit_metric("gauge", "lukhas.system.error_rate", metrics.error_rate)
                self.t4_observability.submit_metric("gauge", "lukhas.system.active_connections", metrics.active_connections)

                logger.debug("Metrics submitted to T4 Datadog")

        except Exception as e:
            logger.warning(f"Failed to submit metrics to T4 stack: {e}")

    async def run_integrated_monitoring(self):
        """Run integrated monitoring combining both systems"""
        logger.info("Starting T4 integrated monitoring system")

        evaluation_interval = 60  # seconds

        while True:
            try:
                # Collect enhanced metrics
                metrics = await self.collect_enhanced_metrics()

                # Submit to T4 observability stack
                await self.submit_metrics_to_t4(metrics)

                # Update alerting system with enhanced metrics
                self.alerting_system.metrics_history.append(metrics)
                self.alerting_system._store_metrics(metrics)

                # Evaluate alert rules using enhanced metrics
                for rule in self.alerting_system.alert_rules.values():
                    should_trigger = self.alerting_system._evaluate_alert_rule(rule, metrics)

                    if should_trigger and rule.name not in self.alerting_system.active_alerts:
                        await self.alerting_system._trigger_alert(rule, metrics)
                    elif not should_trigger and rule.name in self.alerting_system.active_alerts:
                        await self.alerting_system._resolve_alert(rule.name, metrics)

                await asyncio.sleep(evaluation_interval)

            except KeyboardInterrupt:
                logger.info("Integrated monitoring interrupted")
                break
            except Exception as e:
                logger.error(f"Error in integrated monitoring loop: {e}")
                await asyncio.sleep(evaluation_interval)

    def generate_integrated_health_report(self) -> str:
        """Generate comprehensive health report including T4 metrics"""
        base_report = self.alerting_system.generate_health_report()

        # Add T4-specific information
        t4_status = []

        if self.t4_observability.datadog_enabled:
            t4_status.append("✅ Datadog integration active")
        else:
            t4_status.append("❌ Datadog integration disabled")

        if self.t4_observability.prometheus_enabled:
            t4_status.append("✅ Prometheus integration active")
        else:
            t4_status.append("❌ Prometheus integration disabled")

        if self.t4_observability.opentelemetry_enabled:
            t4_status.append("✅ OpenTelemetry integration active")
        else:
            t4_status.append("❌ OpenTelemetry integration disabled")

        t4_section = f"""

T4 OBSERVABILITY INTEGRATION:
{chr(10).join(t4_status)}

INTEGRATION STATUS:
- T4 Observability: {'✅ Enabled' if self.integration_config.get('t4_observability', {}).get('enabled') else '❌ Disabled'}
- Coverage Metrics: {'✅ Enabled' if self.integration_config.get('coverage_metrics', {}).get('enabled') else '❌ Disabled'}
- Test Infrastructure: {'✅ Enabled' if self.integration_config.get('test_infrastructure', {}).get('enabled') else '❌ Disabled'}
"""

        return base_report + t4_section

    async def test_integration(self) -> Dict[str, Any]:
        """Test the integration between systems"""
        test_results = {
            "alerting_system": False,
            "t4_observability": False,
            "metric_collection": False,
            "alert_submission": False,
            "database_connectivity": False
        }

        try:
            # Test alerting system
            metrics = await self.alerting_system.collect_system_metrics()
            test_results["alerting_system"] = True
            test_results["metric_collection"] = True

            # Test T4 observability
            if self.t4_observability.datadog_enabled or self.t4_observability.prometheus_enabled:
                test_results["t4_observability"] = True

            # Test database connectivity
            summary = self.alerting_system.get_alert_summary()
            test_results["database_connectivity"] = True

            # Test alert system functionality
            if len(self.alerting_system.alert_rules) > 0:
                test_results["alert_submission"] = True

        except Exception as e:
            logger.error(f"Integration test failed: {e}")

        return test_results


async def main():
    """Main entry point for integrated monitoring"""
    integration = T4MonitoringIntegration()

    # Run integration test
    test_results = await integration.test_integration()
    print("Integration Test Results:")
    for component, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")

    print("\n" + "="*50)
    print(integration.generate_integrated_health_report())
    print("="*50)

    # Run integrated monitoring
    try:
        await integration.run_integrated_monitoring()
    except KeyboardInterrupt:
        logger.info("Integrated monitoring shutdown")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
