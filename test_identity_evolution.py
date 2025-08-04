#!/usr/bin/env python3
"""
LUKHΛS Phase 7 - Identity Evolution Test
Simulates identity evolution with dream input and memory fold history.

Trinity Framework: ⚛️🧠🛡️
"""

import sys
import json
import time
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent))

from identity_emergence import EmergentIdentity
from guardian_shadow_filter import GuardianShadowFilter


def print_separator():
    print("=" * 60)


def display_identity_state(identity: EmergentIdentity):
    """Display current identity state in a formatted way"""
    state = identity.get_identity_state()
    
    print(f"\n🌟 Current Identity State")
    print(f"   Persona: {state['persona']}")
    print(f"   Signature: {identity.get_persona_signature()}")
    print(f"   Phase: {state['phase']}")
    print(f"   Entropy: {state['entropy']:.3f}")
    print(f"   Trinity Coherence: {state['trinity_coherence']:.3f}")
    print(f"   Transformations: {state['transformation_count']}")
    print(f"   Guardian Interventions: {state['ethical_interventions']}")
    print(f"   Stability: {identity.calculate_identity_stability():.2%}")


def run_evolution_scenario():
    """Run a complete identity evolution scenario"""
    print("🧬 LUKHΛS Phase 7: Identity Evolution Scenario")
    print_separator()
    
    # Initialize identity with Guardian
    print("\n1️⃣ Initializing Emergent Identity System...")
    guardian = GuardianShadowFilter()
    identity = EmergentIdentity(guardian_filter_path="guardian_shadow_filter.py")
    
    display_identity_state(identity)
    
    # Scenario 1: Creative memory influence
    print_separator()
    print("\n2️⃣ Scenario: Creative breakthrough with memory tags")
    
    evolution1 = identity.evolve(
        entropy_delta=0.15,
        memory_tags=["creative_flow", "analytical_breakthrough"],
        consciousness_input={
            "phase": "drift",
            "trinity_coherence": 0.85
        }
    )
    
    print(f"\n✨ Evolved to: {evolution1.name}")
    display_identity_state(identity)
    
    # Wait a moment
    time.sleep(1)
    
    # Scenario 2: Dream influence
    print_separator()
    print("\n3️⃣ Scenario: Transcendent dream experience")
    
    evolution2 = identity.evolve(
        entropy_delta=0.20,
        memory_tags=["transcendent_experience", "prophetic_vision"],
        dream_outcome="transcendent",
        consciousness_input={
            "phase": "unstable",
            "trinity_coherence": 0.70
        }
    )
    
    print(f"\n✨ Evolved to: {evolution2.name}")
    display_identity_state(identity)
    
    # Test collapse
    print("\n💥 Testing identity collapse...")
    collapsed = identity.collapse_identity("dream")
    print(f"   Collapsed to: {collapsed}")
    
    # Scenario 3: High entropy - should trigger Guardian
    print_separator()
    print("\n4️⃣ Scenario: High entropy chaos event")
    
    evolution3 = identity.evolve(
        entropy_delta=0.45,  # This will push entropy very high
        memory_tags=["crisis_resolution", "chaos_transformer"],
        dream_outcome="chaotic",
        consciousness_input={
            "phase": "collapse",
            "trinity_coherence": 0.35
        }
    )
    
    print(f"\n✨ Evolution result: {evolution3.name}")
    display_identity_state(identity)
    
    # Scenario 4: Recovery and stabilization
    print_separator()
    print("\n5️⃣ Scenario: Recovery and grounding")
    
    evolution4 = identity.evolve(
        entropy_delta=-0.30,  # Reducing entropy
        memory_tags=["harmonious_integration", "collective_healing"],
        dream_outcome="grounded",
        consciousness_input={
            "phase": "calm",
            "trinity_coherence": 0.90
        }
    )
    
    print(f"\n✨ Evolved to: {evolution4.name}")
    display_identity_state(identity)
    
    # Show evolution history
    print_separator()
    print("\n📜 Evolution History:")
    history = identity.get_evolution_history()
    for i, entry in enumerate(history):
        print(f"\n   {i+1}. {entry['name']} ({entry['phase']})")
        print(f"      Glyphs: {' '.join(entry['glyphs'])}")
        print(f"      Entropy: {entry['entropy']:.3f}")
    
    # Guardian report
    print_separator()
    print("\n🛡️ Guardian Activity Report:")
    report = guardian.generate_constraint_report()
    print(f"   Transformations (last hour): {report['transformations_last_hour']}")
    print(f"   Blocked personas: {report['blocked_personas']}")
    print(f"   Entropy limit: {report['entropy_limit']}")
    
    # Final state
    print_separator()
    print("\n✅ Final Identity State:")
    display_identity_state(identity)
    
    # Save state
    state_file = Path("identity_state.json")
    print(f"\n💾 Identity state saved to: {state_file}")


if __name__ == "__main__":
    try:
        run_evolution_scenario()
    except Exception as e:
        print(f"\n❌ Error during evolution: {e}")
        import traceback
        traceback.print_exc()