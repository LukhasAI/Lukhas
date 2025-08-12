"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: validate_payload.py
Advanced: validate_payload.py
Integration Date: 2025-05-31T07:55:30.517371
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                LUCΛS :: SCHEMA VALIDATION CLI TOOL                          │
│               Version: v1.0 | Symbolic Payload Verifier (Manual)            │
│     Validate a symbolic payload against message_schema.json from terminal    │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This command-line tool allows a developer to validate any symbolic
    message payload JSON file against the LUCΛS NIAS schema. It prints
    symbolic approval or rejection status with error traces.

"""

import json
import sys

import jsonschema
from jsonschema import validate

SCHEMA_PATH = "core/modules/nias/schemas/message_schema.json"
# ⚠️ Expecting payloads from: core/sample_payloads/


def validate_payload(payload_path):
    try:
        with open(SCHEMA_PATH) as schema_file:
            schema = json.load(schema_file)

        with open(payload_path) as payload_file:
            payload = json.load(payload_file)

        validate(instance=payload, schema=schema)
        print("✅ Symbolic Payload is VALID")
    except jsonschema.exceptions.ValidationError as ve:
        print("❌ Validation FAILED:")
        print(ve)
    except Exception as e:
        print("⚠️  Unexpected error:", str(e))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_payload.py <path_to_payload.json>")
    else:
        validate_payload(sys.argv[1])

"""
──────────────────────────────────────────────────────────────────────────────────────
USAGE:
    From root folder:
        python core/modules/nias/validate_payload.py core/sample_payloads/sample_payload.json

REQUIRES:
    pip install jsonschema

NOTES:
    - Can be extended to support batch validation, LUCΛS dream streaming,
    or symbolic replay
──────────────────────────────────────────────────────────────────────────────────────
"""
