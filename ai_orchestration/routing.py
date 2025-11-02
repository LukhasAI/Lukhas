#!/usr/bin/env python3
"""
LUKHAS O.2 Configurable Routing System

Dynamic routing system with hot reload, A/B testing, and Guardian integration.
Routes AI requests to optimal providers based on configurable rules.

T4/0.01% Excellence: Production-ready routing with comprehensive monitoring.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from opentelemetry import trace
from prometheus_client import Counter, Gauge, Histogram

tracer = trace.get_tracer(__name__)


# Prometheus metrics (test-safe)
class MockMetric:
    def labels(self, **kwargs):
        return self

    def inc(self, amount=1):
        pass

    def observe(self, amount):
        pass

    def set(self, value):
        pass


try:
    routing_decisions_total = Counter(
        "lukhas_routing_decisions_total", "Total routing decisions", ["rule_name", "provider", "component"]
    )
    provider_response_time = Histogram(
        "lukhas_provider_response_time_seconds",
        "Provider response time",
        ["provider", "component"],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    )
    active_providers_gauge = Gauge("lukhas_active_providers_total", "Number of active providers")
    ab_test_assignments_total = Counter(
        "lukhas_ab_test_assignments_total", "Total A/B test assignments", ["test_name", "bucket", "provider"]
    )
except ValueError:
    routing_decisions_total = MockMetric()
    provider_response_time = MockMetric()
    active_providers_gauge = MockMetric()
    ab_test_assignments_total = MockMetric()


class OperatorType(Enum):
    """Routing rule operators."""

    EQUALS = "equals"
    IN = "in"
    NOT_EQUALS = "not_equals"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    REGEX = "regex"


class LoadBalanceStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"


@dataclass
class RoutingCondition:
    """A single routing condition."""

    field: str
    operator: OperatorType
    value: Union[str, List[str], int, float]

    def evaluate(self, request_data: Dict[str, Any]) -> bool:
        """Evaluate condition against request data."""
        field_value = request_data.get(self.field)

        if field_value is None:
            return False

        if self.operator == OperatorType.EQUALS:
            return field_value == self.value
        elif self.operator == OperatorType.IN:
            return field_value in self.value
        elif self.operator == OperatorType.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == OperatorType.NOT_IN:
            return field_value not in self.value
        elif self.operator == OperatorType.GREATER_THAN:
            return field_value > self.value
        elif self.operator == OperatorType.LESS_THAN:
            return field_value < self.value
        elif self.operator == OperatorType.CONTAINS:
            return str(self.value) in str(field_value)
        elif self.operator == OperatorType.REGEX:
            import re

            return bool(re.search(str(self.value), str(field_value)))

        return False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingCondition":
        """Create from dictionary."""
        return cls(field=data["field"], operator=OperatorType(data["operator"]), value=data["value"])


@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""

    name: str
    endpoint: str
    model: str
    capabilities: List[str]
    max_tokens: int = 4096
    temperature: float = 0.1
    priority: int = 1
    enabled: bool = True
    api_key: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ProviderConfig":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            endpoint=data["endpoint"],
            model=data["model"],
            capabilities=data.get("capabilities", []),
            max_tokens=data.get("max_tokens", 4096),
            temperature=data.get("temperature", 0.1),
            priority=data.get("priority", 1),
            enabled=data.get("enabled", True),
            api_key=data.get("api_key"),
        )


@dataclass
class ABTestBucket:
    """A/B test bucket configuration."""

    provider: str
    percentage: float
    options: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ABTestBucket":
        """Create from dictionary."""
        return cls(provider=data["provider"], percentage=data["percentage"], options=data.get("options"))


@dataclass
class LoadBalanceTarget:
    """Load balance target configuration."""

    enabled: bool
    strategy: LoadBalanceStrategy
    providers: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoadBalanceTarget":
        """Create from dictionary."""
        return cls(enabled=data["enabled"], strategy=LoadBalanceStrategy(data["strategy"]), providers=data["providers"])


@dataclass
class RoutingTarget:
    """Routing target configuration."""

    provider: Optional[str] = None
    fallback: Optional[str] = None
    options: Optional[Dict[str, Any]] = None
    ab_test: Optional[Dict[str, Any]] = None
    load_balance: Optional[LoadBalanceTarget] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingTarget":
        """Create from dictionary."""
        load_balance = None
        if "load_balance" in data:
            load_balance = LoadBalanceTarget.from_dict(data["load_balance"])

        return cls(
            provider=data.get("provider"),
            fallback=data.get("fallback"),
            options=data.get("options"),
            ab_test=data.get("ab_test"),
            load_balance=load_balance,
        )


@dataclass
class RoutingRule:
    """A routing rule with conditions and target."""

    name: str
    description: str
    conditions: List[RoutingCondition]
    target: RoutingTarget
    enabled: bool = True
    weight: int = 100

    def matches(self, request_data: Dict[str, Any]) -> bool:
        """Check if rule matches request data."""
        if not self.enabled:
            return False

        # All conditions must be true (AND logic)
        return all(condition.evaluate(request_data) for condition in self.conditions)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoutingRule":
        """Create from dictionary."""
        conditions = [RoutingCondition.from_dict(cond) for cond in data.get("conditions", [])]

        return cls(
            name=data["name"],
            description=data["description"],
            conditions=conditions,
            target=RoutingTarget.from_dict(data["target"]),
            enabled=data.get("enabled", True),
            weight=data.get("weight", 100),
        )


@dataclass
class RoutingResult:
    """Result of routing decision."""

    provider: str
    rule_name: str
    options: Dict[str, Any]
    fallback_provider: Optional[str] = None
    ab_test_bucket: Optional[str] = None
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "rule_name": self.rule_name,
            "options": self.options,
            "fallback_provider": self.fallback_provider,
            "ab_test_bucket": self.ab_test_bucket,
            "processing_time_ms": self.processing_time_ms,
        }


class ConfigurableRoutingSystem:
    """O.2 Configurable Routing System with hot reload and A/B testing."""

    def __init__(self, config_path: str = "config/routing.yml"):
        """Initialize routing system."""
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.providers: Dict[str, ProviderConfig] = {}
        self.rules: List[RoutingRule] = []
        self.last_config_mtime = 0.0

        # A/B testing state
        self._ab_test_buckets: Dict[str, str] = {}  # user_id -> bucket

        # Load balancing state
        self._round_robin_counters: Dict[str, int] = {}

        # Circuit breaker state (simplified)
        self._circuit_breaker_state: Dict[str, Dict[str, Any]] = {}

        # Load initial configuration
        self.reload_config()

    def reload_config(self) -> bool:
        """Reload configuration from file if changed."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Config file not found: {self.config_path}")

            current_mtime = self.config_path.stat().st_mtime
            if current_mtime <= self.last_config_mtime:
                return False  # No changes

            with open(self.config_path, "r") as f:
                new_config = yaml.safe_load(f)

            self._validate_config(new_config)
            self.config = new_config
            self._load_providers()
            self._load_rules()
            self.last_config_mtime = current_mtime

            active_providers_gauge.set(len([p for p in self.providers.values() if p.enabled]))

            return True

        except Exception as e:
            print(f"Error reloading config: {e}")
            return False

    def _validate_config(self, config: Dict[str, Any]):
        """Validate configuration structure."""
        required_sections = ["routing_version", "providers", "rules"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")

    def _load_providers(self):
        """Load provider configurations."""
        self.providers.clear()
        for name, provider_data in self.config.get("providers", {}).items():
            self.providers[name] = ProviderConfig.from_dict(name, provider_data)

    def _load_rules(self):
        """Load routing rules."""
        self.rules.clear()
        for rule_data in self.config.get("rules", []):
            self.rules.append(RoutingRule.from_dict(rule_data))

        # Sort rules by weight (highest first)
        self.rules.sort(key=lambda r: r.weight, reverse=True)

    async def route_request(self, request_data: Dict[str, Any], user_id: Optional[str] = None) -> RoutingResult:
        """
        Route request to appropriate provider.

        Args:
            request_data: Request metadata for routing decisions
            user_id: User ID for A/B test bucket assignment

        Returns:
            RoutingResult with provider and configuration
        """
        with tracer.start_span("routing.route_request") as span:
            start_time = time.time()

            # Hot reload configuration if needed
            self.reload_config()

            span.set_attribute("routing.component", request_data.get("component", "unknown"))
            span.set_attribute("routing.operation_type", request_data.get("operation_type", "unknown"))

            try:
                # Find matching rule
                matching_rule = None
                for rule in self.rules:
                    if rule.matches(request_data):
                        matching_rule = rule
                        break

                if not matching_rule:
                    raise ValueError("No matching routing rule found")

                # Resolve target provider
                result = await self._resolve_target(matching_rule.target, request_data, user_id)
                result.rule_name = matching_rule.name
                result.processing_time_ms = (time.time() - start_time) * 1000

                # Update metrics
                routing_decisions_total.labels(
                    rule_name=matching_rule.name,
                    provider=result.provider,
                    component=request_data.get("component", "unknown"),
                ).inc()

                span.set_attribute("routing.rule_name", matching_rule.name)
                span.set_attribute("routing.provider", result.provider)
                span.set_attribute("routing.processing_time_ms", result.processing_time_ms)

                return result

            except Exception as e:
                span.set_attribute("routing.error", str(e))

                # Fallback to default provider
                default_provider = self.config.get("defaults", {}).get("provider", "claude")
                return RoutingResult(
                    provider=default_provider,
                    rule_name="error_fallback",
                    options={"temperature": 0.1, "max_tokens": 4096},
                    processing_time_ms=(time.time() - start_time) * 1000,
                )

    async def _resolve_target(
        self, target: RoutingTarget, request_data: Dict[str, Any], user_id: Optional[str]
    ) -> RoutingResult:
        """Resolve routing target to specific provider."""

        # Handle A/B testing
        if target.ab_test and target.ab_test.get("enabled", False):
            return await self._resolve_ab_test(target.ab_test, request_data, user_id)

        # Handle load balancing
        if target.load_balance and target.load_balance.enabled:
            return await self._resolve_load_balance(target.load_balance, request_data)

        # Handle simple provider routing
        if target.provider:
            provider_config = self.providers.get(target.provider)
            if not provider_config or not provider_config.enabled:
                # Fall back to fallback provider
                if target.fallback:
                    fallback_config = self.providers.get(target.fallback)
                    if fallback_config and fallback_config.enabled:
                        return RoutingResult(
                            provider=target.fallback,
                            rule_name="",
                            options=target.options or {},
                            fallback_provider=target.provider,
                        )

                raise ValueError(f"Provider {target.provider} not available")

            return RoutingResult(provider=target.provider, rule_name="", options=target.options or {})

        raise ValueError("Invalid routing target configuration")

    async def _resolve_ab_test(
        self, ab_test_config: Dict[str, Any], request_data: Dict[str, Any], user_id: Optional[str]
    ) -> RoutingResult:
        """Resolve A/B test target."""
        test_name = ab_test_config["test_name"]
        buckets = [ABTestBucket.from_dict(b) for b in ab_test_config["buckets"]]

        # Assign user to bucket
        bucket_id = self._assign_ab_bucket(test_name, user_id or "anonymous", buckets)
        selected_bucket = next(b for b in buckets if f"{test_name}_{b.provider}" == bucket_id)

        # Update metrics
        ab_test_assignments_total.labels(test_name=test_name, bucket=bucket_id, provider=selected_bucket.provider).inc()

        return RoutingResult(
            provider=selected_bucket.provider,
            rule_name="",
            options=selected_bucket.options or {},
            ab_test_bucket=bucket_id,
        )

    async def _resolve_load_balance(
        self, load_balance_config: LoadBalanceTarget, request_data: Dict[str, Any]
    ) -> RoutingResult:
        """Resolve load balance target."""
        strategy = load_balance_config.strategy
        providers = load_balance_config.providers

        if strategy == LoadBalanceStrategy.ROUND_ROBIN:
            return self._round_robin_select(providers)
        elif strategy == LoadBalanceStrategy.WEIGHTED:
            return self._weighted_select(providers)
        elif strategy == LoadBalanceStrategy.RANDOM:
            return self._random_select(providers)
        else:
            # Default to first available provider
            for provider_data in providers:
                provider_name = provider_data["provider"]
                if self.providers.get(provider_name, {}).enabled:
                    return RoutingResult(provider=provider_name, rule_name="", options=provider_data.get("options", {}))

        raise ValueError("No available providers for load balancing")

    def _assign_ab_bucket(self, test_name: str, user_id: str, buckets: List[ABTestBucket]) -> str:
        """Assign user to A/B test bucket."""
        # Check if user already has bucket assignment
        bucket_key = f"{test_name}_{user_id}"
        if bucket_key in self._ab_test_buckets:
            return self._ab_test_buckets[bucket_key]

        # Hash-based assignment for consistency
        hash_input = f"{test_name}_{user_id}".encode("utf-8")
        hash_value = int(hashlib.sha256(hash_input).hexdigest()[:8], 16)
        percentage = (hash_value % 100) + 1

        cumulative = 0
        for bucket in buckets:
            cumulative += bucket.percentage
            if percentage <= cumulative:
                bucket_id = f"{test_name}_{bucket.provider}"
                self._ab_test_buckets[bucket_key] = bucket_id
                return bucket_id

        # Fallback to first bucket
        bucket_id = f"{test_name}_{buckets[0].provider}"
        self._ab_test_buckets[bucket_key] = bucket_id
        return bucket_id

    def _round_robin_select(self, providers: List[Dict[str, Any]]) -> RoutingResult:
        """Round robin provider selection."""
        providers_key = "_".join(p["provider"] for p in providers)
        counter = self._round_robin_counters.get(providers_key, 0)

        selected_provider = providers[counter % len(providers)]
        self._round_robin_counters[providers_key] = (counter + 1) % len(providers)

        return RoutingResult(
            provider=selected_provider["provider"], rule_name="", options=selected_provider.get("options", {})
        )

    def _weighted_select(self, providers: List[Dict[str, Any]]) -> RoutingResult:
        """Weighted provider selection."""
        import random

        total_weight = sum(p.get("weight", 1) for p in providers)
        selection = random.uniform(0, total_weight)

        cumulative = 0
        for provider_data in providers:
            cumulative += provider_data.get("weight", 1)
            if selection <= cumulative:
                return RoutingResult(
                    provider=provider_data["provider"], rule_name="", options=provider_data.get("options", {})
                )

        # Fallback to first provider
        return RoutingResult(provider=providers[0]["provider"], rule_name="", options=providers[0].get("options", {}))

    def _random_select(self, providers: List[Dict[str, Any]]) -> RoutingResult:
        """Random provider selection."""
        import random

        selected_provider = random.choice(providers)
        return RoutingResult(
            provider=selected_provider["provider"], rule_name="", options=selected_provider.get("options", {})
        )

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing system statistics."""
        return {
            "config_version": self.config.get("routing_version"),
            "last_reload": self.last_config_mtime,
            "providers": {
                name: {"enabled": config.enabled, "priority": config.priority, "capabilities": config.capabilities}
                for name, config in self.providers.items()
            },
            "rules": {
                rule.name: {"enabled": rule.enabled, "weight": rule.weight, "conditions_count": len(rule.conditions)}
                for rule in self.rules
            },
            "ab_tests": {"active_assignments": len(self._ab_test_buckets)},
        }

    def preview_routing(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Preview routing decision without executing."""
        matching_rules = []
        for rule in self.rules:
            if rule.matches(request_data):
                matching_rules.append(
                    {
                        "name": rule.name,
                        "description": rule.description,
                        "weight": rule.weight,
                        "target": rule.target.__dict__,
                    }
                )

        return {
            "request_data": request_data,
            "matching_rules": matching_rules,
            "selected_rule": matching_rules[0] if matching_rules else None,
        }


# Global routing system instance
_routing_system: Optional[ConfigurableRoutingSystem] = None


def get_routing_system() -> ConfigurableRoutingSystem:
    """Get the default routing system instance."""
    global _routing_system
    if _routing_system is None:
        _routing_system = ConfigurableRoutingSystem()
    return _routing_system
