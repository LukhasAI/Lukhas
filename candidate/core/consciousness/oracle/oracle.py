"""
The Consciousness Oracle.

This module serves as the main entry point for the Consciousness Oracle system,
integrating prediction, receptivity, and evolution mapping into a single,
cohesive interface.
"""

from typing import Any, Dict

from .prediction_engine import PredictionEngine
from .receptivity_windows import ReceptivityWindowCalculator
from ..evolution.journey_mapper import ConsciousnessJourneyMapper


class ConsciousnessOracle:
    """
    Predicts user consciousness evolution and receptivity windows.
    This class acts as a facade for the various components of the oracle.
    """

    # ΛTAG: consciousness, oracle, facade

    def __init__(self):
        """
        Initializes the ConsciousnessOracle and its sub-components.
        """
        self.prediction_engine = PredictionEngine()
        self.receptivity_calculator = ReceptivityWindowCalculator()
        self.journey_mapper = ConsciousnessJourneyMapper()

    async def get_full_consciousness_profile(
        self, user_id: str
    ) -> Dict[str, Any]:
        """
        Generates a complete consciousness profile for a user, including
        forecasts, receptivity windows, and long-term journey mapping.

        Args:
            user_id: The ID of the user.

        Returns:
            A dictionary containing the full consciousness profile.
        """
        # In a real implementation, these calls could be made in parallel.
        forecast = await self.prediction_engine.forecast_consciousness_state(user_id)
        receptivity_windows = await self.receptivity_calculator.calculate_receptivity_windows(user_id)
        journey_map = await self.journey_mapper.map_consciousness_journey(user_id)

        profile = {
            "user_id": user_id,
            "short_term_forecast": forecast,
            "receptivity_windows": receptivity_windows,
            "long_term_journey": journey_map,
        }

        return profile
