import unittest

from identity.utils.entropy_helpers import EntropyCalculator


class TestEntropyHelpers(unittest.TestCase):
    def setUp(self):
        self.calc = EntropyCalculator()

    def test_pattern_entropy_simple(self):
        value = "ABABAB"
        ent = self.calc.pattern_entropy(value, pattern_length=2)
        self.assertGreater(ent, 0)

    def test_validate_randomness(self):
        data = "ABCDEFGH"
        result = self.calc.validate_randomness(data)
        self.assertIn("shannon_entropy", result)
        self.assertIn("pattern_entropy", result)
        self.assertIn("is_random", result)
