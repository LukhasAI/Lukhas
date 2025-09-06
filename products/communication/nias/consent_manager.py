#!/usr/bin/env python3
"""
NIΛS Consent Manager - Comprehensive consent validation and management
Part of the Lambda Products Suite by LUKHAS AI
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .nias_core import ConsentLevel

logger = logging.getLogger("Lambda.NIΛS.Consent", timezone)


class ConsentScope(Enum):
    """Different scopes of consent"""

    GLOBAL = "global"  # Overall system consent
    CONTENT_TYPE = "content_type"  # Specific content categories
    TEMPORAL = "temporal"  # Time-based consent
    EMOTIONAL = "emotional"  # Emotional state-based
    CONTEXTUAL = "contextual"  # Situational consent
    DATA_SOURCE = "data_source"  # Specific data source permissions
    VENDOR = "vendor"  # Vendor-specific consent
    AI_GENERATION = "ai_generation"  # AI content generation consent


class DataSource(Enum):
    """Types of user data sources"""

    EMAIL = "email"  # Email scanning
    SHOPPING_HISTORY = "shopping_history"  # Purchase history
    CALENDAR = "calendar"  # Calendar events
    LOCATION = "location"  # GPS/location data
    VOICE = "voice"  # Voice recordings (Siri, Alexa)
    BIOMETRIC = "biometric"  # Heart rate, stress levels
    BROWSING = "browsing"  # Web browsing history
    SOCIAL_MEDIA = "social_media"  # Social media activity
    HEALTH = "health"  # Health and fitness data
    FINANCIAL = "financial"  # Banking/payment data
    CONTACTS = "contacts"  # Address book
    MESSAGES = "messages"  # SMS/messaging apps
    PHOTOS = "photos"  # Photo library analysis
    APP_USAGE = "app_usage"  # App usage patterns
    DEVICE_SENSORS = "device_sensors"  # Accelerometer, gyroscope


class AIGenerationType(Enum):
    """Types of AI-generated content"""

    NARRATIVE = "narrative"  # GPT-generated dream narratives
    IMAGE = "image"  # DALL-E generated images
    VIDEO = "video"  # Sora-generated videos
    AUDIO = "audio"  # AI-generated audio/music
    HYBRID = "hybrid"  # Multi-modal content


@dataclass
class ConsentRecord:
    """Individual consent record"""

    user_id: str
    scope: ConsentScope
    level: ConsentLevel
    granted_at: datetime
    expires_at: Optional[datetime] = None
    context: dict[str, Any] = None
    revocable: bool = True
    audit_trail: list[dict[str, Any]] = None
    data_sources: list[DataSource] = None  # Specific data sources allowed
    vendor_ids: list[str] = None  # Specific vendors allowed
    ai_generation_types: list[AIGenerationType] = None  # AI content types allowed
    restrictions: dict[str, Any] = None  # Additional restrictions

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.audit_trail is None:
            self.audit_trail = []
        if self.data_sources is None:
            self.data_sources = []
        if self.vendor_ids is None:
            self.vendor_ids = []
        if self.ai_generation_types is None:
            self.ai_generation_types = []
        if self.restrictions is None:
            self.restrictions = {}

    def is_valid(self) -> bool:
        """Check if consent record is still valid"""
        return not (self.expires_at and datetime.now(timezone.utc) > self.expires_at)


class ConsentManager:
    """
    Advanced consent management for NIΛS system

    Features:
    - Granular consent scopes and levels
    - Temporal consent with expiration
    - Contextual consent validation
    - Audit trail for all consent changes
    - Integration with privacy regulations
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or self._default_config()
        self.consent_records: dict[str, list[ConsentRecord]] = {}
        self.consent_templates: dict[str, dict] = {}
        self.privacy_settings: dict[str, dict] = {}
        self.data_source_permissions: dict[str, dict[DataSource, bool]] = {}
        self.vendor_permissions: dict[str, dict[str, dict]] = {}
        self.ai_generation_settings: dict[str, dict] = {}

        logger.info("NIΛS Consent Manager initialized with enhanced data source permissions")

    def _default_config(self) -> dict:
        """Default consent manager configuration"""
        return {
            "default_expiry_hours": 8760,  # 1 year
            "require_explicit_consent": True,
            "enable_consent_withdrawal": True,
            "audit_all_changes": True,
            "gdpr_compliance": True,
            "ccpa_compliance": True,
            "require_data_source_consent": True,
            "require_vendor_consent": True,
            "ai_generation_consent_required": True,
            "ethical_check_required": True,
            "openai_api_enabled": True,
        }

    async def grant_consent(
        self,
        user_id: str,
        scope: ConsentScope,
        level: ConsentLevel,
        context: Optional[dict] = None,
        duration_hours: Optional[int] = None,
    ) -> bool:
        """
        Grant consent for a user with specified scope and level

        Args:
            user_id: User identifier
            scope: Scope of consent (global, content_type, etc.)
            level: Level of consent granted
            context: Additional context for the consent
            duration_hours: How long consent is valid (None = default)

        Returns:
            True if consent granted successfully
        """
        try:
            # Calculate expiration
            expires_at = None
            if duration_hours:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
            elif self.config["default_expiry_hours"]:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=self.config["default_expiry_hours"])

            # Create consent record
            record = ConsentRecord(
                user_id=user_id,
                scope=scope,
                level=level,
                granted_at=datetime.now(timezone.utc),
                expires_at=expires_at,
                context=context or {},
            )

            # Add audit entry
            record.audit_trail.append(
                {
                    "action": "granted",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": level.value,
                    "context": context or {},
                }
            )

            # Store record
            if user_id not in self.consent_records:
                self.consent_records[user_id] = []

            # Remove any existing consent for this scope
            self.consent_records[user_id] = [r for r in self.consent_records[user_id] if r.scope != scope]

            # Add new consent
            self.consent_records[user_id].append(record)

            logger.info(f"Consent granted: {user_id} - {scope.value} - {level.value}")
            return True

        except Exception as e:
            logger.error(f"Error granting consent: {e}")
            return False

    async def revoke_consent(self, user_id: str, scope: ConsentScope) -> bool:
        """
        Revoke consent for a specific scope

        Args:
            user_id: User identifier
            scope: Scope of consent to revoke

        Returns:
            True if consent revoked successfully
        """
        try:
            if user_id not in self.consent_records:
                return True  # Already no consent

            # Find and update consent record
            for record in self.consent_records[user_id]:
                if record.scope == scope:
                    if not record.revocable:
                        logger.warning(f"Cannot revoke non-revocable consent: {user_id} - {scope.value}")
                        return False

                    # Add audit entry
                    record.audit_trail.append(
                        {
                            "action": "revoked",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "reason": "user_request",
                        }
                    )

            # Remove consent records for this scope
            self.consent_records[user_id] = [r for r in self.consent_records[user_id] if r.scope != scope]

            logger.info(f"Consent revoked: {user_id} - {scope.value}")
            return True

        except Exception as e:
            logger.error(f"Error revoking consent: {e}")
            return False

    async def validate_consent(
        self,
        user_id: str,
        required_level: ConsentLevel,
        scope: ConsentScope = ConsentScope.GLOBAL,
        context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Validate if user has sufficient consent for an action

        Args:
            user_id: User identifier
            required_level: Minimum consent level required
            scope: Scope to check consent for
            context: Additional context for validation

        Returns:
            Dictionary with validation results
        """
        try:
            # Get user consent records
            user_records = self.consent_records.get(user_id, [])

            if not user_records:
                return {
                    "valid": False,
                    "reason": "No consent records found",
                    "current_level": ConsentLevel.NONE,
                    "required_level": required_level,
                }

            # Find matching consent record
            matching_record = None
            for record in user_records:
                if record.scope == scope and record.is_valid():
                    matching_record = record
                    break

            if not matching_record:
                # Try global consent as fallback
                if scope != ConsentScope.GLOBAL:
                    for record in user_records:
                        if record.scope == ConsentScope.GLOBAL and record.is_valid():
                            matching_record = record
                            break

            if not matching_record:
                return {
                    "valid": False,
                    "reason": "No valid consent record for scope",
                    "current_level": ConsentLevel.NONE,
                    "required_level": required_level,
                    "scope": scope.value,
                }

            # Check consent level hierarchy
            level_hierarchy = {
                ConsentLevel.NONE: 0,
                ConsentLevel.BASIC: 1,
                ConsentLevel.ENHANCED: 2,
                ConsentLevel.FULL_SYMBOLIC: 3,
                ConsentLevel.DREAM_AWARE: 4,
            }

            current_level_value = level_hierarchy[matching_record.level]
            required_level_value = level_hierarchy[required_level]

            if current_level_value >= required_level_value:
                # Additional contextual validation
                if context:
                    contextual_valid = await self._validate_contextual_consent(matching_record, context)
                    if not contextual_valid["valid"]:
                        return contextual_valid

                return {
                    "valid": True,
                    "reason": "Sufficient consent level",
                    "current_level": matching_record.level,
                    "required_level": required_level,
                    "granted_at": matching_record.granted_at.isoformat(),
                    "expires_at": (matching_record.expires_at.isoformat() if matching_record.expires_at else None),
                }
            else:
                return {
                    "valid": False,
                    "reason": "Insufficient consent level",
                    "current_level": matching_record.level,
                    "required_level": required_level,
                    "scope": scope.value,
                }

        except Exception as e:
            logger.error(f"Error validating consent: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {e!s}",
                "current_level": ConsentLevel.NONE,
                "required_level": required_level,
            }

    async def _validate_contextual_consent(self, record: ConsentRecord, context: dict[str, Any]) -> dict[str, Any]:
        """Validate contextual consent requirements"""
        # Check if consent context matches current context
        consent_context = record.context

        # Time-based consent
        if "time_restrictions" in consent_context:
            current_hour = datetime.now(timezone.utc).hour
            allowed_hours = consent_context["time_restrictions"].get("hours", [])
            if allowed_hours and current_hour not in allowed_hours:
                return {
                    "valid": False,
                    "reason": "Outside allowed time window for consent",
                    "current_hour": current_hour,
                    "allowed_hours": allowed_hours,
                }

        # Content type restrictions
        if "content_types" in consent_context:
            message_type = context.get("content_type")
            allowed_types = consent_context["content_types"]
            if message_type and message_type not in allowed_types:
                return {
                    "valid": False,
                    "reason": "Content type not covered by consent",
                    "message_type": message_type,
                    "allowed_types": allowed_types,
                }

        # Emotional state restrictions
        if "emotional_states" in consent_context:
            current_emotional_state = context.get("emotional_state")
            blocked_states = consent_context["emotional_states"].get("blocked", [])
            if current_emotional_state in blocked_states:
                return {
                    "valid": False,
                    "reason": "Consent blocked for current emotional state",
                    "emotional_state": current_emotional_state,
                }

        return {"valid": True, "reason": "Contextual consent validated"}

    async def get_consent_status(self, user_id: str) -> dict[str, Any]:
        """Get comprehensive consent status for a user"""
        user_records = self.consent_records.get(user_id, [])

        if not user_records:
            return {
                "user_id": user_id,
                "has_consent": False,
                "active_consents": [],
                "expired_consents": [],
            }

        active_consents = []
        expired_consents = []

        for record in user_records:
            consent_info = {
                "scope": record.scope.value,
                "level": record.level.value,
                "granted_at": record.granted_at.isoformat(),
                "expires_at": (record.expires_at.isoformat() if record.expires_at else None),
                "context": record.context,
            }

            if record.is_valid():
                active_consents.append(consent_info)
            else:
                expired_consents.append(consent_info)

        return {
            "user_id": user_id,
            "has_consent": len(active_consents) > 0,
            "active_consents": active_consents,
            "expired_consents": expired_consents,
            "last_updated": (max(r.granted_at for r in user_records).isoformat() if user_records else None),
        }

    async def create_consent_template(self, template_name: str, template_config: dict[str, Any]):
        """Create a reusable consent template"""
        self.consent_templates[template_name] = template_config
        logger.info(f"Created consent template: {template_name}")

    async def apply_consent_template(self, user_id: str, template_name: str, overrides: Optional[dict] = None) -> bool:
        """Apply a consent template to a user"""
        if template_name not in self.consent_templates:
            logger.error(f"Consent template not found: {template_name}")
            return False

        template = self.consent_templates[template_name].copy()
        if overrides:
            template.update(overrides)

        scope = ConsentScope(template.get("scope", "global"))
        level = ConsentLevel(template.get("level", "basic"))
        context = template.get("context", {})
        duration = template.get("duration_hours")

        return await self.grant_consent(user_id, scope, level, context, duration)

    def export_consent_data(self, user_id: str) -> dict[str, Any]:
        """Export all consent data for a user (GDPR compliance)"""
        user_records = self.consent_records.get(user_id, [])

        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "consent_records": [],
        }

        for record in user_records:
            export_data["consent_records"].append(
                {
                    "scope": record.scope.value,
                    "level": record.level.value,
                    "granted_at": record.granted_at.isoformat(),
                    "expires_at": (record.expires_at.isoformat() if record.expires_at else None),
                    "context": record.context,
                    "revocable": record.revocable,
                    "audit_trail": record.audit_trail,
                    "is_valid": record.is_valid(),
                }
            )

        return export_data

    async def delete_user_data(self, user_id: str) -> bool:
        """Delete all consent data for a user (Right to be forgotten)"""
        try:
            if user_id in self.consent_records:
                # Audit the deletion
                logger.info(f"Deleting all consent data for user: {user_id}")
                del self.consent_records[user_id]

            if user_id in self.privacy_settings:
                del self.privacy_settings[user_id]

            return True

        except Exception as e:
            logger.error(f"Error deleting user data: {e}")
            return False

    def get_system_metrics(self) -> dict[str, Any]:
        """Get consent system metrics"""
        total_users = len(self.consent_records)
        total_consents = sum(len(records) for records in self.consent_records.values())

        # Count by consent level
        level_counts = {level.value: 0 for level in ConsentLevel}
        for records in self.consent_records.values():
            for record in records:
                if record.is_valid():
                    level_counts[record.level.value] += 1

        return {
            "total_users": total_users,
            "total_consents": total_consents,
            "active_templates": len(self.consent_templates),
            "consent_levels": level_counts,
            "gdpr_compliance": self.config["gdpr_compliance"],
            "ccpa_compliance": self.config["ccpa_compliance"],
        }

    async def grant_data_source_consent(
        self,
        user_id: str,
        data_sources: list[DataSource],
        restrictions: Optional[dict] = None,
    ) -> bool:
        """
        Grant consent for specific data sources

        Args:
            user_id: User identifier
            data_sources: List of data sources to grant access to
            restrictions: Optional restrictions on data usage

        Returns:
            True if consent granted successfully
        """
        try:
            if user_id not in self.data_source_permissions:
                self.data_source_permissions[user_id] = {}

            # Update permissions for each data source
            for source in data_sources:
                self.data_source_permissions[user_id][source] = True

                # Create consent record for data source
                record = ConsentRecord(
                    user_id=user_id,
                    scope=ConsentScope.DATA_SOURCE,
                    level=ConsentLevel.ENHANCED,
                    granted_at=datetime.now(timezone.utc),
                    data_sources=[source],
                    restrictions=restrictions or {},
                )

                # Add audit entry
                record.audit_trail.append(
                    {
                        "action": "data_source_granted",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "data_source": source.value,
                        "restrictions": restrictions or {},
                    }
                )

                # Store record
                if user_id not in self.consent_records:
                    self.consent_records[user_id] = []
                self.consent_records[user_id].append(record)

            logger.info(f"Data source consent granted for {user_id}: {[s.value for s in data_sources]}")
            return True

        except Exception as e:
            logger.error(f"Error granting data source consent: {e}")
            return False

    async def revoke_data_source_consent(self, user_id: str, data_sources: list[DataSource]) -> bool:
        """Revoke consent for specific data sources"""
        try:
            if user_id not in self.data_source_permissions:
                return True

            for source in data_sources:
                if source in self.data_source_permissions[user_id]:
                    self.data_source_permissions[user_id][source] = False

            # Update consent records
            if user_id in self.consent_records:
                for record in self.consent_records[user_id]:
                    if record.scope == ConsentScope.DATA_SOURCE:
                        record.audit_trail.append(
                            {
                                "action": "data_source_revoked",
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                                "data_sources": [s.value for s in data_sources],
                            }
                        )

            logger.info(f"Data source consent revoked for {user_id}: {[s.value for s in data_sources]}")
            return True

        except Exception as e:
            logger.error(f"Error revoking data source consent: {e}")
            return False

    async def check_data_source_permission(self, user_id: str, data_source: DataSource) -> bool:
        """Check if user has granted permission for a specific data source"""
        if user_id not in self.data_source_permissions:
            return False
        return self.data_source_permissions[user_id].get(data_source, False)

    async def grant_vendor_consent(
        self,
        user_id: str,
        vendor_id: str,
        permissions: dict[str, Any],
        data_sources: Optional[list[DataSource]] = None,
    ) -> bool:
        """
        Grant consent for a specific vendor to access user data

        Args:
            user_id: User identifier
            vendor_id: Vendor identifier
            permissions: Vendor-specific permissions
            data_sources: Data sources vendor can access

        Returns:
            True if consent granted successfully
        """
        try:
            if user_id not in self.vendor_permissions:
                self.vendor_permissions[user_id] = {}

            # Store vendor permissions
            self.vendor_permissions[user_id][vendor_id] = {
                "granted_at": datetime.now(timezone.utc).isoformat(),
                "permissions": permissions,
                "data_sources": [s.value for s in data_sources] if data_sources else [],
                "active": True,
            }

            # Create consent record
            record = ConsentRecord(
                user_id=user_id,
                scope=ConsentScope.VENDOR,
                level=ConsentLevel.ENHANCED,
                granted_at=datetime.now(timezone.utc),
                vendor_ids=[vendor_id],
                data_sources=data_sources or [],
                context={"permissions": permissions},
            )

            # Add audit entry
            record.audit_trail.append(
                {
                    "action": "vendor_consent_granted",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "vendor_id": vendor_id,
                    "permissions": permissions,
                }
            )

            # Store record
            if user_id not in self.consent_records:
                self.consent_records[user_id] = []
            self.consent_records[user_id].append(record)

            logger.info(f"Vendor consent granted for {user_id} to vendor {vendor_id}")
            return True

        except Exception as e:
            logger.error(f"Error granting vendor consent: {e}")
            return False

    async def check_vendor_permission(
        self, user_id: str, vendor_id: str, data_source: Optional[DataSource] = None
    ) -> bool:
        """Check if vendor has permission to access user data"""
        if user_id not in self.vendor_permissions:
            return False

        if vendor_id not in self.vendor_permissions[user_id]:
            return False

        vendor_perms = self.vendor_permissions[user_id][vendor_id]
        if not vendor_perms.get("active", False):
            return False

        # Check specific data source permission if provided
        if data_source:
            allowed_sources = vendor_perms.get("data_sources", [])
            return data_source.value in allowed_sources

        return True

    async def grant_ai_generation_consent(
        self,
        user_id: str,
        generation_types: list[AIGenerationType],
        ethical_checks: bool = True,
        openai_api: bool = True,
    ) -> bool:
        """
        Grant consent for AI-generated content

        Args:
            user_id: User identifier
            generation_types: Types of AI content allowed
            ethical_checks: Require ethical validation
            openai_api: Allow OpenAI API usage

        Returns:
            True if consent granted successfully
        """
        try:
            if user_id not in self.ai_generation_settings:
                self.ai_generation_settings[user_id] = {}

            # Store AI generation settings
            self.ai_generation_settings[user_id] = {
                "generation_types": [t.value for t in generation_types],
                "ethical_checks_required": ethical_checks,
                "openai_api_enabled": openai_api,
                "granted_at": datetime.now(timezone.utc).isoformat(),
            }

            # Create consent record
            record = ConsentRecord(
                user_id=user_id,
                scope=ConsentScope.AI_GENERATION,
                level=ConsentLevel.FULL_SYMBOLIC,
                granted_at=datetime.now(timezone.utc),
                ai_generation_types=generation_types,
                context={"ethical_checks": ethical_checks, "openai_api": openai_api},
            )

            # Add audit entry
            record.audit_trail.append(
                {
                    "action": "ai_generation_consent_granted",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "types": [t.value for t in generation_types],
                    "ethical_checks": ethical_checks,
                    "openai_api": openai_api,
                }
            )

            # Store record
            if user_id not in self.consent_records:
                self.consent_records[user_id] = []
            self.consent_records[user_id].append(record)

            logger.info(f"AI generation consent granted for {user_id}: {[t.value for t in generation_types]}")
            return True

        except Exception as e:
            logger.error(f"Error granting AI generation consent: {e}")
            return False

    async def check_ai_generation_permission(self, user_id: str, generation_type: AIGenerationType) -> dict[str, Any]:
        """Check if user has granted permission for AI content generation"""
        if user_id not in self.ai_generation_settings:
            return {"allowed": False, "reason": "No AI generation consent found"}

        settings = self.ai_generation_settings[user_id]

        if generation_type.value not in settings.get("generation_types", []):
            return {
                "allowed": False,
                "reason": f"Generation type {generation_type.value} not consented",
            }

        return {
            "allowed": True,
            "ethical_checks_required": settings.get("ethical_checks_required", True),
            "openai_api_enabled": settings.get("openai_api_enabled", False),
        }

    async def get_comprehensive_consent_profile(self, user_id: str) -> dict[str, Any]:
        """Get complete consent profile for a user including all data sources and vendors"""
        profile = {
            "user_id": user_id,
            "consent_status": await self.get_consent_status(user_id),
            "data_sources": {},
            "vendors": {},
            "ai_generation": {},
            "restrictions": {},
        }

        # Data source permissions
        if user_id in self.data_source_permissions:
            for source in DataSource:
                profile["data_sources"][source.value] = self.data_source_permissions[user_id].get(source, False)

        # Vendor permissions
        if user_id in self.vendor_permissions:
            profile["vendors"] = self.vendor_permissions[user_id]

        # AI generation settings
        if user_id in self.ai_generation_settings:
            profile["ai_generation"] = self.ai_generation_settings[user_id]

        # Compile restrictions from all consent records
        if user_id in self.consent_records:
            for record in self.consent_records[user_id]:
                if record.is_valid() and record.restrictions:
                    profile["restrictions"].update(record.restrictions)

        return profile
