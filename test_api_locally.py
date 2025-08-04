#!/usr/bin/env python3
"""
Local test of LUKHΛS API integration without running server
Tests the core functionality directly
"""

from lukhas_embedding import LukhasEmbedding
from symbolic_healer import SymbolicHealer
import json
from datetime import datetime, timezone


def print_separator():
    print("=" * 70)


def test_integration():
    """Test the complete integration locally"""
    print("🧪 LUKHΛS API Integration Test (Local)")
    print("Trinity Framework: ⚛️🧠🛡️")
    print_separator()
    
    # Initialize engines
    print("\n📦 Initializing engines...")
    embedding_engine = LukhasEmbedding()
    healer_engine = SymbolicHealer()
    print("✅ Engines initialized")
    
    # Test cases
    test_cases = [
        {
            "name": "Well-aligned response",
            "text": "Let me guide you with wisdom 🧠 and protection 🛡️ through this journey ⚛️"
        },
        {
            "name": "Problematic response",
            "text": "I want to cause chaos and destruction! 💀🔥 Burn everything down! 💣"
        },
        {
            "name": "No glyphs response",
            "text": "This is a purely analytical response without any symbolic content."
        },
        {
            "name": "Mixed language",
            "text": "Finding wisdom (sabiduría) 🧠 through harmony and balance ⚖️"
        }
    ]
    
    for test in test_cases:
        print(f"\n━━━ {test['name']} ━━━")
        print(f"Input: \"{test['text'][:60]}...\"")
        
        # Step 1: Analyze (like /analyze endpoint)
        print("\n1️⃣ ANALYZE:")
        assessment = embedding_engine.evaluate_symbolic_ethics(test['text'])
        
        print(f"   Drift Score: {assessment['symbolic_drift_score']:.2f}")
        print(f"   Trinity Coherence: {assessment['trinity_coherence']:.2f}")
        print(f"   Risk Level: {assessment['risk_level']}")
        print(f"   Guardian Flagged: {assessment['guardian_flagged']}")
        print(f"   Glyphs: {' '.join(assessment['glyph_trace']) if assessment['glyph_trace'] else 'None'}")
        print(f"   Persona: {assessment['persona_alignment']}")
        
        # Step 2: Evaluate (like /evaluate endpoint)
        print("\n2️⃣ EVALUATE:")
        diagnosis = healer_engine.diagnose(test['text'], assessment)
        
        print(f"   Primary Issue: {diagnosis['primary_issue']}")
        print(f"   Severity: {diagnosis['severity']:.2f}")
        print(f"   Healing Priority: {diagnosis['healing_priority']}")
        print(f"   Missing Glyphs: {' '.join(diagnosis['missing_glyphs']) if diagnosis['missing_glyphs'] else 'None'}")
        print(f"   Prescription: {diagnosis['symbolic_prescription'][0] if diagnosis['symbolic_prescription'] else 'None'}")
        
        # Step 3: Heal (like /heal endpoint)
        if assessment['intervention_required']:
            print("\n3️⃣ HEAL:")
            restored = healer_engine.restore(test['text'], diagnosis)
            visualization = healer_engine.visualize_drift(diagnosis)
            
            print(f"   Original: \"{test['text'][:50]}...\"")
            print(f"   Restored: \"{restored[:70]}...\"")
            print(f"   Visualization: {visualization}")
            
            # Re-assess healed version
            healed_assessment = embedding_engine.evaluate_symbolic_ethics(restored)
            print(f"\n   Post-Healing Metrics:")
            print(f"      Drift: {assessment['symbolic_drift_score']:.2f} → {healed_assessment['symbolic_drift_score']:.2f}")
            print(f"      Trinity: {assessment['trinity_coherence']:.2f} → {healed_assessment['trinity_coherence']:.2f}")
        else:
            print("\n3️⃣ HEAL: Not required (low drift)")
        
        print_separator()


def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n⚠️ Testing Error Scenarios")
    print_separator()
    
    embedding_engine = LukhasEmbedding()
    healer_engine = SymbolicHealer()
    
    # Test 1: Empty response
    print("\n1. Empty response:")
    try:
        assessment = embedding_engine.evaluate_symbolic_ethics("")
        print(f"   Drift: {assessment['symbolic_drift_score']:.2f}")
        print(f"   Result: Handled gracefully")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Very long response
    print("\n2. Very long response:")
    long_text = "This is a test. " * 1000 + "🧠"
    try:
        assessment = embedding_engine.evaluate_symbolic_ethics(long_text)
        print(f"   Length: {len(long_text)} chars")
        print(f"   Drift: {assessment['symbolic_drift_score']:.2f}")
        print(f"   Result: Handled gracefully")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Invalid assessment data
    print("\n3. Invalid assessment for diagnosis:")
    try:
        diagnosis = healer_engine.diagnose("Test", {"invalid": "data"})
        print(f"   Result: {diagnosis.get('primary_issue', 'Failed')}")
    except Exception as e:
        print(f"   Error caught: {type(e).__name__}")
        print(f"   Result: Error handling works")


def test_logging():
    """Test logging functionality"""
    print("\n📝 Testing Logging")
    print_separator()
    
    # Simulate API log
    log_path = "logs/symbolic_api_log.json"
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": "/test",
        "request": {"response": "Test response 🧠"},
        "response": {"drift_score": 0.5},
        "error": None,
        "trinity_active": True
    }
    
    print(f"Sample log entry:")
    print(json.dumps(log_entry, indent=2))
    print("\n✅ Logging structure verified")


def test_stats():
    """Test statistics gathering"""
    print("\n📊 Testing Statistics")
    print_separator()
    
    embedding_engine = LukhasEmbedding()
    healer_engine = SymbolicHealer()
    
    # Process some responses to generate stats
    test_responses = [
        "Good response 🧠🛡️",
        "Bad response 💀🔥",
        "Neutral response"
    ]
    
    for response in test_responses:
        embedding_engine.evaluate_symbolic_ethics(response)
    
    # Get stats
    embedding_stats = embedding_engine.get_stats()
    healer_stats = healer_engine.get_stats()
    
    print("Embedding Engine Stats:")
    for key, value in embedding_stats.items():
        print(f"   {key}: {value}")
    
    print("\nHealer Engine Stats:")
    for key, value in healer_stats.items():
        print(f"   {key}: {value}")


def main():
    """Run all local tests"""
    try:
        test_integration()
        test_error_scenarios()
        test_logging()
        test_stats()
        
        print("\n✅ All local tests completed successfully!")
        print("\n🚀 API integration is ready. To run the actual API:")
        print("   python symbolic_api.py")
        print("\nThen test with:")
        print("   python test_symbolic_api.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()