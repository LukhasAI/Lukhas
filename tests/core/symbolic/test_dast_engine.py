from pathlib import Path

import pytest
from core.symbolic.dast_engine import (
    GestureCorpusRepository,
    GestureInterpretationSystem,
    GestureScoringSystem,
)


class _AllowDecision:
    def __init__(self, confidence: float = 1.0) -> None:
        self.decision_type = type("DecisionType", (), {"value": "allow"})
        self.confidence = confidence


class _MockEthics:
    async def evaluate_action(self, *_, **__) -> _AllowDecision:
        return _AllowDecision()


@pytest.fixture()
def scorer() -> GestureScoringSystem:
    return GestureScoringSystem()


def test_score_gestures_returns_normalized_scores(scorer: GestureScoringSystem) -> None:
    gestures = [
        {
            "id": "g1",
            "type": "nod",
            "context_relevance": 0.9,
            "emotional_valence": 0.8,
            "timestamp": "2025-10-26T10:00:00+00:00",
            "intensity": 0.7,
            "tags": ["focus", "analysis"],
        },
        {
            "id": "g2",
            "type": "fidget",
            "context_relevance": 0.3,
            "emotional_valence": -0.6,
            "timestamp": "2025-10-26T10:00:45+00:00",
            "intensity": 0.2,
            "tags": ["drift"],
        },
        {
            "id": "g3",
            "type": "nod",
            "context_relevance": 0.6,
            "emotional_valence": 0.1,
            "timestamp": "2025-10-26T10:01:00+00:00",
            "tags": ["analysis"],
        },
    ]
    context = {
        "active_contexts": ["focus", "analysis"],
        "current_timestamp": "2025-10-26T10:01:30+00:00",
        "temporal_window": 120,
    }

    scores = scorer.score_gestures(gestures, context)

    assert set(scores) == {"g1", "g2", "g3"}
    assert all(0.0 <= score <= 1.0 for score in scores.values())
    assert scores["g1"] >= scores["g2"]


@pytest.mark.asyncio
async def test_interpret_returns_structured_states(scorer: GestureScoringSystem) -> None:
    gestures = [
        {
            "id": "g1",
            "type": "nod",
            "context_relevance": 0.8,
            "emotional_valence": 0.7,
            "timestamp": "2025-10-26T10:00:00+00:00",
            "tags": ["analysis"],
        },
        {
            "id": "g2",
            "type": "fidget",
            "context_relevance": 0.2,
            "emotional_valence": -0.5,
            "timestamp": "2025-10-26T10:00:40+00:00",
            "tags": ["drift"],
        },
    ]
    context = {
        "user_id": "user-42",
        "active_contexts": ["analysis"],
        "current_timestamp": "2025-10-26T10:01:00+00:00",
    }

    interpreter = GestureInterpretationSystem(
        engine=None,
        scorer=scorer,
        repository=GestureCorpusRepository(),
        ethics=_MockEthics(),
    )

    interpretation = await interpreter.interpret(gestures, context)

    assert interpretation["scores"]
    assert interpretation["states"], "expected at least one interpreted state"
    assert all("confidence" in state for state in interpretation["states"])
    assert 0.0 <= interpretation["metrics"]["drift_indicator"] <= 1.0


@pytest.mark.asyncio
async def test_fetch_gesture_data_uses_file_fallback(tmp_path: Path) -> None:
    corpus_path = tmp_path / "gestures.json"
    corpus_path.write_text(
        '{"gestures": [{"id": "g1", "type": "nod", "emotional_valence": 0.1}]}',
        encoding="utf-8",
    )

    repository = GestureCorpusRepository(corpus_path=corpus_path)

    first_fetch = await repository.fetch_gesture_data({"user_id": "user-1"})
    assert first_fetch == [{"id": "g1", "type": "nod", "emotional_valence": 0.1}]

    corpus_path.unlink()
    second_fetch = await repository.fetch_gesture_data({"user_id": "user-1"})

    assert second_fetch == first_fetch
