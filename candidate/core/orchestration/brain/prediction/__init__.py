"""
Prediction Module for lukhas AI

This module provides predictive modeling and resource management capabilities
for proactive system optimization.
"""
import streamlit as st

from .predictive_resource_manager import (
    PredictionModel,
    PredictiveResourceManager,
    ResourceType,
)

__all__ = ["PredictionModel", "PredictiveResourceManager", "ResourceType"]
