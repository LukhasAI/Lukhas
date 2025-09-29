#!/usr/bin/env python3
"""
Wave C C5 Observability Integration Test
=======================================

Demonstrates the observability system integrated with Aka Qualia components.
"""

import json
import time

from lukhas.aka_qualia.monitoring_dashboard import MonitoringDashboard

from lukhas.aka_qualia.memory_noop import NoopMemory
from lukhas.aka_qualia.observability import (
    AkaqMetrics,
    get_observability,
    measure_scene_processing,
    record_glyph_mapped,
    record_scene_processed,
    update_consciousness_metrics,
)


def demo_scene_processing():
    """Demo phenomenological scene processing with observability"""
    print("🧠 Demo: Scene Processing with Observability")

    get_observability()

    # Simulate scene processing stages
    with measure_scene_processing("glyph_mapping", "complex"):
        print("  📊 Measuring GLYPH mapping...")
        time.sleep(0.05)  # Simulate processing time

    with measure_scene_processing("router_dispatch", "high_priority"):
        print("  📊 Measuring router dispatch...")
        time.sleep(0.02)  # Simulate processing time

    with measure_scene_processing("memory_persistence", "normal"):
        print("  📊 Measuring memory persistence...")
        time.sleep(0.03)  # Simulate processing time

    # Record events
    record_scene_processed(user_tier="premium", status="success")
    record_glyph_mapped(glyph_type="vigilance", cache_status="hit", accuracy=0.95, palette_bias="aka_bias")
    record_glyph_mapped(glyph_type="grounding_hint", cache_status="miss", accuracy=0.87, palette_bias="neutral")

    # Update consciousness metrics
    consciousness_metrics = AkaqMetrics(
        drift_phi=0.08,
        congruence_index=0.92,
        neurosis_risk=0.03,
        regulation_intensity=0.4,
        glyph_coverage=0.89,
        router_priority=0.7,
        memory_efficiency=0.94,
        dream_coherence=0.83,
    )

    update_consciousness_metrics(consciousness_metrics, user_id="demo_user")

    print("  ✅ Scene processing metrics recorded")
    return consciousness_metrics


def demo_memory_operations():
    """Demo memory operations with observability"""
    print("🧠 Demo: Memory Operations with Observability")

    obs = get_observability()
    memory = NoopMemory()

    # Simulate memory operations with observability
    test_scenes = [
        {"subject": "demo_scene_1", "object": "test_object", "affect": {"vigilance": 0.6}},
        {"subject": "demo_scene_2", "object": "test_object", "affect": {"vigilance": 0.4}},
        {"subject": "demo_scene_3", "object": "test_object", "affect": {"vigilance": 0.8}},
    ]

    for i, scene in enumerate(test_scenes):
        scene_id = memory.save(
            user_id=f"demo_user_{i}",
            scene=scene,
            glyphs=[{"key": f"demo_glyph_{i}", "attrs": {}}],
            policy={"gain": 0.8},
            metrics={"drift_phi": 0.05 * i},
            cfg_version="c5_demo",
        )
        print(f"  📝 Saved scene: {scene_id}")

        # Simulate retrieval
        history = memory.history(user_id=f"demo_user_{i}", limit=1)
        print(f"  📚 Retrieved {len(history)} scenes from history")

    # Update memory metrics
    obs.update_memory_storage("noop", "scenes", len(test_scenes) * 512)
    obs.update_system_health("memory", True)

    print(f"  ✅ Memory operations completed ({len(test_scenes)} scenes)")
    return len(test_scenes)


def demo_monitoring_dashboard():
    """Demo monitoring dashboard"""
    print("🖥️  Demo: Monitoring Dashboard")

    dashboard = MonitoringDashboard(port=8089)  # Use different port to avoid conflicts

    try:
        dashboard.start()

        if dashboard.is_running():
            status = dashboard.get_status()
            print("  📊 Dashboard URLs:")
            print(f"    Main:    {status['dashboard_url']}")
            print(f"    Metrics: {status['metrics_url']}")
            print(f"    Health:  {status['health_url']}")

            # Let it run briefly
            time.sleep(2)
            print("  ✅ Dashboard demo completed")

            dashboard.stop()
            return True
        else:
            print("  ❌ Failed to start dashboard")
            return False

    except Exception as e:
        print(f"  ❌ Dashboard demo failed: {e}")
        return False


def test_prometheus_metrics():
    """Test Prometheus metrics export"""
    print("📈 Demo: Prometheus Metrics Export")

    obs = get_observability()

    # Generate some test data
    for i in range(5):
        record_scene_processed(status="success")
        record_glyph_mapped(glyph_type=f"test_glyph_{i}", accuracy=0.9 + (i * 0.02))

    # Export metrics
    metrics_data = obs.export_prometheus_metrics()
    metrics_text = metrics_data.decode("utf-8")

    print(f"  📊 Exported {len(metrics_text)} characters of metrics data")
    print("  📋 Sample metrics:")

    lines = metrics_text.split("\n")
    for line in lines[:10]:  # Show first 10 lines
        if line and not line.startswith("#"):
            print(f"    {line}")

    # Assert instead of return
    assert len(metrics_text) > 0, "Metrics data should be generated"
    assert "akaq_" in metrics_text, "Metrics should contain akaq prefixes"


def main():
    """Run Wave C C5 observability integration demo"""
    print("🚀 Wave C C5 Observability Integration Demo")
    print("=" * 50)

    # Check observability system health
    obs = get_observability()
    health = obs.health_check()
    print(f"🏥 Observability Health: {json.dumps(health, indent=2)}")
    print()

    results = {}

    # Demo scene processing
    try:
        demo_scene_processing()
        results["scene_processing"] = "✅ Success"
    except Exception as e:
        results["scene_processing"] = f"❌ Failed: {e}"
    print()

    # Demo memory operations
    try:
        scenes_processed = demo_memory_operations()
        results["memory_operations"] = f"✅ Success ({scenes_processed} scenes)"
    except Exception as e:
        results["memory_operations"] = f"❌ Failed: {e}"
    print()

    # Demo Prometheus metrics
    try:
        metrics_success = test_prometheus_metrics()
        results["prometheus_export"] = "✅ Success" if metrics_success else "❌ Failed"
    except Exception as e:
        results["prometheus_export"] = f"❌ Failed: {e}"
    print()

    # Demo dashboard (optional)
    try:
        dashboard_success = demo_monitoring_dashboard()
        results["monitoring_dashboard"] = "✅ Success" if dashboard_success else "❌ Failed"
    except Exception as e:
        results["monitoring_dashboard"] = f"❌ Failed: {e}"
    print()

    # Final metrics summary
    print("📊 Final Metrics Summary:")
    final_summary = obs.get_metrics_summary()
    print(json.dumps(final_summary, indent=2))
    print()

    # Results summary
    print("📋 Demo Results Summary:")
    for component, result in results.items():
        print(f"  {result:30} {component}")

    all_success = all("✅" in result for result in results.values())
    print()
    if all_success:
        print("🎉 Wave C C5 Observability Integration: ALL DEMOS SUCCESSFUL!")
    else:
        print("⚠️  Some demos had issues - check results above")

    return all_success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
