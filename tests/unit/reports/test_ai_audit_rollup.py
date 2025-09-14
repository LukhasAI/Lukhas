from pathlib import Path
import json

from tools.reports.ai_audit_rollup import normalize_event, append_to_ledger, rollup


def test_normalize_event_fields():
    rec = {
        "trace_id": "abc",
        "component": "Comp",
        "task_type": "general",
        "success": True,
        "latency_ms": 12.5,
        "request_size": 42,
        "prompt_hash": "deadbeef",
        "output_len": 77,
    }
    out = normalize_event(rec)
    assert out["trace_id"] == "abc"
    assert out["component"] == "Comp"
    assert out["success"] is True


def test_rollup_reads_jsonl_and_appends_csv(tmp_path: Path):
    jsonl = tmp_path / "ai_interface_events.jsonl"
    csv_out = tmp_path / "evidence_ledger.csv"

    # Write two events
    events = [
        {
            "trace_id": "t1",
            "component": "C1",
            "task_type": "general",
            "success": True,
            "latency_ms": 5.0,
            "request_size": 10,
            "prompt_hash": "aaaa",
            "output_len": 4,
        },
        {
            "trace_id": "t2",
            "component": "C2",
            "task_type": "code",
            "success": False,
            "latency_ms": 20.0,
            "request_size": 100,
            "prompt_hash": "bbbb",
            "output_len": 0,
        },
    ]
    with jsonl.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    added = rollup(jsonl, csv_out)
    assert added == 2
    text = csv_out.read_text()
    assert "t1" in text and "t2" in text
