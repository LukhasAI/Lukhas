from __future__ import annotations

import os
from typing import Any

from lukhas.observability.matriz_decorators import instrument

# Feature flag for gradual rollout
CONSENT_LEDGER_ACTIVE = os.environ.get("CONSENT_LEDGER_ACTIVE", "false").lower() == "true"

# Conditional import of real implementation
_ledger_instance = None
if CONSENT_LEDGER_ACTIVE:
    try:
        from lukhas.governance.consent_ledger_impl import ConsentLedger

        _ledger_instance = ConsentLedger()
    except ImportError:
        pass


@instrument("AWARENESS", label="governance:consent", capability="consent:record")
def record_consent(event: dict[str, Any], *, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    """Record consent with optional real implementation"""
    _ = kwargs
    if "subject" not in event or "scopes" not in event:
        return {"ok": False, "reason": "invalid_event"}

    if mode != "dry_run" and CONSENT_LEDGER_ACTIVE and _ledger_instance:
        # Use real implementation
        try:
            result = _ledger_instance.record_consent(
                subject_id=event["subject"],
                data_controller=event.get("controller", "lukhas"),
                purpose=event.get("purpose", "processing"),
                scopes=event["scopes"],
                consent_type=event.get("type", "explicit"),
                metadata=event.get("metadata", {}),
            )
            return {"ok": True, "status": "recorded", "consent_id": result.consent_id}
        except Exception as e:
            return {"ok": False, "reason": str(e)}

    return {"ok": True, "status": "recorded(dry_run)"}


@instrument("AWARENESS", label="governance:verify", capability="consent:verify")
def verify_consent(subject: str, scope: str, *, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    """Verify consent status"""
    _ = kwargs
    if mode != "dry_run" and CONSENT_LEDGER_ACTIVE and _ledger_instance:
        try:
            result = _ledger_instance.verify_consent(
                subject_id=subject,
                data_controller=kwargs.get("controller", "lukhas"),
                purpose=kwargs.get("purpose", "processing"),
                scopes=[scope],
            )
            return {"ok": result.verdict == "allow", "verdict": result.verdict}
        except Exception as e:
            return {"ok": False, "reason": str(e)}

    return {"ok": True, "verdict": "allow(dry_run)"}


@instrument("DECISION", label="governance:withdraw", capability="consent:withdraw")
def withdraw_consent(consent_id: str, *, mode: str = "dry_run", **kwargs) -> dict[str, Any]:
    """Withdraw consent (GDPR Article 7.3)"""
    _ = kwargs
    if mode != "dry_run" and CONSENT_LEDGER_ACTIVE and _ledger_instance:
        try:
            success = _ledger_instance.withdraw_consent(
                consent_id=consent_id, reason=kwargs.get("reason", "user_request")
            )
            return {"ok": success, "status": "withdrawn" if success else "failed"}
        except Exception as e:
            return {"ok": False, "reason": str(e)}

    return {"ok": True, "status": "withdrawn(dry_run)"}