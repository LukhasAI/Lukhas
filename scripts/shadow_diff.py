#!/usr/bin/env python3
"""
Shadow-diff harness: Compare Lukhas vs OpenAI for alignment validation.

Validates:
- Envelope shape (status codes, structure)
- Headers (rate-limit parity, trace-id)
- Response timing

Outputs:
- docs/audits/shadow/YYYYMMDD/shadow_diff.json
- docs/audits/shadow/YYYYMMDD/envelope_comparison.md
- docs/audits/shadow/YYYYMMDD/headers_comparison.md

Usage:
  python3 scripts/shadow_diff.py
  make shadow-diff  # via Makefile target
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple


def compare_chat_completion(
    lukhas_url: str,
    openai_url: str,
    auth_headers: Dict[str, str],
    model: str = "gpt-3.5-turbo"
) -> Dict[str, Any]:
    """
    Compare /v1/chat/completions response between Lukhas and OpenAI.

    Returns dict with envelope, headers, and timing comparison.
    """
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'test' once"}],
        "max_tokens": 5,
        "temperature": 0
    }

    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoint": "/v1/chat/completions",
        "lukhas": {},
        "openai": {},
        "comparison": {}
    }

    # Call Lukhas
    try:
        lukhas_start = time.time()
        lukhas_resp = requests.post(
            f"{lukhas_url}/v1/chat/completions",
            headers=auth_headers,
            json=payload,
            timeout=30
        )
        lukhas_duration = time.time() - lukhas_start

        results["lukhas"] = {
            "status_code": lukhas_resp.status_code,
            "headers": dict(lukhas_resp.headers),
            "duration_ms": round(lukhas_duration * 1000, 2),
            "body": lukhas_resp.json() if lukhas_resp.ok else lukhas_resp.text
        }
    except Exception as e:
        results["lukhas"]["error"] = str(e)

    # Call OpenAI
    try:
        openai_start = time.time()
        openai_resp = requests.post(
            f"{openai_url}/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}"},
            json=payload,
            timeout=30
        )
        openai_duration = time.time() - openai_start

        results["openai"] = {
            "status_code": openai_resp.status_code,
            "headers": dict(openai_resp.headers),
            "duration_ms": round(openai_duration * 1000, 2),
            "body": openai_resp.json() if openai_resp.ok else openai_resp.text
        }
    except Exception as e:
        results["openai"]["error"] = str(e)

    # Compare
    results["comparison"] = {
        "status_match": results["lukhas"].get("status_code") == results["openai"].get("status_code"),
        "envelope_keys_match": _compare_envelope_keys(
            results["lukhas"].get("body", {}),
            results["openai"].get("body", {})
        ),
        "headers_parity": _compare_headers(
            results["lukhas"].get("headers", {}),
            results["openai"].get("headers", {})
        )
    }

    return results


def _compare_envelope_keys(lukhas_body: Any, openai_body: Any) -> Dict[str, Any]:
    """Compare top-level keys in response bodies."""
    if not isinstance(lukhas_body, dict) or not isinstance(openai_body, dict):
        return {"match": False, "reason": "Non-dict response"}

    lukhas_keys = set(lukhas_body.keys())
    openai_keys = set(openai_body.keys())

    return {
        "match": lukhas_keys == openai_keys,
        "lukhas_only": list(lukhas_keys - openai_keys),
        "openai_only": list(openai_keys - lukhas_keys),
        "shared": list(lukhas_keys & openai_keys)
    }


def _compare_headers(lukhas_headers: Dict[str, str], openai_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Compare rate-limit headers between Lukhas and OpenAI.

    Checks for:
    - X-RateLimit-Limit (new standard)
    - X-RateLimit-Remaining (new standard)
    - X-RateLimit-Reset (new standard)
    - X-RateLimit-Limit-Requests (legacy OpenAI)
    - X-RateLimit-Remaining-Requests (legacy OpenAI)
    - X-RateLimit-Reset-Requests (legacy OpenAI)
    """
    lukhas_lower = {k.lower(): v for k, v in lukhas_headers.items()}
    openai_lower = {k.lower(): v for k, v in openai_headers.items()}

    critical_headers = [
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "x-ratelimit-limit-requests",
        "x-ratelimit-remaining-requests",
        "x-ratelimit-reset-requests",
        "x-trace-id",
        "x-service-version"
    ]

    parity = {}
    for header in critical_headers:
        parity[header] = {
            "lukhas": lukhas_lower.get(header, "MISSING"),
            "openai": openai_lower.get(header, "MISSING"),
            "present_in_both": header in lukhas_lower and header in openai_lower
        }

    return parity


def generate_markdown_reports(results: Dict[str, Any], output_dir: Path) -> None:
    """Generate human-readable Markdown reports from comparison results."""

    # Envelope comparison report
    envelope_md = f"""# Envelope Comparison Report
**Date**: {results['timestamp']}
**Endpoint**: {results['endpoint']}

## Status Codes
- **Lukhas**: {results['lukhas'].get('status_code', 'N/A')}
- **OpenAI**: {results['openai'].get('status_code', 'N/A')}
- **Match**: {'✅ YES' if results['comparison']['status_match'] else '❌ NO'}

## Envelope Keys
"""

    envelope_keys = results['comparison']['envelope_keys_match']
    if envelope_keys.get('match'):
        envelope_md += "✅ **Keys Match Perfectly**\n\n"
        envelope_md += f"Shared keys: {', '.join(envelope_keys.get('shared', []))}\n"
    else:
        envelope_md += "❌ **Keys Mismatch Detected**\n\n"
        if envelope_keys.get('lukhas_only'):
            envelope_md += f"**Lukhas-only keys**: {', '.join(envelope_keys['lukhas_only'])}\n"
        if envelope_keys.get('openai_only'):
            envelope_md += f"**OpenAI-only keys**: {', '.join(envelope_keys['openai_only'])}\n"
        if envelope_keys.get('shared'):
            envelope_md += f"**Shared keys**: {', '.join(envelope_keys['shared'])}\n"

    # Headers comparison report
    headers_md = f"""# Headers Comparison Report
**Date**: {results['timestamp']}
**Endpoint**: {results['endpoint']}

## Rate-Limit Headers Parity

"""

    headers_parity = results['comparison']['headers_parity']
    for header, info in headers_parity.items():
        status = '✅' if info['present_in_both'] else '❌'
        headers_md += f"### {status} `{header}`\n"
        headers_md += f"- **Lukhas**: `{info['lukhas']}`\n"
        headers_md += f"- **OpenAI**: `{info['openai']}`\n"
        headers_md += f"- **Present in Both**: {info['present_in_both']}\n\n"

    # Write reports
    (output_dir / "envelope_comparison.md").write_text(envelope_md)
    (output_dir / "headers_comparison.md").write_text(headers_md)


def main():
    """Run shadow-diff comparison and write results."""
    # Configuration
    lukhas_url = os.getenv("LUKHAS_BASE_URL", "http://localhost:8000")
    openai_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    auth_token = os.getenv("LUKHAS_AUTH_TOKEN", "test-token")

    auth_headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    # Setup output directory
    date_str = datetime.now().strftime("%Y%m%d")
    output_dir = Path("docs/audits/shadow") / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Running shadow-diff comparison...")
    print(f"   Lukhas: {lukhas_url}")
    print(f"   OpenAI: {openai_url}")

    # Run comparison
    results = compare_chat_completion(lukhas_url, openai_url, auth_headers)

    # Write JSON results
    json_path = output_dir / "shadow_diff.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Shadow-diff JSON: {json_path}")

    # Generate Markdown reports
    generate_markdown_reports(results, output_dir)

    print(f"✅ Envelope comparison: {output_dir / 'envelope_comparison.md'}")
    print(f"✅ Headers comparison: {output_dir / 'headers_comparison.md'}")

    # Summary
    status_match = results['comparison']['status_match']
    envelope_match = results['comparison']['envelope_keys_match'].get('match', False)

    print("\n📊 Summary:")
    print(f"   Status codes: {'✅ MATCH' if status_match else '❌ MISMATCH'}")
    print(f"   Envelope keys: {'✅ MATCH' if envelope_match else '❌ MISMATCH'}")
    print(f"   Output directory: {output_dir}")

    return 0 if (status_match and envelope_match) else 1


if __name__ == "__main__":
    exit(main())
