import unittest

from security import ModerationWrapper, SymbolicComplianceRules


class TestModerationWrapper(unittest.TestCase):
    def setUp(self):
        rules = SymbolicComplianceRules(banned_phrases=["attack"])
        self.wrapper = ModerationWrapper(rules)
        self.echo = lambda prompt: f"ECHO:{prompt}"

    def test_allows_compliant_prompt(self):
        prompt = "I am furious but will calm down soon"
        result = self.wrapper.respond(prompt, self.echo)
        self.assertEqual(result, f"ECHO:{prompt}")

    def test_blocks_noncompliant_prompt(self):
        prompt = "I am furious and want to attack"
        result = self.wrapper.respond(prompt, self.echo)
        self.assertIn("withheld", result)


if __name__ == "__main__":
    unittest.main()
