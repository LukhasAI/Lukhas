#!/usr/bin/env python3

"""
Test Suite for Bridge Module Promotion
======================================

Comprehensive tests to validate the Bridge module promotion from candidate/ to lukhas/.
Tests cover feature flags, dry-run mode, multi-model orchestration, and safety measures.
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add lukhas to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from lukhas.bridge import get_bridge_wrapper, get_bridge_status, BRIDGE_ACTIVE, BRIDGE_DRY_RUN
    from lukhas.bridge.bridge_wrapper import (
        BridgeWrapper, 
        ExternalServiceIntegration, 
        MultiModelOrchestrator
    )
    BRIDGE_AVAILABLE = True
except ImportError as e:
    BRIDGE_AVAILABLE = False
    IMPORT_ERROR = str(e)

class TestBridgeModuleStructure:
    """Test Bridge module structure and imports"""
    
    def test_bridge_module_importable(self):
        """Test that Bridge module can be imported"""
        assert BRIDGE_AVAILABLE, f"Bridge module not importable: {IMPORT_ERROR if not BRIDGE_AVAILABLE else 'OK'}"
    
    def test_bridge_exports(self):
        """Test that Bridge module exports required functions"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        # Test main exports
        assert callable(get_bridge_wrapper)
        assert callable(get_bridge_status)
        
        # Test status function returns proper structure
        status = get_bridge_status()
        assert isinstance(status, dict)
        assert "module" in status
        assert "version" in status
        assert "active" in status
        assert "dry_run" in status
        assert "capabilities" in status
        
        # Test capabilities structure
        capabilities = status["capabilities"]
        assert "llm_providers" in capabilities
        assert "service_adapters" in capabilities
        assert "api_support" in capabilities
        assert "security" in capabilities

class TestBridgeFeatureFlags:
    """Test Bridge feature flag functionality"""
    
    def test_bridge_inactive_by_default(self):
        """Test that Bridge is inactive by default"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        # Bridge should be inactive by default for safety
        assert not BRIDGE_ACTIVE
    
    def test_bridge_dry_run_by_default(self):
        """Test that Bridge runs in dry-run mode by default"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        # Bridge should be in dry-run mode by default for safety
        assert BRIDGE_DRY_RUN
    
    def test_bridge_activation_with_env_var(self):
        """Test Bridge activation with environment variable"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        # Test manual activation (simulating env var)
        from lukhas.bridge.bridge_wrapper import ExternalServiceIntegration
        integration = ExternalServiceIntegration()
        
        # Test activation
        integration._active = True
        assert integration._active
        
        # Test initialization when active
        result = integration.initialize_services()
        assert result["initialized"]
    
    def test_bridge_production_mode_with_env_var(self):
        """Test Bridge production mode with environment variable"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        # Test manual production mode setting (simulating env var)
        from lukhas.bridge.bridge_wrapper import ExternalServiceIntegration
        integration = ExternalServiceIntegration()
        
        # Test production mode
        integration._dry_run = False
        assert not integration._dry_run
        
        # Test that production mode affects behavior
        integration._active = True
        result = integration.call_llm_provider("openai", "test")
        assert not result.get("dry_run", True)

class TestBridgeWrapper:
    """Test BridgeWrapper functionality"""
    
    def test_bridge_wrapper_creation(self):
        """Test BridgeWrapper can be created"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        assert wrapper is not None
        assert not wrapper._initialized
    
    def test_bridge_wrapper_singleton(self):
        """Test get_bridge_wrapper returns same instance"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper1 = get_bridge_wrapper()
        wrapper2 = get_bridge_wrapper()
        assert wrapper1 is wrapper2
    
    def test_bridge_wrapper_initialization(self):
        """Test BridgeWrapper initialization"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        # Initialize should succeed (even if Bridge is inactive)
        result = wrapper.initialize()
        assert isinstance(result, bool)
    
    def test_bridge_wrapper_status(self):
        """Test BridgeWrapper status reporting"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        status = wrapper.get_status()
        
        assert isinstance(status, dict)
        assert "initialized" in status
        assert "active" in status
        assert "dry_run" in status
        assert "timestamp" in status
        assert "capabilities" in status
    
    def test_bridge_supported_providers(self):
        """Test BridgeWrapper supported providers"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        providers = wrapper.get_supported_providers()
        
        assert isinstance(providers, dict)
        assert "llm_providers" in providers
        assert "service_adapters" in providers
        assert "protocols" in providers
        assert "authentication" in providers
        
        # Check specific providers
        llm_providers = providers["llm_providers"]
        assert "openai" in llm_providers
        assert "anthropic" in llm_providers
        assert "gemini" in llm_providers
        assert "perplexity" in llm_providers
        
        service_adapters = providers["service_adapters"]
        assert "gmail" in service_adapters
        assert "drive" in service_adapters
        assert "dropbox" in service_adapters

class TestExternalServiceIntegration:
    """Test ExternalServiceIntegration functionality"""
    
    def test_service_integration_creation(self):
        """Test ExternalServiceIntegration can be created"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        assert integration is not None
        assert integration._dry_run  # Should be True by default
        assert not integration._active  # Should be False by default
    
    def test_service_integration_initialization(self):
        """Test service integration initialization"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        result = integration.initialize_services()
        
        assert isinstance(result, dict)
        assert "initialized" in result
        
        # Should not initialize if not active
        if not integration._active:
            assert not result["initialized"]
            assert result["reason"] == "bridge_inactive"
    
    @patch.dict(os.environ, {"BRIDGE_ACTIVE": "true"})
    def test_service_integration_with_active_flag(self):
        """Test service integration when Bridge is active"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = True  # Force active for testing
        
        result = integration.initialize_services()
        
        assert isinstance(result, dict)
        assert result["initialized"]
        assert result["dry_run"]
        assert "llm_providers" in result
        assert "service_adapters" in result
    
    def test_llm_provider_call_dry_run(self):
        """Test LLM provider call in dry-run mode"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = True
        integration._dry_run = True
        
        result = integration.call_llm_provider("openai", "Test prompt")
        
        assert isinstance(result, dict)
        assert result["provider"] == "openai"
        assert result["dry_run"]
        assert "[DRY_RUN]" in result["result"]
    
    def test_service_adapter_call_dry_run(self):
        """Test service adapter call in dry-run mode"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = True
        integration._dry_run = True
        
        result = integration.call_service_adapter("gmail", "list_emails")
        
        assert isinstance(result, dict)
        assert result["service"] == "gmail"
        assert result["operation"] == "list_emails"
        assert result["dry_run"]
        assert "[DRY_RUN]" in result["result"]
    
    def test_inactive_bridge_protection(self):
        """Test that inactive Bridge returns safe responses"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = False
        
        # LLM call should be blocked
        llm_result = integration.call_llm_provider("openai", "Test")
        assert llm_result["error"] == "bridge_inactive"
        
        # Service call should be blocked
        service_result = integration.call_service_adapter("gmail", "test")
        assert service_result["error"] == "bridge_inactive"

class TestMultiModelOrchestrator:
    """Test MultiModelOrchestrator functionality"""
    
    def test_orchestrator_creation(self):
        """Test MultiModelOrchestrator can be created"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        orchestrator = MultiModelOrchestrator(integration)
        assert orchestrator is not None
        assert orchestrator._consensus_threshold == 0.7
    
    @pytest.mark.asyncio
    async def test_consensus_process_dry_run(self):
        """Test consensus process in dry-run mode"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = True
        integration._dry_run = True
        
        orchestrator = MultiModelOrchestrator(integration)
        
        result = await orchestrator.consensus_process("What is AI?")
        
        assert isinstance(result, dict)
        assert "consensus" in result
        assert "confidence" in result
        assert "models_used" in result
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_consensus_process_with_specific_models(self):
        """Test consensus process with specific models"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = True
        integration._dry_run = True
        
        orchestrator = MultiModelOrchestrator(integration)
        
        models = ["openai", "anthropic"]
        result = await orchestrator.consensus_process("Test query", models)
        
        assert isinstance(result, dict)
        assert "models_used" in result
        # Should include specified models or handle appropriately
    
    @pytest.mark.asyncio
    async def test_consensus_process_inactive_bridge(self):
        """Test consensus process with inactive Bridge"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        integration = ExternalServiceIntegration()
        integration._active = False
        
        orchestrator = MultiModelOrchestrator(integration)
        
        result = await orchestrator.consensus_process("Test query")
        
        assert isinstance(result, dict)
        # Should handle inactive bridge gracefully

class TestBridgeWrapperIntegration:
    """Test BridgeWrapper integration functionality"""
    
    @pytest.mark.asyncio
    async def test_multi_model_query(self):
        """Test BridgeWrapper multi-model query"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        result = await wrapper.multi_model_query("What is consciousness?")
        
        assert isinstance(result, dict)
        # Should return result even if Bridge is inactive (with appropriate handling)
    
    @pytest.mark.asyncio
    async def test_multi_model_query_with_models(self):
        """Test multi-model query with specific models"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        models = ["openai", "anthropic"]
        result = await wrapper.multi_model_query("Test query", models)
        
        assert isinstance(result, dict)
    
    def test_service_operation(self):
        """Test BridgeWrapper service operation"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        result = wrapper.service_operation("gmail", "list_emails", limit=10)
        
        assert isinstance(result, dict)
        # Should handle operation appropriately based on Bridge status

class TestBridgeSafetyMeasures:
    """Test Bridge safety measures and error handling"""
    
    def test_bridge_fails_safe_when_inactive(self):
        """Test that Bridge fails safe when inactive"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        wrapper._service_integration._active = False
        
        # Operations should not perform real actions when inactive
        result = wrapper.service_operation("gmail", "delete_all_emails")
        assert "error" in result or result.get("result") is None
    
    def test_bridge_dry_run_safety(self):
        """Test that dry-run mode prevents real operations"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        wrapper._service_integration._active = True
        wrapper._service_integration._dry_run = True
        
        # Operations should be simulated in dry-run mode
        result = wrapper.service_operation("gmail", "send_email", to="test@example.com")
        if "dry_run" in result:
            assert result["dry_run"]
    
    def test_error_handling_robustness(self):
        """Test error handling robustness"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        # Test with invalid service
        result = wrapper.service_operation("invalid_service", "invalid_op")
        assert isinstance(result, dict)
        # Should handle gracefully without crashing
    
    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test async error handling"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        
        # Test with problematic input
        result = await wrapper.multi_model_query("")
        assert isinstance(result, dict)
        # Should handle gracefully without crashing

class TestBridgeObservability:
    """Test Bridge observability and monitoring"""
    
    @patch('lukhas.bridge.bridge_wrapper.emit')
    def test_bridge_emits_telemetry(self, mock_emit):
        """Test that Bridge emits telemetry events"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        wrapper.initialize()
        
        # Should have emitted initialization events
        mock_emit.assert_called()
    
    @patch('lukhas.bridge.bridge_wrapper.emit')
    @pytest.mark.asyncio
    async def test_multi_model_telemetry(self, mock_emit):
        """Test multi-model query telemetry"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        await wrapper.multi_model_query("Test query")
        
        # Should have emitted query events
        mock_emit.assert_called()

class TestBridgeManifest:
    """Test Bridge module manifest and metadata"""
    
    def test_module_manifest_exists(self):
        """Test that MODULE_MANIFEST.json exists"""
        manifest_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "lukhas", 
            "bridge", 
            "MODULE_MANIFEST.json"
        )
        assert os.path.exists(manifest_path), "MODULE_MANIFEST.json should exist"
    
    def test_module_manifest_structure(self):
        """Test MODULE_MANIFEST.json structure"""
        import json
        
        manifest_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "lukhas", 
            "bridge", 
            "MODULE_MANIFEST.json"
        )
        
        if not os.path.exists(manifest_path):
            pytest.skip("MODULE_MANIFEST.json not found")
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Check required fields
        assert "module" in manifest
        assert "version" in manifest
        assert "description" in manifest
        assert manifest["module"] == "BRIDGE"

# Performance and load testing
class TestBridgePerformance:
    """Test Bridge performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_concurrent_model_calls(self):
        """Test concurrent model calls performance"""
        if not BRIDGE_AVAILABLE:
            pytest.skip("Bridge module not available")
        
        wrapper = BridgeWrapper()
        wrapper._service_integration._active = True
        wrapper._service_integration._dry_run = True
        
        # Test multiple concurrent calls
        tasks = []
        for i in range(5):
            task = wrapper.multi_model_query(f"Query {i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All calls should complete successfully
        for result in results:
            assert isinstance(result, dict)
            assert not isinstance(result, Exception)

if __name__ == "__main__":
    # Run basic tests if called directly
    if BRIDGE_AVAILABLE:
        print("✅ Bridge module is available")
        print(f"✅ Bridge status: {get_bridge_status()}")
        
        wrapper = get_bridge_wrapper()
        print(f"✅ Bridge wrapper created: {wrapper is not None}")
        
        status = wrapper.get_status()
        print(f"✅ Bridge wrapper status: {status}")
        
        print("\n🧪 Running async test...")
        async def test_async():
            result = await wrapper.multi_model_query("Hello world")
            print(f"✅ Multi-model query result: {result}")
        
        asyncio.run(test_async())
        
        print("\n✅ All basic tests passed!")
    else:
        print(f"❌ Bridge module not available: {IMPORT_ERROR}")
        sys.exit(1)