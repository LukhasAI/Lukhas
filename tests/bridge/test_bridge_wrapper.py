import pytest
import os
from unittest.mock import Mock, patch, AsyncMock

from lukhas.bridge.bridge_wrapper import BridgeWrapper, ExternalServiceIntegration, MultiModelOrchestrator, get_bridge_wrapper

class TestExternalServiceIntegration:
    @pytest.fixture
    def service_integration(self):
        return ExternalServiceIntegration()

    def test_initialization_skipped_when_inactive(self, service_integration):
        service_integration._active = False
        result = service_integration.initialize_services()
        assert not result["initialized"]
        assert result["reason"] == "bridge_inactive"

    @patch.dict(os.environ, {"BRIDGE_ACTIVE": "true"})
    def test_initialization_success_dry_run(self, service_integration):
        service_integration = ExternalServiceIntegration() # Re-initialize to pick up env var
        result = service_integration.initialize_services()
        assert result["initialized"]
        assert result["dry_run"]
        assert result["llm_providers"]["openai"]["status"] == "dry_run"
        assert result["service_adapters"]["gmail"]["status"] == "dry_run"

    def test_call_llm_provider_inactive(self, service_integration):
        service_integration._active = False
        result = service_integration.call_llm_provider("openai", "test prompt")
        assert result["error"] == "bridge_inactive"

    def test_call_llm_provider_dry_run(self, service_integration):
        service_integration._dry_run = True
        service_integration._active = True
        result = service_integration.call_llm_provider("openai", "test prompt")
        assert result["dry_run"]
        assert "Simulated response" in result["result"]

class TestMultiModelOrchestrator:
    @pytest.fixture
    def mock_integration(self):
        integration = Mock(spec=ExternalServiceIntegration)
        integration.call_llm_provider.return_value = {"result": "mock response"}
        return integration

    @pytest.fixture
    def orchestrator(self, mock_integration):
        return MultiModelOrchestrator(mock_integration)

    @pytest.mark.asyncio
    async def test_consensus_process_success(self, orchestrator, mock_integration):
        mock_integration.call_llm_provider.side_effect = [
            {"model": "openai", "response": "response 1"},
            {"model": "anthropic", "response": "response 2"},
        ]
        result = await orchestrator.consensus_process("test query", models=["openai", "anthropic"])
        assert "Consensus from 2 models" in result["consensus"]
        assert result["confidence"] > 0.5
        assert len(result["individual_responses"]) == 2

    @pytest.mark.asyncio
    async def test_consensus_process_no_valid_responses(self, orchestrator, mock_integration):
        mock_integration.call_llm_provider.side_effect = [Exception("API error")]
        result = await orchestrator.consensus_process("test query", models=["openai"])
        assert "No valid responses" in result["consensus"]
        assert result["confidence"] == 0.0

class TestBridgeWrapper:
    @pytest.fixture
    def bridge(self):
        return BridgeWrapper()

    @patch("lukhas.bridge.bridge_wrapper.ExternalServiceIntegration.initialize_services")
    def test_initialize_success(self, mock_init_services, bridge):
        mock_init_services.return_value = {"initialized": True}
        assert bridge.initialize()
        assert bridge._initialized

    @patch("lukhas.bridge.bridge_wrapper.ExternalServiceIntegration.initialize_services")
    def test_initialize_failure(self, mock_init_services, bridge):
        mock_init_services.return_value = {"initialized": False, "error": "config missing"}
        assert not bridge.initialize()
        assert not bridge._initialized

    @pytest.mark.asyncio
    @patch("lukhas.bridge.bridge_wrapper.MultiModelOrchestrator.consensus_process", new_callable=AsyncMock)
    async def test_multi_model_query(self, mock_consensus, bridge):
        bridge._initialized = True
        mock_consensus.return_value = {"consensus": "test consensus"}
        result = await bridge.multi_model_query("test")
        assert result["consensus"] == "test consensus"
        mock_consensus.assert_called_once_with("test", None)

    @patch("lukhas.bridge.bridge_wrapper.ExternalServiceIntegration.call_service_adapter")
    def test_service_operation(self, mock_call_adapter, bridge):
        bridge._initialized = True
        mock_call_adapter.return_value = {"result": "success"}
        result = bridge.service_operation("gmail", "send")
        assert result["result"] == "success"
        mock_call_adapter.assert_called_once_with(service="gmail", operation="send")

def test_get_bridge_wrapper_singleton():
    wrapper1 = get_bridge_wrapper()
    wrapper2 = get_bridge_wrapper()
    assert wrapper1 is wrapper2
