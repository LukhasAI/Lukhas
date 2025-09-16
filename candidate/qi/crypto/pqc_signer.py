"""Post-quantum cryptographic signer integration with MATRIZ.

This module provides PQC signing capabilities, intended to be backed by the MATRIZ
service. The functionality is controlled by a feature flag.

To enable MATRIZ integration, set the following environment variable:
    ENABLE_MATRIZ_PQC_SIGNER=true

When enabled, this module will attempt to import and use the `matriz_client`.
When disabled (default), it will raise a NotImplementedError on import.
"""
from __future__ import annotations

import os
import warnings

if os.getenv('ENABLE_MATRIZ_PQC_SIGNER', 'false').lower() == 'true':
    try:
        from matriz_client import PQCClient  # type: ignore

        def sign_message(data: bytes) -> dict[str, str]:
            """
            Signs a message using the MATRIZ PQC client.
            NOTE: This is a placeholder and will raise NotImplementedError.
            """
            raise NotImplementedError("MATRIZ client integration is not fully implemented yet.")

        def verify_signature(data: bytes, signature_info: dict[str, str]) -> bool:
            """
            Verifies a signature using the MATRIZ PQC client.
            NOTE: This is a placeholder and will raise NotImplementedError.
            """
            raise NotImplementedError("MATRIZ client integration is not fully implemented yet.")

        def sign_dilithium(data: bytes) -> dict[str, str]:
            """
            Deprecated alias for sign_message.
            """
            warnings.warn(
                "sign_dilithium is deprecated, use sign_message instead",
                DeprecationWarning,
                stacklevel=2
            )
            return sign_message(data)

        __all__ = ['sign_message', 'verify_signature', 'sign_dilithium']

    except ImportError:
        raise NotImplementedError("MATRIZ client not available. Please install it.")
else:
    raise NotImplementedError(
        "PQC signer requires MATRIZ integration. "
        "Set ENABLE_MATRIZ_PQC_SIGNER=true to enable."
    )
