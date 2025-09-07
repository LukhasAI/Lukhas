import time
from enum import Enum

import streamlit as st


class SupervisionStrategy(Enum):
    RESTART = 1
    STOP = 2
    ESCALATE = 3


class Supervisor:
    def __init__(
        self,
        strategy=SupervisionStrategy.RESTART,
        max_restarts=3,
        restart_delay=1,
    ):
        self.strategy = strategy
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.children = {}

    def add_child(self, actor_id, actor_ref):
        self.children[actor_id] = {"ref": actor_ref, "restarts": 0}

    def handle_failure(self, actor_id, exception):
        print(f"Supervisor: Handling failure for actor {actor_id}: {exception}")
        if actor_id not in self.children:
            print(f"Supervisor: Actor {actor_id} not found in children.")
            return

        if self.strategy == SupervisionStrategy.RESTART:
            self._restart_child(actor_id)
        elif self.strategy == SupervisionStrategy.STOP:
            self._stop_child(actor_id)
        elif self.strategy == SupervisionStrategy.ESCALATE:
            self._escalate_failure(actor_id, exception)

    def _restart_child(self, actor_id):
        child_info = self.children[actor_id]
        if child_info["restarts"] < self.max_restarts:
            child_info["restarts"] += 1
            print(f"Supervisor: Restarting actor {actor_id} (Attempt {child_info['restarts']}/{self.max_restarts})")
            time.sleep(self.restart_delay)
            # In a real implementation, we would restart the actor process or object
            # For now, we'll just print a message
            print(f"Supervisor: Actor {actor_id} restarted.")
        else:
            print(f"Supervisor: Max restarts reached for actor {actor_id}. Stopping.")
            self._stop_child(actor_id)

    def _stop_child(self, actor_id):
        print(f"Supervisor: Stopping actor {actor_id}.")
        # In a real implementation, we would stop the actor process or object
        # For now, we'll just remove it from the children list
        if actor_id in self.children:
            del self.children[actor_id]
        print(f"Supervisor: Actor {actor_id} stopped.")

    def _escalate_failure(self, actor_id, exception):
        print(f"Supervisor: Escalating failure for actor {actor_id}.")
        # In a real implementation, this would propagate the failure to the supervisor's parent
        # For now, we'll just raise the exception
        raise exception
