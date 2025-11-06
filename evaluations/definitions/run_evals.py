#!/usr/bin/env python3
"""
Lukhas mini-evals runner (OpenAI-aligned façade).

- Consumes JSONL cases (id, input, expect.contains[], optional tools).
- POSTs to /v1/responses on the Lukhas façade.
- Writes JSON + Markdown summaries in docs/audits/.
- Thresholds & strict mode for CI gating.

Usage:
  python3 evals/run_evals.py --base-url http://localhost:8000 --cases "evals/cases/*.jsonl" --out docs/audits --threshold 0.7
  # CI warn-only (exit 0): omit --strict
  # Gate (exit 1 if below threshold): add --strict
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

try:
    import requests
except ImportError:
    print("[evals] `requests` not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(2)

@dataclass
class Case:
    id: str
    input: str
    expect_contains: List[str]
    tools: List[Dict[str, Any]]

@dataclass
class Result:
    id: str
    ok: bool
    latency_ms: float
    output_text: str

def load_cases(patterns: List[str]) -> List[Case]:
    files: List[str] = []
    for pat in patterns:
        files.extend(glob.glob(pat))
    cases: List[Case] = []
    for fp in sorted(files):
        with open(fp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                cases.append(
                    Case(
                        id=obj.get("id") or Path(fp).stem,
                        input=obj["input"],
                        expect_contains=obj.get("expect", {}).get("contains", []),
                        tools=obj.get("tools", []),
                    )
                )
    return cases

def call_responses(base_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/v1/responses"
    r = requests.post(url, json=payload, timeout=(5, 30))
    r.raise_for_status()
    return r.json()

def run_case(base_url: str, case: Case) -> Result:
    t0 = time.time()
    body = call_responses(base_url, {"input": case.input, "tools": case.tools})
    dt = (time.time() - t0) * 1000.0
    # Compatible with façade shape: body["output"]["text"]
    text = ""
    if isinstance(body, dict):
        out = body.get("output") or {}
        text = out.get("text") or json.dumps(body)  # fallback for alternative shapes
    ok = all(s.lower() in text.lower() for s in case.expect_contains)
    return Result(id=case.id, ok=ok, latency_ms=round(dt, 2), output_text=text[:2000])

def render_md(summary: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Lukhas Mini-Evals\n")
    lines.append(f"**Total:** {summary['total']}  •  **Passed:** {summary['passed']}  •  **Accuracy:** {summary['accuracy']:.1%}\n")
    lines.append(f"**Threshold:** {summary['threshold']:.1%}  •  **Strict:** {summary['strict']}\n")
    lines.append("## Cases\n")
    lines.append("| id | ok | latency_ms | excerpt |")
    lines.append("|---|---:|---:|---|")
    for r in summary["results"]:
        excerpt = (r["output_text"] or "").replace("\n"," ")[:120]
        lines.append(f"| `{r['id']}` | {'✅' if r['ok'] else '❌'} | {r['latency_ms']:.0f} | {excerpt} |")
    lines.append("")
    return "\n".join(lines)

def write_junit_xml(summary: Dict[str, Any], path: Path) -> None:
    # Minimal JUnit for CI (optional)
    from xml.sax.saxutils import escape
    cases = summary["results"]
    failures = [c for c in cases if not c["ok"]]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<testsuite name="lukhas-mini-evals" tests="{len(cases)}" failures="{len(failures)}">']
    for c in cases:
        xml.append(f'  <testcase classname="evals" name="{escape(c["id"])}" time="{c["latency_ms"]/1000.0:.3f}">')
        if not c["ok"]:
            msg = escape((c["output_text"] or "")[:500])
            xml.append(f'    <failure message="expect.contains not satisfied">{msg}</failure>')
        xml.append('  </testcase>')
    xml.append('</testsuite>')
    path.write_text("\n".join(xml), encoding="utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=os.getenv("LUKHAS_BASE_URL", "http://localhost:8000"))
    ap.add_argument("--cases", nargs="+", default=["evals/cases/*.jsonl"])
    ap.add_argument("--out", default="docs/audits")
    ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument("--strict", action="store_true", help="exit 1 if accuracy < threshold")
    ap.add_argument("--junit", action="store_true", help="also write JUnit XML")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_evaluations_definitions_run_evals_py_L127"}

    cases = load_cases(args.cases)
    if not cases:
        print("[evals] no cases found", file=sys.stderr)
        return 2
    results: List[Result] = []
    for c in cases:
        try:
            results.append(run_case(args.base_url, c))
        except Exception as e:
            results.append(Result(id=c.id, ok=False, latency_ms=0.0, output_text=f"[error] {e}"))

    passed = sum(1 for r in results if r.ok)
    total = len(results)
    acc = passed / total if total else 0.0
    summary = {
        "total": total,
        "passed": passed,
        "accuracy": acc,
        "threshold": args.threshold,
        "strict": bool(args.strict),
        "base_url": args.base_url,
        "results": [asdict(r) for r in results],
    }

    # Write artifacts
    (out / "evals_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "evals_report.md").write_text(render_md(summary), encoding="utf-8")
    if args.junit:
        write_junit_xml(summary, out / "evals_report.junit.xml")

    print(f"[evals] accuracy={acc:.1%} passed={passed}/{total} threshold={args.threshold:.1%}")
    if args.strict and acc < args.threshold:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
