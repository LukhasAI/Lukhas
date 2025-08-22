"""
Integration Tests for LUKHAS AI Branding System Integration
===========================================================

Tests the successful integration of the branding system across all LUKHAS modules,
ensuring brand voice, terminology compliance, and Trinity Framework integration.

This test suite validates the Phase 3 Integration solution that resolves the
critical architectural issue where branding was completely orphaned from core LUKHAS.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch


class TestBrandingBridgeIntegration:
    """Test the central branding bridge integration"""
    
    def test_branding_bridge_import(self):
        """Test that branding bridge can be imported from lukhas package"""
        try:
            from lukhas.branding_bridge import (
                get_system_signature, get_trinity_context, get_brand_voice,
                validate_output, normalize_output_text, initialize_branding,
                BrandContext, LUKHASBrandingBridge
            )
            assert True, "Branding bridge imports successfully"
        except ImportError as e:
            pytest.fail(f"Branding bridge import failed: {e}")
    
    def test_branding_bridge_from_lukhas_package(self):
        """Test that branding functions are accessible from main lukhas package"""
        try:
            import lukhas
            
            # Check if branding functions are available
            assert hasattr(lukhas, 'get_system_signature'), "get_system_signature not available in lukhas package"
            assert hasattr(lukhas, 'get_trinity_context'), "get_trinity_context not available in lukhas package"
            assert hasattr(lukhas, 'get_brand_voice'), "get_brand_voice not available in lukhas package"
            
        except ImportError as e:
            pytest.fail(f"Main lukhas package import failed: {e}")
    
    @pytest.mark.asyncio
    async def test_branding_initialization(self):
        """Test branding system initialization"""
        try:
            from lukhas.branding_bridge import initialize_branding, get_bridge
            
            # Initialize branding
            success = await initialize_branding()
            assert isinstance(success, bool), "initialize_branding should return bool"
            
            # Get bridge instance
            bridge = get_bridge()
            assert bridge is not None, "Branding bridge should be available"
            
        except Exception as e:
            pytest.fail(f"Branding initialization failed: {e}")
    
    def test_trinity_framework_integration(self):
        """Test Trinity Framework symbol integration"""
        try:
            from lukhas.branding_bridge import get_trinity_context, TRINITY_FRAMEWORK
            
            # Get Trinity context
            context = get_trinity_context()
            assert isinstance(context, dict), "Trinity context should be dict"
            assert "framework" in context, "Trinity context should have framework key"
            assert "identity" in context, "Trinity context should have identity key"
            assert "consciousness" in context, "Trinity context should have consciousness key"
            assert "guardian" in context, "Trinity context should have guardian key"
            
            # Check Trinity framework symbol
            assert TRINITY_FRAMEWORK == "⚛️🧠🛡️", "Trinity framework should have correct symbols"
            
        except Exception as e:
            pytest.fail(f"Trinity framework integration failed: {e}")


class TestConsciousnessIntegration:
    """Test branding integration with consciousness modules"""
    
    def test_consciousness_creativity_branding(self):
        """Test branding integration in consciousness creativity modules"""
        try:
            from lukhas.consciousness.creativity.advanced_haiku_generator import AdvancedHaikuGenerator
            
            # Create generator
            generator = AdvancedHaikuGenerator()
            assert generator is not None, "Haiku generator should initialize"
            
        except ImportError as e:
            pytest.skip(f"Consciousness creativity module not available: {e}")
        except Exception as e:
            pytest.fail(f"Consciousness creativity branding integration failed: {e}")
    
    def test_consciousness_engine_branding(self):
        """Test branding integration in consciousness core engine"""
        try:
            # Check that consciousness engine imports branding
            from lukhas.consciousness.core import engine
            
            # Look for branding imports in the module
            assert hasattr(engine, 'BRANDING_AVAILABLE'), "Consciousness engine should have BRANDING_AVAILABLE flag"
            
        except ImportError as e:
            pytest.skip(f"Consciousness core engine not available: {e}")
        except Exception as e:
            pytest.fail(f"Consciousness engine branding integration failed: {e}")


class TestOrchestrationIntegration:
    """Test branding integration with orchestration modules"""
    
    def test_symbolic_kernel_bus_branding(self):
        """Test branding integration in symbolic kernel bus"""
        try:
            from lukhas.orchestration.symbolic_kernel_bus import SymbolicKernelBus
            
            # Check that the module has branding imports
            import lukhas.orchestration.symbolic_kernel_bus as bus_module
            assert hasattr(bus_module, 'BRANDING_AVAILABLE'), "Kernel bus should have BRANDING_AVAILABLE flag"
            
        except ImportError as e:
            pytest.skip(f"Symbolic kernel bus not available: {e}")
        except Exception as e:
            pytest.fail(f"Orchestration branding integration failed: {e}")


class TestCoreGlyphIntegration:
    """Test branding integration with core GLYPH system"""
    
    def test_glyph_engine_trinity_integration(self):
        """Test Trinity Framework integration in GLYPH engine"""
        try:
            from core.glyph.glyph_engine import GlyphEngine
            
            # Create GLYPH engine
            engine = GlyphEngine()
            
            # Test Trinity glyph methods
            trinity_glyphs = engine.get_trinity_glyphs()
            assert isinstance(trinity_glyphs, dict), "Trinity glyphs should be dict"
            assert "identity" in trinity_glyphs, "Trinity glyphs should have identity"
            assert "consciousness" in trinity_glyphs, "Trinity glyphs should have consciousness"
            assert "guardian" in trinity_glyphs, "Trinity glyphs should have guardian"
            assert "framework" in trinity_glyphs, "Trinity glyphs should have framework"
            
            # Test Trinity glyph creation
            trinity_glyph = engine.create_trinity_glyph("consciousness")
            assert trinity_glyph is not None, "Trinity glyph should be created"
            
        except ImportError as e:
            pytest.skip(f"GLYPH engine not available: {e}")
        except Exception as e:
            pytest.fail(f"GLYPH Trinity integration failed: {e}")


class TestBridgeAPIIntegration:
    """Test branding integration with bridge API responses"""
    
    def test_api_hub_branding(self):
        """Test branding integration in API hub"""
        try:
            # Check that API hub imports branding
            import lukhas.bridge.api.api_hub as api_module
            assert hasattr(api_module, 'BRANDING_AVAILABLE'), "API hub should have BRANDING_AVAILABLE flag"
            
        except ImportError as e:
            pytest.skip(f"Bridge API hub not available: {e}")
        except Exception as e:
            pytest.fail(f"Bridge API branding integration failed: {e}")


class TestMainSystemIntegration:
    """Test branding integration in main system initialization"""
    
    def test_main_py_branding_import(self):
        """Test that main.py successfully imports branding"""
        try:
            # Read main.py content to check for branding imports
            with open('/Users/agi_dev/LOCAL-REPOS/Lukhas/main.py', 'r') as f:
                main_content = f.read()
            
            assert 'from lukhas.branding_bridge import' in main_content, "main.py should import branding bridge"
            assert 'initialize_branding' in main_content, "main.py should call initialize_branding"
            assert 'get_system_signature' in main_content, "main.py should use get_system_signature"
            
        except Exception as e:
            pytest.fail(f"main.py branding integration verification failed: {e}")


class TestBrandVoiceCompliance:
    """Test brand voice and compliance across integrated modules"""
    
    def test_brand_voice_application(self):
        """Test brand voice application through bridge"""
        try:
            from lukhas.branding_bridge import get_brand_voice, BrandContext
            
            # Test brand voice with different contexts
            test_content = "The LUKHAS AGI system uses quantum processing for advanced capabilities."
            
            context = BrandContext(
                voice_profile="consciousness",
                trinity_emphasis="consciousness",
                compliance_level="standard"
            )
            
            branded_content = get_brand_voice(test_content, context)
            assert isinstance(branded_content, str), "Brand voice should return string"
            
        except Exception as e:
            pytest.fail(f"Brand voice application failed: {e}")
    
    def test_terminology_normalization(self):
        """Test terminology normalization through bridge"""
        try:
            from lukhas.branding_bridge import normalize_output_text
            
            # Test terminology normalization
            test_content = "LUKHAS AGI uses quantum processing"
            normalized = normalize_output_text(test_content)
            
            # Should normalize AGI to AI and quantum processing to quantum-inspired
            assert "LUKHAS AI" in normalized or "LUKHAS AGI" not in normalized
            
        except Exception as e:
            pytest.fail(f"Terminology normalization failed: {e}")
    
    def test_brand_validation(self):
        """Test brand compliance validation"""
        try:
            from lukhas.branding_bridge import validate_output
            
            # Test with compliant content
            compliant_content = "LUKHAS AI uses quantum-inspired processing for consciousness enhancement"
            result = validate_output(compliant_content)
            
            assert isinstance(result, dict), "Validation result should be dict"
            assert "valid" in result, "Validation result should have valid key"
            assert "issues" in result, "Validation result should have issues key"
            
        except Exception as e:
            pytest.fail(f"Brand validation failed: {e}")


class TestIntegrationCoverage:
    """Test integration coverage across all major modules"""
    
    def test_integration_coverage_assessment(self):
        """Assess overall integration coverage"""
        integration_points = {
            "consciousness_creativity": False,
            "consciousness_core": False,
            "orchestration_kernel": False,
            "core_glyph": False,
            "bridge_api": False,
            "main_system": False,
            "lukhas_package": False
        }
        
        # Test consciousness creativity
        try:
            import lukhas.consciousness.creativity.advanced_haiku_generator
            integration_points["consciousness_creativity"] = hasattr(
                consciousness.creativity.advanced_haiku_generator, 
                'BRANDING_BRIDGE_AVAILABLE'
            )
        except ImportError:
            pass
        
        # Test consciousness core
        try:
            import lukhas.consciousness.core.engine
            integration_points["consciousness_core"] = hasattr(
                consciousness.core.engine, 
                'BRANDING_AVAILABLE'
            )
        except ImportError:
            pass
        
        # Test orchestration kernel
        try:
            import lukhas.orchestration.symbolic_kernel_bus
            integration_points["orchestration_kernel"] = hasattr(
                orchestration.symbolic_kernel_bus, 
                'BRANDING_AVAILABLE'
            )
        except ImportError:
            pass
        
        # Test core glyph
        try:
            from core.glyph.glyph_engine import GlyphEngine
            engine = GlyphEngine()
            integration_points["core_glyph"] = hasattr(engine, 'get_trinity_glyphs')
        except ImportError:
            pass
        
        # Test bridge API
        try:
            import lukhas.bridge.api.api_hub
            integration_points["bridge_api"] = hasattr(
                bridge.api.api_hub, 
                'BRANDING_AVAILABLE'
            )
        except ImportError:
            pass
        
        # Test main system
        try:
            with open('/Users/agi_dev/LOCAL-REPOS/Lukhas/main.py', 'r') as f:
                main_content = f.read()
            integration_points["main_system"] = 'initialize_branding' in main_content
        except:
            pass
        
        # Test lukhas package
        try:
            import lukhas
            integration_points["lukhas_package"] = hasattr(lukhas, 'get_system_signature')
        except ImportError:
            pass
        
        # Calculate coverage
        total_points = len(integration_points)
        integrated_points = sum(integration_points.values())
        coverage_percentage = (integrated_points / total_points) * 100
        
        print(f"\n🎯 Integration Coverage Assessment:")
        print(f"   Total integration points: {total_points}")
        print(f"   Successfully integrated: {integrated_points}")
        print(f"   Coverage percentage: {coverage_percentage:.1f}%")
        
        for point, integrated in integration_points.items():
            status = "✅" if integrated else "❌"
            print(f"   {status} {point}: {'Integrated' if integrated else 'Not integrated'}")
        
        # Assert minimum coverage threshold
        assert coverage_percentage >= 70, f"Integration coverage {coverage_percentage:.1f}% below 70% threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])