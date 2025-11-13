"""
LUKHAS Bridge to MATRIZ Tag Registry Node
"""
from matriz.nodes.tags_node import TagRegistryNode

_node = TagRegistryNode()

def get_tag(tag_name: str):
    return _node.process({"query": {"operation": "get_tag", "args": {"tag_name": tag_name}}})

def explain_tag(tag_name: str, context: dict = None):
    return _node.process(
        {
            "query": {
                "operation": "explain_tag",
                "args": {"tag_name": tag_name, "context": context},
            }
        }
    )

__all__ = ["get_tag", "explain_tag"]
