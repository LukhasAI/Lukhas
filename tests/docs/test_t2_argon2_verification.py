"""Regression tests for the T2 Argon2id verification scaffold."""

from dataclasses import dataclass
from typing import Optional

import pytest

argon2 = pytest.importorskip("argon2")
from argon2.exceptions import VerifyMismatchError

password_hasher = argon2.PasswordHasher()


@dataclass
class DummyContext:
    """Minimal authentication context used in the documentation scaffold."""

    password: Optional[str] = None
    password_hash: Optional[str] = None
    credentials: Optional[dict] = None


def _run_scaffold_logic(ctx: DummyContext) -> tuple[bool, str]:
    """Mirror the documentation snippet to keep behaviour covered by tests."""

    start_ok = False
    failure_reason = "invalid_credentials"

    candidate_password = getattr(ctx, "password", None)
    stored_hash = getattr(ctx, "password_hash", None)

    if stored_hash is None and ctx.credentials is not None:
        stored_hash = ctx.credentials.get("password_hash")
    if candidate_password is None and ctx.credentials is not None:
        candidate_password = ctx.credentials.get("password")

    if not stored_hash:
        failure_reason = "missing_hash"
    elif candidate_password is None:
        failure_reason = "missing_credentials"
    else:
        try:
            password_hasher.verify(stored_hash, candidate_password)
        except VerifyMismatchError:
            failure_reason = "invalid_credentials"
        except Exception:
            failure_reason = "argon2_error"
        else:
            start_ok = True

    return start_ok, failure_reason


def test_scaffold_verifies_valid_password():
    password = "P@ssw0rd!"
    hashed = password_hasher.hash(password)
    ctx = DummyContext(password=password, password_hash=hashed)

    start_ok, reason = _run_scaffold_logic(ctx)

    assert start_ok is True
    assert reason == "invalid_credentials"  # unchanged on success


def test_scaffold_detects_wrong_password():
    password = "correct-horse-battery-staple"
    hashed = password_hasher.hash(password)
    ctx = DummyContext(password="incorrect", password_hash=hashed)

    start_ok, reason = _run_scaffold_logic(ctx)

    assert start_ok is False
    assert reason == "invalid_credentials"


def test_scaffold_handles_missing_hash():
    ctx = DummyContext(password="irrelevant", password_hash=None)

    start_ok, reason = _run_scaffold_logic(ctx)

    assert start_ok is False
    assert reason == "missing_hash"
