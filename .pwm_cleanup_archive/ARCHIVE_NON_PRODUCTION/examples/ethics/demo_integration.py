#!/usr/bin/env python3
"""
Demo Integration: Tuner + Visualizer
Shows integrated workflow of stabilization and visualization

ΛTAG: TUNER_DEMO
"""

import asyncio
import os
import sys

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from ethics.stabilization.tuner import AdaptiveEntanglementStabilizer
from ethics.tools.quantum_mesh_visualizer import QuantumMeshVisualizer


async def demo_integrated_workflow():
    """Demonstrate integrated stabilization and visualization workflow"""
    print("🔧🎨 Integrated Tuner + Visualizer Demo")
    print("=" * 50)

    # Initialize components
    stabilizer = AdaptiveEntanglementStabilizer()
    visualizer = QuantumMeshVisualizer()

    # Step 1: Load and visualize initial state
    print("\n📊 Step 1: Initial Mesh Analysis")
    initial_data = visualizer.load_entanglement_data(live_mode=True)

    print(f"   Mesh Score: {initial_data['unified_field']['mesh_ethics_score']:.3f}")
    print(f"   Risk Level: {initial_data['unified_field']['risk_level']}")
    print(f"   Conflicts: {len(initial_data.get('conflicts', []))}")

    # Step 2: Monitor for instabilities
    print("\n🔍 Step 2: Instability Detection")

    # Simulate loading from log data (using live data for demo)
    trend_data = [initial_data]  # In real scenario, this would be from logs
    stabilizer._update_trends(trend_data)

    unstable_pairs = stabilizer.detect_instability(trend_data)

    if unstable_pairs:
        print(f"   ⚠️  Found {len(unstable_pairs)} unstable pairs:")
        for pair in unstable_pairs:
            print(f"      - {pair[0]}↔{pair[1]}")
    else:
        print("   ✅ No instabilities detected")

    # Step 3: Apply stabilizations
    if unstable_pairs:
        print("\n🛠️  Step 3: Applying Stabilizations")

        for pair in unstable_pairs:
            stabilizers = stabilizer.select_stabilizers(pair)
            print(f"   {pair[0]}↔{pair[1]}: {', '.join(stabilizers)}")

            # Apply with suggestion mode
            stabilizer.suggest_only_mode = True
            stabilizer.apply_symbolic_correction(pair, stabilizers)

    # Step 4: Generate post-stabilization report
    print("\n📈 Step 4: Post-Stabilization Analysis")

    # Export detailed report
    report_path = "ethics/stabilization/demo_report.md"
    visualizer.export_visual_summary(initial_data, report_path, format_type="markdown")
    print(f"   📄 Report exported: {report_path}")

    # Show stabilizer status
    status = stabilizer.get_stabilization_status()
    print(f"   📊 Actions taken: {status['stabilization_history_count']}")
    print(f"   🎯 Suggest-only mode: {status['suggest_only_mode']}")

    # Step 5: Create dashboard
    print("\n🎨 Step 5: Dashboard Generation")
    dashboard_path = visualizer.generate_interactive_dashboard(initial_data)
    print(f"   🖥️  Dashboard: {dashboard_path}")

    print("\n✅ Demo Complete!")
    print("Integration points:")
    print("  • Visualizer provides mesh state analysis")
    print("  • Tuner detects instabilities and selects stabilizers")
    print("  • Both emit structured logs for monitoring")
    print("  • Dashboard shows real-time stabilization effects")


def demo_stabilizer_catalog():
    """Demonstrate the symbolic stabilizer catalog"""
    print("\n🏷️  Symbolic Stabilizer Catalog")
    print("=" * 40)

    from ethics.stabilization.tuner import SymbolicStabilizer

    stabilizers = SymbolicStabilizer.STABILIZERS

    categories = {
        "Harmony & Balance": ["ΛHARMONY", "ΛBALANCE", "ΛANCHOR"],
        "Emotional": ["ΛCALM", "ΛREFLECT", "ΛRESOLVE"],
        "Cognitive": ["ΛFOCUS", "ΛCLARITY", "ΛMEANING"],
        "Emergency": ["ΛRESET", "ΛFREEZE"],
    }

    for category, tags in categories.items():
        print(f"\n{category}:")
        for tag in tags:
            if tag in stabilizers:
                info = stabilizers[tag]
                print(f"  {tag}: {info['description']}")
                print(f"    Strength: {info['strength']}")
                print(f"    Duration: {info['duration_minutes']}min")
                applicable = info["applicable_pairs"]
                if applicable == ["*"]:
                    print("    Scope: Universal")
                else:
                    print(f"    Scope: {', '.join(applicable[:3])}")


if __name__ == "__main__":
    print("🚀 LUKHAS AGI: Adaptive Entanglement Stabilization Demo")

    demo_stabilizer_catalog()

    print("\n" + "=" * 60)

    # Run the integrated demo
    asyncio.run(demo_integrated_workflow())

## CLAUDE CHANGELOG
# - Created integrated demo showing tuner + visualizer workflow # CLAUDE_EDIT_v0.1
# - Demonstrated symbolic stabilizer catalog with categories # CLAUDE_EDIT_v0.1
# - Showed end-to-end instability detection and correction process # CLAUDE_EDIT_v0.1
