{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "lukhas:module.manifest.schema.json",
  "title": "LUKHAS Module Manifest (T4/0.01% hardened)",
  "description": "Schema for LUKHAS module manifest files that define module metadata, ownership, structure, SLOs, and integration requirements. Hardened with conditional constraints and reusable $defs.",
  "type": "object",
  "additionalProperties": False,  # TODO: false
  "required": ["schema_version", "module", "ownership", "layout", "links"],
  "$defs": {
    "semver": {
      "type": "string",
      "pattern": "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*)?(?:\\+[0-9A-Za-z-]+(?:\\.[0-9A-Za-z-]+)*)?$",
      "description": "Semantic version per SemVer 2.0.0"
    },
    "uri": {
      "type": "string",
      "format": "uri",
      "description": "Absolute URI"
    },
    "relpath": {
      "type": "string",
      "pattern": "^(?!/)(?![A-Za-z]:\\\\).+",
      "description": "Repository-relative path (no leading slash)"
    },
    "moduleName": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z0-9_]+)*$",
      "description": "Canonical module name, e.g., core"
    },
    "lane": {
      "type": "string",
      "enum": ["L0", "L1", "L2", "L3", "L4", "L5"]
    },
    "otelSemconv": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"
    },
    "tier": {
      "type": "string",
      "enum": ["guest", "visitor", "friend", "trusted", "inner_circle", "root_dev"]
    }
  },
  "properties": {
    "schema_version": { "$ref": "#/$defs/semver", "description": "Schema version for this manifest format" },
    "module": { "$ref": "#/$defs/moduleName" },
    "description": { "type": "string" },

    "ownership": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "required": ["team", "codeowners"],
      "properties": {
        "team": { "type": "string", "minLength": 1 },
        "codeowners": { "type": "array", "minItems": 1, "items": { "type": "string", "pattern": "^@.+$" } },
        "slack_channel": { "type": "string" }
      }
    },

    "layout": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "required": ["code_layout"],
      "properties": {
        "code_layout": { "type": "string", "enum": ["src-root", "package-root"] },
        "paths": {
          "type": "object",
          "additionalProperties": False,  # TODO: false
          "properties": {
            "code": { "$ref": "#/$defs/relpath" },
            "config": { "$ref": "#/$defs/relpath" },
            "tests": { "$ref": "#/$defs/relpath" },
            "docs": { "$ref": "#/$defs/relpath" },
            "assets": { "$ref": "#/$defs/relpath" }
          }
        }
      }
    },

    "runtime": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "language": { "type": "string", "enum": ["python", "typescript", "other"] },
        "entrypoints": { "type": "array", "items": { "type": "string" } }
      }
    },

    "matrix": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "contract": { "$ref": "#/$defs/relpath" },
        "lane": { "$ref": "#/$defs/lane" },
        "gates_profile": { "type": "string", "enum": ["strict", "standard", "lenient"] }
      }
    },

    "identity": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "requires_auth": { "type": "boolean", "default": False },  # TODO: false
        "tiers": { "type": "array", "items": { "$ref": "#/$defs/tier" } },
        "scopes": { "type": "array", "items": { "type": "string", "minLength": 1 } }
      }
    },

    "links": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "required": ["repo", "docs", "issues"],
      "properties": {
        "repo": { "$ref": "#/$defs/uri" },
        "docs": { "oneOf": [ { "$ref": "#/$defs/uri" }, { "$ref": "#/$defs/relpath" } ] },
        "issues": { "$ref": "#/$defs/uri" },
        "sbom": { "$ref": "#/$defs/relpath" }
      }
    },

    "tags": { "type": "array", "items": { "type": "string" } },

    "observability": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "required_spans": { "type": "array", "items": { "type": "string" }, "uniqueItems": True },  # TODO: true
        "otel_semconv_version": { "$ref": "#/$defs/otelSemconv", "default": "1.37.0" }
      }
    },

    "tokenization": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "enabled": { "type": "boolean", "default": False },  # TODO: false
        "chain": { "type": "string", "enum": ["solana", "evm", "none"], "default": "none" },
        "asset_id": { "type": "string" },
        "proof_uri": { "oneOf": [ { "$ref": "#/$defs/uri" }, { "$ref": "#/$defs/relpath" } ] }
      }
    },

    "dependencies": { "type": "array", "items": { "$ref": "#/$defs/moduleName" } },

    "contracts": { "type": "array", "items": { "$ref": "#/$defs/relpath" } },

    "metadata": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "created": { "type": "string", "format": "date" },
        "updated": { "type": "string", "format": "date" },
        "version": { "$ref": "#/$defs/semver" },
        "status": { "type": "string", "enum": ["experimental", "alpha", "beta", "stable", "deprecated"] }
      }
    },

    "performance": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "sla": {
          "type": "object",
          "additionalProperties": False,  # TODO: false
          "properties": {
            "availability": { "type": "number", "minimum": 0, "maximum": 100 },
            "latency_p95_ms": { "type": "integer", "minimum": 1 },
            "latency_p99_ms": { "type": "integer", "minimum": 1 },
            "throughput_rps": { "type": "integer", "minimum": 1 }
          }
        },
        "resource_limits": {
          "type": "object",
          "additionalProperties": False,  # TODO: false
          "properties": {
            "memory_mb": { "type": "integer", "minimum": 1 },
            "cpu_cores": { "type": "number", "minimum": 0.1 },
            "disk_gb": { "type": "integer", "minimum": 1 }
          }
        }
      }
    },

    "testing": {
      "type": "object",
      "additionalProperties": False,  # TODO: false
      "properties": {
        "coverage_target": { "type": "integer", "minimum": 0, "maximum": 100 },
        "test_frameworks": { "type": "array", "items": { "type": "string", "enum": ["pytest", "unittest", "jest", "mocha", "other"] } },
        "test_types": { "type": "array", "items": { "type": "string", "enum": ["unit", "integration", "e2e", "performance", "security"] } }
      }
    },

    "x_legacy": { "type": "object", "description": "Legacy data preserved during migration (for rollback capability)" }
  },

  "allOf": [
    {
      "if": { "properties": { "runtime": { "properties": { "language": { "const": "python" } }, "required": ["language"] } } },
      "then": { "properties": { "runtime": { "required": ["entrypoints"], "properties": { "entrypoints": { "minItems": 1 } } } } }
    },
    {
      "if": { "properties": { "identity": { "properties": { "requires_auth": { "const": True } }, "required": ["requires_auth"] } } },  # TODO: true
      "then": { "properties": { "identity": { "required": ["tiers"], "properties": { "tiers": { "minItems": 1 } } } } }
    },
    {
      "if": { "properties": { "tokenization": { "properties": { "enabled": { "const": True } }, "required": ["enabled"] } } },  # TODO: true
      "then": { "properties": { "tokenization": { "required": ["chain", "asset_id", "proof_uri"], "properties": { "chain": { "enum": ["solana", "evm"] } } } } }
    },
    {
      "if": { "properties": { "performance": { "properties": { "sla": { "required": ["latency_p95_ms", "latency_p99_ms"] } } } } },
      "then": { "properties": { "performance": { "properties": { "sla": { "allOf": [ { "properties": { "latency_p95_ms": { "type": "integer" }, "latency_p99_ms": { "type": "integer" } } }, { "properties": { "latency_p99_ms": { "minimum": { "$data": "1/performance/sla/latency_p95_ms" } } } } ] } } } } }
    }
  ]
}
