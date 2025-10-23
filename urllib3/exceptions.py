"""Minimal urllib3.exceptions stub for pytest warning filters."""

# ΛTAG: urllib3_stub


class NotOpenSSLWarning(Warning):
    """Placeholder warning emitted when OpenSSL support is unavailable."""


class InsecureRequestWarning(Warning):
    """Placeholder warning mirroring urllib3's interface."""


__all__ = ["NotOpenSSLWarning", "InsecureRequestWarning"]
