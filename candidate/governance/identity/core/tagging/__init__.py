"""
Identity Tagging System

Trust network-based tagging with consensus mechanisms and
tier-aware permission resolution.
"""
import streamlit as st

from .identity_tag_resolver import (
    IdentityTag,
    IdentityTagResolver,
    IdentityTagType,
    TrustLevel,
    TrustRelationship,
)

__all__ = [
    "IdentityTag",
    "IdentityTagResolver",
    "IdentityTagType",
    "TrustLevel",
    "TrustRelationship",
]