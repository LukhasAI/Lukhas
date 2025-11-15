package abas.authz

import data.abas.pii_detection

default allow = false
default reason = "default-deny"

# Block flags
block_minors {
  input.is_minor == true
}

block_sensitive {
  input.using_sensitive_signals == true
}

# PII deny integration
deny_pii {
  input.request.body != null
  act := data.abas.pii_detection.pii_action with input as input
  act.action == "deny"
}

# Legal basis: EU requires explicit TCF v2.2 consent for personalization
legal_basis_eu {
  input.region == "EU"
  input.consent.tcf_present == true
  input.consent.p3 == true
  input.consent.p4 == true
  input.consent.storage_p1 == true
}

legal_basis_non_eu {
  input.region != "EU"
  not block_minors
  not block_sensitive
}

# Contextual allowed in general if not minors/sensitive and no PII deny
allow {
  input.targeting_mode == "contextual"
  not block_minors
  not block_sensitive
  not deny_pii
}

# Personalized allowed only with legal basis and no PII deny
allow {
  input.targeting_mode == "personalized"
  not block_minors
  not block_sensitive
  (legal_basis_eu or legal_basis_non_eu)
  not deny_pii
}

# Denial messages
cond_msg = "blocked: minors cannot receive targeted ads" {
  block_minors
}

cond_msg = "blocked: sensitive data cannot be used for ads" {
  block_sensitive
}

cond_msg = "blocked: pii detected in request body" {
  deny_pii
}

cond_msg = "blocked: consent missing for personalization (TCF v2.2 P3/P4/P1)" {
  input.region == "EU"
  not legal_basis_eu
}

cond_msg = "blocked: default-deny" {
  true
}

reason := cond_msg {
  not allow
}
