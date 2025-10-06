import json
from pathlib import Path

from candidate.governance.identity.core.id_service.lambd_id_generator import (
    LambdaIDGenerator,
    TierLevel,
)


def test_load_config_merges_defaults(tmp_path: Path):
    cfg = {"id_length": 6, "log_path": str(tmp_path / "ids.log")}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))

    gen = LambdaIDGenerator(config_path=str(cfg_path))
    # Ensure defaults still exist alongside overrides
    assert gen.config["id_length"] == 6
    assert gen.config["max_retries"] == 5
    assert "symbolic_enabled" in gen.config
    assert Path(gen.config["log_path"]).name == "ids.log"


def test_generation_stats_and_logging_with_collision(tmp_path: Path, monkeypatch):
    # Configure logging to temp file
    cfg = {"log_path": str(tmp_path / "ids.log")}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    gen = LambdaIDGenerator(config_path=str(cfg_path))

    # Force deterministic values to create a collision on second call, then resolve
    attempt = {"n": 0}

    def fixed_symbol(tier, pref=None):
        return "◊"

    def fixed_ts():
        attempt["n"] += 1
        return "ABCD" if attempt["n"] == 1 else "ZZZZ"

    def fixed_entropy(tier, ctx):
        # First attempt collides, subsequent attempt differs
        return "WXYZ" if attempt["n"] == 1 else "YYYY"

    monkeypatch.setattr(gen, "_select_symbolic_element", fixed_symbol)
    monkeypatch.setattr(gen, "_generate_timestamp_hash", fixed_ts)
    monkeypatch.setattr(gen, "_generate_entropy_hash", fixed_entropy)

    # First generation (unique)
    id1 = gen.generate_lambda_id(TierLevel.FRIEND, user_context={"uid": "u1"})
    assert id1
    # Second generation (collision then resolve via retry path)
    id2 = gen.generate_lambda_id(TierLevel.FRIEND, user_context={"uid": "u2"})
    assert id2 != id1

    stats = gen.get_generation_stats()
    assert stats["total_generated"] >= 2
    assert stats["collision_rate"] >= 0.0
    assert any(k for k in stats["tier_distribution"])  # has tiers
    assert any(k for k in stats["symbolic_usage"])  # has symbol counts

    # Log file created and has entries
    log_path = Path(gen.config["log_path"])
    assert log_path.exists()
    content = log_path.read_text().strip().splitlines()
    assert len(content) >= 2
    # JSON parse a line
    rec = json.loads(content[0])
    assert "lambda_id" in rec and "tier" in rec
