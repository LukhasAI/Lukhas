#!/usr/bin/env python3
"""
Matrix Authorization Gateway Middleware

Gateway middleware that bridges existing ΛiD authentication with Matrix Tracks
authorization decisions. Verifies macaroons, calls OPA for policy decisions,
and emits standardized telemetry spans.

Integrates with existing LUKHAS authentication flows while enforcing Matrix
contract-declared identity requirements.
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Prometheus metrics
from prometheus_client import Counter, Gauge, Histogram

# Import our tools
from tier_macaroon_issuer import TierMacaroonVerifier

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

# Metrics
authz_decisions_total = Counter(
    'lukhas_authz_decisions_total',
    'Total authorization decisions',
    ['module', 'tier', 'decision', 'reason']
)

authz_latency_seconds = Histogram(
    'lukhas_authz_latency_seconds',
    'Authorization decision latency',
    ['module', 'tier'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

authz_active_sessions = Gauge(
    'lukhas_authz_active_sessions',
    'Active authorized sessions',
    ['module', 'tier']
)


@dataclass
class AuthzRequest:
    """Authorization request context."""
    subject: str
    tier: str
    tier_num: int
    scopes: List[str]
    module: str
    action: str
    capability_token: str
    mfa_verified: bool = False
    webauthn_verified: bool = False
    device_id: Optional[str] = None
    region: Optional[str] = None


@dataclass
class AuthzDecision:
    """Authorization decision result."""
    allowed: bool
    reason: str
    policy_sha: Optional[str] = None
    contract_sha: Optional[str] = None
    decision_time_ms: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class MatrixAuthzMiddleware:
    """Matrix Tracks authorization middleware."""

    def __init__(self, shadow_mode: bool = False, opa_endpoint: str = "http://localhost:8181"):
        """Initialize middleware.

        Args:
            shadow_mode: If True, log decisions but don't enforce them
            opa_endpoint: OPA server endpoint
        """
        self.shadow_mode = shadow_mode
        self.opa_endpoint = opa_endpoint
        self.verifier = TierMacaroonVerifier()
        self.contracts_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(f"Matrix AuthZ Middleware initialized (shadow_mode={shadow_mode})")

    def load_contract(self, module: str) -> Dict[str, Any]:
        """Load Matrix contract for module (with caching)."""
        if module in self.contracts_cache:
            return self.contracts_cache[module]

        # Try multiple contract locations
        contract_paths = [
            Path(f"{module}/matrix_{module}.json"),
            Path(f"matrix_{module}.json"),
            Path("memory/matrix_memoria.json") if module == "memoria" else None
        ]

        for path in contract_paths:
            if path and path.exists():
                with open(path) as f:
                    contract = json.load(f)
                    self.contracts_cache[module] = contract
                    return contract

        raise FileNotFoundError(f"No contract found for module: {module}")

    def calculate_contract_sha(self, contract: Dict[str, Any]) -> str:
        """Calculate contract SHA256 for telemetry."""
        import hashlib
        contract_json = json.dumps(contract, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(contract_json.encode()).hexdigest()[:16]

    async def authorize_request(self, request: AuthzRequest) -> AuthzDecision:
        """Main authorization decision logic."""
        start_time = time.time()

        with tracer.start_as_current_span("authz.check") as span:
            try:
                # Load contract
                contract = self.load_contract(request.module)
                contract_sha = self.calculate_contract_sha(contract)

                # Verify macaroon
                capability_claims = self.verifier.verify_capability(request.capability_token)
                if not capability_claims.get("valid", False):
                    decision = AuthzDecision(
                        allowed=False,
                        reason=f"Invalid capability token: {capability_claims.get('error', 'unknown')}",
                        contract_sha=contract_sha
                    )
                    return await self._finalize_decision(request, decision, span, start_time)

                # Build OPA input
                opa_input = self._build_opa_input(request, contract, capability_claims)

                # Call OPA for decision
                opa_result = await self._query_opa(opa_input)

                # Create decision
                decision = AuthzDecision(
                    allowed=opa_result.get("allow", False),
                    reason=opa_result.get("reason", "Policy evaluation"),
                    policy_sha=opa_result.get("policy_sha"),
                    contract_sha=contract_sha,
                    metadata=opa_result.get("decision_metadata", {})
                )

                return await self._finalize_decision(request, decision, span, start_time)

            except Exception as e:
                logger.exception("Authorization error")
                decision = AuthzDecision(
                    allowed=False,
                    reason=f"Authorization error: {e!s}"
                )
                return await self._finalize_decision(request, decision, span, start_time)

    def _build_opa_input(
        self,
        request: AuthzRequest,
        contract: Dict[str, Any],
        capability_claims: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build OPA input from request and contract."""
        return {
            "subject": request.subject,
            "tier": request.tier,
            "tier_num": request.tier_num,
            "scopes": request.scopes,
            "module": request.module,
            "action": request.action,
            "contract": contract,
            "token": capability_claims.get("token", {}),
            "env": {
                "mfa": request.mfa_verified,
                "webauthn_verified": request.webauthn_verified,
                "device_id": request.device_id,
                "region": request.region,
                "ip": None,  # Could be added from request context
                "time": int(time.time())
            }
        }

    async def _query_opa(self, opa_input: Dict[str, Any]) -> Dict[str, Any]:
        """Query OPA for authorization decision."""
        try:
            # In production, this would make HTTP call to OPA server
            # For now, simulate with local OPA evaluation
            result = await self._simulate_opa_decision(opa_input)
            return result

        except Exception as e:
            logger.error(f"OPA query failed: {e}")
            return {
                "allow": False,
                "reason": f"Policy evaluation failed: {e!s}"
            }

    async def _simulate_opa_decision(self, opa_input: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate OPA decision (replace with real OPA call in production)."""
        # This would call: opa eval -d policies/matrix -I opa_input.json "data.matrix.authz.allow"

        try:
            # Write input to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({"input": opa_input}, f)
                input_file = f.name

            # Try to call OPA if available
            try:
                result = subprocess.run([
                    "opa", "eval",
                    "-d", "policies/matrix",
                    "-I", input_file,
                    "data.matrix.authz"
                ], capture_output=True, text=True, timeout=1.0)

                if result.returncode == 0:
                    opa_output = json.loads(result.stdout)
                    authz_result = opa_output.get("result", [{}])[0].get("expressions", [{}])[0].get("value", {})

                    return {
                        "allow": authz_result.get("allow", False),
                        "reason": "OPA policy evaluation",
                        "policy_sha": "opa_live",
                        "decision_metadata": authz_result.get("decision_metadata", {})
                    }

            except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
                pass  # Fall back to simulation

            finally:
                # Clean up temp file
                try:
                    Path(input_file).unlink()
                except Exception as e:
                    logger.debug(f"Expected optional failure: {e}")
                    pass

            # Fallback simulation when OPA not available
            return self._fallback_policy_simulation(opa_input)

        except Exception as e:
            logger.error(f"OPA simulation error: {e}")
            return {
                "allow": False,
                "reason": f"Policy simulation failed: {e!s}"
            }

    def _fallback_policy_simulation(self, opa_input: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback policy simulation when OPA unavailable."""
        contract = opa_input.get("contract", {})
        identity = contract.get("identity", {})

        # Basic checks
        if not identity.get("requires_auth", True):
            return {"allow": True, "reason": "No authentication required"}

        # Check tier requirements
        required_tiers = identity.get("required_tiers", [])
        required_tiers_numeric = identity.get("required_tiers_numeric", [])
        user_tier = opa_input.get("tier")
        user_tier_num = opa_input.get("tier_num", 0)

        tier_allowed = False
        if not required_tiers and not required_tiers_numeric:
            tier_allowed = True  # No tier requirement
        elif (required_tiers and user_tier in required_tiers) or (required_tiers_numeric and user_tier_num in required_tiers_numeric):
            tier_allowed = True

        if not tier_allowed:
            return {
                "allow": False,
                "reason": f"Tier {user_tier} not authorized (required: {required_tiers or required_tiers_numeric})"
            }

        # Check scopes
        required_scopes = set(identity.get("scopes", []))
        user_scopes = set(opa_input.get("scopes", []))

        if required_scopes and not required_scopes.issubset(user_scopes):
            missing = required_scopes - user_scopes
            return {
                "allow": False,
                "reason": f"Missing required scopes: {', '.join(missing)}"
            }

        # Check step-up requirements
        api_policies = {p["fn"]: p for p in identity.get("api_policies", [])}
        action = opa_input.get("action", "")

        if action in api_policies:
            policy = api_policies[action]
            if policy.get("requires_step_up", False):
                if not opa_input.get("env", {}).get("mfa", False):
                    return {
                        "allow": False,
                        "reason": f"Step-up authentication required for {action}"
                    }

        # Check token expiration and audience
        token = opa_input.get("token", {})
        token_exp = token.get("exp", 0)
        token_aud = token.get("aud", "")
        current_time = opa_input.get("env", {}).get("time", int(time.time()))

        if token_exp > 0 and current_time >= token_exp:
            return {
                "allow": False,
                "reason": "Token expired"
            }

        # Check audience
        if token_aud and token_aud != "lukhas-matrix":
            return {
                "allow": False,
                "reason": "Wrong audience in token"
            }

        # Subject validation - check exact match first, then patterns
        accepted_subjects = identity.get("accepted_subjects", [])
        if accepted_subjects:  # If subjects are specified, validate them
            subject = opa_input.get("subject", "")
            subject_allowed = False

            # Check exact match
            if subject in accepted_subjects:
                subject_allowed = True
            else:
                # Check wildcard patterns
                for pattern in accepted_subjects:
                    if pattern.endswith("*"):
                        prefix = pattern[:-1]
                        if subject.startswith(prefix):
                            subject_allowed = True
                            break

            if not subject_allowed:
                return {
                    "allow": False,
                    "reason": "Unknown service account"
                }

        return {
            "allow": True,
            "reason": "Policy checks passed",
            "decision_metadata": {
                "tier_numeric": user_tier_num,
                "policy_version": "fallback_v1"
            }
        }

    async def _finalize_decision(
        self,
        request: AuthzRequest,
        decision: AuthzDecision,
        span: trace.Span,
        start_time: float
    ) -> AuthzDecision:
        """Finalize authorization decision with telemetry and metrics."""

        decision.decision_time_ms = (time.time() - start_time) * 1000

        # Update span attributes
        span.set_attributes({
            "subject": request.subject,
            "tier": request.tier,
            "tier_num": request.tier_num,
            "scopes": ",".join(request.scopes),
            "module": request.module,
            "action": request.action,
            "decision": "allow" if decision.allowed else "deny",
            "reason": decision.reason,
            "policy_sha": decision.policy_sha or "unknown",
            "contract_sha": decision.contract_sha or "unknown",
            "capability_id": request.capability_token[:16] + "...",
            "mfa_used": request.mfa_verified,
            "region": request.region or "unknown",
            "decision_time_ms": decision.decision_time_ms
        })

        # Set span status
        if decision.allowed:
            span.set_status(Status(StatusCode.OK))
        else:
            span.set_status(Status(StatusCode.ERROR, decision.reason))

        # Update metrics
        authz_decisions_total.labels(
            module=request.module,
            tier=request.tier,
            decision="allow" if decision.allowed else "deny",
            reason=decision.reason[:50]  # Truncate for cardinality
        ).inc()

        authz_latency_seconds.labels(
            module=request.module,
            tier=request.tier
        ).observe(decision.decision_time_ms / 1000)

        # Update active sessions gauge
        if decision.allowed:
            authz_active_sessions.labels(
                module=request.module,
                tier=request.tier
            ).inc()

        # Log decision
        if decision.allowed:
            logger.info(f"AuthZ ALLOW: {request.subject} -> {request.module}.{request.action} "
                       f"({decision.decision_time_ms:.1f}ms)")
        else:
            logger.warning(f"AuthZ DENY: {request.subject} -> {request.module}.{request.action} "
                          f"- {decision.reason} ({decision.decision_time_ms:.1f}ms)")

        return decision

    async def middleware_handler(
        self,
        capability_token: str,
        module: str,
        action: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Main middleware entry point for HTTP handlers."""

        # Verify and extract capability claims
        capability_claims = self.verifier.verify_capability(capability_token)
        if not capability_claims.get("valid", False):
            return False, f"Invalid capability token: {capability_claims.get('error', 'unknown')}"

        # Build authorization request
        request = AuthzRequest(
            subject=capability_claims["subject"],
            tier=capability_claims["tier"],
            tier_num=capability_claims["tier_num"],
            scopes=capability_claims["scopes"],
            module=module,
            action=action,
            capability_token=capability_token,
            mfa_verified=capability_claims["env"]["mfa"],
            webauthn_verified=capability_claims["env"]["webauthn_verified"],
            device_id=capability_claims["env"]["device_id"],
            region=capability_claims["env"]["region"]
        )

        # Make authorization decision
        decision = await self.authorize_request(request)

        if self.shadow_mode:
            # In shadow mode, always allow but log the decision
            logger.info(f"SHADOW MODE: Would {'ALLOW' if decision.allowed else 'DENY'} - {decision.reason}")
            return True, f"Shadow mode: {decision.reason}"
        else:
            return decision.allowed, decision.reason


# Example usage functions
async def example_api_handler():
    """Example of how to integrate middleware with API handlers."""
    middleware = MatrixAuthzMiddleware(shadow_mode=True)  # Start in shadow mode

    # Simulate API request with capability token
    capability_token = "eyJ2ZXJzaW9uIjoyLCJsb2NhdGlvbiI6Imx1a2hhcy1tYXRyaXgtYXV0aHoiLCJpZGVudGlmaWVyIjoibHVraGFzOnVzZXI6Z29uem86dHJ1c3RlZDoxNzU4ODkyMjYxIiwiY2F2ZWF0cyI6WyJzdWIgPSBsdWtoYXM6dXNlcjpnb256byIsInRpZXIgPSB0cnVzdGVkIiwidGllcl9udW0gPSAzIiwic2NvcGVzID0gbWVtb3JpYS5yZWFkLG1lbW9yaWEuZm9sZCIsImF1ZCA9IGx1a2hhcy1tYXRyaXgiLCJleHAgPSAxNzU4ODk0MDYxIiwiaWF0ID0gMTc1ODg5MjI2MSIsIm1mYSA9IEZhbHNlIiwid2ViYXV0aG5fdmVyaWZpZWQgPSBUcnVlIl0sInNpZ25hdHVyZSI6ImVhYjUzNGM2YjU0ZTcxNGU3ZjE4MzNjMGIzMDZhZTkwZDI5YjA4NTUxMTE2NWQ2MWU4YTBkMGY2NGM3MTA5NGEifQ=="

    # Check authorization for memory recall
    allowed, reason = await middleware.middleware_handler(
        capability_token=capability_token,
        module="memoria",
        action="recall"
    )

    if allowed:
        print(f"✅ Memory recall authorized: {reason}")
        # Proceed with API logic
    else:
        print(f"❌ Memory recall denied: {reason}")
        # Return 403 Forbidden


def main():
    """CLI for testing middleware."""
    import argparse

    parser = argparse.ArgumentParser(description="Matrix Authorization Middleware")
    parser.add_argument("--shadow", action="store_true", help="Run in shadow mode")
    parser.add_argument("--test", action="store_true", help="Run test scenario")

    args = parser.parse_args()

    if args.test:
        asyncio.run(example_api_handler())
    else:
        print("Matrix Authorization Middleware")
        print(f"Shadow mode: {args.shadow}")


if __name__ == "__main__":
    main()
