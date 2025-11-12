import pytest
from products.communication.abas.bio_adaptation_engine import (
    AdaptationRecommendation,
    BioAdaptationEngine,
    BiometricProfile,
    BiometricType,
)


@pytest.fixture
def engine():
    return BioAdaptationEngine()

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_normal(engine):
    biometric_data = {
        "user_id": "test_user",
        "heart_rate": 75,
        "stress_level": 0.3,
        "arousal": 0.6,
        "attention": 0.8,
        "temperature": 37.0,
        "sleep_quality": 0.85,
    }
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["user_id"] == "test_user"
    assert not analysis["adaptation_needed"]
    assert analysis["patterns"]["heart_rate"]["status"] == "normal"
    assert analysis["patterns"]["stress"]["status"] == "optimal"
    assert analysis["patterns"]["attention"]["status"] == "high"
    assert analysis["patterns"]["sleep"]["status"] == "excellent"

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_elevated_heart_rate(engine):
    biometric_data = {"heart_rate": 100}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["heart_rate"]["status"] == "elevated"
    assert analysis["adaptation_needed"]

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_low_heart_rate(engine):
    biometric_data = {"heart_rate": 40}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["heart_rate"]["status"] == "low"
    assert analysis["adaptation_needed"]

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_high_stress(engine):
    biometric_data = {"stress_level": 0.8}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["stress"]["status"] == "high"
    assert analysis["adaptation_needed"]

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_low_stress(engine):
    biometric_data = {"stress_level": 0.1}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["stress"]["status"] == "low"

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_low_attention(engine):
    biometric_data = {"attention": 0.4}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["attention"]["status"] == "low"
    assert analysis["adaptation_needed"]

@pytest.mark.asyncio
async def test_analyze_biometric_patterns_poor_sleep(engine):
    biometric_data = {"sleep_quality": 0.5}
    analysis = await engine.analyze_biometric_patterns(biometric_data)
    assert analysis["patterns"]["sleep"]["status"] == "poor"
    assert analysis["adaptation_needed"]

@pytest.mark.asyncio
async def test_adapt_dream_parameters_high_stress(engine):
    biometric_data = {"stress_level": 0.8}
    dream_params = {"intensity": 0.8, "duration": 60, "type": "free"}
    adapted_params = await engine.adapt_dream_parameters(biometric_data, dream_params)
    assert adapted_params["intensity"] < dream_params["intensity"]
    assert adapted_params["type"] == "guided"
    assert "adaptation_info" in adapted_params

@pytest.mark.asyncio
async def test_adapt_dream_parameters_low_stress(engine):
    biometric_data = {"stress_level": 0.2}
    dream_params = {"intensity": 0.5, "duration": 30, "type": "free"}
    adapted_params = await engine.adapt_dream_parameters(biometric_data, dream_params)
    assert adapted_params["intensity"] > dream_params["intensity"]

@pytest.mark.asyncio
async def test_adapt_dream_parameters_poor_attention_and_sleep(engine):
    biometric_data = {"attention": 0.4, "sleep_quality": 0.5}
    dream_params = {"intensity": 0.5, "duration": 60, "type": "free"}
    adapted_params = await engine.adapt_dream_parameters(biometric_data, dream_params)
    assert adapted_params["duration"] < dream_params["duration"]

@pytest.mark.asyncio
async def test_adapt_dream_parameters_good_attention_and_sleep(engine):
    biometric_data = {"attention": 0.9, "sleep_quality": 0.9}
    dream_params = {"intensity": 0.5, "duration": 30, "type": "free"}
    adapted_params = await engine.adapt_dream_parameters(biometric_data, dream_params)
    assert adapted_params["duration"] > dream_params["duration"]

@pytest.mark.asyncio
async def test_generate_bio_feedback_elevated_heart_rate(engine):
    biometric_data = {"heart_rate": 110}
    recommendations = await engine.generate_bio_feedback(biometric_data)
    assert len(recommendations) > 0
    assert any(r.recommendation_type == "heart_rate_reduction" for r in recommendations)

@pytest.mark.asyncio
async def test_generate_bio_feedback_high_stress(engine):
    biometric_data = {"stress_level": 0.9}
    recommendations = await engine.generate_bio_feedback(biometric_data)
    assert len(recommendations) > 0
    assert any(r.recommendation_type == "stress_reduction" for r in recommendations)

@pytest.mark.asyncio
async def test_generate_bio_feedback_low_attention(engine):
    biometric_data = {"attention": 0.3}
    recommendations = await engine.generate_bio_feedback(biometric_data)
    assert len(recommendations) > 0
    assert any(r.recommendation_type == "focus_enhancement" for r in recommendations)

@pytest.mark.asyncio
async def test_generate_bio_feedback_poor_sleep(engine):
    biometric_data = {"sleep_quality": 0.4}
    recommendations = await engine.generate_bio_feedback(biometric_data)
    assert len(recommendations) > 0
    assert any(r.recommendation_type == "sleep_optimization" for r in recommendations)

@pytest.mark.asyncio
async def test_update_bio_profile_new_user(engine):
    user_id = "new_user"
    biometric_data = {"heart_rate": 80, "stress_level": 0.4}
    summary = await engine.update_bio_profile(user_id, biometric_data)
    assert summary["user_id"] == user_id
    assert summary["profile_updated"]
    assert user_id in engine.user_profiles
    assert engine.user_profiles[user_id].baseline_heart_rate == 80

@pytest.mark.asyncio
async def test_update_bio_profile_existing_user(engine):
    user_id = "existing_user"
    initial_data = {"heart_rate": 70, "stress_level": 0.3}
    await engine.update_bio_profile(user_id, initial_data)

    updated_data = {"heart_rate": 90, "stress_level": 0.5}
    summary = await engine.update_bio_profile(user_id, updated_data)

    assert summary["user_id"] == user_id
    assert summary["profile_updated"]
    profile = engine.user_profiles[user_id]
    assert 70 < profile.baseline_heart_rate < 90
    assert 1 - 0.5 < profile.stress_tolerance < 1 - 0.3
