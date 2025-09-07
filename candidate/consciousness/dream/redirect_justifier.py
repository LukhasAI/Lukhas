"""
Module: redirect_justifier.py
Author: Jules 03
Date: 2025-07-19
Description: Provides a symbolic summary for dream redirects.
"""
from typing import Any, Dict

import streamlit as st

# LUKHAS_TAG: dream_redirect_chain


class RedirectJustifier:
    """
    Translates redirect reasoning into a symbolic summary.
    """

    def justify(
        self,
        drift_delta: float,
        emotion_conflict: float,
        snapshot_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Generates a symbolic summary for a redirect.

        Args:
            drift_delta (float): The drift delta that triggered the redirect.
            emotion_conflict (float): The emotion conflict that triggered the redirect.
            snapshot_context (Dict[str, Any]): The context of the snapshot that triggered the redirect.

        Returns:
            Dict[str, Any]: A symbolic summary of the redirect.
        """
        summary = (
            f"Redirect triggered due to high drift ({drift_delta:.2f}) and emotion conflict ({emotion_conflict:.2f})."
        )
        tags = ["redirect", "drift", "emotion_conflict"]
        insight_level = int((drift_delta + emotion_conflict) * 5)

        return {
            "summary": summary,
            "tags": tags,
            "insight_level": insight_level,
        }
