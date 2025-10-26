import pytest
from products.enterprise.core.rigor.ab_testing_platform import T4ABTestingPlatform


def test_ab_testing_platform_records_and_evaluates():
    platform = T4ABTestingPlatform(tier="enterprise", significance_threshold=0.95)
    experiment = platform.create_experiment("homepage", ["control", "variant"], metadata={"area": "ux"})

    # Control: 100 exposures, 20 conversions (20%)
    for index in range(100):
        platform.record_event(experiment.experiment_id, "control", converted=index < 20)

    # Variant: 100 exposures, 40 conversions (40%)
    for index in range(100):
        platform.record_event(experiment.experiment_id, "variant", converted=index < 40)

    result = platform.evaluate_experiment(experiment.experiment_id)

    assert result["experiment"]["metadata"]["area"] == "ux"
    assert result["control"]["conversion_rate"] == pytest.approx(0.2, rel=1e-6)
    assert result["challengers"]["variant"]["conversion_rate"] == pytest.approx(0.4, rel=1e-6)
    assert result["challengers"]["variant"]["significant"] is True
    assert result["winner"] == "variant"


def test_ab_testing_platform_threshold_validation():
    with pytest.raises(ValueError):
        T4ABTestingPlatform(tier="enterprise", significance_threshold=1.5)

    platform = T4ABTestingPlatform(tier="enterprise")
    experiment = platform.create_experiment("copy-test", ["control", "variant"])

    # Minimal exposures keep experiment inconclusive
    platform.record_event(experiment.experiment_id, "control", converted=False)
    platform.record_event(experiment.experiment_id, "variant", converted=True)

    result = platform.evaluate_experiment(experiment.experiment_id)
    assert result["winner"] is None
    assert result["challengers"]["variant"]["significant"] is False
