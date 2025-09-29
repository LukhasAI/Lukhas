import pytest
from lukhas.qi.bio.bio_optimizer import (
    handle_failed_target,
    reset_metabolic_baseline,
    adjust_sensitivity,
    switch_backup_sensor,
    interpolate_missing_data,
    apply_smoothing_filter,
    reduce_gain,
)

def test_handle_failed_target_metabolic_drift():
    """Tests that the dispatcher correctly calls metabolic drift strategies."""
    context = {"log": []}
    results = handle_failed_target('metabolic_drift', context)

    assert "Resetting metabolic baseline" in context["log"]
    assert "Adjusting sensitivity" in context["log"]
    assert "reset_metabolic_baseline" in results
    assert "adjust_sensitivity" in results

def test_handle_failed_target_sensor_loss():
    """Tests that the dispatcher correctly calls sensor loss strategies."""
    context = {"log": []}
    results = handle_failed_target('sensor_loss', context)

    assert "Switching to backup sensor" in context["log"]
    assert "Interpolating missing data" in context["log"]
    assert "switch_backup_sensor" in results
    assert "interpolate_missing_data" in results

def test_handle_failed_target_parameter_instability():
    """Tests that the dispatcher correctly calls parameter instability strategies."""
    context = {"log": []}
    results = handle_failed_target('parameter_instability', context)

    assert "Applying smoothing filter" in context["log"]
    assert "Reducing gain" in context["log"]
    assert "apply_smoothing_filter" in results
    assert "reduce_gain" in results

def test_handle_failed_target_unknown_target():
    """Tests that the dispatcher handles unknown targets gracefully."""
    context = {"log": []}
    results = handle_failed_target('unknown_target_type', context)
    assert results == []
    assert context["log"] == []

def test_corrective_action_functions():
    """Tests the basic implementation of each corrective action."""
    context = {"log": []}

    reset_metabolic_baseline(context)
    assert "Resetting metabolic baseline" in context["log"]

    adjust_sensitivity(context)
    assert "Adjusting sensitivity" in context["log"]

    switch_backup_sensor(context)
    assert "Switching to backup sensor" in context["log"]

    interpolate_missing_data(context)
    assert "Interpolating missing data" in context["log"]

    apply_smoothing_filter(context)
    assert "Applying smoothing filter" in context["log"]

    reduce_gain(context)
    assert "Reducing gain" in context["log"]
