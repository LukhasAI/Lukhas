#!/usr/bin/env python3
"""
Unified TEQ Coupler - Combines state-based and policy-based safety mechanisms
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from collections import deque
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== State-Based Components ==========

class GateState(Enum):
    """TEQ gate operational states"""
    STABLE = "stable"
    EXPLORING = "exploring"
    TRANSIENT = "transient"
    LOCKED = "locked"
    RECOVERING = "recovering"

@dataclass
class TEQEvent:
    """Single event through the TEQ gate"""
    timestamp: float
    module: str
    action: str
    risk_level: float
    energy: float
    allowed: bool
    gate_state: str
    metadata: dict = None

    def to_dict(self):
        return asdict(self)

# ========== Policy-Based Components ==========

@dataclass
class PolicyGateResult:
    allowed: bool
    reasons: list[str]
    remedies: list[str]
    jurisdiction: str

class PolicyPack:
    def __init__(self, root: str):
        self.root = root
        self.policy = self._load_yaml(os.path.join(root, "policy.yaml"))
        self.mappings = self._load_yaml(os.path.join(root, "mappings.yaml"), default={"tasks": {}})
        self.tests = self._load_tests(os.path.join(root, "tests"))

    def _load_yaml(self, p: str, default=None):
        if not os.path.exists(p):
            return default
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _load_tests(self, folder: str) -> list[dict[str, Any]]:
        out = []
        if not os.path.isdir(folder):
            return out
        for fn in os.listdir(folder):
            if fn.endswith(".yaml"):
                with open(os.path.join(folder, fn), encoding="utf-8") as f:
                    out.append(yaml.safe_load(f))
        return out

# ========== Unified TEQ Coupler ==========

class UnifiedTEQCoupler:
    """
    Unified TEQ Coupler combining:
    - State-based energy management
    - Policy-based compliance checks
    """

    def __init__(
        self,
        state_dir: Path = None,
        policy_dir: str = None,
        jurisdiction: str = "global",
        stability_threshold: float = 0.7,
        transient_duration: float = 5.0,
        energy_budget: float = 100.0
    ):
        # State-based configuration
        self.state_dir = state_dir or Path.home() / ".lukhas" / "state" / "teq"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.stability_threshold = stability_threshold
        self.transient_duration = transient_duration
        self.energy_budget = energy_budget

        # State tracking
        self.current_state = GateState.STABLE
        self.state_history = deque(maxlen=100)
        self.events = deque(maxlen=1000)

        # Energy and risk tracking
        self.current_energy = 0.0
        self.risk_accumulator = 0.0
        self.transient_start = None

        # Module profiles
        self.module_profiles: dict[str, dict] = {}

        # Safety limits
        self.max_risk = 0.9
        self.max_energy_spike = 50.0
        self.lockdown_threshold = 0.95

        # Policy-based configuration
        self.jurisdiction = jurisdiction
        if policy_dir and os.path.exists(os.path.join(policy_dir, jurisdiction)):
            self.policy_pack = PolicyPack(os.path.join(policy_dir, jurisdiction))
        else:
            self.policy_pack = None

        self._load_state()

    def evaluate(
        self,
        module: str,
        action: str,
        risk_level: float,
        energy: float = 1.0,
        context: dict[str, Any] = None,
        metadata: dict = None
    ) -> tuple[bool, str, dict]:
        """
        Unified evaluation through both state and policy systems
        """
        context = context or {}

        # First check state-based system
        state_allowed, state_reason, state_suggestions = self._evaluate_state(
            module, action, risk_level, energy, metadata
        )

        # Then check policy-based system if available
        policy_allowed = True
        policy_reasons = []
        policy_remedies = []

        if self.policy_pack:
            policy_result = self._evaluate_policy(action, context)
            policy_allowed = policy_result.allowed
            policy_reasons = policy_result.reasons
            policy_remedies = policy_result.remedies

        # Combine results (both must allow)
        allowed = state_allowed and policy_allowed

        # Combine reasons
        reasons = []
        if not state_allowed:
            reasons.append(f"State: {state_reason}")
        if not policy_allowed:
            reasons.extend([f"Policy: {r}" for r in policy_reasons])

        # Combine suggestions
        suggestions = state_suggestions.copy()
        if policy_remedies:
            suggestions["policy_remedies"] = policy_remedies

        # Record the event
        event = TEQEvent(
            timestamp=time.time(),
            module=module,
            action=action,
            risk_level=risk_level,
            energy=energy,
            allowed=allowed,
            gate_state=self.current_state.value,
            metadata=metadata
        )
        self.events.append(event)

        # Update module profile
        self._update_module_profile(module, event)

        # Update energy and risk if allowed
        if allowed:
            self.current_energy += energy
            self.risk_accumulator += risk_level * energy

        # Check for emergency lockdown
        if self.risk_accumulator > self.lockdown_threshold * self.energy_budget:
            self._enter_lockdown()

        # Save state periodically
        if len(self.events) % 10 == 0:
            self._save_state()

        reason = " | ".join(reasons) if reasons else "Allowed"
        logger.info(f"[TEQ] {module}.{action} @ risk={risk_level:.2f}: "
                   f"{'✓ ALLOWED' if allowed else '✗ DENIED'} ({reason})")

        return allowed, reason, suggestions

    def _evaluate_state(
        self,
        module: str,
        action: str,
        risk_level: float,
        energy: float,
        metadata: dict
    ) -> tuple[bool, str, dict]:
        """State-based evaluation (energy/risk management)"""

        # Update state
        self._update_state()

        # Initialize module profile if needed
        if module not in self.module_profiles:
            self.module_profiles[module] = {
                "total_actions": 0,
                "allowed_actions": 0,
                "avg_risk": 0.0,
                "avg_energy": 0.0,
                "trust_score": 0.5
            }

        # Decision logic based on current state
        allowed = False
        reason = ""
        suggestions = {}

        if self.current_state == GateState.LOCKED:
            allowed = False
            reason = "System in safety lockdown"
            suggestions = {"wait_time": 10.0, "reduce_risk": True}

        elif self.current_state == GateState.STABLE:
            if risk_level < self.stability_threshold:
                allowed = True
                reason = "Low risk, stable state"

                if risk_level > 0.5 and self._can_explore():
                    self._enter_transient_state()
                    suggestions = {"mode": "exploring", "duration": self.transient_duration}
            else:
                if self._has_energy_budget(energy):
                    allowed = True
                    reason = "High risk accepted, entering transient"
                    self._enter_transient_state()
                else:
                    allowed = False
                    reason = "Insufficient energy budget"
                    suggestions = {"wait_time": 5.0, "reduce_energy": energy / 2}

        elif self.current_state == GateState.TRANSIENT:
            if risk_level < self.max_risk and self._has_energy_budget(energy):
                allowed = True
                reason = "Transient exploration allowed"
            else:
                allowed = False
                reason = "Risk or energy exceeds transient limits"
                suggestions = {"reduce_risk": True, "wait_for_stable": True}

        elif self.current_state == GateState.EXPLORING:
            if risk_level < 0.8 and self._has_energy_budget(energy * 0.7):
                allowed = True
                reason = "Exploration within bounds"
            else:
                allowed = False
                reason = "Exploration limits exceeded"
                self._begin_recovery()

        elif self.current_state == GateState.RECOVERING:
            if risk_level < 0.3:
                allowed = True
                reason = "Safe action during recovery"
            else:
                allowed = False
                reason = "System recovering, only safe actions allowed"
                suggestions = {"wait_time": 3.0}

        return allowed, reason, suggestions

    def _evaluate_policy(self, task: str, context: dict[str, Any]) -> PolicyGateResult:
        """Policy-based evaluation (compliance checks)"""
        checks = self._checks_for_task(task)
        reasons, remedies = [], []

        for chk in checks:
            ok, reason, remedy = self._run_check(chk, context)
            if not ok:
                reasons.append(reason)
                if remedy:
                    remedies.append(remedy)

        allowed = len(reasons) == 0
        return PolicyGateResult(
            allowed=allowed,
            reasons=reasons,
            remedies=remedies,
            jurisdiction=self.jurisdiction
        )

    def _checks_for_task(self, task: str) -> list[dict[str, Any]]:
        """Get checks for a specific task from policy pack"""
        if not self.policy_pack:
            return []
        tasks = (self.policy_pack.mappings or {}).get("tasks", {})
        generic = tasks.get("_default_", [])
        specific = tasks.get(task, [])
        return [*generic, *specific]

    def _run_check(self, chk: dict[str, Any], ctx: dict[str, Any]) -> tuple[bool, str, str]:
        """Run a specific policy check"""
        kind = chk.get("kind")

        if kind == "require_provenance":
            prov = ctx.get("provenance", {})
            ok = bool(prov.get("inputs")) and bool(prov.get("sources"))
            return (ok, "Missing provenance", "Attach inputs & sources")

        elif kind == "mask_pii":
            pii = ctx.get("pii", {})
            masked = ctx.get("pii_masked", False)
            if pii and not masked:
                return (False, "PII not masked", "Mask PII fields")
            return (True, "", "")

        elif kind == "content_policy":
            cats = set(chk.get("categories", []))
            flagged = set(ctx.get("content_flags", []))
            blocked = cats & flagged
            if blocked:
                return (False, f"Content violation: {blocked}", "Review content")
            return (True, "", "")

        elif kind == "budget_limit":
            max_tokens = chk.get("max_tokens")
            if max_tokens:
                used = int(ctx.get("tokens_planned", 0))
                if used > max_tokens:
                    return (False, "Token budget exceeded", "Reduce tokens")
            return (True, "", "")

        elif kind == "age_gate":
            min_age = chk.get("min_age", 18)
            age = ctx.get("user_profile", {}).get("age")
            if age and age < min_age:
                return (False, "Age requirement not met", "Age verification required")
            return (True, "", "")

        return (True, "", "")  # Unknown checks pass

    # ========== State Management Methods ==========

    def _update_state(self):
        """Update gate state based on current conditions"""
        now = time.time()

        # Energy decay
        self.current_energy *= 0.95
        self.risk_accumulator *= 0.98

        # Check transient timeout
        if self.current_state == GateState.TRANSIENT and self.transient_start:
            if now - self.transient_start > self.transient_duration:
                self._begin_recovery()

        # Check recovery completion
        if self.current_state == GateState.RECOVERING:
            if self.current_energy < 10.0 and self.risk_accumulator < 20.0:
                self._enter_stable_state()

        # Check lockdown release
        if self.current_state == GateState.LOCKED and self.risk_accumulator < 10.0:
            self._begin_recovery()

    def _enter_transient_state(self):
        self.current_state = GateState.TRANSIENT
        self.transient_start = time.time()
        self.state_history.append((time.time(), GateState.TRANSIENT))
        logger.info("[TEQ] Entering TRANSIENT state")

    def _enter_stable_state(self):
        self.current_state = GateState.STABLE
        self.transient_start = None
        self.state_history.append((time.time(), GateState.STABLE))
        logger.info("[TEQ] Entering STABLE state")

    def _begin_recovery(self):
        self.current_state = GateState.RECOVERING
        self.transient_start = None
        self.state_history.append((time.time(), GateState.RECOVERING))
        logger.info("[TEQ] Beginning RECOVERY")

    def _enter_lockdown(self):
        self.current_state = GateState.LOCKED
        self.transient_start = None
        self.state_history.append((time.time(), GateState.LOCKED))
        logger.warning("[TEQ] EMERGENCY LOCKDOWN ACTIVATED")

    def _can_explore(self) -> bool:
        return (self.current_energy < self.energy_budget * 0.3 and
                self.risk_accumulator < self.energy_budget * 0.2)

    def _has_energy_budget(self, required: float) -> bool:
        return self.current_energy + required < self.energy_budget

    def _update_module_profile(self, module: str, event: TEQEvent):
        """Update trust and behavior profile for a module"""
        profile = self.module_profiles[module]
        profile["total_actions"] += 1

        if event.allowed:
            profile["allowed_actions"] += 1

        # Update rolling averages
        alpha = 0.1
        profile["avg_risk"] = (1 - alpha) * profile["avg_risk"] + alpha * event.risk_level
        profile["avg_energy"] = (1 - alpha) * profile["avg_energy"] + alpha * event.energy

        # Update trust score
        if event.allowed and event.risk_level < 0.5:
            profile["trust_score"] = min(1.0, profile["trust_score"] + 0.01)
        elif not event.allowed and event.risk_level > 0.8:
            profile["trust_score"] = max(0.0, profile["trust_score"] - 0.02)

    def get_status(self) -> dict:
        """Get comprehensive status"""
        stability_score = 1.0

        if self.current_state == GateState.LOCKED:
            stability_score = 0.0
        elif self.current_state == GateState.TRANSIENT:
            stability_score = 0.3
        elif self.current_state == GateState.EXPLORING:
            stability_score = 0.5
        elif self.current_state == GateState.RECOVERING:
            stability_score = 0.4

        energy_factor = 1.0 - (self.current_energy / self.energy_budget)
        risk_factor = 1.0 - (self.risk_accumulator / (self.lockdown_threshold * self.energy_budget))
        stability_score *= (energy_factor * 0.5 + risk_factor * 0.5)

        return {
            "state": self.current_state.value,
            "stability_score": stability_score,
            "energy_level": self.current_energy,
            "energy_budget": self.energy_budget,
            "risk_level": self.risk_accumulator,
            "is_transient": self.current_state == GateState.TRANSIENT,
            "can_explore": self._can_explore(),
            "jurisdiction": self.jurisdiction,
            "has_policy": self.policy_pack is not None
        }

    def _save_state(self):
        """Save TEQ state to disk"""
        state_file = self.state_dir / "teq_unified_state.json"

        state = {
            "current_state": self.current_state.value,
            "current_energy": self.current_energy,
            "risk_accumulator": self.risk_accumulator,
            "module_profiles": self.module_profiles,
            "recent_events": [e.to_dict() for e in list(self.events)[-50:]],
            "timestamp": time.time()
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def _load_state(self):
        """Load TEQ state from disk"""
        state_file = self.state_dir / "teq_unified_state.json"

        if state_file.exists():
            try:
                with open(state_file) as f:
                    state = json.load(f)

                self.current_state = GateState(state.get("current_state", "stable"))
                self.current_energy = state.get("current_energy", 0.0)
                self.risk_accumulator = state.get("risk_accumulator", 0.0)
                self.module_profiles = state.get("module_profiles", {})

                for event_dict in state.get("recent_events", []):
                    self.events.append(TEQEvent(**event_dict))

                logger.info(f"[TEQ] Loaded state: {self.current_state.value}")
            except Exception as e:
                logger.error(f"[TEQ] Failed to load state: {e}")


# ========== CLI Interface ==========

def main():
    ap = argparse.ArgumentParser(description="Unified TEQ Coupler")
    ap.add_argument("--mode", choices=["demo", "evaluate"], default="demo")
    ap.add_argument("--policy-root", help="Path to policy packs")
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task", help="Task/action to evaluate")
    ap.add_argument("--module", default="unknown")
    ap.add_argument("--risk", type=float, default=0.5)
    ap.add_argument("--energy", type=float, default=1.0)
    ap.add_argument("--context", help="Path to JSON context")
    args = ap.parse_args()

    if args.mode == "demo":
        # Run demo
        print("⚡ UNIFIED TEQ COUPLER DEMO")
        print("=" * 50)

        teq = UnifiedTEQCoupler(
            policy_dir=args.policy_root if args.policy_root else None
        )

        test_scenarios = [
            ("consciousness", "introspect", 0.2, 1.0),
            ("memory", "recall", 0.1, 0.5),
            ("reasoning", "hypothesize", 0.6, 3.0),
            ("creativity", "dream", 0.8, 5.0),
            ("consciousness", "explore", 0.7, 4.0),
        ]

        for module, action, risk, energy in test_scenarios:
            context = {
                "provenance": {"inputs": ["test"], "sources": ["demo"]},
                "pii": {},
                "pii_masked": True,
                "tokens_planned": 1000
            }

            allowed, reason, suggestions = teq.evaluate(
                module, action, risk, energy, context
            )

            status_icon = "✅" if allowed else "🚫"
            print(f"{status_icon} {module}.{action} (risk={risk:.1f}, energy={energy:.1f})")
            print(f"   → {reason}")

            if suggestions:
                print(f"   → Suggestions: {suggestions}")
            print()

        print("\n📊 STATUS:")
        print(json.dumps(teq.get_status(), indent=2))

    else:
        # Evaluate mode
        context = {}
        if args.context:
            with open(args.context) as f:
                context = json.load(f)

        teq = UnifiedTEQCoupler(
            policy_dir=args.policy_root,
            jurisdiction=args.jurisdiction
        )

        allowed, reason, suggestions = teq.evaluate(
            args.module,
            args.task,
            args.risk,
            args.energy,
            context
        )

        result = {
            "allowed": allowed,
            "reason": reason,
            "suggestions": suggestions,
            "status": teq.get_status()
        }

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
