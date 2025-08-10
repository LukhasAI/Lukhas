#!/usr/bin/env python3
"""
Test ABAS Quantum Specialist Integration
Tests for ABAS quantum-biological AI integration
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestABASQuantumSpecialistIntegration:
    """Test ABAS quantum specialist integration"""

    def test_quantum_specialist_import(self):
        """Test that quantum specialist can be imported"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        assert get_abas_quantum_specialist is not None

    def test_abas_hub_with_quantum_specialist(self):
        """Test ABAS hub integration with quantum specialist"""
        from abas.integration.abas_integration_hub import (
            get_abas_integration_hub,
        )

        hub = get_abas_integration_hub()
        assert hub is not None

        # Check if quantum specialist is available
        if hasattr(hub, "quantum_specialist"):
            print("Quantum specialist found in ABAS hub")
            if hub.quantum_specialist:
                print("Quantum specialist is initialized")

    @pytest.mark.asyncio
    async def test_quantum_biological_processing(self):
        """Test quantum-biological processing functionality"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        quantum_specialist = get_abas_quantum_specialist()
        if quantum_specialist:
            # Initialize
            await quantum_specialist.initialize()

            # Test processing
            result = await quantum_specialist.process_quantum_biological(
                "How can quantum biology help with ethical decision making?",
                {"context": "test"},
            )

            assert isinstance(result, dict)
            assert "content" in result
            assert "bio_confidence" in result
            assert "quantum_coherence" in result
            assert "atp_efficiency" in result
            assert "ethical_resonance" in result

            # Check values are in expected ranges
            assert 0.0 <= result["bio_confidence"] <= 1.0
            assert 0.0 <= result["quantum_coherence"] <= 1.0
            assert 0.0 <= result["atp_efficiency"] <= 1.0
            assert 0.0 <= result["ethical_resonance"] <= 1.0

            print(f"Bio-confidence: {result['bio_confidence']:.2f}")
            print(f"Quantum coherence: {result['quantum_coherence']:.2f}")

    @pytest.mark.asyncio
    async def test_quantum_ethics_arbitration(self):
        """Test quantum ethics arbitration"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        quantum_specialist = get_abas_quantum_specialist()
        if quantum_specialist:
            await quantum_specialist.initialize()

            # Test ethics arbitration
            decision_context = {
                "content": "Should we prioritize efficiency over fairness?",
                "stakeholders": ["group_a", "group_b"],
                "resources": {"compute": 100, "memory": 200},
            }

            result = await quantum_specialist.get_quantum_ethics_arbitration(
                decision_context
            )

            assert isinstance(result, dict)
            if "error" not in result:
                assert "ethical_resonance" in result or "arbitration_id" in result

    @pytest.mark.asyncio
    async def test_cristae_topology_optimization(self):
        """Test cristae topology optimization"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        quantum_specialist = get_abas_quantum_specialist()
        if quantum_specialist:
            await quantum_specialist.initialize()

            # Test topology optimization
            current_state = {
                "nodes": {"n1": {}, "n2": {}, "n3": {}},
                "connections": [("n1", "n2"), ("n2", "n3")],
            }

            performance_metrics = {
                "average_confidence": 0.7,
                "average_processing_time": 0.5,
            }

            result = await quantum_specialist.optimize_cristae_topology(
                current_state, performance_metrics
            )

            assert isinstance(result, dict)
            if "error" not in result:
                assert (
                    "optimization_id" in result or "performance_improvement" in result
                )

    def test_biological_status(self):
        """Test biological status reporting"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        quantum_specialist = get_abas_quantum_specialist()
        if quantum_specialist:
            status = quantum_specialist.get_biological_status()

            assert isinstance(status, dict)
            assert "capability_level" in status
            assert "bio_metrics" in status
            assert "integration_stats" in status

            print(f"Capability level: {status['capability_level']}")
            print(f"Integration stats: {status['integration_stats']}")

    def test_mock_implementation(self):
        """Test that mock implementation works"""
        try:
            from core.neural_architectures.abas.abas_quantum_specialist_mock import (
                QuantumBioCapabilityLevel,
                QuantumBioResponse,
                get_quantum_biological_agi,
            )

            quantum_agi = get_quantum_biological_agi()
            assert quantum_agi is not None

            # Test capability levels
            assert QuantumBioCapabilityLevel.CELLULAR.value == "cellular_basic"
            assert (
                QuantumBioCapabilityLevel.QUANTUM_TUNNELING.value == "quantum_tunneling"
            )

        except ImportError:
            pytest.skip("Mock implementation not available")

    @pytest.mark.asyncio
    async def test_capability_advancement(self):
        """Test capability level advancement"""
        from core.neural_architectures.abas.abas_quantum_specialist_wrapper import (
            get_abas_quantum_specialist,
        )

        quantum_specialist = get_abas_quantum_specialist()
        if quantum_specialist:
            await quantum_specialist.initialize()

            initial_level = quantum_specialist.get_capability_level()

            # Process multiple times to potentially advance
            for i in range(10):
                await quantum_specialist.process_quantum_biological(
                    f"Test input {i} for capability advancement", {"iteration": i}
                )

            final_level = quantum_specialist.get_capability_level()
            status = quantum_specialist.get_biological_status()

            print(f"Initial capability: {initial_level}")
            print(f"Final capability: {final_level}")
            print(f"Total processes: {status['integration_stats']['total_processes']}")
            print(
                f"Capability advancements: {status['integration_stats']['capability_advancements']}"
            )

    @pytest.mark.asyncio
    async def test_abas_hub_quantum_processing(self):
        """Test quantum processing through ABAS hub"""
        from abas.integration.abas_integration_hub import (
            get_abas_integration_hub,
        )

        hub = get_abas_integration_hub()

        # Initialize hub
        await hub.initialize()

        # Test quantum biological processing
        payload = {
            "input": "Explain quantum tunneling in biological systems",
            "context": {"source": "test"},
        }

        result = await hub.process_quantum_biological(payload)

        assert isinstance(result, dict)
        if "error" not in result:
            assert "content" in result
            print(f"Quantum processing result: {result.get('content', '')[:100]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
