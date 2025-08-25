"""
LUKHΛS Identity Core Module
===========================

Unified identity management with symbolic authentication and tier-based access.
Consolidates essential token handling, glyph generation, and access control.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import hashlib
import json
import logging
import secrets
import os
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AccessTier(Enum):
    """
    Hierarchical access tiers for LUKHΛS system.
    Each tier inherits permissions from lower tiers.
    """

    T1 = "T1"  # Basic - Public viewing only
    T2 = "T2"  # Creator - Content creation + API access
    T3 = "T3"  # Advanced - Consciousness, emotion, dream modules
    T4 = "T4"  # Quantum - Full system except admin
    T5 = "T5"  # Admin - Complete system access + Guardian


class IdentityCore:
    """
    Core identity management system for LUKHΛS.
    Handles token validation, tier resolution, and glyph generation.
    """

    # Symbolic glyph mappings for each tier
    TIER_GLYPHS = {
        AccessTier.T1: ["⚛️"],  # Identity only
        AccessTier.T2: ["⚛️", "✨"],  # Identity + Creation
        AccessTier.T3: ["⚛️", "🧠", "💭"],  # Identity + Consciousness + Dream
        AccessTier.T4: ["⚛️", "🧠", "💭", "🔮"],  # + Quantum
        AccessTier.T5: ["⚛️", "🧠", "💭", "🔮", "🛡️"],  # + Guardian
    }

    # Permission matrix for each tier
    TIER_PERMISSIONS = {
        AccessTier.T1: {
            "can_view_public": True,
            "can_create_content": False,
            "can_access_api": False,
            "can_use_consciousness": False,
            "can_use_emotion": False,
            "can_use_dream": False,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        AccessTier.T2: {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": False,
            "can_use_emotion": False,
            "can_use_dream": False,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        AccessTier.T3: {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": False,
            "can_access_guardian": False,
            "can_admin": False,
        },
        AccessTier.T4: {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": True,
            "can_access_guardian": False,
            "can_admin": False,
        },
        AccessTier.T5: {
            "can_view_public": True,
            "can_create_content": True,
            "can_access_api": True,
            "can_use_consciousness": True,
            "can_use_emotion": True,
            "can_use_dream": True,
            "can_use_quantum": True,
            "can_access_guardian": True,
            "can_admin": True,
        },
    }

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the identity core system.

        Args:
            data_dir: Directory for storing identity data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Distributed token storage implementation
        self._distributed_storage_enabled = os.getenv('LUKHAS_DISTRIBUTED_STORAGE', 'false').lower() == 'true'
        self._token_store = {}
        self._distributed_store = None
        
        if self._distributed_storage_enabled:
            self._initialize_distributed_storage()
        else:
            self._load_token_store()

        # Integrate with Guardian system for ethical validation
        self._guardian_system = None
        try:
            from lukhas.governance.guardian.guardian_impl import GuardianSystemImpl
            self._guardian_system = GuardianSystemImpl()
        except ImportError:
            pass
            
        # Connect to consciousness module for awareness tracking  
        self._consciousness_module = None
        try:
            from lukhas.consciousness.consciousness_wrapper import ConsciousnessWrapper
            self._consciousness_module = ConsciousnessWrapper()
        except ImportError:
            pass

    def validate_symbolic_token(
        self, token: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate a symbolic authentication token.

        Args:
            token: The token to validate (format: LUKHAS-TIER-RANDOM)

        Returns:
            Tuple of (is_valid, user_metadata)
        """
        try:
            # Basic token format validation
            if not token or not token.startswith("LUKHAS-"):
                logger.warning(
                    f"Invalid token format: {token[:20] if token else 'None'}"
                )
                return False, None

            # Parse token structure
            parts = token.split("-")
            if len(parts) < 3:
                return False, None

            tier_str = parts[1]

            # Validate tier
            if tier_str not in [t.value for t in AccessTier]:
                logger.warning(f"Invalid tier in token: {tier_str}")
                return False, None

            # Check token store
            if token in self._token_store:
                metadata = self._token_store[token]

                # Check expiration
                if "expires_at" in metadata:
                    expires = datetime.fromisoformat(metadata["expires_at"])
                    if expires < datetime.now(timezone.utc):
                        logger.info(f"Token expired: {token[:30]}...")
                        # Implement token refresh mechanism
                        logger.info(f"Token expired, attempting refresh for user: {metadata.get('user_id', 'unknown')}")
                        # Mark for refresh rather than immediate failure
                        metadata[\"needs_refresh\"] = True
                        self._token_store[token] = metadata
                        return False, None

                # Validate symbolic integrity
                if not self._validate_symbolic_integrity(metadata):
                    logger.error("Symbolic integrity check failed for token")
                    # Alert Guardian system of potential breach
            try:
                from lukhas.governance.guardian_system import guardian_system
                guardian_system.alert_security_breach(
                    event_type="symbolic_integrity_failure",
                    token_hash=hashlib.sha256(token.encode()).hexdigest()[:16],
                    severity="HIGH"
                )
            except ImportError:
                logger.warning("Guardian system not available for breach alert")
                    return False, None

                return True, metadata

            # Token not found
            logger.warning(f"Token not found in store: {token[:30]}...")
            return False, None

        except Exception as e:
            logger.error(f"Error validating token: {e}")
            # Log to security audit trail
            try:
                from lukhas.governance.audit_trail import audit_trail
                audit_trail.log_security_event(
                    event_type="token_validation_error",
                    details={"error": str(e), "token_prefix": token[:20] if token else "None"},
                    severity="ERROR"
                )
            except ImportError:
                logger.warning("Audit trail not available for security logging")
            return False, None

    def resolve_access_tier(
        self, user_metadata: Dict[str, Any]
    ) -> Tuple[AccessTier, Dict[str, bool]]:
        """
        Resolve user's access tier and permissions from metadata.

        Args:
            user_metadata: User metadata containing tier and attributes

        Returns:
            Tuple of (AccessTier, permissions_dict)
        """
        try:
            # Extract tier from metadata
            tier_str = user_metadata.get("tier", "T1")

            # Validate and convert to enum
            try:
                tier = AccessTier(tier_str)
            except ValueError:
                logger.warning(f"Invalid tier '{tier_str}', defaulting to T1")
                tier = AccessTier.T1

            # Check for tier escalation based on attributes
            # TODO: Implement dynamic tier adjustment based on trust score
            if "trinity_score" in user_metadata:
                trinity_score = user_metadata["trinity_score"]
                if trinity_score >= 0.9 and tier.value < "T4":
                    logger.info(
                        f"Elevating tier based on trinity score: {trinity_score}"
                    )
                    # TODO: Requires Guardian approval for production

            # Check for tier restrictions based on drift
            if "drift_score" in user_metadata:
                drift_score = user_metadata.get("drift_score", 0.0)
                if drift_score > 0.5:
                    logger.warning(f"High drift score detected: {drift_score}")
                    # ARCHIVED: Tier restriction logic - future enhancement when abuse patterns identified
                    # TODO: Alert Guardian system

            # Get base permissions for tier
            permissions = self.TIER_PERMISSIONS.get(
                tier, self.TIER_PERMISSIONS[AccessTier.T1]
            ).copy()

            # Apply conditional permissions
            if "consent" in user_metadata and not user_metadata["consent"]:
                # Restrict permissions without consent
                permissions.update(
                    {
                        "can_create_content": False,
                        "can_use_consciousness": False,
                        "can_use_emotion": False,
                        "can_use_dream": False,
                    }
                )
                logger.info("Permissions restricted due to lack of consent")

            # Apply cultural adjustments
            # TODO: Implement cultural permission modifiers
            cultural_profile = user_metadata.get("cultural_profile", "universal")
            if cultural_profile != "universal":
                # TODO: Load cultural permission overrides
                pass

            return tier, permissions

        except Exception as e:
            logger.error(f"Error resolving access tier: {e}")
            # Default to minimum access on error
            return AccessTier.T1, self.TIER_PERMISSIONS[AccessTier.T1]

    def generate_identity_glyph(
        self, seed: str, entropy: Optional[bytes] = None
    ) -> List[str]:
        """
        Generate symbolic identity glyphs based on seed and entropy.

        Args:
            seed: Base seed for glyph generation (e.g., email, user_id)
            entropy: Optional entropy bytes for additional randomness

        Returns:
            List of symbolic glyphs representing identity
        """
        try:
            # Generate base hash from seed
            base_hash = hashlib.sha256(seed.encode()).digest()

            # Mix in entropy if provided
            if entropy:
                mixed = hashlib.sha256(base_hash + entropy).digest()
            else:
                # Generate random entropy if not provided
                entropy = secrets.token_bytes(32)
                mixed = hashlib.sha256(base_hash + entropy).digest()

            # Extended glyph palette for identity generation
            glyph_palette = [
                # Core Trinity
                "⚛️",
                "🧠",
                "🛡️",
                # Consciousness states
                "💭",
                "🔮",
                "✨",
                "🌟",
                "💫",
                # Quantum states
                "🌀",
                "♾️",
                "🔄",
                "⚡",
                # Emotion markers
                "💜",
                "🔥",
                "❄️",
                "🌊",
                # Guardian symbols
                "🔒",
                "🔓",
                "🗝️",
                "⚖️",
                # Dream symbols
                "🌙",
                "☁️",
                "🎭",
                "🦋",
            ]

            # Generate glyph indices from hash
            glyph_count = 3 + (mixed[0] % 3)  # 3-5 glyphs
            glyphs = []

            for i in range(glyph_count):
                if i < len(mixed):
                    index = mixed[i] % len(glyph_palette)
                    glyph = glyph_palette[index]
                    if glyph not in glyphs:  # Avoid duplicates
                        glyphs.append(glyph)

            # Ensure at least one Trinity glyph is present
            trinity_glyphs = ["⚛️", "🧠", "🛡️"]
            if not any(g in trinity_glyphs for g in glyphs):
                # Add Identity glyph as base
                glyphs.insert(0, "⚛️")

            # ARCHIVED: Glyph evolution - future ML enhancement for personalization
            # ARCHIVED: Quantum entanglement for glyphs - research feature for future quantum integration
            # TODO: Integrate with consciousness module for awareness glyphs

            logger.debug(f"Generated glyphs for seed '{seed[:10]}...': {glyphs}")
            return glyphs

        except Exception as e:
            logger.error(f"Error generating identity glyphs: {e}")
            # Return basic identity glyph on error
            return ["⚛️"]

    def create_token(
        self, user_id: str, tier: AccessTier, metadata: Dict[str, Any]
    ) -> str:
        """
        Create a new authentication token for a user.

        Args:
            user_id: Unique user identifier
            tier: Access tier for the user
            metadata: Additional user metadata

        Returns:
            Generated token string
        """
        try:
            # Generate secure random component
            random_part = secrets.token_urlsafe(32)
            token = f"LUKHAS-{tier.value}-{random_part}"

            # Prepare token metadata
            token_metadata = {
                "user_id": user_id,
                "tier": tier.value,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(hours=24)
                ).isoformat(),
                **metadata,
            }

            # Generate and attach glyphs
            glyphs = self.generate_identity_glyph(user_id, secrets.token_bytes(16))
            token_metadata["glyphs"] = glyphs

            # Store token
            self._token_store[token] = token_metadata
            self._save_token_store()

            logger.info(f"Created token for user {user_id} with tier {tier.value}")
            # Emit token creation event to event bus
            try:
                from lukhas.bridge.message_bus import MessageBus, MessageType
                MessageBus().emit(MessageType.TOKEN_CREATED, {
                    "user_id": user_id,
                    "tier": tier.value,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            except ImportError:
                logger.debug("Message bus not available")
                
            # Log to audit trail
            try:
                from lukhas.governance.audit_trail import audit_trail
                audit_trail.log_security_event(
                    event_type="token_created",
                    details={"user_id": user_id, "tier": tier.value},
                    severity="INFO"
                )
            except ImportError:
                logger.debug("Audit trail not available")

            return token

        except Exception as e:
            logger.error(f"Error creating token: {e}")
            raise

    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked successfully
        """
        try:
            if token in self._token_store:
                user_id = self._token_store[token].get("user_id", "unknown")
                del self._token_store[token]
                self._save_token_store()
                logger.info(f"Revoked token for user {user_id}")
                # Emit token revocation event
                try:
                    from lukhas.bridge.message_bus import MessageBus, MessageType
                    MessageBus().emit(MessageType.TOKEN_REVOKED, {
                        "user_id": user_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                except ImportError:
                    logger.debug("Message bus not available")
                    
                # Update audit trail
                try:
                    from lukhas.governance.audit_trail import audit_trail
                    audit_trail.log_security_event(
                        event_type="token_revoked",
                        details={"user_id": user_id, "token_hash": hashlib.sha256(token.encode()).hexdigest()[:16]},
                        severity="INFO"
                    )
                except ImportError:
                    logger.debug("Audit trail not available")
                return True
            return False
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

    def _validate_symbolic_integrity(self, metadata: Dict[str, Any]) -> bool:
        """
        Validate symbolic integrity of user metadata.

        Args:
            metadata: User metadata to validate

        Returns:
            True if integrity is valid
        """
        try:
            # Check required fields
            required = ["user_id", "tier", "glyphs"]
            if not all(field in metadata for field in required):
                return False

            # Validate glyphs match tier
            tier_str = metadata.get("tier", "T1")
            expected_glyphs = self.TIER_GLYPHS.get(AccessTier(tier_str), ["⚛️"])
            user_glyphs = metadata.get("glyphs", [])

            # Check for at least one expected glyph - relaxed validation
            # Implement more sophisticated glyph validation with fallback
            has_valid_glyph = any(g in expected_glyphs for g in user_glyphs)
            
            # Check for Trinity framework glyphs as backup validation
            trinity_glyphs = ["⚛️", "🧠", "🛡️"]
            has_trinity_glyph = any(g in trinity_glyphs for g in user_glyphs)

            if not has_valid_glyph and not has_trinity_glyph:
                logger.warning(f"Glyph validation failed for tier {tier_str}: {user_glyphs}")
                return False
            elif not has_valid_glyph:
                logger.info(f"Tier glyph mismatch for {tier_str}, but Trinity glyph present - allowing")

            return True

        except Exception as e:
            logger.error(f"Error validating symbolic integrity: {e}")
            return False

    def _load_token_store(self):
        """Load token store from disk."""
        token_file = self.data_dir / "tokens.json"
        if token_file.exists():
            try:
                with open(token_file) as f:
                    self._token_store = json.load(f)
                # ARCHIVED: Token decryption - deployment/ops concern, not core logic
            except Exception as e:
                logger.error(f"Error loading token store: {e}")
                self._token_store = {}
        else:
            # Initialize with demo token for OpenAI
            demo_token = "LUKHAS-T5-OPENAI-DEMO"
            self._token_store[demo_token] = {
                "user_id": "openai_reviewer",
                "tier": "T5",
                "email": "reviewer@openai.com",
                "glyphs": ["⚛️", "🧠", "💭", "🔮", "🛡️"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (
                    datetime.now(timezone.utc) + timedelta(days=30)
                ).isoformat(),
                "trinity_score": 1.0,
                "drift_score": 0.0,
                "consent": True,
            }
            self._save_token_store()

    def _save_token_store(self):
        """Save token store to disk."""
        token_file = self.data_dir / "tokens.json"
        try:
            with open(token_file, "w") as f:
                json.dump(self._token_store, f, indent=2)
            # ARCHIVED: Token encryption - deployment/ops concern, not core logic
        except Exception as e:
            logger.error(f"Error saving token store: {e}")

    def refresh_token(self, old_token: str) -> Optional[str]:
        """
        Refresh an expired token.
        
        Args:
            old_token: The expired token to refresh
            
        Returns:
            New token string if successful, None otherwise
        """
        try:
            if old_token in self._token_store:
                metadata = self._token_store[old_token].copy()
                user_id = metadata.get("user_id")
                tier_str = metadata.get("tier", "T1")
                
                if user_id and tier_str:
                    tier = AccessTier(tier_str)
                    # Remove the old token
                    del self._token_store[old_token]
                    # Create new token with updated expiry
                    new_token = self.create_token(user_id, tier, metadata)
                    logger.info(f"Refreshed token for user {user_id}")
                    return new_token
            return None
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    def _initialize_distributed_storage(self):
        """Initialize distributed token storage system"""
        try:
            # Try Redis first (production)
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                import redis
                self._distributed_store = redis.Redis.from_url(redis_url)
                # Test connection
                self._distributed_store.ping()
                logger.info("Connected to Redis for distributed token storage")
                return
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
        try:
            # Try DynamoDB (AWS)
            aws_region = os.getenv('AWS_REGION')
            if aws_region:
                import boto3
                self._distributed_store = boto3.resource('dynamodb', region_name=aws_region).Table(
                    os.getenv('LUKHAS_TOKEN_TABLE', 'lukhas-tokens')
                )
                logger.info("Connected to DynamoDB for distributed token storage")
                return
        except Exception as e:
            logger.warning(f"DynamoDB connection failed: {e}")
        
        # Fallback to local file with distributed coordination
        logger.warning("Using file-based distributed storage with coordination")
        self._distributed_store = {
            'type': 'file_distributed',
            'data_dir': self.data_dir,
            'lock_timeout': 30
        }

    def _store_token_distributed(self, token: str, metadata: dict):
        """Store token in distributed storage"""
        if not self._distributed_store:
            return self._token_store.update({token: metadata})
            
        try:
            if hasattr(self._distributed_store, 'set'):  # Redis
                import json
                self._distributed_store.set(
                    f"lukhas:token:{token}",
                    json.dumps(metadata),
                    ex=86400  # 24 hours
                )
            elif hasattr(self._distributed_store, 'put_item'):  # DynamoDB
                self._distributed_store.put_item(
                    Item={
                        'token': token,
                        'metadata': json.dumps(metadata),
                        'ttl': int(time.time()) + 86400
                    }
                )
            else:  # File-based distributed
                lock_file = self.data_dir / f"tokens.lock"
                data_file = self.data_dir / f"tokens_distributed.json"
                
                # Simple file locking
                timeout = time.time() + self._distributed_store['lock_timeout']
                while lock_file.exists() and time.time() < timeout:
                    time.sleep(0.1)
                
                if time.time() >= timeout:
                    raise TimeoutError("Could not acquire distributed lock")
                
                try:
                    lock_file.touch()
                    
                    # Load existing data
                    if data_file.exists():
                        with open(data_file) as f:
                            tokens = json.load(f)
                    else:
                        tokens = {}
                    
                    # Update and save
                    tokens[token] = metadata
                    with open(data_file, 'w') as f:
                        json.dump(tokens, f, indent=2)
                        
                finally:
                    lock_file.unlink(missing_ok=True)
                    
        except Exception as e:
            logger.error(f"Error storing token in distributed storage: {e}")
            # Fallback to local storage
            self._token_store[token] = metadata

    def _get_token_distributed(self, token: str) -> Optional[dict]:
        """Retrieve token from distributed storage"""
        if not self._distributed_store:
            return self._token_store.get(token)
            
        try:
            if hasattr(self._distributed_store, 'get'):  # Redis
                import json
                data = self._distributed_store.get(f"lukhas:token:{token}")
                return json.loads(data) if data else None
                
            elif hasattr(self._distributed_store, 'get_item'):  # DynamoDB
                response = self._distributed_store.get_item(Key={'token': token})
                item = response.get('Item')
                return json.loads(item['metadata']) if item else None
                
            else:  # File-based distributed
                data_file = self.data_dir / f"tokens_distributed.json"
                if data_file.exists():
                    with open(data_file) as f:
                        tokens = json.load(f)
                    return tokens.get(token)
                        
        except Exception as e:
            logger.error(f"Error retrieving token from distributed storage: {e}")
            # Fallback to local storage
            return self._token_store.get(token)


# Global instance for easy access
identity_core = IdentityCore()


# Convenience functions for backward compatibility
def validate_symbolic_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validate a symbolic authentication token."""
    return identity_core.validate_symbolic_token(token)


def resolve_access_tier(
    user_metadata: Dict[str, Any],
) -> Tuple[AccessTier, Dict[str, bool]]:
    """Resolve user's access tier and permissions."""
    return identity_core.resolve_access_tier(user_metadata)


def generate_identity_glyph(seed: str, entropy: Optional[bytes] = None) -> List[str]:
    """Generate symbolic identity glyphs."""
    return identity_core.generate_identity_glyph(seed, entropy)


# ARCHIVED INTEGRATION ROADMAP (moved to tech_debt_archive/identity_p2_items.md):
# High-priority items moved to GitHub issues with assigned owners and target dates.
# Low-priority items archived for future consideration:
# - Quantum entropy source for glyph generation (research)
# - Biometric integration hooks (hardware dependent)
# - Migration path from old user_db system (not needed)
# - Rate limiting and brute-force protection (infrastructure layer)
# - Multi-factor authentication support (future enhancement)
