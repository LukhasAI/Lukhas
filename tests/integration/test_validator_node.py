#!/usr/bin/env python3
"""Integration tests for validator_node module."""
import pytest

class TestValidatorNode:
    def test_module_imports(self):
        import matriz.nodes.validator_node
        assert matriz.nodes.validator_node is not None
