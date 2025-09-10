"""
CRITICAL FILE - DO NOT MODIFY WITHOUT APPROVAL
lukhas AI System - Core Neural Architecture Component
File: __init__.py
Path: core/neural_architectures/__init__.py
Created: 2025-01-27
Author: lukhas AI Team
TAGS: [CRITICAL, KeyFile, Neural_Architecture]
Neural Architecture Module
Advanced neural processing and architecture components for the LUKHAS AGI system.
This module provides sophisticated neural processing capabilities including
adaptive neural networks, pattern recognition, cross-modal integration,
and quantum-enhanced processing.
"""
import streamlit as st

try:
    from .neural_integrator import (
        AdaptiveNeuralNetwork,
        NeuralArchitectureType,
        NeuralContext,
        NeuralIntegrator,
        NeuralMode,
        NeuralPattern,
        get_neural_integrator,
    )
except ImportError:
    # Neural integrator not available due to torch dependency
    pass
__all__ = [
    "AdaptiveNeuralNetwork",
    "NeuralArchitectureType",
    "NeuralContext",
    "NeuralIntegrator",
    "NeuralMode",
    "NeuralPattern",
    "get_neural_integrator",
]