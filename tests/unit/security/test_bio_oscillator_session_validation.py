"""Tests for BioOscillator session token validation."""

from __future__ import annotations

import hashlib
import importlib.machinery
import importlib.util
import logging
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_modules():
    """Load BioOscillator and SessionTokenStore while patching dependencies."""

    for module_name in list(sys.modules):
        if module_name == "qi" or module_name.startswith("qi."):
            sys.modules.pop(module_name)

    qi_module = types.ModuleType("qi")
    qi_spec = importlib.machinery.ModuleSpec("qi", loader=None, is_package=True)
    qi_spec.submodule_search_locations = [str(REPO_ROOT / "qi")]
    qi_module.__spec__ = qi_spec
    qi_module.__path__ = qi_spec.submodule_search_locations
    sys.modules["qi"] = qi_module

    security_module = types.ModuleType("qi.security")
    security_spec = importlib.machinery.ModuleSpec("qi.security", loader=None, is_package=True)
    security_spec.submodule_search_locations = [str(REPO_ROOT / "qi" / "security")]
    security_module.__spec__ = security_spec
    security_module.__path__ = security_spec.submodule_search_locations
    sys.modules["qi.security"] = security_module

    token_spec = importlib.util.spec_from_file_location(
        "qi.security.token_store", REPO_ROOT / "qi" / "security" / "token_store.py"
    )
    token_module = importlib.util.module_from_spec(token_spec)
    assert token_spec.loader is not None
    sys.modules["qi.security.token_store"] = token_module
    token_spec.loader.exec_module(token_module)

    bio_module = types.ModuleType("qi.bio")
    bio_spec = importlib.machinery.ModuleSpec("qi.bio", loader=None, is_package=True)
    bio_spec.submodule_search_locations = [str(REPO_ROOT / "qi" / "bio")]
    bio_module.__spec__ = bio_spec
    bio_module.__path__ = bio_spec.submodule_search_locations
    sys.modules["qi.bio"] = bio_module

    oscillators_pkg = types.ModuleType("qi.bio.oscillators")
    oscillators_spec = importlib.machinery.ModuleSpec("qi.bio.oscillators", loader=None, is_package=True)
    oscillators_spec.submodule_search_locations = [str(REPO_ROOT / "qi" / "bio" / "oscillators")]
    oscillators_pkg.__spec__ = oscillators_spec
    oscillators_pkg.__path__ = oscillators_spec.submodule_search_locations
    sys.modules["qi.bio.oscillators"] = oscillators_pkg

    oscillator_spec = importlib.util.spec_from_file_location(
        "qi.bio.oscillators.oscillator", REPO_ROOT / "qi" / "bio" / "oscillators" / "oscillator.py"
    )
    oscillator_module = importlib.util.module_from_spec(oscillator_spec)
    assert oscillator_spec.loader is not None
    sys.modules["qi.bio.oscillators.oscillator"] = oscillator_module

    original_get_logger = logging.getLogger

    def patched_get_logger(name, *args, **kwargs):
        return original_get_logger(name)

    logging.getLogger = patched_get_logger
    try:
        oscillator_spec.loader.exec_module(oscillator_module)
    finally:
        logging.getLogger = original_get_logger

    return (
        oscillator_module.BioOscillator,
        token_module.SessionTokenStore,
        oscillator_module.SecurityContext,
    )


BioOscillator, SessionTokenStore, SecurityContext = _load_modules()


@pytest.fixture
def oscillator_with_store(tmp_path):
    store = SessionTokenStore(state_dir=tmp_path)
    BioOscillator.configure_session_token_store(store)
    oscillator = BioOscillator()
    yield oscillator, store
    BioOscillator.configure_session_token_store(None)


def test_verify_session_token_requires_registered_token(oscillator_with_store):
    oscillator, _ = oscillator_with_store
    assert not oscillator._verify_session_token("missing-token")


def test_verify_session_token_accepts_registered_token(oscillator_with_store):
    oscillator, store = oscillator_with_store
    store.register_token("valid-token", metadata={"user_id": "user-123"})
    assert oscillator._verify_session_token("valid-token")


def test_verify_session_token_rejects_expired_token(tmp_path):
    current_time = {
        "value": datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    }

    def clock() -> datetime:
        return current_time["value"]

    store = SessionTokenStore(state_dir=tmp_path, clock=clock)
    BioOscillator.configure_session_token_store(store)
    oscillator = BioOscillator()

    store.register_token("expiring-token", ttl_seconds=30)
    current_time["value"] = current_time["value"] + timedelta(seconds=120)

    try:
        assert not oscillator._verify_session_token("expiring-token")
    finally:
        BioOscillator.configure_session_token_store(None)


@pytest.mark.asyncio
async def test_verify_lukhas_id_registers_token_when_missing(tmp_path):
    store = SessionTokenStore(state_dir=tmp_path)
    BioOscillator.configure_session_token_store(store)
    oscillator = BioOscillator()

    security_context = SecurityContext(
        lukhas_id="lambda-789",
        access_level=3,
        session_token="auto-registered-token",
        verification_data={"session_metadata": {"source": "unit-test"}},
    )

    try:
        assert await oscillator.verify_lukhas_id(security_context)
        tokens = store.list_tokens()
        token_hash = hashlib.sha256("auto-registered-token".encode("utf-8")).hexdigest()
        assert token_hash in tokens
    finally:
        BioOscillator.configure_session_token_store(None)
