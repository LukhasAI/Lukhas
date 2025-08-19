{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "lukhas://schemas/matriz_node_v1.json",
  "title": "MATADA Node v1 (schema v1.1)",
  "type": "object",
  "additionalProperties": false,
  "required": ["version", "id", "type", "state", "timestamps", "provenance"],
  "properties": {
    "version": { "type": "integer", "const": 1 },
    "id": {
      "type": "string",
      "minLength": 3,
      "maxLength": 128,
      "description": "Stable node identifier such as LT-<trace>#N<index> or UUID"
    },
    "type": {
      "type": "string",
      "enum": [
        "SENSORY_IMG","SENSORY_AUD","SENSORY_VID","SENSORY_TOUCH",
        "EMOTION","INTENT","DECISION","CONTEXT","MEMORY","REFLECTION",
        "CAUSAL","TEMPORAL","AWARENESS","HYPOTHESIS","REPLAY","DRM"
      ]
    },
    "labels": {
      "type": "array",
      "description": "Namespaced labels for routing, analysis, and governance (e.g., 'colony:role=planner@1').",
      "items": { "type": "string", "minLength": 1, "maxLength": 64 },
      "maxItems": 12
    },
    "state": {
      "type": "object",
      "required": ["confidence", "salience"],
      "additionalProperties": true,
      "properties": {
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
        "valence": { "type": "number", "minimum": -1, "maximum": 1 },
        "arousal": { "type": "number", "minimum": 0, "maximum": 1 },
        "salience": { "type": "number", "minimum": 0, "maximum": 1 },
        "novelty": { "type": "number", "minimum": 0, "maximum": 1 },
        "urgency": { "type": "number", "minimum": 0, "maximum": 1 },
        "shock_factor": { "type": "number", "minimum": 0, "maximum": 1 },
        "risk": { "type": "number", "minimum": 0, "maximum": 1 },
        "utility": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "timestamps": {
      "type": "object",
      "additionalProperties": false,
      "required": ["created_ts"],
      "properties": {
        "created_ts": { "type": "integer", "description": "Epoch milliseconds" },
        "updated_ts": { "type": "integer" },
        "observed_ts": { "type": "integer", "description": "Epoch ms of the real-world observation (if applicable)" }
      }
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["producer", "capabilities", "tenant", "trace_id", "consent_scopes"],
      "properties": {
        "producer": { "type": "string", "description": "Module path or service name that produced this node" },
        "capabilities": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
        "tenant": { "type": "string" },
        "trace_id": { "type": "string" },
        "consent_scopes": { "type": "array", "items": { "type": "string" } },
        "subject_pseudonym": { "type": "string", "description": "Optional pseudonymized subject identifier" },
        "model_signature": { "type": "string", "description": "Hasher or version of the model/tool" },
        "policy_version": { "type": "string", "description": "Active policy or guardrail version at creation time" },
        "colony": {
          "type": "object",
          "additionalProperties": false,
          "required": ["id", "role"],
          "properties": {
            "id": { "type": "string", "minLength": 1, "maxLength": 64, "description": "Colony or swarm identifier" },
            "role": { "type": "string", "minLength": 1, "maxLength": 64, "description": "Functional role (e.g., planner, critic, summarizer)" },
            "iteration": { "type": "integer", "minimum": 0, "description": "Optional iteration index within the colony run" }
          }
        }
      }
    },
    "links": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["target_node_id", "link_type", "direction"],
        "properties": {
          "target_node_id": { "type": "string" },
          "link_type": { "type": "string", "enum": ["temporal", "causal", "semantic", "emotional", "spatial", "evidence"] },
          "weight": { "type": "number", "minimum": 0, "maximum": 1 },
          "direction": { "type": "string", "enum": ["bidirectional", "unidirectional"] },
          "explanation": { "type": "string" }
        }
      }
    },
    "evolves_to": { "type": "array", "items": { "type": "string" } },
    "triggers": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["event_type", "timestamp"],
        "properties": {
          "trigger_node_id": { "type": "string" },
          "event_type": { "type": "string" },
          "effect": { "type": "string" },
          "timestamp": { "type": "integer" }
        }
      }
    },
    "reflections": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["reflection_type", "timestamp"],
        "properties": {
          "reflection_type": { "type": "string", "enum": ["regret", "affirmation", "dissonance_resolution", "moral_conflict", "self_question"] },
          "timestamp": { "type": "integer" },
          "old_state": { "$ref": "#/properties/state" },
          "new_state": { "$ref": "#/properties/state" },
          "cause": { "type": "string" }
        }
      }
    },
    "embeddings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["space", "vector"],
        "properties": {
          "space": { "type": "string" },
          "vector": { "type": "array", "items": { "type": "number" } },
          "dim": { "type": "integer" },
          "norm": { "type": "number" }
        }
      }
    },
    "evidence": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "kind": { "type": "string", "enum": ["trace","doc","url","input_key","consent_record","artifact"] },
          "uri": { "type": "string" },
          "hash": { "type": "string" }
        }
      }
    },
    "schema_ref": { "type": "string", "const": "lukhas://schemas/matriz_node_v1.json" }
  }
}

"""MATADA schema validation utility (v1.1)
Usage:
  cat nodes.json | python -m MATADA.utils.matada_validate
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections.abc import Iterable
from typing import List

try:
    from jsonschema import Draft202012Validator
except Exception:
    raise SystemExit("jsonschema is required. pip install jsonschema>=4.0")

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "matriz_node_v1.json"

with SCHEMA_PATH.open("r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

VALIDATOR = Draft202012Validator(SCHEMA)


def validate_nodes(nodes: Iterable[dict]) -> bool:
    errors: List[str] = []
    for i, node in enumerate(nodes):
        for err in VALIDATOR.iter_errors(node):
            loc = "/".join(str(x) for x in err.path)
            errors.append(f"[{i}] {err.message} @ {loc}")
    if errors:
        raise ValueError("MATADA validation failed:\n" + "\n".join(errors))
    return True


if __name__ == "__main__":
    data = json.load(sys.stdin)
    if isinstance(data, dict):
        data = [data]
    validate_nodes(data)
    print("MATADA OK (v1.1)")
