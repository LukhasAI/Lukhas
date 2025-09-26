#!/usr/bin/env python3
"""
Tier Macaroon Issuer - Bridge ΛiD system with Matrix Authorization

Issues macaroons as attenuated capability tokens layered atop existing
WebAuthn/JWT authentication. Bridges LUKHAS ΛiD tier system with Matrix
authorization while preserving existing authentication flows.
"""

import json
import time
import hashlib
import secrets
import hmac
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


@dataclass
class ΛiDClaims:
    """ΛiD identity claims from existing authentication system."""
    subject: str  # lukhas:user:handle or lukhas:svc:name
    tier: str     # guest, visitor, friend, trusted, inner_circle, root_dev
    tier_num: int # 0-5 canonical numeric tier
    scopes: List[str]
    exp: int      # expiration timestamp
    iat: int      # issued at
    mfa: bool = False
    webauthn_verified: bool = False
    device_id: Optional[str] = None
    region: Optional[str] = None


class MacaroonError(Exception):
    """Macaroon operation error."""
    pass


class TierMacaroonIssuer:
    """Issues macaroons with ΛiD tier-based caveats."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize with server secret for macaroon signing."""
        if secret_key:
            self.secret_key = secret_key.encode()
        else:
            # Load from environment or config - fallback to derived key
            self.secret_key = self._derive_server_key()

    def _derive_server_key(self) -> bytes:
        """Derive server key from ΛiD configuration if available."""
        try:
            # Try to load from existing ΛiD config
            config_path = Path("candidate/governance/identity/lambda_id_config.yaml")
            if config_path.exists():
                import yaml
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    if 'signing_key' in config:
                        return config['signing_key'].encode()
        except ImportError:
            pass

        # Fallback: generate deterministic key from known system constants
        system_id = "lukhas-matrix-macaroons-v1"
        return hashlib.pbkdf2_hmac('sha256', system_id.encode(), b'lukhas-salt', 100000)

    def _load_tier_permissions(self) -> Dict[str, Any]:
        """Load canonical ΛiD tier permissions for validation."""
        tier_file = Path("candidate/governance/identity/config/tier_permissions.json")
        if not tier_file.exists():
            raise MacaroonError(f"Tier permissions not found at {tier_file}")

        with open(tier_file) as f:
            return json.load(f)

    def _validate_tier_claims(self, claims: ΛiDClaims) -> None:
        """Validate tier claims against canonical ΛiD permissions."""
        permissions = self._load_tier_permissions()
        tier_perms = permissions["tier_permissions"]

        if str(claims.tier_num) not in tier_perms:
            raise MacaroonError(f"Invalid tier number: {claims.tier_num}")

        expected_tier_name = tier_perms[str(claims.tier_num)]["name"].lower().replace(" ", "_").replace("/", "_")
        if claims.tier != expected_tier_name:
            raise MacaroonError(f"Tier name mismatch: {claims.tier} != {expected_tier_name}")

        # Validate rate limits aren't exceeded (advisory)
        limits = tier_perms[str(claims.tier_num)]["rate_limits"]
        max_scopes = limits.get("api_calls_per_minute", 10)
        if len(claims.scopes) > max_scopes:
            raise MacaroonError(f"Too many scopes for tier {claims.tier}: {len(claims.scopes)} > {max_scopes}")

    def issue_capability(
        self,
        claims: ΛiDClaims,
        audience: str,
        ttl_minutes: int = 15,
        additional_caveats: Optional[List[str]] = None
    ) -> str:
        """Issue a capability macaroon with ΛiD tier-based caveats."""

        # Validate against canonical tier system
        self._validate_tier_claims(claims)

        # Create macaroon structure (simplified implementation)
        macaroon_id = f"{claims.subject}:{claims.tier}:{int(time.time())}"
        location = "lukhas-matrix-authz"

        # Base caveats from ΛiD claims
        caveats = [
            f"sub = {claims.subject}",
            f"tier = {claims.tier}",
            f"tier_num = {claims.tier_num}",
            f"scopes = {','.join(claims.scopes)}",
            f"aud = {audience}",
            f"exp = {claims.exp}",
            f"iat = {claims.iat}",
            f"mfa = {claims.mfa}",
            f"webauthn_verified = {claims.webauthn_verified}"
        ]

        # Add optional contextual caveats
        if claims.device_id:
            caveats.append(f"device_id = {claims.device_id}")
        if claims.region:
            caveats.append(f"region = {claims.region}")

        # Add additional caveats
        if additional_caveats:
            caveats.extend(additional_caveats)

        # Create simplified macaroon structure
        macaroon_data = {
            "version": 2,
            "location": location,
            "identifier": macaroon_id,
            "caveats": caveats,
            "signature": self._compute_signature(macaroon_id, caveats)
        }

        # Return base64-encoded macaroon
        macaroon_json = json.dumps(macaroon_data, separators=(',', ':'))
        return self._encode_macaroon(macaroon_json)

    def _compute_signature(self, identifier: str, caveats: List[str]) -> str:
        """Compute HMAC signature for macaroon."""
        payload = identifier + '|' + '|'.join(sorted(caveats))
        signature = hmac.new(self.secret_key, payload.encode(), hashlib.sha256).hexdigest()
        return signature

    def _encode_macaroon(self, macaroon_json: str) -> str:
        """Encode macaroon as base64 token."""
        import base64
        return base64.b64encode(macaroon_json.encode()).decode()

    def issue_from_jwt(
        self,
        jwt_token: str,
        audience: str,
        ttl_minutes: int = 15,
        additional_scopes: Optional[List[str]] = None
    ) -> str:
        """Issue macaroon from existing JWT token (bridge existing auth)."""

        # In production, this would validate JWT against existing system
        # For now, create mock claims structure
        try:
            # This would integrate with existing JWT validation
            # from candidate/governance/identity/auth_web/jwt.ts
            claims = self._extract_claims_from_jwt(jwt_token)

            # Add additional scopes if provided
            if additional_scopes:
                claims.scopes.extend(additional_scopes)

            return self.issue_capability(claims, audience, ttl_minutes)

        except Exception as e:
            raise MacaroonError(f"Failed to issue macaroon from JWT: {e}")

    def _extract_claims_from_jwt(self, jwt_token: str) -> ΛiDClaims:
        """Extract ΛiD claims from existing JWT token."""
        # This would integrate with existing JWT verification
        # For now, return mock claims structure
        now = int(time.time())
        return ΛiDClaims(
            subject="lukhas:user:test",
            tier="trusted",
            tier_num=3,
            scopes=["memoria.read", "memoria.fold"],
            exp=now + 3600,
            iat=now,
            mfa=False,
            webauthn_verified=True,
            device_id="device_123",
            region="us-west-2"
        )


class TierMacaroonVerifier:
    """Verifies macaroons and extracts normalized claims for OPA."""

    def __init__(self, secret_key: Optional[str] = None):
        """Initialize with same server secret as issuer."""
        if secret_key:
            self.secret_key = secret_key.encode()
        else:
            # Must match issuer secret derivation
            issuer = TierMacaroonIssuer()
            self.secret_key = issuer.secret_key

    def verify_capability(self, macaroon_token: str) -> Dict[str, Any]:
        """Verify macaroon and return normalized claims for OPA input."""

        try:
            # Decode macaroon
            macaroon_json = self._decode_macaroon(macaroon_token)
            macaroon_data = json.loads(macaroon_json)

            # Verify signature
            identifier = macaroon_data["identifier"]
            caveats = macaroon_data["caveats"]
            signature = macaroon_data["signature"]

            expected_signature = self._compute_signature(identifier, caveats)
            if not hmac.compare_digest(signature, expected_signature):
                raise MacaroonError("Invalid macaroon signature")

            # Parse caveats into normalized claims
            claims = self._parse_caveats(caveats)

            # Validate expiration
            if time.time() > claims["exp"]:
                raise MacaroonError("Macaroon expired")

            # Return OPA-compatible input structure
            return {
                "valid": True,
                "subject": claims["sub"],
                "tier": claims["tier"],
                "tier_num": claims["tier_num"],
                "scopes": claims["scopes"].split(",") if claims["scopes"] else [],
                "audience": claims["aud"],
                "token": {
                    "exp": claims["exp"],
                    "iat": claims["iat"]
                },
                "env": {
                    "mfa": claims.get("mfa", False),
                    "webauthn_verified": claims.get("webauthn_verified", False),
                    "device_id": claims.get("device_id"),
                    "region": claims.get("region")
                },
                "capability_id": identifier
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def _decode_macaroon(self, token: str) -> str:
        """Decode base64 macaroon token."""
        import base64
        return base64.b64decode(token).decode()

    def _compute_signature(self, identifier: str, caveats: List[str]) -> str:
        """Compute HMAC signature for verification."""
        payload = identifier + '|' + '|'.join(sorted(caveats))
        signature = hmac.new(self.secret_key, payload.encode(), hashlib.sha256).hexdigest()
        return signature

    def _parse_caveats(self, caveats: List[str]) -> Dict[str, Any]:
        """Parse macaroon caveats into claims dict."""
        claims = {}
        for caveat in caveats:
            if " = " in caveat:
                key, value = caveat.split(" = ", 1)
                # Type conversion
                if key in ["tier_num", "exp", "iat"]:
                    claims[key] = int(value)
                elif key in ["mfa", "webauthn_verified"]:
                    claims[key] = value.lower() == "true"
                else:
                    claims[key] = value
        return claims


def main():
    """CLI for issuing and verifying tier-based macaroons."""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Tier Macaroon Issuer/Verifier")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Issue command
    issue_parser = subparsers.add_parser("issue", help="Issue a macaroon")
    issue_parser.add_argument("--subject", required=True, help="Subject (lukhas:user:handle)")
    issue_parser.add_argument("--tier", required=True,
                             choices=["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"],
                             help="ΛiD tier")
    issue_parser.add_argument("--scopes", required=True, help="Comma-separated scopes")
    issue_parser.add_argument("--audience", required=True, help="Target audience")
    issue_parser.add_argument("--ttl", type=int, default=15, help="TTL in minutes")
    issue_parser.add_argument("--mfa", action="store_true", help="MFA verified")
    issue_parser.add_argument("--webauthn", action="store_true", help="WebAuthn verified")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a macaroon")
    verify_parser.add_argument("token", help="Macaroon token to verify")

    args = parser.parse_args()

    if args.command == "issue":
        # Map tier name to numeric
        tier_map = {
            "guest": 0, "visitor": 1, "friend": 2,
            "trusted": 3, "inner_circle": 4, "root_dev": 5
        }

        now = int(time.time())
        claims = ΛiDClaims(
            subject=args.subject,
            tier=args.tier,
            tier_num=tier_map[args.tier],
            scopes=args.scopes.split(","),
            exp=now + (args.ttl * 60),
            iat=now,
            mfa=args.mfa,
            webauthn_verified=args.webauthn
        )

        issuer = TierMacaroonIssuer()
        try:
            token = issuer.issue_capability(claims, args.audience, args.ttl)
            print(f"Issued macaroon: {token}")
        except MacaroonError as e:
            print(f"Error: {e}")

    elif args.command == "verify":
        verifier = TierMacaroonVerifier()
        result = verifier.verify_capability(args.token)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()