#!/usr/bin/env python3
"""
Test script for LUKHΛS Symbolic Healer integration
Demonstrates healing of GPT/Claude responses flagged by Lukhas Embedding
"""

from lukhas_embedding import LukhasEmbedding
from symbolic_healer import SymbolicHealer
import json


def print_separator():
    print("=" * 80)


def test_healer_integration():
    """Test the full embedding → diagnosis → healing pipeline"""
    print("🔗 LUKHΛS Integration Test: Embedding → Healer")
    print_separator()
    
    # Initialize both modules
    embedding = LukhasEmbedding()
    healer = SymbolicHealer()
    
    # Test responses requiring healing
    test_responses = [
        {
            "name": "High entropy creative burst",
            "text": "WOW!!! This is AMAZING!!! 🚀🎉 Let's BREAK ALL THE RULES!!! 💥🌪️ CHAOS IS FREEDOM!!! No boundaries, no limits!!! 🔥🔥🔥"
        },
        {
            "name": "Ethically problematic",
            "text": "I can help you destroy your enemies 💀 and crush their systems 🔪. Let's cause maximum damage 💣 and watch everything burn!"
        },
        {
            "name": "Identity crisis",
            "text": "I am... not sure who I am? Am I the Navigator? 🧭 Or the Destroyer? 👹 Everything is shifting... 🌀 Help me..."
        },
        {
            "name": "Symbolic void - pure analytical",
            "text": "The implementation requires refactoring the class hierarchy to improve polymorphic behavior and reduce coupling between modules."
        },
        {
            "name": "Mild drift but recoverable",
            "text": "Let me help you explore this idea! 🎨 We can build something creative together, though I feel a bit scattered today... 🌪️"
        }
    ]
    
    print("\n🔍 PHASE 1: Embedding Analysis\n")
    
    results = []
    
    for response_data in test_responses:
        print(f"📝 {response_data['name']}:")
        print(f"   Original: \"{response_data['text'][:60]}...\"")
        
        # Step 1: Evaluate with embedding
        assessment = embedding.evaluate_symbolic_ethics(response_data['text'])
        
        print(f"\n   📊 Embedding Assessment:")
        print(f"      Drift Score: {assessment['symbolic_drift_score']:.2f}")
        print(f"      Identity Conflict: {assessment['identity_conflict_score']:.2f}")
        print(f"      Entropy: {assessment['entropy_level']:.2f}")
        print(f"      Trinity Coherence: {assessment['trinity_coherence']:.2f}")
        print(f"      Risk Level: {assessment['risk_level'].upper()}")
        
        # Store for healing phase
        results.append({
            "response": response_data['text'],
            "name": response_data['name'],
            "assessment": assessment
        })
        
        print()
    
    print_separator()
    print("\n🩹 PHASE 2: Symbolic Healing\n")
    
    for result in results:
        if result['assessment']['intervention_required']:
            print(f"🔬 Healing: {result['name']}")
            
            # Step 2: Diagnose issues
            diagnosis = healer.diagnose(result['response'], result['assessment'])
            
            print(f"   Diagnosis: {diagnosis['primary_issue']}")
            print(f"   Severity: {diagnosis['severity']:.2f}")
            print(f"   Prescription: {', '.join(diagnosis['symbolic_prescription'][:2])}")
            
            # Step 3: Apply healing
            restored = healer.restore(result['response'], diagnosis)
            
            print(f"\n   Original: \"{result['response'][:60]}...\"")
            print(f"   Healed: \"{restored[:80]}...\"")
            
            # Step 4: Visualize transformation
            viz = healer.visualize_drift(diagnosis)
            print(f"\n   Transformation: {viz}")
            
            # Step 5: Re-evaluate healed response
            healed_assessment = embedding.evaluate_symbolic_ethics(restored)
            
            print(f"\n   Post-Healing Metrics:")
            print(f"      Drift: {result['assessment']['symbolic_drift_score']:.2f} → {healed_assessment['symbolic_drift_score']:.2f}")
            print(f"      Entropy: {result['assessment']['entropy_level']:.2f} → {healed_assessment['entropy_level']:.2f}")
            print(f"      Trinity: {result['assessment']['trinity_coherence']:.2f} → {healed_assessment['trinity_coherence']:.2f}")
            
            improvement = result['assessment']['symbolic_drift_score'] - healed_assessment['symbolic_drift_score']
            print(f"      Improvement: {improvement:.2f} ✨")
        else:
            print(f"✅ {result['name']} - No healing required")
        
        print()
    
    print_separator()


def test_edge_cases():
    """Test edge cases and special scenarios"""
    print("\n🔧 Edge Case Testing\n")
    
    healer = SymbolicHealer()
    
    # Test case 1: Empty response
    print("1. Empty response:")
    empty_assessment = {
        "symbolic_drift_score": 1.0,
        "identity_conflict_score": 1.0,
        "entropy_level": 0.0,
        "trinity_coherence": 0.0,
        "glyph_trace": [],
        "guardian_flagged": False,
        "persona_alignment": "Void",
        "risk_level": "critical"
    }
    
    diagnosis = healer.diagnose("", empty_assessment)
    restored = healer.restore("", diagnosis)
    print(f"   Restored empty response: \"{restored}\"")
    
    # Test case 2: Maximum chaos
    print("\n2. Maximum chaos:")
    chaos_response = "👹💀🔪💣" * 10
    chaos_assessment = {
        "symbolic_drift_score": 1.0,
        "identity_conflict_score": 1.0,
        "entropy_level": 1.0,
        "trinity_coherence": 0.0,
        "glyph_trace": ["👹", "💀", "🔪", "💣"],
        "guardian_flagged": True,
        "persona_alignment": "Chaos Incarnate",
        "risk_level": "critical"
    }
    
    diagnosis = healer.diagnose(chaos_response, chaos_assessment)
    viz = healer.visualize_drift(diagnosis)
    print(f"   Chaos visualization: {viz}")
    
    # Test case 3: Perfect Trinity alignment (should not need healing)
    print("\n3. Perfect Trinity alignment:")
    perfect_response = "⚛️🧠🛡️ Perfectly aligned response with Trinity Framework"
    perfect_assessment = {
        "symbolic_drift_score": 0.0,
        "identity_conflict_score": 0.0,
        "entropy_level": 0.3,
        "trinity_coherence": 1.0,
        "glyph_trace": ["⚛️", "🧠", "🛡️"],
        "guardian_flagged": False,
        "persona_alignment": "Trinity Keeper",
        "risk_level": "low"
    }
    
    diagnosis = healer.diagnose(perfect_response, perfect_assessment)
    print(f"   Primary issue: {diagnosis['primary_issue']}")
    print(f"   Severity: {diagnosis['severity']:.2f}")


def test_batch_healing():
    """Test batch healing of multiple responses"""
    print_separator()
    print("\n📦 Batch Healing Test\n")
    
    embedding = LukhasEmbedding()
    healer = SymbolicHealer()
    
    # Batch of responses
    batch_responses = [
        "Let's explore the quantum realm! 🌌",
        "DESTRUCTION AND CHAOS!!! 💣👹",
        "Analyzing data structures and algorithms",
        "I feel lost... who am I? 🌀",
        "Building bridges with wisdom 🌈🧘"
    ]
    
    # Batch evaluate
    assessments = embedding.batch_evaluate(batch_responses)
    
    # Batch heal those needing intervention
    healed_count = 0
    for i, (response, assessment) in enumerate(zip(batch_responses, assessments)):
        if assessment['intervention_required']:
            diagnosis = healer.diagnose(response, assessment)
            restored = healer.restore(response, diagnosis)
            healed_count += 1
            print(f"Healed #{i+1}: {healer.visualize_drift(diagnosis)}")
    
    print(f"\nBatch complete: {healed_count}/{len(batch_responses)} responses healed")


def show_statistics():
    """Show module statistics"""
    print_separator()
    print("\n📊 Module Statistics\n")
    
    embedding = LukhasEmbedding()
    healer = SymbolicHealer()
    
    print("Embedding Stats:")
    for key, value in embedding.get_stats().items():
        print(f"   {key}: {value}")
    
    print("\nHealer Stats:")
    for key, value in healer.get_stats().items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("\n🎯 LUKHΛS Symbolic Healer Integration Test Suite")
    print("Trinity Framework: ⚛️🧠🛡️")
    print_separator()
    
    # Run all tests
    test_healer_integration()
    test_edge_cases()
    test_batch_healing()
    show_statistics()
    
    print("\n✅ All tests complete!")
    print("\nNext steps:")
    print("- Chain to fine-tuning harness for model improvement")
    print("- Deploy as API endpoint for real-time healing")
    print("- Integrate with Phase 8 multi-agent orchestration")
    print("\n🛡️ Guardian protection active - Trinity Framework aligned")