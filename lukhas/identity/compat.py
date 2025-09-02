"""Compatibility helpers for ΛID naming across the codebase.

Provides safe, local mapping helpers so modules can accept both the
historical `lambda_id` and the preferred short form `lid`/`l_id`.

Use these helpers to read external inputs and to produce outputs that
include both keys where necessary for backwards compatibility.
"""

from collections.abc import Mapping
from typing import Any, Optional


def canonicalize_id_from_kwargs(kwargs: Mapping[str, Any]) -> Optional[str]:
    """Return canonical `lid` value from a kwargs-like mapping.

    Preference order:
    - `lid`
    - `l_id`
    - `lambda_id`
    - `_lambda_id`
    - `user_id` (fallback)
    """
    if not kwargs:
        return None

    # Include historical and common misspellings to be tolerant during migration.
    # Preference order includes canonical short names first, then legacy full names
    # and a previously-observed misspelling 'lambd' (missing 'a').
    for key in (
        "lid",
        "l_id",
        "_l_id",
        "lambda_id",
        "_lambda_id",
        "lambd",
        "_lambd",
        "user_id",
    ):
        value = kwargs.get(key)
        if value:
            return value

    return None


def ensure_both_id_keys(obj: dict[str, Any], lid: Optional[str]) -> None:
    """Ensure the mapping `obj` contains both `lid` and `lambda_id` keys.

    This is useful when returning data to callers that may expect the
    historical JSON key `lambda_id` while internal logic uses `lid`.
    """
    if lid is None:
        return

    # Canonical short name
    obj.setdefault("lid", lid)

    # Backwards-compatible historical key
    obj.setdefault("lambda_id", lid)


def normalize_output_ids(obj: dict[str, Any]) -> None:
    """Normalize an output mapping so it contains the canonical `lid` key and
    the legacy `lambda_id` key.

    Use this before returning JSON responses so callers receive both keys
    and clients can migrate at their own pace.
    """
    if not obj:
        return

    # If caller supplied 'lambda_id' but not 'lid', populate 'lid'
    if "lid" not in obj and "lambda_id" in obj:
        obj["lid"] = obj["lambda_id"]

    # Ensure legacy key exists for compatibility
    if "lambda_id" not in obj and "lid" in obj:
        obj["lambda_id"] = obj["lid"]
