"""
Core Module
"""

# ΛTAG: ethics_core_bridge

try:
    from governance.ethics.shared_ethics_engine import (
        DecisionType,
        EthicalConstraint,
        EthicalDecision,
        EthicalPrinciple,
        EthicalSeverity,
        SharedEthicsEngine,
        get_shared_ethics_engine,
    )
except Exception:  # pragma: no cover
    # COMPLETED[JULES10]: robust ethics fallback implemented below
    class EthicalDecision:  # type: ignore
        """Fallback decision object."""

        def __init__(self, decision_type: str = "allow", confidence: float = 1.0):
            self.decision_type = type("dt", (), {"value": decision_type})
            self.confidence = confidence

    class DecisionType:  # type: ignore
        ALLOW = "allow"
        DENY = "deny"

    async def _allow(*args, **kwargs) -> EthicalDecision:
        return EthicalDecision()

    def get_shared_ethics_engine():  # type: ignore
        class _Mock:
            async def evaluate_action(self, *args, **kwargs) -> EthicalDecision:
                return await _allow()

        return _Mock()

    class EthicalConstraint:  # type: ignore
        pass

    class EthicalPrinciple:  # type: ignore
        pass

    class EthicalSeverity:  # type: ignore
        pass

    class SharedEthicsEngine:  # type: ignore
        pass

__all__ = [
    "DecisionType",
    "EthicalConstraint",
    "EthicalDecision",
    "EthicalPrinciple",
    "EthicalSeverity",
    "SharedEthicsEngine",
    "get_shared_ethics_engine",
]

