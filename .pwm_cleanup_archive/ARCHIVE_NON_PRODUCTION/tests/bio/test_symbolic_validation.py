import unittest

from core.bio_systems.curiosity_spark import CuriositySpark
from core.bio_systems.resilience_boost import ResilienceBoost
from core.bio_systems.stability_anchor import StabilityAnchor
from core.bio_systems.stress_signal import StressSignal
from core.bio_systems.trust_binder import TrustBinder


class TestSymbolicValidation(unittest.TestCase):

    def test_trust_binder(self):
        """
        Tests that the TrustBinder is working correctly.
        """
        trust_binder = TrustBinder()
        affect_deltas = trust_binder.process_affect({"calm": 0.8})
        self.assertAlmostEqual(affect_deltas["stability"], 0.08)

    def test_curiosity_spark(self):
        """
        Tests that the CuriositySpark is working correctly.
        """
        curiosity_spark = CuriositySpark()
        self.assertEqual(curiosity_spark.level, 0.5)

    def test_stress_signal(self):
        """
        Tests that the StressSignal is working correctly.
        """
        stress_signal = StressSignal()
        self.assertEqual(stress_signal.level, 0.5)

    def test_stability_anchor(self):
        """
        Tests that the StabilityAnchor is working correctly.
        """
        stability_anchor = StabilityAnchor()
        self.assertEqual(stability_anchor.level, 0.5)

    def test_resilience_boost(self):
        """
        Tests that the ResilienceBoost is working correctly.
        """
        resilience_boost = ResilienceBoost()
        self.assertEqual(resilience_boost.level, 0.5)


if __name__ == "__main__":
    unittest.main()
