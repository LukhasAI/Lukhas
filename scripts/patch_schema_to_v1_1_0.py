#!/usr/bin/env python3
"""
Module: patch_schema_to_v1_1_0.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""
Patch schemas/matriz_module_compliance.schema.json → v1.1.0

- Add "🌊 Flow (Consciousness)" to constellation enum
- Deprecate module.lane (optional); add module.colony
- Tighten nested objects with additionalProperties: false
- Extend logging levels; add observability.events
- Add top-level "security" block
- Add T1_critical gates via if/then
- Bump version field to 1.1.0 (schema metadata)
"""
import datetime
import json
import pathlib
import sys

SCHEMA_PATH = pathlib.Path("schemas/matriz_module_compliance.schema.json")

def ensure_ap_false(node):
    if isinstance(node, dict) and node.get("type") == "object":
        node.setdefault("additionalProperties", False)
    return node

def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else SCHEMA_PATH
    schema = json.loads(path.read_text(encoding="utf-8"))

    # --- bump version metadata if present ---
    if "version" in schema:
        schema["version"] = "1.1.0"
    # keep $id if present

    props = schema.setdefault("properties", {})

    # --- MODULE: add colony, deprecate lane, adjust required ---
    module = props.get("module", {})
    module_props = module.setdefault("properties", {})
    req = module.setdefault("required", [])
    if "lane" in req:
        req = [r for r in req if r != "lane"]
        module["required"] = req
    module_props.setdefault("colony", {
        "type": "string",
        "description": "Flat capability domain (replaces legacy 'lane')."
    })
    if "lane" in module_props:
        lane_desc = module_props["lane"].get("description", "")
        if "DEPRECATED" not in lane_desc:
            module_props["lane"]["description"] = (lane_desc + " (DEPRECATED: use 'colony')").strip()
    ensure_ap_false(module)
    props["module"] = module

    # --- CONSTELLATION: add Flow star, add star_aliases ---
    ca = props.get("constellation_alignment", {})
    ca_props = ca.setdefault("properties", {})
    primary = ca_props.get("primary_star", {})
    enum = primary.get("enum", [])
    flow = "🌊 Flow (Consciousness)"
    if flow not in enum:
        enum.append(flow)
        primary["enum"] = enum
    ca_props.setdefault("star_aliases", {
        "type":"array", "items":{"type":"string"},
        "description":"Optional aliases that map to canonical star name"
    })
    ensure_ap_false(ca)
    props["constellation_alignment"] = ca

    # --- OBSERVABILITY: extend logging levels; add events; tighten ---
    obs = props.get("observability", {})
    obs_props = obs.setdefault("properties", {})
    logging = obs_props.setdefault("logging", {"type":"object","properties":{}})
    log_props = logging.setdefault("properties", {})
    levels = set(log_props.get("default_level", {}).get("enum", ["DEBUG","INFO","WARNING","ERROR"]))
    levels.update(["TRACE","CRITICAL"])
    log_props["default_level"] = {"type":"string","enum":sorted(levels)}
    ensure_ap_false(logging)
    obs_props["logging"] = logging

    obs_props.setdefault("events", {
        "type":"object",
        "properties": {
            "publishes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}},
            "subscribes":{"type":"array","items":{"type":"string","pattern":"^[a-z0-9_.:-]+@v\\d+$"}}
        }
    })
    ensure_ap_false(obs)
    props["observability"] = obs

    # --- SECURITY: add top-level block if missing ---
    props.setdefault("security", {
        "type":"object",
        "properties":{
            "requires_auth":{"type":"boolean"},
            "data_classification":{"type":"string","enum":["public","internal","restricted","sensitive"]},
            "secrets_used":{"type":"array","items":{"type":"string"}},
            "network_calls":{"type":"boolean"},
            "sandboxed":{"type":"boolean"},
            "policies":{"type":"array","items":{"type":"string"}}
        }
    })

    # --- Tighten nested objects globally where known ---
    for key in ["module","matriz_integration","constellation_alignment","dependencies",
                "exports","testing","observability","metadata","security"]:
        if key in props:
            ensure_ap_false(props[key])

    # --- Add T1_critical gates via if/then ---
    gates = {
        "if": {
            "properties": {
                "testing": {
                    "properties": {
                        "quality_tier": {"const":"T1_critical"}
                    }
                }
            }
        },
        "then": {
            "properties": {
                "testing": {
                    "required": ["has_tests","test_paths"],
                    "properties": {
                        "has_tests":{"const": True},
                        "test_paths":{"type":"array","minItems":1}
                    }
                },
                "metadata": {
                    "required": ["owner"],
                    "properties": {"owner":{"type":"string","minLength":1}}
                },
                "observability": {
                    "properties": {
                        "spans":{"type":"array","minItems":1},
                        "metrics":{"type":"array","minItems":1},
                        "logging":{"type":"object","required":["logger_name","default_level"]}
                    }
                }
            }
        }
    }
    allOf = list(schema.get("allOf", []))
    allOf.append(gates)
    schema["allOf"] = allOf

    # --- write back ---
    text = json.dumps(schema, indent=4, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")
    print("Patched →", path, "at", datetime.datetime.utcnow().isoformat()+"Z")

if __name__ == "__main__":
    main()
