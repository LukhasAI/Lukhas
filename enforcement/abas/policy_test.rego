package abas.authz_test

import data.abas.authz

# Test: Block minors from receiving ads
test_block_minors {
    input := {
        "is_minor": true,
        "targeting_mode": "contextual",
        "region": "US",
        "request": {"body": ""}
    }
    not authz.allow with input as input
    authz.reason == "blocked: minors cannot receive targeted ads" with input as input
}

# Test: Block sensitive signals
test_block_sensitive_signals {
    input := {
        "is_minor": false,
        "using_sensitive_signals": true,
        "targeting_mode": "contextual",
        "region": "US",
        "request": {"body": ""}
    }
    not authz.allow with input as input
    authz.reason == "blocked: sensitive data cannot be used for ads" with input as input
}

# Test: Contextual targeting allowed when safe
test_allow_contextual_safe {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "contextual",
        "region": "US",
        "request": {"body": ""}
    }
    authz.allow with input as input
}

# Test: EU personalized requires TCF consent
test_eu_personalized_requires_tcf {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "personalized",
        "region": "EU",
        "request": {"body": ""},
        "consent": {
            "tcf_present": false
        }
    }
    not authz.allow with input as input
    authz.reason == "blocked: consent missing for personalization (TCF v2.2 P3/P4/P1)" with input as input
}

# Test: EU personalized allowed with valid TCF consent
test_eu_personalized_with_tcf {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "personalized",
        "region": "EU",
        "request": {"body": ""},
        "consent": {
            "tcf_present": true,
            "p3": true,
            "p4": true,
            "storage_p1": true
        }
    }
    authz.allow with input as input
}

# Test: Non-EU personalized allowed without TCF
test_non_eu_personalized_allowed {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "personalized",
        "region": "US",
        "request": {"body": ""}
    }
    authz.allow with input as input
}

# Test: PII detection blocks request
test_pii_blocks_request {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "contextual",
        "region": "US",
        "request": {"body": "I am gay and need support"}
    }
    not authz.allow with input as input
    authz.reason == "blocked: pii detected in request body" with input as input
}

# Test: Contextual with clean body allowed
test_contextual_clean_body {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "targeting_mode": "contextual",
        "region": "US",
        "request": {"body": "Looking for tech news"}
    }
    authz.allow with input as input
}

# Test: Default deny when no targeting mode specified
test_default_deny {
    input := {
        "is_minor": false,
        "using_sensitive_signals": false,
        "region": "US",
        "request": {"body": ""}
    }
    not authz.allow with input as input
    authz.reason == "blocked: default-deny" with input as input
}
