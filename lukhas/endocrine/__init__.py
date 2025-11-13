"""
LUKHAS Bridge to MATRIZ Endocrine Node
"""
from matriz.nodes.endocrine_node import EndocrineNode

_node = EndocrineNode()

def trigger_stress(intensity: float = 0.5):
    return _node.process(
        {
            "query": {
                "operation": "trigger_stress",
                "args": {"intensity": intensity},
            }
        }
    )

def trigger_reward(intensity: float = 0.5):
    return _node.process(
        {
            "query": {
                "operation": "trigger_reward",
                "args": {"intensity": intensity},
            }
        }
    )

def get_hormone_profile():
    return _node.process({"query": {"operation": "get_hormone_profile", "args": {}}})

__all__ = ["get_hormone_profile", "trigger_reward", "trigger_stress"]
