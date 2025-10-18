from consciousness.dream.expand import archetypes


def test_tag_identifies_hero():
    snapshot = {"confidence": 0.8}
    result = archetypes.tag(snapshot)
    assert "Hero" in result

def test_tag_identifies_shadow():
    snapshot = {"confidence": 0.2}
    result = archetypes.tag(snapshot)
    assert "Shadow" in result

def test_mesh_detects_clash():
    dreams = [
        {"confidence": 0.8},  # Hero
        {"confidence": 0.2}   # Shadow
    ]
    result = archetypes.mesh(dreams)
    assert result == "clash"

def test_mesh_detects_harmony():
    dreams = [
        {"confidence": 0.8},  # Hero
        {"confidence": 0.9}   # Hero
    ]
    result = archetypes.mesh(dreams)
    assert result == "harmony"
