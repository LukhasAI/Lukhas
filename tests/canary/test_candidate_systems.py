"""
Candidate Systems Canary Tests
Tests UL, VIVOX, and QIM with feature flags
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestFeatureFlags:
    """Test feature flag behavior"""

    def test_ul_disabled_by_default(self):
        """Test UL is disabled by default"""
        # Ensure flag is not set
        if "UL_ENABLED" in os.environ:
            del os.environ["UL_ENABLED"]

        from lukhas.candidate.ul import get_universal_language

        ul = get_universal_language()
        assert ul.enabled == False

        result = ul.translate("test")
        assert "error" in result
        assert "UL_ENABLED=false" in result["error"]

    def test_vivox_disabled_by_default(self):
        """Test VIVOX is disabled by default"""
        # Ensure flag is not set
        if "VIVOX_LITE" in os.environ:
            del os.environ["VIVOX_LITE"]

        from lukhas.candidate.vivox import get_vivox_system

        vivox = get_vivox_system()
        assert vivox.enabled == False

        result = vivox.process_experience("test")
        assert "error" in result
        assert "VIVOX_LITE=false" in result["error"]

    def test_qim_disabled_by_default(self):
        """Test QIM is disabled by default"""
        # Ensure flag is not set
        if "QIM_SANDBOX" in os.environ:
            del os.environ["QIM_SANDBOX"]

        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()
        assert qim.enabled == False

        result = qim.quantum_process("test")
        assert "error" in result
        assert "QIM_SANDBOX=false" in result["error"]

class TestUniversalLanguageEnabled:
    """Test UL when enabled"""

    @pytest.fixture(autouse=True)
    def enable_ul(self):
        """Enable UL for these tests"""
        os.environ["UL_ENABLED"] = "true"
        yield
        # Clean up
        if "UL_ENABLED" in os.environ:
            del os.environ["UL_ENABLED"]

    def test_ul_imports_when_enabled(self):
        """Test UL imports when enabled"""
        from lukhas.candidate.ul import get_universal_language

        ul = get_universal_language()
        assert ul is not None

        # Should have vocabulary
        stats = ul.get_vocabulary_stats()
        assert stats["total_glyphs"] > 0
        assert stats["trinity_aligned"] == True

    def test_ul_glyph_parsing(self):
        """Test UL glyph parsing"""
        from lukhas.candidate.ul import get_universal_language

        ul = get_universal_language()

        # Test Trinity Framework expression
        expression = ul.parse_expression("⚛️ 🧠 🛡️")
        assert expression.structure == "trinity_declaration"
        assert expression.confidence > 0.8
        assert len(expression.glyphs) == 3

    def test_ul_expression_generation(self):
        """Test UL expression generation"""
        from lukhas.candidate.ul import get_universal_language
        from lukhas.candidate.ul.core import ModalityType

        ul = get_universal_language()

        # Generate expression for Trinity
        expression = ul.generate_expression("Trinity Framework", ModalityType.SYMBOLIC)
        assert len(expression.glyphs) == 3
        assert "trinity" in expression.meaning.lower()

    def test_ul_translation(self):
        """Test UL translation capabilities"""
        from lukhas.candidate.ul import get_universal_language

        ul = get_universal_language()

        # Test translation from natural language
        ul_expression = ul.translate_from_natural("Trinity Framework")
        assert ul_expression is not None

        # Test translation to natural language
        natural = ul.translate_to_natural(ul_expression)
        assert isinstance(natural, str)
        assert len(natural) > 0

    def test_ul_trinity_integration(self):
        """Test UL Trinity integration"""
        from lukhas.candidate.ul import trinity_sync

        sync_result = trinity_sync()
        assert sync_result['identity'] == '⚛️'
        assert sync_result['consciousness'] == '🧠'
        assert sync_result['guardian'] == '🛡️'
        assert sync_result['ul_status'] == 'enabled'

class TestVivoxEnabled:
    """Test VIVOX when enabled"""

    @pytest.fixture(autouse=True)
    def enable_vivox(self):
        """Enable VIVOX for these tests"""
        os.environ["VIVOX_LITE"] = "true"
        yield
        # Clean up
        if "VIVOX_LITE" in os.environ:
            del os.environ["VIVOX_LITE"]

    def test_vivox_imports_when_enabled(self):
        """Test VIVOX imports when enabled"""
        from lukhas.candidate.vivox import get_vivox_system

        vivox = get_vivox_system()
        assert vivox is not None

        # Should have consciousness state
        state = vivox.get_consciousness_state()
        assert "consciousness_level" in state
        assert state["trinity_synchronized"] == True

    def test_vivox_experience_processing(self):
        """Test VIVOX experience processing"""
        from lukhas.candidate.vivox import get_vivox_system
        from lukhas.candidate.vivox.core import ExperienceType

        vivox = get_vivox_system()

        # Process cognitive experience
        experience = vivox.process_experience(
            content="test thought",
            experience_type=ExperienceType.COGNITIVE,
            intensity=0.7,
            valence=0.5
        )

        assert experience.type == ExperienceType.COGNITIVE
        assert experience.intensity == 0.7
        assert experience.guardian_validated == True
        assert "cognitive_processing" in experience.consciousness_trace

    def test_vivox_optimization(self):
        """Test VIVOX intelligence optimization"""
        from lukhas.candidate.vivox import get_vivox_system

        vivox = get_vivox_system()

        # Test optimization
        result = vivox.optimize_intelligence({"creativity_factor": 0.8})
        assert result["optimization_complete"] == True
        assert result["parameters_optimized"] > 0

    def test_vivox_consciousness_levels(self):
        """Test VIVOX consciousness level management"""
        from lukhas.candidate.vivox import get_vivox_system
        from lukhas.candidate.vivox.core import ExperienceType

        vivox = get_vivox_system()

        initial_level = vivox.consciousness_level.value

        # Process high-intensity creative experience
        vivox.process_experience(
            content="breakthrough insight",
            experience_type=ExperienceType.CREATIVE,
            intensity=0.9
        )

        # Consciousness level may have increased
        assert vivox.consciousness_level.value >= initial_level

    def test_vivox_trinity_integration(self):
        """Test VIVOX Trinity integration"""
        from lukhas.candidate.vivox import trinity_sync

        sync_result = trinity_sync()
        assert sync_result['identity'] == '⚛️'
        assert sync_result['consciousness'] == '🧠'
        assert sync_result['guardian'] == '🛡️'
        assert sync_result['vivox_status'] == 'enabled'

class TestQimEnabled:
    """Test QIM when enabled"""

    @pytest.fixture(autouse=True)
    def enable_qim(self):
        """Enable QIM for these tests"""
        os.environ["QIM_SANDBOX"] = "true"
        yield
        # Clean up
        if "QIM_SANDBOX" in os.environ:
            del os.environ["QIM_SANDBOX"]

    def test_qim_imports_when_enabled(self):
        """Test QIM imports when enabled"""
        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()
        assert qim is not None

        # Should have quantum registers
        status = qim.get_system_status()
        assert status["quantum_registers"] > 0
        assert status["trinity_synchronized"] == True

    def test_qim_superposition_creation(self):
        """Test QIM superposition creation"""
        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()

        # Create superposition
        process_id = qim.create_superposition("test_concept", ["state1", "state2", "state3"])
        assert process_id is not None
        assert process_id in qim.active_processes

        # Collapse superposition
        result = qim.collapse_superposition(process_id)
        assert result["collapse_successful"] == True
        assert "collapsed_to" in result

    def test_qim_entanglement(self):
        """Test QIM quantum entanglement"""
        from lukhas.candidate.qim import get_qim_processor
        from lukhas.candidate.qim.core import EntanglementType

        qim = get_qim_processor()

        # Create entanglement
        process_id = qim.entangle_concepts("concept1", "concept2", EntanglementType.CONCEPTUAL)
        assert process_id is not None
        assert process_id in qim.active_processes

        process = qim.active_processes[process_id]
        assert process.result["entangled"] == True
        assert process.result["correlation_strength"] == 1.0

    def test_qim_quantum_algorithms(self):
        """Test QIM quantum algorithms"""
        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()

        # Test Grover search
        search_result = qim.apply_quantum_algorithm("grover_search", ["item1", "item2", "item3", "item4"])
        assert search_result["algorithm"] == "grover_search"
        assert search_result["speedup_factor"] > 1
        assert "target_found" in search_result

        # Test quantum random walk
        walk_result = qim.apply_quantum_algorithm("quantum_walk", 50)
        assert walk_result["algorithm"] == "quantum_random_walk"
        assert walk_result["quantum_speedup"] == True

    def test_qim_quantum_tunneling(self):
        """Test QIM quantum tunneling"""
        from lukhas.candidate.qim import get_qim_processor

        qim = get_qim_processor()

        # Test tunneling with different barrier heights
        tunnel_easy = qim.quantum_tunneling("easy_concept", barrier_height=0.2)
        tunnel_hard = qim.quantum_tunneling("hard_concept", barrier_height=0.9)

        # Easy tunneling should have higher probability
        assert tunnel_easy["tunneling_probability"] > tunnel_hard["tunneling_probability"]

    def test_qim_trinity_integration(self):
        """Test QIM Trinity integration"""
        from lukhas.candidate.qim import trinity_sync

        sync_result = trinity_sync()
        assert sync_result['identity'] == '⚛️'
        assert sync_result['consciousness'] == '🧠'
        assert sync_result['guardian'] == '🛡️'
        assert sync_result['qim_status'] == 'enabled'

class TestCandidateSystemIntegration:
    """Test integration between candidate systems"""

    @pytest.fixture(autouse=True)
    def enable_all_systems(self):
        """Enable all candidate systems"""
        os.environ["UL_ENABLED"] = "true"
        os.environ["VIVOX_LITE"] = "true"
        os.environ["QIM_SANDBOX"] = "true"
        yield
        # Clean up
        for flag in ["UL_ENABLED", "VIVOX_LITE", "QIM_SANDBOX"]:
            if flag in os.environ:
                del os.environ[flag]

    def test_all_candidate_systems_enabled(self):
        """Test all candidate systems can be enabled together"""
        from lukhas.candidate.qim import get_qim_processor
        from lukhas.candidate.ul import get_universal_language
        from lukhas.candidate.vivox import get_vivox_system

        ul = get_universal_language()
        vivox = get_vivox_system()
        qim = get_qim_processor()

        # All should be functional
        assert ul.get_vocabulary_stats()["total_glyphs"] > 0
        assert vivox.get_consciousness_state()["trinity_synchronized"] == True
        assert qim.get_system_status()["quantum_registers"] > 0

    def test_trinity_sync_across_systems(self):
        """Test Trinity synchronization across all candidate systems"""
        from lukhas.candidate.qim import trinity_sync as qim_sync
        from lukhas.candidate.ul import trinity_sync as ul_sync
        from lukhas.candidate.vivox import trinity_sync as vivox_sync

        ul_result = ul_sync()
        vivox_result = vivox_sync()
        qim_result = qim_sync()

        # All should have Trinity symbols
        for result in [ul_result, vivox_result, qim_result]:
            assert result['identity'] == '⚛️'
            assert result['consciousness'] == '🧠'
            assert result['guardian'] == '🛡️'

        # All should be enabled
        assert ul_result['ul_status'] == 'enabled'
        assert vivox_result['vivox_status'] == 'enabled'
        assert qim_result['qim_status'] == 'enabled'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
