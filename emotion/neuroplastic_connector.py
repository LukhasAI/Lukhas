"""Bridge module for emotion.neuroplastic_connector → labs.emotion.neuroplastic_connector"""
from __future__ import annotations

from labs.emotion.neuroplastic_connector import (
    ConnectorManager,
    NeuroplasticConnector,
    create_connector,
)

__all__ = ["ConnectorManager", "NeuroplasticConnector", "create_connector"]
