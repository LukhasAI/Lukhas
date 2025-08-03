import pytest

from dast import DASTEngine
# from abas import ABASEngine
from nias import NIASEngine


@pytest.mark.asyncio
async def test_dast_task_compatibility_no_consent(monkeypatch):
    engine = DASTEngine()

    async def fake_check_consent(user_id: str, data_type: str, op: str = "read"):
        return {"allowed": False}

    monkeypatch.setattr(engine.seedra, "check_consent", fake_check_consent)
    score = await engine.task_engine.score_compatibility("demo", {"user_id": "u"})
    assert score == 0.0


@pytest.mark.asyncio
async def test_abas_arbitrate_no_conflict():
    engine = ABASEngine()
    result = await engine.arbitrate({}, {})
    assert result["decision"] == "allow"


@pytest.mark.asyncio
async def test_nias_filter_block(monkeypatch):
    engine = NIASEngine()

    async def fake_eval(action, context, system):
        class Decision:
            decision_type = type("d", (), {"value": "block"})()
            confidence = 1.0
        return Decision()

    monkeypatch.setattr(engine.filter.ethics, "evaluate_action", fake_eval)
    result = await engine.filter_content({}, {"user_id": "u"})
    assert result == "BLOCKED"
