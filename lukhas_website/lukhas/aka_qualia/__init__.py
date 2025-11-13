#!/usr/bin/env python3

"""
██╗     ██╗   ██╗██╗  ██╗██╗  ██╗ █████╗ ███████╗
██║     ██║   ██║██║ ██╔╝██║  ██║██╔══██╗██╔════╝
██║     ██║   ██║█████╔╝ ███████║███████║███████╗
██║     ██║   ██║██╔═██╗ ██╔══██║██╔══██║╚════██║
███████╗╚██████╔╝██║  ██╗██║  ██║██║  ██║███████║
╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

Aka Qualia - Phenomenological Module
=====================================

Bidirectional translator between raw multimodal signals and phenomenal scenes
with operational proto-qualia, ethical regulation, and symbolic routing.

Revolutionary Features:
- 8-dimensional proto-qualia operational framework
- Energy-preserving sublimation transforms
- TEQ Guardian ethical oversight
- Loop prevention and neurosis reduction
- Measurable phenomenological outcomes

Performance Targets:
- ≥25% neurosis reduction via loop prevention
- ≥15% goals↔ethics↔scene congruence improvement
- ≥70% positive repair delta post-regulation
- Measurable ablation value vs baseline

Usage:
    from aka_qualia.core import AkaQualia
    aq = AkaQualia(pls, teq_guardian, glyph_mapper, router, memory, cfg)
    result = await aq.step(signals=S, goals=G, ethics_state=E, guardian_state=U, memory_ctx=M)
"""
import streamlit as st

from aka_qualia.core import AkaQualia
from aka_qualia.models import (
    Metrics,
    PhenomenalGlyph,
    PhenomenalScene,
    ProtoQualia,
    RegulationPolicy,
    RiskProfile,
)

__version__ = "0.1.0"
__all__ = [
    "AkaQualia",
    "Metrics",
    "PhenomenalGlyph",
    "PhenomenalScene",
    "ProtoQualia",
    "RegulationPolicy",
    "RiskProfile",
]
