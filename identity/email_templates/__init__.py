"""
LUKHAS AI Identity Email Templates

Comprehensive email template system for identity operations including:
- Guardian invitations and responses
- Account recovery workflows
- Alias rotation confirmations
- Security notifications

Templates support:
- Multiple languages (EN/ES)
- Plain text and HTML formats
- Accessibility compliance (WCAG 2.1 AA)
- LUKHAS branding standards
"""

from .alias import AliasRotationTemplates
from .engine import TemplateEngine
from .guardian import GuardianTemplates
from .recovery import RecoveryTemplates

__all__ = [
    'TemplateEngine',
    'GuardianTemplates',
    'RecoveryTemplates',
    'AliasRotationTemplates'
]

__version__ = '1.0.0'
