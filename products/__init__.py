"""LUKHAS AI Products Package.

Consolidated products organized by functional domain:

- intelligence/   - Analytics, monitoring, and tracking systems
- communication/  - Messaging, attention, and social systems  
- content/        - Content generation and creativity engines
- infrastructure/ - Core systems, legacy integration, and cloud platforms
- security/       - Security, privacy, and financial systems
- experience/     - Voice, UX, language, and visualization systems
- enterprise/     - Business-grade infrastructure and intelligence
- automation/     - AI agent frameworks and development tools
- shared/         - Common utilities and cross-product components

All lambda_core/ and lambda_products/ layers have been eliminated for simplicity.
"""

# Product category imports for easier access
from . import intelligence
from . import communication  
from . import content
from . import infrastructure
from . import security
from . import experience
from . import enterprise
from . import automation
from . import shared

__all__ = [
    'intelligence',
    'communication', 
    'content',
    'infrastructure',
    'security',
    'experience',
    'enterprise',
    'automation',
    'shared'
]
