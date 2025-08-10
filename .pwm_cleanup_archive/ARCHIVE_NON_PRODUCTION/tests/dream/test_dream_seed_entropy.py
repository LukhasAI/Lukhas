import unittest

from dream.dream_seed import _seed_diversity_index, generate_semantic_dream

from quantum.quantum_flux import QuantumFlux


class TestDreamSeedEntropy(unittest.TestCase):
    def test_entropy_influences_index(self):
        flux1 = QuantumFlux(seed=1)
        flux2 = QuantumFlux(seed=2)
        idx1 = _seed_diversity_index(0.2, entropy_source=flux1)
        idx2 = _seed_diversity_index(0.2, entropy_source=flux2)
        self.assertNotEqual(idx1, idx2)

    def test_generate_semantic_dream_uses_entropy(self):
        flux_a = QuantumFlux(seed=1)
        flux_b = QuantumFlux(seed=2)
        trace = {"collapse_id": "t1", "resonance": 0.1}
        dream_a = generate_semantic_dream(trace, flux=flux_a)
        dream_b = generate_semantic_dream(trace, flux=flux_b)
        self.assertNotEqual(dream_a["text"], dream_b["text"])


if __name__ == "__main__":
    unittest.main()
