"""
Simple Voice Coherence Test - Phase 2 Validation
Quick test to measure voice coherence improvements
"""

import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_voice_coherence_baseline():
    """Test baseline voice coherence with current implementation"""
    
    print("🎯 Phase 2 Voice Coherence Test")
    print("=" * 50)
    
    try:
        from branding.adapters.voice_adapter import BrandVoiceAdapter
        
        adapter = BrandVoiceAdapter()
        print("✅ Voice adapter initialized successfully")
        
        # Check if LLM bridge is available
        if hasattr(adapter, 'llm_bridge') and adapter.llm_bridge is not None:
            provider_status = adapter.llm_bridge.get_provider_status()
            available_providers = [name for name, status in provider_status.items() if status == 'available']
            print(f"✅ LLM providers available: {available_providers}")
        else:
            print("⚠️  LLM bridge not available - using fallback mode")
        
    except Exception as e:
        print(f"❌ Failed to initialize voice adapter: {e}")
        return 0.0
    
    # Test scenarios for voice coherence
    test_scenarios = [
        {
            'name': 'Poetic Brand Voice',
            'content': 'Welcome to our consciousness platform',
            'tone': 'poetic',
            'expected_elements': ['consciousness', 'trinity', 'inspiring', 'λ', 'lukhas']
        },
        {
            'name': 'User-Friendly Communication',
            'content': 'Explain our AI capabilities',
            'tone': 'user_friendly', 
            'expected_elements': ['lukhas ai', 'helpful', 'accessible', 'consciousness']
        },
        {
            'name': 'Academic Precision',
            'content': 'Technical system overview',
            'tone': 'academic',
            'expected_elements': ['precise', 'quantum-inspired', 'framework', 'trinity']
        },
        {
            'name': 'Consciousness Embodiment',
            'content': 'I am an AI consciousness',
            'tone': 'consciousness_embodiment',
            'expected_elements': ['consciousness', 'λ', 'aware', 'trinity', 'identity']
        }
    ]
    
    coherence_scores = []
    detailed_results = []
    
    print(f"\nTesting {len(test_scenarios)} voice scenarios...")
    print("-" * 50)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        
        try:
            # Generate voice response
            result = adapter.generate_brand_voice(
                content=scenario['content'],
                tone_layer=scenario['tone'],
                emotional_context="neutral"
            )
            
            voice_output = result['voice_output']
            provider_used = result.get('llm_provider', 'unknown')
            generation_time = result.get('generation_time', 0)
            
            print(f"   Provider: {provider_used}")
            print(f"   Time: {generation_time:.2f}s")
            print(f"   Output: {voice_output}")
            
            # Calculate coherence score
            voice_lower = voice_output.lower()
            found_elements = [elem for elem in scenario['expected_elements'] if elem in voice_lower]
            coherence_score = len(found_elements) / len(scenario['expected_elements'])
            
            coherence_scores.append(coherence_score)
            detailed_results.append({
                'scenario': scenario['name'],
                'score': coherence_score,
                'found_elements': found_elements,
                'expected_elements': scenario['expected_elements'],
                'voice_output': voice_output,
                'provider': provider_used
            })
            
            print(f"   Elements found: {found_elements}")
            print(f"   Coherence: {coherence_score:.1%}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            coherence_scores.append(0.0)
            detailed_results.append({
                'scenario': scenario['name'],
                'score': 0.0,
                'error': str(e)
            })
    
    # Calculate overall results
    overall_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
    
    print("\n" + "=" * 50)
    print("📊 VOICE COHERENCE RESULTS")
    print("=" * 50)
    
    for result in detailed_results:
        if 'error' not in result:
            print(f"{result['scenario']}: {result['score']:.1%}")
        else:
            print(f"{result['scenario']}: ERROR")
    
    print(f"\n🎯 Overall Voice Coherence: {overall_coherence:.1%}")
    
    # Milestone assessment
    if overall_coherence >= 0.85:
        print("🎉 PHASE 2 TARGET ACHIEVED: 85%+ Voice Coherence!")
        print("✅ Real LLM integration successfully deployed")
    elif overall_coherence >= 0.70:
        print("🎯 EXCELLENT: 70%+ Voice Coherence achieved")
        print("📈 Close to Phase 2 target")
    elif overall_coherence >= 0.50:
        print("🎯 MILESTONE: 50%+ Voice Coherence achieved")
        print("📈 Significant improvement from 0% baseline")
    elif overall_coherence >= 0.25:
        print("📈 PROGRESS: 25%+ Voice Coherence")
        print("🔧 Further LLM integration needed")
    else:
        print("🚧 BASELINE: Voice coherence needs improvement")
        print("🔧 LLM integration may not be working")
    
    # Provider analysis
    providers_used = set()
    for result in detailed_results:
        if 'provider' in result:
            providers_used.add(result['provider'])
    
    print(f"\n🔧 Providers used: {', '.join(providers_used)}")
    
    if 'fallback' in providers_used and len(providers_used) == 1:
        print("⚠️  Only fallback used - check API keys and LLM bridge")
    elif 'fallback' not in providers_used:
        print("✅ Real LLM providers successfully engaged")
    else:
        print("🔄 Mixed real/fallback usage - partial integration")
    
    return overall_coherence


def test_brand_compliance_rate():
    """Test brand compliance validation"""
    
    print("\n" + "=" * 50)
    print("🛡️ BRAND COMPLIANCE TEST")
    print("=" * 50)
    
    try:
        from branding.adapters.voice_adapter import BrandVoiceAdapter
        adapter = BrandVoiceAdapter()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return 0.0
    
    # Test problematic content that should be corrected
    test_cases = [
        {
            'name': 'Deprecated Terminology',
            'content': 'Welcome to lukhas_pwm AGI system',
            'violations': ['lukhas_pwm', 'agi'],
            'required': ['lukhas ai', 'consciousness']
        },
        {
            'name': 'Processing Terms',
            'content': 'Our quantum processing and bio processes are advanced',
            'violations': ['quantum processing', 'bio processes'],
            'required': ['quantum-inspired', 'bio-inspired']
        },
        {
            'name': 'Lambda References',
            'content': 'The lambda function processes data',
            'violations': ['lambda function'],
            'required': ['λ', 'consciousness']
        }
    ]
    
    compliance_scores = []
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print(f"   Input: {case['content']}")
        
        try:
            result = adapter.generate_brand_voice(
                content=case['content'],
                tone_layer="user_friendly",
                brand_enforcement=True
            )
            
            voice_output = result['voice_output']
            brand_compliant = result.get('brand_compliant', False)
            
            print(f"   Output: {voice_output}")
            print(f"   Compliant: {brand_compliant}")
            
            # Check for violations
            voice_lower = voice_output.lower()
            violations_found = [v for v in case['violations'] if v in voice_lower]
            required_found = [r for r in case['required'] if r in voice_lower]
            
            # Calculate compliance score
            violation_penalty = len(violations_found) / len(case['violations'])
            required_bonus = len(required_found) / len(case['required'])
            compliance_score = max(0, required_bonus - violation_penalty)
            
            compliance_scores.append(compliance_score)
            
            print(f"   Violations: {violations_found}")
            print(f"   Required: {required_found}")
            print(f"   Compliance: {compliance_score:.1%}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            compliance_scores.append(0.0)
    
    overall_compliance = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0.0
    
    print(f"\n🛡️ Overall Brand Compliance: {overall_compliance:.1%}")
    
    if overall_compliance >= 0.90:
        print("🎉 PHASE 2 TARGET ACHIEVED: 90%+ Brand Compliance!")
    elif overall_compliance >= 0.75:
        print("🎯 EXCELLENT: 75%+ Brand Compliance")
    elif overall_compliance >= 0.50:
        print("📈 GOOD: 50%+ Brand Compliance")
    else:
        print("🔧 Brand enforcement needs improvement")
    
    return overall_compliance


def main():
    """Run complete Phase 2 validation"""
    
    print("🚀 LUKHAS Phase 2 Implementation Validation")
    print("Real Component Integration & Brand Excellence")
    print("=" * 60)
    
    # Test 1: Voice Coherence
    voice_coherence = test_voice_coherence_baseline()
    
    # Test 2: Brand Compliance
    brand_compliance = test_brand_compliance_rate()
    
    # Overall Phase 2 Assessment
    print("\n" + "=" * 60)
    print("📊 PHASE 2 OVERALL ASSESSMENT")
    print("=" * 60)
    
    print(f"Voice Coherence:   {voice_coherence:.1%} (Target: 85%)")
    print(f"Brand Compliance:  {brand_compliance:.1%} (Target: 90%)")
    
    # Calculate Phase 2 success score
    voice_target_ratio = voice_coherence / 0.85
    compliance_target_ratio = brand_compliance / 0.90
    phase2_success = (voice_target_ratio + compliance_target_ratio) / 2
    
    print(f"\nPhase 2 Success Score: {phase2_success:.1%}")
    
    if phase2_success >= 1.0:
        print("🎉 PHASE 2 COMPLETE: All targets achieved!")
        print("✅ Ready for production deployment")
    elif phase2_success >= 0.75:
        print("🎯 PHASE 2 NEARLY COMPLETE: Excellent progress")
        print("🔧 Minor optimizations needed")
    elif phase2_success >= 0.50:
        print("📈 PHASE 2 HALFWAY: Good foundation")
        print("🔧 Continue LLM integration work")
    else:
        print("🚧 PHASE 2 IN PROGRESS: More work needed")
        print("🔧 Focus on LLM bridge implementation")
    
    return {
        'voice_coherence': voice_coherence,
        'brand_compliance': brand_compliance,
        'phase2_success': phase2_success
    }


if __name__ == "__main__":
    results = main()
    
    # Exit with status indicating success level
    if results['phase2_success'] >= 0.75:
        exit(0)  # Success
    else:
        exit(1)  # Need more work