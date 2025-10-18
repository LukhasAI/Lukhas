import asyncio
import logging
from enum import Enum
from typing import Any

from core.tiered_state_management import StateType, TieredStateManager

# ΛTAG: consistency_management
logger = logging.getLogger("ΛTRACE.consistency")


class Consistency(Enum):
    EVENTUAL = "eventual"
    STRONG = "strong"


class ConsistencyManager:
    """Applies state updates with the requested consistency level."""

    def __init__(self, state_manager: TieredStateManager | None = None):
        self.state_manager = state_manager or TieredStateManager()
        logger.info("ΛTRACE: ConsistencyManager initialized")

    async def apply_updates(
        self,
        updates: dict[str, dict[str, Any]],
        level: Consistency = Consistency.EVENTUAL,
        state_type: StateType = StateType.LOCAL_EPHEMERAL,
    ) -> None:
        """Apply updates according to consistency requirements."""
        if level is Consistency.STRONG:
            for aggregate_id, data in updates.items():
                await self.state_manager.update_state(aggregate_id, data, state_type)
        else:
            await asyncio.gather(
                *[self.state_manager.update_state(aid, data, state_type) for aid, data in updates.items()]
            )
        logger.debug("ΛTRACE: Updates applied", count=len(updates), level=level.value)
