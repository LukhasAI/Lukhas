#!/usr/bin/env python3
"""
System Health Audit
- Runs: ruff stats, pytest+coverage (smoke+unit core), compat hits, openapi validate,
        star-rules coverage (if present), deps scan (pip-audit if available)
- Emits: docs/audits/health/latest.json and latest.md
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "docs" / "audits" / "health"
OUTDIR.mkdir(parents=True, exist_ok=True)

# Back-compat: also write to docs/audits/ root
AUDITS_ROOT = ROOT / "docs" / "audits"
AUDITS_ROOT.mkdir(parents=True, exist_ok=True)


def run(cmd, cwd=ROOT, ok_codes=(0,), text=True):
    """Run command and return (ok, stdout, stderr, returncode)."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=text, shell=isinstance(cmd, str))
    return p.returncode in ok_codes, p.stdout.strip(), p.stderr.strip(), p.returncode


def try_run(label, cmd, parse=lambda s: s, force_parse=False):
    """Try running command, capture result with parsed output.

    Args:
        force_parse: If True, parse output even on non-zero exit (for tools that exit 1 on findings)
    """
    ok, out, err, rc = run(cmd)
    # Parse output even if command failed if force_parse=True (for tools that exit 1 on findings)
    should_parse = ok or (force_parse and out)
    return {
        "task": label,
        "ok": ok,
        "rc": rc,
        "stdout": out[-2000:],
        "stderr": err[-2000:],
        "parsed": parse(out) if should_parse else None
    }


def parse_ruff_stats(out):
    """Parse ruff --statistics output."""
    stats = {}
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+([A-Z0-9]+)\s", line)
        if m:
            stats[m.group(2)] = int(m.group(1))
    return stats


def parse_pytest(out):
    """Parse pytest summary line."""
    # e.g. "26 failed, 226 passed, 3 warnings in 17.80s"
    m = re.search(r"(?P<failed>\d+)\sfailed,\s(?P<passed>\d+)\spassed.*in\s(?P<secs>[\d\.]+)s", out)
    if not m:
        m = re.search(r"(?P<passed>\d+)\spassed.*in\s(?P<secs>[\d\.]+)s", out)
    if not m:
        # If maxfail stops early, count from "FAILED" lines
        failed_count = len(re.findall(r"^FAILED\s", out, re.MULTILINE))
        # Count dots in first line for rough passed count
        dots_line = out.split('\n')[0] if out else ""
        passed_count = dots_line.count('.')
        if failed_count > 0 or passed_count > 0:
            return {"passed": passed_count, "failed": failed_count, "maxfail_stopped": True}
    return m.groupdict() if m else {"summary": out[-400:]}


def load_json(path):
    """Load JSON file safely."""
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return None


def main():
    """Run comprehensive system health audit."""
    ts = int(time.time())
    print(f"🩺 Running LUKHAS System Health Audit (ts={ts})")
    print("=" * 70)

    results = {}

    # 1) Ruff statistics (exits 1 on findings, so force_parse=True)
    print("\n📊 Running ruff checks...")
    results["ruff_statistics"] = try_run(
        "ruff_stats",
        ["python3", "-m", "ruff", "check", ".", "--statistics"],
        parse=parse_ruff_stats,
        force_parse=True
    )

    results["ruff_count"] = try_run(
        "ruff_count",
        "python3 -m ruff check . --output-format=concise 2>&1 | wc -l",
        parse=lambda s: {"total": int(s.strip()) if s.strip().isdigit() else 0},
        force_parse=True
    )

    # 2) Smoke tests with coverage (exits 1 on failures, so force_parse=True)
    print("\n🧪 Running smoke tests...")
    results["pytest_smoke"] = try_run(
        "pytest_smoke",
        ["python3", "-m", "pytest", "tests/smoke/", "-q", "--tb=no"],
        parse=parse_pytest,
        force_parse=True
    )

    # 3) Unit core tests (exits 1 on failures, so force_parse=True)
    print("\n🔬 Running core unit tests...")
    results["pytest_core"] = try_run(
        "pytest_core",
        ["python3", "-m", "pytest", "tests/unit/", "-q", "--tb=no", "-k", "auth or rate or idempotency or trace"],
        parse=parse_pytest,
        force_parse=True
    )

    # 4) Compat hits
    if (ROOT / "scripts/report_compat_hits.py").exists():
        print("\n📦 Checking compat hits...")
        results["compat_hits"] = try_run(
            "compat_hits",
            ["python3", "scripts/report_compat_hits.py"]
        )

    # 5) OpenAPI validate
    openapi_spec = ROOT / "docs/openapi/lukhas-openapi.json"
    if openapi_spec.exists():
        print("\n🔍 Validating OpenAPI spec...")
        results["openapi_validate"] = try_run(
            "openapi_validate",
            ["python3", "-c",
             "import json,sys,pathlib;"
             "p=pathlib.Path('docs/openapi/lukhas-openapi.json');"
             "d=json.load(open(p));"
             "assert 'openapi' in d and 'paths' in d;"
             "print('ok:', len(d.get('paths',{})),'paths')"],
            parse=lambda s: {"valid": True, "paths": int(s.split()[-2]) if "ok:" in s else 0}
        )
    else:
        results["openapi_validate"] = {"ok": False, "message": "OpenAPI spec not found"}

    # 6) Star rules coverage (optional)
    if (ROOT / "scripts/gen_rules_coverage.py").exists():
        print("\n⭐ Generating star rules coverage...")
        ok, _out, _err, rc = run(["python3", "scripts/gen_rules_coverage.py", "--out", "docs/audits/star_rules_coverage.md"])
        results["star_rules_coverage"] = {"ok": ok, "rc": rc}

    # 7) pip-audit (optional)
    if shutil.which("pip-audit"):
        print("\n🔒 Running pip-audit...")
        results["pip_audit"] = try_run(
            "pip_audit",
            ["pip-audit", "-r", "requirements.txt"]
        )

    # 8) Guardian/RL health check (from /healthz endpoint if API running)
    print("\n🛡️ Checking Guardian & Rate Limiter health...")
    guardian_health = {}
    try:
        import requests
        # Try local dev server first, fall back to other ports
        for port in [8000, 8080, 5000]:
            try:
                resp = requests.get(f"http://localhost:{port}/healthz", timeout=2)
                if resp.status_code == 200:
                    health_data = resp.json()
                    checks = health_data.get("checks", {})

                    # Extract Guardian PDP stats
                    if "guardian_pdp" in checks:
                        pdp = checks["guardian_pdp"]
                        if isinstance(pdp, dict) and pdp.get("available"):
                            guardian_health["pdp"] = {
                                "available": True,
                                "decisions": pdp.get("decisions", 0),
                                "allow_count": pdp.get("allow_count", 0),
                                "deny_count": pdp.get("deny_count", 0),
                                "policy_etag": pdp.get("policy_etag", "unknown"),
                            }
                        else:
                            guardian_health["pdp"] = {"available": False}

                    # Extract Redis backend stats
                    if "redis_backend" in checks:
                        redis = checks["redis_backend"]
                        if isinstance(redis, dict):
                            guardian_health["redis"] = {
                                "available": redis.get("available", False),
                                "connected": redis.get("stats", {}).get("connected", False) if isinstance(redis.get("stats"), dict) else False,
                            }
                        else:
                            guardian_health["redis"] = {"available": False}

                    # Extract rate limiter status
                    if "rate_limiter" in checks:
                        guardian_health["rate_limiter"] = {
                            "available": checks["rate_limiter"]
                        }

                    break  # Found API, stop trying
            except requests.exceptions.RequestException:
                continue  # Try next port

        if not guardian_health:
            guardian_health = {"status": "api_not_running", "note": "Run API to get live Guardian/RL stats"}

    except ImportError:
        guardian_health = {"status": "requests_not_installed", "note": "Install requests to check /healthz"}
    except Exception as e:
        guardian_health = {"status": "error", "error": str(e)}

    results["guardian_rl_health"] = {"ok": bool(guardian_health), "parsed": guardian_health}

    # Assemble summary
    print("\n" + "=" * 70)
    print("📋 Generating summary...")

    # Get git version info
    git_sha = "unknown"
    git_version = "unknown"
    try:
        ok, sha_out, _, _ = run(["git", "rev-parse", "--short=8", "HEAD"])
        if ok:
            git_sha = sha_out.strip()

        ok, ver_out, _, _ = run(["git", "describe", "--tags", "--always"])
        if ok:
            git_version = ver_out.strip()
    except Exception:
        pass

    summary = {
        "version": git_version,
        "git_sha": git_sha,
        "ts": ts,
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "ruff": {
            "stats": results["ruff_statistics"].get("parsed", {}),
            "count": results["ruff_count"].get("parsed", {"total": None})
        },
        "tests": {
            "smoke": results["pytest_smoke"].get("parsed", {}),
            "unit_core": results["pytest_core"].get("parsed", {})
        },
        "compat": results.get("compat_hits", {}),
        "openapi": results.get("openapi_validate", {}),
        "star_rules": results.get("star_rules_coverage", {}),
        "deps": results.get("pip_audit", {}).get("parsed") if results.get("pip_audit") else None,
        "guardian_rl": results.get("guardian_rl_health", {}).get("parsed", {}),
    }

    # Write JSON (both locations for back-compat)
    json_content = json.dumps({"summary": summary, "raw": results}, indent=2)

    json_path = OUTDIR / "latest.json"
    json_path.write_text(json_content)
    print(f"✅ Wrote {json_path}")

    # Back-compat: also write to root audits dir
    json_path_compat = AUDITS_ROOT / "system_health.json"
    json_path_compat.write_text(json_content)
    print(f"✅ Wrote {json_path_compat} (back-compat)")

    # Write Markdown
    smoke_data = summary['tests'].get('smoke') or {}
    smoke_passed = int(smoke_data.get('passed', 0)) if isinstance(smoke_data.get('passed'), (int, str)) else 0
    smoke_failed = int(smoke_data.get('failed', 0)) if isinstance(smoke_data.get('failed'), (int, str)) else 0
    smoke_total = smoke_passed + smoke_failed
    smoke_pct = (smoke_passed / smoke_total * 100) if smoke_total > 0 else 0

    ruff_data = summary['ruff'].get('count') or {}
    ruff_total = ruff_data.get('total', 'N/A')

    md_lines = [
        "# LUKHAS System Health Audit (auto-generated)",
        "",
        f"**Version:** `{summary['version']}` | **Commit:** `{summary['git_sha']}`  ",
        f"**Timestamp:** `{summary['timestamp_iso']}`",
        "",
        "## Summary",
        "",
        f"- **Ruff Total:** {ruff_total} issues",
        f"- **Smoke Tests:** {smoke_passed}/{smoke_total} passing ({smoke_pct:.1f}%)",
        f"- **Unit Core Tests:** {summary['tests']['unit_core']}",
        f"- **OpenAPI:** {summary.get('openapi', {}).get('parsed', 'N/A')}",
        "",
        "## Ruff Statistics",
        "",
        "```"
    ]

    ruff_stats = summary['ruff'].get('stats') or {}
    if ruff_stats:
        for code, count in sorted(ruff_stats.items(), key=lambda x: -x[1]):
            md_lines.append(f"{count:6d}  {code}")
    else:
        md_lines.append("No ruff statistics available")

    md_lines.extend([
        "```",
        "",
        "## Test Results",
        "",
        "###  Smoke Tests",
        ""
    ])

    # Format smoke test results
    if isinstance(smoke_data, dict) and 'passed' in smoke_data:
        md_lines.append(f"- **Status:** {smoke_passed}/{smoke_total} passing ({smoke_pct:.1f}%)")
        md_lines.append(f"- **Passed:** {smoke_passed}")
        md_lines.append(f"- **Failed:** {smoke_failed}")
    else:
        md_lines.append(f"- **Status:** {smoke_data}")

    md_lines.extend([
        "",
        "### Core Unit Tests",
        ""
    ])

    # Format unit test results
    unit_data = summary['tests'].get('unit_core') or {}
    if isinstance(unit_data, dict) and 'summary' in unit_data:
        md_lines.append("```")
        md_lines.append(unit_data['summary'][:500])
        md_lines.append("```")
    else:
        md_lines.append(f"- **Status:** {unit_data}")

    md_lines.extend([
        "",
        "## Compat Hits",
        "",
        f"{summary.get('compat', {}).get('parsed', 'N/A')}",
        ""
    ])

    # Guardian/RL section
    guardian_rl = summary.get('guardian_rl', {})
    md_lines.extend([
        "## Guardian & Rate Limiter Status",
        ""
    ])

    if guardian_rl.get("status") == "api_not_running":
        md_lines.append("⚪ **API not running** - Start API to get live Guardian/RL stats")
    elif guardian_rl.get("status") == "error":
        md_lines.append(f"🔴 **Error:** {guardian_rl.get('error', 'Unknown')}")
    else:
        # PDP stats
        pdp = guardian_rl.get("pdp", {})
        if pdp.get("available"):
            md_lines.extend([
                "### Guardian PDP",
                "- **Status:** ✅ Available",
                f"- **Total Decisions:** {pdp.get('decisions', 0)}",
                f"- **Allow Count:** {pdp.get('allow_count', 0)}",
                f"- **Deny Count:** {pdp.get('deny_count', 0)}",
                f"- **Policy ETag:** `{pdp.get('policy_etag', 'unknown')}`",
                ""
            ])
        else:
            md_lines.extend(["### Guardian PDP", "- **Status:** ⚪ Not configured", ""])

        # Redis stats
        redis = guardian_rl.get("redis", {})
        if redis.get("available"):
            status = "✅ Connected" if redis.get("connected") else "🔴 Disconnected"
            md_lines.extend([
                "### Redis Backend",
                f"- **Status:** {status}",
                ""
            ])
        else:
            md_lines.extend(["### Redis Backend", "- **Status:** ⚪ Not configured", ""])

        # Rate limiter
        rl = guardian_rl.get("rate_limiter", {})
        if rl.get("available"):
            md_lines.extend([
                "### Rate Limiter",
                "- **Status:** ✅ Active",
                ""
            ])
        else:
            md_lines.extend(["### Rate Limiter", "- **Status:** 🔴 Not available", ""])

    md_lines.extend([
        "",
        "---",
        f"*Generated: {summary['timestamp_iso']}*"
    ])

    md_content = "\n".join(md_lines)

    md_path = OUTDIR / "latest.md"
    md_path.write_text(md_content)
    print(f"✅ Wrote {md_path}")

    # Back-compat: also write to root audits dir
    md_path_compat = AUDITS_ROOT / "system_health.md"
    md_path_compat.write_text(md_content)
    print(f"✅ Wrote {md_path_compat} (back-compat)")

    print("\n" + "=" * 70)
    print("🩺 Health Audit Complete!")
    print(f"   Smoke: {smoke_passed}/{smoke_total} ({smoke_pct:.1f}%)")
    print(f"   Ruff:  {ruff_total} issues")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
