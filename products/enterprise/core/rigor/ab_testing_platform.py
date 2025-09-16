"""Enterprise-grade A/B testing platform for rigorous experimentation."""

from __future__ import annotations

import logging
import math
import uuid
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

logger = logging.getLogger(__name__)


@dataclass
class VariantResult:
    """Tracked results for a single experiment variant."""

    name: str
    exposures: int = 0
    conversions: int = 0

    def record(self, converted: bool) -> None:
        self.exposures += 1
        if converted:
            self.conversions += 1

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.exposures if self.exposures else 0.0

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "name": self.name,
            "exposures": self.exposures,
            "conversions": self.conversions,
            "conversion_rate": self.conversion_rate,
        }


@dataclass
class Experiment:
    """Definition and runtime state for an experiment."""

    experiment_id: str
    name: str
    tier: str
    significance_threshold: float
    variants: Dict[str, VariantResult] = field(default_factory=dict)
    metadata: dict[str, str] = field(default_factory=dict)

    def ensure_variant(self, variant: str) -> VariantResult:
        if variant not in self.variants:
            self.variants[variant] = VariantResult(name=variant)
        return self.variants[variant]

    def to_dict(self) -> dict[str, object]:
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "tier": self.tier,
            "significance_threshold": self.significance_threshold,
            "variants": {name: variant.to_dict() for name, variant in self.variants.items()},
            "metadata": self.metadata,
        }


class T4ABTestingPlatform:
    """Rigorous A/B testing manager with deterministic analysis."""

    # ΛTAG: ab_testing_metrics
    def __init__(self, tier: str, significance_threshold: float = 0.95):
        if not 0 < significance_threshold < 1:
            raise ValueError("significance_threshold must be between 0 and 1")

        self.tier = tier
        self.significance_threshold = significance_threshold
        self._experiments: Dict[str, Experiment] = {}

        logger.info(
            "Initialized T4ABTestingPlatform",
            extra={
                "tier": tier,
                "significance_threshold": significance_threshold,
            },
        )

    # ΛTAG: experiment_registry
    def create_experiment(
        self,
        name: str,
        variants: Iterable[str],
        *,
        metadata: Optional[dict[str, str]] = None,
        significance_threshold: Optional[float] = None,
    ) -> Experiment:
        """Register a new experiment with optional custom significance threshold."""

        experiment_id = uuid.uuid4().hex
        threshold = significance_threshold or self.significance_threshold
        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            tier=self.tier,
            significance_threshold=threshold,
            metadata=metadata or {},
        )

        for variant in variants:
            experiment.ensure_variant(variant)

        self._experiments[experiment_id] = experiment
        logger.info("Registered experiment", extra=experiment.to_dict())
        return experiment

    def record_event(self, experiment_id: str, variant: str, converted: bool) -> VariantResult:
        """Record an exposure/conversion event for a variant."""

        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise KeyError(f"Experiment {experiment_id} not found")

        variant_result = experiment.ensure_variant(variant)
        variant_result.record(converted)
        logger.debug(
            "Recorded variant event",
            extra={
                "experiment_id": experiment_id,
                "variant": variant,
                "converted": converted,
                "exposures": variant_result.exposures,
                "conversions": variant_result.conversions,
            },
        )
        return variant_result

    def _z_score(self, control: VariantResult, challenger: VariantResult) -> float:
        """Calculate z-score between two variants using pooled probability."""

        if control.exposures == 0 or challenger.exposures == 0:
            return 0.0

        control_rate = control.conversion_rate
        challenger_rate = challenger.conversion_rate
        pooled = (control.conversions + challenger.conversions) / (
            control.exposures + challenger.exposures
        )
        denominator = math.sqrt(pooled * (1 - pooled) * (1 / control.exposures + 1 / challenger.exposures))
        if denominator == 0:
            return 0.0
        return (challenger_rate - control_rate) / denominator

    def _p_value_from_z(self, z_score: float) -> float:
        """Two-tailed p-value derived from z-score."""

        # Complementary error function approximation for deterministic p-value.
        return math.erfc(abs(z_score) / math.sqrt(2))

    def evaluate_experiment(self, experiment_id: str) -> dict[str, object]:
        """Compute experiment statistics and determine winner if significant."""

        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise KeyError(f"Experiment {experiment_id} not found")

        variants = list(experiment.variants.values())
        if len(variants) < 2:
            raise ValueError("At least two variants required to evaluate experiment")

        control = variants[0]
        evaluations: dict[str, dict[str, float]] = {}
        winning_variant: Optional[str] = None
        winning_p_value: Optional[float] = None

        for variant in variants[1:]:
            z_score = self._z_score(control, variant)
            p_value = self._p_value_from_z(z_score)
            significant = p_value <= (1 - experiment.significance_threshold)
            evaluations[variant.name] = {
                "z_score": z_score,
                "p_value": p_value,
                "conversion_rate": variant.conversion_rate,
                "exposures": variant.exposures,
                "conversions": variant.conversions,
                "significant": significant,
            }

            if significant and (winning_p_value is None or p_value < winning_p_value):
                winning_variant = variant.name
                winning_p_value = p_value

        result = {
            "experiment": experiment.to_dict(),
            "control": control.to_dict(),
            "challengers": evaluations,
            "winner": winning_variant,
            "winner_p_value": winning_p_value,
        }

        logger.info("Evaluated experiment", extra=result)
        return result

    def get_experiment(self, experiment_id: str) -> Experiment:
        experiment = self._experiments.get(experiment_id)
        if not experiment:
            raise KeyError(f"Experiment {experiment_id} not found")
        return experiment

    def list_experiments(self) -> list[dict[str, object]]:
        return [experiment.to_dict() for experiment in self._experiments.values()]
