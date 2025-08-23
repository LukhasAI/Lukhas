"""
Recovery Email Templates

Handles account recovery email generation including started, approved, 
and denied notifications with proper security messaging and enumeration-safe content.
"""

from typing import Dict, Union, Optional, List
from datetime import datetime, timedelta
from .engine import TemplateEngine, LanguageCode, EmailTemplate

class RecoveryTemplates:
    """Template manager for account recovery emails."""
    
    def __init__(self, engine: Optional[TemplateEngine] = None):
        """Initialize recovery templates with optional custom engine."""
        self.engine = engine or TemplateEngine()
    
    def create_started_notification(
        self,
        user_display_name: str,
        recovery_ticket_id: str,
        guardian_count: int,
        required_approvals: int,
        request_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create recovery started notification email.
        
        Args:
            user_display_name: Display name of the user requesting recovery
            recovery_ticket_id: Unique identifier for the recovery request
            guardian_count: Total number of guardians notified
            required_approvals: Number of approvals needed to proceed
            request_timestamp: When recovery was initiated (defaults to now)
            language: Language code for the template
            
        Returns:
            EmailTemplate: Recovery started notification email
        """
        
        # Validate inputs
        if not user_display_name or not user_display_name.strip():
            raise ValueError("user_display_name is required")
            
        if not recovery_ticket_id or not recovery_ticket_id.strip():
            raise ValueError("recovery_ticket_id is required")
            
        if guardian_count <= 0:
            raise ValueError("guardian_count must be positive")
            
        if required_approvals <= 0 or required_approvals > guardian_count:
            raise ValueError("required_approvals must be positive and <= guardian_count")
            
        # Default timestamp to now
        if request_timestamp is None:
            request_timestamp = datetime.utcnow()
            
        # Prepare template variables
        variables = {
            'user_display_name': user_display_name.strip(),
            'recovery_ticket_id': recovery_ticket_id.strip(),
            'guardian_count': guardian_count,
            'required_approvals': required_approvals,
            'request_timestamp': request_timestamp
        }
        
        return self.engine.render_template('recovery_started', language, variables)
    
    def create_approved_notification(
        self,
        user_display_name: str,
        session_url: str,
        session_ttl: timedelta = timedelta(hours=1),
        request_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create recovery approved notification with ephemeral session access.
        
        Args:
            user_display_name: Display name of the user
            session_url: URL for temporary recovery session access
            session_ttl: Time-to-live for the recovery session
            request_timestamp: When recovery was approved (defaults to now)
            language: Language code for the template
            
        Returns:
            EmailTemplate: Recovery approved notification email
        """
        
        # Validate inputs
        if not user_display_name or not user_display_name.strip():
            raise ValueError("user_display_name is required")
            
        if not session_url or not session_url.strip():
            raise ValueError("session_url is required")
            
        if not session_url.startswith('https://'):
            raise ValueError("session_url must use HTTPS")
            
        # Default timestamp to now
        if request_timestamp is None:
            request_timestamp = datetime.utcnow()
            
        # Prepare template variables
        variables = {
            'user_display_name': user_display_name.strip(),
            'session_url': session_url.strip(),
            'session_ttl': session_ttl,
            'request_timestamp': request_timestamp
        }
        
        return self.engine.render_template('recovery_approved', language, variables)
    
    def create_denied_notification(
        self,
        user_display_name: str,
        denial_reason: str,
        request_timestamp: Optional[datetime] = None,
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create recovery denied notification email.
        
        Args:
            user_display_name: Display name of the user
            denial_reason: Reason for denial (enumeration-safe)
            request_timestamp: When recovery was denied (defaults to now)
            language: Language code for the template
            
        Returns:
            EmailTemplate: Recovery denied notification email
        """
        
        # Validate inputs
        if not user_display_name or not user_display_name.strip():
            raise ValueError("user_display_name is required")
            
        if not denial_reason or not denial_reason.strip():
            raise ValueError("denial_reason is required")
            
        # Default timestamp to now
        if request_timestamp is None:
            request_timestamp = datetime.utcnow()
            
        # Prepare template variables  
        variables = {
            'user_display_name': user_display_name.strip(),
            'denial_reason': denial_reason.strip(),
            'request_timestamp': request_timestamp
        }
        
        return self.engine.render_template('recovery_denied', language, variables)
    
    def get_enumeration_safe_denial_reasons(self, language: LanguageCode = 'en') -> List[str]:
        """
        Get list of enumeration-safe denial reasons.
        
        These reasons don't reveal specific information about the account
        or recovery process that could be used for reconnaissance.
        
        Args:
            language: Language code for localized reasons
            
        Returns:
            List of safe denial reason strings
        """
        
        if language == 'es':
            return [
                "Aprobaciones insuficientes recibidas",
                "Solicitud expiró antes de completarse",
                "Los guardianes no respondieron a tiempo",
                "Solicitud de recuperación cancelada",
                "Error de validación en el proceso de recuperación"
            ]
        else:  # English default
            return [
                "Insufficient approvals received",
                "Request expired before completion", 
                "Guardians did not respond in time",
                "Recovery request was cancelled",
                "Validation error in recovery process"
            ]
    
    def validate_session_url(self, session_url: str) -> Dict[str, bool]:
        """
        Validate recovery session URL for security requirements.
        
        Args:
            session_url: URL to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'https_required': False,
            'valid_format': False,
            'contains_token': False,
            'reasonable_length': False
        }
        
        if session_url:
            # Must use HTTPS
            if session_url.startswith('https://'):
                results['https_required'] = True
                
            # Basic URL format
            if '://' in session_url and '.' in session_url:
                results['valid_format'] = True
                
            # Should contain some form of token/identifier
            if any(char in session_url for char in ['=', '&', '?', '/', '-']):
                results['contains_token'] = True
                
            # Reasonable length (not too short or suspiciously long)
            if 20 <= len(session_url) <= 500:
                results['reasonable_length'] = True
                
        return results
    
    def get_recommended_session_ttl(self, security_level: str = 'standard') -> timedelta:
        """
        Get recommended session TTL based on security requirements.
        
        Args:
            security_level: 'low', 'standard', 'high', or 'maximum'
            
        Returns:
            Recommended session TTL as timedelta
        """
        ttl_mapping = {
            'low': timedelta(hours=4),        # 4 hours
            'standard': timedelta(hours=1),   # 1 hour (default)
            'high': timedelta(minutes=30),    # 30 minutes
            'maximum': timedelta(minutes=15)  # 15 minutes
        }
        
        return ttl_mapping.get(security_level, timedelta(hours=1))
    
    def create_recovery_progress_update(
        self,
        user_display_name: str,
        recovery_ticket_id: str,
        approvals_received: int,
        approvals_required: int,
        guardians_remaining: List[str],
        language: LanguageCode = 'en'
    ) -> EmailTemplate:
        """
        Create progress update email during recovery process.
        
        Args:
            user_display_name: Display name of the user
            recovery_ticket_id: Recovery ticket identifier
            approvals_received: Number of approvals received so far
            approvals_required: Total number of approvals needed
            guardians_remaining: List of guardian names who haven't responded
            language: Language code for the template
            
        Returns:
            EmailTemplate: Recovery progress update email
            
        Note:
            This would require a separate template file for progress updates.
            Currently returns a basic started notification as placeholder.
        """
        
        # For now, return a started notification
        # This would be expanded with a dedicated progress template
        return self.create_started_notification(
            user_display_name=user_display_name,
            recovery_ticket_id=recovery_ticket_id,
            guardian_count=len(guardians_remaining) + approvals_received,
            required_approvals=approvals_required,
            language=language
        )