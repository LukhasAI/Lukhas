"""
State Management in a Stateless World
Addresses TODOs 115-117, 131-134

This module provides a simple implementation of a state manager that uses
event sourcing and snapshotting to manage state in a distributed,
stateless environment.
"""
import json
import os

import streamlit as st


class StateManager:
    def __init__(self, agent_id, storage_path="/tmp/state"):
        self.agent_id = agent_id
        self.storage_path = os.path.join(storage_path, agent_id)
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        self.state = {}
        self.event_log = []
        self._load_latest_snapshot()
        self._replay_events()

    def _load_latest_snapshot(self):
        try:
            snapshot_files = [f for f in os.listdir(self.storage_path) if f.endswith(".snapshot")]
            if not snapshot_files:
                return
            latest_snapshot = max(snapshot_files)
            with open(os.path.join(self.storage_path, latest_snapshot)) as f:
                self.state = json.load(f)
        except Exception as e:
            print(f"StateManager: Could not load snapshot: {e}")

    def _replay_events(self):
        try:
            with open(os.path.join(self.storage_path, "events.log")) as f:
                for line in f:
                    event = json.loads(line)
                    self.apply_event(event, replay=True)
        except FileNotFoundError:
            pass  # No events to replay

    def apply_event(self, event, replay=False):
        # In a real system, you would have more sophisticated event handlers
        if event["type"] == "set":
            self.state[event["key"]] = event["value"]
        elif event["type"] == "delete" and event["key"] in self.state:
            del self.state[event["key"]]

        if not replay:
            self.log_event(event)

    def log_event(self, event):
        self.event_log.append(event)
        with open(os.path.join(self.storage_path, "events.log"), "a") as f:
            f.write(json.dumps(event) + "\n")

    def take_snapshot(self):
        snapshot_file = f"{len(self.event_log)}.snapshot"
        with open(os.path.join(self.storage_path, snapshot_file), "w") as f:
            json.dump(self.state, f)
        print(f"StateManager: Snapshot taken at event {len(self.event_log)}")


if __name__ == "__main__":
    state_manager = StateManager("agent-001")
    state_manager.apply_event({"type": "set", "key": "name", "value": "Jules"})
    state_manager.apply_event({"type": "set", "key": "role", "value": "Software Engineer"})
    state_manager.take_snapshot()
    state_manager.apply_event({"type": "delete", "key": "role"})

    print(f"Final state: {state_manager.state}")
