"""Integration tests for core module."""

import pytest


class TestCore:

    def test_module_imports(self):
        import matriz.consciousness.reflection.core

        assert matriz.consciousness.reflection.core is not None
