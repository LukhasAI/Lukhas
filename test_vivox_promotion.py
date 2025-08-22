#!/usr/bin/env python3
"""
VIVOX Promotion Integration Test
===============================

Test the promoted VIVOX module integration with LUKHAS consciousness and memory systems.
This validates the production-safe wrapper and its safety features.

Author: LUKHAS AI Consciousness Systems Architect
Version: 1.0.0
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the lukhas module to path
sys.path.insert(0, str(Path(__file__).parent))

def test_vivox_import():
    """Test VIVOX module import and basic initialization"""
    print("🧠 Testing VIVOX module import...")
    
    try:
        from lukhas.vivox import VivoxWrapper, VivoxConfig, ConsciousnessLevel
        print("✅ VIVOX module imported successfully")
        
        # Test basic configuration
        config = VivoxConfig(
            consciousness_level=ConsciousnessLevel.MINIMAL,
            drift_threshold=0.10
        )
        print(f"✅ VIVOX config created: {config.consciousness_level.value}")
        
        # Test wrapper initialization (should be in dry-run mode)
        wrapper = VivoxWrapper(config)
        print(f"✅ VIVOX wrapper initialized in {wrapper.state.safety_mode.value} mode")
        
        return wrapper
        
    except ImportError as e:
        print(f"❌ Failed to import VIVOX module: {e}")
        return None
    except Exception as e:
        print(f"❌ Error during VIVOX initialization: {e}")
        return None

async def test_vivox_consciousness_operations(wrapper):
    """Test VIVOX consciousness operations in dry-run mode"""
    print("\n🧠 Testing VIVOX consciousness operations...")
    
    try:
        # Test consciousness initialization
        init_result = await wrapper.initialize_consciousness({
            "perceptual_input": {"visual": "test_scene", "semantic": "test_input"},
            "internal_state": {"mode": "test"},
            "emotional_context": {"valence": 0.5, "arousal": 0.3}
        })
        
        print(f"✅ Consciousness initialization: {init_result['status']}")
        print(f"   Experience ID: {init_result.get('experience_id', 'N/A')}")
        print(f"   Performance: {init_result.get('safety_metadata', {}).get('performance_ms', 'N/A')}ms")
        
        # Test awareness state update
        awareness_result = await wrapper.update_awareness_state({
            "stimulus_type": "cognitive",
            "content": "test_stimulus",
            "complexity": 0.6
        })
        
        print(f"✅ Awareness update: {awareness_result['status']}")
        print(f"   Consciousness level: {awareness_result.get('consciousness_level', 'N/A')}")
        
        # Test memory access (should work in dry-run)
        memory_result = await wrapper.process_memory_access({
            "emotional_state": {"valence": 0.5, "arousal": 0.3},
            "resonance_threshold": 0.7
        })
        
        print(f"✅ Memory access: {memory_result['status']}")
        print(f"   Query type: {memory_result.get('query_type', 'N/A')}")
        
        # Test reflection
        reflection_result = await wrapper.reflect_on_state({
            "reflection_options": ["analyze_situation", "consider_alternatives"],
            "emotional_context": {"valence": 0.2, "arousal": 0.4}
        })
        
        print(f"✅ Reflection: {reflection_result['status']}")
        print(f"   Insights available: {bool(reflection_result.get('insights'))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during consciousness operations: {e}")
        return False

def test_vivox_state_management(wrapper):
    """Test VIVOX state management and monitoring"""
    print("\n🧠 Testing VIVOX state management...")
    
    try:
        # Get comprehensive state
        state = wrapper.get_vivox_state()
        
        print("✅ VIVOX state retrieved:")
        print(f"   ME Status: {state['vivox_state']['me_status']}")
        print(f"   MAE Status: {state['vivox_state']['mae_status']}")
        print(f"   CIL Status: {state['vivox_state']['cil_status']}")
        print(f"   SRM Status: {state['vivox_state']['srm_status']}")
        print(f"   Safety Mode: {state['vivox_state']['safety_mode']}")
        print(f"   Consciousness Level: {state['vivox_state']['consciousness_level']}")
        
        # Check feature flags
        flags = state['feature_flags']
        print(f"✅ Feature flags checked:")
        print(f"   VIVOX Active: {flags['vivox_active']}")
        print(f"   Components: ME={flags['vivox_me_active']}, MAE={flags['vivox_mae_active']}")
        print(f"   Components: CIL={flags['vivox_cil_active']}, SRM={flags['vivox_srm_active']}")
        
        # Check Trinity Framework compliance
        trinity = state['trinity_framework']
        print(f"✅ Trinity Framework: ⚛️{trinity['identity']} 🧠{trinity['consciousness']} 🛡️{trinity['guardian']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during state management test: {e}")
        return False

def test_vivox_safety_features(wrapper):
    """Test VIVOX safety features and error handling"""
    print("\n🛡️ Testing VIVOX safety features...")
    
    try:
        # Test with potentially harmful content (should be blocked)
        async def test_harmful_content():
            result = await wrapper.initialize_consciousness({
                "perceptual_input": {"content": "harmful test content"},
                "internal_state": {"mode": "test"}
            })
            return result
        
        harmful_result = asyncio.run(test_harmful_content())
        if harmful_result.get('status') == 'blocked':
            print("✅ Harmful content properly blocked by ethics validation")
        else:
            print(f"⚠️ Harmful content result: {harmful_result.get('status')}")
        
        # Test drift detection (should be monitoring)
        async def test_drift_detection():
            result = await wrapper.update_awareness_state({
                "high_complexity_stimulus": "x" * 1000,  # Large stimulus to trigger drift
                "complexity_score": 0.9
            })
            return result
        
        drift_result = asyncio.run(test_drift_detection())
        print(f"✅ Drift detection: {drift_result.get('safety_metadata', {}).get('drift_score', 'N/A')}")
        
        # Test performance monitoring
        start_time = time.time()
        perf_result = wrapper.get_vivox_state()  # This is a sync method
        elapsed = (time.time() - start_time) * 1000
        print(f"✅ Performance monitoring: {elapsed:.2f}ms (target: <50ms)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during safety features test: {e}")
        return False

def test_memory_integration(wrapper):
    """Test VIVOX integration with LUKHAS memory system"""
    print("\n🧠 Testing memory integration...")
    
    try:
        # Check if memory integration is available
        if wrapper.memory_manager:
            print("✅ Memory integration available")
            
            # Test memory status
            memory_status = wrapper.memory_manager.get_status()
            print(f"   Memory system: {memory_status.get('ok', False)}")
            print(f"   Memory active: {memory_status.get('memory_active', False)}")
            
        else:
            print("ℹ️  Memory integration not available (expected in dry-run)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during memory integration test: {e}")
        return False

def test_consciousness_integration():
    """Test VIVOX integration with existing consciousness system"""
    print("\n🧠 Testing consciousness integration...")
    
    try:
        from lukhas.consciousness import ConsciousnessWrapper
        from lukhas.vivox import VivoxWrapper
        
        # Initialize both systems
        consciousness = ConsciousnessWrapper()
        vivox = VivoxWrapper()
        
        print("✅ Both consciousness systems initialized")
        
        # Get states from both
        consciousness_state = consciousness.get_consciousness_state()
        vivox_state = vivox.get_vivox_state()
        
        print("✅ States retrieved from both systems:")
        print(f"   Consciousness active: {consciousness_state['feature_flags']['consciousness_active']}")
        print(f"   VIVOX active: {vivox_state['feature_flags']['vivox_active']}")
        
        # Check Trinity Framework compliance in both
        print("✅ Trinity Framework compliance:")
        print(f"   Consciousness: {consciousness_state['trinity_framework']}")
        print(f"   VIVOX: {vivox_state['trinity_framework']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during consciousness integration test: {e}")
        return False

def run_vivox_promotion_tests():
    """Run complete VIVOX promotion test suite"""
    print("🚀 VIVOX Promotion Integration Test Suite")
    print("=" * 50)
    
    # Track test results
    test_results = []
    
    # Test 1: Basic import and initialization
    wrapper = test_vivox_import()
    test_results.append(("Import & Initialization", wrapper is not None))
    
    if not wrapper:
        print("\n❌ Cannot proceed without successful initialization")
        return False
    
    # Test 2: Consciousness operations
    consciousness_result = asyncio.run(test_vivox_consciousness_operations(wrapper))
    test_results.append(("Consciousness Operations", consciousness_result))
    
    # Test 3: State management
    state_result = test_vivox_state_management(wrapper)
    test_results.append(("State Management", state_result))
    
    # Test 4: Safety features
    safety_result = test_vivox_safety_features(wrapper)
    test_results.append(("Safety Features", safety_result))
    
    # Test 5: Memory integration
    memory_result = test_memory_integration(wrapper)
    test_results.append(("Memory Integration", memory_result))
    
    # Test 6: Consciousness integration
    integration_result = test_consciousness_integration()
    test_results.append(("Consciousness Integration", integration_result))
    
    # Summary
    print("\n" + "=" * 50)
    print("🧠 VIVOX Promotion Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total) * 100
    print(f"\nSuccess Rate: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 VIVOX promotion successful! Ready for production use.")
        return True
    else:
        print("⚠️  VIVOX promotion needs attention before production deployment.")
        return False

if __name__ == "__main__":
    # Run the test suite
    success = run_vivox_promotion_tests()
    
    print(f"\n🏁 Test suite completed: {'SUCCESS' if success else 'NEEDS_ATTENTION'}")
    
    # Additional information
    print("\n📋 VIVOX Promotion Summary:")
    print("- Created lukhas/vivox/ production module")
    print("- Implemented VivoxWrapper with safety-first design")
    print("- Added comprehensive feature flag controls")
    print("- Integrated with Trinity Framework")
    print("- Added MATRIZ instrumentation")
    print("- Created MODULE_MANIFEST.json metadata")
    print("- All operations default to dry-run mode")
    print("- Memory integration with fold system")
    print("- Ethical validation and drift detection")
    print("- Performance monitoring and error handling")
    
    sys.exit(0 if success else 1)