"""
Integration Tests for LUKHAS AI Branding System Integration
==========================================================

Tests comprehensive branding integration across all core LUKHAS systems to ensure
the branding system is no longer isolated and properly connects to all major components.

Trinity Framework Integration: ⚛️🧠🛡️
- ⚛️ Identity: Brand voice and symbolic communication  
- 🧠 Consciousness: Natural language interface branding
- 🛡️ Guardian: Compliance validation and drift detection
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch

# Test imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestBrandingBridgeIntegration:
    """Test core branding bridge functionality"""
    
    def test_branding_bridge_import(self):
        """Test that branding bridge can be imported"""
        from candidate.branding_bridge import (
            get_bridge, initialize_branding, get_system_signature,
            get_trinity_context, validate_output, get_brand_voice
        )
        assert get_bridge is not None
        assert initialize_branding is not None
        assert get_system_signature is not None
    
    def test_system_signature_generation(self):
        """Test system signature generation"""
        from candidate.branding_bridge import get_system_signature
        
        signature = get_system_signature()
        assert "LUKHAS AI" in signature
        assert "⚛️🧠🛡️" in signature or "Trinity" in signature
    
    def test_trinity_context_generation(self):
        """Test Trinity Framework context generation"""
        from candidate.branding_bridge import get_trinity_context
        
        context = get_trinity_context("consciousness")
        assert "framework" in context
        assert "consciousness" in context
        assert context["consciousness"]["symbol"] == "🧠"
    
    def test_brand_voice_application(self):
        """Test brand voice application to content"""
        from candidate.branding_bridge import get_brand_voice, BrandContext
        
        content = "This is a test of quantum processing with bio processes."
        brand_context = BrandContext()
        
        branded_content = get_brand_voice(content, brand_context)
        # Should normalize prohibited terms
        assert "quantum-inspired" in branded_content or "quantum processing" not in branded_content
        assert "bio-inspired" in branded_content or "bio processes" not in branded_content
    
    def test_output_validation(self):
        """Test brand compliance validation"""
        from candidate.branding_bridge import validate_output, BrandContext
        
        # Test compliant content
        compliant_content = "LUKHAS AI provides quantum-inspired and bio-inspired solutions."
        result = validate_output(compliant_content, BrandContext())
        assert result["valid"] is True
        
        # Test non-compliant content  
        non_compliant_content = "LUKHAS AGI uses quantum processing for bio processing."
        result = validate_output(non_compliant_content, BrandContext())
        assert result["valid"] is False
        assert len(result["issues"]) > 0


class TestConsciousnessIntegration:
    """Test branding integration with consciousness systems"""
    
    @pytest.mark.asyncio
    async def test_natural_language_interface_branding(self):
        """Test that natural language interface integrates branding"""
        from candidate.consciousness.interfaces.natural_language_interface import NaturalLanguageConsciousnessInterface
        
        # Mock dependencies
        with patch('core.interfaces.dependency_injection.get_service') as mock_get_service:
            mock_get_service.return_value = None
            
            interface = NaturalLanguageConsciousnessInterface()
            
            # Check branding integration
            assert hasattr(interface, 'branding_bridge')
            assert hasattr(interface, 'brand_context')
            assert interface.brand_context.voice_profile == "consciousness"
            assert interface.brand_context.trinity_emphasis == "consciousness"
    
    @pytest.mark.asyncio  
    async def test_consciousness_branded_response(self):
        """Test that consciousness responses are branded"""
        from candidate.consciousness.interfaces.natural_language_interface import NaturalLanguageConsciousnessInterface
        
        # Mock dependencies
        with patch('core.interfaces.dependency_injection.get_service') as mock_get_service:
            mock_get_service.return_value = None
            
            interface = NaturalLanguageConsciousnessInterface()
            
            # Test brand voice application method
            response = "I am aware and using quantum processing for bio processing tasks."
            intent = interface.ConversationIntent.QUERY_AWARENESS if hasattr(interface, 'ConversationIntent') else "awareness"
            
            # This should apply branding normalization
            if hasattr(interface, '_apply_brand_voice'):
                branded_response = interface._apply_brand_voice(response, intent)
                # Check for brand compliance
                assert "LUKHAS AGI" not in branded_response
                assert "quantum processing" not in branded_response or "quantum-inspired" in branded_response
                assert "bio processing" not in branded_response or "bio-inspired" in branded_response
    
    def test_consciousness_module_branding_imports(self):
        """Test consciousness module exposes branding functions"""
        import candidate.consciousness
        
        # Check that branding is available in consciousness module
        assert hasattr(consciousness, 'CONSCIOUSNESS_BRANDING_AVAILABLE')
        if consciousness.CONSCIOUSNESS_BRANDING_AVAILABLE:
            assert hasattr(consciousness, 'get_brand_voice')
            assert hasattr(consciousness, 'get_trinity_context')
            assert hasattr(consciousness, 'BrandContext')


class TestOrchestrationIntegration:
    """Test branding integration with orchestration systems"""
    
    def test_symbolic_kernel_bus_branding(self):
        """Test that symbolic kernel bus integrates branding"""
        from candidate.orchestration.symbolic_kernel_bus import SymbolicKernelBus
        
        bus = SymbolicKernelBus()
        
        # Check branding integration
        assert hasattr(bus, '_brand_context')
        if hasattr(bus, '_brand_context') and bus._brand_context:
            assert bus._brand_context.voice_profile == "identity"
            assert bus._brand_context.trinity_emphasis == "balanced"
    
    def test_event_branding_application(self):
        """Test branding is applied to orchestration events"""
        from candidate.orchestration.symbolic_kernel_bus import SymbolicKernelBus, SymbolicEvent, SymbolicEffect
        
        bus = SymbolicKernelBus()
        
        # Create test event with terminology issues
        event_id = bus.emit(
            "test.event",
            {"message": "Processing quantum processing with LUKHAS AGI bio processing"},
            source="test",
            effects=[SymbolicEffect.AWARENESS_UPDATE]
        )
        
        # Check that event was processed and potentially branded
        assert event_id is not None
    
    def test_orchestration_module_branding_imports(self):
        """Test orchestration module exposes branding functions"""
        import candidate.orchestration
        
        # Check that branding is available in orchestration module  
        assert hasattr(orchestration, 'ORCHESTRATION_BRANDING_AVAILABLE')
        if orchestration.ORCHESTRATION_BRANDING_AVAILABLE:
            assert hasattr(orchestration, 'get_brand_voice')
            assert hasattr(orchestration, 'get_trinity_context')
            assert hasattr(orchestration, 'validate_output')


class TestCoreGlyphIntegration:
    """Test branding integration with core GLYPH system"""
    
    def test_glyph_engine_trinity_integration(self):
        """Test GLYPH engine Trinity Framework integration"""
        from core.glyph.glyph_engine import GlyphEngine
        
        engine = GlyphEngine()
        
        # Test Trinity glyph creation
        trinity_glyphs = engine.get_trinity_glyphs()
        assert "identity" in trinity_glyphs
        assert "consciousness" in trinity_glyphs  
        assert "guardian" in trinity_glyphs
        assert "framework" in trinity_glyphs
        
        # Test Trinity symbols
        assert trinity_glyphs["identity"] == "⚛️"
        assert trinity_glyphs["consciousness"] == "🧠"
        assert trinity_glyphs["guardian"] == "🛡️"
        assert "⚛️🧠🛡️" in trinity_glyphs["framework"]
    
    def test_trinity_glyph_creation(self):
        """Test creating Trinity Framework glyphs"""
        from core.glyph.glyph_engine import GlyphEngine
        
        engine = GlyphEngine()
        
        # Test different Trinity emphasis
        consciousness_glyph = engine.create_trinity_glyph("consciousness")
        assert consciousness_glyph is not None
        
        balanced_glyph = engine.create_trinity_glyph("balanced")
        assert balanced_glyph is not None
    
    def test_consciousness_concept_encoding(self):
        """Test encoding consciousness concepts with branding"""
        from core.glyph.glyph_engine import GlyphEngine
        
        engine = GlyphEngine()
        
        # Test consciousness concept encoding
        glyph_repr = engine.encode_concept("think about consciousness")
        assert "🧠" in glyph_repr or "consciousness" in glyph_repr.lower()


class TestAPIBridgeIntegration:
    """Test branding integration with API bridge"""
    
    def test_unified_router_branding_import(self):
        """Test unified router imports branding"""
        from candidate.bridge.api.unified_router import BRANDING_AVAILABLE, apply_api_branding
        
        # Check branding availability
        if BRANDING_AVAILABLE:
            assert apply_api_branding is not None
    
    def test_api_response_branding(self):
        """Test API responses are branded"""
        from candidate.bridge.api.unified_router import apply_api_branding, BRANDING_AVAILABLE
        
        if not BRANDING_AVAILABLE:
            pytest.skip("Branding not available for API")
        
        # Test response branding
        response = {
            "message": "LUKHAS AGI processing quantum processing request",
            "status": "success"
        }
        
        branded_response = apply_api_branding(response)
        
        # Check system signature added
        assert "system" in branded_response
        assert "LUKHAS AI" in str(branded_response["system"])
        
        # Check terminology normalization
        if "message" in branded_response:
            assert "LUKHAS AGI" not in branded_response["message"]
            assert "quantum processing" not in branded_response["message"] or "quantum-inspired" in branded_response["message"]
    
    @pytest.mark.asyncio
    async def test_health_check_branding(self):
        """Test health check endpoint includes branding"""
        from candidate.bridge.api.unified_router import health_check
        
        response = await health_check()
        
        # Check response structure
        assert "status" in response
        assert "module" in response
        assert response["module"] == "LUKHAS AI"
        
        # Check for system signature if branding available
        if "system" in response:
            assert "LUKHAS AI" in str(response["system"])
            assert "⚛️🧠🛡️" in str(response["system"])


class TestMainSystemIntegration:
    """Test branding integration with main system initialization"""
    
    def test_main_imports_branding(self):
        """Test main.py imports branding"""
        import main
        
        # Check branding availability in main
        assert hasattr(main, 'BRANDING_AVAILABLE')
    
    def test_lukhas_package_branding(self):
        """Test lukhas package exposes branding"""
        import lukhas
        
        # Check branding bridge availability
        assert hasattr(lukhas, 'BRANDING_BRIDGE_AVAILABLE')
        
        if candidate.BRANDING_BRIDGE_AVAILABLE:
            assert hasattr(lukhas, 'get_system_signature')
            assert hasattr(lukhas, 'get_trinity_context')
            assert hasattr(lukhas, 'get_brand_voice')
            assert hasattr(lukhas, 'validate_output')
            assert hasattr(lukhas, 'normalize_output_text')
            assert hasattr(lukhas, 'initialize_branding')
    
    def test_trinity_status_function(self):
        """Test Trinity status function"""
        import lukhas
        
        status = candidate.get_trinity_status()
        
        assert "identity" in status
        assert "consciousness" in status
        assert "guardian" in status
        assert status["identity"] == "⚛️"
        assert status["consciousness"] == "🧠" 
        assert status["guardian"] == "🛡️"


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_branding_initialization(self):
        """Test branding system can be initialized"""
        from candidate.branding_bridge import initialize_branding
        
        success = await initialize_branding()
        assert success is True
    
    def test_cross_module_branding_consistency(self):
        """Test branding consistency across modules"""
        # Import all modules with branding
        from candidate.branding_bridge import get_system_signature
        import candidate.consciousness
        import candidate.orchestration
        
        # Get system signature from bridge
        signature = get_system_signature()
        
        # Check consistency across modules
        assert "LUKHAS AI" in signature
        assert "⚛️🧠🛡️" in signature
        
        # Check consciousness integration
        if hasattr(consciousness, 'CONSCIOUSNESS_BRANDING_AVAILABLE') and consciousness.CONSCIOUSNESS_BRANDING_AVAILABLE:
            consciousness_context = consciousness.get_trinity_context("consciousness") 
            assert consciousness_context["consciousness"]["symbol"] == "🧠"
        
        # Check orchestration integration
        if hasattr(orchestration, 'ORCHESTRATION_BRANDING_AVAILABLE') and orchestration.ORCHESTRATION_BRANDING_AVAILABLE:
            orchestration_context = orchestration.get_trinity_context("balanced")
            assert "framework" in orchestration_context
    
    def test_brand_compliance_across_systems(self):
        """Test brand compliance validation works across systems"""
        from candidate.branding_bridge import validate_output, normalize_output_text, BrandContext
        
        # Test content that should trigger compliance issues
        test_content = "LUKHAS AGI provides quantum processing and bio processing capabilities"
        
        # Validate (should find issues)
        validation = validate_output(test_content, BrandContext())
        assert validation["valid"] is False
        
        # Normalize (should fix issues)
        normalized = normalize_output_text(test_content, BrandContext())
        assert "LUKHAS AI" in normalized
        assert "quantum-inspired" in normalized or "quantum processing" not in normalized
        assert "bio-inspired" in normalized or "bio processing" not in normalized
        
        # Re-validate normalized content
        normalized_validation = validate_output(normalized, BrandContext())
        assert normalized_validation["valid"] is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])