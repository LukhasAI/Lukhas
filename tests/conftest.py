"""Testing utilities and lightweight stubs for missing third-party deps."""

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import types
import warnings
from typing import Any, Dict, List, Optional, Union

os.environ.setdefault("LUKHAS_SUPPRESS_MATRIZ_COMPAT_WARNING", "1")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="matriz")


def _install_jwt_stub() -> None:
    jwt_module = types.ModuleType("jwt")

    class ExpiredSignatureError(Exception):
        pass

    class InvalidAudienceError(Exception):
        pass

    class InvalidIssuerError(Exception):
        pass

    class InvalidSignatureError(Exception):
        pass

    class DecodeError(Exception):
        pass

    def _b64encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

    def _b64decode(segment: str) -> bytes:
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode(segment + padding)

    def encode(payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
        if algorithm not in {"HS256", "HS512", "RS256", "RS512"}:
            raise DecodeError(f"Unsupported algorithm: {algorithm}")

        header = {"alg": "HS256", "typ": "JWT"}
        header_segment = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_segment = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

        signing_input = f"{header_segment}.{payload_segment}".encode()
        signature = hmac.new(key.encode("utf-8"), signing_input, hashlib.sha256).digest()
        signature_segment = _b64encode(signature)
        return f"{header_segment}.{payload_segment}.{signature_segment}"

    def decode(
        token: str,
        key: Optional[str] = None,
        algorithms: Optional[List[str]] = None,
        issuer: Optional[str] = None,
        audience: Optional[Union[str, List[str]]] = None,
        leeway: int = 0,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        options = options or {}
        verify_signature = options.get("verify_signature", True)
        verify_exp = options.get("verify_exp", True)
        verify_nbf = options.get("verify_nbf", True)
        verify_iat = options.get("verify_iat", True)
        verify_aud = options.get("verify_aud", True)
        verify_iss = options.get("verify_iss", True)

        try:
            header_segment, payload_segment, signature_segment = token.split(".")
        except ValueError as exc:
            raise DecodeError("Invalid token format") from exc

        header = json.loads(_b64decode(header_segment))
        payload = json.loads(_b64decode(payload_segment))

        algorithm = header.get("alg", "HS256")
        if algorithms and algorithm not in algorithms:
            raise DecodeError("Algorithm not allowed")

        if verify_signature:
            if key is None:
                raise DecodeError("Key required for verification")
            signing_input = f"{header_segment}.{payload_segment}".encode()
            expected_sig = hmac.new(key.encode("utf-8"), signing_input, hashlib.sha256).digest()
            if not hmac.compare_digest(expected_sig, _b64decode(signature_segment)):
                raise InvalidSignatureError("Signature mismatch")

        now = int(time.time())
        exp = int(payload.get("exp", now + 1))
        nbf = int(payload.get("nbf", now - 1))
        iat = int(payload.get("iat", now))

        if verify_exp and now - leeway > exp:
            raise ExpiredSignatureError("Token expired")
        if verify_nbf and now + leeway < nbf:
            raise DecodeError("Token not yet valid")
        if verify_iat and iat - leeway > now:
            raise DecodeError("Token issued in the future")

        if verify_iss and issuer and payload.get("iss") != issuer:
            raise InvalidIssuerError("Invalid issuer")

        if verify_aud and audience:
            token_aud = payload.get("aud")
            if isinstance(audience, list):
                valid = token_aud in audience if isinstance(token_aud, str) else bool(set(audience) & set(token_aud or []))
            else:
                if isinstance(token_aud, list):
                    valid = audience in token_aud
                else:
                    valid = token_aud == audience
            if not valid:
                raise InvalidAudienceError("Invalid audience")

        return payload

    jwt_module.encode = encode
    jwt_module.decode = decode
    jwt_module.ExpiredSignatureError = ExpiredSignatureError
    jwt_module.InvalidAudienceError = InvalidAudienceError
    jwt_module.InvalidIssuerError = InvalidIssuerError
    jwt_module.InvalidSignatureError = InvalidSignatureError
    jwt_module.DecodeError = DecodeError

    sys.modules.setdefault("jwt", jwt_module)


def _install_yaml_stub() -> None:
    yaml_module = types.ModuleType("yaml")

    def safe_load(data: str) -> Any:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {}

    yaml_module.safe_load = safe_load

    sys.modules.setdefault("yaml", yaml_module)


_install_jwt_stub()
_install_yaml_stub()


# Pytest skip helpers for optional dependencies
import pytest

# Check if labs is available
try:
    import importlib
    importlib.import_module("labs")
    LABS_AVAILABLE = True
except ImportError:
    LABS_AVAILABLE = False

# Skip decorator for tests requiring labs
requires_labs = pytest.mark.skipif(
    not LABS_AVAILABLE,
    reason="labs not installed - skipping labs-dependent test"
)
