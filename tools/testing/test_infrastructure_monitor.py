#!/usr/bin/env python3
"""
Test Infrastructure Monitor
==========================
Production-ready testing infrastructure with comprehensive monitoring,
error handling, and automated recovery capabilities.

Features:
- Real-time test execution monitoring
- Automated failure recovery and retry logic
- Performance metrics and trend analysis
- Resource usage monitoring and alerting
- Test flakiness detection and quarantine
- Infrastructure health checks
- Test data management and cleanup
"""

import json
import logging
import os
import sys
import time
import psutil
import signal
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import subprocess
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/test_infrastructure.log')
    ]
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]


class TestHealthStatus(Enum):
    """Test infrastructure health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


class TestExecutionStatus(Enum):
    """Test execution status"""
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ResourceMetrics:
    """System resource metrics during test execution"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, int]
    load_average: List[float]
    timestamp: str


@dataclass
class TestExecutionMetrics:
    """Comprehensive test execution metrics"""
    test_id: str
    start_time: str
    end_time: Optional[str]
    duration: float
    status: TestExecutionStatus
    exit_code: int
    stdout_lines: int
    stderr_lines: int
    resource_usage: ResourceMetrics
    performance_markers: Dict[str, float]
    flakiness_score: float


@dataclass
class InfrastructureHealth:
    """Infrastructure health assessment"""
    status: TestHealthStatus
    cpu_available: bool
    memory_available: bool
    disk_available: bool
    network_accessible: bool
    dependencies_ready: bool
    test_database_ready: bool
    external_services_ready: bool
    issues: List[str]
    recommendations: List[str]


class TestInfrastructureMonitor:
    """Production-ready test infrastructure monitor"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.active_executions: Dict[str, TestExecutionMetrics] = {}
        self.health_history: List[InfrastructureHealth] = []
        self.performance_baseline: Dict[str, float] = {}
        self.flaky_test_registry: Dict[str, List[datetime]] = {}

        # Resource thresholds
        self.cpu_threshold = self.config.get('cpu_threshold', 80.0)
        self.memory_threshold = self.config.get('memory_threshold', 85.0)
        self.disk_threshold = self.config.get('disk_threshold', 90.0)

        # Retry configuration
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 30)

        # Monitoring intervals
        self.health_check_interval = self.config.get('health_check_interval', 60)
        self.metrics_collection_interval = self.config.get('metrics_collection_interval', 10)

        # Signal handling for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.monitoring_active = True
        self.monitoring_thread = None

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            'cpu_threshold': 80.0,
            'memory_threshold': 85.0,
            'disk_threshold': 90.0,
            'max_retries': 3,
            'retry_delay': 30,
            'health_check_interval': 60,
            'metrics_collection_interval': 10,
            'reports_dir': 'reports/testing',
            'cleanup_retention_days': 7,
            'flakiness_threshold': 0.3
        }

        if config_path and config_path.exists():
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config {config_path}: {e}")

        return default_config

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.monitoring_active = False

        # Cancel active test executions
        for test_id in list(self.active_executions.keys()):
            self._cancel_test_execution(test_id, "Infrastructure shutdown")

    def start_monitoring(self):
        """Start infrastructure monitoring in background thread"""
        logger.info("Starting test infrastructure monitoring...")
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_health_check = 0
        last_metrics_collection = 0

        while self.monitoring_active:
            current_time = time.time()

            # Periodic health checks
            if current_time - last_health_check >= self.health_check_interval:
                try:
                    self._perform_health_check()
                    last_health_check = current_time
                except Exception as e:
                    logger.error(f"Health check failed: {e}")

            # Collect metrics for active executions
            if current_time - last_metrics_collection >= self.metrics_collection_interval:
                try:
                    self._collect_execution_metrics()
                    last_metrics_collection = current_time
                except Exception as e:
                    logger.error(f"Metrics collection failed: {e}")

            time.sleep(5)  # Base loop interval

    def _perform_health_check(self) -> InfrastructureHealth:
        """Perform comprehensive infrastructure health check"""
        issues = []
        recommendations = []

        # Check CPU availability
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_available = cpu_percent < self.cpu_threshold
        if not cpu_available:
            issues.append(f"High CPU usage: {cpu_percent:.1f}%")
            recommendations.append("Consider reducing test parallelism")

        # Check memory availability
        memory = psutil.virtual_memory()
        memory_available = memory.percent < self.memory_threshold
        if not memory_available:
            issues.append(f"High memory usage: {memory.percent:.1f}%")
            recommendations.append("Run memory cleanup or reduce test concurrency")

        # Check disk space
        disk = psutil.disk_usage('/')
        disk_available = disk.percent < self.disk_threshold
        if not disk_available:
            issues.append(f"Low disk space: {disk.percent:.1f}% used")
            recommendations.append("Clean up test artifacts and logs")

        # Check network connectivity
        network_accessible = self._check_network_connectivity()
        if not network_accessible:
            issues.append("Network connectivity issues detected")
            recommendations.append("Check internet connection and DNS resolution")

        # Check dependencies
        dependencies_ready = self._check_dependencies()
        if not dependencies_ready:
            issues.append("Missing or broken test dependencies")
            recommendations.append("Reinstall test dependencies")

        # Check test database
        test_database_ready = self._check_test_database()
        if not test_database_ready:
            issues.append("Test database not accessible")
            recommendations.append("Start test database service")

        # Check external services
        external_services_ready = self._check_external_services()
        if not external_services_ready:
            issues.append("External services not responding")
            recommendations.append("Check external service status")

        # Determine overall status
        if not any([cpu_available, memory_available, disk_available]):
            status = TestHealthStatus.CRITICAL
        elif not all([network_accessible, dependencies_ready, test_database_ready]):
            status = TestHealthStatus.DEGRADED
        elif issues:
            status = TestHealthStatus.DEGRADED
        else:
            status = TestHealthStatus.HEALTHY

        health = InfrastructureHealth(
            status=status,
            cpu_available=cpu_available,
            memory_available=memory_available,
            disk_available=disk_available,
            network_accessible=network_accessible,
            dependencies_ready=dependencies_ready,
            test_database_ready=test_database_ready,
            external_services_ready=external_services_ready,
            issues=issues,
            recommendations=recommendations
        )

        self.health_history.append(health)
        self._save_health_report(health)

        if status != TestHealthStatus.HEALTHY:
            logger.warning(f"Infrastructure health: {status.value}")
            for issue in issues:
                logger.warning(f"  Issue: {issue}")
            for rec in recommendations:
                logger.info(f"  Recommendation: {rec}")

        return health

    def _check_network_connectivity(self) -> bool:
        """Check network connectivity"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def _check_dependencies(self) -> bool:
        """Check if test dependencies are available"""
        try:
            import pytest
            import coverage
            return True
        except ImportError:
            return False

    def _check_test_database(self) -> bool:
        """Check test database availability"""
        # For now, assume always ready - implement specific checks as needed
        return True

    def _check_external_services(self) -> bool:
        """Check external service availability"""
        # Placeholder for external service health checks
        return True

    def _collect_execution_metrics(self):
        """Collect metrics for all active test executions"""
        current_time = datetime.now(timezone.utc).isoformat()

        for test_id, execution in self.active_executions.items():
            try:
                # Get current resource usage
                resource_metrics = ResourceMetrics(
                    cpu_percent=psutil.cpu_percent(),
                    memory_percent=psutil.virtual_memory().percent,
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    network_io=dict(psutil.net_io_counters()._asdict()),
                    load_average=list(os.getloadavg()),
                    timestamp=current_time
                )

                execution.resource_usage = resource_metrics

            except Exception as e:
                logger.error(f"Failed to collect metrics for {test_id}: {e}")

    def execute_test_suite(
        self,
        test_command: List[str],
        test_id: Optional[str] = None,
        retry_on_failure: bool = True,
        timeout: Optional[int] = None
    ) -> TestExecutionMetrics:
        """Execute test suite with comprehensive monitoring and error handling"""

        if test_id is None:
            test_id = f"test_{int(time.time())}_{hash(' '.join(test_command)) % 10000}"

        logger.info(f"Starting test execution: {test_id}")
        logger.info(f"Command: {' '.join(test_command)}")

        # Check infrastructure health before starting
        health = self._perform_health_check()
        if health.status == TestHealthStatus.CRITICAL:
            logger.error("Infrastructure in critical state, aborting test execution")
            raise RuntimeError("Infrastructure health critical")

        start_time = datetime.now(timezone.utc)
        execution = TestExecutionMetrics(
            test_id=test_id,
            start_time=start_time.isoformat(),
            end_time=None,
            duration=0.0,
            status=TestExecutionStatus.RUNNING,
            exit_code=-1,
            stdout_lines=0,
            stderr_lines=0,
            resource_usage=self._get_current_resource_metrics(),
            performance_markers={},
            flakiness_score=0.0
        )

        self.active_executions[test_id] = execution

        try:
            # Execute with retries if configured
            attempts = 0
            max_attempts = self.max_retries + 1 if retry_on_failure else 1

            while attempts < max_attempts:
                attempts += 1

                if attempts > 1:
                    execution.status = TestExecutionStatus.RETRYING
                    logger.info(f"Retrying test execution {test_id} (attempt {attempts}/{max_attempts})")
                    time.sleep(self.retry_delay)

                try:
                    result = self._execute_single_attempt(test_command, test_id, timeout)

                    # Update execution metrics with result
                    execution.end_time = datetime.now(timezone.utc).isoformat()
                    execution.duration = (datetime.now(timezone.utc) - start_time).total_seconds()
                    execution.exit_code = result.returncode
                    execution.stdout_lines = len(result.stdout.splitlines()) if result.stdout else 0
                    execution.stderr_lines = len(result.stderr.splitlines()) if result.stderr else 0

                    if result.returncode == 0:
                        execution.status = TestExecutionStatus.PASSED
                        logger.info(f"Test execution {test_id} passed on attempt {attempts}")
                        break
                    else:
                        execution.status = TestExecutionStatus.FAILED
                        logger.warning(f"Test execution {test_id} failed on attempt {attempts}")

                        if attempts < max_attempts:
                            # Record failure for flakiness analysis
                            self._record_test_failure(test_id)

                except subprocess.TimeoutExpired:
                    execution.status = TestExecutionStatus.TIMEOUT
                    logger.error(f"Test execution {test_id} timed out on attempt {attempts}")

                except Exception as e:
                    execution.status = TestExecutionStatus.ERROR
                    logger.error(f"Test execution {test_id} error on attempt {attempts}: {e}")

            # Calculate flakiness score
            execution.flakiness_score = self._calculate_flakiness_score(test_id, attempts > 1)

            # Save execution metrics
            self._save_execution_metrics(execution)

            return execution

        finally:
            # Clean up
            if test_id in self.active_executions:
                del self.active_executions[test_id]

    def _execute_single_attempt(
        self,
        test_command: List[str],
        test_id: str,
        timeout: Optional[int]
    ) -> subprocess.CompletedProcess:
        """Execute a single test attempt"""

        # Setup environment
        env = os.environ.copy()
        env['TEST_EXECUTION_ID'] = test_id
        env['TEST_INFRASTRUCTURE_MONITORING'] = '1'

        # Execute command
        result = subprocess.run(
            test_command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )

        return result

    def _get_current_resource_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics"""
        return ResourceMetrics(
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            network_io=dict(psutil.net_io_counters()._asdict()),
            load_average=list(os.getloadavg()),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    def _record_test_failure(self, test_id: str):
        """Record test failure for flakiness analysis"""
        if test_id not in self.flaky_test_registry:
            self.flaky_test_registry[test_id] = []

        self.flaky_test_registry[test_id].append(datetime.now(timezone.utc))

        # Clean old entries (keep last 30 days)
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        self.flaky_test_registry[test_id] = [
            dt for dt in self.flaky_test_registry[test_id] if dt > cutoff
        ]

    def _calculate_flakiness_score(self, test_id: str, had_retry: bool) -> float:
        """Calculate flakiness score for test"""
        if test_id not in self.flaky_test_registry:
            return 0.0

        failures = self.flaky_test_registry[test_id]
        if not failures:
            return 0.0

        # Base score on failure frequency and recency
        recent_failures = len([f for f in failures if f > datetime.now(timezone.utc) - timedelta(days=7)])
        total_failures = len(failures)

        base_score = min(total_failures / 10.0, 1.0)  # Normalize to 0-1
        recency_factor = min(recent_failures / 3.0, 1.0)  # Weight recent failures

        flakiness_score = (base_score + recency_factor) / 2

        if had_retry:
            flakiness_score = min(flakiness_score + 0.2, 1.0)

        return flakiness_score

    def _cancel_test_execution(self, test_id: str, reason: str):
        """Cancel active test execution"""
        if test_id in self.active_executions:
            execution = self.active_executions[test_id]
            execution.status = TestExecutionStatus.CANCELLED
            execution.end_time = datetime.now(timezone.utc).isoformat()
            logger.info(f"Cancelled test execution {test_id}: {reason}")

    def _save_execution_metrics(self, execution: TestExecutionMetrics):
        """Save execution metrics to storage"""
        reports_dir = Path(self.config['reports_dir'])
        reports_dir.mkdir(parents=True, exist_ok=True)

        # Save individual execution
        execution_file = reports_dir / f"execution_{execution.test_id}.json"
        with open(execution_file, 'w') as f:
            json.dump(asdict(execution), f, indent=2, default=str)

        # Update summary
        self._update_execution_summary(execution)

    def _save_health_report(self, health: InfrastructureHealth):
        """Save health report"""
        reports_dir = Path(self.config['reports_dir'])
        reports_dir.mkdir(parents=True, exist_ok=True)

        health_file = reports_dir / "infrastructure_health_latest.json"
        with open(health_file, 'w') as f:
            json.dump(asdict(health), f, indent=2, default=str)

    def _update_execution_summary(self, execution: TestExecutionMetrics):
        """Update execution summary"""
        reports_dir = Path(self.config['reports_dir'])
        summary_file = reports_dir / "execution_summary.json"

        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)
        else:
            summary = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_duration': 0.0,
                'last_updated': None
            }

        summary['total_executions'] += 1
        if execution.status == TestExecutionStatus.PASSED:
            summary['successful_executions'] += 1
        else:
            summary['failed_executions'] += 1

        # Update average duration
        current_avg = summary['average_duration']
        new_count = summary['total_executions']
        summary['average_duration'] = ((current_avg * (new_count - 1)) + execution.duration) / new_count
        summary['last_updated'] = datetime.now(timezone.utc).isoformat()

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

    def cleanup_old_artifacts(self):
        """Clean up old test artifacts and reports"""
        reports_dir = Path(self.config['reports_dir'])
        if not reports_dir.exists():
            return

        cutoff = datetime.now() - timedelta(days=self.config['cleanup_retention_days'])
        cleaned_count = 0

        for file_path in reports_dir.glob("execution_*.json"):
            try:
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to clean {file_path}: {e}")

        logger.info(f"Cleaned up {cleaned_count} old test artifacts")

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""
        latest_health = self.health_history[-1] if self.health_history else None

        return {
            'monitoring_active': self.monitoring_active,
            'active_executions': len(self.active_executions),
            'latest_health': asdict(latest_health) if latest_health else None,
            'flaky_tests': {
                test_id: len(failures)
                for test_id, failures in self.flaky_test_registry.items()
                if len(failures) >= 3  # Only show tests with 3+ failures
            }
        }


def main():
    """CLI interface for test infrastructure monitor"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Test Infrastructure Monitor")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--start-monitoring", action="store_true", help="Start background monitoring")
    parser.add_argument("--health-check", action="store_true", help="Perform health check")
    parser.add_argument("--status", action="store_true", help="Show infrastructure status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old artifacts")
    parser.add_argument("--execute", nargs="+", help="Execute test command with monitoring")

    args = parser.parse_args()

    monitor = TestInfrastructureMonitor(args.config)

    if args.start_monitoring:
        print("Starting test infrastructure monitoring...")
        monitor.start_monitoring()
        try:
            while True:
                time.sleep(60)
                status = monitor.get_infrastructure_status()
                print(f"Status: {status['latest_health']['status'] if status['latest_health'] else 'unknown'}")
        except KeyboardInterrupt:
            print("Stopping monitoring...")

    elif args.health_check:
        health = monitor._perform_health_check()
        print(f"Infrastructure Health: {health.status.value}")
        if health.issues:
            print("Issues:")
            for issue in health.issues:
                print(f"  - {issue}")
        if health.recommendations:
            print("Recommendations:")
            for rec in health.recommendations:
                print(f"  - {rec}")

    elif args.status:
        status = monitor.get_infrastructure_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.cleanup:
        monitor.cleanup_old_artifacts()
        print("Cleanup completed")

    elif args.execute:
        monitor.start_monitoring()
        execution = monitor.execute_test_suite(args.execute)
        print(f"Test execution completed: {execution.status.value}")
        print(f"Duration: {execution.duration:.2f}s")
        if execution.flakiness_score > 0.3:
            print(f"Warning: High flakiness score: {execution.flakiness_score:.2f}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()