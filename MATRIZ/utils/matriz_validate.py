from __future__ import annotations

import json
import pathlib
import sys
from collections.abc import Iterable

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "matriz" / "matriz_node_v1.json"

ALLOWED_SCHEMA_REFS = {
    "lukhas://schemas/matriz_node_v1.json",
    "lukhas://schemas/matada_node_v1.json",  # legacy accepted during transition
}

_schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
_validator = Draft202012Validator(_schema)


def validate_node(node: dict) -> None:
    sr = node.get("schema_ref")
    if sr and sr not in ALLOWED_SCHEMA_REFS:
        raise ValueError(f"Unsupported schema_ref: {sr!r}")

    # Create a copy without metadata fields for validation
    node_copy = dict(node)
    node_copy.pop("$kind", None)  # Remove if present
    node_copy.pop("schema_ref", None)  # Remove if present

    _validator.validate(node_copy)


def validate_nodes(nodes: Iterable[dict]) -> None:
    for i, n in enumerate(nodes):
        try:
            validate_node(n)
        except Exception as e:
            raise ValueError(f"Node index {i} failed validation: {e}") from e


def _validate_file(f: pathlib.Path) -> int:
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(data, list):
            validate_nodes(data)
        else:
            # Assume single node if dict-like
            validate_node(data)
        print(f"OK  {f}")
        return 0
    except Exception as e:
        print(f"ERR {f}: {e}", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python -m matriz.utils.matriz_validate <file_or_dir> [...]",
            file=sys.stderr,
        )
        sys.exit(2)
    paths = [pathlib.Path(p) for p in sys.argv[1:]]
    errors = 0
    for p in paths:
        if p.is_dir():
            for f in p.rglob("*.json"):
                errors += _validate_file(f)
        else:
            errors += _validate_file(p)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
