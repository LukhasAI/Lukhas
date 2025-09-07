"""
Integration patches for supervision system with existing actor system
This bridges the supervision module with the base actor system
"""
import streamlit as st

import asyncio
import logging
import time
from typing import Optional

from lukhas.core.actor_system import Actor, ActorSystem
from lukhas.core.supervision import RootSupervisor, SupervisionStrategy

logger = logging.getLogger(__name__)


def patch_actor_system_for_supervision():
    """Monkey patch the ActorSystem to support supervision features"""

    # Store original methods
    original_init = ActorSystem.__init__
    original_start = ActorSystem.start

    def new_init(self, system_name: str = "lukhas-actors"):
        # Call original init
        original_init(self, system_name)

        # Add supervision support
        self.root_supervisor: Optional[RootSupervisor] = None
        self.supervision_enabled = True

    async def new_start(self):
        # Call original start
        await original_start(self)

        # Create root supervisor if supervision is enabled
        if self.supervision_enabled:
            try:
                self.root_supervisor = RootSupervisor()
                await self.root_supervisor.start(self)
                logger.info("Root supervisor started for actor system")
            except Exception as e:
                logger.error(f"Failed to start root supervisor: {e}")

    # Apply patches
    ActorSystem.__init__ = new_init
    ActorSystem.start = new_start


def patch_actor_for_supervision():
    """Patch the base Actor class to notify supervisor on failures"""

    # Store original message loop
    Actor._message_loop

    async def new_message_loop(self):
        """Enhanced message loop with supervision support"""
        while self._running:
            try:
                # Get message from mailbox
                message = await asyncio.wait_for(self.mailbox.get(), timeout=1.0)

                await self._process_message(message)
                self._stats["messages_processed"] += 1
                self._stats["last_activity"] = time.time()

            except asyncio.TimeoutError:
                # No message received, continue
                continue
            except Exception as e:
                self._stats["messages_failed"] += 1
                logger.error(f"Actor {self.actor_id} message processing error: {e}")

                # Notify supervisor of failure (enhanced from original)
                if self.supervisor:
                    import traceback

                    await self.supervisor.tell(
                        "child_failed",
                        {
                            "child_id": self.actor_id,
                            "error": str(e),
                            "error_type": type(e).__name__,
                            "stack_trace": traceback.format_exc(),
                        },
                    )

    # Apply patch
    Actor._message_loop = new_message_loop


# Auto-apply patches when imported
patch_actor_system_for_supervision()
patch_actor_for_supervision()

# Enhanced actor system with supervision


class SupervisedActorSystem(ActorSystem):
    """Actor system with built-in supervision support"""

    def __init__(self, system_name: str = "lukhas-actors-supervised"):
        super().__init__(system_name)
        self.default_supervision_strategy = SupervisionStrategy()

    async def create_supervised_actor(
        self,
        actor_class: type,
        actor_id: str,
        supervisor_id: Optional[str] = None,
        supervision_strategy: Optional[SupervisionStrategy] = None,
        *args,
        **kwargs,
    ):
        """Create an actor under supervision"""

        # Determine supervisor
        if supervisor_id:
            supervisor_ref = self.get_actor_ref(supervisor_id)
            if not supervisor_ref:
                raise ValueError(f"Supervisor {supervisor_id} not found")
        else:
            # Use root supervisor
            if not self.root_supervisor:
                raise RuntimeError("Root supervisor not available")
            supervisor_ref = self.get_actor_ref("root-supervisor")

        # Create the actor under supervision
        response = await supervisor_ref.ask(
            "create_child",
            {
                "child_class": actor_class,
                "child_id": actor_id,
                "args": args,
                "kwargs": kwargs,
            },
        )

        if response.get("status") == "error":
            raise RuntimeError(f"Failed to create supervised actor: {response}")

        return self.get_actor_ref(actor_id)


# Global supervised actor system instance
_global_supervised_system = None


async def get_supervised_actor_system() -> SupervisedActorSystem:
    """Get the global supervised actor system instance"""
    global _global_supervised_system
    if _global_supervised_system is None:
        _global_supervised_system = SupervisedActorSystem()
        await _global_supervised_system.start()
    return _global_supervised_system
