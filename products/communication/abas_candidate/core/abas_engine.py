"""ABAS Arbitration Engine

Resolves conflicts and manages policy registration for the Golden Trio.
"""

import logging
from typing import Any

try:
    from ethics.core import get_shared_ethics_engine  # ΛTAG: ethics_bridge
except (ImportError, AttributeError):  # pragma: no cover - fallback when namespace missing
    from candidate.governance.ethics.shared_ethics_engine import get_shared_ethics_engine

try:
    from candidate.core.symbolic_core.symbolic_vocabulary import SymbolicVocabulary, get_symbolic_vocabulary
except ImportError:
    # Fallback for legacy path
    try:
        from symbolic.core import SymbolicVocabulary, get_symbolic_vocabulary
    except ImportError:
        # Mock implementation if symbolic module unavailable
        class MockSymbol:
            def __init__(self, symbol_type: str, data: Any):
                self.symbol_type = symbol_type
                self.data = data
                self.id = f"{symbol_type}_{hash(str(data))}"

            def to_dict(self) -> dict[str, Any]:
                return {"id": self.id, "type": self.symbol_type, "data": self.data}

        class SymbolicVocabulary:
            def create_symbol(self, symbol_type: str, data: Any) -> MockSymbol:
                return MockSymbol(symbol_type, data)

        def get_symbolic_vocabulary() -> SymbolicVocabulary:
            return SymbolicVocabulary()


logger = logging.getLogger(__name__)


class ABASRegistry:
    """Registry for symbolic policies."""

    # ΛTAG: abas, policy_registry

    def __init__(self) -> None:
        self.symbolic: SymbolicVocabulary = get_symbolic_vocabulary()
        self.ethics = get_shared_ethics_engine()
        self.policies: list[dict[str, Any]] = []

    async def register_policy(self, policy: dict[str, Any]) -> None:
        policy_symbol = self.symbolic.create_symbol("policy", policy)
        decision = await self.ethics.evaluate_action(
            {"type": "register_policy"},
            {"policy": policy_symbol.to_dict()},
            "ABAS",
        )
        if decision.decision_type.value == "allow":
            self.policies.append(policy_symbol.to_dict())


class ConflictDetector:
    """Detects conflicts using the orchestrator."""

    # ΛTAG: abas, conflict_detection

    def __init__(self) -> None:
        try:
            from candidate.orchestration.golden_trio import get_trio_orchestrator

            self.orchestrator = get_trio_orchestrator()
        except Exception:
            self.orchestrator = None

    async def detect_conflicts(self, current: dict[str, Any], proposed: dict[str, Any]) -> list[str]:
        # ΛTAG: abas, dependency_analysis
        conflicts: list[str] = []

        orchestrator_context: dict[str, Any] = {}
        if self.orchestrator:
            try:
                orchestrator_context = await self.orchestrator.context_manager.get_full_context()
            except Exception as exc:  # pragma: no cover - orchestrator failures are non-critical
                logger.debug("Golden Trio context unavailable", extra={"error": str(exc)})

        proposed_deps = proposed.get("dependencies", [])
        if proposed_deps:
            system_state = orchestrator_context.get("system_state", {})
            for dep in proposed_deps:
                if not isinstance(dep, dict):
                    continue
                system = dep.get("system")
                requirement = dep.get("requirement")
                if not system or not requirement:
                    continue
                current_state = system_state.get(system.lower(), {}) if isinstance(system_state, dict) else {}
                active_elements = set(current_state.get("active_tasks", [])) | set(current.get("active_tasks", []))
                if requirement not in active_elements:
                    conflicts.append(f"missing:{system}:{requirement}")

        if proposed.get("policy_id") and current.get("policy_id") == proposed["policy_id"]:
            conflicts.append("duplicate_policy")

        if conflicts:
            logger.info("ABAS dependency conflicts detected", extra={"conflicts": conflicts})

        return conflicts


class ResolutionAlgorithm:
    """Resolves conflicts based on ethics."""

    # ΛTAG: abas, conflict_resolution

    def __init__(self) -> None:
        self.ethics = get_shared_ethics_engine()

    async def resolve_conflict(self, conflict: dict[str, Any]) -> dict[str, Any]:
        decision = await self.ethics.evaluate_action(conflict, {}, "ABAS")
        return {"decision": decision.decision_type.value}


class ABASEngine:
    """Main ABAS engine combining registry, detection, and resolution."""

    # ΛTAG: abas, core_engine

    def __init__(self) -> None:
        self.registry = ABASRegistry()
        self.detector = ConflictDetector()
        self.resolution = ResolutionAlgorithm()

    async def arbitrate(self, state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
        conflicts = await self.detector.detect_conflicts(state, action)
        if conflicts:
            return await self.resolution.resolve_conflict({"conflicts": conflicts})
        return {"decision": "allow"}
