# LUKHAS Module

## Purpose

The `lukhas` module serves as a compatibility shim and a stable entry point to the LUKHAS AI system. As the codebase evolves and core components are migrated to dedicated top-level modules, this module provides a consistent import path, ensuring that existing integrations and tools continue to function without disruption.

## Architecture

The `lukhas` module is designed to be a lightweight wrapper that re-exports functionality from other, more specialized modules. It contains critical subsystems that are fundamental to the LUKHAS architecture:

- **`identity/`**: Manages authentication, authorization, and other identity-related services.
- **`memory/`**: Provides the core memory and data storage capabilities for the AI.

## Key Components

- **`lukhas/__init__.py`**: The main entry point to the module, which handles the aliasing of other modules to provide a unified namespace.

## Usage Examples

To ensure backward compatibility, you can continue to import modules from `lukhas` as you normally would:

```python
from lukhas.core import AsyncCognitiveOrchestrator
from lukhas.memory import EmbeddingIndex
```
