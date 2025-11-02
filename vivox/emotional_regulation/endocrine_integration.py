"""
VIVOX.ERN Endocrine System Integration
Connects emotional regulation to biological hormone simulation
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from core.common import get_logger
try:
    from core.endocrine.hormone_system import HormoneSystem, HormoneType
from .vivox_ern_core import RegulationResponse, RegulationStrategy, VADVector
        try:
        try:
        try:

logger = logging.getLogger(__name__)

            for hormone, amount in triggers.items():
                if abs(amount) > 0.01:  # Only release significant amounts
                    # Determine duration based on hormone type and amount
                    duration = self._calculate_release_duration(hormone, amount)

                    # Execute release
                    if amount > 0:
                        await self.hormone_system.release_hormone(
                            hormone_type=hormone, amount=amount, duration=duration
                        )
                    else:
                        # Negative amount = suppression
                        await self.hormone_system.suppress_hormone(
                            hormone_type=hormone,
                            suppression_factor=abs(amount),
                            duration=duration,
                        )

                    logger.debug(f"Released {hormone}: {amount:.3f} for {duration}min")

        except Exception as e:
            logger.error(f"Error executing hormone releases: {e}")

    def _calculate_release_duration(self, hormone: str, amount: float) -> float:
        """Calculate appropriate release duration for hormone"""

        # Base durations for different hormones (in minutes)
        base_durations = {
            HormoneType.ADRENALINE: 15.0,  # Quick acting
            HormoneType.CORTISOL: 60.0,  # Medium duration
            HormoneType.DOPAMINE: 30.0,  # Medium-short
            HormoneType.SEROTONIN: 45.0,  # Medium
            HormoneType.GABA: 20.0,  # Short-medium
            HormoneType.OXYTOCIN: 25.0,  # Short-medium
            HormoneType.MELATONIN: 120.0,  # Long duration
            HormoneType.ENDORPHIN: 40.0,  # Medium
        }

        base_duration = base_durations.get(hormone, 30.0)

        # Scale duration by release amount
        intensity_factor = min(2.0, max(0.5, abs(amount) * 2))

        return base_duration * intensity_factor

    async def _record_hormone_release(
        self,
        triggers: dict[str, float],
        regulation_response: RegulationResponse,
        context: dict[str, Any],
    ):
        """Record hormone release for learning and analysis"""

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": context.get("user_id", "unknown"),
            "regulation_strategy": regulation_response.strategy_used.value,
            "regulation_effectiveness": regulation_response.effectiveness,
            "emotional_state": regulation_response.original_state.to_dict(),
            "hormone_triggers": triggers,
            "context": context,
        }

        self.hormone_release_history.append(record)

        # Limit history size
        if len(self.hormone_release_history) > 1000:
            self.hormone_release_history = self.hormone_release_history[-800:]

    def _simulate_hormone_release(
        self, regulation_response: RegulationResponse, context: dict[str, Any]
    ) -> dict[str, float]:
        """Simulate hormone release when endocrine system is not available"""

        # Basic simulation based on regulation response
        simulated_triggers = {}

        effectiveness = regulation_response.effectiveness
        original_state = regulation_response.original_state
        strategy = regulation_response.strategy_used

        # Stress-related hormones
        if original_state.arousal > 0.5 or original_state.valence < -0.3:
            simulated_triggers[HormoneType.CORTISOL] = (1 - effectiveness) * 0.6
            simulated_triggers[HormoneType.ADRENALINE] = (1 - effectiveness) * 0.4

        # Positive regulation hormones
        if effectiveness > 0.6:
            if strategy == RegulationStrategy.BREATHING:
                simulated_triggers[HormoneType.GABA] = effectiveness * 0.4
                simulated_triggers[HormoneType.SEROTONIN] = effectiveness * 0.3
            elif strategy == RegulationStrategy.COGNITIVE:
                simulated_triggers[HormoneType.DOPAMINE] = effectiveness * 0.3
                simulated_triggers[HormoneType.SEROTONIN] = effectiveness * 0.2

        return simulated_triggers

    def get_hormone_analytics(self, user_id: str, hours: int = 24) -> dict[str, Any]:
        """Get hormone release analytics for user"""

        cutoff_time = datetime.now(timezone.utc).timestamp() - (hours * 3600)

        relevant_records = [
            record
            for record in self.hormone_release_history
            if record["user_id"] == user_id and datetime.fromisoformat(record["timestamp"]).timestamp() > cutoff_time
        ]

        if not relevant_records:
            return {"message": "No hormone data available"}

        # Analyze hormone patterns
        hormone_totals = {}
        strategy_effectiveness = {}

        for record in relevant_records:
            # Sum hormone releases
            for hormone, amount in record["hormone_triggers"].items():
                if hormone not in hormone_totals:
                    hormone_totals[hormone] = {
                        "positive": 0.0,
                        "negative": 0.0,
                        "count": 0,
                    }

                if amount > 0:
                    hormone_totals[hormone]["positive"] += amount
                else:
                    hormone_totals[hormone]["negative"] += abs(amount)
                hormone_totals[hormone]["count"] += 1

            # Track strategy effectiveness
            strategy = record["regulation_strategy"]
            effectiveness = record["regulation_effectiveness"]

            if strategy not in strategy_effectiveness:
                strategy_effectiveness[strategy] = []
            strategy_effectiveness[strategy].append(effectiveness)

        # Calculate averages
        for strategy in strategy_effectiveness:
            scores = strategy_effectiveness[strategy]
            strategy_effectiveness[strategy] = {
                "average": sum(scores) / len(scores),
                "count": len(scores),
            }

        return {
            "total_hormone_events": len(relevant_records),
            "hormone_release_patterns": hormone_totals,
            "strategy_effectiveness": strategy_effectiveness,
            "most_active_hormones": sorted(
                [(h, data["positive"] + data["negative"]) for h, data in hormone_totals.items()],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
            "stress_indicators": {
                "cortisol_releases": hormone_totals.get(HormoneType.CORTISOL, {}).get("positive", 0),
                "adrenaline_releases": hormone_totals.get(HormoneType.ADRENALINE, {}).get("positive", 0),
                "stress_regulation_success": sum(
                    1
                    for r in relevant_records
                    if r["regulation_effectiveness"] > 0.7
                    and (
                        HormoneType.CORTISOL in r["hormone_triggers"] or HormoneType.ADRENALINE in r["hormone_triggers"]
                    )
                ),
            },
            "wellbeing_indicators": {
                "serotonin_releases": hormone_totals.get(HormoneType.SEROTONIN, {}).get("positive", 0),
                "dopamine_releases": hormone_totals.get(HormoneType.DOPAMINE, {}).get("positive", 0),
                "endorphin_releases": hormone_totals.get(HormoneType.ENDORPHIN, {}).get("positive", 0),
            },
        }

    def get_integration_status(self) -> dict[str, Any]:
        """Get endocrine integration status"""
        return {
            "endocrine_system_available": ENDOCRINE_AVAILABLE,
            "hormone_mappings_loaded": len(self.emotional_hormone_mappings),
            "regulation_mappings_loaded": len(self.regulation_hormone_mappings),
            "hormone_release_history_size": len(self.hormone_release_history),
            "feedback_enabled": self.hormone_feedback_enabled,
            "feedback_sensitivity": self.feedback_sensitivity,
            "baseline_hormones": self.baseline_levels,
        }
