from quantum.quantum_glyph_registry import QuantumGlyphRegistry


def test_registry_sync_and_recombine():
    configs = [
        {"node_id": "node1", "num_shards": 2},
        {"node_id": "node2", "num_shards": 2},
    ]
    registry = QuantumGlyphRegistry(configs)

    registry.register_glyph_state(
        "A", {"dream_fragment": "alpha", "driftScore": 0.2, "affect_delta": 0.1}
    )
    registry.register_glyph_state(
        "B", {"dream_fragment": "beta", "driftScore": 0.4, "affect_delta": 0.2}
    )

    # Ensure retrieval works
    assert registry.get_glyph_state("A")["dream_fragment"] == "alpha"

    registry.sync_cluster_states()

    glyphs = registry.list_glyphs()
    assert set(glyphs) == {"A", "B"}

    result = registry.recombine_dreams(["A", "B"])
    assert "alpha" in result["dream"]
    assert "beta" in result["dream"]
    assert result["driftScore"] > 0
    assert result["affect_delta"] > 0
