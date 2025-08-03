#!/usr/bin/env python3
"""
Test the Mutation Tree component of TrustHelix
"""

import logging
from core.mutation_tree import SymbolicMutationTree

logging.basicConfig(level=logging.INFO, format='%(message)s')


def test_mutation_tree():
    """Test the mutation tree functionality"""
    
    print("🌳 TRUSTHELIX MUTATION TREE TEST")
    print("=" * 60)
    
    # Initialize tree
    tree = SymbolicMutationTree()
    
    # Test user
    user_id = "test_user_001"
    glyphs = ["🔐", "🧬", "🪷"]
    
    print(f"\n👤 User: {user_id}")
    print(f"🎭 Initial glyphs: {' '.join(glyphs)}")
    print("\n" + "-" * 60)
    
    # Test sequence of actions
    test_actions = [
        ("authenticate", "success", "Normal login"),
        ("unlock_profile", "success", "Profile access"),
        ("consent_granted", "success", "New permissions"),
        ("suspicious_attempt", "failure", "Anomaly detected"),
        ("failed_auth", "failure", "Wrong password"),
        ("authenticate", "success", "Successful retry"),
        ("view_data", "success", "Data access")
    ]
    
    for action, outcome, description in test_actions:
        print(f"\n🎬 Action: {action}")
        print(f"   Description: {description}")
        print(f"   Current glyphs: {' '.join(glyphs)}")
        
        # Track action
        new_glyphs, drift = tree.track_action(user_id, glyphs, action, outcome)
        
        print(f"   → New glyphs: {' '.join(new_glyphs)}")
        print(f"   → Drift: {drift:.3f} {tree.get_drift_state().value}")
        
        glyphs = new_glyphs
    
    # Show final state
    print("\n" + "=" * 60)
    print(tree.visualize_tree())
    
    # Show consent path
    print("\n📜 User Consent Path:")
    path = tree.get_consent_path(user_id)
    for i, entry in enumerate(path):
        print(f"   [{i+1}] {' '.join(entry['glyphs'])} - {entry['action']} ({entry['drift_state']})")
    
    # Calculate final entropy
    entropy = tree.calculate_entropy()
    print(f"\n📊 System Entropy: {entropy:.3f}")
    
    # Export mutation log
    mutations = tree.export_mutation_log()
    print(f"\n🔄 Total Mutations: {len(mutations)}")
    print("   Recent mutations:")
    for mut in mutations[-3:]:
        print(f"   • {mut['from_glyph']} → {mut['to_glyph']} ({mut['reason']})")
    
    print("\n✅ Mutation tree test complete!")


if __name__ == "__main__":
    test_mutation_tree()