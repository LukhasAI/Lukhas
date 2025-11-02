"""Utilities for aggregating and normalizing security scan reports."""

from __future__ import annotations

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


class SecurityReportError(RuntimeError):
    """Raised when security report data cannot be processed."""


_SEVERITY_ORDER: Mapping[str, int] = {
    "CRITICAL": 5,
    "HIGH": 4,
    "MEDIUM": 3,
    "LOW": 2,
    "INFO": 1,
    "UNKNOWN": 0,
}


@dataclass
class VulnerabilityRecord:
    """Normalized representation of a single vulnerability finding."""

    identifier: str
    package: Optional[str] = None
    installed_version: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    fix_versions: Tuple[str, ...] = ()
    sources: Tuple[str, ...] = ()

    def merge(self, other: "VulnerabilityRecord") -> "VulnerabilityRecord":
        """Return a new record that combines data from ``self`` and ``other``."""

        severity = _pick_severity(self.severity, other.severity)
        description = self.description or other.description
        installed_version = self.installed_version or other.installed_version
        fix_versions = tuple(sorted(set(self.fix_versions) | set(other.fix_versions)))
        sources = tuple(sorted(set(self.sources + other.sources)))
        package = self.package or other.package
        identifier = self.identifier or other.identifier
        return VulnerabilityRecord(
            identifier=identifier,
            package=package,
            installed_version=installed_version,
            severity=severity,
            description=description,
            fix_versions=fix_versions,
            sources=sources,
        )


@dataclass
class SecuritySummary:
    """Summary of aggregated security scan results."""

    vulnerabilities: List[VulnerabilityRecord] = field(default_factory=list)
    bandit_issue_count: int = 0
    missing_reports: Tuple[str, ...] = ()

    @property
    def total_vulnerabilities(self) -> int:
        """Return the total number of aggregated vulnerabilities."""

        return len(self.vulnerabilities)


def _pick_severity(first: Optional[str], second: Optional[str]) -> Optional[str]:
    """Return the most severe option between ``first`` and ``second``."""

    if first is None:
        return _normalize_severity(second)
    if second is None:
        return _normalize_severity(first)

    first_norm = _normalize_severity(first)
    second_norm = _normalize_severity(second)
    if first_norm is None:
        return second_norm
    if second_norm is None:
        return first_norm
    return first_norm if _SEVERITY_ORDER.get(first_norm, -1) >= _SEVERITY_ORDER.get(second_norm, -1) else second_norm


def _normalize_severity(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = str(value).strip().upper()
    if normalized in _SEVERITY_ORDER:
        return normalized
    return normalized or None


class SecurityReportAggregator:
    """Aggregate multiple security scan outputs into a unified summary."""

    REPORT_FILES: Mapping[str, Tuple[str, ...]] = {
        "pip_audit": ("pip-audit.json",),
        "safety": ("safety-report.json", "safety-scan.json"),
        "bandit": ("bandit.json", "bandit-report.json"),
    }

    def __init__(self, reports_dir: Path | str):
        self.reports_dir = Path(reports_dir)
        if not self.reports_dir.exists():
            raise FileNotFoundError(f"Security reports directory '{self.reports_dir}' does not exist")

    def summarize(self) -> SecuritySummary:
        """Load available reports and return a summary of the findings."""

        missing: List[str] = []
        vulnerabilities: MutableMapping[Tuple[str, Optional[str]], VulnerabilityRecord] = {}
        bandit_issue_count = 0

        pip_audit_data = self._load_json_report("pip_audit", missing)
        if pip_audit_data is not None:
            for record in self._extract_from_pip_audit(pip_audit_data):
                _merge_record(vulnerabilities, record)

        safety_data = self._load_json_report("safety", missing)
        if safety_data is not None:
            for record in self._extract_from_safety(safety_data):
                _merge_record(vulnerabilities, record)

        bandit_data = self._load_json_report("bandit", missing)
        if bandit_data is not None:
            bandit_issue_count = len(bandit_data.get("results", []))

        sorted_vulns = sorted(
            vulnerabilities.values(),
            key=lambda item: (
                item.package or "", item.identifier, _SEVERITY_ORDER.get(item.severity or "", -1) * -1
            ),
        )

        return SecuritySummary(
            vulnerabilities=sorted_vulns,
            bandit_issue_count=bandit_issue_count,
            missing_reports=tuple(sorted(missing)),
        )

    def _load_json_report(self, name: str, missing: List[str]) -> Optional[object]:
        filenames = self.REPORT_FILES.get(name, ())
        for filename in filenames:
            path = self.reports_dir / filename
            if path.exists():
                try:
                    with path.open("r", encoding="utf-8") as handle:
                        return json.load(handle)
                except json.JSONDecodeError as exc:
                    raise SecurityReportError(f"Unable to parse {filename}: {exc}") from exc
        missing.append(name)
        return None

    def _extract_from_pip_audit(self, data: object) -> Iterable[VulnerabilityRecord]:
        if not isinstance(data, list):
            raise SecurityReportError("pip-audit report is expected to be a list")

        for entry in data:
            if not isinstance(entry, Mapping):
                continue
            package = entry.get("name")
            installed_version = entry.get("version")
            vulnerabilities = entry.get("vulns") or []
            if not isinstance(vulnerabilities, Sequence):
                continue
            for vuln in vulnerabilities:
                if not isinstance(vuln, Mapping):
                    continue
                identifier = str(vuln.get("id") or "UNKNOWN")
                severity = vuln.get("severity")
                description = vuln.get("description")
                fix_versions = _to_tuple(vuln.get("fix_versions"))
                yield VulnerabilityRecord(
                    identifier=identifier,
                    package=_to_optional_str(package),
                    installed_version=_to_optional_str(installed_version),
                    severity=_normalize_severity(severity),
                    description=_to_optional_str(description),
                    fix_versions=fix_versions,
                    sources=("pip-audit",),
                )

    def _extract_from_safety(self, data: object) -> Iterable[VulnerabilityRecord]:
        vulnerabilities = None
        if isinstance(data, Mapping):
            vulnerabilities = data.get("vulnerabilities")
        if vulnerabilities is None:
            raise SecurityReportError("safety report is missing 'vulnerabilities' section")
        if not isinstance(vulnerabilities, Sequence):
            raise SecurityReportError("safety report 'vulnerabilities' must be a sequence")

        for vuln in vulnerabilities:
            if not isinstance(vuln, Mapping):
                continue
            dependency = vuln.get("dependency") or {}
            package = None
            installed_version = None
            if isinstance(dependency, Mapping):
                package = dependency.get("package_name") or dependency.get("name")
                installed_version = dependency.get("installed_version") or dependency.get("version")

            identifier = str(vuln.get("vulnerability_id") or vuln.get("id") or "UNKNOWN")
            severity = vuln.get("severity") or vuln.get("cvss_score")
            description = vuln.get("advisory") or vuln.get("description")
            fix_versions = _to_tuple(vuln.get("fix_versions"))
            yield VulnerabilityRecord(
                identifier=identifier,
                package=_to_optional_str(package),
                installed_version=_to_optional_str(installed_version),
                severity=_normalize_severity(severity),
                description=_to_optional_str(description),
                fix_versions=fix_versions,
                sources=("safety",),
            )


def _to_optional_str(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _to_tuple(value: object) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value if str(item).strip()]
        return tuple(sorted(set(items)))
    text = str(value).strip()
    return (text,) if text else ()


def _merge_record(target: MutableMapping[Tuple[str, Optional[str]], VulnerabilityRecord], record: VulnerabilityRecord) -> None:
    key = (record.identifier, record.package)
    if key in target:
        target[key] = target[key].merge(record)
    else:
        target[key] = record
