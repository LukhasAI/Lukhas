"""
Lightweight smoke check for LUKHAS PWM
--------------------------------------
Validates app import, feedback health, Signal Bus publish, and
offline safety logic.
Supports optional --json output for CI artifacts.
Exit code is non-zero on failure.
"""

from __future__ import annotations

import sys
import json
import time
import asyncio
import argparse
import traceback


def main() -> int:
    ok = True
    results: dict = {"steps": []}

    # Ensure repo root on sys.path
    if "" not in sys.path:
        sys.path.insert(0, "")

    # 1) Import FastAPI app (timed)
    try:
        t0 = time.monotonic()
        from serve.main import app  # type: ignore

        t1 = time.monotonic()

        route_paths = sorted(
            {
                getattr(r, "path", None)
                for r in getattr(app, "routes", [])
                if hasattr(r, "path")
            }
        )
        results["app"] = {
            "loaded": True,
            "route_count": len(route_paths),
            "routes_sample": route_paths[:20],
        }
        results["routes"] = {"count": len(route_paths)}
        results.setdefault("timings", {})["import_app_ms"] = round((t1 - t0) * 1000, 2)
        results["steps"].append("import_app")
    except Exception as e:
        ok = False
        results["app"] = {
            "loaded": False,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    # 2) /feedback/health via TestClient (timed)
    try:
        if results.get("app", {}).get("loaded"):
            from fastapi.testclient import TestClient  # type: ignore

            client = TestClient(app)  # type: ignore[name-defined]
            t0 = time.monotonic()
            resp = client.get("/feedback/health")
            t1 = time.monotonic()
            results["feedback_health"] = {
                "status_code": getattr(resp, "status_code", None),
                "json": (
                    resp.json()
                    if resp.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else getattr(resp, "text", "")
                ),
            }
            results.setdefault("timings", {})["feedback_health_ms"] = round(
                (t1 - t0) * 1000, 2
            )
            if getattr(resp, "status_code", None) != 200:
                ok = False
            results["steps"].append("feedback_health")
        else:
            results["feedback_health"] = {
                "skipped": True,
                "reason": "app not loaded",
            }
    except Exception as e:
        ok = False
        results["feedback_health"] = {
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    # 3) Import LLM wrapper symbol
    try:
        from bridge.llm_wrappers.openai_modulated_service import (
            OpenAIModulatedService,
        )

        assert OpenAIModulatedService is not None
        results["llm_wrapper_import"] = {"imported": True}
        results["steps"].append("llm_wrapper_import")
    except Exception as e:
        ok = False
        results["llm_wrapper_import"] = {
            "imported": False,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    # 4) SignalBus sanity
    try:
        from orchestration.signals.signal_bus import (
            get_signal_bus,
            Signal,
            SignalType,
        )

        bus = get_signal_bus()
        before = dict(bus.get_metrics())
        published = bus.publish(
            Signal(name=SignalType.STRESS, level=0.5, source="smoke")
        )
        after = dict(bus.get_metrics())
        results["signal_bus"] = {
            "published": bool(published),
            "signals_published_diff": after.get("signals_published", 0)
            - before.get("signals_published", 0),
            "active_signals": after.get("active_signals"),
            "subscribers": after.get("subscribers"),
        }
        results["steps"].append("signal_bus")
    except Exception as e:
        # Do not fail the whole smoke on bus errors, but record
        results["signal_bus"] = {"ok": False, "error": str(e)}

    # 5) Offline blocked-tool governance test
    try:
        from orchestration.signals.homeostasis import ModulationParams

        class DummyClient:
            def __init__(self) -> None:
                self.calls = 0

            async def chat_completion(self, *_, **__):
                self.calls += 1
                if self.calls == 1:
                    return {
                        "choices": [
                            {
                                "message": {
                                    "content": None,
                                    "tool_calls": [
                                        {
                                            "id": "call_1",
                                            "type": "function",
                                            "function": {
                                                "name": "forbidden_tool",
                                                "arguments": {"x": 1},
                                            },
                                        }
                                    ],
                                }
                            }
                        ]
                    }
                return {"choices": [{"message": {"content": "ok"}}]}

        # Reuse imported symbol if available; otherwise skip
        try:
            OpenAIModulatedService  # noqa: F401  # type: ignore
        except NameError:
            from bridge.llm_wrappers.openai_modulated_service import (
                OpenAIModulatedService,  # type: ignore
            )

        svc = OpenAIModulatedService(client=DummyClient())
        params = ModulationParams(
            tool_allowlist=["allowed_tool"],
            retrieval_k=0,
        )

        async def _run_block_test():
            return await svc.generate(
                prompt="test",
                context={"additional_context": "smoke"},
                params=params,
                stream=False,
            )

        t0 = time.monotonic()
        out = asyncio.run(_run_block_test())
        t1 = time.monotonic()
        ta = out.get("tool_analytics", {})
        incidents = ta.get("incidents", [])
        tightened = ta.get("safety_tightened", False)
        results["llm_block_test"] = {
            "incidents": len(incidents),
            "tightened": bool(tightened),
            "elapsed_ms": round((t1 - t0) * 1000, 2),
        }
        results["offline_governance"] = {
            "incidents": len(incidents),
            "tightened": bool(tightened),
        }
        if not incidents or not tightened:
            ok = False
        results["steps"].append("llm_block_test")
    except Exception as e:
        ok = False
        results["llm_block_test"] = {
            "ok": False,
            "error": str(e),
            "trace": traceback.format_exc(),
        }

    payload = {"ok": ok, **results}

    # Optional JSON output for CI
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--json", dest="json_path")
    try:
        args, _ = parser.parse_known_args()
    except SystemExit:
        args = argparse.Namespace(json_path=None)

    if getattr(args, "json_path", None):
        try:
            with open(args.json_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, sort_keys=True)
        except Exception:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
