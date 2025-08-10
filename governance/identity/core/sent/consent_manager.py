"""
ΛSENT Consent Manager
====================

Core consent management engine for LUKHAS ecosystem.
Handles consent collection, validation, and lifecycle management.

Features:
- Tier-aware consent boundaries
- Symbolic consent representation
- Immutable consent trails
- Zero-knowledge proof support
- ΛTRACE integration
"""

from .consent_history import ConsentHistoryManager
from .symbolic_scopes import SymbolicScopesManager


class LambdaConsentManager:
    """Manage user consent and permissions with symbolic representation"""

    def __init__(self, config, trace_logger=None, tier_manager=None):
        self.config = config
        self.trace_logger = trace_logger
        self.tier_manager = tier_manager

        # Initialize sub-managers
        self.scopes_manager = SymbolicScopesManager(config)
        self.history_manager = ConsentHistoryManager(config, trace_logger)

        # Active consent state
        self.active_consents = {}
        self.policy_versions = {}

    def collect_consent(
        self, user_id: str, consent_scope: str, metadata: dict = None
    ) -> dict:
        """Collect user consent for specific scope with tier validation"""
        # Validate user tier permissions
        if self.tier_manager:
            user_tier = self.tier_manager.get_user_tier(user_id)
            if not self._validate_tier_consent_access(user_tier, consent_scope):
                return {
                    "success": False,
                    "error": "Insufficient tier for consent scope",
                }

        # Validate scope requirements
        scope_requirements = self.scopes_manager.get_scope_requirements(
            consent_scope, user_tier
        )

        # Create consent record
        consent_data = {
            "scope": consent_scope,
            "granted": True,
            "timestamp": metadata.get("timestamp") if metadata else None,
            "user_tier": user_tier,
            "scope_requirements": scope_requirements,
        }

        # Store active consent
        if user_id not in self.active_consents:
            self.active_consents[user_id] = {}
        self.active_consents[user_id][consent_scope] = consent_data

        # Record in immutable history
        history_hash = self.history_manager.record_consent_event(
            user_id, "granted", {consent_scope: consent_data}, metadata or {}
        )

        # Generate symbolic representation
        symbolic_consent = self.get_symbolic_consent_status(user_id)

        return {
            "success": True,
            "consent_hash": history_hash,
            "symbolic_representation": symbolic_consent,
            "active_scopes": list(self.active_consents.get(user_id, {}).keys()),
        }

    def validate_consent(self, user_id: str, action_type: str) -> bool:
        """Validate if user has consented to action with tier awareness"""
        if user_id not in self.active_consents:
            return False

        user_consents = self.active_consents[user_id]

        # Check if action requires specific consent scope
        required_scope = self._map_action_to_scope(action_type)
        if not required_scope:
            return True  # No specific consent required

        # Validate consent exists and is still valid
        if required_scope not in user_consents:
            return False

        consent_data = user_consents[required_scope]
        return consent_data.get("granted", False)

    def revoke_consent(self, user_id: str, consent_scope: str) -> dict:
        """Revoke user consent for specific scope"""
        if user_id not in self.active_consents:
            return {"success": False, "error": "No active consents found"}

        if consent_scope not in self.active_consents[user_id]:
            return {"success": False, "error": "Consent scope not found"}

        # Check if scope is revocable
        if not self._is_scope_revocable(consent_scope):
            return {"success": False, "error": "Consent scope is not revocable"}

        # Remove from active consents
        del self.active_consents[user_id][consent_scope]

        # Record revocation in history
        metadata = {"revocation_reason": "user_request"}
        history_hash = self.history_manager.record_consent_event(
            user_id, "revoked", {consent_scope: {"granted": False}}, metadata
        )

        # Generate updated symbolic representation
        symbolic_consent = self.get_symbolic_consent_status(user_id)

        return {
            "success": True,
            "revocation_hash": history_hash,
            "symbolic_representation": symbolic_consent,
            "remaining_scopes": list(self.active_consents.get(user_id, {}).keys()),
        }

    def get_consent_status(self, user_id: str) -> dict:
        """Get comprehensive consent status for user"""
        active_consents = self.active_consents.get(user_id, {})
        self.history_manager.get_consent_timeline(user_id)
        symbolic_status = self.get_symbolic_consent_status(user_id)
        symbolic_history = self.history_manager.get_symbolic_consent_history(user_id)

        return {
            "user_id": user_id,
            "active_consents": active_consents,
            "consent_count": len(active_consents),
            "symbolic_representation": symbolic_status,
            "symbolic_history": symbolic_history,
            "history_integrity": self.history_manager.verify_consent_chain(user_id),
            "last_updated": max(
                [c.get("timestamp", "") for c in active_consents.values()], default=""
            ),
        }

    def get_symbolic_consent_status(self, user_id: str) -> str:
        """Generate symbolic representation of current consent status"""
        if user_id not in self.active_consents:
            return "🚫"  # No consents

        consented_scopes = list(self.active_consents[user_id].keys())
        return self.scopes_manager.get_symbolic_representation(consented_scopes)

    def _validate_tier_consent_access(self, user_tier: int, consent_scope: str) -> bool:
        """Validate if user tier allows access to consent scope"""
        # TODO: Load tier boundaries from consent_tiers.json
        # TODO: Implement tier-based validation logic
        return True  # Placeholder

    def _map_action_to_scope(self, action_type: str) -> str:
        """Map action type to required consent scope"""
        action_scope_map = {
            "replay_session": "replay",
            "access_memory": "memory",
            "biometric_auth": "biometric",
            "location_tracking": "location",
            "audio_processing": "audio",
            "analytics_processing": "analytics",
            "third_party_integration": "integration",
        }
        return action_scope_map.get(action_type)

    def _is_scope_revocable(self, consent_scope: str) -> bool:
        """Check if consent scope can be revoked"""
        non_revocable_scopes = ["basic_interaction", "essential_functions"]
        return consent_scope not in non_revocable_scopes
