"""
Integration tests for the LUKHAS Bio-Symbolic Architecture and its integration
with the consciousness system.
"""

from unittest.mock import patch

import pytest
from bio.core.architecture_analyzer import (
    Architecture,
    BioSymbolicArchitectureAnalyzer,
    SymbolicData,
)
from bio.core.bio_symbolic import BioSymbolic, BioSymbolicOrchestrator, SymbolicGlyph


@pytest.mark.bio_architecture
class TestBioSymbolicArchitecture:
    """
    Tests for the bio-symbolic architecture analysis, processing, and integration.
    """

    def test_architecture_analyzer_stubs(self):
        """
        Test that the BioSymbolicArchitectureAnalyzer can be instantiated and its
        stub methods can be called without errors.
        """
        analyzer = BioSymbolicArchitectureAnalyzer()

        # Test analyze_hierarchy_depth
        analysis_result = analyzer.analyze_hierarchy_depth("some/bio/path")
        assert analysis_result.depth == 0
        assert analysis_result.complexity == 0.0

        # Test design_integration_pathway
        arch1 = Architecture(name="arch1", components={})
        arch2 = Architecture(name="arch2", components={})
        pathway_result = analyzer.design_integration_pathway(arch1, arch2)
        assert not pathway_result.steps
        assert pathway_result.estimated_effort == 0.0

        # Test validate_symbolic_processing
        s_data = SymbolicData(glyph="test", payload={})
        validation_result = analyzer.validate_symbolic_processing(s_data)
        assert validation_result.is_valid

    def test_refactored_bio_symbolic_processing(self):
        """
        Test the refactored BioSymbolic class to ensure it correctly dispatches
        to the appropriate processor.
        """
        bio_symbolic = BioSymbolic()

        # Test rhythm processing
        rhythm_data = {"type": "rhythm", "frequency": 5.0, "timestamp": "now"}
        rhythm_result = bio_symbolic.process(rhythm_data)
        assert rhythm_result["glyph"] == SymbolicGlyph.VITAL.value

        # Test energy processing
        energy_data = {"type": "energy", "level": 0.1, "timestamp": "now"}
        energy_result = bio_symbolic.process(energy_data)
        assert energy_result["glyph"] == SymbolicGlyph.POWER_CRITICAL.value

        # Test unknown processing
        unknown_data = {"type": "unknown_type", "timestamp": "now"}
        unknown_result = bio_symbolic.process(unknown_data)
        assert unknown_result["type"] == "generic"

    def test_bio_symbolic_orchestrator_pipeline(self):
        """
        Test the BioSymbolicOrchestrator pipeline, including the call to the
        bio-feedback loop.
        """
        orchestrator = BioSymbolicOrchestrator()

        inputs = [
            {"type": "rhythm", "frequency": 0.05, "timestamp": "now"},  # CIRCADIAN
            {"type": "energy", "level": 0.9, "timestamp": "now"},  # POWER_ABUNDANT
            {"type": "stress", "response": "flow", "timestamp": "now"},  # STRESS_FLOW
            {"type": "energy", "level": 0.6, "timestamp": "now"},  # POWER_BALANCED
        ]

        with patch("bio.core.bio_symbolic.bio_feedback_loop") as mock_feedback_loop:
            result = orchestrator.orchestrate(inputs)

            # Check orchestration results
            assert len(result["results"]) == 4
            assert result["overall_coherence"] > 0

            # Since POWER_ABUNDANT, POWER_BALANCED, and STRESS_FLOW all map to
            # energetic states, and CIRCADIAN to restorative, the dominant glyph
            # should be one of the energetic ones. We can check that a glyph was found.
            assert result["dominant_glyph"] is not None

            # Check that the feedback loop was called
            mock_feedback_loop.assert_called_once()
            # Check that it was called with the orchestration result
            mock_feedback_loop.assert_called_with(result)

    def test_bio_consciousness_coupling(self):
        """
        A simple test to ensure the bio-consciousness mapping is accessible and correct.
        This is implicitly tested in the orchestrator test, but an explicit check is good.
        """
        from consciousness.bio_integration import BIO_CONSCIOUSNESS_MAP, BioAwareConsciousnessState

        # Check a few mappings
        assert BIO_CONSCIOUSNESS_MAP[SymbolicGlyph.POWER_CRITICAL] == BioAwareConsciousnessState.STRESSED_ADAPTATION
        assert BIO_CONSCIOUSNESS_MAP[SymbolicGlyph.DREAM_EXPLORE] == BioAwareConsciousnessState.CREATIVE_EXPLORATION
        assert BIO_CONSCIOUSNESS_MAP[SymbolicGlyph.CIRCADIAN] == BioAwareConsciousnessState.RESTORATIVE_INTEGRATION
