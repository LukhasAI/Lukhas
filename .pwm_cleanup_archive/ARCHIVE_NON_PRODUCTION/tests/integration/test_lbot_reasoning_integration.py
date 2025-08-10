#!/usr/bin/env python3
"""
Integration test for LBot reasoning system with symbolic reasoning engine
Tests the integration of ΛBotAdvancedReasoningOrchestrator with SymbolicEngine
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from reasoning.LBot_reasoning_processed import (
    AdvancedReasoningRequest,
    AdvancedReasoningResult,
    ΛBotAdvancedReasoningOrchestrator,
)

# Import the modules under test
from reasoning.reasoning_engine import SymbolicEngine


class TestLBotReasoningIntegration:
    """Test LBot reasoning system integration with symbolic engine"""

    @pytest_asyncio.fixture
    async def symbolic_engine(self):
        """Create a SymbolicEngine instance for testing"""
        config = {
            "confidence_threshold": 0.7,
            "max_depth": 5,
            "reasoning_history_limit": 100,
        }
        engine = SymbolicEngine(config)
        yield engine

    @pytest_asyncio.fixture
    async def lbot_orchestrator(self):
        """Create a LBot orchestrator instance for testing"""
        config = {"test_mode": True}
        orchestrator = ΛBotAdvancedReasoningOrchestrator(config)
        yield orchestrator

    @pytest.mark.asyncio
    async def test_lbot_orchestrator_initialization(self, symbolic_engine):
        """Test that LBot orchestrator is properly initialized in symbolic engine"""
        # Check that the orchestrator is initialized
        assert hasattr(symbolic_engine, "lbot_orchestrator")

        # Check component status
        status = symbolic_engine.get_component_status()
        assert "lbot_orchestrator" in status
        assert "advanced_reasoning" in status
        assert "quantum_bio_symbolic" in status

        # If orchestrator is available, it should be enabled
        if symbolic_engine.lbot_orchestrator:
            assert status["lbot_orchestrator"] == "available"
            assert status["advanced_reasoning"] == "enabled"
            assert status["quantum_bio_symbolic"] is True
            assert "lbot_orchestrator" in status["advanced_components"]

    @pytest.mark.asyncio
    async def test_advanced_pr_analysis_interface(self, symbolic_engine):
        """Test the advanced pull request analysis interface"""
        # Check that the method exists
        assert hasattr(symbolic_engine, "analyze_pull_request_advanced")

        # Test with mock data
        repository = "test/repo"
        pr_number = 123
        diff_content = "test diff content"
        files_changed = ["file1.py", "file2.py"]

        # Call the method
        result = await symbolic_engine.analyze_pull_request_advanced(
            repository, pr_number, diff_content, files_changed
        )

        # Check that result is properly formatted
        assert isinstance(result, dict)
        assert "reasoning_timestamp_utc" in result

        # If orchestrator is available, should have advanced result
        if symbolic_engine.lbot_orchestrator:
            assert "advanced_result" in result
            assert "reasoning_type" in result
            assert result["reasoning_type"] == "lbot_quantum_bio_symbolic"
            assert result["orchestrator_available"] is True
        else:
            # Should have fallback error message
            assert "error" in result
            assert "fallback_available" in result

    @pytest.mark.asyncio
    async def test_symbolic_engine_lbot_integration(self, symbolic_engine):
        """Test that symbolic engine properly integrates with LBot orchestrator"""
        # Test basic reasoning with LBot integration
        input_data = {
            "text": "Analyze this pull request for security vulnerabilities",
            "context": {
                "repository": "test/repo",
                "pr_number": 456,
                "files_changed": ["security.py", "auth.py"],
            },
        }

        # Test basic reasoning (should work regardless of LBot availability)
        basic_result = symbolic_engine.reason(input_data)
        assert isinstance(basic_result, dict)
        assert "reasoning_timestamp_utc" in basic_result

        # Check if LBot integration is working
        status = symbolic_engine.get_component_status()
        if status["lbot_orchestrator"] == "available":
            # Test advanced analysis
            advanced_result = await symbolic_engine.analyze_pull_request_advanced(
                "test/repo", 456, "diff content", ["security.py", "auth.py"]
            )
            assert "advanced_result" in advanced_result

    @pytest.mark.asyncio
    async def test_error_handling_without_lbot(self):
        """Test error handling when LBot orchestrator is not available"""
        # Create engine without LBot integration
        with patch("reasoning.reasoning_engine.SymbolicEngine.__init__") as mock_init:
            # Mock the initialization to simulate missing LBot
            def mock_init_func(self, config=None):
                self.config = config or {}
                self.lbot_orchestrator = None
                self.logger = MagicMock()
                self.metrics = {}

            mock_init.side_effect = mock_init_func
            engine = SymbolicEngine()

            # Test that advanced analysis gracefully handles missing orchestrator
            result = await engine.analyze_pull_request_advanced("test/repo", 123)
            assert "error" in result
            assert "fallback_available" in result
            assert result["fallback_available"] is True

    @pytest.mark.asyncio
    async def test_component_status_reporting(self, symbolic_engine):
        """Test that component status is properly reported"""
        status = symbolic_engine.get_component_status()

        # Check required status fields
        required_fields = [
            "symbolic_engine",
            "lbot_orchestrator",
            "advanced_reasoning",
            "quantum_bio_symbolic",
            "reasoning_components",
            "advanced_components",
            "metrics",
            "initialization_timestamp",
        ]

        for field in required_fields:
            assert field in status

        # Check that basic components are always present
        assert "reasoning_graph" in status["reasoning_components"]
        assert "reasoning_history" in status["reasoning_components"]
        assert "symbolic_rules" in status["reasoning_components"]
        assert "logic_operators" in status["reasoning_components"]

        # Symbolic engine should always be active
        assert status["symbolic_engine"] == "active"

    @pytest.mark.asyncio
    async def test_lbot_orchestrator_direct_usage(self, lbot_orchestrator):
        """Test LBot orchestrator directly"""
        if not lbot_orchestrator:
            pytest.skip("LBot orchestrator not available")

        # Test that orchestrator can be created
        assert lbot_orchestrator is not None

        # Test advanced PR analysis method exists
        assert hasattr(lbot_orchestrator, "analyze_pull_request_advanced")

        # Test calling the method (may fail due to missing dependencies, but should not crash)
        try:
            result = await lbot_orchestrator.analyze_pull_request_advanced(
                "test/repo", 789, "test diff", ["test.py"]
            )
            # If it succeeds, check the result format
            assert isinstance(result, (dict, AdvancedReasoningResult))
        except Exception as e:
            # Expected in test environment - dependencies may be missing
            assert "not available" in str(e).lower() or "mock" in str(e).lower()

    @pytest.mark.asyncio
    async def test_integration_error_recovery(self, symbolic_engine):
        """Test that integration gracefully handles errors"""
        # Test with invalid repository data
        result = await symbolic_engine.analyze_pull_request_advanced("", -1, None, None)

        # Should return a result, not crash
        assert isinstance(result, dict)
        assert "reasoning_timestamp_utc" in result

        # Should either have advanced result or error message
        has_result = "advanced_result" in result
        has_error = "error" in result
        assert has_result or has_error

    @pytest.mark.asyncio
    async def test_advanced_reasoning_request_format(self):
        """Test that advanced reasoning request format is correct"""
        request = AdvancedReasoningRequest(
            request_id="test-123",
            request_type="pr_analysis",
            input_data={"repository": "test/repo"},
            context={"user": "test_user"},
            priority="high",
            created_at="2025-01-31T00:00:00Z",
        )

        # Check that request has required fields
        assert request.request_id == "test-123"
        assert request.request_type == "pr_analysis"
        assert request.priority == "high"
        assert isinstance(request.input_data, dict)
        assert isinstance(request.context, dict)
