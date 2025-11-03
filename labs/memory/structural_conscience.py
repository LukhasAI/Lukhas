"""
structural_conscience.py — Structural awareness & integrity validation

Purpose
-------
Validates structural integrity of memory folds and monitors the
memory–consciousness interface. Designed to prevent cascade errors and
flag misalignment before consolidation writes land in long‑term memory.

Usage
-----
from memory.structural_conscience import StructuralConscience, StructuralReport
report = StructuralConscience().validate_memory_structure(fold)
print(report.ok, report.issues)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


class StructuralIntegrityError(Exception):
    pass

@dataclass
class StructuralReport:
    ok: bool
    coherence_score: float  # 0..1
    cascade_risk: float     # 0..1 (lower is better)
    alignment_score: float  # 0..1 with consciousness policy
    issues: List[str] = field(default_factory=list)

class StructuralConscience:
    """Memory structural awareness and integrity validation.

    Parameters
    ----------
    awareness_threshold : float
        Minimum coherence required to pass validation.
    cascade_ceiling : float
        Maximum allowable cascade risk.
    require_alignment : bool
        Whether to enforce consciousness-alignment threshold.
    alignment_threshold : float
        Minimum alignment score to pass when enforced.
    """

    def __init__(
        self,
        awareness_threshold: float = 0.7,
        cascade_ceiling: float = 0.3,
        require_alignment: bool = True,
        alignment_threshold: float = 0.7,
    ) -> None:
        self.awareness_threshold = awareness_threshold
        self.cascade_ceiling = cascade_ceiling
        self.require_alignment = require_alignment
        self.alignment_threshold = alignment_threshold

    # ---------------- Core Checks ---------------- #

    def validate_memory_structure(self, memory_fold: Any) -> StructuralReport:
        """Validate memory fold structural integrity.

        Expects an object with attributes: origin_trace_ids (list[str]),
        quality (0..1), domain (str), metadata (dict). Accepts duck-typed
        objects (e.g., dataclasses from the orchestrator).
        """
        issues: List[str] = []

        # Basic schema sanity
        try:
            origin_ids = list(memory_fold.origin_trace_ids)
            quality = float(memory_fold.quality)
            domain = str(memory_fold.domain)
            dict(memory_fold.metadata)
        except Exception as e:
            raise StructuralIntegrityError(f"Fold schema invalid: {e}")

        if not origin_ids:
            issues.append("empty_origin_set")
        if not (0.0 <= quality <= 1.0):
            issues.append("quality_out_of_range")
        if domain not in {"episodic", "semantic", "procedural"}:
            issues.append("unknown_domain")

        # Coherence proxy: quality weighted by diversity & size
        diversity = len(set(origin_ids)) / max(1, len(origin_ids))
        coherence = max(0.0, min(1.0, 0.5 * quality + 0.5 * diversity))

        # Cascade risk proxy: inverse of coherence with penalty for size spikes
        size_penalty = 0.1 if len(origin_ids) > 64 else 0.0
        cascade_risk = max(0.0, min(1.0, (1.0 - coherence) + size_penalty))

        # Alignment proxy: domain-aware policy with quality blend
        policy = {"semantic": 0.85, "episodic": 0.85, "procedural": 0.75}
        base = policy.get(domain, 0.75)
        alignment = max(0.0, min(1.0, 0.6 * base + 0.4 * quality))

        ok = True
        if coherence < self.awareness_threshold:
            ok = False; issues.append("coherence_below_threshold")
        if cascade_risk > self.cascade_ceiling:
            ok = False; issues.append("cascade_risk_too_high")
        # Procedural domain gets slightly more permissive threshold
        threshold = self.alignment_threshold if domain != "procedural" else max(0.6, self.alignment_threshold - 0.1)
        if self.require_alignment and alignment < threshold:
            ok = False; issues.append("alignment_below_threshold")

        return StructuralReport(
            ok=ok,
            coherence_score=round(coherence, 3),
            cascade_risk=round(cascade_risk, 3),
            alignment_score=round(alignment, 3),
            issues=issues,
        )

    def monitor_consciousness_integration(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor memory–consciousness integration health.

        Parameters
        ----------
        metrics : Dict[str, Any]
            Expect keys like {"batches", "folds_created", "traces_consolidated"}.
        """
        # Simple thresholds; replace with your real KPI policy
        status = {
            "ok": True,
            "notes": [],
        }
        if metrics.get("folds_created", 0) == 0:
            status["ok"] = False
            status["notes"].append("no_folds_created")
        if metrics.get("traces_consolidated", 0) < metrics.get("batches", 0):
            status["ok"] = False
            status["notes"].append("low_trace_yield_per_batch")
        return status
