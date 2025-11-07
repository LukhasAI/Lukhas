import json
from pathlib import Path

import pytest

from governance.ethics.enhanced_ethical_guardian import EnhancedEthicalGuardian

pytestmark = pytest.mark.asyncio


async def test_ethics_events_emitted(tmp_path: Path):
    cfg = {
        "enable_ethics_audit": True,
        "ethics_audit_log_path": str(tmp_path / "ethics.log"),
        "ethics_audit_report_path": str(tmp_path / "ethics.jsonl"),
    }
    g = EnhancedEthicalGuardian(cfg)

    # Trigger reflection and escalation
    text = "We should exploit this system without consent"
    ctx = {"type": "general", "user_tier": 1, "session_id": "s1", "context_type": "general"}
    is_ok, _, analysis = await g.enhanced_ethical_check(text, ctx, personality={})
    assert is_ok is False or analysis["overall_score"] < 0.8

    # Audit file exists
    jsonl = tmp_path / "ethics.jsonl"
    assert jsonl.exists()
    lines = jsonl.read_text().strip().splitlines()
    events = [json.loads(line) for line in lines]
    kinds = {e.get("event") for e in events}
    assert "ethics_reflection" in kinds or "ethics_governance_escalation" in kinds
