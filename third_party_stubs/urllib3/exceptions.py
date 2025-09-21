"""Stub exceptions module for urllib3."""

class NotOpenSSLWarning(Warning):
    """Placeholder warning to satisfy test configuration."""


class InsecureRequestWarning(Warning):
    """Placeholder warning for insecure request handling."""

__all__ = ["NotOpenSSLWarning", "InsecureRequestWarning"]
