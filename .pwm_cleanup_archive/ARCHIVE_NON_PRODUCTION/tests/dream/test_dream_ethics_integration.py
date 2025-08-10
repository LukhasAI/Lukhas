import unittest

from dream.dream_generator import generate_dream


class TestDreamEthicsIntegration(unittest.TestCase):
    def test_risk_and_alignment_tags_present(self):
        def stub_eval(dream):
            return {"status": "ok"}

        dream = generate_dream(stub_eval)
        self.assertIn("risk_tag", dream)
        self.assertIn("alignment_tag", dream)
        if dream["emotional_intensity"] > 0.7:
            self.assertIn("ethics", dream)


if __name__ == "__main__":
    unittest.main()
