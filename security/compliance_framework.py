"""Compliance framework utilities for the security package."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Optional


class ControlStatus(Enum):
    """Status values for compliance controls."""

    IMPLEMENTED = "implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    NOT_IMPLEMENTED = "not_implemented"


class EvidenceType(Enum):
    """Type of evidence collected during control assessments."""

    CONFIGURATION = "configuration"
    POLICY = "policy"
    LOG = "log"
    SCREENSHOT = "screenshot"
    OTHER = "other"


class RiskLevel(Enum):
    """Qualitative risk levels used for assessments."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_RISK_SCORES: Dict[RiskLevel, int] = {
    RiskLevel.LOW: 1,
    RiskLevel.MEDIUM: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.CRITICAL: 4,
}


@dataclass
class ControlAssessment:
    """Representation of a control assessment outcome."""

    id: str
    control_id: str
    result: ControlStatus
    assessment_type: str
    findings: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class EvidenceRecord:
    """Metadata about collected evidence."""

    id: str
    control_id: str
    evidence_type: EvidenceType
    title: str
    description: str
    content: str
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    stored_path: Optional[str] = None


@dataclass
class RiskAssessment:
    """Risk assessment entry."""

    id: str
    title: str
    description: str
    risk_category: str
    likelihood: RiskLevel
    impact: RiskLevel
    residual_risk: RiskLevel
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ComplianceReport:
    """Summary of the compliance posture."""

    id: str
    generated_at: datetime
    overall_status: str
    totals: Dict[str, Any]
    details: Dict[str, Any]


def _normalise_control_status(value: Any) -> ControlStatus:
    """Convert arbitrary status values to :class:`ControlStatus`."""

    if isinstance(value, ControlStatus):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()
        for status in ControlStatus:
            if status.value == normalized:
                return status

    # Unknown values default to not implemented to avoid overstating compliance.
    return ControlStatus.NOT_IMPLEMENTED


def _score_to_level(score: int) -> RiskLevel:
    """Map a numeric risk score to a qualitative level."""

    if score >= _RISK_SCORES[RiskLevel.CRITICAL]:
        return RiskLevel.CRITICAL
    if score >= _RISK_SCORES[RiskLevel.HIGH]:
        return RiskLevel.HIGH
    if score >= _RISK_SCORES[RiskLevel.MEDIUM]:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


class ComplianceFramework:
    """Minimal compliance framework used by the security test suite."""

    def __init__(self, evidence_path: str, guardian_integration: bool = True) -> None:
        self.evidence_path = evidence_path
        self.guardian_integration = guardian_integration
        self.automation_handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.assessments: Dict[str, ControlAssessment] = {}
        self.evidence: Dict[str, EvidenceRecord] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}
        self.assessment_count = 0
        self.automation_count = 0

        os.makedirs(self.evidence_path, exist_ok=True)

    # ------------------------------------------------------------------
    # Automation
    # ------------------------------------------------------------------
    def register_automation_handler(
        self, control_id: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """Register an automation handler for a control."""

        self.automation_handlers[control_id] = handler

    def assess_control(self, control_id: str, assessment_type: str = "manual") -> ControlAssessment:
        """Run an assessment for the given control."""

        handler = self.automation_handlers.get(control_id)
        assessment_id = str(uuid.uuid4())
        findings: List[str] = []
        metadata: Dict[str, Any] = {}
        confidence = 0.0

        if handler:
            self.automation_count += 1
            context = {"id": control_id, "assessment_type": assessment_type}
            handler_result = handler(context) or {}
            result_status = _normalise_control_status(handler_result.get("status"))
            findings = list(handler_result.get("findings", []))
            metadata = dict(handler_result.get("metadata", {}))
            confidence = float(handler_result.get("confidence", 0.0))
        else:
            result_status = ControlStatus.NOT_IMPLEMENTED
            metadata["reason"] = "no_automation_handler"

        assessment = ControlAssessment(
            id=assessment_id,
            control_id=control_id,
            result=result_status,
            assessment_type=assessment_type,
            findings=findings,
            metadata=metadata,
            confidence=confidence,
        )
        self.assessments[assessment_id] = assessment
        self.assessment_count += 1
        return assessment

    # ------------------------------------------------------------------
    # Evidence management
    # ------------------------------------------------------------------
    def collect_evidence(
        self,
        control_id: str,
        evidence_type: EvidenceType,
        title: str,
        description: str,
        content: str,
    ) -> str:
        """Collect evidence for a control and persist metadata."""

        os.makedirs(self.evidence_path, exist_ok=True)
        evidence_id = str(uuid.uuid4())
        stored_path = os.path.join(self.evidence_path, f"{evidence_id}.txt")
        with open(stored_path, "w", encoding="utf-8") as handle:
            handle.write(content)

        record = EvidenceRecord(
            id=evidence_id,
            control_id=control_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            content=content,
            stored_path=stored_path,
        )
        self.evidence[evidence_id] = record
        return evidence_id

    # ------------------------------------------------------------------
    # Risk management
    # ------------------------------------------------------------------
    def run_risk_assessment(
        self,
        title: str,
        description: str,
        risk_category: str,
        likelihood: RiskLevel,
        impact: RiskLevel,
    ) -> str:
        """Run a lightweight risk assessment and store the results."""

        risk_id = str(uuid.uuid4())
        score = max(_RISK_SCORES[likelihood], _RISK_SCORES[impact])
        residual_risk = _score_to_level(score)
        assessment = RiskAssessment(
            id=risk_id,
            title=title,
            description=description,
            risk_category=risk_category,
            likelihood=likelihood,
            impact=impact,
            residual_risk=residual_risk,
        )
        self.risk_assessments[risk_id] = assessment
        return risk_id

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def _recent_assessments(self, limit: int = 10) -> Iterable[ControlAssessment]:
        return sorted(self.assessments.values(), key=lambda a: a.assessed_at, reverse=True)[:limit]

    def generate_compliance_report(self) -> ComplianceReport:
        """Generate a compliance report summarising assessments."""

        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc)

        total_controls = len(self.assessments)
        implemented_controls = len(
            [assessment for assessment in self.assessments.values() if assessment.result == ControlStatus.IMPLEMENTED]
        )
        implementation_ratio = implemented_controls / total_controls if total_controls else 0.0

        if total_controls == 0:
            overall_status = "Compliant (No Assessments)"
        elif implementation_ratio >= 0.8:
            overall_status = "Compliant"
        elif implementation_ratio >= 0.5:
            overall_status = "Partially Compliant"
        else:
            overall_status = "Needs Improvement"

        totals = {
            "total_controls": total_controls,
            "implemented_controls": implemented_controls,
            "automation_runs": self.automation_count,
            "evidence_items": len(self.evidence),
            "risk_assessments": len(self.risk_assessments),
        }

        details = {
            "implementation_ratio": implementation_ratio,
            "recent_assessments": [
                {
                    "id": assessment.id,
                    "control_id": assessment.control_id,
                    "result": assessment.result.value,
                    "assessed_at": assessment.assessed_at.isoformat(),
                }
                for assessment in self._recent_assessments()
            ],
        }

        return ComplianceReport(
            id=report_id,
            generated_at=generated_at,
            overall_status=overall_status,
            totals=totals,
            details=details,
        )


def create_compliance_framework(config: Optional[Dict[str, Any]] = None) -> ComplianceFramework:
    """Factory helper used by the test suite to build a framework instance."""

    config = config or {}
    evidence_path = config.get("evidence_path", os.path.join(os.getcwd(), "compliance_evidence"))
    guardian_integration = bool(config.get("guardian_integration", True))

    framework = ComplianceFramework(
        evidence_path=evidence_path,
        guardian_integration=guardian_integration,
    )

    for control_id, handler in config.get("automation_handlers", {}).items():
        framework.register_automation_handler(control_id, handler)

    return framework


__all__ = [
    "ComplianceFramework",
    "ComplianceReport",
    "ControlAssessment",
    "ControlStatus",
    "EvidenceRecord",
    "EvidenceType",
    "RiskAssessment",
    "RiskLevel",
    "create_compliance_framework",
]
