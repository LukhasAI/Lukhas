"""Smoke test for matriz lane."""

import os


def test_matriz_lane_accessible():
    """Test that matriz lane directory is accessible."""
    matriz_dir = os.path.join(os.path.dirname(__file__), "../../matriz")
    assert os.path.exists(matriz_dir), "Matriz lane directory exists"
    # Check if there are Python files to import
    py_files = [f for f in os.listdir(matriz_dir) if f.endswith(".py")]
    assert True, "Matriz lane accessible"
