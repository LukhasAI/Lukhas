#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Externalized Orchestrator Routing Configuration
================================================================

Implements externalized routing configuration with hot-reload capabilities,
A/B testing, and advanced routing strategies.

Architecture:
- YAML-based configuration with hot-reload
- Multiple routing strategies (round-robin, weighted, health-based)
- A/B testing framework
- Circuit breaker patterns
- Context preservation across hops
- Performance targets: <100ms routing decisions, <250ms context handoff

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from opentelemetry import trace
from lukhas.observability import counter, histogram
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Prometheus metrics for routing performance
routing_decisions_total = counter(
    'lukhas_routing_decisions_total',
    'Total routing decisions made',
    ['strategy', 'provider', 'success']
)

routing_latency_seconds = histogram(
    'lukhas_routing_latency_seconds',
    'Routing decision latency',
    ['strategy'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

context_handoff_duration = histogram(
    'lukhas_context_handoff_duration_seconds',
    'Context handoff duration',
    ['source', 'destination'],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

config_reload_total = counter(
    'lukhas_config_reload_total',
    'Total configuration reloads',
    ['source', 'success']
)

ab_test_assignments = counter(
    'lukhas_ab_test_assignments_total',
    'A/B test assignments',
    ['experiment', 'variant']
)


class RoutingStrategy(Enum):
    """Routing strategy types"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    HEALTH_BASED = "health_based"
    LATENCY_BASED = "latency_based"
    COST_OPTIMIZED = "cost_optimized"
    A_B_TEST = "ab_test"
    HYBRID = "hybrid"


class HealthStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Provider health metrics"""
    provider: str
    status: HealthStatus = HealthStatus.UNKNOWN
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0
    last_check: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    last_error: Optional[str] = None


@dataclass
class RoutingRule:
    """Individual routing rule configuration"""
    name: str
    pattern: str
    strategy: RoutingStrategy
    providers: List[str]
    weights: Optional[Dict[str, float]] = None
    health_threshold: float = 0.95
    latency_threshold_ms: float = 250.0
    fallback_providers: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ABTestConfig:
    """A/B test configuration"""
    name: str
    enabled: bool
    traffic_split: Dict[str, int]  # variant_name -> percentage
    rules: List[str]  # rule names to apply test to
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingConfiguration:
    """Complete routing configuration"""
    version: str
    default_strategy: RoutingStrategy
    default_providers: List[str]
    rules: List[RoutingRule]
    ab_tests: List[ABTestConfig]
    health_check_interval: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    context_timeout: float = 10.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConfigurationFileHandler(FileSystemEventHandler):
    """File system handler for configuration hot-reload"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            logger.info(f"Configuration file changed: {event.src_path}")
            asyncio.create_task(self.config_manager.reload_configuration())


class RoutingConfigurationManager:
    """Manages routing configuration with hot-reload capabilities"""

    def __init__(self, config_path: str = "/Users/agi_dev/LOCAL-REPOS/Lukhas/config/routing.yaml"):
        self.config_path = Path(config_path)
        self.current_config: Optional[RoutingConfiguration] = None
        self.config_version: str = "1.0.0"
        self.last_reload: float = 0.0

        # File watcher for hot-reload
        self.observer = Observer()
        self.file_handler = ConfigurationFileHandler(self)

        # A/B test state
        self.ab_test_assignments: Dict[str, str] = {}  # session_id -> variant

        logger.info(f"Routing configuration manager initialized: {self.config_path}")

    async def initialize(self) -> None:
        """Initialize configuration manager"""
        with tracer.start_span("routing_config.initialize") as span:
            try:
                await self.load_configuration()
                self.start_file_watcher()
                span.set_attribute("config_version", self.config_version)
                logger.info("✅ Routing configuration initialized successfully")
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"❌ Failed to initialize routing configuration: {e}")
                raise

    async def load_configuration(self) -> None:
        """Load configuration from YAML file"""
        start_time = time.time()

        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}, creating default")
                await self.create_default_configuration()

            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)

            # Parse configuration
            self.current_config = self._parse_configuration(config_data)
            self.config_version = config_data.get('version', '1.0.0')
            self.last_reload = time.time()

            config_reload_total.labels(source="file", success="true").inc()

            logger.info(f"✅ Configuration loaded successfully (v{self.config_version})")

        except Exception as e:
            config_reload_total.labels(source="file", success="false").inc()
            logger.error(f"❌ Failed to load configuration: {e}")

            # Fall back to default configuration
            if self.current_config is None:
                await self.create_default_configuration()

            raise

    async def reload_configuration(self) -> None:
        """Reload configuration (called by file watcher)"""
        logger.info("🔄 Hot-reloading configuration...")

        try:
            old_version = self.config_version
            await self.load_configuration()

            if old_version != self.config_version:
                logger.info(f"📝 Configuration updated: {old_version} -> {self.config_version}")

                # Emit configuration change event
                from .kernel_bus import emit
                await emit(
                    "orchestration.config.changed",
                    {
                        "old_version": old_version,
                        "new_version": self.config_version,
                        "timestamp": time.time()
                    },
                    source="routing_config",
                    mode="live"
                )

        except Exception as e:
            logger.error(f"❌ Failed to reload configuration: {e}")

    def start_file_watcher(self) -> None:
        """Start file system watcher for hot-reload"""
        if self.config_path.parent.exists():
            self.observer.schedule(
                self.file_handler,
                str(self.config_path.parent),
                recursive=False
            )
            self.observer.start()
            logger.info(f"📁 File watcher started for {self.config_path.parent}")

    def stop_file_watcher(self) -> None:
        """Stop file system watcher"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("📁 File watcher stopped")

    def get_configuration(self) -> RoutingConfiguration:
        """Get current routing configuration"""
        if self.current_config is None:
            raise ValueError("Configuration not loaded")
        return self.current_config

    def get_rule_for_request(self, request_type: str, context: Dict[str, Any] = None) -> Optional[RoutingRule]:
        """Find matching routing rule for a request"""
        if not self.current_config:
            return None

        context = context or {}

        # Check for pattern matches
        for rule in self.current_config.rules:
            if self._matches_pattern(rule.pattern, request_type, context):
                return rule

        # Return default rule if no matches
        return RoutingRule(
            name="default",
            pattern="*",
            strategy=self.current_config.default_strategy,
            providers=self.current_config.default_providers
        )

    def get_ab_test_variant(self, session_id: str, experiment_name: str) -> Optional[str]:
        """Get A/B test variant for session"""
        if not self.current_config:
            return None

        # Check if session already assigned
        cache_key = f"{session_id}:{experiment_name}"
        if cache_key in self.ab_test_assignments:
            return self.ab_test_assignments[cache_key]

        # Find experiment
        experiment = None
        for test in self.current_config.ab_tests:
            if test.name == experiment_name and test.enabled:
                experiment = test
                break

        if not experiment:
            return None

        # Assign variant based on hash
        hash_input = f"{session_id}{experiment_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        percentage = hash_value % 100

        cumulative = 0
        for variant, split in experiment.traffic_split.items():
            cumulative += split
            if percentage < cumulative:
                self.ab_test_assignments[cache_key] = variant
                ab_test_assignments.labels(experiment=experiment_name, variant=variant).inc()
                return variant

        return None

    async def create_default_configuration(self) -> None:
        """Create default configuration file"""
        default_config = {
            "version": "1.0.0",
            "default_strategy": "health_based",
            "default_providers": ["openai", "anthropic", "google"],
            "rules": [
                {
                    "name": "documentation_tasks",
                    "pattern": "documentation|architecture|review",
                    "strategy": "weighted",
                    "providers": ["anthropic", "openai", "google"],
                    "weights": {"anthropic": 0.6, "openai": 0.3, "google": 0.1},
                    "health_threshold": 0.95,
                    "latency_threshold_ms": 250.0,
                    "fallback_providers": ["openai", "google"]
                },
                {
                    "name": "code_generation",
                    "pattern": "code|implementation|debug",
                    "strategy": "round_robin",
                    "providers": ["openai", "anthropic", "google"],
                    "health_threshold": 0.95,
                    "latency_threshold_ms": 200.0,
                    "fallback_providers": ["anthropic", "google"]
                },
                {
                    "name": "analysis_tasks",
                    "pattern": "analysis|explain|understand",
                    "strategy": "latency_based",
                    "providers": ["google", "openai", "anthropic"],
                    "health_threshold": 0.90,
                    "latency_threshold_ms": 150.0,
                    "fallback_providers": ["openai", "anthropic"]
                }
            ],
            "ab_tests": [
                {
                    "name": "documentation_provider_test",
                    "enabled": False,
                    "traffic_split": {"anthropic": 50, "openai": 50},
                    "rules": ["documentation_tasks"],
                    "metadata": {"description": "Test Claude vs GPT for documentation tasks"}
                }
            ],
            "health_check_interval": 30.0,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60.0,
            "context_timeout": 10.0,
            "metadata": {
                "created_by": "lukhas_orchestration",
                "created_at": time.time(),
                "description": "Default LUKHAS routing configuration"
            }
        }

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)

        logger.info(f"✅ Default configuration created: {self.config_path}")

    def _parse_configuration(self, config_data: Dict[str, Any]) -> RoutingConfiguration:
        """Parse YAML configuration into RoutingConfiguration object"""

        # Parse routing rules
        rules = []
        for rule_data in config_data.get('rules', []):
            rule = RoutingRule(
                name=rule_data['name'],
                pattern=rule_data['pattern'],
                strategy=RoutingStrategy(rule_data['strategy']),
                providers=rule_data['providers'],
                weights=rule_data.get('weights'),
                health_threshold=rule_data.get('health_threshold', 0.95),
                latency_threshold_ms=rule_data.get('latency_threshold_ms', 250.0),
                fallback_providers=rule_data.get('fallback_providers'),
                metadata=rule_data.get('metadata', {})
            )
            rules.append(rule)

        # Parse A/B tests
        ab_tests = []
        for test_data in config_data.get('ab_tests', []):
            test = ABTestConfig(
                name=test_data['name'],
                enabled=test_data['enabled'],
                traffic_split=test_data['traffic_split'],
                rules=test_data['rules'],
                metadata=test_data.get('metadata', {})
            )
            ab_tests.append(test)

        return RoutingConfiguration(
            version=config_data['version'],
            default_strategy=RoutingStrategy(config_data['default_strategy']),
            default_providers=config_data['default_providers'],
            rules=rules,
            ab_tests=ab_tests,
            health_check_interval=config_data.get('health_check_interval', 30.0),
            circuit_breaker_threshold=config_data.get('circuit_breaker_threshold', 5),
            circuit_breaker_timeout=config_data.get('circuit_breaker_timeout', 60.0),
            context_timeout=config_data.get('context_timeout', 10.0),
            metadata=config_data.get('metadata', {})
        )

    def _matches_pattern(self, pattern: str, request_type: str, context: Dict[str, Any]) -> bool:
        """Check if request matches routing pattern"""
        # Simple pattern matching (can be enhanced with regex)
        if pattern == "*":
            return True

        # Split pattern by | for OR logic
        patterns = [p.strip() for p in pattern.split('|')]

        request_lower = request_type.lower()

        for p in patterns:
            if p.lower() in request_lower:
                return True

        return False


# Global configuration manager instance
_config_manager: Optional[RoutingConfigurationManager] = None


async def get_routing_config_manager() -> RoutingConfigurationManager:
    """Get or create global routing configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = RoutingConfigurationManager()
        await _config_manager.initialize()
    return _config_manager


async def get_routing_configuration() -> RoutingConfiguration:
    """Get current routing configuration"""
    manager = await get_routing_config_manager()
    return manager.get_configuration()
