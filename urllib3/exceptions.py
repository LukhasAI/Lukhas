"""Minimal urllib3.exceptions stub for pytest warning filters."""

# ΛTAG: urllib3_stub


class NotOpenSSLWarning(Warning):
    """Placeholder warning emitted when OpenSSL support is unavailable."""


class InsecureRequestWarning(Warning):
    """Placeholder warning mirroring urllib3's interface."""


class HTTPError(Exception):
    """Base HTTP exception class for urllib3 compatibility."""


class DependencyWarning(Warning):
    """Placeholder warning for urllib3 dependency issues."""


__all__ = ["HTTPError", "InsecureRequestWarning", "NotOpenSSLWarning", "DependencyWarning"]
