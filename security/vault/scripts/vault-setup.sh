#!/bin/bash
# Setup Vault for LUKHAS
vault policy write lukhas-identity-policy ./policies/lukhas-identity-policy.hcl
vault policy write consciousness-secrets-policy ./policies/consciousness-secrets-policy.hcl
vault policy write agent-communication-policy ./policies/agent-communication-policy.hcl
