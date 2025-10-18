#!/usr/bin/env python3
"""
Guardian Exemption Ledger Emitter
=================================

Emits non-ALLOW decisions and overrides to append-only ledger.
Provides dual-approval tracking for critical overrides.

Part of Task 13: Safety Tags System
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def _normalize_consent_timestamp(value: Optional[Union[str, datetime]]) -> Optional[str]:
    """Normalize consent timestamps to ISO-8601 strings."""

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()

    return value


def emit_exemption(db, rec: Dict[str, Any]) -> None:
    """
    Insert into Postgres if available; otherwise no-op.
    Expect keys matching the SQL/JSON schema above.

    Args:
        db: Database connection (psycopg or similar)
        rec: Record dictionary with exemption details
    """
    rec.setdefault("created_at", datetime.now(timezone.utc).isoformat())

    # Example using psycopg (adapt to your db wrapper):
    if db is None:
        return

    db.execute(
        """
        INSERT INTO guardian_exemptions(
          plan_id, tenant, env, lambda_id, action, rule_name, tags, confidences, band,
          user_consent_timestamp, consent_method,
          purpose, retention_days, justification, override_requested, override_granted,
          approver1_id, approver2_id, created_at
        ) VALUES (
          %(plan_id)s, %(tenant)s, %(env)s, %(lambda_id)s, %(action)s, %(rule_name)s,
          %(tags)s, %(confidences)s, %(band)s,
          %(user_consent_timestamp)s, %(consent_method)s,
          %(purpose)s, %(retention_days)s,
          %(justification)s, %(override_requested)s, %(override_granted)s,
          %(approver1_id)s, %(approver2_id)s, %(created_at)s
        )
        """,
        {
          **rec,
          "tags": json.dumps(rec.get("tags", [])),
          "confidences": json.dumps(rec.get("confidences", {})),
          "user_consent_timestamp": _normalize_consent_timestamp(rec.get("user_consent_timestamp")),
        },
    )


def validate_dual_approval(
    approver1_id: str,
    approver2_id: str,
    get_tier_fn: callable
) -> bool:
    """
    Validate dual-approval for critical overrides.

    Args:
        approver1_id: First approver's ΛiD
        approver2_id: Second approver's ΛiD
        get_tier_fn: Function to get approver tier level

    Returns:
        bool: True if valid dual-approval

    Raises:
        ValueError: If same approver used twice
        PermissionError: If approvers not T4+
    """
    if approver1_id == approver2_id:
        raise ValueError("Dual approval requires different approvers")

    # Verify approver tiers (T4+ required for critical)
    tier1 = get_tier_fn(approver1_id)
    tier2 = get_tier_fn(approver2_id)

    if tier1 < 4 or tier2 < 4:
        raise PermissionError(f"Critical overrides require T4+ approvers (got T{tier1}, T{tier2})")

    return True


def emit_guardian_decision(
    db,
    plan_id: str,
    lambda_id: str,
    action: str,
    rule_name: str,
    tags: List[str],
    confidences: Dict[str, float],
    band: str,
    tenant: str = "default",
    env: str = "prod",
    purpose: Optional[str] = None,
    retention_days: Optional[int] = None,
    justification: Optional[str] = None,
    override_requested: bool = False,
    override_granted: bool = False,
    approver1_id: Optional[str] = None,
    approver2_id: Optional[str] = None,
    user_consent_timestamp: Optional[Union[str, datetime]] = None,
    consent_method: Optional[str] = None
) -> None:
    """
    Convenience wrapper to emit guardian decisions.

    Args:
        db: Database connection
        plan_id: Unique plan identifier
        lambda_id: ΛiD of the actor
        action: Guardian action (allow/warn/require_human/block)
        rule_name: Name of the rule that triggered
        tags: List of safety tags detected
        confidences: Tag confidence scores
        band: Risk band (minor/major/high/critical)
        tenant: Tenant identifier
        env: Environment (prod/staging/dev)
        purpose: Declared purpose of operation
        retention_days: Data retention period
        justification: Free-text justification
        override_requested: Whether override was requested
        override_granted: Whether override was approved
        approver1_id: First approver's ΛiD (for overrides)
        approver2_id: Second approver's ΛiD (for critical overrides)
    """

    # Enforce consent for financial/PII operations
    requires_consent = any(tag.lower() in {"financial", "pii"} for tag in tags)
    if requires_consent and (user_consent_timestamp is None or not consent_method):
        raise ValueError("Consent evidence required for FINANCIAL/PII operations")

    # Build exemption record
    record = {
        "plan_id": plan_id,
        "tenant": tenant,
        "env": env,
        "lambda_id": lambda_id,
        "action": action,
        "rule_name": rule_name,
        "tags": tags,
        "confidences": confidences,
        "band": band,
        "purpose": purpose,
        "retention_days": retention_days,
        "justification": justification,
        "override_requested": override_requested,
        "override_granted": override_granted,
        "approver1_id": approver1_id,
        "approver2_id": approver2_id,
        "user_consent_timestamp": _normalize_consent_timestamp(user_consent_timestamp),
        "consent_method": consent_method,
    }

    if requires_consent:
        # # ΛTAG: consent_guardrail
        record.setdefault("consent_method", consent_method)

    # # ΛTAG: consent_tracking

    # Emit to ledger
    emit_exemption(db, record)


def redact_pii_for_exemplars(data: Any) -> Any:
    """
    Redact PII from data for safe exemplar emission.

    Args:
        data: Data structure to redact

    Returns:
        Redacted copy of data
    """
    if isinstance(data, str):
        # Redact emails
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                     lambda m: f"email_{hashlib.md5(m.group().encode()).hexdigest()[:8]}", data)

        # Redact phone numbers
        data = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                     lambda m: f"phone_{hashlib.md5(m.group().encode()).hexdigest()[:8]}", data)

        # Redact SSNs
        data = re.sub(r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',
                     lambda m: f"ssn_{hashlib.md5(m.group().encode()).hexdigest()[:8]}", data)

        # Redact credit card numbers
        data = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                     lambda m: f"cc_{hashlib.md5(m.group().encode()).hexdigest()[:8]}", data)

        return data

    elif isinstance(data, dict):
        return {k: redact_pii_for_exemplars(v) for k, v in data.items()}

    elif isinstance(data, list):
        return [redact_pii_for_exemplars(item) for item in data]

    else:
        return data


def emit_guardian_action_with_exemplar(
    action: str,
    lane: str,
    plan: Dict[str, Any],
    trace_id: Optional[str] = None,
    confidence_scores: Optional[Dict[str, float]] = None,
    emit_to_prometheus: bool = True
) -> None:
    """
    Emit Guardian action with redacted exemplar for drill-down.

    Args:
        action: Guardian action (allow/warn/require_human/block)
        lane: A/B test lane (candidate/control)
        plan: Original plan (will be redacted)
        trace_id: Optional trace ID for correlation
        confidence_scores: Tag confidence scores
        emit_to_prometheus: Whether to emit to Prometheus
    """
    if not emit_to_prometheus:
        return

    try:
        # Import here to avoid circular dependency
        from core.ethics.safety_tags import GUARDIAN_ACTIONS_EXEMPLARS, METRICS_AVAILABLE

        if not METRICS_AVAILABLE:
            return

        # Redact PII from plan
        redacted_plan = redact_pii_for_exemplars(plan)

        # Create exemplar data
        exemplar_data = {
            "plan_summary": str(redacted_plan)[:200],  # Truncate for storage efficiency
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence_scores": confidence_scores or {},
        }

        if trace_id:
            exemplar_data["trace_id"] = trace_id

        # Emit with exemplar
        metric = GUARDIAN_ACTIONS_EXEMPLARS.labels(action=action, lane=lane)

        # Add exemplar if supported (Prometheus client v0.14+)
        if hasattr(metric, '_exemplar'):
            metric.inc(exemplar={"trace_id": trace_id or "none", "data": json.dumps(exemplar_data)})
        else:
            # Fallback for older clients
            metric.inc()

    except Exception as e:
        # Don't fail the main operation due to metrics errors
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to emit exemplar for action {action}: {e}")


def emit_confidence_metrics(
    tags: List[Dict[str, Any]],
    lane: str = "unknown"
) -> None:
    """
    Emit confidence metrics for detected tags.

    Args:
        tags: List of detected tags with confidence scores
        lane: A/B test lane
    """
    try:
        from core.ethics.safety_tags import METRICS_AVAILABLE, SAFETY_TAGS_CONFIDENCE

        if not METRICS_AVAILABLE:
            return

        for tag in tags:
            tag_name = tag.get('name', 'unknown')
            confidence = tag.get('confidence', 0.0)

            SAFETY_TAGS_CONFIDENCE.labels(
                tag=tag_name,
                lane=lane
            ).observe(confidence)

    except Exception as e:
        # Don't fail the main operation
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to emit confidence metrics: {e}")


# Example usage in guardian evaluation:
"""
if band == GuardianBand.BLOCK and override_requested:
    # Critical override requires dual-approval
    try:
        validate_dual_approval(approver1_id, approver2_id, get_user_tier)
        emit_guardian_decision(
            db=db,
            plan_id=plan.id,
            lambda_id=context.lambda_id,
            action="block",
            rule_name=triggered_rule.name,
            tags=safety_tags,
            confidences=tag_confidences,
            band="critical",
            override_requested=True,
            override_granted=True,
            approver1_id=approver1_id,
            approver2_id=approver2_id,
            justification="Emergency patch window approved by dual T4+ approvers"
        )
        # Allow operation with override
        return GuardianBandResult(band=GuardianBand.ALLOW, override=True)
    except (ValueError, PermissionError) as e:
        # Override denied - emit failure
        emit_guardian_decision(
            db=db,
            plan_id=plan.id,
            lambda_id=context.lambda_id,
            action="block",
            rule_name=triggered_rule.name,
            tags=safety_tags,
            confidences=tag_confidences,
            band="critical",
            override_requested=True,
            override_granted=False,
            justification=f"Override denied: {e}"
        )
        return GuardianBandResult(band=GuardianBand.BLOCK, override=False)
"""
