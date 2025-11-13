# MATRIZ Cognitive Node Guide

This document provides a guide to the MATRIZ cognitive nodes and the node registry.

## Cognitive Nodes

Cognitive nodes are the fundamental building blocks of the MATRIZ system. Each node is a specialized component that performs a specific cognitive function. The system is designed to be modular, allowing for the addition of new nodes to extend its capabilities.

### Node Categories

Nodes are organized into four main categories:

*   **Thought**: Nodes that perform reasoning and other cognitive tasks.
*   **Action**: Nodes that execute actions, such as using tools.
*   **Decision**: Nodes that make decisions, such as selecting from a list of options.
*   **Awareness**: Nodes that provide self-awareness and state assessment.

### Implemented Nodes

The following nodes are currently implemented:

*   `DeductiveReasoningNode`: A `Thought` node that performs deductive reasoning.
*   `ToolUsageNode`: An `Action` node that selects and uses a tool.
*   `OptionSelectionNode`: A `Decision` node that selects the best option from a list.
*   `StateAssessmentNode`: An `Awareness` node that assesses the current state.
*   `MathNode`: A `Computation` node that evaluates mathematical expressions.

## Node Registry

The node registry is a central location for registering and retrieving cognitive nodes. This allows for a decoupled architecture where new nodes can be added without modifying the core system.

### Usage

The registry provides the following functions:

*   `register_node(node_name, node_class)`: Register a new node.
*   `get_node(node_name)`: Retrieve a node by name.
*   `get_all_nodes()`: Get a dictionary of all registered nodes.
