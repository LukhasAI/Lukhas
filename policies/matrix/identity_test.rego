# Matrix Tracks Identity Authorization Tests
# Generated from canonical ΛiD tier_permissions.json

package matrix.authz

# Test basic tier authorization
test_tier_guest_denied {
    not allow with input as {
        "subject": "lukhas:user:test",
        "tier": "guest",
        "tier_num": 0,
        "scopes": ["memoria.read"],
        "contract": {
            "identity": {
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }
        },
        "token": {"exp": 1758898206},
        "env": {"mfa": false, "webauthn_verified": true}
    }
}

test_tier_trusted_allowed {
    allow with input as {
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.read", "memoria.fold"],
        "contract": {
            "identity": {
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }
        },
        "token": {"exp": 1758898206},
        "env": {"mfa": false, "webauthn_verified": true}
    }
}

test_step_up_required {
    not allow with input as {
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.fold"],
        "action": "fold",
        "contract": {
            "identity": {
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.fold"],
                "api_policies": [
                    {"fn": "fold", "requires_step_up": true}
                ]
            }
        },
        "token": {"exp": 1758898206},
        "env": {"mfa": false, "webauthn_verified": true}
    }
}

test_step_up_satisfied {
    allow with input as {
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.fold"],
        "action": "fold",
        "contract": {
            "identity": {
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.fold"],
                "api_policies": [
                    {"fn": "fold", "requires_step_up": true}
                ]
            }
        },
        "token": {"exp": 1758898206},
        "env": {"mfa": true, "webauthn_verified": true}
    }
}

test_expired_token {
    not allow with input as {
        "subject": "lukhas:user:test",
        "tier": "trusted",
        "tier_num": 3,
        "scopes": ["memoria.read"],
        "contract": {
            "identity": {
                "requires_auth": true,
                "required_tiers": ["trusted"],
                "scopes": ["memoria.read"]
            }
        },
        "token": {"exp": 1758891006},
        "env": {"mfa": false, "webauthn_verified": true}
    }
}
