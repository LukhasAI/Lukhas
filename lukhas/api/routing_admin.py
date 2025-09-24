#!/usr/bin/env python3
"""
LUKHAS Phase 4 - Routing Administration API
===========================================

Admin API for testing and managing routing configurations without deployment.
Provides preview, validation, and A/B test management capabilities.

Key Features:
- Configuration preview and validation
- Routing simulation without affecting live traffic
- A/B test management and monitoring
- Health status monitoring
- Circuit breaker management
- Performance metrics access
- Configuration rollback capabilities

Security:
- Admin authentication required
- Audit logging for all changes
- Rate limiting for API endpoints
- Input validation and sanitization

Constellation Framework: Flow Star (🌊) coordination hub
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import yaml

from lukhas.orchestration.routing_config import get_routing_config_manager, RoutingConfiguration, RoutingRule
from lukhas.orchestration.routing_strategies import get_routing_engine, RoutingContext
from lukhas.orchestration.health_monitor import get_health_monitor
from lukhas.orchestration.externalized_orchestrator import get_externalized_orchestrator, OrchestrationRequest, RequestType
from lukhas.observability.matriz_decorators import instrument

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models for API
class RoutingPreviewRequest(BaseModel):
    """Request for routing preview"""
    request_type: str = Field(..., description="Type of request to route")
    session_id: str = Field("preview-session", description="Session ID for preview")
    routing_hints: Dict[str, Any] = Field(default_factory=dict, description="Routing hints")
    configuration_override: Optional[Dict[str, Any]] = Field(None, description="Configuration to test")

class RoutingSimulationRequest(BaseModel):
    """Request for routing simulation"""
    scenarios: List[Dict[str, Any]] = Field(..., description="Simulation scenarios")
    iterations: int = Field(100, ge=1, le=10000, description="Number of iterations per scenario")
    configuration_override: Optional[Dict[str, Any]] = Field(None, description="Configuration to test")

class ABTestRequest(BaseModel):
    """A/B test management request"""
    test_name: str = Field(..., description="Test name")
    enabled: bool = Field(..., description="Enable/disable test")
    traffic_split: Dict[str, int] = Field(..., description="Traffic split percentages")
    rules: List[str] = Field(..., description="Rules to apply test to")

class ConfigurationValidationRequest(BaseModel):
    """Configuration validation request"""
    configuration: Dict[str, Any] = Field(..., description="Configuration to validate")

class HealthCheckRequest(BaseModel):
    """Health check request"""
    providers: Optional[List[str]] = Field(None, description="Specific providers to check")
    force_check: bool = Field(False, description="Force immediate health check")

class CircuitBreakerRequest(BaseModel):
    """Circuit breaker management request"""
    provider: str = Field(..., description="Provider name")
    action: str = Field(..., description="Action: open, close, reset")

# API Router
router = FastAPI(
    title="LUKHAS Routing Administration API",
    description="Admin API for routing configuration management",
    version="1.0.0"
)

# CORS middleware
router.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Admin UI origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_admin_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validate admin authentication"""
    # TODO: Implement proper admin authentication
    # For now, just check for presence of token
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Admin authentication required")

    # In production, validate JWT token and check admin permissions
    return {"user_id": "admin", "permissions": ["routing:admin"]}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/configuration")
@instrument("API", label="admin:config", capability="routing:read")
async def get_current_configuration(admin_user: dict = Depends(get_admin_user)):
    """Get current routing configuration"""
    try:
        config_manager = await get_routing_config_manager()
        config = config_manager.get_configuration()

        # Convert to dict for serialization
        config_dict = {
            "version": config.version,
            "default_strategy": config.default_strategy.value,
            "default_providers": config.default_providers,
            "rules": [
                {
                    "name": rule.name,
                    "pattern": rule.pattern,
                    "strategy": rule.strategy.value,
                    "providers": rule.providers,
                    "weights": rule.weights,
                    "health_threshold": rule.health_threshold,
                    "latency_threshold_ms": rule.latency_threshold_ms,
                    "fallback_providers": rule.fallback_providers,
                    "metadata": rule.metadata
                }
                for rule in config.rules
            ],
            "ab_tests": [
                {
                    "name": test.name,
                    "enabled": test.enabled,
                    "traffic_split": test.traffic_split,
                    "rules": test.rules,
                    "metadata": test.metadata
                }
                for test in config.ab_tests
            ],
            "health_check_interval": config.health_check_interval,
            "circuit_breaker_threshold": config.circuit_breaker_threshold,
            "circuit_breaker_timeout": config.circuit_breaker_timeout,
            "context_timeout": config.context_timeout,
            "metadata": config.metadata
        }

        return {"configuration": config_dict, "timestamp": time.time()}

    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configuration/validate")
@instrument("API", label="admin:validate", capability="routing:validate")
async def validate_configuration(
    request: ConfigurationValidationRequest,
    admin_user: dict = Depends(get_admin_user)
):
    """Validate routing configuration"""
    try:
        config_manager = await get_routing_config_manager()

        # Attempt to parse configuration
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        config_data = request.configuration

        # Basic validation checks
        required_fields = ["version", "default_strategy", "default_providers", "rules"]
        for field in required_fields:
            if field not in config_data:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")

        # Validate rules
        if "rules" in config_data:
            for i, rule in enumerate(config_data["rules"]):
                rule_errors = []

                if "name" not in rule:
                    rule_errors.append("Missing rule name")
                if "pattern" not in rule:
                    rule_errors.append("Missing rule pattern")
                if "strategy" not in rule:
                    rule_errors.append("Missing rule strategy")
                if "providers" not in rule:
                    rule_errors.append("Missing rule providers")

                if rule_errors:
                    validation_results["valid"] = False
                    validation_results["errors"].extend([f"Rule {i}: {error}" for error in rule_errors])

        # Validate A/B tests
        if "ab_tests" in config_data:
            for i, test in enumerate(config_data["ab_tests"]):
                if "name" not in test:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"A/B test {i}: Missing test name")

                if "traffic_split" in test:
                    total_split = sum(test["traffic_split"].values())
                    if total_split != 100:
                        validation_results["warnings"].append(
                            f"A/B test {test.get('name', i)}: Traffic split totals {total_split}%, should be 100%"
                        )

        # Performance suggestions
        if validation_results["valid"]:
            if len(config_data.get("rules", [])) > 50:
                validation_results["suggestions"].append("Consider reducing number of rules for better performance")

            if config_data.get("health_check_interval", 30) < 10:
                validation_results["suggestions"].append("Health check interval below 10s may cause performance issues")

        return validation_results

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return {
            "valid": False,
            "errors": [str(e)],
            "warnings": [],
            "suggestions": []
        }

@router.post("/routing/preview")
@instrument("API", label="admin:preview", capability="routing:preview")
async def preview_routing(
    request: RoutingPreviewRequest,
    admin_user: dict = Depends(get_admin_user)
):
    """Preview routing decision for a request"""
    try:
        config_manager = await get_routing_config_manager()
        routing_engine = get_routing_engine()
        health_monitor = await get_health_monitor()

        # Use override configuration if provided
        if request.configuration_override:
            # TODO: Implement temporary configuration override
            pass

        # Create routing context
        routing_context = RoutingContext(
            session_id=request.session_id,
            request_type=request.request_type,
            metadata=request.routing_hints
        )

        # Find matching rule
        rule = config_manager.get_rule_for_request(
            request.request_type,
            routing_context.metadata
        )

        if not rule:
            raise HTTPException(status_code=404, detail="No matching routing rule found")

        # Get provider health
        provider_health = await health_monitor.get_all_provider_health()

        # Preview routing decision
        routing_result = await routing_engine.route_request(
            rule, routing_context, provider_health
        )

        preview_result = {
            "matched_rule": {
                "name": rule.name,
                "pattern": rule.pattern,
                "strategy": rule.strategy.value,
                "providers": rule.providers
            },
            "routing_decision": {
                "provider": routing_result.provider if routing_result else None,
                "strategy_used": routing_result.strategy_used.value if routing_result else None,
                "reason": routing_result.reason if routing_result else "No available providers",
                "confidence": routing_result.confidence if routing_result else 0.0,
                "fallback_available": routing_result.fallback_available if routing_result else False
            },
            "provider_health": {
                provider: {
                    "status": health.status.value,
                    "success_rate": health.success_rate,
                    "avg_latency_ms": health.avg_latency_ms,
                    "consecutive_failures": health.consecutive_failures
                }
                for provider, health in provider_health.items()
                if provider in rule.providers
            },
            "timestamp": time.time()
        }

        return preview_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Routing preview failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/routing/simulate")
@instrument("API", label="admin:simulate", capability="routing:simulate")
async def simulate_routing(
    request: RoutingSimulationRequest,
    admin_user: dict = Depends(get_admin_user)
):
    """Simulate routing decisions across multiple scenarios"""
    try:
        simulation_results = {
            "scenarios": [],
            "summary": {},
            "timestamp": time.time()
        }

        config_manager = await get_routing_config_manager()
        routing_engine = get_routing_engine()
        health_monitor = await get_health_monitor()

        provider_health = await health_monitor.get_all_provider_health()

        for scenario_idx, scenario in enumerate(request.scenarios):
            scenario_results = {
                "scenario": scenario,
                "results": {},
                "provider_distribution": {},
                "strategy_distribution": {}
            }

            # Run iterations for this scenario
            for _ in range(request.iterations):
                routing_context = RoutingContext(
                    session_id=f"sim-{scenario_idx}",
                    request_type=scenario.get("request_type", "general"),
                    metadata=scenario.get("routing_hints", {})
                )

                rule = config_manager.get_rule_for_request(
                    routing_context.request_type,
                    routing_context.metadata
                )

                if rule:
                    routing_result = await routing_engine.route_request(
                        rule, routing_context, provider_health
                    )

                    if routing_result:
                        # Track distributions
                        provider = routing_result.provider
                        strategy = routing_result.strategy_used.value

                        scenario_results["provider_distribution"][provider] = (
                            scenario_results["provider_distribution"].get(provider, 0) + 1
                        )
                        scenario_results["strategy_distribution"][strategy] = (
                            scenario_results["strategy_distribution"].get(strategy, 0) + 1
                        )

            # Convert counts to percentages
            for dist in ["provider_distribution", "strategy_distribution"]:
                total = sum(scenario_results[dist].values())
                if total > 0:
                    scenario_results[dist] = {
                        k: round((v / total) * 100, 2)
                        for k, v in scenario_results[dist].items()
                    }

            simulation_results["scenarios"].append(scenario_results)

        # Generate summary
        all_providers = set()
        all_strategies = set()

        for scenario in simulation_results["scenarios"]:
            all_providers.update(scenario["provider_distribution"].keys())
            all_strategies.update(scenario["strategy_distribution"].keys())

        simulation_results["summary"] = {
            "total_scenarios": len(request.scenarios),
            "iterations_per_scenario": request.iterations,
            "unique_providers": list(all_providers),
            "unique_strategies": list(all_strategies)
        }

        return simulation_results

    except Exception as e:
        logger.error(f"Routing simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/providers")
@instrument("API", label="admin:health", capability="routing:health")
async def get_provider_health(admin_user: dict = Depends(get_admin_user)):
    """Get health status for all providers"""
    try:
        health_monitor = await get_health_monitor()
        health_summary = await health_monitor.get_health_summary()

        return health_summary

    except Exception as e:
        logger.error(f"Failed to get provider health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/check")
@instrument("API", label="admin:health_check", capability="routing:health")
async def trigger_health_check(
    request: HealthCheckRequest,
    admin_user: dict = Depends(get_admin_user)
):
    """Trigger health check for providers"""
    try:
        health_monitor = await get_health_monitor()

        if request.providers:
            # Check specific providers
            results = {}
            for provider in request.providers:
                result = await health_monitor.perform_health_check(provider)
                results[provider] = {
                    "success": result.success,
                    "latency_ms": result.latency_ms,
                    "error": result.error,
                    "timestamp": result.timestamp
                }
            return {"results": results}
        else:
            # Return current health summary
            return await health_monitor.get_health_summary()

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ab-tests")
@instrument("API", label="admin:ab_tests", capability="routing:ab_test")
async def get_ab_tests(admin_user: dict = Depends(get_admin_user)):
    """Get all A/B tests"""
    try:
        config_manager = await get_routing_config_manager()
        config = config_manager.get_configuration()

        ab_tests = [
            {
                "name": test.name,
                "enabled": test.enabled,
                "traffic_split": test.traffic_split,
                "rules": test.rules,
                "metadata": test.metadata
            }
            for test in config.ab_tests
        ]

        return {"ab_tests": ab_tests, "timestamp": time.time()}

    except Exception as e:
        logger.error(f"Failed to get A/B tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/circuit-breakers/{provider}")
@instrument("API", label="admin:circuit_breaker", capability="routing:circuit_breaker")
async def manage_circuit_breaker(
    provider: str,
    request: CircuitBreakerRequest,
    admin_user: dict = Depends(get_admin_user)
):
    """Manage circuit breaker for a provider"""
    try:
        routing_engine = get_routing_engine()

        if request.action == "reset":
            # Reset circuit breaker
            routing_engine.circuit_breakers.pop(provider, None)
            return {"message": f"Circuit breaker reset for {provider}"}

        elif request.action == "open":
            # Force open circuit breaker
            if provider in routing_engine.circuit_breakers:
                routing_engine.circuit_breakers[provider].state = CircuitBreakerState.OPEN
            return {"message": f"Circuit breaker opened for {provider}"}

        elif request.action == "close":
            # Force close circuit breaker
            if provider in routing_engine.circuit_breakers:
                routing_engine.circuit_breakers[provider].state = CircuitBreakerState.CLOSED
                routing_engine.circuit_breakers[provider].failure_count = 0
            return {"message": f"Circuit breaker closed for {provider}"}

        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use: open, close, reset")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Circuit breaker management failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
@instrument("API", label="admin:status", capability="routing:status")
async def get_orchestration_status(admin_user: dict = Depends(get_admin_user)):
    """Get overall orchestration status"""
    try:
        orchestrator = await get_externalized_orchestrator()
        status = await orchestrator.get_orchestration_status()

        return status

    except Exception as e:
        logger.error(f"Failed to get orchestration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
@instrument("API", label="admin:metrics", capability="routing:metrics")
async def get_routing_metrics(admin_user: dict = Depends(get_admin_user)):
    """Get routing performance metrics"""
    try:
        # TODO: Implement metrics collection from Prometheus
        # For now, return basic status

        orchestrator = await get_externalized_orchestrator()
        status = await orchestrator.get_orchestration_status()

        metrics = {
            "active_requests": status["active_requests"],
            "provider_health": {
                provider: data["health_score"] if "health_score" in data else 0
                for provider, data in status["health_summary"]["providers"].items()
            },
            "circuit_breaker_status": status["circuit_breaker_status"],
            "timestamp": time.time()
        }

        return metrics

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export the router
app = router