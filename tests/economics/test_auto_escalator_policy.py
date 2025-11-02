"""Tests for the auto escalator policy incentives."""

# ΛTAG: auto_escalator_policy_tests

import asyncio
import time
from typing import Any

import pytest
from src.economics.auto_escalator_policy import (
    AutoEscalatorPolicy,
    EscalatorTier,
    UserValueMetrics,
)


def _build_metrics(**overrides: Any) -> UserValueMetrics:
    """Helper to construct metrics objects with sensible defaults."""

    base = dict(
        user_id="user-test",
        current_tier=EscalatorTier.VISITOR,
        monthly_transaction_volume=750.0,
        total_lifetime_volume=2500.0,
        avg_order_value=125.0,
        engagement_score=0.65,
        session_frequency=4.2,
        time_on_platform=8.5,
        data_quality_score=0.78,
        consent_breadth=0.85,
        data_freshness=0.92,
        feedback_score=0.72,
        referral_count=3,
        merchant_satisfaction=0.88,
        platform_advocacy=0.56,
        total_value_score=0.0,
        next_tier_progress=0.0,
        escalation_eligible=False,
        last_updated=time.time(),
    )
    base.update(overrides)
    return UserValueMetrics(**base)


def test_calculate_total_value_score_weighting():
    policy = AutoEscalatorPolicy({})
    metrics = _build_metrics(
        monthly_transaction_volume=1000.0,
        engagement_score=0.8,
        data_quality_score=0.9,
        feedback_score=0.7,
        referral_count=4,
        platform_advocacy=0.6,
    )

    score = policy._calculate_total_value_score(metrics)

    assert score == pytest.approx(0.7325, rel=1e-4)


def test_evaluate_tier_escalation_all_requirements_met(monkeypatch):
    policy = AutoEscalatorPolicy({})
    metrics = _build_metrics()
    metrics.total_value_score = policy._calculate_total_value_score(metrics)

    async def fake_calculate(user_id: str) -> UserValueMetrics:
        assert user_id == "lukhas-user"
        return metrics

    monkeypatch.setattr(policy, "calculate_user_value_metrics", fake_calculate)

    result = asyncio.run(policy.evaluate_tier_escalation("lukhas-user"))

    assert result["escalation_eligible"] is True
    assert result["next_tier"] == EscalatorTier.FRIEND.value
    assert result["progress_to_next_tier"] == pytest.approx(1.0)
    assert all(req_info["met"] for req_info in result["requirements"].values())


def test_evaluate_tier_escalation_partial_progress(monkeypatch):
    policy = AutoEscalatorPolicy({})
    metrics = _build_metrics(
        monthly_transaction_volume=200.0,
        engagement_score=0.45,
        data_quality_score=0.6,
        feedback_score=0.2,
        referral_count=1,
        platform_advocacy=0.4,
    )
    metrics.total_value_score = policy._calculate_total_value_score(metrics)

    async def fake_calculate(user_id: str) -> UserValueMetrics:
        return metrics

    monkeypatch.setattr(policy, "calculate_user_value_metrics", fake_calculate)

    result = asyncio.run(policy.evaluate_tier_escalation("lukhas-user"))

    assert result["escalation_eligible"] is False
    assert result["requirements"]["volume"]["met"] is False
    assert result["requirements"]["feedback"]["met"] is False
    assert result["progress_to_next_tier"] == pytest.approx(0.7666, rel=1e-3)


def test_get_next_tier_progression():
    policy = AutoEscalatorPolicy({})

    assert policy._get_next_tier(EscalatorTier.GUEST) == EscalatorTier.VISITOR
    assert policy._get_next_tier(EscalatorTier.ROOT_DEV) is None


def test_apply_tier_escalation_blocked_by_cooldown(monkeypatch):
    policy = AutoEscalatorPolicy({"escalation_cooldown_days": 30})

    async def fake_evaluate(user_id: str) -> dict[str, Any]:
        return {
            "escalation_eligible": True,
            "current_tier": EscalatorTier.VISITOR.value,
            "next_tier": EscalatorTier.FRIEND.value,
            "requirements": {},
            "total_value_score": 0.8,
        }

    async def fake_last_escalation(user_id: str) -> float:
        return time.time()

    monkeypatch.setattr(policy, "evaluate_tier_escalation", fake_evaluate)
    monkeypatch.setattr(policy, "_get_last_escalation_time", fake_last_escalation)

    result = asyncio.run(policy.apply_tier_escalation("lukhas-user"))

    assert result["escalated"] is False
    assert result["reason"] == "Escalation cooldown active"


def test_apply_tier_escalation_force_bypasses_cooldown(monkeypatch):
    policy = AutoEscalatorPolicy({"escalation_cooldown_days": 30})

    async def fake_evaluate(user_id: str) -> dict[str, Any]:
        return {
            "escalation_eligible": True,
            "current_tier": EscalatorTier.VISITOR.value,
            "next_tier": EscalatorTier.FRIEND.value,
            "requirements": {"volume": {"required": 500, "actual": 750, "met": True}},
            "total_value_score": 0.92,
        }

    async def fake_last_escalation(user_id: str) -> float:
        return time.time()

    store_calls: list[dict[str, Any]] = []
    update_calls: list[tuple[str, EscalatorTier]] = []
    notify_calls: list[tuple[str, dict[str, Any]]] = []

    async def fake_store(record: dict[str, Any]) -> None:
        store_calls.append(record)

    async def fake_update(user_id: str, tier: EscalatorTier) -> None:
        update_calls.append((user_id, tier))

    async def fake_notify(user_id: str, record: dict[str, Any]) -> None:
        notify_calls.append((user_id, record))

    monkeypatch.setattr(policy, "evaluate_tier_escalation", fake_evaluate)
    monkeypatch.setattr(policy, "_get_last_escalation_time", fake_last_escalation)
    monkeypatch.setattr(policy, "_store_escalation_record", fake_store)
    monkeypatch.setattr(policy, "_update_user_tier", fake_update)
    monkeypatch.setattr(policy, "_notify_user_escalation", fake_notify)

    result = asyncio.run(policy.apply_tier_escalation("lukhas-user", force=True))

    assert result["escalated"] is True
    assert result["from_tier"] == EscalatorTier.VISITOR.value
    assert result["to_tier"] == EscalatorTier.FRIEND.value
    assert store_calls and store_calls[0]["user_id"] == "lukhas-user"
    assert update_calls == [("lukhas-user", EscalatorTier.FRIEND)]
    assert notify_calls and notify_calls[0][0] == "lukhas-user"


def test_calculate_transaction_split_applies_bonuses_and_caps_total(monkeypatch):
    """Ensure transaction split bonus logic applies without exceeding the total amount."""

    policy = AutoEscalatorPolicy({})
    metrics = _build_metrics(
        current_tier=EscalatorTier.VISITOR,
        data_quality_score=0.95,
        engagement_score=0.85,
    )

    async def fake_metrics(user_id: str) -> UserValueMetrics:
        assert user_id == "lukhas-user"
        return metrics

    monkeypatch.setattr(policy, "calculate_user_value_metrics", fake_metrics)

    result = asyncio.run(
        policy.calculate_transaction_split("lukhas-user", transaction_amount=2000.0, opportunity_id="opp-42")
    )

    assert result["user_tier"] == EscalatorTier.VISITOR.value
    # ΛTAG: transaction_split_bonus_validation
    assert result["bonuses_applied"] == {"user_bonus": pytest.approx(18.0), "platform_bonus": 0.0}
    assert result["user_amount"] == pytest.approx(810.7, rel=1e-4)
    assert result["platform_amount"] == pytest.approx(1189.3, rel=1e-4)
    assert result["transaction_amount"] == 2000.0


def test_generate_escalation_transparency_report_aggregates_context(monkeypatch):
    """Validate transparency report composes metrics, evaluation, and history."""

    policy = AutoEscalatorPolicy({})
    metrics = _build_metrics(
        current_tier=EscalatorTier.TRUSTED,
        total_value_score=0.88,
        session_frequency=6.0,
        platform_advocacy=0.7,
    )

    async def fake_metrics(user_id: str) -> UserValueMetrics:
        return metrics

    async def fake_eval(user_id: str) -> dict[str, Any]:
        return {
            "escalation_eligible": False,
            "current_tier": EscalatorTier.TRUSTED.value,
            "next_tier": EscalatorTier.INNER_CIRCLE.value,
            "requirements": {
                "volume": {"required": 5000.0, "actual": 3000.0, "met": False},
            },
            "progress_to_next_tier": 0.6,
            "total_value_score": metrics.total_value_score,
        }

    async def fake_history(user_id: str) -> list[dict[str, Any]]:
        return [
            {
                "from_tier": EscalatorTier.FRIEND.value,
                "to_tier": EscalatorTier.TRUSTED.value,
                "escalated_at": 1700000000,
            }
        ]

    monkeypatch.setattr(policy, "calculate_user_value_metrics", fake_metrics)
    monkeypatch.setattr(policy, "evaluate_tier_escalation", fake_eval)
    monkeypatch.setattr(policy, "_get_escalation_history", fake_history)

    report = asyncio.run(policy.generate_escalation_transparency_report("lukhas-user"))

    assert report["user_id"] == "lukhas-user"
    assert report["current_status"]["tier"] == EscalatorTier.TRUSTED.value
    assert report["current_status"]["total_value_score"] == pytest.approx(0.88)
    assert report["escalation_status"]["progress_to_next_tier"] == pytest.approx(0.6)
    assert report["escalation_history"][0]["to_tier"] == EscalatorTier.TRUSTED.value
    # ΛTAG: transparency_report_validation
    assert EscalatorTier.TRUSTED.value in report["tier_comparison"]
    assert set(report["tier_comparison"].keys()) == {tier.value for tier in EscalatorTier}
    assert report["methodology"]["value_weights"] == policy.value_weights
