#!/usr/bin/env python3
"""Integration tests for compliance_monitor module."""
import pytest


class TestComplianceMonitor:
    def test_module_imports(self):
        import core.governance.ethics.compliance_monitor

        assert core.governance.ethics.compliance_monitor is not None
