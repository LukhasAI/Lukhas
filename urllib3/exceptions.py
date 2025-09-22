"""Stub exceptions used by pytest warning filters."""

# ΛTAG: test_stub


class HTTPError(Exception):
    """Base HTTP error exception."""
    pass


class NotOpenSSLWarning(Warning):
    """Placeholder warning to satisfy pytest filters."""


class InsecureRequestWarning(Warning):
    """Placeholder insecure request warning."""
