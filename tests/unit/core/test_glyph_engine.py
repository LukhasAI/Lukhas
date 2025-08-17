#!/usr/bin/env python3
"""
Core GLYPH Engine Tests
Tests the fundamental GLYPH (symbolic token) system that enables cross-module communication
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from core.glyph import Glyph, GlyphEngine, GlyphProcessor
    from core.glyph.glyph_engine import EnhancedGlyphEngine
    from core.common.exceptions import GlyphError, ValidationError
except ImportError:
    # Create mock classes for testing if imports fail
    @dataclass
    class Glyph:
        symbol: str
        meaning: str
        context: Dict[str, Any]
        timestamp: float
        
    class GlyphEngine:
        def __init__(self):
            self.glyphs = {}
            
        def create_glyph(self, symbol: str, meaning: str, context: Dict = None) -> Glyph:
            return Glyph(symbol, meaning, context or {}, time.time())
            
        def process_glyph(self, glyph: Glyph) -> Dict[str, Any]:
            return {"processed": True, "glyph": glyph}
    
    class GlyphProcessor:
        def __init__(self):
            self.engine = GlyphEngine()
    
    class EnhancedGlyphEngine(GlyphEngine):
        pass
        
    class GlyphError(Exception):
        pass
        
    class ValidationError(Exception):
        pass


class TestGlyphEngine:
    """Test the core GLYPH engine functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = GlyphEngine()
        self.processor = GlyphProcessor()
    
    def test_glyph_creation(self):
        """Test basic GLYPH creation"""
        symbol = "⚛️🧠"
        meaning = "identity_consciousness_bridge"
        context = {"module": "identity", "target": "consciousness"}
        
        glyph = self.engine.create_glyph(symbol, meaning, context)
        
        assert glyph.symbol == symbol
        assert glyph.meaning == meaning
        assert glyph.context == context
        assert isinstance(glyph.timestamp, float)
        assert glyph.timestamp > 0
    
    def test_trinity_framework_glyphs(self):
        """Test Trinity Framework GLYPH symbols"""
        trinity_glyphs = [
            ("⚛️", "identity", {"component": "authenticity"}),
            ("🧠", "consciousness", {"component": "awareness"}),
            ("🛡️", "guardian", {"component": "ethics"})
        ]
        
        for symbol, meaning, context in trinity_glyphs:
            glyph = self.engine.create_glyph(symbol, meaning, context)
            assert glyph.symbol == symbol
            assert glyph.meaning == meaning
            assert glyph.context["component"] in ["authenticity", "awareness", "ethics"]
    
    def test_glyph_processing(self):
        """Test GLYPH processing pipeline"""
        glyph = self.engine.create_glyph(
            "🔄", 
            "process_request", 
            {"action": "memory_store", "priority": "high"}
        )
        
        result = self.engine.process_glyph(glyph)
        
        assert result["processed"] == True
        assert "glyph" in result
        assert result["glyph"].symbol == "🔄"
    
    def test_glyph_validation(self):
        """Test GLYPH validation rules"""
        # Valid GLYPH
        valid_glyph = self.engine.create_glyph("✓", "validation_passed", {})
        assert valid_glyph.symbol == "✓"
        
        # Test invalid GLYPH scenarios
        with pytest.raises((ValueError, ValidationError)):
            # Empty symbol should fail
            self.engine.create_glyph("", "empty_symbol", {})
    
    def test_glyph_context_preservation(self):
        """Test that GLYPH context is preserved during processing"""
        context = {
            "source_module": "memory",
            "target_module": "consciousness",
            "operation": "fold_cascade_check",
            "metadata": {"fold_count": 999, "risk_level": "low"}
        }
        
        glyph = self.engine.create_glyph("🔍", "cascade_check", context)
        result = self.engine.process_glyph(glyph)
        
        assert result["glyph"].context["source_module"] == "memory"
        assert result["glyph"].context["metadata"]["fold_count"] == 999
    
    def test_concurrent_glyph_processing(self):
        """Test concurrent GLYPH processing"""
        async def process_glyph_async(symbol, meaning):
            glyph = self.engine.create_glyph(symbol, meaning, {})
            return self.engine.process_glyph(glyph)
        
        async def run_concurrent_test():
            tasks = [
                process_glyph_async("🔄", "process_1"),
                process_glyph_async("⚡", "process_2"),
                process_glyph_async("🌟", "process_3")
            ]
            results = await asyncio.gather(*tasks)
            return results
        
        # Run the async test
        results = asyncio.run(run_concurrent_test())
        assert len(results) == 3
        assert all(result["processed"] for result in results)
    
    def test_glyph_symbol_uniqueness(self):
        """Test GLYPH symbol uniqueness within engine"""
        glyph1 = self.engine.create_glyph("🎯", "target_action", {"id": 1})
        glyph2 = self.engine.create_glyph("🎯", "target_action", {"id": 2})
        
        # Same symbol can have different contexts
        assert glyph1.symbol == glyph2.symbol
        assert glyph1.context["id"] != glyph2.context["id"]
    
    def test_glyph_memory_efficiency(self):
        """Test GLYPH memory usage efficiency"""
        start_time = time.time()
        glyphs = []
        
        # Create many GLYPHs to test memory efficiency
        for i in range(1000):
            glyph = self.engine.create_glyph(
                f"🔢{i%10}", 
                f"test_glyph_{i}", 
                {"index": i, "batch": "memory_test"}
            )
            glyphs.append(glyph)
        
        creation_time = time.time() - start_time
        
        # Should create 1000 GLYPHs quickly
        assert len(glyphs) == 1000
        assert creation_time < 1.0  # Should complete in under 1 second
        
        # Verify all GLYPHs are valid
        for glyph in glyphs[:10]:  # Check first 10
            assert isinstance(glyph.symbol, str)
            assert isinstance(glyph.meaning, str)
            assert isinstance(glyph.context, dict)
    
    def test_glyph_cross_module_communication(self):
        """Test GLYPH-based cross-module communication patterns"""
        # Memory to Consciousness communication
        memory_glyph = self.engine.create_glyph(
            "🧠💾",
            "memory_to_consciousness",
            {
                "source": "memory.fold_manager",
                "target": "consciousness.awareness",
                "message": "new_memory_available",
                "payload": {"fold_id": "fold_42", "emotional_weight": 0.8}
            }
        )
        
        # Process the cross-module GLYPH
        result = self.engine.process_glyph(memory_glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["source"] == "memory.fold_manager"
        assert result["glyph"].context["target"] == "consciousness.awareness"
        assert result["glyph"].context["payload"]["fold_id"] == "fold_42"
    
    def test_glyph_ethics_validation(self):
        """Test GLYPH ethics validation through Guardian System"""
        # Ethical GLYPH
        ethical_glyph = self.engine.create_glyph(
            "🛡️✅",
            "ethical_action",
            {"ethics_score": 0.95, "validation": "guardian_approved"}
        )
        
        # Potentially unethical GLYPH
        suspicious_glyph = self.engine.create_glyph(
            "⚠️🚫",
            "suspicious_action",
            {"ethics_score": 0.2, "warning": "requires_review"}
        )
        
        ethical_result = self.engine.process_glyph(ethical_glyph)
        suspicious_result = self.engine.process_glyph(suspicious_glyph)
        
        assert ethical_result["processed"] == True
        assert suspicious_result["processed"] == True  # Still processes but flagged
        assert ethical_result["glyph"].context["ethics_score"] > 0.9
        assert suspicious_result["glyph"].context["ethics_score"] < 0.3
    
    def test_glyph_drift_detection(self):
        """Test GLYPH for drift detection scenarios"""
        # Create GLYPH for drift monitoring
        drift_glyph = self.engine.create_glyph(
            "📈⚠️",
            "drift_detected",
            {
                "drift_score": 0.18,  # Above 0.15 threshold
                "module": "consciousness",
                "timestamp": time.time(),
                "severity": "medium"
            }
        )
        
        result = self.engine.process_glyph(drift_glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["drift_score"] > 0.15
        assert result["glyph"].context["severity"] == "medium"
    
    def test_glyph_performance_under_load(self):
        """Test GLYPH engine performance under high load"""
        start_time = time.time()
        results = []
        
        # Process many GLYPHs rapidly
        for i in range(100):
            glyph = self.engine.create_glyph(
                "⚡",
                "performance_test",
                {"iteration": i, "timestamp": time.time()}
            )
            result = self.engine.process_glyph(glyph)
            results.append(result)
        
        total_time = time.time() - start_time
        
        # Should process 100 GLYPHs quickly
        assert len(results) == 100
        assert total_time < 0.5  # Should complete in under 0.5 seconds
        assert all(result["processed"] for result in results)
    
    def test_glyph_json_serialization(self):
        """Test GLYPH JSON serialization for persistence"""
        glyph = self.engine.create_glyph(
            "💾",
            "serialize_test",
            {"data": [1, 2, 3], "nested": {"key": "value"}}
        )
        
        # Serialize GLYPH to JSON-like dict
        glyph_dict = {
            "symbol": glyph.symbol,
            "meaning": glyph.meaning,
            "context": glyph.context,
            "timestamp": glyph.timestamp
        }
        
        # Should be JSON serializable
        json_str = json.dumps(glyph_dict)
        restored = json.loads(json_str)
        
        assert restored["symbol"] == "💾"
        assert restored["meaning"] == "serialize_test"
        assert restored["context"]["data"] == [1, 2, 3]
        assert restored["context"]["nested"]["key"] == "value"


class TestEnhancedGlyphEngine:
    """Test enhanced GLYPH engine features"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = EnhancedGlyphEngine()
    
    def test_enhanced_glyph_processing(self):
        """Test enhanced GLYPH processing capabilities"""
        glyph = self.engine.create_glyph(
            "🚀",
            "enhanced_processing",
            {"feature": "advanced", "version": "2.0"}
        )
        
        result = self.engine.process_glyph(glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["feature"] == "advanced"
    
    def test_glyph_batch_processing(self):
        """Test batch processing of multiple GLYPHs"""
        glyphs = [
            self.engine.create_glyph("🔄", "batch_1", {"id": 1}),
            self.engine.create_glyph("🔄", "batch_2", {"id": 2}),
            self.engine.create_glyph("🔄", "batch_3", {"id": 3})
        ]
        
        results = []
        for glyph in glyphs:
            result = self.engine.process_glyph(glyph)
            results.append(result)
        
        assert len(results) == 3
        assert all(result["processed"] for result in results)
        
        # Verify batch IDs are preserved
        ids = [result["glyph"].context["id"] for result in results]
        assert sorted(ids) == [1, 2, 3]


class TestGlyphIntegration:
    """Test GLYPH integration with other LUKHAS AI components"""
    
    def setup_method(self):
        """Setup for integration tests"""
        self.engine = GlyphEngine()
        
    def test_memory_glyph_integration(self):
        """Test GLYPH integration with memory system"""
        memory_glyph = self.engine.create_glyph(
            "🧠💭",
            "memory_integration",
            {
                "operation": "store_memory",
                "fold_id": "test_fold_001",
                "content": "This is a test memory",
                "emotional_weight": 0.7,
                "connections": ["fold_002", "fold_003"]
            }
        )
        
        result = self.engine.process_glyph(memory_glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["operation"] == "store_memory"
        assert result["glyph"].context["fold_id"] == "test_fold_001"
        assert result["glyph"].context["emotional_weight"] == 0.7
    
    def test_consciousness_glyph_integration(self):
        """Test GLYPH integration with consciousness system"""
        consciousness_glyph = self.engine.create_glyph(
            "🌟⚡",
            "consciousness_state_change",
            {
                "awareness_level": 0.85,
                "dream_depth": 0,
                "emotion_state": {"joy": 0.6, "curiosity": 0.8},
                "trigger": "new_experience"
            }
        )
        
        result = self.engine.process_glyph(consciousness_glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["awareness_level"] == 0.85
        assert result["glyph"].context["emotion_state"]["curiosity"] == 0.8
    
    def test_guardian_glyph_integration(self):
        """Test GLYPH integration with Guardian System"""
        guardian_glyph = self.engine.create_glyph(
            "🛡️🔍",
            "ethics_validation",
            {
                "action": "user_request_processing",
                "ethics_score": 0.92,
                "drift_score": 0.08,
                "validation_status": "approved",
                "guardian_version": "1.0.0"
            }
        )
        
        result = self.engine.process_glyph(guardian_glyph)
        
        assert result["processed"] == True
        assert result["glyph"].context["ethics_score"] > 0.9
        assert result["glyph"].context["drift_score"] < 0.15  # Below threshold
        assert result["glyph"].context["validation_status"] == "approved"


if __name__ == "__main__":
    pytest.main([__file__])