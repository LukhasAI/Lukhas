# Authentication & LucasID Access

## Overview

This module handles symbolic and biometric authentication flows for LUKHAS Cognitive AI agents. It integrates with:
- Lukhas_ID tier management
- Consent logs
- QRGLYMPH visualization
- World ID & retina mark (experimental)

## Key Features

- 🌐 Multi-factor symbolic login (emoji, word-seed, retina prototype)
- 🧠 Tiered access (T0–T5) based on consent_tiers.json and user trace
- 🔏 ZKProof-ready structure for future biometric attestations
- 🌀 Linked to Lukhas' dream registry for reflective access gates

## Path Dependencies

This module works closely with:
- `id_portal/backend/app/tier_manager.py`
- `aid/identity_trace.py`
- `aid/consent_log_writer.py`
- `lukhas_settings.json`
- `lukhas_config.py`

## Developer Notes

- Coming integration: Retina invisible hash (proof of concept under /aid/biometric_auth/)
- Symbolic login feedback is logged in `lukhas_output_log.py`
- Tier 5 unlocks full Cognitive AI symbolic flow including dream publishing, visual glyphs, and voice print.
