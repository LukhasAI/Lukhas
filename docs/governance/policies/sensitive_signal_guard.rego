package matriz.governance

default allow = false

allow {
  input.signal_type == "memory.personal"
  valid_attestation
  input.tier >= 5
}

valid_attestation {
  # Placeholder; wire to GLYMPH verifier.
  input.attestation.signature != ""
}
