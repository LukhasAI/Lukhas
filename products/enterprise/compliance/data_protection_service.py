"""Compatibility wrapper for enterprise compliance service.

This module re-exports the core data protection implementation so legacy
import paths continue to function without duplicating logic."""

from products.enterprise.core.compliance.data_protection_service import *  # noqa: F401,F403

# ΛTAG: compliance_reexport -- ensure enterprise compliance modules share one implementation
