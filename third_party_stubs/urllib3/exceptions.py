"""Stub exceptions module for urllib3."""


class NotOpenSSLWarning(Warning):
    """Placeholder warning to satisfy test configuration."""


class InsecureRequestWarning(Warning):
    """Placeholder warning for insecure request handling."""


class DependencyWarning(Warning):
    """Compatibility warning class expected by some libs."""


class HTTPError(Exception):
    """Base HTTP error used by callers importing from urllib3.exceptions."""


__all__ = ["NotOpenSSLWarning", "InsecureRequestWarning", "DependencyWarning", "HTTPError"]
