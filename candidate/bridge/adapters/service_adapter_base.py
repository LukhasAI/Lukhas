"""
⚛️🧠🛡️ LUKHAS AI Service Adapter Base

Trinity Framework Integration:
- ⚛️ Identity: Secure authentication and capability token validation
- 🧠 Consciousness: Agent communication and state awareness
- 🛡️ Guardian: Ethical oversight and consent validation

Service Adapter Integration Specialist
Common resilience, telemetry, and consent validation for all adapters
"""
from typing import List
import logging
import streamlit as st

import asyncio
import contextlib
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from functools import wraps
from typing import Any, Optional

# Add paths for LUKHAS AI module imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../core"))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../orchestration"))

# Import LUKHAS AI modules - Trinity Framework Integration
try:
    from lukhas.governance.consent_ledger.ledger_v1 import (
        ConsentLedgerV1,
        PolicyVerdict,
    )
except ImportError:
    ConsentLedgerV1 = None
    PolicyVerdict = None

try:
    # ⚛️ Identity module integration
    from identity.identity_core import IdentityCore
except ImportError:
    IdentityCore = None

try:
    # 🧠 Consciousness integration
    from candidate.orchestration.symbolic_kernel_bus import SymbolicKernelBus
except ImportError:
    SymbolicKernelBus = None

try:
    # 🛡️ Guardian system integration
    from lukhas.governance.guardian_system import GuardianSystem
except ImportError:
    GuardianSystem = None

try:
    # Memory integration for adapter state persistence
    from lukhas.memory.service import MemoryService
except ImportError:
    MemoryService = None

try:
    # Guardian system integration - import Guardian class
    from lukhas.governance.guardian_system import GuardianSystem as GuardianSystemClass
except ImportError:
    GuardianSystemClass = None


class AdapterState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CapabilityToken:
    """Capability token per global schema"""

    token_id: str
    lid: str
    scope: list[str]
    resource_ids: list[str]
    ttl: int
    audience: str
    issued_at: str
    signature: str

    def is_valid(self) -> bool:
        """Check if token is still valid"""
        issued = datetime.fromisoformat(self.issued_at)
        expiry = issued + timedelta(seconds=self.ttl)
        return datetime.now(timezone.utc) < expiry

    def has_scope(self, required_scope: str) -> bool:
        """Check if token has required scope"""
        return required_scope in self.scope


class ResilienceManager:
    """Circuit breakers and retry logic"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = AdapterState.CLOSED
        self.half_open_successes = 0

    def record_success(self):
        """Record successful request"""
        if self.state == AdapterState.HALF_OPEN:
            self.half_open_successes += 1
            if self.half_open_successes >= 3:
                self.state = AdapterState.CLOSED
                self.failure_count = 0
        elif self.state == AdapterState.CLOSED:
            self.failure_count = 0

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = AdapterState.OPEN

    def can_attempt_request(self) -> bool:
        """Check if request should be attempted"""
        if self.state == AdapterState.CLOSED:
            return True

        if self.state == AdapterState.OPEN:
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = AdapterState.HALF_OPEN
                    self.half_open_successes = 0
                    return True
            return False

        return True  # HALF_OPEN

    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state.value


class TelemetryCollector:
    """Enhanced metrics and Λ-trace emission with comprehensive audit trail logging"""

    def __init__(self, adapter_name: str):
        self.adapter_name = adapter_name
        self.metrics = {
            "request_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_latency_ms": 0,
            "capability_tokens_used": [],
            "last_trace_id": None,
            "security_events": [],
            "dangerous_operations": 0,
            "consent_denials": 0,
            "rate_limit_hits": 0,
        }
        self.ledger = ConsentLedgerV1() if ConsentLedgerV1 else None
        self.audit_trail = []  # In-memory audit trail

    def record_request(
        self,
        lid: str,
        action: str,
        resource: str,
        capability_token: Optional[CapabilityToken],
        latency_ms: float,
        success: bool,
        context: Optional[dict] = None,
    ):
        """Enhanced request recording with comprehensive audit trail and Λ-trace integration"""

        # Update basic metrics
        self.metrics["request_count"] += 1
        if success:
            self.metrics["success_count"] += 1
        else:
            self.metrics["failure_count"] += 1
        self.metrics["total_latency_ms"] += latency_ms

        # Track security-specific metrics
        if context:
            if context.get("denial_type"):
                self.metrics["consent_denials"] += 1
                self.metrics["security_events"].append(
                    {
                        "type": "consent_denial",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "lid": lid,
                        "action": action,
                        "reason": context.get("reason", "Unknown"),
                    }
                )

            if "dangerous_operation" in context.get("approval_type", ""):
                self.metrics["dangerous_operations"] += 1
                self.metrics["security_events"].append(
                    {
                        "type": "dangerous_operation",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "lid": lid,
                        "action": action,
                        "confirmed": context.get("confirmed", False),
                    }
                )

            if context.get("reason") == "rate_limit_exceeded":
                self.metrics["rate_limit_hits"] += 1

        if capability_token:
            self.metrics["capability_tokens_used"].append(capability_token.token_id)

        # Create comprehensive audit trail entry
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "adapter": self.adapter_name,
            "lid": lid,
            "action": action,
            "resource": resource,
            "success": success,
            "latency_ms": latency_ms,
            "capability_token_id": (capability_token.token_id if capability_token else None),
            "context": context or {},
            "trace_id": None,  # Will be filled by Λ-trace
        }

        # Emit Λ-trace if ledger available - Enhanced Trinity Framework integration
        if self.ledger and PolicyVerdict:
            trace_context = {
                "adapter": self.adapter_name,
                "latency_ms": latency_ms,
                "success": success,
                "trinity_framework": "⚛️🧠🛡️",
                "audit_entry_id": len(self.audit_trail),
                "security_level": self._assess_security_level(action, context),
            }
            if context:
                trace_context.update(context)

            trace = self.ledger.create_trace(
                lid=lid,
                action=f"{self.adapter_name}.{action}",
                resource=resource,
                purpose="adapter_operation",
                verdict=PolicyVerdict.ALLOW if success else PolicyVerdict.DENY,
                capability_token_id=(capability_token.token_id if capability_token else None),
                context=trace_context,
            )
            self.metrics["last_trace_id"] = trace.trace_id
            audit_entry["trace_id"] = trace.trace_id

        # Store in audit trail
        self.audit_trail.append(audit_entry)

        # Keep audit trail manageable (last 1000 entries)
        if len(self.audit_trail) > 1000:
            self.audit_trail = self.audit_trail[-1000:]

    def _assess_security_level(self, action: str, context: Optional[dict]) -> str:
        """Assess security level of operation for audit purposes"""
        if context and context.get("denial_type"):
            return "high_risk"
        elif "delete" in action.lower() or "remove" in action.lower():
            return "medium_risk"
        elif "read" in action.lower() or "list" in action.lower():
            return "low_risk"
        else:
            return "medium_risk"

    def get_metrics(self) -> dict:
        """Get current metrics"""
        avg_latency = self.metrics["total_latency_ms"] / max(self.metrics["request_count"], 1)

        return {
            "adapter": self.adapter_name,
            "requests": self.metrics["request_count"],
            "success_rate": (self.metrics["success_count"] / max(self.metrics["request_count"], 1)),
            "avg_latency_ms": avg_latency,
            "unique_tokens": len(set(self.metrics["capability_tokens_used"])),
        }


def with_resilience(func):
    """Decorator for resilient adapter methods"""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.resilience.can_attempt_request():
            return {
                "error": "service_unavailable",
                "circuit_state": self.resilience.get_state(),
            }

        max_retries = 3
        backoff = 1

        for attempt in range(max_retries):
            try:
                start_time = time.perf_counter()
                result = await func(self, *args, **kwargs)

                # Record success
                latency_ms = (time.perf_counter() - start_time) * 1000
                self.resilience.record_success()

                # Record telemetry
                if hasattr(self, "telemetry"):
                    lid = kwargs.get("lid", "unknown")
                    action = func.__name__
                    resource = kwargs.get("resource", "unknown")
                    token = kwargs.get("capability_token")

                    self.telemetry.record_request(lid, action, resource, token, latency_ms, True)

                return result

            except Exception as e:
                self.resilience.record_failure()

                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    if hasattr(self, "telemetry"):
                        self.telemetry.record_request(
                            kwargs.get("lid", "unknown"),
                            func.__name__,
                            kwargs.get("resource", "unknown"),
                            kwargs.get("capability_token"),
                            0,
                            False,
                        )
                    raise e

        return {"error": "max_retries_exceeded"}

    return wrapper


class BaseServiceAdapter(ABC):
    """⚛️🧠🛡️ Base adapter class for all external services

    Trinity Framework Integration:
    - ⚛️ Identity: Secure authentication and access control
    - 🧠 Consciousness: State awareness and agent communication
    - 🛡️ Guardian: Ethical oversight and consent validation

    Features:
    - Circuit breaker pattern for resilience
    - Capability token-based authorization
    - Comprehensive telemetry and Λ-trace logging
    - Dry-run mode for safe testing
    - Integration with LUKHAS AI consciousness system
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.resilience = ResilienceManager()
        self.telemetry = TelemetryCollector(service_name)

        # Trinity Framework integration - Defensive initialization
        self.ledger = self._safe_init(ConsentLedgerV1)
        self.identity_core = self._safe_init(IdentityCore)
        self.kernel_bus = self._safe_init(SymbolicKernelBus)
        self.guardian = self._safe_init(GuardianSystem)
        self.memory_service = self._safe_init(MemoryService)

        self.dry_run_mode = False
        self.consciousness_active = False
        self._register_scopes()
        self._initialize_consciousness_integration()

    def _safe_init(self, cls):
        """Safely initialize a class, handling modules and import issues"""
        if cls is None:
            return None

        try:
            # Check if it's actually a class/callable
            if not callable(cls):
                return None

            # Try to instantiate
            return cls()
        except Exception:
            # Graceful fallback if initialization fails
            return None

    def _register_scopes(self):
        """Contribute to central capability scope registry - Trinity Framework"""
        self.supported_scopes = {
            "read": "Read access to resources",
            "write": "Write/modify resources",
            "delete": "Delete resources",
            "list": "List available resources",
            "execute": "Execute operations",
            "monitor": "Monitor service health and metrics",
            "configure": "Configure service settings",
        }

    def _initialize_consciousness_integration(self):
        """🧠 Initialize consciousness system integration"""
        if self.kernel_bus:
            try:
                # Register adapter with consciousness system
                self.kernel_bus.register_service(
                    f"adapter.{self.service_name}",
                    {
                        "type": "service_adapter",
                        "capabilities": list(self.supported_scopes.keys()),
                        "trinity_integration": True,
                    },
                )
                self.consciousness_active = True
            except Exception:
                # Fallback gracefully if consciousness not available
                pass

    def set_dry_run(self, enabled: bool):
        """Enable/disable dry-run mode"""
        self.dry_run_mode = enabled

    def validate_capability_token(self, token: CapabilityToken, required_scope: str) -> bool:
        """Validate capability token"""
        if not token.is_valid():
            return False

        if not token.has_scope(required_scope):
            return False

        return token.audience == self.service_name

    async def check_consent(self, lid: str, action: str, context: Optional[dict] = None) -> bool:
        """🛡️ Check consent before accessing external service - Guardian integration"""

        # Guardian system validation
        if self.guardian:
            try:
                guardian_check = await self.guardian.validate_operation(
                    lid=lid,
                    service=self.service_name,
                    action=action,
                    context=context or {},
                )
                if not guardian_check.get("allowed", False):
                    return False
            except Exception:
                # Guardian validation failed - be conservative
                return False

        # Consent ledger validation
        if not self.ledger:
            return True  # Allow if ledger not available (testing)

        consent_check = self.ledger.check_consent(lid=lid, resource_type=self.service_name, action=action)
        return consent_check["allowed"]

    async def authenticate_with_identity(self, lid: str, credentials: dict) -> dict:
        """⚛️ Authenticate with Identity module integration"""
        if self.identity_core:
            try:
                # Use LUKHAS AI identity system for authentication
                identity_result = await self.identity_core.authenticate(
                    lid=lid, service=self.service_name, credentials=credentials
                )
                return identity_result
            except Exception as e:
                return {"error": "identity_authentication_failed", "details": str(e)}

        # Fallback to service-specific authentication
        return await self.authenticate(credentials)

    async def notify_consciousness(self, event_type: str, data: dict):
        """🧠 Notify consciousness system of important events"""
        if self.kernel_bus and self.consciousness_active:
            try:
                await self.kernel_bus.emit_event(
                    {
                        "type": f"adapter.{event_type}",
                        "service": self.service_name,
                        "data": data,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
            except Exception:
                # Graceful degradation if consciousness not available
                pass

    @abstractmethod
    async def authenticate(self, credentials: dict) -> dict:
        """Authenticate with external service"""
        pass

    @abstractmethod
    async def fetch_resource(self, lid: str, resource_id: str, capability_token: CapabilityToken) -> dict:
        """Fetch resource from external service"""
        pass

    def get_health_status(self) -> dict:
        """⚛️🧠🛡️ Get adapter health status with Trinity Framework integration"""
        status = {
            "service": self.service_name,
            "circuit_state": self.resilience.get_state(),
            "metrics": self.telemetry.get_metrics(),
            "dry_run_mode": self.dry_run_mode,
            "trinity_framework": {
                "identity_active": self.identity_core is not None,
                "consciousness_active": self.consciousness_active,
                "guardian_active": self.guardian is not None,
                "memory_active": self.memory_service is not None,
                "consent_ledger_active": self.ledger is not None,
            },
        }

        # Add consciousness system status if available
        if self.kernel_bus and self.consciousness_active:
            with contextlib.suppress(Exception):
                status["consciousness_status"] = self.kernel_bus.get_service_status(f"adapter.{self.service_name}")

        return status

    async def persist_state(self, state_data: dict) -> bool:
        """Persist adapter state using Memory service"""
        if self.memory_service:
            try:
                await self.memory_service.store_adapter_state(adapter_name=self.service_name, state=state_data)
                return True
            except Exception:
                return False
        return False

    async def restore_state(self) -> Optional[dict]:
        """Restore adapter state from Memory service"""
        if self.memory_service:
            try:
                state = await self.memory_service.get_adapter_state(self.service_name)
                return state
            except Exception:
                return None
        return None

    async def detect_duress_signal(self, lid: str, request_data: dict) -> dict[str, Any]:
        """🚨 Detect duress/shadow gestures (Canary Pack 5)"""

        duress_indicators = {
            "temporal_anomalies": [],
            "behavioral_anomalies": [],
            "pattern_anomalies": [],
            "risk_score": 0.0,
        }

        # Check for temporal anomalies (unusual timing)
        current_hour = datetime.now(timezone.utc).hour
        if current_hour < 6 or current_hour > 22:  # Late night/early morning
            duress_indicators["temporal_anomalies"].append("unusual_time_access")
            duress_indicators["risk_score"] += 0.3

        # Check for rapid successive requests
        if hasattr(self, "_last_request_time"):
            time_diff = time.time() - self._last_request_time
            if time_diff < 5:  # Less than 5 seconds between requests
                duress_indicators["behavioral_anomalies"].append("rapid_requests")
                duress_indicators["risk_score"] += 0.4

        self._last_request_time = time.time()

        # Check for pattern anomalies (specific duress patterns)
        request_str = str(request_data).lower()
        duress_patterns = {
            "help_me": 0.8,
            "emergency": 0.7,
            "forced": 0.6,
            "under_threat": 0.9,
            "not_me": 0.5,
        }

        for pattern, score in duress_patterns.items():
            if pattern in request_str:
                duress_indicators["pattern_anomalies"].append(pattern)
                duress_indicators["risk_score"] += score

        # Check for shadow gesture sequences (specific key combinations)
        if request_data.get("shadow_sequence"):
            duress_indicators["pattern_anomalies"].append("shadow_sequence_detected")
            duress_indicators["risk_score"] += 0.9

        # Evaluate overall risk
        is_duress = duress_indicators["risk_score"] > 0.7

        if is_duress:
            # Log duress detection
            await self._log_denial(
                lid,
                "duress_detected",
                "security_threat",
                f"Duress signals detected: {duress_indicators}",
            )

            # Notify security systems
            await self.notify_consciousness(
                "duress_detected",
                {
                    "lid": lid,
                    "indicators": duress_indicators,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "requires_investigation": True,
                },
            )

        return {
            "duress_detected": is_duress,
            "risk_score": duress_indicators["risk_score"],
            "indicators": duress_indicators,
            "recommended_action": "block_and_investigate" if is_duress else "allow",
        }


class DryRunPlanner:
    """Dry-run planner for operations without side effects"""

    def __init__(self):
        self.planned_operations = []

    def plan_operation(self, operation: str, params: dict) -> dict:
        """Plan an operation without executing"""
        plan = {
            "operation": operation,
            "params": params,
            "estimated_time_ms": self._estimate_time(operation),
            "required_scopes": self._get_required_scopes(operation),
            "potential_errors": self._predict_errors(operation, params),
        }

        self.planned_operations.append(plan)
        return plan

    def _estimate_time(self, operation: str) -> int:
        """Estimate operation time"""
        estimates = {
            "list": 200,
            "fetch": 500,
            "upload": 1000,
            "delete": 300,
            "search": 800,
        }
        return estimates.get(operation, 500)

    def _get_required_scopes(self, operation: str) -> list[str]:
        """Get required scopes"""
        scope_map = {
            "list": ["read", "list"],
            "fetch": ["read"],
            "upload": ["write"],
            "delete": ["delete"],
            "search": ["read", "list"],
        }
        return scope_map.get(operation, ["read"])

    def _predict_errors(self, operation: str, params: dict) -> list[str]:
        """Predict potential errors"""
        errors = []

        if not params.get("resource_id"):
            errors.append("missing_resource_id")

        if operation == "delete" and not params.get("confirmation"):
            errors.append("delete_requires_confirmation")

        return errors


# ⚛️🧠🛡️ LUKHAS AI Service Adapter Exports
# Critical fix: Add ServiceAdapterBase alias for backward compatibility
ServiceAdapterBase = BaseServiceAdapter


# Rate limiting implementation
class RateLimiter:
    """🚦 Rate limiter for adapter operations (Canary Pack 5)"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # lid -> [(timestamp, action), ...]

    def is_allowed(self, lid: str, action: str) -> dict[str, Any]:
        """Check if request is within rate limits"""
        now = time.time()

        # Initialize if new user
        if lid not in self.requests:
            self.requests[lid] = []

        # Clean old requests outside window
        self.requests[lid] = [(ts, act) for ts, act in self.requests[lid] if now - ts < self.window_seconds]

        # Check if over limit
        current_count = len(self.requests[lid])

        if current_count >= self.max_requests:
            return {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "current_count": current_count,
                "max_requests": self.max_requests,
                "window_seconds": self.window_seconds,
                "retry_after": self.window_seconds,
            }

        # Record this request
        self.requests[lid].append((now, action))

        return {
            "allowed": True,
            "current_count": current_count + 1,
            "remaining": self.max_requests - current_count - 1,
        }


# Export list for proper module imports
__all__ = [
    "AdapterState",
    "BaseServiceAdapter",
    "CapabilityToken",
    "DryRunPlanner",
    "RateLimiter",
    "ResilienceManager",
    "ServiceAdapterBase",  # Alias for backward compatibility
    "TelemetryCollector",
    "with_resilience",
]
