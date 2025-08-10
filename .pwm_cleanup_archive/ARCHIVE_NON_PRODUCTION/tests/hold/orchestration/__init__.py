"""This package contains all the tests for the orchestration module."""

# Jules 01: The following line is a workaround to fix the imports in the tests.
# It should be removed once a proper solution is found.
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
