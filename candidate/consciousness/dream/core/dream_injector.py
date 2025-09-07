"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUCΛS :: DREAM INJECTOR & BATCH VALIDATOR                │
│                Version: v1.0 | NIAS Symbolic Flow + Schema Runner           │
│     Validates multiple payloads and simulates dream fallback scenarios       │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This utility scans a folder for symbolic payloads (.json), validates
    them against the NIAS schema, and simulates delivery or dream fallback.
    It logs outcomes per message: DELIVERED | DREAM | REJECTED

"""
import streamlit as st

import json
import os

import jsonschema
from jsonschema import validate

try:
    from candidate.core.modules.nias.dream_recorder import record_dream_message
except ImportError:
    # Create a placeholder if the module doesn't exist
    def record_dream_message(*args, **kwargs):
        return {"status": "recorded", "message": "placeholder_recording"}


SCHEMA_PATH = "core/modules/nias/schemas/message_schema.json"
PAYLOADS_DIR = "core/sample_payloads/"
DELIVERED, DREAMED, REJECTED = [], [], []


def process_payload(file_path, schema):
    with open(file_path) as f:
        payload = json.load(f)
    try:
        validate(instance=payload, schema=schema)
        if payload.get("required_tier", 0) > 3:
            REJECTED.append((payload["message_id"], "Tier too high"))
        elif payload.get("dream_fallback", False):
            record_dream_message(payload)
            DREAMED.append(payload["message_id"])
        else:
            DELIVERED.append(payload["message_id"])
    except jsonschema.exceptions.ValidationError as e:
        REJECTED.append((os.path.basename(file_path), str(e).splitlines()[0]))


def run_batch_validation():
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    for filename in os.listdir(PAYLOADS_DIR):
        if filename.endswith(".json") and filename.startswith("sample_payload"):
            file_path = os.path.join(PAYLOADS_DIR, filename)
            process_payload(file_path, schema)

    print("\n🧠 SYMBOLIC BATCH SUMMARY")
    print("-----------------------------")
    print(f"✅ Delivered: {len(DELIVERED} → {DELIVERED}")
    print(f"🌙 Dreamed: {len(DREAMED} → {DREAMED}")
    print(f"❌ Rejected: {len(REJECTED} → {REJECTED}")


if __name__ == "__main__":
    run_batch_validation()

"""
──────────────────────────────────────────────────────────────────────────────────────
EXECUTION:
    Run from repo root:
        python core/modules/nias/dream_injector.py

REQUIRES:
    pip install jsonschema

NOTES:
    - Extend to auto-tag dream archive or generate feedback traces
    - May later interface with dream_recorder or lukhas_voice modules
──────────────────────────────────────────────────────────────────────────────────────
"""
