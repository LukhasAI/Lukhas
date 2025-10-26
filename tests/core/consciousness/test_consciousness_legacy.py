from core.orchestration.brain.integration.brain_integration import EnhancedBrainIntegration


def test_consciousness_legacy_consensus_aligned():
    brain = EnhancedBrainIntegration(config={"consciousness_legacy": {"drift_threshold": 0.4}})

    result = brain.record_consciousness_layer_state(
        "layer-alpha",
        driftScore=0.2,
        affect_delta=0.1,
        glyph_markers=["ΛCORE"],
    )

    assert result["status"] == "aligned"
    assert result["driftScore"] <= 0.4
    assert result["agreement_ratio"] == 1.0


def test_consciousness_legacy_consensus_alert():
    brain = EnhancedBrainIntegration(config={"consciousness_legacy": {"drift_threshold": 0.25}})

    brain.record_consciousness_layer_state(
        "layer-alpha",
        driftScore=0.2,
        affect_delta=0.0,
        glyph_markers=["ΛCORE"],
    )

    alert_result = brain.record_consciousness_layer_state(
        "layer-beta",
        driftScore=0.5,
        affect_delta=0.4,
        glyph_markers=["ΛALERT"],
    )

    assert alert_result["status"] == "drift_alert"
    assert "layer-beta" in alert_result["dissenting_layers"]

    status = brain.get_comprehensive_status()
    assert status["consciousness_legacy"]["last_consensus"]["status"] == "drift_alert"
    assert status["processing_stats"]["consciousness_drift_alerts"] >= 1
    assert status["consciousness_legacy"]["drift_summary"]["layers"]
