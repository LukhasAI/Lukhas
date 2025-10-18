from pathlib import Path

from tools.reports.ai_audit_dashboard import generate_dashboard


def test_generate_dashboard_from_csv(tmp_path: Path):
    csv_path = tmp_path / "evidence_ledger.csv"
    out_md = tmp_path / "ai_audit_summary.md"

    csv_path.write_text(
        "timestamp_utc,trace_id,component,task_type,success,latency_ms,request_size,prompt_hash,output_len\n"
        "2025-09-14T10:00:00Z,t1,C1,general,True,12.0,10,aaaa,100\n"
        "2025-09-14T10:01:00Z,t2,C2,code,False,25.0,20,bbbb,0\n"
        "2025-09-14T10:02:00Z,t3,C1,web,True,5.0,30,cccc,50\n"
    )

    total = generate_dashboard(csv_path, out_md)
    assert total == 3
    text = out_md.read_text()
    assert "AI Interface Audit Summary" in text
    assert "Top Components" in text
    assert "C1" in text and "C2" in text
