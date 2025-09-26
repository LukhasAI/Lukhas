# Matrix Tracks Identity Authorization Policy
# Generated from canonical ΛiD tier_permissions.json
# DO NOT EDIT - Run tools/tier_opa_generator.py to regenerate
#
# Generated: 2025-09-26T13:50:06.224306+00:00
# Permissions checksum: 1e412bb5c069c6f07af04bd86cd0829e79dda8b3603df8c07526fdf094ca91b9

package matrix.authz

default allow = false

# Canonical tier mappings (generated from ΛiD system)
tier_names := ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
tier_rank := {
    "guest": 0,
    "visitor": 1,
    "friend": 2,
    "trusted": 3,
    "inner_circle": 4,
    "root_dev": 5
}

# Rate limits per tier (requests per minute)
tier_rate_limits := {
  "guest": {
    "generation_per_hour": 5,
    "api_calls_per_minute": 10
  },
  "visitor": {
    "generation_per_hour": 10,
    "api_calls_per_minute": 20
  },
  "friend": {
    "generation_per_hour": 25,
    "api_calls_per_minute": 50
  },
  "trusted": {
    "generation_per_hour": 50,
    "api_calls_per_minute": 100
  },
  "inner_circle": {
    "generation_per_hour": 100,
    "api_calls_per_minute": 200
  },
  "root_dev": {
    "generation_per_hour": 1000,
    "api_calls_per_minute": 1000
  }
}

# Feature flags per tier
tier_features := {
  "guest": {
    "api_access": "read_only",
    "biometric_auth": false,
    "multi_device_sync": false
  },
  "visitor": {
    "api_access": "basic",
    "biometric_auth": false,
    "multi_device_sync": false
  },
  "friend": {
    "api_access": "standard",
    "biometric_auth": false,
    "multi_device_sync": true
  },
  "trusted": {
    "api_access": "advanced",
    "biometric_auth": true,
    "multi_device_sync": true
  },
  "inner_circle": {
    "api_access": "premium",
    "biometric_auth": true,
    "multi_device_sync": true
  },
  "root_dev": {
    "api_access": "enterprise",
    "biometric_auth": true,
    "multi_device_sync": true
  }
}

# Contract-level authorization checks
contract_ok {
    not input.contract.identity.requires_auth == false
    subject_ok
    tier_ok
    scopes_ok
    api_policy_ok
}

subject_ok {
    pats := input.contract.identity.accepted_subjects
    pats == []  # empty means any authenticated ΛiD subject
} {
    # Check exact match first (for specific service accounts)
    input.subject in input.contract.identity.accepted_subjects
} {
    # Check wildcard patterns
    some p
    p := input.contract.identity.accepted_subjects[_]
    endswith(p, "*")
    prefix := trim_right(p, "*")
    startswith(input.subject, prefix)
}

tier_ok {
    # Accept either textual tiers or numeric list (dual compatibility)
    t := input.tier
    reqt := input.contract.identity.required_tiers
    reqn := input.contract.identity.required_tiers_numeric

    reqt == []  # no tier requirement
    reqn == []
} {
    reqt != []
    tier_match_text(t, reqt)
} {
    reqn != []
    tier_match_num(input.tier_num, reqn)
}

tier_match_text(t, req) {
    some r
    r := req[_]
    t == r
}

tier_match_num(n, reqn) {
    some r
    r := reqn[_]
    n == r
}

scopes_ok {
    need := input.contract.identity.scopes
    need == []
} {
    all_scopes_present(need, input.scopes)
}

api_policy_ok {
    apis := {p.fn: p | p := input.contract.identity.api_policies[_]}
    not input.action in apis
} {
    step_up_ok(apis[input.action])
}

step_up_ok(p) {
    not p.requires_step_up
} {
    input.env.mfa == true
}

all_scopes_present(need, have) {
    count(need) == count({ n | n := need[_]; n in have })
}

# Time-based token validation
token_valid {
    time.now_ns() < input.token.exp * 1000000000
    audience_valid
}

# Audience validation
audience_valid {
    input.token.aud == "lukhas-matrix"
}

# Rate limiting check (advisory - gateway should enforce)
rate_limit_ok {
    tier := input.tier
    tier in tier_rate_limits
    # Rate limit logic would be enforced by gateway middleware
    # This is just policy validation
    true
}

# WebAuthn requirement check
webauthn_ok {
    not input.contract.identity.webauthn_required
} {
    input.env.webauthn_verified == true
}

# Main authorization decision
allow {
    contract_ok
    token_valid
    webauthn_ok
    rate_limit_ok
}

# Additional metadata for telemetry
decision_metadata := {
    "policy_version": "1.0.0",
    "policy_checksum": "1e412bb5c069c6f07af04bd86cd0829e79dda8b3603df8c07526fdf094ca91b9",
    "tier_numeric": tier_rank[input.tier],
    "rate_limit": tier_rate_limits[input.tier],
    "features": tier_features[input.tier],
    "timestamp": time.now_ns()
}
