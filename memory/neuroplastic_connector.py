"""Bridge module for memory.neuroplastic_connector → labs.memory.neuroplastic_connector"""
from __future__ import annotations

from labs.memory.neuroplastic_connector import (
    ConnectorManager,
    NeuroplasticConnector,
    create_connector,
)

__all__ = ["ConnectorManager", "NeuroplasticConnector", "create_connector"]
