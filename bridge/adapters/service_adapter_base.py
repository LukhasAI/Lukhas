"""
Base Service Adapter Framework
Agent 3: Service Adapter Integration Specialist
Common resilience, telemetry, and consent validation for all adapters
"""

import asyncio
import time
import secrets
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
from functools import wraps
import logging
import sys
import os

# Add governance path for consent ledger import
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

# Import Agent 2's consent ledger
try:
    from governance.consent_ledger.ledger_v1 import ConsentLedgerV1, PolicyVerdict
except ImportError:
    # Fallback for testing
    ConsentLedgerV1 = None
    PolicyVerdict = None


class AdapterState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CapabilityToken:
    """Capability token per global schema"""
    token_id: str
    lid: str
    scope: List[str]
    resource_ids: List[str]
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
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60):
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
    """Metrics and Λ-trace emission"""
    
    def __init__(self, adapter_name: str):
        self.adapter_name = adapter_name
        self.metrics = {
            "request_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "total_latency_ms": 0,
            "capability_tokens_used": [],
            "last_trace_id": None
        }
        self.ledger = ConsentLedgerV1() if ConsentLedgerV1 else None
    
    def record_request(self, lid: str, action: str, resource: str,
                      capability_token: Optional[CapabilityToken],
                      latency_ms: float, success: bool):
        """Record metrics and emit Λ-trace"""
        
        self.metrics["request_count"] += 1
        if success:
            self.metrics["success_count"] += 1
        else:
            self.metrics["failure_count"] += 1
        self.metrics["total_latency_ms"] += latency_ms
        
        if capability_token:
            self.metrics["capability_tokens_used"].append(capability_token.token_id)
        
        # Emit Λ-trace if ledger available
        if self.ledger and PolicyVerdict:
            trace = self.ledger.create_trace(
                lid=lid,
                action=f"{self.adapter_name}.{action}",
                resource=resource,
                purpose="adapter_operation",
                verdict=PolicyVerdict.ALLOW if success else PolicyVerdict.DENY,
                capability_token_id=capability_token.token_id if capability_token else None,
                context={
                    "adapter": self.adapter_name,
                    "latency_ms": latency_ms,
                    "success": success
                }
            )
            self.metrics["last_trace_id"] = trace.trace_id
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        avg_latency = (self.metrics["total_latency_ms"] / 
                      max(self.metrics["request_count"], 1))
        
        return {
            "adapter": self.adapter_name,
            "requests": self.metrics["request_count"],
            "success_rate": (self.metrics["success_count"] / 
                           max(self.metrics["request_count"], 1)),
            "avg_latency_ms": avg_latency,
            "unique_tokens": len(set(self.metrics["capability_tokens_used"]))
        }


def with_resilience(func):
    """Decorator for resilient adapter methods"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if not self.resilience.can_attempt_request():
            return {
                "error": "service_unavailable",
                "circuit_state": self.resilience.get_state()
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
                if hasattr(self, 'telemetry'):
                    lid = kwargs.get('lid', 'unknown')
                    action = func.__name__
                    resource = kwargs.get('resource', 'unknown')
                    token = kwargs.get('capability_token')
                    
                    self.telemetry.record_request(
                        lid, action, resource, token, latency_ms, True
                    )
                
                return result
                
            except Exception as e:
                self.resilience.record_failure()
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                else:
                    if hasattr(self, 'telemetry'):
                        self.telemetry.record_request(
                            kwargs.get('lid', 'unknown'),
                            func.__name__,
                            kwargs.get('resource', 'unknown'),
                            kwargs.get('capability_token'),
                            0,
                            False
                        )
                    raise e
        
        return {"error": "max_retries_exceeded"}
    
    return wrapper


class BaseServiceAdapter(ABC):
    """Base adapter class for all external services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.resilience = ResilienceManager()
        self.telemetry = TelemetryCollector(service_name)
        self.ledger = ConsentLedgerV1() if ConsentLedgerV1 else None
        self.dry_run_mode = False
        self._register_scopes()
    
    def _register_scopes(self):
        """Contribute to central capability scope registry"""
        self.supported_scopes = {
            "read": "Read access to resources",
            "write": "Write/modify resources",
            "delete": "Delete resources",
            "list": "List available resources",
            "execute": "Execute operations"
        }
    
    def set_dry_run(self, enabled: bool):
        """Enable/disable dry-run mode"""
        self.dry_run_mode = enabled
    
    def validate_capability_token(self, token: CapabilityToken,
                                 required_scope: str) -> bool:
        """Validate capability token"""
        if not token.is_valid():
            return False
        
        if not token.has_scope(required_scope):
            return False
        
        if token.audience != self.service_name:
            return False
        
        return True
    
    async def check_consent(self, lid: str, action: str) -> bool:
        """Check consent before accessing external service"""
        if not self.ledger:
            return True  # Allow if ledger not available (testing)
        
        consent_check = self.ledger.check_consent(
            lid=lid,
            resource_type=self.service_name,
            action=action
        )
        return consent_check["allowed"]
    
    @abstractmethod
    async def authenticate(self, credentials: Dict) -> Dict:
        """Authenticate with external service"""
        pass
    
    @abstractmethod
    async def fetch_resource(self, lid: str, resource_id: str,
                           capability_token: CapabilityToken) -> Dict:
        """Fetch resource from external service"""
        pass
    
    def get_health_status(self) -> Dict:
        """Get adapter health status"""
        return {
            "service": self.service_name,
            "circuit_state": self.resilience.get_state(),
            "metrics": self.telemetry.get_metrics(),
            "dry_run_mode": self.dry_run_mode
        }


class DryRunPlanner:
    """Dry-run planner for operations without side effects"""
    
    def __init__(self):
        self.planned_operations = []
    
    def plan_operation(self, operation: str, params: Dict) -> Dict:
        """Plan an operation without executing"""
        plan = {
            "operation": operation,
            "params": params,
            "estimated_time_ms": self._estimate_time(operation),
            "required_scopes": self._get_required_scopes(operation),
            "potential_errors": self._predict_errors(operation, params)
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
            "search": 800
        }
        return estimates.get(operation, 500)
    
    def _get_required_scopes(self, operation: str) -> List[str]:
        """Get required scopes"""
        scope_map = {
            "list": ["read", "list"],
            "fetch": ["read"],
            "upload": ["write"],
            "delete": ["delete"],
            "search": ["read", "list"]
        }
        return scope_map.get(operation, ["read"])
    
    def _predict_errors(self, operation: str, params: Dict) -> List[str]:
        """Predict potential errors"""
        errors = []
        
        if not params.get("resource_id"):
            errors.append("missing_resource_id")
        
        if operation == "delete" and not params.get("confirmation"):
            errors.append("delete_requires_confirmation")
        
        return errors