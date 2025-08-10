import random
import unittest

from bio.eeg_sync_bridge import (
    BrainwaveBand,
    ingest_mock_eeg,
    map_to_symbolic_state,
)


class TestEEGSyncBridge(unittest.TestCase):
    def test_ingest_mock_eeg(self):
        random.seed(1)
        samples = list(ingest_mock_eeg(num_samples=2))
        self.assertEqual(len(samples), 2)
        for sample in samples:
            for band in BrainwaveBand:
                self.assertIn(band.value, sample)

    def test_map_to_symbolic_state(self):
        signals = {
            "delta": 0.8,
            "theta": 0.1,
            "alpha": 0.2,
            "beta": 0.3,
            "gamma": 0.4,
        }
        result = map_to_symbolic_state(signals)
        self.assertEqual(result["state"], "deep_dream")
        self.assertEqual(result["dominant_band"], "delta")
        self.assertAlmostEqual(result["driftScore"], 0.26)
        self.assertAlmostEqual(result["affect_delta"], -0.19999999999999998)


if __name__ == "__main__":
    unittest.main()
