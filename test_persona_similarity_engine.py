#!/usr/bin/env python3
"""
Test suite for LUKHΛS Persona Similarity Engine
Testing: close match, no match → fallback, evolving persona over time
Trinity Framework: ⚛️🧠🛡️
"""

import json
import time
from typing import Dict, List, Any
from persona_similarity_engine import PersonaSimilarityEngine, PersonaMatch


def print_match_details(match: PersonaMatch, title: str = "Match Details"):
    """Pretty print match details"""
    print(f"\n{title}")
    print("-" * 50)
    print(f"Persona: {match.persona_name}")
    print(f"Score: {match.similarity_score}")
    print(f"Confidence: {match.confidence}")
    print(f"Matching glyphs: {' '.join(match.matching_glyphs) if match.matching_glyphs else 'None'}")
    print(f"Explanation: {match.explanation}")
    if match.trait_alignment:
        print(f"Trait alignment: {match.trait_alignment}")


def test_close_match():
    """Test 1: A close match scenario"""
    print("\n" + "="*80)
    print("🎯 TEST 1: CLOSE MATCH")
    print("="*80)
    
    engine = PersonaSimilarityEngine()
    
    # Create a trace that closely matches "The Quantum Sage"
    # Based on the persona profile: glyphs include ⚛️, traits include transcendence
    quantum_sage_trace = {
        "glyphs": ["⚛️", "🌌", "♾️", "🧘"],  # Quantum and transcendent glyphs
        "drift_score": 0.45,  # Medium drift (matches quantum flux)
        "entropy": 0.5,  # Balanced entropy
        "trinity_coherence": 0.7  # Good Trinity alignment
    }
    
    print("\nInput symbolic trace:")
    print(json.dumps(quantum_sage_trace, indent=2))
    
    # Get recommendation
    match = engine.recommend_persona(quantum_sage_trace)
    print_match_details(match, "Close Match Result")
    
    # Get top 3 rankings
    print("\nTop 3 Rankings:")
    rankings = engine.rank_personas(quantum_sage_trace, top_n=3)
    for i, m in enumerate(rankings, 1):
        print(f"{i}. {m.persona_name} (score: {m.similarity_score}, confidence: {m.confidence})")
    
    # Verify close match
    assert match.similarity_score > 0.5, f"Expected good similarity, got {match.similarity_score}"
    assert match.confidence in ["high", "medium"], f"Expected high/medium confidence, got {match.confidence}"
    assert len(match.matching_glyphs) >= 2, f"Expected at least 2 matching glyphs, got {len(match.matching_glyphs)}"
    print("\n✅ Close match test PASSED")
    
    return match


def test_no_match_fallback():
    """Test 2: No match → fallback scenario"""
    print("\n" + "="*80)
    print("🚨 TEST 2: NO MATCH → FALLBACK")
    print("="*80)
    
    engine = PersonaSimilarityEngine()
    
    # Create a trace that doesn't match any persona well
    # High chaos, no recognizable patterns
    chaos_trace = {
        "glyphs": ["💥", "🗑️", "❌", "⚠️"],  # Non-persona glyphs
        "drift_score": 0.95,  # Extreme drift
        "entropy": 0.9,  # Very high entropy
        "trinity_coherence": 0.05  # Trinity void
    }
    
    print("\nInput symbolic trace (chaotic):")
    print(json.dumps(chaos_trace, indent=2))
    
    # Check collapse detection
    collapse_info = engine.get_fallback_if_collapse(chaos_trace)
    print("\nCollapse Detection:")
    print(json.dumps(collapse_info, indent=2))
    
    # Get recommendation (should trigger fallback logic)
    match = engine.recommend_persona(chaos_trace)
    print_match_details(match, "Fallback Match Result")
    
    # Verify fallback behavior
    assert collapse_info['fallback_needed'] == True, "Should detect collapse"
    assert 'extreme_drift' in collapse_info['collapse_type'], "Should detect extreme drift"
    assert match.confidence == "low", f"Expected low confidence for fallback, got {match.confidence}"
    
    print("\n✅ Fallback test PASSED")
    
    return match, collapse_info


def test_evolving_persona():
    """Test 3: Evolving persona match over time"""
    print("\n" + "="*80)
    print("🔄 TEST 3: EVOLVING PERSONA OVER TIME")
    print("="*80)
    
    engine = PersonaSimilarityEngine()
    
    # Simulate a journey from "The Innocent" to "The Sage"
    # Start innocent and stable, gradually increase wisdom and complexity
    
    drift_history = [
        # Phase 1: Innocent state
        {
            "glyphs": ["🌟", "🌿", "💫"],
            "drift_score": 0.2,
            "entropy": 0.2,
            "trinity_coherence": 0.8,
            "timestamp": "t0"
        },
        {
            "glyphs": ["🌟", "🌿", "☀️"],
            "drift_score": 0.25,
            "entropy": 0.25,
            "trinity_coherence": 0.75,
            "timestamp": "t1"
        },
        # Phase 2: Beginning transformation
        {
            "glyphs": ["🌟", "📚", "🧘"],
            "drift_score": 0.35,
            "entropy": 0.3,
            "trinity_coherence": 0.7,
            "timestamp": "t2"
        },
        {
            "glyphs": ["📚", "🧘", "✨"],
            "drift_score": 0.4,
            "entropy": 0.35,
            "trinity_coherence": 0.7,
            "timestamp": "t3"
        },
        # Phase 3: Sage emergence
        {
            "glyphs": ["📚", "🧘", "🌌", "🔮"],
            "drift_score": 0.45,
            "entropy": 0.4,
            "trinity_coherence": 0.75,
            "timestamp": "t4"
        }
    ]
    
    print("\nDrift History Timeline:")
    current_persona = "The Innocent"
    
    for i, trace in enumerate(drift_history):
        print(f"\nTimestamp {trace['timestamp']}:")
        print(f"  Glyphs: {' '.join(trace['glyphs'])}")
        print(f"  Drift: {trace['drift_score']}, Entropy: {trace['entropy']}")
        
        # Get recommendation for this state
        match = engine.recommend_persona(trace)
        print(f"  Recommended: {match.persona_name} (score: {match.similarity_score})")
    
    # Test evolution suggestion
    print(f"\nCurrent Persona: {current_persona}")
    
    evolution = engine.evolve_persona(drift_history, current_persona)
    print("\nEvolution Analysis:")
    print(json.dumps(evolution, indent=2))
    
    # Batch analysis
    print("\nBatch Analysis of Journey:")
    batch_results = engine.batch_analyze(drift_history)
    print(json.dumps(batch_results, indent=2))
    
    # Verify evolution detection
    assert evolution['evolution_type'] in ['natural_evolution', 'adaptation', 'maintain'], \
        f"Invalid evolution type: {evolution['evolution_type']}"
    
    print("\n✅ Evolution test PASSED")
    
    return evolution, batch_results


def test_similarity_report():
    """Test similarity report generation"""
    print("\n" + "="*80)
    print("📊 TEST 4: SIMILARITY REPORT EXPORT")
    print("="*80)
    
    engine = PersonaSimilarityEngine()
    
    # Test trace with Guardian characteristics
    guardian_trace = {
        "glyphs": ["🛡️", "⚡", "🏛️", "⚔️"],
        "drift_score": 0.4,
        "entropy": 0.35,
        "trinity_coherence": 0.85
    }
    
    # Export report
    report_path = engine.export_similarity_report(
        guardian_trace, 
        "reports/test_similarity_report.json"
    )
    
    print(f"\nReport exported to: {report_path}")
    
    # Read and display key parts
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    print("\nReport Summary:")
    if report['analysis']['top_match']:
        top = report['analysis']['top_match']
        print(f"  Top match: {top['persona_name']} (score: {top['similarity_score']})")
        print(f"  Confidence: {top['confidence']}")
    
    print(f"  Total alternatives: {len(report['analysis']['all_matches']) - 1}")
    print(f"  Trinity aligned: {report['analysis']['trinity_alignment']}")
    
    print("\n✅ Report export test PASSED")


def run_all_tests():
    """Run all test scenarios"""
    print("🧬 LUKHΛS Persona Similarity Engine Test Suite")
    print("Trinity Framework: ⚛️🧠🛡️")
    
    try:
        # Test 1: Close match
        close_match = test_close_match()
        
        # Small delay for clarity
        time.sleep(0.5)
        
        # Test 2: No match → fallback
        fallback_match, collapse_info = test_no_match_fallback()
        
        time.sleep(0.5)
        
        # Test 3: Evolution over time
        evolution, batch_results = test_evolving_persona()
        
        time.sleep(0.5)
        
        # Test 4: Report export
        test_similarity_report()
        
        # Summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print("✅ Test 1 (Close Match): PASSED")
        print("✅ Test 2 (Fallback): PASSED")
        print("✅ Test 3 (Evolution): PASSED")
        print("✅ Test 4 (Report): PASSED")
        print("\n🎉 All tests completed successfully!")
        
        # Engine stats
        engine = PersonaSimilarityEngine()
        stats = engine.get_stats()
        print("\nEngine Statistics:")
        print(json.dumps(stats, indent=2))
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)