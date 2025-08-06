#!/usr/bin/env python3
"""
NIΛS Consent Manager - Comprehensive consent validation and management
Part of the Lambda Products Suite by LUKHAS AI
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .nias_core import ConsentLevel, MessageTier

logger = logging.getLogger("Lambda.NIΛS.Consent")

class ConsentScope(Enum):
    """Different scopes of consent"""
    GLOBAL = "global"           # Overall system consent
    CONTENT_TYPE = "content_type"  # Specific content categories
    TEMPORAL = "temporal"       # Time-based consent
    EMOTIONAL = "emotional"     # Emotional state-based
    CONTEXTUAL = "contextual"   # Situational consent

@dataclass
class ConsentRecord:
    """Individual consent record"""
    user_id: str
    scope: ConsentScope
    level: ConsentLevel
    granted_at: datetime
    expires_at: Optional[datetime] = None
    context: Dict[str, Any] = None
    revocable: bool = True
    audit_trail: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.audit_trail is None:
            self.audit_trail = []

    def is_valid(self) -> bool:
        """Check if consent record is still valid"""
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True

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
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.consent_records: Dict[str, List[ConsentRecord]] = {}
        self.consent_templates: Dict[str, Dict] = {}
        self.privacy_settings: Dict[str, Dict] = {}
        
        logger.info("NIΛS Consent Manager initialized")
    
    def _default_config(self) -> Dict:
        """Default consent manager configuration"""
        return {
            "default_expiry_hours": 8760,  # 1 year
            "require_explicit_consent": True,
            "enable_consent_withdrawal": True,
            "audit_all_changes": True,
            "gdpr_compliance": True,
            "ccpa_compliance": True
        }
    
    async def grant_consent(self, user_id: str, scope: ConsentScope, 
                           level: ConsentLevel, context: Optional[Dict] = None,
                           duration_hours: Optional[int] = None) -> bool:
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
                expires_at = datetime.now() + timedelta(hours=duration_hours)
            elif self.config["default_expiry_hours"]:
                expires_at = datetime.now() + timedelta(hours=self.config["default_expiry_hours"])
            
            # Create consent record
            record = ConsentRecord(
                user_id=user_id,
                scope=scope,
                level=level,
                granted_at=datetime.now(),
                expires_at=expires_at,
                context=context or {}
            )
            
            # Add audit entry
            record.audit_trail.append({
                "action": "granted",
                "timestamp": datetime.now().isoformat(),
                "level": level.value,
                "context": context or {}
            })
            
            # Store record
            if user_id not in self.consent_records:
                self.consent_records[user_id] = []
            
            # Remove any existing consent for this scope
            self.consent_records[user_id] = [
                r for r in self.consent_records[user_id] 
                if r.scope != scope
            ]
            
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
                    record.audit_trail.append({
                        "action": "revoked",
                        "timestamp": datetime.now().isoformat(),
                        "reason": "user_request"
                    })
            
            # Remove consent records for this scope
            self.consent_records[user_id] = [
                r for r in self.consent_records[user_id] 
                if r.scope != scope
            ]
            
            logger.info(f"Consent revoked: {user_id} - {scope.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking consent: {e}")
            return False
    
    async def validate_consent(self, user_id: str, required_level: ConsentLevel,
                              scope: ConsentScope = ConsentScope.GLOBAL,
                              context: Optional[Dict] = None) -> Dict[str, Any]:
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
                    "required_level": required_level
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
                    "scope": scope.value
                }
            
            # Check consent level hierarchy
            level_hierarchy = {
                ConsentLevel.NONE: 0,
                ConsentLevel.BASIC: 1,
                ConsentLevel.ENHANCED: 2,
                ConsentLevel.FULL_SYMBOLIC: 3,
                ConsentLevel.DREAM_AWARE: 4
            }
            
            current_level_value = level_hierarchy[matching_record.level]
            required_level_value = level_hierarchy[required_level]
            
            if current_level_value >= required_level_value:
                # Additional contextual validation
                if context:
                    contextual_valid = await self._validate_contextual_consent(
                        matching_record, context
                    )
                    if not contextual_valid["valid"]:
                        return contextual_valid
                
                return {
                    "valid": True,
                    "reason": "Sufficient consent level",
                    "current_level": matching_record.level,
                    "required_level": required_level,
                    "granted_at": matching_record.granted_at.isoformat(),
                    "expires_at": matching_record.expires_at.isoformat() if matching_record.expires_at else None
                }
            else:
                return {
                    "valid": False,
                    "reason": "Insufficient consent level",
                    "current_level": matching_record.level,
                    "required_level": required_level,
                    "scope": scope.value
                }
                
        except Exception as e:
            logger.error(f"Error validating consent: {e}")
            return {
                "valid": False,
                "reason": f"Validation error: {str(e)}",
                "current_level": ConsentLevel.NONE,
                "required_level": required_level
            }
    
    async def _validate_contextual_consent(self, record: ConsentRecord, 
                                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contextual consent requirements"""
        # Check if consent context matches current context
        consent_context = record.context
        
        # Time-based consent
        if "time_restrictions" in consent_context:
            current_hour = datetime.now().hour
            allowed_hours = consent_context["time_restrictions"].get("hours", [])
            if allowed_hours and current_hour not in allowed_hours:
                return {
                    "valid": False,
                    "reason": "Outside allowed time window for consent",
                    "current_hour": current_hour,
                    "allowed_hours": allowed_hours
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
                    "allowed_types": allowed_types
                }
        
        # Emotional state restrictions
        if "emotional_states" in consent_context:
            current_emotional_state = context.get("emotional_state")
            blocked_states = consent_context["emotional_states"].get("blocked", [])
            if current_emotional_state in blocked_states:
                return {
                    "valid": False,
                    "reason": "Consent blocked for current emotional state",
                    "emotional_state": current_emotional_state
                }
        
        return {"valid": True, "reason": "Contextual consent validated"}
    
    async def get_consent_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive consent status for a user"""
        user_records = self.consent_records.get(user_id, [])
        
        if not user_records:
            return {
                "user_id": user_id,
                "has_consent": False,
                "active_consents": [],
                "expired_consents": []
            }
        
        active_consents = []
        expired_consents = []
        
        for record in user_records:
            consent_info = {
                "scope": record.scope.value,
                "level": record.level.value,
                "granted_at": record.granted_at.isoformat(),
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
                "context": record.context
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
            "last_updated": max(r.granted_at for r in user_records).isoformat() if user_records else None
        }
    
    async def create_consent_template(self, template_name: str, 
                                    template_config: Dict[str, Any]):
        """Create a reusable consent template"""
        self.consent_templates[template_name] = template_config
        logger.info(f"Created consent template: {template_name}")
    
    async def apply_consent_template(self, user_id: str, template_name: str,
                                   overrides: Optional[Dict] = None) -> bool:
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
    
    def export_consent_data(self, user_id: str) -> Dict[str, Any]:
        """Export all consent data for a user (GDPR compliance)"""
        user_records = self.consent_records.get(user_id, [])
        
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "consent_records": []
        }
        
        for record in user_records:
            export_data["consent_records"].append({
                "scope": record.scope.value,
                "level": record.level.value,
                "granted_at": record.granted_at.isoformat(),
                "expires_at": record.expires_at.isoformat() if record.expires_at else None,
                "context": record.context,
                "revocable": record.revocable,
                "audit_trail": record.audit_trail,
                "is_valid": record.is_valid()
            })
        
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
    
    def get_system_metrics(self) -> Dict[str, Any]:
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
            "ccpa_compliance": self.config["ccpa_compliance"]
        }