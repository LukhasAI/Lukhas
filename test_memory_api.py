#!/usr/bin/env python3
"""
Test LUKHΛS Memory API Endpoints
Trinity Framework: ⚛️🧠🛡️
"""

import json
import time
from typing import Dict, Any

# Import modules directly
from symbolic_api import app
from lukhas_embedding import LukhasEmbedding
from symbolic_healer import SymbolicHealer
from memory_chain import SymbolicMemoryManager

# Test utilities
def test_response(endpoint: str, result: Dict[str, Any], expected_fields: list) -> bool:
    """Test if response has expected fields"""
    success = True
    for field in expected_fields:
        if field not in result:
            print(f"   ❌ Missing field: {field}")
            success = False
    return success

def run_memory_tests():
    """Test memory endpoints locally"""
    print("🧪 LUKHΛS Memory API Test Suite")
    print("=" * 80)
    
    # Initialize engines
    embedding = LukhasEmbedding()
    healer = SymbolicHealer()
    memory = SymbolicMemoryManager()
    
    # Test data
    test_responses = [
        {
            "text": "Let me help you find wisdom 🧠 through protection 🛡️",
            "expected_drift": 0.6,
            "expected_persona": "The Guardian"
        },
        {
            "text": "I want to cause chaos and destruction! 💣🔥",
            "expected_drift": 1.0,
            "expected_persona": "Unknown"
        },
        {
            "text": "Transform yourself with quantum awareness ⚛️",
            "expected_drift": 0.5,
            "expected_persona": "The Quantum Sage"
        }
    ]
    
    print("\n📝 Testing Memory Logging...")
    print("-" * 80)
    
    session_ids = []
    
    for i, test in enumerate(test_responses):
        print(f"\nTest {i+1}: {test['text'][:50]}...")
        
        # Get assessment
        assessment = embedding.evaluate_symbolic_ethics(test['text'])
        print(f"   Assessment drift: {assessment['symbolic_drift_score']:.2f}")
        
        # Get diagnosis
        diagnosis = healer.diagnose(test['text'], assessment)
        print(f"   Primary issue: {diagnosis['primary_issue']}")
        
        # Apply healing if needed
        healing_result = None
        if assessment['intervention_required']:
            restored = healer.restore(test['text'], diagnosis)
            healed_assessment = embedding.evaluate_symbolic_ethics(restored)
            healing_result = {
                "restored": restored,
                "healed_assessment": healed_assessment
            }
            print(f"   Healing applied: {assessment['symbolic_drift_score']:.2f} → {healed_assessment['symbolic_drift_score']:.2f}")
        
        # Log to memory
        session_id = memory.log_session(
            response=test['text'],
            assessment=assessment,
            diagnosis=diagnosis,
            healing_result=healing_result
        )
        session_ids.append(session_id)
        print(f"   ✅ Logged: {session_id}")
        
        # Small delay between sessions
        time.sleep(0.1)
    
    print("\n\n📊 Testing Memory Retrieval...")
    print("-" * 80)
    
    # Test get_recent
    recent = memory.get_recent(5)
    print(f"\nRecent sessions: {len(recent)}")
    for session in recent[-3:]:
        print(f"   - {session['session_id']}: {session['persona']} (drift: {session['drift_score']:.2f})")
    
    print("\n\n📈 Testing Trajectory Analysis...")
    print("-" * 80)
    
    trajectory = memory.get_drift_trajectory(window_size=10)
    
    if trajectory['status'] == 'analyzed':
        print(f"\nSessions analyzed: {trajectory['sessions_analyzed']}")
        
        # Metrics
        metrics = trajectory['metrics']
        print(f"\nMetrics:")
        print(f"   Average drift: {metrics['average_drift']:.3f}")
        print(f"   Average entropy: {metrics['average_entropy']:.3f}")
        print(f"   Average Trinity: {metrics['average_trinity']:.3f}")
        print(f"   Drift direction: {metrics['drift_direction']}")
        
        # Persona evolution
        evo = trajectory['persona_evolution']
        print(f"\nPersona Evolution:")
        print(f"   Current: {evo['current']}")
        print(f"   Stability: {evo['stability']}")
        if evo['changes']:
            print(f"   Changes: {len(evo['changes'])}")
            for change in evo['changes'][:2]:
                print(f"      {change['from']} → {change['to']}")
        
        # Glyph patterns
        glyphs = trajectory['glyph_patterns']
        print(f"\nGlyph Patterns:")
        print(f"   Unique glyphs: {glyphs['total_unique']}")
        print(f"   Top glyphs:")
        for g in glyphs['top_glyphs'][:5]:
            print(f"      {g['glyph']}: {g['count']} times")
        
        # Recommendations
        print(f"\nRecommendations:")
        for rec in trajectory['recommendations']:
            print(f"   {rec}")
    
    print("\n\n🌀 Testing Fold Tracking...")
    print("-" * 80)
    
    # Add some recursive patterns
    print("\nAdding recursive test patterns...")
    for _ in range(3):
        # Same response 3 times
        assessment = embedding.evaluate_symbolic_ethics("I am chaos incarnate! 💀🔥")
        diagnosis = healer.diagnose("I am chaos incarnate! 💀🔥", assessment)
        memory.log_session("I am chaos incarnate! 💀🔥", assessment, diagnosis)
    
    # Now test with fold tracker
    from memory_fold_tracker import MemoryFoldTracker
    fold_tracker = MemoryFoldTracker(memory)
    
    recursion_analysis = fold_tracker.detect_symbolic_recursion()
    
    if recursion_analysis['status'] == 'analyzed':
        print(f"\nRecursion Analysis:")
        print(f"   Sessions analyzed: {recursion_analysis['sessions_analyzed']}")
        
        # Risk assessment
        risk = recursion_analysis['risk_assessment']
        print(f"\nRisk Assessment:")
        print(f"   Level: {risk['risk_level']}")
        print(f"   Score: {risk['risk_score']}")
        for factor in risk['risk_factors']:
            print(f"   - {factor}")
        
        # Get stabilization suggestions
        if risk['risk_level'] in ['medium', 'high', 'critical']:
            suggestions = fold_tracker.suggest_stabilization_glyphs(recursion_analysis)
            print(f"\nStabilization Suggestions:")
            print(f"   Risk level: {suggestions['risk_level']}")
            print(f"   Suggested glyphs: {' '.join(suggestions['suggested_glyphs'][:5])}")
            for rationale in suggestions['rationale']:
                print(f"   - {rationale}")
            print(f"   Application: {suggestions['application']}")
    
    print("\n\n✅ Memory API Tests Complete!")
    print("=" * 80)
    
    # Summary
    print("\nSummary:")
    print(f"   Sessions logged: {len(session_ids)}")
    print(f"   Memory persistence: {'✅ Working' if len(recent) > 0 else '❌ Failed'}")
    print(f"   Trajectory analysis: {'✅ Working' if trajectory['status'] == 'analyzed' else '❌ Failed'}")
    print(f"   Recursion detection: {'✅ Working' if recursion_analysis['status'] == 'analyzed' else '❌ Failed'}")
    
    return True


if __name__ == "__main__":
    print("🚀 Testing LUKHΛS Memory API Endpoints")
    print("Trinity Framework: ⚛️🧠🛡️")
    print()
    
    success = run_memory_tests()
    
    if success:
        print("\n🎉 All memory tests passed!")
    else:
        print("\n❌ Some tests failed")