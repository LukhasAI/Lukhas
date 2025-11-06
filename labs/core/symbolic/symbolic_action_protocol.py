"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Enhanced Core TypeScript - Integrated from Advanced Systems
Original: symbolic_action_protocol.py
Advanced: symbolic_action_protocol.py
Integration Date: 2025-05-31T07:55:29.965394
"""
from datetime import timezone

"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : symbolic_action_protocol.py                               │
│ 🧾 DESCRIPTION : Defines symbolic-safe action proposals based on dreams,   │
│                 emotion states, and user-configured consent tiers.         │
│ 🧩 TYPE        : Symbolic Governance Logic 🔧 VERSION: v0.1.0               │
│ 🖋️ AUTHOR      : LUKHAS SYSTEMS           📅 UPDATED: 2025-05-05              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - lukhas_core/emotional_resonance.py                                     │
│   - lukhas_data/consent_tiers.json                                         │
│   - utils/symbolic_trace_logger.py                                        │
└────────────────────────────────────────────────────────────────────────────┘
"""


from datetime import datetime

from data_legacy.consent_manager import ConsentTierManager

from utils.trace_logger import log_symbolic_trace


class SymbolicActionProtocol:
    def __init__(self, user_id, consent_level):
        self.user_id = user_id
        self.consent_level = consent_level
        self.tier_config = ConsentTierManager.load(consent_level)

    def evaluate_proposal(self, proposal: dict) -> dict:
        """
        Evaluate a symbolic action suggestion and return the modified version
        with tier-safe execution flags.
        """
        action_type = proposal.get("type")
        symbolic_trigger = proposal.get("trigger")
        est_cost = proposal.get("estimated_cost", 0)

        allowed = self._check_permissions(action_type, est_cost)
        log_symbolic_trace(self.user_id, action_type, symbolic_trigger, allowed)

        proposal["permitted"] = allowed
        proposal["timestamp_evaluated"] = datetime.now(timezone.utc).isoformat()
        return proposal

    def _check_permissions(self, action_type, cost):
        allowed_actions = self.tier_config.get("allowed_actions", [])
        max_cost = self.tier_config.get("max_autonomous_cost", 0)
        emergency_mode = self.tier_config.get("emergency_mode", False)

        return (action_type in allowed_actions and cost <= max_cost) or emergency_mode

    def explain_action(self, proposal: dict) -> str:
        """
            🔍 Introspective Explanation (Altman-style):
            Provide a human-readable explanation of why an action proposal was permitted or denied.

            Inspired by Steve Jobs - this message should feel intimate, emotional,
        and symbolic.

            Returns:
                A poetic but transparent string for the user or interface layer.
        """
        action = proposal.get("type", "unknown action")
        trigger = proposal.get("trigger", "unknown trigger")
        permitted = proposal.get("permitted", False)
        cost = proposal.get("estimated_cost", 0)
        tier = self.consent_level

        # Symbolic pulse: a moment of clarity in the emotional flow of decisions
        log_symbolic_trace(self.user_id, "explain_action", trigger, permitted)

        if permitted:
            return (
                f"🟢 Lukhas recognized a symbolic cue ({trigger}) "
                f"and determined the action '{action}' is allowed within Tier {tier} limits (€{cost})."
            )
        else:
            return (
                f"🔒 Lukhas received a symbolic signal ({trigger}), but '{action}' exceeds Tier {tier} permissions "
                f"or spending limits. The moment was felt - but held safely in silence."
            )
