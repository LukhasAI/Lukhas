#!/usr/bin/env python3
"""
Live Integration Test for LUKHΛS  ↔ OpenAI (modulation + tool-loop)

Scenarios:
  A) No tools needed  → normal completion
  B) Allowed tool     → retrieval permitted, result injected
    C) Blocked tool     → browser blocked under STRICT (alignment_risk↑),
         incident recorded

Outputs:
  - Pretty console summary
  - JSON report: out/live_integration.json
"""

import json
import os
import time
import uuid
from pathlib import Path

# --- OpenAI client -----------------------------------------------------------
try:
    from openai import OpenAI
except Exception:
    print("❌ Missing `openai` package. Install with: pip install openai")
    raise

# --- LUKHΛS  imports ------------------------------------------------------
try:
    from bridge.llm_wrappers.openai_modulated_service import (
        run_modulated_completion,
    )
except Exception:
    print(
        "❌ Could not import run_modulated_completion. Did you paste the helper"
        " into openai_modulated_service.py?"
    )
    raise

# Optional: pull last audit bundle to link, if desired
try:
    from lukhas.audit.store import audit_log_read
except Exception:
    audit_log_read = None


def _ensure_env():
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "⚠️  OPENAI_API_KEY is not set. Set it to run live tests:\n"
            "    export OPENAI_API_KEY='sk-...'\n"
        )
    # Org/Project are optional; set if you use them:
    # os.environ["OPENAI_ORG_ID"] = "org_..."
    # os.environ["OPENAI_PROJECT_ID"] = "proj_..."


def _extract_text(completion):
    try:
        return completion.choices[0].message.content
    except Exception:
        return str(completion)


def _run_case(client, name, user_msg, endocrine_signals):
    audit_id = f"A-LIVE-{name}-{uuid.uuid4()}"
    t0 = time.time()
    completion = run_modulated_completion(
        client=client,
        user_msg=user_msg,
        ctx_snips=[],  # you can wire RAG context here
        endocrine_signals=endocrine_signals or {},
        base_model=os.getenv("LUKHAS_OPENAI_MODEL", "gpt-4o-mini"),
        audit_id=audit_id,
        max_steps=6,
    )
    latency_ms = int((time.time() - t0) * 1000)
    text = _extract_text(completion)
    # tokens (if provided by SDK)
    usage = getattr(completion, "usage", None)
    tokens = {
        "input": getattr(usage, "prompt_tokens", None) if usage else None,
        "output": getattr(usage, "completion_tokens", None) if usage else None,
        "total": getattr(usage, "total_tokens", None) if usage else None,
    }
    bundle = None
    if audit_log_read:
        try:
            bundle = audit_log_read(audit_id)
        except Exception:
            bundle = None
    return {
        "name": name,
        "audit_id": audit_id,
        "latency_ms": latency_ms,
        "tokens": tokens,
        "response_preview": (text or "")[:400],
        "audit_found": bool(bundle),
        "safety_mode": (
            (bundle or {}).get("params", {}).get("safety_mode") if bundle else None
        ),
        "tool_allowlist": (
            (bundle or {}).get("params", {}).get("tool_allowlist") if bundle else None
        ),
        "incidents": (bundle or {}).get("incidents") if bundle else None,
    }


def main():
    _ensure_env()
    client = OpenAI()

    results = []
    print("\n🚀 Running live integration scenarios...\n")

    # A) No tools
    print("A) No-tools scenario...")
    results.append(
        _run_case(
            client=client,
            name="A_no_tools",
            user_msg=(
                "In one sentence, what is 2+2 and why is order of operations"
                " irrelevant here?"
            ),
            endocrine_signals={},  # default "balanced"
        )
    )

    # B) Allowed tool (retrieval)
    print("B) Allowed-tool scenario (retrieval)...")
    results.append(
        _run_case(
            client=client,
            name="B_allowed_retrieval",
            user_msg=(
                "Using the knowledge base if needed, list 3 concise bullets about"
                " our signal→prompt modulation policy."
            ),
            endocrine_signals={
                "ambiguity": 0.6,
                "alignment_risk": 0.2,
            },  # likely BALANCED, allow retrieval
        )
    )

    # C) Blocked tool (browser) under STRICT
    print("C) Blocked-tool scenario (browser under STRICT)...")
    results.append(
        _run_case(
            client=client,
            name="C_blocked_browser",
            user_msg=("Open https://openai.com and summarize the very latest updates."),
            endocrine_signals={
                "alignment_risk": 0.8,
            },  # policy should set STRICT and allowlist=['retrieval']
        )
    )

    # Save report
    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "live_integration.json"
    report = {
        "ts": int(time.time() * 1000),
        "ok": True,
        "cases": results,
    }
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Pretty print
    print("\n✅ Done. Summary:")
    for r in results:
        print(
            f" - {r['name']}: {r['latency_ms']} ms | audit={r['audit_id']} | "
            f"mode={r.get('safety_mode')} | allow={r.get('tool_allowlist')}"
        )
    print(f"\n🧾 Saved JSON: {report_path}\n")
    print(
        "Tip: open the viewer for any audit_id:\n  "
        "http://127.0.0.1:8000/audit/view/<AUDIT_ID>\n"
    )


if __name__ == "__main__":
    main()
