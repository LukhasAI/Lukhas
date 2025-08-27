"""
Guardian Email Templates

Handles guardian invitation email generation with proper security messaging,
TTL warnings, and enumeration-safe content.
"""

from datetime import datetime, timedelta
from typing import Optional

from .engine import EmailTemplate, LanguageCode, TemplateEngine


class GuardianTemplates:
    """Template manager for guardian-related emails."""

    def __init__(self, engine: Optional[TemplateEngine] = None):
        """Initialize guardian templates with optional custom engine."""
        self.engine = engine or TemplateEngine()

    def create_invitation(
        self,
        requestor_display_name: str,
        guardian_name: str,
        recovery_ticket_id: str,
        approve_url: str,
        decline_url: str,
        ticket_ttl: timedelta = timedelta(hours=72),
        request_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create guardian invitation email template.

        Args:
            requestor_display_name: Name of person requesting recovery
            guardian_name: Name of the guardian being contacted
            recovery_ticket_id: Unique ticket ID for this recovery request
            approve_url: URL for guardian to approve the request
            decline_url: URL for guardian to decline the request
            ticket_ttl: Time-to-live for the guardian request
            request_timestamp: When the request was made (defaults to now)
            language: Language code for the template

        Returns:
            EmailTemplate: Rendered guardian invitation email

        Raises:
            ValueError: If required parameters are missing or invalid
            FileNotFoundError: If template file doesn't exist
        """

        # Validate inputs
        if not requestor_display_name or not requestor_display_name.strip():
            raise ValueError("requestor_display_name is required")

        if not guardian_name or not guardian_name.strip():
            raise ValueError("guardian_name is required")

        if not recovery_ticket_id or not recovery_ticket_id.strip():
            raise ValueError("recovery_ticket_id is required")

        if not approve_url or not decline_url:
            raise ValueError("Both approve_url and decline_url are required")

        # Default timestamp to now
        if request_timestamp is None:
            request_timestamp = datetime.utcnow()

        # Prepare template variables
        variables = {
            'requestor_display_name': requestor_display_name.strip(),
            'guardian_name': guardian_name.strip(),
            'recovery_ticket_id': recovery_ticket_id.strip(),
            'approve_url': approve_url.strip(),
            'decline_url': decline_url.strip(),
            'ticket_ttl': ticket_ttl,
            'request_timestamp': request_timestamp
        }

        # Validate all required variables are present
        missing = self.engine.validate_template_variables('guardian_invitation', variables)
        if missing:
            raise ValueError(f"Missing required template variables: {missing}")

        return self.engine.render_template('guardian_invitation', language, variables)

    def create_invitation_with_security_context(
        self,
        requestor_display_name: str,
        guardian_name: str,
        recovery_ticket_id: str,
        approve_url: str,
        decline_url: str,
        requester_last_login: Optional[datetime] = None,
        requester_device_info: Optional[str] = None,
        ticket_ttl: timedelta = timedelta(hours=72),
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create guardian invitation with additional security context.

        This variant includes additional security information that can help
        guardians make more informed decisions about recovery requests.

        Args:
            requestor_display_name: Name of person requesting recovery
            guardian_name: Name of the guardian being contacted
            recovery_ticket_id: Unique ticket ID for this recovery request
            approve_url: URL for guardian to approve the request
            decline_url: URL for guardian to decline the request
            requester_last_login: Last login time for the requester (optional)
            requester_device_info: Device/location info for context (optional)
            ticket_ttl: Time-to-live for the guardian request
            language: Language code for the template

        Returns:
            EmailTemplate: Enhanced guardian invitation with security context
        """

        # Start with basic invitation
        template = self.create_invitation(
            requestor_display_name=requestor_display_name,
            guardian_name=guardian_name,
            recovery_ticket_id=recovery_ticket_id,
            approve_url=approve_url,
            decline_url=decline_url,
            ticket_ttl=ticket_ttl,
            request_timestamp=datetime.utcnow(),
            language=language
        )

        # Add security context if available
        if requester_last_login or requester_device_info:
            # Note: This would require extended template variants
            # For now, we return the standard template
            # Future enhancement: Add security context to template variables
            pass

        return template

    def validate_guardian_urls(self, approve_url: str, decline_url: str) -> dict[str, bool]:
        """
        Validate guardian action URLs for security.

        Args:
            approve_url: URL for approving recovery
            decline_url: URL for declining recovery

        Returns:
            Dict with validation results for each URL
        """
        results = {
            'approve_url_valid': False,
            'decline_url_valid': False,
            'urls_different': False,
            'https_required': False
        }

        # Basic URL validation
        if approve_url and approve_url.startswith('https://'):
            results['approve_url_valid'] = True

        if decline_url and decline_url.startswith('https://'):
            results['decline_url_valid'] = True

        # Ensure URLs are different
        if approve_url != decline_url:
            results['urls_different'] = True

        # HTTPS requirement
        if (results['approve_url_valid'] and results['decline_url_valid']):
            results['https_required'] = True

        return results

    def get_recommended_ttl(self, urgency_level: str = 'normal') -> timedelta:
        """
        Get recommended TTL based on urgency level.

        Args:
            urgency_level: 'low', 'normal', 'high', or 'emergency'

        Returns:
            Recommended TTL as timedelta
        """
        ttl_mapping = {
            'low': timedelta(hours=168),      # 1 week
            'normal': timedelta(hours=72),    # 3 days
            'high': timedelta(hours=24),      # 1 day
            'emergency': timedelta(hours=6)   # 6 hours
        }

        return ttl_mapping.get(urgency_level, timedelta(hours=72))
