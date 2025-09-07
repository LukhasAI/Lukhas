import numpy as np
import streamlit as st


def validate_modal_agreement(vector_a: np.ndarray, vector_b: np.ndarray, threshold: float = 0.8) -> bool:
    """Return True if cosine similarity between vectors exceeds threshold."""
    if vector_a.shape != vector_b.shape:
        raise ValueError("Vectors must have same shape")
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denom == 0:
        return False
    similarity = float(np.dot(vector_a.ravel(), vector_b.ravel()) / denom)
    return similarity >= threshold
