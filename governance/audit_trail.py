"""Bridge module for governance.audit_trail → labs.governance.audit_trail"""
from __future__ import annotations

from labs.governance.audit_trail import AuditEntry, AuditLevel, DecisionType

__all__ = ["AuditEntry", "AuditLevel", "DecisionType"]
