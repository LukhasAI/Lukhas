"""NIAS (Neuro-Introspective Audit System) for runtime request/response auditing.

NIAS provides lightweight, failure-safe audit logging for all API requests with:
- <2ms p50 overhead via async file I/O
- JSONL event stream for analytics and compliance
- Automatic drift score integration (when available)
- Privacy-safe metadata capture

See Also:
    - docs/nias/NIAS_PLAN.md - Architecture and design
    - docs/nias/EU_COMPLIANCE.md - GDPR/DSA compliance guidance
"""

from lukhas.guardian.nias.middleware import NIASMiddleware
from lukhas.guardian.nias.models import NIASAuditEvent

__all__ = ['NIASMiddleware', 'NIASAuditEvent']
