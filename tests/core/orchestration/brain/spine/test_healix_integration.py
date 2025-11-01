"""Tests for Healix mapper dependencies and dashboard orchestration."""
from __future__ import annotations

from core.blockchain import BlockchainWrapper
from core.consciousness.drift_detector import ConsciousnessDriftDetector
from core.emotion import EmotionMapper
from core.identity.vault import get_access_log, reset_registry
from core.orchestration.brain.dashboard.main_dashboard import HealixDashboard
from core.orchestration.brain.spine.accent_adapter import AccentAdapter
from core.widgets import create_healix_widget


def test_emotion_mapper_basic_scoring() -> None:
    mapper = EmotionMapper()
    record = {"mood_hint": "calm", "emotion_vector": [0.6, 0.6, 0.5]}
    tone = mapper.suggest_tone("memory", record)
    intensity = mapper.score_intensity(record)
    similarity = mapper.tone_similarity_score("calm", record)
    assert tone == "calm"
    assert 0.0 <= intensity <= 1.0
    assert similarity > 0.0


def test_drift_detector_summary() -> None:
    detector = ConsciousnessDriftDetector(retention=12)
    baseline = {"emotion_vector": [0.5, 0.5, 0.5]}
    current = {"emotion_vector": [0.9, 0.1, 0.5]}
    summary = detector.summarize(baseline, current)
    assert "driftScore" in summary and summary["driftScore"] >= 0.0
    assert detector.is_drift(baseline, current)


def test_blockchain_wrapper_records_transactions() -> None:
    wrapper = BlockchainWrapper()
    entry = wrapper.record_transaction("test::1", {"value": 42})
    assert wrapper.verify_integrity()
    assert wrapper.get_transactions()[0] == entry


def test_healix_dashboard_builds_state() -> None:
    reset_registry(tiers={"user-123": "guardian"})
    memory_records = [
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "type": "memory",
            "tone": "calm",
            "intensity": 0.7,
            "hash": "abc",
            "recall_count": 2,
            "emotion_vector": [0.6, 0.4, 0.5],
            "mood_hint": "calm",
        },
        {
            "timestamp": "2025-01-02T00:00:00Z",
            "type": "memory",
            "tone": "curious",
            "intensity": 0.4,
            "hash": "def",
            "recall_count": 1,
            "emotion_vector": [0.4, 0.6, 0.5],
            "mood_hint": "curious",
        },
    ]
    accent = AccentAdapter(tier="guardian", memory_source=lambda _: memory_records)
    dashboard = HealixDashboard(
        accent_adapter=accent,
        emotion_mapper=EmotionMapper(),
        drift_detector=ConsciousnessDriftDetector(retention=12),
        widget=create_healix_widget(),
        blockchain=BlockchainWrapper(),
    )
    baseline = {"emotion_vector": [0.5, 0.5, 0.5]}
    state = dashboard.build_dashboard_state("user-123", baseline_state=baseline)
    assert len(state["timeline"]) == len(memory_records)
    assert state["drift"]["driftScore"] >= 0.0
    assert state["ledger_length"] == 1
    assert get_access_log()
