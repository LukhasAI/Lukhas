#!/usr/bin/env python3
"""
Tier Permissions to OPA Generator

Generates OPA Rego bundle from canonical ΛiD tier_permissions.json to ensure
single source of truth. Never hand-maintain policy constants - always generate.

This bridges the existing LUKHAS ΛiD tier system with Matrix Tracks authorization.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def load_tier_permissions() -> Dict[str, Any]:
    """Load canonical ΛiD tier permissions."""
    tier_file = Path("candidate/governance/identity/config/tier_permissions.json")

    if not tier_file.exists():
        raise FileNotFoundError(f"Canonical tier permissions not found at {tier_file}")

    with open(tier_file) as f:
        return json.load(f)


def calculate_permissions_checksum(permissions: Dict[str, Any]) -> str:
    """Calculate SHA256 checksum of tier permissions for policy validation."""
    canonical_json = json.dumps(permissions, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def generate_rego_bundle(permissions: Dict[str, Any]) -> str:
    """Generate OPA Rego bundle from ΛiD tier permissions."""

    tier_permissions = permissions["tier_permissions"]
    permissions["validation_rules"]

    # Extract tier mappings
    tier_names = []
    tier_numeric = []
    tier_rate_limits = {}
    tier_features = {}

    for tier_num, tier_data in tier_permissions.items():
        tier_name = tier_data["name"].lower().replace(" ", "_").replace("/", "_")
        tier_names.append(f'"{tier_name}"')
        tier_numeric.append(int(tier_num))

        # Rate limits per tier
        limits = tier_data["rate_limits"]
        tier_rate_limits[tier_name] = {
            "generation_per_hour": limits.get("generation_per_hour", 0),
            "api_calls_per_minute": limits.get("api_calls_per_minute", 0)
        }

        # Feature flags per tier
        features = tier_data["features"]
        tier_features[tier_name] = {
            "api_access": features.get("api_access", "read_only"),
            "biometric_auth": features.get("biometric_auth", False),
            "multi_device_sync": features.get("multi_device_sync", False)
        }

    checksum = calculate_permissions_checksum(permissions)
    timestamp = datetime.now(timezone.utc).isoformat()

    rego_content = f'''# Matrix Tracks Identity Authorization Policy
# Generated from canonical ΛiD tier_permissions.json
# DO NOT EDIT - Run tools/tier_opa_generator.py to regenerate
#
# Generated: {timestamp}
# Permissions checksum: {checksum}

package matrix.authz

default allow = false

# Canonical tier mappings (generated from ΛiD system)
tier_names := [{', '.join(tier_names)}]
tier_rank := {{
    "guest": 0,
    "visitor": 1,
    "friend": 2,
    "trusted": 3,
    "inner_circle": 4,
    "root_dev": 5
}}

# Rate limits per tier (requests per minute)
tier_rate_limits := {json.dumps(tier_rate_limits, indent=2)}

# Feature flags per tier
tier_features := {json.dumps(tier_features, indent=2)}

# Contract-level authorization checks
contract_ok {{
    not input.contract.identity.requires_auth == false
    subject_ok
    tier_ok
    scopes_ok
    api_policy_ok
}}

subject_ok {{
    pats := input.contract.identity.accepted_subjects
    pats == []  # empty means any authenticated ΛiD subject
}} {{
    # Check exact match first (for specific service accounts)
    input.subject in input.contract.identity.accepted_subjects
}} {{
    # Check wildcard patterns
    some p
    p := input.contract.identity.accepted_subjects[_]
    endswith(p, "*")
    prefix := trim_right(p, "*")
    startswith(input.subject, prefix)
}}

tier_ok {{
    # Accept either textual tiers or numeric list (dual compatibility)
    t := input.tier
    reqt := input.contract.identity.required_tiers
    reqn := input.contract.identity.required_tiers_numeric

    reqt == []  # no tier requirement
    reqn == []
}} {{
    reqt != []
    tier_match_text(t, reqt)
}} {{
    reqn != []
    tier_match_num(input.tier_num, reqn)
}}

tier_match_text(t, req) {{
    some r
    r := req[_]
    t == r
}}

tier_match_num(n, reqn) {{
    some r
    r := reqn[_]
    n == r
}}

scopes_ok {{
    need := input.contract.identity.scopes
    need == []
}} {{
    all_scopes_present(need, input.scopes)
}}

api_policy_ok {{
    apis := {{p.fn: p | p := input.contract.identity.api_policies[_]}}
    not input.action in apis
}} {{
    step_up_ok(apis[input.action])
}}

step_up_ok(p) {{
    not p.requires_step_up
}} {{
    input.env.mfa == true
}}

all_scopes_present(need, have) {{
    count(need) == count({{ n | n := need[_]; n in have }})
}}

# Time-based token validation
token_valid {{
    time.now_ns() < input.token.exp * 1000000000
    audience_valid
}}

# Audience validation
audience_valid {{
    input.token.aud == "lukhas-matrix"
}}

# Rate limiting check (advisory - gateway should enforce)
rate_limit_ok {{
    tier := input.tier
    tier in tier_rate_limits
    # Rate limit logic would be enforced by gateway middleware
    # This is just policy validation
    true
}}

# WebAuthn requirement check
webauthn_ok {{
    not input.contract.identity.webauthn_required
}} {{
    input.env.webauthn_verified == true
}}

# Main authorization decision
allow {{
    contract_ok
    token_valid
    webauthn_ok
    rate_limit_ok
}}

# Additional metadata for telemetry
decision_metadata := {{
    "policy_version": "{permissions["tier_system"]["version"]}",
    "policy_checksum": "{checksum}",
    "tier_numeric": tier_rank[input.tier],
    "rate_limit": tier_rate_limits[input.tier],
    "features": tier_features[input.tier],
    "timestamp": time.now_ns()
}}
'''

    return rego_content


def generate_test_fixtures(permissions: Dict[str, Any]) -> str:
    """Generate OPA test fixtures from tier permissions."""

    test_content = f'''# Matrix Tracks Identity Authorization Tests
# Generated from canonical ΛiD tier_permissions.json

package matrix.authz

# Test basic tier authorization
test_tier_guest_denied {{
    not allow with input as {{
        "subject": "lukhas:user:test",
        "tier": "guest",
        "tier_num": 0,
        "scopes": ["memoria.read"],
        "contract": {{
            "identity": {{
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }}
        }},
        "token": {{"exp": {int(datetime.now(timezone.utc).timestamp()) + 3600}}},
        "env": {{"mfa": false, "webauthn_verified": true}}
    }}
}}

test_tier_trusted_allowed {{
    allow with input as {{
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.read", "memoria.fold"],
        "contract": {{
            "identity": {{
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }}
        }},
        "token": {{"exp": {int(datetime.now(timezone.utc).timestamp()) + 3600}}},
        "env": {{"mfa": false, "webauthn_verified": true}}
    }}
}}

test_step_up_required {{
    not allow with input as {{
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.fold"],
        "action": "fold",
        "contract": {{
            "identity": {{
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.fold"],
                "api_policies": [
                    {{"fn": "fold", "requires_step_up": true}}
                ]
            }}
        }},
        "token": {{"exp": {int(datetime.now(timezone.utc).timestamp()) + 3600}}},
        "env": {{"mfa": false, "webauthn_verified": true}}
    }}
}}

test_step_up_satisfied {{
    allow with input as {{
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.fold"],
        "action": "fold",
        "contract": {{
            "identity": {{
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.fold"],
                "api_policies": [
                    {{"fn": "fold", "requires_step_up": true}}
                ]
            }}
        }},
        "token": {{"exp": {int(datetime.now(timezone.utc).timestamp()) + 3600}}},
        "env": {{"mfa": true, "webauthn_verified": true}}
    }}
}}

test_expired_token {{
    not allow with input as {{
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.read"],
        "contract": {{
            "identity": {{
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }}
        }},
        "token": {{"exp": {int(datetime.now(timezone.utc).timestamp()) - 3600}}},
        "env": {{"mfa": false, "webauthn_verified": true}}
    }}
}}
'''

    return test_content


def main():
    """Generate OPA bundle and tests from canonical ΛiD tier permissions."""
    print("🔧 Generating OPA bundle from ΛiD tier permissions...")

    # Load canonical tier permissions
    permissions = load_tier_permissions()
    checksum = calculate_permissions_checksum(permissions)

    # Create policies directory
    policies_dir = Path("policies/matrix")
    policies_dir.mkdir(parents=True, exist_ok=True)

    # Generate main policy
    rego_content = generate_rego_bundle(permissions)
    policy_file = policies_dir / "identity.rego"
    policy_file.write_text(rego_content)

    # Generate tests
    test_content = generate_test_fixtures(permissions)
    test_file = policies_dir / "identity_test.rego"
    test_file.write_text(test_content)

    # Generate checksum file for CI validation
    checksum_file = policies_dir / "permissions.checksum"
    checksum_file.write_text(f"{checksum}\\n")

    print("✅ Generated OPA bundle:")
    print(f"   Policy: {policy_file}")
    print(f"   Tests: {test_file}")
    print(f"   Checksum: {checksum}")
    print(f"   Tier mappings: {list(permissions['tier_permissions'].keys())}")

    # Validate generated Rego syntax
    try:
        import subprocess
        result = subprocess.run(
            ["opa", "fmt", str(policy_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Generated Rego syntax is valid")
        else:
            print(f"⚠️ Rego syntax warning: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("ℹ️ OPA not available for syntax validation (install with: brew install open-policy-agent/tap/opa)")


if __name__ == "__main__":
    main()
