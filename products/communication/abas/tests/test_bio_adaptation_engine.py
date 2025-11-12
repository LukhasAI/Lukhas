"""
Unit tests for the Bio Adaptation Engine
"""
import asyncio
import unittest
from products.communication.abas.bio_adaptation_engine import (
    BioAdaptationEngine,
    BiometricType,
    AdaptationRecommendation,
)


class TestBioAdaptationEngine(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = BioAdaptationEngine()
        self.test_user_id = "test_user"
        self.normal_biometrics = {
            "user_id": self.test_user_id,
            "heart_rate": 70,
            "stress_level": 0.4,
            "arousal": 0.6,
            "attention": 0.7,
            "temperature": 37.0,
            "sleep_quality": 0.7,
        }
        self.high_stress_biometrics = {
            "user_id": self.test_user_id,
            "heart_rate": 100,
            "stress_level": 0.8,
            "arousal": 0.9,
            "attention": 0.4,
            "temperature": 37.5,
            "sleep_quality": 0.5,
        }

    async def test_initialization(self):
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.user_profiles, {})

    async def test_analyze_biometric_patterns_normal(self):
        analysis = await self.engine.analyze_biometric_patterns(self.normal_biometrics)
        self.assertEqual(analysis["user_id"], self.test_user_id)
        self.assertFalse(analysis["adaptation_needed"])
        self.assertEqual(analysis["patterns"]["heart_rate"]["status"], "normal")
        self.assertEqual(analysis["patterns"]["stress"]["status"], "optimal")
        self.assertEqual(analysis["patterns"]["attention"]["status"], "medium")
        self.assertEqual(analysis["patterns"]["sleep"]["status"], "good")
        self.assertEqual(len(analysis["priority_areas"]), 0)

    async def test_analyze_biometric_patterns_high_stress(self):
        analysis = await self.engine.analyze_biometric_patterns(
            self.high_stress_biometrics
        )
        self.assertTrue(analysis["adaptation_needed"])
        self.assertEqual(analysis["patterns"]["heart_rate"]["status"], "elevated")
        self.assertEqual(analysis["patterns"]["stress"]["status"], "high")
        self.assertEqual(analysis["patterns"]["attention"]["status"], "low")
        self.assertEqual(analysis["patterns"]["sleep"]["status"], "poor")
        self.assertEqual(
            set(analysis["priority_areas"]),
            {"heart_rate", "stress", "attention", "sleep"},
        )

    async def test_adapt_dream_parameters_high_stress(self):
        original_params = {"intensity": 0.8, "duration": 60, "type": "free"}
        adapted_params = await self.engine.adapt_dream_parameters(
            self.high_stress_biometrics, original_params
        )
        self.assertLess(adapted_params["intensity"], original_params["intensity"])
        self.assertLess(adapted_params["duration"], original_params["duration"])
        self.assertEqual(adapted_params["type"], "guided")

    async def test_adapt_dream_parameters_optimal_state(self):
        optimal_biometrics = {
            "user_id": self.test_user_id,
            "heart_rate": 70,
            "stress_level": 0.2,
            "arousal": 0.6,
            "attention": 0.91,
            "temperature": 37.0,
            "sleep_quality": 0.9,
        }
        original_params = {"intensity": 0.5, "duration": 30, "type": "free"}
        adapted_params = await self.engine.adapt_dream_parameters(
            optimal_biometrics, original_params
        )
        self.assertGreater(adapted_params["intensity"], original_params["intensity"])
        self.assertGreater(adapted_params["duration"], original_params["duration"])
        self.assertEqual(adapted_params["type"], "lucid")

    async def test_generate_bio_feedback_high_stress(self):
        recommendations = await self.engine.generate_bio_feedback(
            self.high_stress_biometrics
        )
        self.assertEqual(len(recommendations), 4)
        types = [r.recommendation_type for r in recommendations]
        self.assertIn("heart_rate_reduction", types)
        self.assertIn("stress_reduction", types)
        self.assertIn("focus_enhancement", types)
        self.assertIn("sleep_optimization", types)

    async def test_generate_bio_feedback_normal(self):
        recommendations = await self.engine.generate_bio_feedback(
            self.normal_biometrics
        )
        self.assertEqual(len(recommendations), 0)

    async def test_update_bio_profile_create_new(self):
        summary = await self.engine.update_bio_profile(
            self.test_user_id, self.normal_biometrics
        )
        self.assertIn(self.test_user_id, self.engine.user_profiles)
        self.assertTrue(summary["profile_updated"])
        self.assertEqual(summary["profile_age_days"], 0)
        profile = self.engine.user_profiles[self.test_user_id]
        self.assertEqual(profile.baseline_heart_rate, self.normal_biometrics["heart_rate"])

    async def test_update_bio_profile_update_existing(self):
        # Create initial profile
        await self.engine.update_bio_profile(
            self.test_user_id, self.normal_biometrics
        )
        profile = self.engine.user_profiles[self.test_user_id]
        self.assertEqual(profile.baseline_heart_rate, self.normal_biometrics["heart_rate"])

        # Update with new data
        updated_biometrics = self.normal_biometrics.copy()
        updated_biometrics["heart_rate"] = 85
        await self.engine.update_bio_profile(self.test_user_id, updated_biometrics)

        # Check if the baseline has moved slightly towards the new value (EMA)
        self.assertGreater(profile.baseline_heart_rate, self.normal_biometrics["heart_rate"])
        self.assertLess(profile.baseline_heart_rate, 85)
        expected_hr = (
            0.1 * updated_biometrics["heart_rate"]
            + 0.9 * self.normal_biometrics["heart_rate"]
        )
        self.assertAlmostEqual(profile.baseline_heart_rate, expected_hr)


if __name__ == "__main__":
    unittest.main()
