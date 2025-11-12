"""OWASP Top 10 Security Test Suite.

Security testing for LUKHAS AI platform addressing OWASP Top 10 vulnerabilities (2021 edition).

## Current Test Coverage

**Phase 1: Security Principles** ✅ (17 tests - 100% passing)
- `test_owasp_principles.py` - Core OWASP security principles
  - A01: JWT signature verification, expiration, claims extraction
  - A05: Security headers, rate limiting, error messages
  - A07: Password policies, hashing, API key randomness, JWT algorithms
  - A09: Log structure, sensitive data exclusion, retention, event types

**Phase 2: Integration Tests** 🚧 (58+ tests - future work)
- `test_owasp_a01_access_control.py.future` - Full access control (15+ tests)
- `test_owasp_a05_security_misconfiguration.py.future` - Configuration (15+ tests)
- `test_owasp_a07_auth_failures.py.future` - Authentication (15+ tests)
- `test_owasp_a09_logging_failures.py.future` - Logging (13+ tests)

## Usage

    # Run current security tests
    pytest tests/security/test_owasp_principles.py -v

    # Run all security tests
    pytest tests/security/ -v

    # Run with coverage
    pytest tests/security/ --cov=lukhas --cov-report=html

## Related Documentation

- OWASP Top 10: https://owasp.org/Top10/
- Security Audit: docs/development/GPT5_AUDIT_IMPLEMENTATION_COMPLETE.md
- Test Documentation: tests/security/OWASP_SECURITY_TESTS.md
"""

__all__ = [
    "test_owasp_principles",
]
