# @generated LUKHAS scaffold v1.0
# template_id: module.scaffold/v1
# template_commit: f95979630
# do_not_edit: true
# human_editable: false
#
"""
Unit tests for security module.
"""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest


def _load_module(name: str) -> ModuleType | None:
    """Best-effort import helper that returns ``None`` when unavailable."""

    try:
        return importlib.import_module(name)
    except ImportError:
        return None


SECURITY_MODULE = _load_module("security")

if SECURITY_MODULE is None:
    pytest.skip("Module security not available", allow_module_level=True)


IDENTITY_GUARD_MODULE = _load_module("security.IDENTITY_GUARD")

IDENTITY_GUARD_CLASS = (
    getattr(IDENTITY_GUARD_MODULE, "IdentityGuard", None) if IDENTITY_GUARD_MODULE is not None else None
)
IDENTITY_GUARD_MAIN = getattr(IDENTITY_GUARD_MODULE, "main", None) if IDENTITY_GUARD_MODULE is not None else None


class TestSecurityModule(unittest.TestCase):
    """Unit tests for security module core functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "module_name": "security",
            "test_mode": True,
        }

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_module_import(self):
        """Test that module can be imported successfully."""
        self.assertIsInstance(SECURITY_MODULE, ModuleType)
        self.assertEqual(SECURITY_MODULE.__name__, "security")

    def test_module_version(self):
        """Test module has version information."""
        version_present = any(hasattr(SECURITY_MODULE, attr) for attr in ("__version__", "VERSION"))
        self.assertTrue(version_present or SECURITY_MODULE.__doc__)

    def test_module_initialization(self):
        """Test module can be initialized."""
        if IDENTITY_GUARD_CLASS is None:
            self.skipTest("IdentityGuard component unavailable")

        guard = IDENTITY_GUARD_CLASS()
        self.assertTrue(hasattr(guard, "validate_file"))

    @pytest.mark.unit
    def test_core_functionality(self):
        """Test core module functionality."""
        if IDENTITY_GUARD_CLASS is None:
            self.skipTest("IdentityGuard component unavailable")

        guard = IDENTITY_GUARD_CLASS()
        is_valid, violations = guard.validate_file(Path("nonexistent.txt"))

        self.assertTrue(is_valid)
        self.assertEqual(violations, [])

    @pytest.mark.unit
    def test_error_handling(self):
        """Test module error handling."""
        if IDENTITY_GUARD_CLASS is None:
            self.skipTest("IdentityGuard component unavailable")

        guard = IDENTITY_GUARD_CLASS()
        with tempfile.NamedTemporaryFile("w", suffix=".py", prefix="api_guard_", delete=False) as tmp_file:
            tmp_file.write(
                "from fastapi import APIRouter\n"
                "router = APIRouter()\n\n"
                '@router.get("/items")\n'
                "def list_items():\n"
                '    data = {"value": 1}\n'
                "    return data\n"
            )
            temp_path = Path(tmp_file.name)

        try:
            is_valid, violations = guard.validate_file(temp_path)
            self.assertFalse(is_valid)
            joined = " ".join(violations)
            self.assertIn("UNPROTECTED API ENDPOINT", joined)
            self.assertIn("DATA OPERATION WITHOUT USER TRACKING", joined)
        finally:
            temp_path.unlink(missing_ok=True)

    @pytest.mark.unit
    def test_configuration_validation(self):
        """Test configuration validation."""
        if IDENTITY_GUARD_CLASS is None:
            self.skipTest("IdentityGuard component unavailable")

        guard = IDENTITY_GUARD_CLASS()
        with tempfile.NamedTemporaryFile("w", suffix=".py", prefix="api_guard_", delete=False) as tmp_file:
            tmp_file.write(
                "from fastapi import APIRouter, Depends\n"
                "from identity.middleware import AuthContext, require_t3_or_above\n\n"
                "router = APIRouter()\n\n"
                '@router.get("/items")\n'
                "def list_items(user: AuthContext = Depends(require_t3_or_above)):\n"
                '    data = {"user_id": user.user_id}\n'
                "    return data\n"
            )
            temp_path = Path(tmp_file.name)

        try:
            with mock.patch("security.IDENTITY_GUARD.print"):
                self.assertTrue(guard.validate_changes([str(temp_path)]))
        finally:
            temp_path.unlink(missing_ok=True)


# Test individual components if entrypoints available


@unittest.skipIf(IDENTITY_GUARD_CLASS is None, "IdentityGuard component unavailable")
class TestIdentityGuard(unittest.TestCase):
    """Tests for IdentityGuard component."""

    def test_identityguard_import(self):
        """Test IdentityGuard can be imported."""
        self.assertIs(IDENTITY_GUARD_CLASS, getattr(IDENTITY_GUARD_MODULE, "IdentityGuard"))

    def test_identityguard_instantiation(self):
        """Test IdentityGuard can be instantiated."""
        guard = IDENTITY_GUARD_CLASS()
        self.assertIsInstance(guard, IDENTITY_GUARD_CLASS)

    def test_validate_file_detects_unprotected_api(self):
        """Ensure violations are reported for unprotected API endpoints."""

        guard = IDENTITY_GUARD_CLASS()

        with tempfile.NamedTemporaryFile("w", suffix=".py", prefix="api_guard_", delete=False) as tmp_file:
            tmp_file.write(
                "from fastapi import APIRouter\n"
                "router = APIRouter()\n\n"
                '@router.get("/items")\n'
                "def list_items():\n"
                '    data = {"value": 1}\n'
                "    return data\n"
            )
            temp_path = Path(tmp_file.name)

        try:
            is_valid, violations = guard.validate_file(temp_path)
            self.assertFalse(is_valid)
            self.assertTrue(violations)
            combined = " ".join(violations)
            self.assertIn("UNPROTECTED API ENDPOINT", combined)
        finally:
            temp_path.unlink(missing_ok=True)


@unittest.skipIf(IDENTITY_GUARD_MAIN is None, "main component unavailable")
class Testmain(unittest.TestCase):
    """Tests for main component."""

    def test_main_import(self):
        """Test main can be imported."""
        self.assertTrue(callable(IDENTITY_GUARD_MAIN))

    def test_main_instantiation(self):
        """Test main can be instantiated."""
        with (
            mock.patch.object(sys, "argv", ["identity_guard"]),
            mock.patch("security.IDENTITY_GUARD.IdentityGuard") as guard_cls,
        ):
            guard_instance = guard_cls.return_value
            guard_instance.validate_changes.return_value = True

            IDENTITY_GUARD_MAIN()

            guard_instance.validate_changes.assert_called_once_with(None)

    def test_main_pre_commit_exit_codes(self):
        """Pre-commit flag should exit with appropriate status code."""

        with (
            mock.patch.object(sys, "argv", ["identity_guard", "--pre-commit"]),
            mock.patch("security.IDENTITY_GUARD.IdentityGuard") as guard_cls,
            mock.patch("security.IDENTITY_GUARD.sys.exit") as mock_exit,
        ):
            guard_instance = guard_cls.return_value
            guard_instance.validate_changes.return_value = False

            IDENTITY_GUARD_MAIN()

            mock_exit.assert_called_once_with(1)


@unittest.skipIf(IDENTITY_GUARD_CLASS is None, "IdentityGuard component unavailable")
class TestValidateChanges(unittest.TestCase):
    """Tests for validate_changes component."""

    def setUp(self):
        self.guard = IDENTITY_GUARD_CLASS()

    def test_validate_changes_returns_true_for_compliant_file(self):
        """Compliant files should pass validation."""

        with tempfile.NamedTemporaryFile("w", suffix=".py", prefix="api_guard_", delete=False) as tmp_file:
            tmp_file.write(
                "from fastapi import APIRouter, Depends\n"
                "from identity.middleware import AuthContext, require_t3_or_above\n\n"
                "router = APIRouter()\n\n"
                '@router.get("/items")\n'
                "def list_items(user: AuthContext = Depends(require_t3_or_above)):\n"
                '    data = {"user_id": user.user_id}\n'
                "    return data\n"
            )
            temp_path = Path(tmp_file.name)

        try:
            with mock.patch("security.IDENTITY_GUARD.print"):
                result = self.guard.validate_changes([str(temp_path)])
            self.assertTrue(result)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_validate_changes_returns_false_for_unprotected_file(self):
        """Violations should cause validate_changes to fail."""

        with tempfile.NamedTemporaryFile("w", suffix=".py", prefix="api_guard_", delete=False) as tmp_file:
            tmp_file.write(
                "from fastapi import APIRouter\n\n"
                "router = APIRouter()\n\n"
                '@router.get("/items")\n'
                "def list_items():\n"
                '    data = {"value": 1}\n'
                "    return data\n"
            )
            temp_path = Path(tmp_file.name)

        try:
            with mock.patch("security.IDENTITY_GUARD.print"):
                result = self.guard.validate_changes([str(temp_path)])
            self.assertFalse(result)
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
