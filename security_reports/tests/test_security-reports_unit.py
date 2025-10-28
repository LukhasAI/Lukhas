# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
"""Unit tests for the :mod:`security_reports` module."""

from __future__ import annotations

import pytest

from security_reports import (
    SecurityReport,
    SecurityReportRepository,
    SecurityReportValidationError,
    SeverityLevel,
    build_secure_payload,
    validate_report,
)


@pytest.mark.unit
def test_build_secure_payload_redacts_sensitive_values():
    report = SecurityReport(
        report_id="rep-001",
        severity=SeverityLevel.HIGH,
        summary="API token exposed in request logs",
        details={
            "api_token": "abcd-1234",
            "endpoint": "/v1/audit",
        },
    )

    payload = build_secure_payload(report)

    assert payload["report_id"] == "rep-001"
    assert payload["severity"] == "high"
    assert payload["details"]["api_token"] == "[REDACTED]"
    assert payload["details"]["endpoint"] == "/v1/audit"


@pytest.mark.unit
def test_validate_report_rejects_sensitive_detail_values():
    report = SecurityReport(
        report_id="rep-002",
        severity=SeverityLevel.MEDIUM,
        summary="Service account credential rotated",
        details={"status": "rotated", "notes": "token=abcd-1234"},
    )

    with pytest.raises(SecurityReportValidationError):
        validate_report(report)


@pytest.mark.unit
def test_repository_upsert_and_search_returns_sanitised_reports():
    repo = SecurityReportRepository()
    report = SecurityReport(
        report_id="rep-003",
        severity=SeverityLevel.CRITICAL,
        summary="Compromised credential detected",
        details={
            "credential_id": "cred-123",
            "admin_password": "hunter2",
        },
    )

    repo.upsert(report)

    stored = repo.get("rep-003")
    assert stored.details["admin_password"] == "[REDACTED]"

    critical_reports = repo.search_by_severity("CRITICAL")
    assert critical_reports == [stored]
