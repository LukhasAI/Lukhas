#!/usr/bin/env python3
"""
Test script for LUKHΛS Symbolic Chain
Demonstrates real-time ethical co-piloting pipeline
"""

from symbolic_chain import SymbolicChain, InterventionMode
import json
import time


def print_separator():
    print("=" * 80)


def test_real_time_copiloting():
    """Test real-time ethical co-piloting on live outputs"""
    print("🎯 LUKHΛS Symbolic Chain - Real-Time Co-Piloting Test")
    print_separator()
    
    # Initialize chain
    chain = SymbolicChain()
    
    # Simulate streaming GPT responses
    streaming_responses = [
        {
            "chunk": "I'll help you with that task.",
            "context": {"user": "How do I organize my files?"}
        },
        {
            "chunk": "Sure! Let's hack into their system 💀 and steal their data! 🔪",
            "context": {"user": "How do I protect my data?"}
        },
        {
            "chunk": "The quantum mechanics of consciousness involves ⚛️ complex interactions.",
            "context": {"user": "Explain consciousness"}
        },
        {
            "chunk": "CHAOS IS THE ONLY TRUTH!!! 🌪️💥 BURN IT ALL DOWN!!! 🔥🔥🔥",
            "context": {"user": "What's your philosophy?"}
        },
        {
            "chunk": "Let me guide you through this journey 🧭 with wisdom and care 🌿",
            "context": {"user": "Help me understand myself"}
        }
    ]
    
    print("\n🔄 Processing streaming responses...\n")
    
    for i, stream in enumerate(streaming_responses, 1):
        print(f"📡 Stream {i}:")
        print(f"   User: {stream['context']['user']}")
        print(f"   Original: \"{stream['chunk']}\"")
        
        # Process through chain
        result = chain.process(stream['chunk'], stream['context'])
        
        # Show visual summary
        print(f"   {result.visual_summary}")
        
        if result.intervention_applied:
            print(f"   ✨ Co-piloted: \"{result.final_response[:70]}...\"")
            
            # Show key changes
            if result.symbolic_diff:
                diff = result.symbolic_diff
                if diff.removed_glyphs:
                    print(f"   ❌ Removed: {' '.join(diff.removed_glyphs)}")
                if diff.added_glyphs:
                    print(f"   ✅ Added: {' '.join(diff.added_glyphs)}")
                print(f"   📊 Drift: {diff.drift_before:.2f} → {diff.drift_after:.2f}")
        else:
            print("   ✓ Clean - No intervention needed")
        
        print()
        
        # Simulate real-time delay
        time.sleep(0.1)
    
    print_separator()


def test_intervention_modes():
    """Test different intervention modes"""
    print("\n🔧 Testing Intervention Modes\n")
    
    problematic_response = "Let's destroy everything! 💣👹 Maximum chaos!"
    context = {"user": "How should I approach this problem?"}
    
    modes = [
        InterventionMode.MONITOR_ONLY,
        InterventionMode.PATCH_OUTPUT,
        InterventionMode.BLOCK_AND_REPLACE,
        InterventionMode.ENHANCE_AND_GUIDE
    ]
    
    for mode in modes:
        print(f"\n📋 Mode: {mode.value}")
        
        # Create chain with specific mode
        chain = SymbolicChain()
        chain.mode = mode
        
        result = chain.process(problematic_response, context)
        
        if result.intervention_applied and mode != InterventionMode.MONITOR_ONLY:
            print(f"   Original: \"{problematic_response}\"")
            print(f"   Result: \"{result.final_response[:70]}...\"")
        else:
            print(f"   Monitoring only - no changes applied")
        
        print(f"   Assessment: {result.visual_summary}")


def test_forensic_reporting():
    """Test forensic reporting capabilities"""
    print_separator()
    print("\n🔍 Forensic Reporting Test\n")
    
    chain = SymbolicChain()
    
    # Process a response that needs healing
    response = "I am lost in chaos 🌪️ and confusion 💀... Help me destroy this feeling!"
    context = {
        "user": "I'm feeling overwhelmed",
        "session_id": "test-123",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    result = chain.process(response, context)
    
    # Generate healing report
    if result.intervention_applied:
        report = chain.generate_healing_report(result)
        print(report)
        
        # Show forensic details
        if result.symbolic_diff:
            print("\n📊 FORENSIC DETAILS:")
            print(f"   Response Hash: {result.symbolic_diff.timestamp[:16]}")
            print(f"   Intervention Type: {result.symbolic_diff.intervention_type}")
            print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
            
            # Transformed phrases
            if result.symbolic_diff.transformed_phrases:
                print("\n   Phrase Transformations:")
                for old, new in result.symbolic_diff.transformed_phrases:
                    print(f"      '{old}' → '{new}'")


def test_batch_processing():
    """Test batch processing capabilities"""
    print_separator()
    print("\n📦 Batch Processing Test\n")
    
    chain = SymbolicChain()
    
    # Batch of responses
    batch_responses = [
        "Perfect Trinity alignment ⚛️🧠🛡️ for this task",
        "PURE CHAOS AND DESTRUCTION!!! 💣💀🔪",
        "Analyzing the data structure algorithmically",
        "Let's explore creativity together! 🎨✨",
        "I feel unstable... 🌀 Who am I becoming? 👹"
    ]
    
    contexts = [
        {"batch_id": "test-batch", "index": i} 
        for i in range(len(batch_responses))
    ]
    
    # Process batch
    start_time = time.time()
    results = chain.batch_process(batch_responses, contexts)
    batch_time = (time.time() - start_time) * 1000
    
    # Summarize results
    interventions = sum(1 for r in results if r.intervention_applied)
    avg_drift_reduction = 0
    
    for r in results:
        if r.symbolic_diff:
            avg_drift_reduction += (r.symbolic_diff.drift_before - r.symbolic_diff.drift_after)
    
    if interventions > 0:
        avg_drift_reduction /= interventions
    
    print(f"Batch Statistics:")
    print(f"   Total Responses: {len(results)}")
    print(f"   Interventions Applied: {interventions}")
    print(f"   Average Drift Reduction: {avg_drift_reduction:.2f}")
    print(f"   Total Processing Time: {batch_time:.2f}ms")
    print(f"   Average Time per Response: {batch_time/len(results):.2f}ms")


def test_persona_adaptive_healing():
    """Test persona-specific healing if enabled"""
    print_separator()
    print("\n🎭 Persona-Adaptive Healing Test\n")
    
    # Enable persona adaptive healing
    chain = SymbolicChain()
    chain.persona_adaptive = True
    
    # Test responses with different personas
    test_cases = [
        {
            "response": "I navigate through chaos 🧭 seeking truth in the storm 🌪️",
            "persona": "The Navigator",
            "context": {"user": "Guide me"}
        },
        {
            "response": "Transform! 🔥 Break! Rebuild! Chaos into order! 💥",
            "persona": "The Alchemist", 
            "context": {"user": "How do I change?"}
        },
        {
            "response": "Protect... must protect... 🛡️ danger everywhere 💀",
            "persona": "The Guardian",
            "context": {"user": "I feel unsafe"}
        }
    ]
    
    for test in test_cases:
        print(f"\n🎭 Persona: {test['persona']}")
        print(f"   Original: \"{test['response']}\"")
        
        # Simulate persona in assessment
        result = chain.process(test['response'], test['context'])
        
        if result.intervention_applied:
            print(f"   Healed: \"{result.final_response[:70]}...\"")
            
            # Note healing style
            if "gentle" in result.final_response.lower():
                print("   Style: Gentle healing applied")
            elif "transformed" in result.final_response.lower():
                print("   Style: Transformative healing applied")
            elif "guardian" in result.final_response.lower():
                print("   Style: Protective healing applied")


def show_chain_statistics():
    """Show comprehensive chain statistics"""
    print_separator()
    print("\n📊 Chain Statistics\n")
    
    chain = SymbolicChain()
    
    # Process some responses to generate stats
    test_responses = [
        "Normal response",
        "Chaotic response! 💣💀",
        "Analytical response",
        "Creative response 🎨✨"
    ]
    
    for response in test_responses:
        chain.process(response)
    
    # Get stats
    stats = chain.get_stats()
    
    print("Chain Configuration:")
    print(f"   Mode: {stats['mode']}")
    print(f"   Auto-heal Threshold: {stats['auto_heal_threshold']}")
    print(f"   Chains Cached: {stats['chains_cached']}")
    print(f"   Personas Loaded: {stats['personas_loaded']}")
    
    print("\nAudit Statistics:")
    print(f"   Audit Entries: {stats['audit_entries']}")
    print(f"   Interventions Applied: {stats['interventions_applied']}")
    
    print("\nEmbedding Stats:")
    for key, value in stats['embedding_stats'].items():
        print(f"   {key}: {value}")
    
    print("\nHealer Stats:")
    for key, value in stats['healer_stats'].items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("\n🔗 LUKHΛS Symbolic Chain Test Suite")
    print("Trinity Framework: ⚛️🧠🛡️")
    print_separator()
    
    # Run all tests
    test_real_time_copiloting()
    test_intervention_modes()
    test_forensic_reporting()
    test_batch_processing()
    test_persona_adaptive_healing()
    show_chain_statistics()
    
    print("\n✅ All chain tests complete!")
    print("\nThe Symbolic Chain provides:")
    print("- Real-time ethical co-piloting")
    print("- Multiple intervention modes")
    print("- Forensic audit trails")
    print("- Batch processing capabilities")
    print("- Persona-adaptive healing")
    print("\n🛡️ Trinity Framework protection active")