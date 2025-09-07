from dataclasses import dataclass, field

import numpy as np
import streamlit as st


@dataclass
class EmotionVector:
    joy: float = 0.0
    sadness: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0

    def as_array(self):
        return np.array([self.joy, self.sadness, self.anger, self.fear, self.surprise, self.disgust])

    def get_dominant(self) -> str:
        values = self.as_array()
        idx = int(np.argmax(values))
        return ["joy", "sadness", "anger", "fear", "surprise", "disgust"][idx]


@dataclass
class EmotionalState:
    vector: EmotionVector = field(default_factory=EmotionVector)
