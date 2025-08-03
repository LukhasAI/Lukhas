"""

#TAG:governance
#TAG:policy
#TAG:neuroplastic
#TAG:colony


══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - POLICY ENGINE INTEGRATION
║ Integration module for ethics policy engines.
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: integration.py
║ Path: lukhas/[subdirectory]/integration.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Ethics Team | Jules
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Integration module for ethics policy engines.
╚══════════════════════════════════════════════════════════════════════════════════
"""

# Module imports
from core.common import get_logger
from typing import Optional, Dict, Any

# Configure module logger
logger = get_logger(__name__)

# Module constants
MODULE_VERSION = "1.0.0"
MODULE_NAME = "policy engine integration"

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .base import (
    Decision,
    EthicsEvaluation,
    PolicyRegistry,
    RiskLevel
)
from .examples import ThreeLawsPolicy, GPT4Policy, GPT4Config

logger = get_logger(__name__)


@dataclass
class GovernanceDecision:
    """Wrapper to convert existing governance decisions to new format"""
    action: str
    requester: str
    context: Dict[str, Any]
    risk_level: str = "medium"

    def to_policy_decision(self) -> Decision:
        """Convert to policy engine Decision format"""
        # Map risk levels
        risk_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL
        }

        return Decision(
            action=self.action,
            context=self.context,
            requester_id=self.requester,
            urgency=risk_map.get(self.risk_level.lower(), RiskLevel.MEDIUM),
            symbolic_state=self.context.get('symbolic_state'),
            glyphs=self.context.get('glyphs')
        )


class PolicyEngineIntegration:
    """Integration layer for ethics policy engines

    This class provides a bridge between the existing governance engine
    and the new pluggable policy system.
    """

    def __init__(self):
        self.registry = PolicyRegistry()
        self._initialized = False

    def initialize_default_policies(self) -> None:
        """Initialize with default policy configurations"""
        # Register Three Laws as primary policy
        three_laws = ThreeLawsPolicy(strict_mode=True)
        self.registry.register_policy(three_laws, set_as_default=True)

        # Register GPT-4 policy as secondary
        gpt4_config = GPT4Config(
            model="gpt-4",
            temperature=0.3,
            enable_caching=True
        )
        gpt4_policy = GPT4Policy(config=gpt4_config)
        self.registry.register_policy(gpt4_policy)

        self._initialized = True
        logger.info("Initialized default ethics policies")

    def evaluate_governance_decision(self,
                                   action: str,
                                   requester: str,
                                   context: Dict[str, Any],
                                   risk_level: str = "medium") -> Dict[str, Any]:
        """Evaluate a governance decision using policy engines

        This method provides backward compatibility with existing
        governance engine interfaces.

        Args:
            action: The action to evaluate
            requester: Who is requesting the action
            context: Additional context
            risk_level: Risk level assessment

        Returns:
            Dictionary with evaluation results
        """
        if not self._initialized:
            self.initialize_default_policies()

        # Convert to new format
        gov_decision = GovernanceDecision(
            action=action,
            requester=requester,
            context=context,
            risk_level=risk_level
        )

        decision = gov_decision.to_policy_decision()

        # Get evaluations from all active policies
        evaluations = self.registry.evaluate_decision(decision)

        # Get consensus
        consensus = self.registry.get_consensus_evaluation(evaluations)

        # Convert back to legacy format
        return {
            'allowed': consensus.allowed,
            'reasoning': consensus.reasoning,
            'confidence': consensus.confidence,
            'risk_flags': consensus.risk_flags,
            'recommendations': consensus.recommendations,
            'policy_evaluations': [
                {
                    'policy': e.policy_name,
                    'allowed': e.allowed,
                    'confidence': e.confidence
                }
                for e in evaluations
            ]
        }

    def add_custom_policy(self, policy_class, *args, **kwargs) -> None:
        """Add a custom policy to the registry

        Args:
            policy_class: The policy class to instantiate
            *args, **kwargs: Arguments for policy initialization
        """
        policy = policy_class(*args, **kwargs)
        self.registry.register_policy(policy)
        logger.info(f"Added custom policy: {policy.get_policy_name()}")

    def get_policy_metrics(self) -> Dict[str, Any]:
        """Get metrics from all registered policies"""
        return self.registry.get_policy_metrics()

    def shutdown(self) -> None:
        """Cleanup resources"""
        for policy_name in self.registry.get_active_policies():
            self.registry.unregister_policy(policy_name)
        self._initialized = False


# Global instance for easy integration
_global_policy_engine = None


def get_policy_engine() -> PolicyEngineIntegration:
    """Get or create global policy engine instance"""
    global _global_policy_engine
    if _global_policy_engine is None:
        _global_policy_engine = PolicyEngineIntegration()
    return _global_policy_engine


def evaluate_with_policies(action: str,
                          requester: str,
                          context: Dict[str, Any],
                          risk_level: str = "medium") -> Dict[str, Any]:
    """Convenience function for policy evaluation

    This function provides a simple interface for existing code
    to use the new policy engine system.
    """
    engine = get_policy_engine()
    return engine.evaluate_governance_decision(
        action=action,
        requester=requester,
        context=context,
        risk_level=risk_level
    )

"""
═══════════════════════════════════════════════════════════════════════════════
║ 📋 FOOTER - LUKHAS AI
╠══════════════════════════════════════════════════════════════════════════════
║ VALIDATION:
║   - Tests: lukhas/tests/test_integration.py
║   - Coverage: N/A%
║   - Linting: pylint N/A/10
║
║ MONITORING:
║   - Metrics: N/A
║   - Logs: N/A
║   - Alerts: N/A
║
║ COMPLIANCE:
║   - Standards: N/A
║   - Ethics: Refer to LUKHAS Ethics Guidelines
║   - Safety: Refer to LUKHAS Safety Protocols
║
║ REFERENCES:
║   - Docs: docs/ethics/policy engine integration.md
║   - Issues: github.com/lukhas-ai/lukhas/issues?label=policy engine integration
║   - Wiki: N/A
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
║
║ DISCLAIMER:
║   This module is part of the LUKHAS AGI system. Use only as intended
║   within the system architecture. Modifications may affect system
║   stability and require approval from the LUKHAS Architecture Board.
╚═══════════════════════════════════════════════════════════════════════════
"""