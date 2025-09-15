from products.content.poetica.creativity_engines.personality.brain import LUKHASBrain


class _StubCore:
    def __init__(self) -> None:
        self.components: dict[str, object] = {}

    def register_component(self, name: str, component: object) -> None:
        self.components[name] = component


def test_lukhas_brain_registers_components_and_scores_decision() -> None:
    core = _StubCore()
    brain = LUKHASBrain(core)

    trace = brain.memory_manager.record_event("dream", {"emotional_intensity": 0.4})
    decision = brain.decision_engine.evaluate(
        "generate",
        {"signals": {"creative": 0.9}, "compliance": 0.8},
    )

    assert "brain" in core.components
    assert trace.affect_delta != 0.0
    assert decision["approved"] is True
    assert 0.0 <= decision["score"] <= 1.0
