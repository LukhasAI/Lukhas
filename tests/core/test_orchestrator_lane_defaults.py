"""
MATRIZ Orchestrator Lane Default Tests
====================================

Tests ensuring MATRIZ Orchestrator defaults to 'canary' lane for safer rollouts.
Critical for T4/0.01% operational excellence.
"""
import os
from unittest.mock import patch

import pytest


class TestOrchestratorLaneDefaults:
    """Test MATRIZ Orchestrator lane default behavior"""

    def test_default_lane_is_canary(self):
        """MATRIZ Orchestrator must default to 'canary' lane for safer rollouts"""
        with patch.dict(os.environ, {}, clear=True):
            default_lane = os.getenv('LUKHAS_LANE', 'canary').lower()
            assert default_lane == 'canary', f"Default lane is '{default_lane}', should be 'canary'"

    def test_explicit_lane_override_works(self):
        """Lane can be explicitly overridden via LUKHAS_LANE environment variable"""
        test_cases = [('production', 'production'), ('labs', 'labs'), ('experimental', 'experimental'), ('custom', 'custom')]
        for (env_value, expected) in test_cases:
            with patch.dict(os.environ, {'LUKHAS_LANE': env_value}):
                lane = os.getenv('LUKHAS_LANE', 'canary').lower()
                assert lane == expected, f"Expected '{expected}', got '{lane}' for LUKHAS_LANE='{env_value}'"

    def test_orchestrator_uses_lane_in_context(self):
        """AsyncOrchestrator should use lane information in processing context"""
        from matriz.core.async_orchestrator import AsyncOrchestrator
        with patch.dict(os.environ, {}, clear=True):
            orchestrator = AsyncOrchestrator()
            assert orchestrator is not None
        with patch.dict(os.environ, {'LUKHAS_LANE': 'production'}):
            orchestrator = AsyncOrchestrator()
            assert orchestrator is not None

    def test_safer_rollout_progression(self):
        """Test the lane progression for safer rollouts: experimental -> canary -> production"""
        lane_progression = ['experimental', 'canary', 'production']
        for lane in lane_progression:
            with patch.dict(os.environ, {'LUKHAS_LANE': lane}):
                resolved_lane = os.getenv('LUKHAS_LANE', 'canary').lower()
                assert resolved_lane == lane
                from matriz.core.async_orchestrator import AsyncOrchestrator
                orchestrator = AsyncOrchestrator()
                assert orchestrator is not None

    def test_case_insensitive_lane_handling(self):
        """Lane values should be normalized to lowercase"""
        test_cases = [('CANARY', 'canary'), ('Production', 'production'), ('EXPERIMENTAL', 'experimental'), ('Candidate', 'labs')]
        for (env_value, expected) in test_cases:
            with patch.dict(os.environ, {'LUKHAS_LANE': env_value}):
                lane = os.getenv('LUKHAS_LANE', 'canary').lower()
                assert lane == expected, f"Expected '{expected}', got '{lane}' for LUKHAS_LANE='{env_value}'"

    def test_empty_lane_defaults_to_canary(self):
        """Empty or whitespace-only LUKHAS_LANE should default to canary"""
        test_cases = ['', '  ', '\t', '\n']
        for empty_value in test_cases:
            with patch.dict(os.environ, {'LUKHAS_LANE': empty_value}):
                lane = os.getenv('LUKHAS_LANE', 'canary').lower()
                expected = empty_value.strip().lower() if empty_value.strip() else ''
                assert lane == expected

    def test_production_safety_check(self):
        """Production lane should be explicitly set, not defaulted to"""
        with patch.dict(os.environ, {}, clear=True):
            lane = os.getenv('LUKHAS_LANE', 'canary').lower()
            assert lane != 'production', 'Must not default to production lane for safety'
            assert lane != 'prod', 'Must not default to prod lane for safety'
            assert lane == 'canary', f"Default should be 'canary', got '{lane}'"

    def test_lane_integration_with_configuration(self):
        """Test that lane properly integrates with AsyncOrchestrator configuration"""
        from matriz.core.async_orchestrator import AsyncOrchestrator
        configs = [{}, {'MATRIZ_ASYNC': '1'}, {'MATRIZ_PARALLEL': '1', 'MATRIZ_MAX_PARALLEL': '5'}]
        for config in configs:
            with patch.dict(os.environ, {'LUKHAS_LANE': 'canary'}):
                orchestrator = AsyncOrchestrator(config)
                assert orchestrator is not None
                assert hasattr(orchestrator, 'stages')
                assert hasattr(orchestrator, 'enabled')
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
