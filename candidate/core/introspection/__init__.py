# ΛLOCKED: Core introspection module initialization
"""
Core Introspection Module

Phase 3C: Modular Introspection System
Provides symbolic-aware module scanning and state reporting
"""
import streamlit as st

from .introspector import ModuleIntrospector, analyze_module, report_symbolic_state

__all__ = ["ModuleIntrospector", "analyze_module", "report_symbolic_state"]
