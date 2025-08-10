from bio.mitochondria_model import MitochondriaModel
from core.integrated_system import DistributedAISystem


def test_task_priority_score():
    class DummyModel(MitochondriaModel):
        def energy_output(self) -> float:
            return 1.0

    system = DistributedAISystem("test-system", energy_model=DummyModel())
    score = system.task_priority_score({"priority": 0.6})
    assert 0.0 <= score <= 1.0
    assert score > 0.6
