"""Core security report utilities.

This module provides a minimal implementation for working with security
incident reports in the LUKHAS workspace.  The implementation focuses on
defensive validation and data scrubbing so that sensitive material cannot
leak into logs or analytics pipelines.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Dict, Iterable, Mapping


class SecurityReportValidationError(ValueError):
    """Raised when a :class:`SecurityReport` fails validation."""


class SeverityLevel(str, Enum):
    """Enumeration describing the severity of a security report."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_value(cls, value: str | "SeverityLevel") -> "SeverityLevel":
        """Return a :class:`SeverityLevel` instance from *value*.

        Args:
            value: A :class:`SeverityLevel` member or a string representation
                (case-insensitive).

        Raises:
            SecurityReportValidationError: If *value* cannot be coerced to a
                :class:`SeverityLevel` instance.
        """

        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()
            try:
                return cls(normalized)
            except ValueError as exc:  # pragma: no cover - defensive
                raise SecurityReportValidationError(
                    f"Unknown severity level: {value!r}"
                ) from exc

        raise SecurityReportValidationError(
            f"Unsupported severity type: {type(value)!r}"
        )


_SENSITIVE_KEY_PATTERN = re.compile(
    r"(password|secret|token|apikey|api_key|credential|privkey)", re.IGNORECASE
)


def _contains_sensitive_data(value: str) -> bool:
    """Return ``True`` if the string *value* appears to contain secrets."""

    return bool(_SENSITIVE_KEY_PATTERN.search(value))


def _sanitize_mapping(data: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a sanitised copy of *data* with sensitive values redacted."""

    sanitised: Dict[str, Any] = {}
    for key, value in data.items():
        replacement: Any = value

        if isinstance(key, str) and _contains_sensitive_data(key):
            replacement = "[REDACTED]"
        elif isinstance(value, str) and _contains_sensitive_data(value):
            replacement = "[REDACTED]"

        sanitised[key] = replacement
    return sanitised


@dataclass(frozen=True, slots=True)
class SecurityReport:
    """Structured representation of a security incident report."""

    report_id: str
    severity: SeverityLevel
    summary: str
    details: Mapping[str, Any]

    def sanitise(self) -> "SecurityReport":
        """Return a sanitised copy of the report with sensitive data redacted."""

        return replace(self, details=_sanitize_mapping(self.details))

    def to_payload(self) -> Dict[str, Any]:
        """Return a dictionary payload suitable for serialisation."""

        sanitised = self.sanitise()
        return {
            "report_id": sanitised.report_id,
            "severity": sanitised.severity.value,
            "summary": sanitised.summary,
            "details": dict(sanitised.details),
        }


def validate_report(report: SecurityReport, *, allowed_detail_keys: Iterable[str] | None = None) -> None:
    """Validate *report* ensuring it is safe to store or emit.

    Args:
        report: The :class:`SecurityReport` instance to validate.
        allowed_detail_keys: Optional iterable restricting detail keys.

    Raises:
        SecurityReportValidationError: If *report* is invalid.
    """

    if not isinstance(report, SecurityReport):
        raise SecurityReportValidationError("Report must be a SecurityReport instance")

    if not report.report_id or not report.report_id.strip():
        raise SecurityReportValidationError("report_id must be a non-empty string")

    if not isinstance(report.severity, SeverityLevel):
        raise SecurityReportValidationError("severity must be a SeverityLevel")

    if not report.summary or not report.summary.strip():
        raise SecurityReportValidationError("summary must be provided")

    detail_keys = set(report.details.keys())
    if allowed_detail_keys is not None:
        allowed = set(allowed_detail_keys)
        missing = detail_keys - allowed
        if missing:
            raise SecurityReportValidationError(
                f"Unexpected detail keys present: {sorted(missing)!r}"
            )

    for key, value in report.details.items():
        if not isinstance(key, str) or not key:
            raise SecurityReportValidationError("detail keys must be non-empty strings")

        if isinstance(value, str) and _contains_sensitive_data(value):
            raise SecurityReportValidationError(
                f"detail {key!r} contains sensitive information"
            )


def build_secure_payload(report: SecurityReport) -> Dict[str, Any]:
    """Validate and sanitise *report*, returning a serialisable payload."""

    validate_report(report)
    return report.to_payload()


class SecurityReportRepository:
    """In-memory repository that stores sanitised security reports."""

    def __init__(self) -> None:
        self._storage: Dict[str, SecurityReport] = {}

    def upsert(self, report: SecurityReport) -> None:
        """Insert or update *report* after validating and sanitising it."""

        validate_report(report)
        self._storage[report.report_id] = report.sanitise()

    def get(self, report_id: str) -> SecurityReport:
        """Return the stored report for *report_id*.

        Raises:
            KeyError: If *report_id* does not exist.
        """

        return self._storage[report_id]

    def search_by_severity(self, severity: SeverityLevel | str) -> list[SecurityReport]:
        """Return a list of reports matching *severity* (case-insensitive)."""

        severity_value = SeverityLevel.from_value(severity)
        return [
            report for report in self._storage.values() if report.severity is severity_value
        ]


__all__ = [
    "SecurityReport",
    "SecurityReportRepository",
    "SecurityReportValidationError",
    "SeverityLevel",
    "build_secure_payload",
    "validate_report",
]
