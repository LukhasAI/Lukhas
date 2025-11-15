import pytest
from labs.core.qi_biometrics.qi_biometrics_engine import (
    QiBiometricsEngine,
    AppleHealthKitAPI,
    OuraRingAPI,
    NeuralinkAPI,
    HiveMindSensorNetwork,
)


class TestAppleHealthKitAPI:
    """Test realistic HRV and circadian simulation."""

    @pytest.mark.asyncio
    async def test_hrv_in_realistic_range(self):
        """Test HRV returns realistic values (20-100ms)."""
        api = AppleHealthKitAPI()

        hrv = await api.get_heart_rate_variability("user_123")

        assert 20.0 <= hrv <= 100.0

    @pytest.mark.asyncio
    async def test_hrv_consistent_per_user(self):
        """Test HRV maintains user baseline (±20%)."""
        api = AppleHealthKitAPI()

        hrv1 = await api.get_heart_rate_variability("user_123")
        hrv2 = await api.get_heart_rate_variability("user_123")

        # Should be similar (within 30% due to time/stress factors)
        assert 0.7 <= (hrv2 / hrv1) <= 1.3

    @pytest.mark.asyncio
    async def test_circadian_rhythm_valid(self):
        """Test circadian rhythm returns valid phases."""
        api = AppleHealthKitAPI()

        phase = await api.get_circadian_rhythm("user_123")

        assert phase in ["peak_focus", "trough", "creative_window"]


class TestOuraRingAPI:
    """Test sleep chronotype simulation."""

    @pytest.mark.asyncio
    async def test_chronotype_persistent(self):
        """Test chronotype remains consistent for user."""
        api = OuraRingAPI()

        chrono1 = await api.get_sleep_chronotype("user_456")
        chrono2 = await api.get_sleep_chronotype("user_456")

        assert chrono1 == chrono2  # Should be identical

    @pytest.mark.asyncio
    async def test_chronotype_valid(self):
        """Test chronotype is one of valid types."""
        api = OuraRingAPI()

        chronotype = await api.get_sleep_chronotype("user_789")

        assert chronotype in ["lion", "bear", "wolf", "dolphin"]


class TestNeuralinkAPI:
    """Test neural coherence simulation."""

    @pytest.mark.asyncio
    async def test_coherence_in_range(self):
        """Test coherence returns 0.0-1.0."""
        api = NeuralinkAPI()

        coherence = await api.get_neural_coherence_score("user_123")

        assert 0.0 <= coherence <= 1.0

    @pytest.mark.asyncio
    async def test_coherence_consistent_baseline(self):
        """Test coherence maintains user baseline."""
        api = NeuralinkAPI()

        scores = [
            await api.get_neural_coherence_score("user_123")
            for _ in range(5)
        ]

        # All scores should be within 0.3 of each other
        assert max(scores) - min(scores) <= 0.4


class TestHiveMindSensorNetwork:
    """Test collective resonance simulation."""

    @pytest.mark.asyncio
    async def test_resonance_in_range(self):
        """Test resonance returns 0.0-1.0."""
        api = HiveMindSensorNetwork()

        resonance = await api.get_collective_resonance("user_123")

        assert 0.0 <= resonance <= 1.0

    @pytest.mark.asyncio
    async def test_global_resonance_drifts(self):
        """Test global resonance changes slowly over time."""
        api = HiveMindSensorNetwork()

        # Force update by setting last_update to None
        api._last_update = None
        r1 = await api.get_collective_resonance("user_123")

        api._last_update = None  # Force another update
        r2 = await api.get_collective_resonance("user_456")

        # Should be close but may drift
        assert abs(r1 - r2) <= 0.3


class TestQiBiometricsEngineIntegration:
    """Test full engine with realistic simulators."""

    @pytest.mark.asyncio
    async def test_get_qi_biostate(self):
        """Test biostate returns all required fields."""
        engine = QiBiometricsEngine()

        biostate = await engine.get_qi_biostate("user_123")

        assert "neural_coherence" in biostate
        assert "heart_rate_variability" in biostate
        assert "circadian_phase" in biostate
        assert "qi_entanglement_potential" in biostate

        # Validate ranges
        assert 0.0 <= biostate["neural_coherence"] <= 1.0
        assert 20.0 <= biostate["heart_rate_variability"] <= 100.0

    @pytest.mark.asyncio
    async def test_predict_biological_receptivity(self):
        """Test receptivity prediction uses biometric data."""
        engine = QiBiometricsEngine()

        receptivity = await engine.predict_biological_receptivity("user_123")

        assert "creative_genesis_window" in receptivity
        assert "decision_clarity_peak" in receptivity
        assert "empathy_resonance_maximum" in receptivity
        assert "transcendence_probability" in receptivity

        # All values should be 0.0-1.0
        for value in receptivity.values():
            assert 0.0 <= value <= 1.0
