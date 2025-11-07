import json
from pathlib import Path

from tiers import GlobalTier

from consciousness.awareness.awareness_log_synchronizer import AwarenessLogSynchronizer


def test_sync_for_user_respects_tier(tmp_path: Path):
    log_file = tmp_path / "logs.jsonl"
    entries = [
        {"user_id": "alpha", "tier": 0, "msg": "public"},
        {"user_id": "alpha", "tier": 2, "msg": "elevated", "summary": "detail"},
        {"user_id": "alpha", "tier": 3, "msg": "privileged"},
    ]
    log_file.write_text("\n".join(json.dumps(e) for e in entries))

    sync = AwarenessLogSynchronizer(str(log_file))
    visible = sync.sync_for_user("alpha", GlobalTier.ELEVATED)

    assert visible[0]["msg"] == "public"
    assert visible[1]["expansion"] == "detail"
    assert visible[2]["restricted"] is True
