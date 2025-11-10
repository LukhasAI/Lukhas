"""Check for OpenAPI drift between the saved schema and the live FastAPI app."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

HTTP_METHODS = {
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
}


def _sorted(values: Iterable[str]) -> list[str]:
    return sorted(values)


def deep_schema_diff(
    saved: Any, live: Any, base_path: str | None = None
) -> list[dict[str, Any]]:
    """Produce a deep diff between two JSON-like structures.

    The diff is represented as a list of dictionaries containing the path, the
    saved value, the live value, and the type of change (added, removed,
    modified).
    """

    path_prefix = base_path or "<root>"
    diffs: list[dict[str, Any]] = []

    if isinstance(saved, Mapping) and isinstance(live, Mapping):
        saved_keys = set(saved.keys())
        live_keys = set(live.keys())
        for key in _sorted(saved_keys - live_keys):
            diffs.append(
                {
                    "path": f"{path_prefix}.{key}",
                    "saved": saved[key],
                    "live": None,
                    "change": "removed",
                }
            )
        for key in _sorted(live_keys - saved_keys):
            diffs.append(
                {
                    "path": f"{path_prefix}.{key}",
                    "saved": None,
                    "live": live[key],
                    "change": "added",
                }
            )
        for key in _sorted(saved_keys & live_keys):
            next_path = f"{path_prefix}.{key}" if path_prefix else key
            diffs.extend(deep_schema_diff(saved[key], live[key], next_path))
        return diffs

    if isinstance(saved, list) and isinstance(live, list):
        if saved != live:
            diffs.append(
                {
                    "path": path_prefix,
                    "saved": saved,
                    "live": live,
                    "change": "modified",
                }
            )
        return diffs

    if saved != live:
        diffs.append(
            {
                "path": path_prefix,
                "saved": saved,
                "live": live,
                "change": "modified",
            }
        )

    return diffs


def _extract_methods(path_item: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        method: details
        for method, details in path_item.items()
        if method.lower() in HTTP_METHODS and isinstance(details, Mapping)
    }


def _diff_responses(
    saved_responses: Mapping[str, Any] | None,
    live_responses: Mapping[str, Any] | None,
) -> dict[str, Any]:
    saved_map: Mapping[str, Any] = saved_responses or {}
    live_map: Mapping[str, Any] = live_responses or {}

    summary: dict[str, Any] = {}

    saved_keys = set(saved_map.keys())
    live_keys = set(live_map.keys())

    added = _sorted(live_keys - saved_keys)
    removed = _sorted(saved_keys - live_keys)
    if added:
        summary["added"] = added
    if removed:
        summary["removed"] = removed

    modified_entries: list[dict[str, Any]] = []
    for status in _sorted(saved_keys & live_keys):
        differences = deep_schema_diff(
            saved_map[status], live_map[status], f"responses.{status}"
        )
        if differences:
            modified_entries.append({"status": status, "differences": differences})

    if modified_entries:
        summary["modified"] = modified_entries

    return summary


def _diff_methods(
    saved_path_item: Mapping[str, Any], live_path_item: Mapping[str, Any]
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    saved_methods = _extract_methods(saved_path_item)
    live_methods = _extract_methods(live_path_item)

    saved_keys = set(saved_methods.keys())
    live_keys = set(live_methods.keys())

    added_methods = _sorted(live_keys - saved_keys)
    removed_methods = _sorted(saved_keys - live_keys)
    if added_methods:
        result["added_methods"] = added_methods
    if removed_methods:
        result["removed_methods"] = removed_methods

    modified_methods: dict[str, Any] = {}
    for method in _sorted(saved_keys & live_keys):
        response_diff = _diff_responses(
            saved_methods[method].get("responses"),
            live_methods[method].get("responses"),
        )
        if response_diff:
            modified_methods[method] = {"responses": response_diff}

    if modified_methods:
        result["modified_methods"] = modified_methods

    return result


def compute_openapi_diff(saved: Mapping[str, Any], live: Mapping[str, Any]) -> dict[str, Any]:
    """Compute the drift summary between two OpenAPI specifications."""

    summary: dict[str, Any] = {
        "drift_detected": False,
        "paths": {"added": [], "removed": [], "modified": {}},
    }

    saved_paths = saved.get("paths") or {}
    live_paths = live.get("paths") or {}

    if not isinstance(saved_paths, Mapping) or not isinstance(live_paths, Mapping):
        raise ValueError("OpenAPI document is missing 'paths' mapping")

    saved_path_keys = set(saved_paths.keys())
    live_path_keys = set(live_paths.keys())

    added_paths = _sorted(live_path_keys - saved_path_keys)
    removed_paths = _sorted(saved_path_keys - live_path_keys)

    summary["paths"]["added"] = added_paths
    summary["paths"]["removed"] = removed_paths

    if added_paths or removed_paths:
        summary["drift_detected"] = True

    modified_paths: dict[str, Any] = {}
    for path in _sorted(saved_path_keys & live_path_keys):
        path_diff = _diff_methods(saved_paths[path], live_paths[path])
        if path_diff:
            modified_paths[path] = path_diff

    if modified_paths:
        summary["paths"]["modified"] = modified_paths
        summary["drift_detected"] = True
    else:
        summary["paths"]["modified"] = {}

    return summary


def _prompt_confirmation() -> bool:
    try:
        response = input("Apply --autofix and update openapi.json? [y/N]: ")
    except EOFError:
        return False
    return response.strip().lower() in {"y", "yes"}


def load_live_openapi() -> Mapping[str, Any]:
    try:
        from fastapi.testclient import TestClient
    except Exception as exc:  # pragma: no cover - optional dependency during import time
        raise RuntimeError("fastapi.testclient is not available") from exc

    try:
        serve_main = importlib.import_module("serve.main")
    except Exception as exc:  # pragma: no cover - runtime guard
        raise RuntimeError(f"Could not import app: {exc}") from exc

    app = getattr(serve_main, "app", None)
    if app is None:
        raise RuntimeError("serve.main does not expose an 'app' instance")

    client = TestClient(app)
    response = client.get("/openapi.json")
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch live OpenAPI schema: HTTP {response.status_code}"
        )
    return response.json()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--openapi-file",
        default="openapi.json",
        help="Path to the saved OpenAPI schema (default: openapi.json)",
    )
    parser.add_argument(
        "--autofix",
        action="store_true",
        help="Update the saved OpenAPI schema when drift is detected.",
    )

    args = parser.parse_args(argv)
    openapi_path = Path(args.openapi_file)

    try:
        live = load_live_openapi()
    except RuntimeError as exc:
        print(str(exc))
        return 0

    if not openapi_path.exists():
        print("No saved openapi.json; skipping drift check.")
        return 0

    with open(openapi_path, encoding="utf-8") as f:
        saved = json.load(f)

    summary = compute_openapi_diff(saved, live)
    summary["autofix_applied"] = False

    if summary["drift_detected"]:
        if args.autofix and _prompt_confirmation():
            with open(openapi_path, "w", encoding="utf-8") as f:
                json.dump(live, f, indent=2, sort_keys=True)
                f.write("\n")
            summary["autofix_applied"] = True
            exit_code = 0
        else:
            exit_code = 1
    else:
        exit_code = 0

    print(json.dumps(summary, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
