"""
Privacy-Preserving Symbol System for Universal Language
========================================================

Implements device-local private language with end-to-end privacy.
Based on Universal Language spec from /Users/agi_dev/LOCAL-REPOS/Universal_Language/.
"""
import random
import streamlit as st

import hashlib
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy levels for symbol storage and transmission"""

    LOCAL_ONLY = "local_only"  # Never leaves device
    ANONYMOUS = "anonymous"  # Only hashes/IDs transmitted
    ENCRYPTED = "encrypted"  # Encrypted before transmission
    DIFFERENTIAL = "differential"  # With differential privacy noise
    PUBLIC = "public"  # Can be shared openly


@dataclass
class PrivateSymbol:
    """
    Private symbol stored on device only.

    Based on Universal Language spec for private idiolect.
    """

    symbol_id: str
    token: Any  # The actual private token (emoji, stroke, etc.)
    token_type: str  # emoji, stroke, word, color, audio, image
    meaning_id: str  # Universal concept ID
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    fingerprint: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    usage_count: int = 0

    def __post_init__(self):
        if not self.fingerprint:
            self.fingerprint = self.generate_fingerprint()

    def generate_fingerprint(self) -> str:
        """Generate fingerprint for the private token"""
        if self.token_type == "emoji":
            # Unicode canonical sequence
            return str(self.token)
        elif self.token_type == "stroke":
            # Hash of normalized path
            path_str = json.dumps(self.token)
            return hashlib.sha256(path_str.encode()).hexdigest()[:16]
        elif self.token_type == "color":
            # Normalized color representation
            return str(self.token)
        elif self.token_type == "word":
            # Simple text hash
            return hashlib.sha256(str(self.token).encode()).hexdigest()[:16]
        else:
            # Generic hash
            return hashlib.sha256(str(self.token).encode()).hexdigest()[:16]

    def to_anonymous(self) -> dict[str, Any]:
        """Convert to anonymous representation (no private data)"""
        return {
            "anonymous_id": hashlib.sha256(self.symbol_id.encode()).hexdigest()[:16],
            "token_type": self.token_type,
            "meaning_id": self.meaning_id,
            "confidence": self.confidence,
            "usage_count": self.usage_count,
        }


@dataclass
class PrivateBinding:
    """Binding between private symbol and universal meaning"""

    binding_id: str
    symbol_id: str
    meaning_id: str  # Universal Concept Layer ID
    confidence: float = 1.0
    context: Optional[str] = None
    active: bool = True
    created_at: float = field(default_factory=time.time)

    def to_universal(self) -> str:
        """Get universal concept ID for transmission"""
        return self.meaning_id


class SymbolEncryption:
    """
    Handles encryption for private symbols.

    Based on Universal Language spec security requirements.
    """

    def __init__(self, device_secret: Optional[bytes] = None):
        self.device_secret = device_secret or self._generate_device_secret()
        self.key_cache: dict[str, bytes] = {}

    def _generate_device_secret(self) -> bytes:
        """Generate device-specific secret"""
        return secrets.token_bytes(32)

    def derive_key(self, user_id: str, salt: bytes) -> bytes:
        """
        Derive encryption key using PBKDF2.

        Based on spec: K_device = KDF(ΛiD_seed ∥ device_secret ∥ salt)
        """
        cache_key = f"{user_id}:{salt.hex()}"
        if cache_key in self.key_cache:
            return self.key_cache[cache_key]

        # Simplified PBKDF2 implementation
        # In production, use proper crypto library
        combined = f"{user_id}:{self.device_secret.hex()}:{salt.hex()}".encode()
        key = hashlib.pbkdf2_hmac("sha256", combined, salt, 100000)

        self.key_cache[cache_key] = key
        return key

    def encrypt_symbol(self, symbol: PrivateSymbol, key: bytes) -> bytes:
        """Encrypt a private symbol"""
        # Serialize symbol
        symbol_data = json.dumps(
            {
                "token": str(symbol.token),
                "token_type": symbol.token_type,
                "meaning_id": symbol.meaning_id,
                "confidence": symbol.confidence,
            }
        )

        # Simple XOR encryption (use AES-GCM in production)
        encrypted = self._xor_encrypt(symbol_data.encode(), key)
        return encrypted

    def decrypt_symbol(self, encrypted_data: bytes, key: bytes) -> dict[str, Any]:
        """Decrypt a private symbol"""
        # Simple XOR decryption
        decrypted = self._xor_encrypt(encrypted_data, key)
        return json.loads(decrypted.decode())

    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption (for demonstration)"""
        # In production, use AES-GCM
        key_repeated = key * (len(data) // len(key) + 1)
        return bytes(a ^ b for a, b in zip(data, key_repeated))

    def hash_for_anonymous(self, data: str, salt: Optional[bytes] = None) -> str:
        """Create anonymous hash of data"""
        salt = salt or secrets.token_bytes(16)
        return hashlib.sha256(f"{data}:{salt.hex()}".encode()).hexdigest()[:16]


class ConceptAnonymizer:
    """
    Anonymizes concepts for privacy-preserving transmission.

    Only concept IDs cross the wire, never raw private tokens.
    """

    def __init__(self):
        self.anonymization_cache: dict[str, str] = {}
        self.reverse_cache: dict[str, str] = {}
        self.noise_epsilon = 1.0  # Differential privacy parameter

    def anonymize_concept(self, concept_id: str, user_id: str) -> str:
        """Anonymize a concept ID for transmission"""
        cache_key = f"{user_id}:{concept_id}"

        if cache_key in self.anonymization_cache:
            return self.anonymization_cache[cache_key]

        # Create anonymous ID
        anonymous_id = hashlib.sha256(cache_key.encode()).hexdigest()[:16]

        # Cache both directions
        self.anonymization_cache[cache_key] = anonymous_id
        self.reverse_cache[anonymous_id] = concept_id

        return anonymous_id

    def deanonymize_concept(self, anonymous_id: str) -> Optional[str]:
        """Recover original concept ID from anonymous ID"""
        return self.reverse_cache.get(anonymous_id)

    def add_differential_privacy(self, value: float) -> float:
        """Add Laplacian noise for differential privacy"""
        # Add noise based on epsilon parameter
        scale = 1.0 / self.noise_epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

    def anonymize_statistics(self, stats: dict[str, Any]) -> dict[str, Any]:
        """Anonymize statistics with differential privacy"""
        anonymous_stats = {}

        for key, value in stats.items():
            if isinstance(value, (int, float)):
                # Add noise to numerical values
                anonymous_stats[key] = self.add_differential_privacy(value)
            elif isinstance(value, str):
                # Hash string values
                anonymous_stats[key] = hashlib.sha256(value.encode()).hexdigest()[:8]
            else:
                # Keep other types as-is or omit
                anonymous_stats[key] = "REDACTED"

        return anonymous_stats


class PrivateSymbolVault:
    """
    Device-local vault for private symbols.

    Based on Universal Language spec - encrypted local storage,
    never leaves device by default.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.symbols: dict[str, PrivateSymbol] = {}
        self.bindings: dict[str, PrivateBinding] = {}
        self.render_preferences: dict[str, str] = {}  # concept_id -> preferred_symbol_id
        self.encryption = SymbolEncryption()
        self.anonymizer = ConceptAnonymizer()
        self.privacy_mode = PrivacyLevel.LOCAL_ONLY
        self.audit_log: list[dict[str, Any]] = []

        # Generate user-specific salt
        self.user_salt = secrets.token_bytes(16)
        self.encryption_key = self.encryption.derive_key(user_id, self.user_salt)

        logger.info(f"Private Symbol Vault initialized for user {user_id}")

    def bind_symbol(
        self,
        token: Any,
        token_type: str,
        meaning_id: str,
        confidence: float = 1.0,
        tags: Optional[list[str]] = None,
    ) -> PrivateSymbol:
        """Bind a private token to a universal meaning"""
        # Create private symbol
        symbol = PrivateSymbol(
            symbol_id=self._generate_symbol_id(),
            token=token,
            token_type=token_type,
            meaning_id=meaning_id,
            confidence=confidence,
            tags=tags or [],
        )

        # Store symbol
        self.symbols[symbol.symbol_id] = symbol

        # Create binding
        binding = PrivateBinding(
            binding_id=self._generate_binding_id(),
            symbol_id=symbol.symbol_id,
            meaning_id=meaning_id,
            confidence=confidence,
        )
        self.bindings[binding.binding_id] = binding

        # Log event
        self._log_event(
            "bind",
            {"symbol_id": symbol.symbol_id, "token_type": token_type, "meaning_id": meaning_id},
        )

        return symbol

    def unbind_symbol(self, symbol_id: str):
        """Remove binding for a symbol"""
        # Find and deactivate binding
        for binding in self.bindings.values():
            if binding.symbol_id == symbol_id:
                binding.active = False
                binding.confidence = 0.0

        # Log event
        self._log_event("unbind", {"symbol_id": symbol_id})

    def translate_private_to_universal(self, tokens: list[Any]) -> list[str]:
        """
        Translate private tokens to universal concept IDs.

        Core privacy feature - only concept IDs transmitted.
        """
        concept_ids = []

        for token in tokens:
            # Find matching symbol
            symbol = self._find_symbol_by_token(token)

            if symbol:
                # Get binding
                binding = self._get_active_binding(symbol.symbol_id)
                if binding:
                    # Use universal concept ID
                    concept_ids.append(binding.meaning_id)

                    # Update usage count
                    symbol.usage_count += 1
                else:
                    # No binding - use placeholder
                    concept_ids.append(f"UNBOUND.{symbol.fingerprint[:8]}")
            else:
                # Unknown token - create anonymous placeholder
                anonymous_id = self.anonymizer.hash_for_anonymous(str(token))
                concept_ids.append(f"UNKNOWN.{anonymous_id}")

        # Log translation (anonymous)
        self._log_event(
            "translate_to_universal",
            {"token_count": len(tokens), "concept_count": len(concept_ids)},
        )

        return concept_ids

    def translate_universal_to_private(self, concept_ids: list[str], mode: str = "preferred") -> list[Any]:
        """
        Translate universal concept IDs to private tokens.

        Personalized rendering based on user preferences.
        """
        private_tokens = []

        for concept_id in concept_ids:
            # Check render preference
            if concept_id in self.render_preferences:
                preferred_symbol_id = self.render_preferences[concept_id]
                symbol = self.symbols.get(preferred_symbol_id)
                if symbol:
                    private_tokens.append(symbol.token)
                    continue

            # Find symbols bound to this concept
            matching_symbols = self._find_symbols_by_meaning(concept_id)

            if matching_symbols:
                if mode == "preferred":
                    # Use highest confidence symbol
                    symbol = max(matching_symbols, key=lambda s: s.confidence)
                elif mode == "diverse":
                    # Rotate through different symbols
                    symbol = matching_symbols[len(private_tokens) % len(matching_symbols)]
                else:
                    # Default to first
                    symbol = matching_symbols[0]

                private_tokens.append(symbol.token)
            else:
                # No private symbol - use concept ID as fallback
                private_tokens.append(f"[{concept_id}]")

        # Log translation
        self._log_event(
            "translate_to_private",
            {"concept_count": len(concept_ids), "token_count": len(private_tokens), "mode": mode},
        )

        return private_tokens

    def set_render_preference(self, concept_id: str, symbol_id: str):
        """Set preferred private symbol for a concept"""
        if symbol_id in self.symbols:
            self.render_preferences[concept_id] = symbol_id
            self._log_event("set_preference", {"concept_id": concept_id, "symbol_id": symbol_id})

    def export_vault(self, password: str) -> bytes:
        """Export encrypted vault for backup"""
        # Serialize vault data
        vault_data = {
            "user_id": self.user_id,
            "symbols": {sid: s.__dict__ for sid, s in self.symbols.items()},
            "bindings": {bid: b.__dict__ for bid, b in self.bindings.items()},
            "preferences": self.render_preferences,
            "timestamp": time.time(),
        }

        # Derive export key from password
        export_salt = secrets.token_bytes(16)
        export_key = hashlib.pbkdf2_hmac("sha256", password.encode(), export_salt, 100000)

        # Encrypt vault
        vault_json = json.dumps(vault_data, default=str)
        encrypted = self.encryption._xor_encrypt(vault_json.encode(), export_key)

        # Package with salt
        export_package = {"salt": export_salt.hex(), "data": encrypted.hex(), "version": "1.0"}

        return json.dumps(export_package).encode()

    def import_vault(self, exported_data: bytes, password: str) -> bool:
        """Import encrypted vault from backup"""
        try:
            # Parse export package
            package = json.loads(exported_data.decode())
            export_salt = bytes.fromhex(package["salt"])
            encrypted_data = bytes.fromhex(package["data"])

            # Derive import key
            import_key = hashlib.pbkdf2_hmac("sha256", password.encode(), export_salt, 100000)

            # Decrypt vault
            decrypted = self.encryption._xor_encrypt(encrypted_data, import_key)
            vault_data = json.loads(decrypted.decode())

            # Restore symbols and bindings with merge logic
            imported_symbols = vault_data.get("symbols", {})
            imported_bindings = vault_data.get("bindings", {})
            imported_stats = vault_data.get("stats", {})

            # Merge symbols with conflict resolution
            for symbol_id, symbol_data in imported_symbols.items():
                if symbol_id in self.symbols:
                    # Symbol exists - merge by choosing more recent or comprehensive version
                    existing_symbol = self.symbols[symbol_id]
                    imported_symbol = symbol_data

                    # Compare modification times if available
                    existing_time = existing_symbol.get("modified", 0)
                    imported_time = imported_symbol.get("modified", 0)

                    if imported_time > existing_time:
                        self.symbols[symbol_id] = imported_symbol
                        logger.info(f"Updated existing symbol {symbol_id} with imported version")
                    else:
                        logger.info(f"Kept existing symbol {symbol_id} (more recent)")
                else:
                    # New symbol - add it
                    self.symbols[symbol_id] = symbol_data
                    logger.info(f"Added new imported symbol {symbol_id}")

            # Merge bindings similarly
            for binding_key, binding_data in imported_bindings.items():
                if binding_key in self.bindings:
                    # Binding exists - merge values
                    existing_binding = self.bindings[binding_key]
                    imported_binding = binding_data

                    # For bindings, we can merge the values if they're different
                    if existing_binding != imported_binding:
                        # Create a merged binding with both values
                        if isinstance(existing_binding, list) and isinstance(imported_binding, list):
                            merged_values = list(set(existing_binding + imported_binding))
                            self.bindings[binding_key] = merged_values
                        else:
                            # Keep the imported version
                            self.bindings[binding_key] = imported_binding
                        logger.info(f"Merged binding {binding_key}")
                    else:
                        logger.info(f"Binding {binding_key} unchanged (same values)")
                else:
                    # New binding - add it
                    self.bindings[binding_key] = binding_data
                    logger.info(f"Added new imported binding {binding_key}")

            # Update stats by merging counters
            for stat_key, stat_value in imported_stats.items():
                if stat_key in self.stats:
                    if isinstance(stat_value, (int, float)) and isinstance(self.stats[stat_key], (int, float)):
                        # Sum numeric stats
                        self.stats[stat_key] += stat_value
                    else:
                        # Use imported value for non-numeric stats
                        self.stats[stat_key] = stat_value
                else:
                    self.stats[stat_key] = stat_value

            self._log_event("import", {"timestamp": vault_data.get("timestamp")})
            return True

        except Exception as e:
            logger.error(f"Failed to import vault: {e}")
            return False

    def get_privacy_stats(self) -> dict[str, Any]:
        """Get privacy-preserving statistics"""
        raw_stats = {
            "total_symbols": len(self.symbols),
            "total_bindings": len(self.bindings),
            "active_bindings": sum(1 for b in self.bindings.values() if b.active),
            "total_usage": sum(s.usage_count for s in self.symbols.values()),
            "unique_concepts": len({b.meaning_id for b in self.bindings.values()}),
        }

        # Apply differential privacy if not in local-only mode
        if self.privacy_mode != PrivacyLevel.LOCAL_ONLY:
            return self.anonymizer.anonymize_statistics(raw_stats)

        return raw_stats

    # Helper methods
    def _generate_symbol_id(self) -> str:
        """Generate unique symbol ID"""
        return f"SYMBOL_{secrets.token_hex(8)}"

    def _generate_binding_id(self) -> str:
        """Generate unique binding ID"""
        return f"BIND_{secrets.token_hex(8)}"

    def _find_symbol_by_token(self, token: Any) -> Optional[PrivateSymbol]:
        """Find symbol matching a token"""
        for symbol in self.symbols.values():
            if symbol.token == token:
                return symbol
        return None

    def _find_symbols_by_meaning(self, meaning_id: str) -> list[PrivateSymbol]:
        """Find all symbols bound to a meaning"""
        matching_symbols = []

        for binding in self.bindings.values():
            if binding.active and binding.meaning_id == meaning_id:
                symbol = self.symbols.get(binding.symbol_id)
                if symbol:
                    matching_symbols.append(symbol)

        return matching_symbols

    def _get_active_binding(self, symbol_id: str) -> Optional[PrivateBinding]:
        """Get active binding for a symbol"""
        for binding in self.bindings.values():
            if binding.active and binding.symbol_id == symbol_id:
                return binding
        return None

    def _log_event(self, event_type: str, metadata: dict[str, Any]):
        """Log vault event for audit"""
        self.audit_log.append({"timestamp": time.time(), "event": event_type, "metadata": metadata})

        # Limit audit log size
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]


# Singleton instances per user
_vault_instances: dict[str, PrivateSymbolVault] = {}


def get_private_vault(user_id: str) -> PrivateSymbolVault:
    """Get or create private vault for a user"""
    if user_id not in _vault_instances:
        _vault_instances[user_id] = PrivateSymbolVault(user_id)
    return _vault_instances[user_id]
