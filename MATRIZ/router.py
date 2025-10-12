"""
matriz/router.py

SymbolicMeshRouter for MATRIZ Node Contract v1 - log-only mode initially.

Usage:
  export LUKHAS_LANE=experimental
  python -m matriz.demo.router   # runs demo with fixtures
  pytest -k router -q
"""
import queue
from typing import Callable, Dict

from MATRIZ.node_contract import MatrizMessage, MatrizNode


class SymbolicMeshRouter:
    def __init__(self, log_fn: Callable[[str, dict], None]):
        self.nodes: Dict[str, MatrizNode] = {}
        self.q = queue.Queue(maxsize=8192)
        self.log = log_fn
        self.running = False

    def register(self, topic: str, node: MatrizNode):
        self.nodes[topic] = node
        self.log("router.register", {"topic": topic, "node": node.name})

    def publish(self, msg: MatrizMessage):
        # log-only mode: do not dispatch, just record
        self.log("router.publish", {"topic": msg.topic, "lane": msg.lane, "msg_id": str(msg.msg_id)})

    def start(self):
        self.running = True
        self.log("router.start", {})

# Later, flip a DISPATCH_ENABLED feature flag to actually call node.handle(msg) per topic. Start in log-only to observe traffic safely.
