# Matrix Tracks Identity Authorization Policy
# Generated from canonical ΛiD tier_permissions.json
# DO NOT EDIT - Run tools/tier_opa_generator.py to regenerate
#
# Generated: 2025-09-26T13:50:06.224306+00:00
# Permissions checksum: 1e412bb5c069c6f07af04bd86cd0829e79dda8b3603df8c07526fdf094ca91b9

package matrix.authz

default allow := false

# Canonical tier mappings (generated from ΛiD system)
tier_names := ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
tier_rank := {
	"guest": 0,
	"visitor": 1,
	"friend": 2,
	"trusted": 3,
	"inner_circle": 4,
	"root_dev": 5,
}

# Rate limits per tier (requests per minute)
tier_rate_limits := {
	"guest": {
		"generation_per_hour": 5,
		"api_calls_per_minute": 10,
	},
	"visitor": {
		"generation_per_hour": 10,
		"api_calls_per_minute": 20,
	},
	"friend": {
		"generation_per_hour": 25,
		"api_calls_per_minute": 50,
	},
	"trusted": {
		"generation_per_hour": 50,
		"api_calls_per_minute": 100,
	},
	"inner_circle": {
		"generation_per_hour": 100,
		"api_calls_per_minute": 200,
	},
	"root_dev": {
		"generation_per_hour": 1000,
		"api_calls_per_minute": 1000,
	},
}

# Feature flags per tier
tier_features := {
	"guest": {
		"api_access": "read_only",
		"biometric_auth": false,
		"multi_device_sync": false,
	},
	"visitor": {
		"api_access": "basic",
		"biometric_auth": false,
		"multi_device_sync": false,
	},
	"friend": {
		"api_access": "standard",
		"biometric_auth": false,
		"multi_device_sync": true,
	},
	"trusted": {
		"api_access": "advanced",
		"biometric_auth": true,
		"multi_device_sync": true,
	},
	"inner_circle": {
		"api_access": "premium",
		"biometric_auth": true,
		"multi_device_sync": true,
	},
	"root_dev": {
		"api_access": "enterprise",
		"biometric_auth": true,
		"multi_device_sync": true,
	},
}

# Contract-level authorization checks
contract_ok if {
	not input.contract.identity.requires_auth == false
	subject_ok
	tier_ok
	scopes_ok
	api_policy_ok
}

subject_ok if {
	# If accepted_subjects not defined or empty, allow any authenticated subject
	not input.contract.identity.accepted_subjects
}

subject_ok if {
	pats := input.contract.identity.accepted_subjects
	pats == [] # empty means any authenticated ΛiD subject
}

subject_ok if {
	# Check exact match first (for specific service accounts)
	input.subject in input.contract.identity.accepted_subjects
}

subject_ok if {
	# Check wildcard patterns
	some pat in input.contract.identity.accepted_subjects
	endswith(pat, "*")
	prefix := trim_right(pat, "*")
	startswith(input.subject, prefix)
}

tier_ok if {
	# Accept either textual tiers or numeric list (dual compatibility)
	t := input.tier
	reqt := input.contract.identity.required_tiers
	reqn := input.contract.identity.required_tiers_numeric

	reqt == [] # no tier requirement
	reqn == []
}

tier_ok if {
	reqt := input.contract.identity.required_tiers
	t := input.tier
	reqt != []
	tier_match_text(t, reqt)
}

tier_ok if {
	reqn := input.contract.identity.required_tiers_numeric
	reqn != []
	tier_match_num(input.tier_num, reqn)
}

tier_match_text(t, req) if {
	some rt in req
	t == rt
}

tier_match_num(n, reqn) if {
	some rn in reqn
	n == rn
}

scopes_ok if {
	need := input.contract.identity.scopes
	need == []
}

scopes_ok if {
	need := input.contract.identity.scopes
	need != []
	all_scopes_present(need, input.scopes)
}

api_policy_ok if {
	not input.contract.identity.api_policies # No api_policies defined
}

api_policy_ok if {
	not input.action # No action specified
}

api_policy_ok if {
	apis := {p.fn: p | p := input.contract.identity.api_policies[_]}
	input.action # Action is defined
	not input.action in apis # But it's not in api_policies
}

api_policy_ok if {
	apis := {p.fn: p | p := input.contract.identity.api_policies[_]}
	input.action in apis
	step_up_ok(apis[input.action])
}

step_up_ok(p) if {
	not p.requires_step_up
}

step_up_ok(p) if {
	input.env.mfa == true
}

all_scopes_present(need, have) if {
	count(need) == count({n | n := need[_]; n in have})
}

# Time-based token validation
token_valid if {
	time.now_ns() < input.token.exp * 1000000000
	audience_valid
}

# Audience validation
audience_valid if {
	not input.token.aud # No audience field, allow
}

audience_valid if {
	input.token.aud == "lukhas-matrix"
}

# Rate limiting check (advisory - gateway should enforce)
rate_limit_ok if {
	not input.tier # No tier specified
}

rate_limit_ok if {
	tier := input.tier
	tier in tier_rate_limits

	# Rate limit logic would be enforced by gateway middleware
	# This is just policy validation
	true
}

rate_limit_ok if {
	tier := input.tier
	not tier in tier_rate_limits # Unknown tier, allow
}

# WebAuthn requirement check
webauthn_ok if {
	not input.contract.identity.webauthn_required
}

webauthn_ok if {
	input.env.webauthn_verified == true
}

# Main authorization decision
allow if {
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
	"timestamp": time.now_ns(),
}
