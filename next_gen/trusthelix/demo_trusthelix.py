#!/usr/bin/env python3
"""
TrustHelix Demo - Shows the complete ethical audit system in action
"""
import time
import streamlit as st

import asyncio
import logging

from core.consent_path import ConsentPathLogger
from core.drift_tracker import DriftTracker
from core.mutation_tree import SymbolicMutationTree

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%H:%M:%S")


async def demo_trusthelix():
    """Demonstrate TrustHelix features with a user journey"""

    print("🌳 TRUSTHELIX DEMO - Ethical Audit System")
    print("=" * 60)

    # Initialize components
    mutation_tree = SymbolicMutationTree()
    drift_tracker = DriftTracker()
    consent_logger = ConsentPathLogger(":memory:")  # In-memory for demo

    # Test user
    user_id = "alice_tier5"
    initial_glyphs = ["🔐", "🧬", "🪷"]

    print(f"\n👤 User: {user_id}")
    print(f"🎭 Initial glyphs: {' '.join(initial_glyphs}")
    print("\n" + "-" * 60)

    # Simulate user journey
    actions = [
        ("authenticate", "success", "User logs in normally"),
        ("unlock_profile", "success", "Views their profile"),
        ("consent_granted", "success", "Grants new permissions"),
        ("view_data", "success", "Accesses personal data"),
        ("suspicious_attempt", "failure", "Unusual access pattern detected"),
        ("authenticate", "failure", "Failed login attempt"),
        ("emergency_access", "partial", "Recovery mode activated"),
    ]

    current_glyphs = initial_glyphs.copy()

    for i, (action, outcome, description) in enumerate(actions):
        print(f"\n🎬 Action {i + 1}: {action}")
        print(f"   Description: {description}")
        print(f"   Current glyphs: {' '.join(current_glyphs}")

        # Track in mutation tree
        new_glyphs, drift_score = mutation_tree.track_action(user_id, current_glyphs, action, outcome)

        # Calculate entropy
        entropy = mutation_tree.calculate_entropy()

        # Track drift
        drift_event = drift_tracker.record_drift(
            user_id,
            drift_score,
            action,
            entropy,
            {"outcome": outcome, "description": description},
        )

        # Log consent
        consent_entry = consent_logger.log_consent(
            user_id,
            new_glyphs,
            action,
            outcome,
            drift_score,
            {"entropy": entropy, "description": description},
        )

        # Show results
        print(f"   → New glyphs: {' '.join(new_glyphs}")
        print(f"   → Drift: {drift_score:.3f} {drift_event.state_emoji}")
        print(f"   → Consent hash: {consent_entry.consent_hash[:16]}...")

        current_glyphs = new_glyphs

        # Brief pause for readability
        await asyncio.sleep(0.5)

    # Show final analysis
    print("\n" + "=" * 60)
    print("📊 FINAL ANALYSIS")
    print("=" * 60)

    # Mutation tree visualization
    print("\n" + mutation_tree.visualize_tree())

    # Drift analysis
    print("\n🌀 Drift Analysis:")
    analysis = drift_tracker.get_drift_analysis(user_id, "immediate")
    print(f"   Average drift: {analysis['avg_drift']:.3f}")
    print(f"   Dominant state: {analysis['dominant_state']}")
    print("   Recommendations:")
    for rec in analysis["recommendations"]:
        print(f"      {rec}")

    # Pattern insights
    print("\n🔍 Pattern Insights:")
    patterns = drift_tracker.get_pattern_insights()
    for insight in patterns["insights"]:
        print(f"   {insight}")

    # Consent path
    print("\n" + consent_logger.export_path_visualization(user_id))

    # Integrity check
    valid, errors = consent_logger.verify_path_integrity(user_id)
    if valid:
        print("\n✅ Consent path integrity verified - no tampering detected")
    else:
        print("\n❌ Consent path integrity issues:")
        for error in errors:
            print(f"   - {error}")

    print("\n🌳 TrustHelix demo complete!")


if __name__ == "__main__":
    asyncio.run(demo_trusthelix())
