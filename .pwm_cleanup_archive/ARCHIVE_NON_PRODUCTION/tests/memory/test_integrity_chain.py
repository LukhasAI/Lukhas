import json

from memory.fold_engine import MemoryIntegrityLedger


def test_integrity_chain(tmp_path):
    MemoryIntegrityLedger.LEDGER_PATH = str(tmp_path / "ledger.jsonl")
    MemoryIntegrityLedger._last_hash = None
    MemoryIntegrityLedger.log_fold_transition("m1", "create", {}, {"a": 1})
    MemoryIntegrityLedger.log_fold_transition("m1", "update", {"a": 1}, {"a": 2})
    with open(MemoryIntegrityLedger.LEDGER_PATH) as f:
        lines = [json.loads(l) for l in f]
    assert lines[1]["prev_hash"] == lines[0]["entry_hash"]
