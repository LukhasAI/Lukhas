from lukhas_pwm.dna.memory_inmem import InMemoryHelix
from lukhas_pwm.migration.dual_write import write_memory_dual
from lukhas_pwm.migration.legacy_jsonl import LegacyJSONL


def test_dual_write_toggle(monkeypatch, tmp_path):
    legacy_path = tmp_path / "legacy.jsonl"
    legacy = LegacyJSONL(str(legacy_path))
    dna = InMemoryHelix()

    # default: legacy only
    monkeypatch.delenv("FLAG_DNA_DUAL_WRITE", raising=False)
    write_memory_dual(
        legacy=legacy, dna=dna, key="k1", value="v1", version=1, strength=0.5
    )
    assert legacy.read("k1")["value"] == "v1"
    assert dna.read("k1") is None

    # enable dual write
    monkeypatch.setenv("FLAG_DNA_DUAL_WRITE", "true")
    write_memory_dual(
        legacy=legacy, dna=dna, key="k2", value="v2", version=2, strength=0.7
    )
    assert legacy.read("k2")["value"] == "v2"
    assert dna.read("k2")["value"] == "v2"
