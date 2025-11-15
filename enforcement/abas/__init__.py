"""ABAS (Ad-Based Abuse Shield) enforcement module.

This module provides OPA-based policy enforcement for ad serving endpoints,
with PII detection, TCF v2.2 consent validation, and EU compliance checks.
"""

from enforcement.abas.middleware import ABASMiddleware

__all__ = ["ABASMiddleware"]
