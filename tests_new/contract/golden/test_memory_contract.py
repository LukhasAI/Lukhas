import json

import pytest


@pytest.mark.no_mock
def test_memory_dump_contract(tmp_path):
    p = tmp_path / "dump.json"
    from lukhas.memory import dump_state

    dump_state(str(p))  # must write a real file
    got = json.loads(p.read_text())
    assert {"version", "folds", "checksum"} <= got.keys()
    assert isinstance(got["folds"], int) and got["folds"] >= 0
    assert isinstance(got["checksum"], str) and len(got["checksum"]) >= 8