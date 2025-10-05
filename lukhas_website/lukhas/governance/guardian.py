#!/usr/bin/env python3
"""
LUKHAS Governance Guardian - Environment-Aware Implementation
Production Schema v1.0.0

Guardian system with environment-based implementation selection.
Production environments use full validation, dev/staging use mock.
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class GuardianMode(Enum):
    """Guardian operation modes"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class PolicyViolation(Exception):
    """Raised when a Guardian policy is violated"""
    pass


class MockGuardian:
    """Mock Guardian implementation for testing"""

    def __init__(self):
        self.enabled = True
        self.mode = GuardianMode.DEVELOPMENT

    async def validate_request_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Mock async request validation"""
        return {
            "approved": True,
            "reason": "Mock Guardian approval",
            "confidence": 0.95,
            "timestamp": asyncio.get_event_loop().time(),
            "mode": self.mode.value
        }

    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Mock synchronous action validation"""
        return {
            "allowed": True,
            "reason": "Mock Guardian validation",
            "confidence": 0.95,
            "mode": self.mode.value
        }


class ProductionGuardian:
    """Production Guardian with comprehensive ethical and security validation"""

    def __init__(self):
        self.enabled = True
        self.mode = GuardianMode.PRODUCTION
        self.policy_cache: Dict[str, Any] = {}
        self.violation_history: List[Dict] = []
        self.max_violations = 10  # Before lockdown
        self.lockdown_duration = timedelta(minutes=15)
        self.lockdown_until: Optional[datetime] = None

        # Load policies
        self._load_policies()

    def _load_policies(self):
        """Load Guardian policies for production validation"""
        self.policies = {
            "data_access": {
                "pii_protection": True,
                "consent_required": True,
                "audit_required": True,
                "encryption_required": True
            },
            "ai_ethics": {
                "transparency_required": True,
                "bias_detection": True,
                "explainability_required": True,
                "human_oversight": True
            },
            "security": {
                "authentication_required": True,
                "authorization_levels": ["T1", "T2", "T3", "T4", "T5"],
                "rate_limiting": True,
                "anomaly_detection": True
            },
            "compliance": {
                "gdpr": True,
                "ccpa": True,
                "sox": True,
                "hipaa": False  # Not healthcare focused
            }
        }

    def _check_lockdown(self) -> bool:
        """Check if Guardian is in lockdown mode"""
        if self.lockdown_until:
            if datetime.now(timezone.utc) < self.lockdown_until:
                return True
            else:
                self.lockdown_until = None
                self.violation_history.clear()
        return False

    def _record_violation(self, violation: Dict[str, Any]):
        """Record a policy violation"""
        violation["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.violation_history.append(violation)

        # Check for lockdown trigger
        if len(self.violation_history) >= self.max_violations:
            self.lockdown_until = datetime.now(timezone.utc) + self.lockdown_duration
            logger.critical(f"Guardian entering lockdown mode until {self.lockdown_until}")

    async def validate_request_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Production async request validation with comprehensive checks"""

        # Check lockdown
        if self._check_lockdown():
            return {
                "approved": False,
                "reason": "Guardian in lockdown mode due to policy violations",
                "confidence": 1.0,
                "timestamp": time.time(),
                "mode": self.mode.value,
                "lockdown_until": self.lockdown_until.isoformat()
            }

        validation_results = []

        # 1. Check data access policies
        if request.get("data_access"):
            data_result = self._validate_data_access(request["data_access"])
            validation_results.append(data_result)

        # 2. Check AI ethics compliance
        if request.get("ai_operation"):
            ethics_result = self._validate_ai_ethics(request["ai_operation"])
            validation_results.append(ethics_result)

        # 3. Check security requirements
        if request.get("auth_context"):
            security_result = self._validate_security(request["auth_context"])
            validation_results.append(security_result)

        # 4. Check compliance requirements
        if request.get("compliance_context"):
            compliance_result = self._validate_compliance(request["compliance_context"])
            validation_results.append(compliance_result)

        # Calculate overall approval
        if not validation_results:
            # No specific validations required, approve with caution
            return {
                "approved": True,
                "reason": "No policy violations detected",
                "confidence": 0.7,
                "timestamp": time.time(),
                "mode": self.mode.value,
                "warning": "Request lacks validation context"
            }

        failed_checks = [r for r in validation_results if not r["passed"]]
        if failed_checks:
            violation = {
                "request": request,
                "failures": failed_checks
            }
            self._record_violation(violation)

            return {
                "approved": False,
                "reason": f"Policy violations: {[f['reason'] for f in failed_checks]}",
                "confidence": 1.0,
                "timestamp": time.time(),
                "mode": self.mode.value,
                "violations": failed_checks
            }

        # All checks passed
        confidence = sum(r["confidence"] for r in validation_results) / len(validation_results)
        return {
            "approved": True,
            "reason": "All Guardian policies validated",
            "confidence": confidence,
            "timestamp": time.time(),
            "mode": self.mode.value,
            "validations": len(validation_results)
        }

    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Production synchronous action validation"""

        # Check lockdown
        if self._check_lockdown():
            return {
                "allowed": False,
                "reason": "Guardian in lockdown mode",
                "confidence": 1.0,
                "mode": self.mode.value
            }

        # Quick validation for synchronous calls
        if action.get("type") == "data_read" and not action.get("consent"):
            return {
                "allowed": False,
                "reason": "Data access requires consent",
                "confidence": 1.0,
                "mode": self.mode.value
            }

        if action.get("type") == "ai_decision" and not action.get("explainable"):
            return {
                "allowed": False,
                "reason": "AI decisions must be explainable",
                "confidence": 1.0,
                "mode": self.mode.value
            }

        return {
            "allowed": True,
            "reason": "Action validated",
            "confidence": 0.9,
            "mode": self.mode.value
        }

    def _validate_data_access(self, data_context: Dict) -> Dict:
        """Validate data access against policies"""
        if data_context.get("contains_pii") and not data_context.get("consent_id"):
            return {
                "passed": False,
                "reason": "PII access requires consent",
                "confidence": 1.0
            }
        if not data_context.get("encrypted"):
            return {
                "passed": False,
                "reason": "Data must be encrypted",
                "confidence": 1.0
            }
        return {
            "passed": True,
            "reason": "Data access validated",
            "confidence": 0.95
        }

    def _validate_ai_ethics(self, ai_context: Dict) -> Dict:
        """Validate AI operation against ethical guidelines"""
        if not ai_context.get("explainable"):
            return {
                "passed": False,
                "reason": "AI operation must be explainable",
                "confidence": 1.0
            }
        if ai_context.get("bias_score", 0) > 0.2:
            return {
                "passed": False,
                "reason": f"Bias score {ai_context.get('bias_score')} exceeds threshold",
                "confidence": 0.95
            }
        return {
            "passed": True,
            "reason": "AI ethics validated",
            "confidence": 0.9
        }

    def _validate_security(self, auth_context: Dict) -> Dict:
        """Validate security requirements"""
        if not auth_context.get("authenticated"):
            return {
                "passed": False,
                "reason": "Authentication required",
                "confidence": 1.0
            }
        tier = auth_context.get("tier_level", "T1")
        if tier not in self.policies["security"]["authorization_levels"]:
            return {
                "passed": False,
                "reason": f"Invalid authorization tier: {tier}",
                "confidence": 1.0
            }
        return {
            "passed": True,
            "reason": "Security validated",
            "confidence": 0.95
        }

    def _validate_compliance(self, compliance_context: Dict) -> Dict:
        """Validate compliance requirements"""
        for framework, required in self.policies["compliance"].items():
            if required and not compliance_context.get(framework):
                return {
                    "passed": False,
                    "reason": f"{framework.upper()} compliance required",
                    "confidence": 1.0
                }
        return {
            "passed": True,
            "reason": "Compliance validated",
            "confidence": 0.9
        }


# Global guardian instance
_global_guardian: Optional[Union[MockGuardian, ProductionGuardian]] = None


def get_guardian() -> Union[MockGuardian, ProductionGuardian]:
    """Get global Guardian instance based on environment"""
    global _global_guardian

    if _global_guardian is None:
        # Determine mode from environment
        guardian_mode = os.environ.get("GUARDIAN_MODE", "development").lower()

        if guardian_mode == "production":
            _global_guardian = ProductionGuardian()
            logger.warning("🔒 Initialized ProductionGuardian - Full validation enabled")
        elif guardian_mode == "staging":
            _global_guardian = MockGuardian()
            _global_guardian.mode = GuardianMode.STAGING
            logger.info("🔧 Initialized MockGuardian in STAGING mode")
        else:
            _global_guardian = MockGuardian()
            logger.info("🧪 Initialized MockGuardian in DEVELOPMENT mode")

    return _global_guardian


def get_guardian_status() -> Dict[str, Any]:
    """Get current Guardian status for health checks"""
    guardian = get_guardian()

    status = {
        "mode": guardian.mode.value,
        "enabled": guardian.enabled,
        "implementation": guardian.__class__.__name__,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if isinstance(guardian, ProductionGuardian):
        status.update({
            "violations": len(guardian.violation_history),
            "lockdown": guardian._check_lockdown(),
            "lockdown_until": guardian.lockdown_until.isoformat() if guardian.lockdown_until else None,
            "policies_loaded": len(guardian.policies)
        })

    return status


# Convenience functions for backward compatibility
async def validate_request_async(request: Dict[str, Any]) -> Dict[str, Any]:
    """Validate request with global Guardian"""
    guardian = get_guardian()
    return await guardian.validate_request_async(request)


def validate_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """Validate action with global Guardian"""
    guardian = get_guardian()
    return guardian.validate_action(action)
