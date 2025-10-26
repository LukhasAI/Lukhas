"""Adapters namespace (compatibility shim).

Historically, OpenAI-compatible API lived under `lukhas/adapters/openai/api.py`.
The implementation has moved to `serve/`, but CI and docs still reference the
old import path. This package preserves that entrypoint without duplicating
implementation.
"""

__all__ = []

