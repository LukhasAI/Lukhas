"""Bridge module for emotion.models → labs.emotion.models"""
from __future__ import annotations

from labs.emotion.models import EmotionModel, ModelManager, create_emotion_model

__all__ = ["EmotionModel", "ModelManager", "create_emotion_model"]
