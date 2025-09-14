import unittest
from unittest.mock import Mock
from branding.personal_brand.consciousness_authority_builder import (
    ConsciousnessAuthorityBuilder,
    AuthorityScore,
    Strategy,
)

class TestConsciousnessAuthorityBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ConsciousnessAuthorityBuilder()
        # Mock the wrappers for unit testing
        self.builder.identity_wrapper = Mock()
        self.builder.consciousness_wrapper = Mock()

    def test_calculate_authority_score(self):
        profile_data = {
            "name": "Test User",
            "title": "Consciousness Researcher",
            "bio": "A bio.",
            "skills": ["python", "pytorch", "neuroscience"],
        }
        history = [
            {"tags": ["consciousness", "technical"]},
            {"tags": ["consciousness"]},
            {"tags": ["community"]},
            {"tags": ["innovation"]},
        ]

        score = self.builder.calculate_authority_score(profile_data, history)

        self.assertIsInstance(score, AuthorityScore)
        self.assertAlmostEqual(score.profile_completeness, 1.0)
        self.assertAlmostEqual(score.consciousness_depth, 0.2)
        self.assertAlmostEqual(score.technical_expertise, 0.35)
        self.assertAlmostEqual(score.community_engagement, 0.02)
        self.assertAlmostEqual(score.innovation_leadership, 0.2)

        expected_overall = (
            0.2 * 0.3 + 0.35 * 0.25 + 0.02 * 0.2 + 0.2 * 0.2 + 1.0 * 0.05
        )
        self.assertAlmostEqual(score.overall_score, expected_overall)

    def test_build_consciousness_narrative(self):
        score = AuthorityScore(
            overall_score=0.75,
            consciousness_depth=0.8,
            technical_expertise=0.7,
            community_engagement=0.6,
            innovation_leadership=0.9,
            profile_completeness=1.0,
        )
        narrative = self.builder.build_consciousness_narrative(score)
        self.assertIn("an emerging authority", narrative)
        self.assertIn("innovation leadership", narrative)

    def test_suggest_positioning_strategy(self):
        score = AuthorityScore(
            overall_score=0.7,
            consciousness_depth=0.6,
            technical_expertise=0.9,
            community_engagement=0.5,
            innovation_leadership=0.8,
            profile_completeness=1.0,
        )
        market_data = {}
        strategy = self.builder.suggest_positioning_strategy(score, market_data)
        self.assertIsInstance(strategy, Strategy)
        self.assertEqual(strategy.name, "The Technical Evangelist")

if __name__ == '__main__':
    unittest.main()
