# owner: Jules-07
# tier: tier4
# module_uid: candidate.bio.energy.spirulina_atp_system
# criticality: P2

from unittest.mock import AsyncMock, patch

import pytest

from lukhas.bio.energy.spirulina_atp_system import (
    SpirulinaATPHybridSystem,
    create_spirulina_atp_system,
)


@pytest.mark.tier4
@pytest.mark.bio
class TestSpirulinaATPSystem:
    """Test suite for the SpirulinaATPHybridSystem."""

    def test_create_system_factory(self):
        """Test the factory function for creating the system."""
        system = create_spirulina_atp_system(scale=2.0, optimize_for_consciousness=True)
        assert isinstance(system, SpirulinaATPHybridSystem)
        assert system.system_scale == 2.0

    @pytest.mark.asyncio
    async def test_system_initialization(self):
        """Test the initialization of the SpirulinaATPHybridSystem."""
        system = SpirulinaATPHybridSystem(system_scale=1.0)
        assert system.system_scale == 1.0
        assert system.target_tflops_per_watt == 24.1
        status = await system.get_system_status()
        assert status is not None

    @patch("labs.bio.energy.spirulina_atp_system.SpirulinaPhotosynthethicEngine")
    @patch("labs.bio.energy.spirulina_atp_system.ATPSynthesisEngine")
    @patch("labs.bio.energy.spirulina_atp_system.BiohybridCapacitorArray")
    @pytest.mark.asyncio
    async def test_process_energy_cycle(self, mock_capacitor_array_cls, mock_atp_engine_cls, mock_spirulina_engine_cls):
        """Test the main energy processing cycle with mocked subsystems."""
        # Arrange
        mock_spirulina_instance = AsyncMock()
        mock_spirulina_instance.harvest_quantum_energy.return_value = 10.0
        mock_spirulina_instance.distribution_efficiency = 0.63
        mock_spirulina_instance.thylakoid_quantum_efficiency = 0.87
        mock_spirulina_engine_cls.return_value = mock_spirulina_instance

        mock_atp_instance = AsyncMock()
        mock_atp_instance.synthesize_energy.return_value = 5.0
        mock_atp_instance.create_synergy_with_spirulina.return_value = 15.0
        mock_atp_engine_cls.return_value = mock_atp_instance

        mock_capacitor_instance = AsyncMock()
        mock_capacitor_instance.capacitors = []
        mock_capacitor_instance.store_energy.return_value = {
            "stored_energy_j": 20.0,
            "overflow_energy_j": 0.0,
            "total_stored_j": 20.0,
            "storage_efficiency": 1.0,
            "retention_rate": 0.98,
        }
        mock_capacitor_array_cls.return_value = mock_capacitor_instance

        system = SpirulinaATPHybridSystem(system_scale=1.0)

        # Act
        result = await system.process_energy_cycle(quantum_input=0.8, substrate_availability=0.9)

        # Assert
        mock_spirulina_instance.harvest_quantum_energy.assert_called_once()
        mock_atp_instance.synthesize_energy.assert_called_once()
        mock_atp_instance.create_synergy_with_spirulina.assert_called_once()
        mock_capacitor_instance.store_energy.assert_called_once()

        assert result is not None
        assert "energy_sources" in result
        assert "storage_performance" in result
        assert "system_metrics" in result
        assert result["efficiency_tflops_per_watt"] > 0

    @pytest.mark.asyncio
    async def test_get_system_status(self):
        """Test the get_system_status method."""
        system = SpirulinaATPHybridSystem(system_scale=0.5)
        status = await system.get_system_status()
        assert "system_performance" in status
        assert "energy_storage" in status
        assert "subsystem_status" in status
        assert status["energy_storage"]["total_capacity_j"] > 0

    def test_calculate_virtuoso_agi_alignment(self):
        """Test the Virtuoso AGI alignment calculation."""
        system = SpirulinaATPHybridSystem()
        system.current_metrics.tflops_per_watt = 20.0
        system.current_metrics.charge_retention_rate = 0.95
        system.current_metrics.thermal_efficiency = 0.6

        alignment = system.calculate_virtuoso_agi_alignment()
        assert 0 < alignment <= 0.94
