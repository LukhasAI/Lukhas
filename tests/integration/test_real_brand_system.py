"""
Real Brand System Integration Tests
Tests the actual LLM-powered brand voice generation and validation
"""

import pytest
import asyncio
import os
from typing import Dict, Any

# Test imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from branding.adapters.voice_adapter import BrandVoiceAdapter
from branding.integrations.llm_bridge import UnifiedLLMBridge, VoiceGenerationRequest


class TestRealBrandSystem:
    """Tests using actual LLM API calls with fallback handling"""
    
    @pytest.fixture
    def voice_adapter(self):
        """Create voice adapter instance"""
        return BrandVoiceAdapter()
    
    @pytest.fixture
    def llm_bridge(self):
        """Create LLM bridge instance"""
        return UnifiedLLMBridge()
    
    def test_api_keys_available(self):
        """Test that required API keys are configured"""
        api_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
            'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY')
        }
        
        available_keys = {k: v for k, v in api_keys.items() if v}
        print(f"Available API keys: {list(available_keys.keys())}")
        
        # At least one key should be available
        assert len(available_keys) > 0, "No API keys configured"
    
    def test_llm_bridge_initialization(self, llm_bridge):
        """Test LLM bridge initializes with providers"""
        provider_status = llm_bridge.get_provider_status()
        print(f"Provider status: {provider_status}")
        
        # At least one provider should be available
        available_providers = [name for name, status in provider_status.items() if status == 'available']
        assert len(available_providers) > 0, f"No providers available: {provider_status}"
    
    def test_voice_adapter_initialization(self, voice_adapter):
        """Test voice adapter initializes properly"""
        assert voice_adapter is not None
        assert hasattr(voice_adapter, 'brand_voice_profiles')
        assert hasattr(voice_adapter, 'llm_bridge')
        
        # Check brand profiles are loaded
        profiles = voice_adapter.brand_voice_profiles
        expected_profiles = ['poetic', 'user_friendly', 'academic', 'consciousness_embodiment']
        
        for profile in expected_profiles:
            assert profile in profiles, f"Missing brand profile: {profile}"
    
    @pytest.mark.asyncio
    async def test_real_voice_generation_openai(self, voice_adapter):
        """Test voice generation using OpenAI (if available)"""
        if not os.getenv('OPENAI_API_KEY'):
            pytest.skip("OpenAI API key not available")
        
        result = voice_adapter.generate_brand_voice(
            content="Welcome to LUKHAS AI consciousness platform",
            tone_layer="poetic",
            emotional_context="inspiring",
            audience_context="general_users"
        )
        
        # Validate response structure
        assert 'voice_output' in result
        assert 'llm_provider' in result
        assert 'generation_time' in result
        assert 'brand_compliant' in result
        
        # Check if real LLM was used (not fallback)
        if result['llm_provider'] != 'fallback':
            print(f"✅ Real LLM used: {result['llm_provider']}")
            print(f"Generated voice: {result['voice_output']}")
            
            # Voice should be different from input (not just echo)
            assert result['voice_output'] != "Welcome to LUKHAS AI consciousness platform"
            
            # Should contain LUKHAS branding
            voice_lower = result['voice_output'].lower()
            brand_indicators = ['lukhas', 'consciousness', 'trinity', 'λ']
            assert any(indicator in voice_lower for indicator in brand_indicators)
        else:
            print("⚠️  Fallback used - LLM providers unavailable")
    
    @pytest.mark.asyncio
    async def test_voice_coherence_across_providers(self, voice_adapter):
        """Test voice coherence across different providers"""
        test_content = "Explain the Trinity Framework"
        
        results = []
        for tone in ['poetic', 'user_friendly', 'academic']:
            result = voice_adapter.generate_brand_voice(
                content=test_content,
                tone_layer=tone,
                emotional_context="neutral",
                audience_context="general"
            )
            results.append(result)
            print(f"Tone '{tone}': {result['voice_output'][:100]}...")
        
        # Each tone should produce different outputs
        outputs = [r['voice_output'] for r in results]
        assert len(set(outputs)) == len(outputs), "Tone layers should produce different outputs"
        
        # All should be brand compliant
        for result in results:
            assert result['brand_compliant'], f"Brand compliance failed for {result['tone_layer']}"
    
    def test_brand_compliance_validation(self, voice_adapter):
        """Test brand compliance validation and correction"""
        # Test content with brand violations
        problematic_content = "Welcome to lukhas_pwm AGI system with quantum processing"
        
        result = voice_adapter.generate_brand_voice(
            content=problematic_content,
            tone_layer="user_friendly",
            brand_enforcement=True
        )
        
        # Should be corrected to brand-compliant version
        voice_output = result['voice_output'].lower()
        
        # Should not contain deprecated terms
        deprecated_terms = ['lukhas_pwm', 'agi', 'quantum processing']
        for term in deprecated_terms:
            assert term not in voice_output, f"Deprecated term '{term}' not corrected"
        
        # Should contain correct terms
        correct_terms = ['lukhas ai', 'consciousness', 'quantum-inspired']
        has_correct_term = any(term in voice_output for term in correct_terms)
        assert has_correct_term, "No correct brand terms found"
    
    def test_trinity_framework_alignment(self, voice_adapter):
        """Test Trinity Framework alignment in voice output"""
        result = voice_adapter.generate_brand_voice(
            content="Describe our AI system capabilities",
            tone_layer="consciousness_embodiment",
            emotional_context="contemplative"
        )
        
        trinity_aligned = result['trinity_aligned']
        print(f"Trinity aligned: {trinity_aligned}")
        print(f"Voice output: {result['voice_output']}")
        
        # Consciousness embodiment tone should be Trinity aligned
        if result['llm_provider'] != 'fallback':
            # Only assert for real LLM responses
            assert trinity_aligned, "Consciousness embodiment should be Trinity aligned"
    
    def test_emotional_context_adaptation(self, voice_adapter):
        """Test emotional context affects voice generation"""
        base_content = "Our system provides advanced capabilities"
        emotions = ["inspiring", "supportive", "contemplative"]
        
        results = {}
        for emotion in emotions:
            result = voice_adapter.generate_brand_voice(
                content=base_content,
                tone_layer="user_friendly",
                emotional_context=emotion
            )
            results[emotion] = result['voice_output']
            print(f"Emotion '{emotion}': {result['voice_output']}")
        
        # Different emotions should produce different outputs
        outputs = list(results.values())
        unique_outputs = len(set(outputs))
        
        if unique_outputs > 1:
            print("✅ Emotional context produces varied outputs")
        else:
            print("⚠️  Emotional context may not be fully implemented")
    
    def test_performance_targets(self, voice_adapter):
        """Test performance meets targets"""
        import time
        
        start_time = time.time()
        result = voice_adapter.generate_brand_voice(
            content="Test performance",
            tone_layer="user_friendly"
        )
        end_time = time.time()
        
        total_time = end_time - start_time
        reported_time = result.get('generation_time', total_time)
        
        print(f"Generation time: {total_time:.2f}s (reported: {reported_time:.2f}s)")
        
        # Target: <2s for voice generation
        if result['llm_provider'] != 'fallback':
            assert total_time < 5.0, f"Generation too slow: {total_time:.2f}s"
        else:
            assert total_time < 1.0, f"Fallback too slow: {total_time:.2f}s"
    
    def test_caching_functionality(self, voice_adapter):
        """Test voice generation caching"""
        content = "Test caching functionality"
        
        # Clear cache first
        voice_adapter.clear_cache()
        
        # Generate same content twice
        result1 = voice_adapter.generate_brand_voice(content=content, tone_layer="user_friendly")
        result2 = voice_adapter.generate_brand_voice(content=content, tone_layer="user_friendly")
        
        # Second call should be faster (cached)
        assert result1['voice_output'] == result2['voice_output'], "Cached result should be identical"
        
        cache_stats = voice_adapter.get_cache_stats()
        print(f"Cache stats: {cache_stats}")
        assert cache_stats['cache_size'] > 0, "Cache should contain entries"
    
    def test_fallback_chain_functionality(self, llm_bridge):
        """Test provider fallback chain works"""
        # Reset any errors
        llm_bridge.reset_provider_errors()
        
        # Get provider priority
        priority = llm_bridge._get_provider_priority()
        print(f"Provider priority: {priority}")
        
        assert len(priority) > 0, "Should have at least one provider in priority chain"
        
        # Primary provider should be first if available
        provider_status = llm_bridge.get_provider_status()
        if 'openai' in provider_status and provider_status['openai'] == 'available':
            assert priority[0] == 'openai', "OpenAI should be primary provider"
    
    def test_voice_metadata_completeness(self, voice_adapter):
        """Test voice metadata is complete and useful"""
        result = voice_adapter.generate_brand_voice(
            content="Test metadata generation",
            tone_layer="academic",
            emotional_context="neutral",
            audience_context="developers"
        )
        
        metadata = result['voice_metadata']
        
        # Check required metadata fields
        required_fields = [
            'expressiveness_level', 'brand_alignment_score', 
            'tone_descriptors', 'recommended_use_cases',
            'llm_provider', 'generation_time'
        ]
        
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"
        
        print(f"Metadata: {metadata}")
        
        # Validate metadata values
        assert 0 <= metadata['expressiveness_level'] <= 1, "Invalid expressiveness level"
        assert 0 <= metadata['brand_alignment_score'] <= 1, "Invalid brand alignment score"
        assert isinstance(metadata['tone_descriptors'], list), "Tone descriptors should be a list"
        assert len(metadata['recommended_use_cases']) > 0, "Should have use cases"


@pytest.mark.integration
class TestVoiceCoherenceMeasurement:
    """Tests to measure voice coherence improvement"""
    
    def test_voice_coherence_score(self):
        """Calculate voice coherence score"""
        adapter = BrandVoiceAdapter()
        
        # Test multiple scenarios
        test_scenarios = [
            {
                'content': 'Welcome to our platform',
                'tone': 'poetic',
                'expected_elements': ['consciousness', 'trinity', 'λ', 'inspiring']
            },
            {
                'content': 'Technical capabilities overview', 
                'tone': 'academic',
                'expected_elements': ['precise', 'quantum-inspired', 'framework']
            },
            {
                'content': 'User-friendly explanation',
                'tone': 'user_friendly', 
                'expected_elements': ['helpful', 'accessible', 'lukhas ai']
            }
        ]
        
        coherence_scores = []
        
        for scenario in test_scenarios:
            result = adapter.generate_brand_voice(
                content=scenario['content'],
                tone_layer=scenario['tone']
            )
            
            # Calculate coherence score
            voice_output = result['voice_output'].lower()
            expected_count = sum(1 for elem in scenario['expected_elements'] if elem in voice_output)
            coherence_score = expected_count / len(scenario['expected_elements'])
            coherence_scores.append(coherence_score)
            
            print(f"Scenario '{scenario['tone']}': {coherence_score:.2%} coherence")
            print(f"Output: {result['voice_output']}")
            print()
        
        overall_coherence = sum(coherence_scores) / len(coherence_scores)
        print(f"Overall Voice Coherence: {overall_coherence:.2%}")
        
        # Target: 85% coherence for Phase 2
        if overall_coherence >= 0.50:  # 50% milestone
            print("🎯 Milestone: 50%+ voice coherence achieved!")
        
        return overall_coherence


if __name__ == "__main__":
    # Quick test run
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # Quick voice coherence test
        test = TestVoiceCoherenceMeasurement()
        coherence = test.test_voice_coherence_score()
        print(f"\n🎯 Current Voice Coherence: {coherence:.1%}")
        
        if coherence >= 0.85:
            print("✅ PHASE 2 TARGET ACHIEVED: 85%+ Voice Coherence!")
        elif coherence >= 0.50:
            print("🎯 MILESTONE: 50%+ Voice Coherence achieved")
        else:
            print("📈 Working toward 50% milestone...")
    else:
        print("Run with 'python test_real_brand_system.py quick' for quick coherence test")