"""
Identity Manager for WΛLLET
Manages the identity framework for WΛLLET wallet system.

Integrated from existing identity_manager.py implementation.
"""

import json
import logging
import os
import time
import uuid
from collections import defaultdict
from typing import Any, Optional

from .qi_identity_core import LambdaWalletIdentity, QITier
from .symbolic_vault import WalletSymbolicVault

logger = logging.getLogger("WΛLLET.IdentityManager")


class WalletIdentityManager:
    """
    Manages the identity framework for the WΛLLET wallet system.

    This system coordinates wallet identity, transaction memory,
    and secure access to sensitive financial data. It enables the system
    to maintain consistent wallet identities, learn from transaction patterns,
    and adapt while preserving security protocols.
    """

    def __init__(self, identity_file: Optional[str] = None, encryption_level: str = "high"):
        self.logger = logging.getLogger("WalletIdentityManager")

        # Wallet-specific identity attributes
        self.wallet_identity = {
            "id": str(uuid.uuid4()),
            "created_at": time.time(),
            "name": "WΛLLET Identity System",
            "version": "1.0.0",
            "description": "Quantum-secured digital wallet identity management",
            "core_values": [
                "financial_security",
                "user_privacy",
                "transaction_integrity",
                "regulatory_compliance",
                "user_empowerment",
            ],
            "wallet_traits": {
                "security_focus": 0.95,
                "user_friendliness": 0.8,
                "privacy_protection": 0.9,
                "regulatory_compliance": 0.85,
                "innovation_openness": 0.7,
            },
            "supported_currencies": ["ETH", "BTC", "ΛCOIN", "USDC", "DAI"],
            "wallet_features": [
                "multi_signature",
                "cold_storage",
                "defi_integration",
                "nft_support",
                "cross_chain",
            ],
        }

        # Wallet-specific components
        self.active_wallets: dict[str, LambdaWalletIdentity] = {}
        self.wallet_vaults: dict[str, WalletSymbolicVault] = {}

        # Transaction and access patterns
        self.transaction_patterns = defaultdict(list)
        self.access_patterns = defaultdict(dict)

        # Identity evolution tracking
        self.wallet_identity_snapshots = []

        # Load identity if specified
        if identity_file and os.path.exists(identity_file):
            self._load_wallet_identity(identity_file)
        else:
            # Save initial snapshot
            self._take_wallet_identity_snapshot("initialization")

        self.logger.info(f"WΛLLET Identity Manager initialized with ID: {self.wallet_identity['id']}")

    def create_wallet_identity(
        self,
        emoji_seed: str,
        tier: QITier = QITier.USER,
        biometric_data: Optional[bytes] = None,
    ) -> LambdaWalletIdentity:
        """
        Create a new wallet identity with quantum security

        Args:
            emoji_seed: Symbolic seed for identity generation
            tier: Access tier for the wallet
            biometric_data: Optional biometric data for enhanced security

        Returns:
            Created wallet identity
        """
        wallet_identity = LambdaWalletIdentity.generate(emoji_seed=emoji_seed, tier=tier, biometric_data=biometric_data)

        # Store in active wallets
        self.active_wallets[wallet_identity.lambda_id] = wallet_identity

        # Create associated symbolic vault
        vault = WalletSymbolicVault(wallet_identity.lambda_id)
        self.wallet_vaults[wallet_identity.lambda_id] = vault

        # Initialize access patterns
        self.access_patterns[wallet_identity.lambda_id] = {
            "creation_time": time.time(),
            "access_count": 0,
            "last_accessed": None,
            "transaction_count": 0,
            "security_events": [],
        }

        self.logger.info(f"Created wallet identity: {wallet_identity.lambda_id}")

        # Take snapshot of significant change
        self._take_wallet_identity_snapshot(f"wallet_created_{wallet_identity.lambda_id}")

        return wallet_identity

    def process_transaction_experience(
        self,
        lambda_id: str,
        transaction_data: dict[str, Any],
        security_level: str = "high",
    ) -> dict[str, Any]:
        """
        Process a transaction experience and update wallet identity components

        Args:
            lambda_id: Wallet identity ID
            transaction_data: The transaction data
            security_level: Security level for memory storage

        Returns:
            Processed transaction data with identity updates
        """
        if lambda_id not in self.active_wallets:
            return {"error": "Wallet identity not found"}

        self.active_wallets[lambda_id]
        vault = self.wallet_vaults[lambda_id]

        # Record transaction pattern
        transaction_pattern = {
            "timestamp": time.time(),
            "transaction_type": transaction_data.get("type", "unknown"),
            "amount": transaction_data.get("amount", 0),
            "currency": transaction_data.get("currency", "unknown"),
            "security_level": security_level,
        }

        self.transaction_patterns[lambda_id].append(transaction_pattern)

        # Update access patterns
        self.access_patterns[lambda_id]["transaction_count"] += 1
        self.access_patterns[lambda_id]["last_accessed"] = time.time()

        # Determine if this is a significant transaction
        significance = self._assess_transaction_significance(transaction_data)

        if significance > 0.7:
            # Store in encrypted vault
            encrypted_memory = vault.encrypt_wallet_memory(
                {
                    **transaction_data,
                    "significance": significance,
                    "processed_at": time.time(),
                },
                access_layer=2 if security_level == "high" else 1,
            )

            return {
                "transaction_processed": True,
                "significance": significance,
                "encrypted": True,
                "memory_id": encrypted_memory.get("timestamp"),
                "security_level": security_level,
            }

        return {
            "transaction_processed": True,
            "significance": significance,
            "encrypted": False,
        }

    def get_wallet_identity_state(self, lambda_id: str) -> dict[str, Any]:
        """Get the current wallet identity state"""
        if lambda_id not in self.active_wallets:
            return {"error": "Wallet identity not found"}

        wallet_identity = self.active_wallets[lambda_id]
        vault = self.wallet_vaults[lambda_id]
        access_pattern = self.access_patterns[lambda_id]

        return {
            "lambda_id": wallet_identity.lambda_id,
            "tier": wallet_identity.tier.name,
            "wallet_address": wallet_identity.wallet_address,
            "creation_time": wallet_identity.creation_time.isoformat(),
            "last_verified": wallet_identity.last_verified.isoformat(),
            "has_biometric": wallet_identity.biometric_hash is not None,
            "consent_signatures_count": len(wallet_identity.consent_signatures),
            "transaction_count": access_pattern["transaction_count"],
            "vault_status": vault.get_wallet_status(),
            "last_updated": time.time(),
        }

    def update_wallet_identity(
        self, lambda_id: str, updates: dict[str, Any], reason: str = "manual_update"
    ) -> dict[str, Any]:
        """
        Update wallet identity attributes manually

        Args:
            lambda_id: Wallet identity ID
            updates: Dictionary of identity updates
            reason: Reason for the update

        Returns:
            Updated identity state
        """
        if lambda_id not in self.active_wallets:
            return {"error": "Wallet identity not found"}

        wallet_identity = self.active_wallets[lambda_id]

        # Save current state for snapshot
        self.get_wallet_identity_state(lambda_id)

        # Apply updates to allowed fields

        for field, value in updates.items():
            if field == "tier" and isinstance(value, str):
                try:
                    wallet_identity.tier = QITier[value.upper()]
                except KeyError:
                    self.logger.warning(f"Invalid tier: {value}")

        # Take snapshot of change
        self._take_wallet_identity_snapshot(f"{reason}_{lambda_id}")

        # Return updated state
        return self.get_wallet_identity_state(lambda_id)

    def get_transaction_patterns(self, lambda_id: str) -> list[dict[str, Any]]:
        """Get transaction patterns for wallet identity"""
        return self.transaction_patterns.get(lambda_id, [])

    def get_wallet_evolution(self, lambda_id: str) -> list[dict[str, Any]]:
        """Get the history of wallet identity evolution via snapshots"""
        return [
            {
                "timestamp": snapshot["timestamp"],
                "reason": snapshot["reason"],
                "wallet_count": len(snapshot.get("active_wallets", {})),
                "snapshot_id": snapshot.get("id"),
            }
            for snapshot in self.wallet_identity_snapshots
            if lambda_id in snapshot.get("reason", "")
        ]

    def _assess_transaction_significance(self, transaction_data: dict[str, Any]) -> float:
        """Assess the significance of a transaction"""
        significance = 0.0

        # Large amounts are more significant
        amount = transaction_data.get("amount", 0)
        if amount > 1000:  # ΛCOIN threshold
            significance += 0.3
        elif amount > 100:
            significance += 0.2

        # First-time recipient addresses
        if transaction_data.get("is_new_recipient", False):
            significance += 0.3

        # Cross-chain transactions
        if transaction_data.get("is_cross_chain", False):
            significance += 0.2

        # DeFi interactions
        if transaction_data.get("is_defi", False):
            significance += 0.2

        # High-value currencies
        currency = transaction_data.get("currency", "")
        if currency in ["BTC", "ETH"]:
            significance += 0.1

        return min(significance, 1.0)

    def _take_wallet_identity_snapshot(self, reason: str):
        """Take a snapshot of current wallet identity state"""
        snapshot = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "reason": reason,
            "wallet_identity": self.wallet_identity.copy(),
            "active_wallets": {k: v.lambda_id for k, v in self.active_wallets.items()},
        }

        self.wallet_identity_snapshots.append(snapshot)

        # Limit the number of stored snapshots
        max_snapshots = 100
        if len(self.wallet_identity_snapshots) > max_snapshots:
            self.wallet_identity_snapshots = self.wallet_identity_snapshots[-max_snapshots:]

    def _load_wallet_identity(self, identity_file: str):
        """Load wallet identity from a file"""
        try:
            with open(identity_file) as f:
                saved_identity = json.load(f)

            # Update identity with saved values
            for key, value in saved_identity.items():
                if key in self.wallet_identity:
                    self.wallet_identity[key] = value

            self.logger.info(f"Loaded wallet identity from {identity_file}")

            # Take snapshot of loaded identity
            self._take_wallet_identity_snapshot("loaded_from_file")

        except Exception as e:
            self.logger.error(f"Failed to load wallet identity from {identity_file}: {e}")
            # Continue with default identity

    def save_wallet_identity(self, identity_file: str) -> bool:
        """Save current wallet identity to a file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(identity_file), exist_ok=True)

            # Create saveable data
            save_data = {
                **self.wallet_identity,
                "active_wallets_count": len(self.active_wallets),
                "transaction_patterns_count": sum(len(patterns) for patterns in self.transaction_patterns.values()),
                "snapshots_count": len(self.wallet_identity_snapshots),
            }

            with open(identity_file, "w") as f:
                json.dump(save_data, f, indent=2, default=str)

            self.logger.info(f"Saved wallet identity to {identity_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save wallet identity to {identity_file}: {e}")
            return False

    def get_security_summary(self) -> dict[str, Any]:
        """Get security summary for all wallet identities"""
        total_wallets = len(self.active_wallets)
        biometric_protected = sum(1 for wallet in self.active_wallets.values() if wallet.biometric_hash is not None)

        tier_distribution = defaultdict(int)
        for wallet in self.active_wallets.values():
            tier_distribution[wallet.tier.name] += 1

        return {
            "total_wallets": total_wallets,
            "biometric_protected": biometric_protected,
            "biometric_percentage": (biometric_protected / max(1, total_wallets)) * 100,
            "tier_distribution": dict(tier_distribution),
            "total_transactions": sum(len(patterns) for patterns in self.transaction_patterns.values()),
            "vaults_active": len(self.wallet_vaults),
            "security_events": sum(
                len(pattern.get("security_events", [])) for pattern in self.access_patterns.values()
            ),
        }
