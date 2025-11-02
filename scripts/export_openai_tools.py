#!/usr/bin/env python3
"""
Export OpenAI tool specs from LUKHAS manifests.

Converts LUKHAS module manifests into OpenAI-compatible function calling schemas.
Writes build/openai_tools.json with:
  {"tools":[{"type":"function","function":{"name":"...","description":"...","parameters":{...}}}, ...]}

Usage:
  python3 scripts/export_openai_tools.py [--manifests PATH] [--out PATH] [--verbose]
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

def generate_parameter_schema(capability: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate OpenAI-compatible JSON Schema parameters from capability.

    Falls back to empty object schema if no parameters defined.
    """
    # Check for explicit schema
    if capability.get("schema"):
        return capability["schema"]

    # Check for parameters field (alternative format)
    if capability.get("parameters"):
        return capability["parameters"]

    # Check interfaces for parameter hints
    interfaces = capability.get("interfaces", [])
    if interfaces:
        # Build schema from interface signatures
        properties = {}
        for iface in interfaces:
            if isinstance(iface, dict) and "parameters" in iface:
                properties.update(iface["parameters"])

        if properties:
            return {
                "type": "object",
                "properties": properties,
                "required": []
            }

    # Default: empty object (no parameters)
    return {
        "type": "object",
        "properties": {},
        "required": []
    }

def extract_tool_from_capability(capability: Dict[str, Any], manifest_path: Path) -> Dict[str, Any]:
    """
    Convert a capability from a manifest into an OpenAI tool spec.

    Args:
        capability: Capability dict from manifest
        manifest_path: Path to source manifest (for fallback naming)

    Returns:
        OpenAI tool spec dict
    """
    # Extract name (with fallbacks)
    name = capability.get("name") or capability.get("id") or manifest_path.stem
    # Sanitize name: lowercase, replace invalid chars, truncate to 64 chars
    name = name.lower().replace(".", "_").replace("-", "_")[:64]

    # Extract description
    description = capability.get("description", "")
    if not description:
        # Fallback to type-based description
        cap_type = capability.get("type", "function")
        description = f"{name} ({cap_type})"

    # Generate parameter schema
    parameters = generate_parameter_schema(capability)

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }

def load_manifest(path: Path) -> Dict[str, Any]:
    """
    Load a manifest JSON file with error handling.

    Returns empty dict on parse error.
    """
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse error in {path}: {e}")
        return {}
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Export OpenAI tool specs from LUKHAS manifests")
    parser.add_argument("--manifests", default="manifests", help="Path to manifests directory")
    parser.add_argument("--out", default="build", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Create output directory
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find all manifests
    manifest_dir = Path(args.manifests)
    if not manifest_dir.exists():
        logger.error(f"Manifests directory not found: {manifest_dir}")
        return 1

    manifest_files = list(manifest_dir.rglob("module.manifest.json"))
    logger.info(f"Found {len(manifest_files)} manifest files")

    # Extract tools from all manifests
    tools = []
    skipped = 0

    for mf in manifest_files:
        manifest = load_manifest(mf)
        if not manifest:
            skipped += 1
            continue

        capabilities = manifest.get("capabilities", [])
        if not capabilities:
            logger.debug(f"No capabilities in {mf}")
            continue

        for cap in capabilities:
            try:
                tool = extract_tool_from_capability(cap, mf)
                tools.append(tool)
                logger.debug(f"Exported tool: {tool['function']['name']} from {mf.name}")
            except Exception as e:
                logger.warning(f"Failed to export capability from {mf}: {e}")
                continue

    # Write output
    output_file = out_dir / "openai_tools.json"
    output_data = {
        "tools": tools,
        "metadata": {
            "total_tools": len(tools),
            "manifests_processed": len(manifest_files) - skipped,
            "manifests_skipped": skipped
        }
    }

    output_file.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    logger.info(f"✅ Wrote {output_file} with {len(tools)} tools")
    logger.info(f"   Processed: {len(manifest_files) - skipped} manifests")
    logger.info(f"   Skipped: {skipped} manifests")

    return 0

if __name__ == "__main__":
    sys.exit(main())
