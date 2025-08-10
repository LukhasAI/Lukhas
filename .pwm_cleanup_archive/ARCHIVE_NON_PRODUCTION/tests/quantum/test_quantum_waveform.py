import unittest

from quantum.quantum_waveform import QuantumWaveform


class TestQuantumWaveform(unittest.TestCase):
    def test_collapse_triggers_dream(self):
        wf = QuantumWaveform(base_seed="test")
        dream = wf.collapse(probability=1.0)
        self.assertIsNotNone(dream)
        self.assertIn("dream_id", dream)

    def test_recursive_collapse(self):
        wf = QuantumWaveform(base_seed="seed")
        dream = wf.collapse(probability=1.0, recursion_limit=2)
        self.assertIn("recursive_child", dream)


if __name__ == "__main__":
    unittest.main()
