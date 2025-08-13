from lukhas_pwm.dna.memory_inmem import InMemoryHelix
from lukhas_pwm.migration.legacy_jsonl import LegacyJSONL
from lukhas_pwm.migration.read_strategy import read_memory


def test_read_shadow_logs_and_returns_primary(monkeypatch, capsys, tmp_path):
    legacy = LegacyJSONL(str(tmp_path / "legacy.jsonl"))
    dna = InMemoryHelix()
    # seed different versions
    legacy.write("k", "legacy", version=1, strength=0.5, meta={})
    dna.write("k", "dna", version=2, strength=0.5, meta={})

    # shadow (primary legacy)
    monkeypatch.setenv("FLAG_DNA_READ_SHADOW", "true")
    monkeypatch.delenv("FLAG_DNA_CUTOVER_READ_FROM", raising=False)
    out = read_memory(legacy=legacy, dna=dna, key="k")
    assert out["value"] == "legacy"
    assert "drift" in capsys.readouterr().out.lower()

    # cutover to dna
    monkeypatch.setenv("FLAG_DNA_CUTOVER_READ_FROM", "dna")
    out2 = read_memory(legacy=legacy, dna=dna, key="k")
    assert out2["value"] == "dna"
