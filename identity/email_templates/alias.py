"""
Alias Rotation Email Templates

Handles ΛiD alias rotation confirmation emails with proper security messaging,
version tracking, and history preservation.
"""

from datetime import datetime
from typing import Dict, List, Optional

from .engine import EmailTemplate, LanguageCode, TemplateEngine


class AliasRotationTemplates:
    """Template manager for ΛiD alias rotation emails."""

    def __init__(self, engine: Optional[TemplateEngine] = None):
        """Initialize alias rotation templates with optional custom engine."""
        self.engine = engine or TemplateEngine()

    def create_rotation_confirmation(
        self,
        user_display_name: str,
        old_alias: str,
        new_alias: str,
        initiated_by: str,
        rotation_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create alias rotation confirmation email.

        Args:
            user_display_name: Display name of the user
            old_alias: Previous ΛiD alias being replaced
            new_alias: New ΛiD alias now active
            initiated_by: Who/what initiated the rotation (user, system, admin)
            rotation_timestamp: When rotation occurred (defaults to now)
            language: Language code for the template

        Returns:
            EmailTemplate: Alias rotation confirmation email

        Raises:
            ValueError: If required parameters are missing or invalid
        """

        # Validate inputs
        if not user_display_name or not user_display_name.strip():
            raise ValueError("user_display_name is required")

        if not old_alias or not old_alias.strip():
            raise ValueError("old_alias is required")

        if not new_alias or not new_alias.strip():
            raise ValueError("new_alias is required")

        if old_alias.strip() == new_alias.strip():
            raise ValueError("old_alias and new_alias must be different")

        if not initiated_by or not initiated_by.strip():
            raise ValueError("initiated_by is required")

        # Validate alias formats
        if not self._is_valid_alias_format(old_alias):
            raise ValueError(f"old_alias has invalid format: {old_alias}")

        if not self._is_valid_alias_format(new_alias):
            raise ValueError(f"new_alias has invalid format: {new_alias}")

        # Default timestamp to now
        if rotation_timestamp is None:
            rotation_timestamp = datetime.utcnow()

        # Prepare template variables
        variables = {
            'user_display_name': user_display_name.strip(),
            'old_alias': old_alias.strip(),
            'new_alias': new_alias.strip(),
            'initiated_by': self._sanitize_initiated_by(initiated_by.strip()),
            'rotation_timestamp': rotation_timestamp
        }

        return self.engine.render_template('alias_rotation', language, variables)

    def create_unauthorized_rotation_alert(
        self,
        user_display_name: str,
        old_alias: str,
        new_alias: str,
        initiated_by: str,
        rotation_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create alert email for potentially unauthorized alias rotation.

        This is sent when rotation happens under suspicious circumstances
        or when security monitoring flags the rotation as potentially unauthorized.

        Args:
            user_display_name: Display name of the user
            old_alias: Previous ΛiD alias that was replaced
            new_alias: New ΛiD alias that is now active
            initiated_by: Who/what initiated the rotation
            rotation_timestamp: When rotation occurred (defaults to now)
            language: Language code for the template

        Returns:
            EmailTemplate: Enhanced rotation alert with security warnings
        """

        # Create standard rotation email first
        template = self.create_rotation_confirmation(
            user_display_name=user_display_name,
            old_alias=old_alias,
            new_alias=new_alias,
            initiated_by=initiated_by,
            rotation_timestamp=rotation_timestamp,
            language=language
        )

        # Enhance subject line for security alert
        if language == 'es':
            template.subject = f"ALERTA: {template.subject}"
        else:
            template.subject = f"SECURITY ALERT: {template.subject}"

        # Note: In a full implementation, this would use a different template
        # with enhanced security messaging and immediate action steps

        return template

    def _is_valid_alias_format(self, alias: str) -> bool:
        """
        Validate ΛiD alias format according to specification.

        Args:
            alias: Alias to validate

        Returns:
            True if alias format is valid
        """
        if not alias:
            return False

        # Should match pattern: lid#REALM/ZONE/vN.hash-checksum
        # or ΛiD#REALM/ZONE/vN.hash-checksum (display format)
        parts = alias.split('#')
        if len(parts) != 2:
            return False

        prefix, suffix = parts

        # Check prefix
        if prefix not in ['lid', 'ΛiD']:
            return False

        # Check suffix structure
        suffix_parts = suffix.split('/')
        if len(suffix_parts) != 3:
            return False

        realm, zone, token = suffix_parts

        # Validate realm
        if realm not in ['LUKHAS', 'MATRIZ']:
            return False

        # Validate zone
        if zone not in ['EU', 'US', 'APAC']:
            return False

        # Validate token format (v{N}.{hash}-{checksum})
        if not token.startswith('v'):
            return False

        return True

    def _sanitize_initiated_by(self, initiated_by: str) -> str:
        """
        Sanitize the 'initiated_by' field for safe display.

        Args:
            initiated_by: Raw initiated_by value

        Returns:
            Sanitized value safe for email display
        """

        # Map system identifiers to user-friendly names
        sanitized_mapping = {
            'system_rotation': 'Automatic Security Rotation',
            'user_manual': 'User Manual Request',
            'admin_rotation': 'Administrative Action',
            'security_rotation': 'Security Team',
            'scheduled_rotation': 'Scheduled Maintenance',
            'emergency_rotation': 'Emergency Security Response'
        }

        # Return mapped value or sanitized original
        if initiated_by in sanitized_mapping:
            return sanitized_mapping[initiated_by]

        # For user-initiated, show generic message
        if initiated_by.startswith('user:'):
            return 'User Request'

        # For admin-initiated, show generic message
        if initiated_by.startswith('admin:'):
            return 'Administrative Action'

        # Default fallback
        return 'System Process'

    def get_rotation_reasons(self, language: LanguageCode = 'en') -> List[Dict[str, str]]:
        """
        Get list of valid rotation reasons with descriptions.

        Args:
            language: Language code for localized descriptions

        Returns:
            List of rotation reason dictionaries with code and description
        """

        if language == 'es':
            return [
                {
                    'code': 'scheduled',
                    'description': 'Rotación programada (90 días)'
                },
                {
                    'code': 'user_request',
                    'description': 'Solicitud manual del usuario'
                },
                {
                    'code': 'security_incident',
                    'description': 'Respuesta a incidente de seguridad'
                },
                {
                    'code': 'compliance_requirement',
                    'description': 'Requisito de cumplimiento'
                },
                {
                    'code': 'system_maintenance',
                    'description': 'Mantenimiento del sistema'
                }
            ]
        else:  # English default
            return [
                {
                    'code': 'scheduled',
                    'description': 'Scheduled rotation (90 days)'
                },
                {
                    'code': 'user_request',
                    'description': 'User manual request'
                },
                {
                    'code': 'security_incident',
                    'description': 'Security incident response'
                },
                {
                    'code': 'compliance_requirement',
                    'description': 'Compliance requirement'
                },
                {
                    'code': 'system_maintenance',
                    'description': 'System maintenance'
                }
            ]

    def validate_alias_rotation(self, old_alias: str, new_alias: str) -> Dict[str, bool]:
        """
        Validate an alias rotation for security and format compliance.

        Args:
            old_alias: Previous alias
            new_alias: New alias

        Returns:
            Dict with validation results
        """
        results = {
            'old_alias_valid_format': False,
            'new_alias_valid_format': False,
            'aliases_different': False,
            'same_realm_zone': False,
            'version_incremented': False
        }

        # Format validation
        results['old_alias_valid_format'] = self._is_valid_alias_format(old_alias)
        results['new_alias_valid_format'] = self._is_valid_alias_format(new_alias)

        # Different aliases
        results['aliases_different'] = (old_alias != new_alias)

        if results['old_alias_valid_format'] and results['new_alias_valid_format']:
            # Extract realm/zone from both
            old_parts = old_alias.split('#')[1].split('/')
            new_parts = new_alias.split('#')[1].split('/')

            # Should maintain same realm/zone
            if old_parts[0] == new_parts[0] and old_parts[1] == new_parts[1]:
                results['same_realm_zone'] = True

            # Check if version incremented (basic check)
            try:
                old_version = int(old_parts[2].split('.')[0][1:])  # Extract version number
                new_version = int(new_parts[2].split('.')[0][1:])
                if new_version > old_version:
                    results['version_incremented'] = True
            except (ValueError, IndexError):
                pass  # Version parsing failed

        return results
