"""Bridge module for core.neuroplastic_connector → labs.core.neuroplastic_connector"""
from __future__ import annotations

from labs.core.neuroplastic_connector import (
    ConnectorManager,
    NeuroplasticConnector,
    create_connector,
)

__all__ = ["ConnectorManager", "NeuroplasticConnector", "create_connector"]
