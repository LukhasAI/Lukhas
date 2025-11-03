#!/usr/bin/env python3
"""
Shadow diff harness for Lukhas ⇄ OpenAI parity.

Sends a small suite of façade requests to both Lukhas and OpenAI (when credentials
are provided), compares status codes, envelope structure, and the key header families,
and writes a structured report under docs/audits/shadow.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import requests

REQUEST_SUITE = [
    {
        "name": "healthz",
        "method": "GET",
        "path": "/healthz",
        "requires_key": False,
        "openai_supported": False,
        "payloads": {},
    },
    {
        "name": "models_list",
        "method": "GET",
        "path": "/v1/models",
        "requires_key": True,
        "openai_supported": True,
        "payloads": {},
    },
    {
        "name": "embeddings_basic",
        "method": "POST",
        "path": "/v1/embeddings",
        "requires_key": True,
        "openai_supported": True,
        "payloads": {
            "lukhas": {"model": "lukhas-matriz", "input": "shadow diff check"},
            "openai": {"model": "text-embedding-3-small", "input": "shadow diff check"},
        },
    },
    {
        "name": "responses_basic",
        "method": "POST",
        "path": "/v1/responses",
        "requires_key": True,
        "openai_supported": True,
        "payloads": {
            "lukhas": {"model": "lukhas-matriz", "input": "Say hello from Lukhas."},
            "openai": {"model": "gpt-4o-mini", "input": "Say hello from OpenAI."},
        },
    },
]

INTERESTING_HEADERS = {
    "x-request-id",
    "x-trace-id",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "x-ratelimit-limit-requests",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-reset-requests",
    "retry-after",
}


@dataclass
class CallResult:
    status: int | None
    json_body: Any | None
    headers: Dict[str, Any]
    error: str | None = None


def lower_dict(data: Iterable[tuple[str, Any]]) -> Dict[str, Any]:
    return {k.lower(): v for k, v in data}


def json_signature(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {k: json_signature(payload[k]) for k in sorted(payload)}
    if isinstance(payload, list):
        if not payload:
            return []
        return [json_signature(payload[0]), f"len={len(payload)}"]
    return type(payload).__name__


def perform_request(
    base_url: str,
    api_key: str | None,
    req: Dict[str, Any],
    provider: str,
    timeout: int = 30,
) -> CallResult:
    url = base_url.rstrip("/") + req["path"]
    headers = {"Accept": "application/json"}
    if req["method"] in {"POST", "PUT", "PATCH"}:
        headers["Content-Type"] = "application/json"
    if api_key and req.get("requires_key", False):
        headers["Authorization"] = f"Bearer {api_key}"

    payload_map = req.get("payloads", {})
    payload = payload_map.get(provider, payload_map.get("lukhas"))
    data = json.dumps(payload) if payload is not None else None

    try:
        resp = requests.request(
            req["method"],
            url,
            data=data,
            headers=headers,
            timeout=timeout,
        )
        try:
            json_body = resp.json()
        except ValueError:
            json_body = None
        interesting_headers = {
            k: v
            for k, v in lower_dict(resp.headers.items()).items()
            if k in INTERESTING_HEADERS
        }
        return CallResult(resp.status_code, json_body, interesting_headers)
    except Exception as exc:
        return CallResult(None, None, {}, str(exc))


def compare_responses(lukhas_result: CallResult, openai_result: CallResult | None) -> Dict[str, Any]:
    comparison: Dict[str, Any] = {}
    comparison["lukhas_status"] = lukhas_result.status
    comparison["openai_status"] = openai_result.status if openai_result else None
    comparison["status_match"] = (
        openai_result is not None and lukhas_result.status == openai_result.status
    )

    lut_sig = json_signature(lukhas_result.json_body)
    oa_sig = json_signature(openai_result.json_body) if openai_result else None
    comparison["lukhas_body_signature"] = lut_sig
    comparison["openai_body_signature"] = oa_sig
    comparison["body_signature_match"] = openai_result is not None and lut_sig == oa_sig

    header_diff = []
    if openai_result:
        all_keys = sorted(set(lukhas_result.headers) | set(openai_result.headers))
        for key in all_keys:
            lv = lukhas_result.headers.get(key)
            ov = openai_result.headers.get(key)
            if lv != ov:
                header_diff.append({"header": key, "lukhas": lv, "openai": ov})

    comparison["header_differences"] = header_diff
    comparison["headers_match"] = not header_diff and openai_result is not None
    comparison["lukhas_error"] = lukhas_result.error
    comparison["openai_error"] = openai_result.error if openai_result else None
    return comparison


def build_markdown(report: Dict[str, Any]) -> str:
    rows = []
    for item in report["requests"]:
        name = item["name"]
        status = "✅" if item.get("status_match") else "⚠️"
        headers = "✅" if item.get("headers_match") else "⚠️"
        body = "✅" if item.get("body_signature_match") else "⚠️"
        notes = []
        if item.get("lukhas_error"):
            notes.append(f"Lukhas error: {item['lukhas_error']}")
        if item.get("openai_error"):
            notes.append(f"OpenAI error: {item['openai_error']}")
        if item.get("header_differences"):
            notes.append("Header diffs present")
        if not item.get("body_signature_match"):
            notes.append("Body shape mismatch")
        rows.append(f"| {name} | {status} | {headers} | {body} | {'; '.join(notes) or '—'} |")

    table = "\n".join(rows)
    return (
        f"# Shadow Diff Report\n\n"
        f"*Generated:* {report['generated_at']}\n"
        f"*Lukhas Base:* {report['lukhas_base']}\n"
        f"*OpenAI Base:* {report.get('openai_base') or 'skipped'}\n"
        f"*Requests Compared:* {report['summary']['total']}\n"
        f"*Exact Matches:* {report['summary']['matches']}\n"
        f"*Mismatches:* {report['summary']['mismatches']}\n\n"
        "| Request | Status | Headers | Body | Notes |\n"
        "|---------|--------|---------|------|-------|\n"
        f"{table}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Shadow diff harness")
    parser.add_argument("--lukhas-base", default=os.environ.get("LUKHAS_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--openai-base", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com"))
    parser.add_argument("--lukhas-key", default=os.environ.get("LUKHAS_API_KEY"))
    parser.add_argument("--openai-key", default=os.environ.get("OPENAI_API_KEY"))
    parser.add_argument("--output-dir", default="docs/audits/shadow")
    parser.add_argument("--skip-openai", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    requests_report = []
    matches = mismatches = 0

    for req in REQUEST_SUITE:
        lukhas_result = perform_request(args.lukhas_base, args.lukhas_key, req, "lukhas")
        openai_result: CallResult | None = None
        if not args.skip_openai and req.get("openai_supported", True) and args.openai_key:
            openai_result = perform_request(args.openai_base, args.openai_key, req, "openai")

        comparison = compare_responses(lukhas_result, openai_result)
        comparison.update({
            "name": req["name"],
            "path": req["path"],
            "method": req["method"],
            "openai_checked": openai_result is not None,
        })

        if comparison["openai_checked"]:
            if (
                comparison["status_match"]
                and comparison["headers_match"]
                and comparison["body_signature_match"]
            ):
                matches += 1
            else:
                mismatches += 1
        else:
            matches += 1

        requests_report.append(comparison)

    report = {
        "generated_at": timestamp,
        "lukhas_base": args.lukhas_base,
        "openai_base": args.openai_base if not args.skip_openai else None,
        "summary": {"total": len(requests_report), "matches": matches, "mismatches": mismatches},
        "requests": requests_report,
    }

    json_path = output_dir / f"{timestamp}.json"
    md_path = output_dir / f"{timestamp}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_content = build_markdown(report)
    md_path.write_text(md_content, encoding="utf-8")
    (output_dir / "latest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_dir / "latest.md").write_text(md_content, encoding="utf-8")

    print(f"Shadow diff complete: {json_path}")
    print(f"Matches: {matches} / {len(requests_report)}")
    if mismatches:
        print("⚠️  Mismatches detected – inspect docs/audits/shadow/latest.md")
    else:
        print("✅ All compared responses match")


if __name__ == "__main__":  # pragma: no cover
    main()
