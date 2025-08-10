import json
import os

from bridge.connectors import blockchain_bridge


def test_anchor_hash(tmp_path):
    path = tmp_path / "anchor.json"
    os.environ["LUKHAS_BLOCKCHAIN_ANCHOR"] = str(path)
    blockchain_bridge.ANCHOR_LOG = path
    blockchain_bridge.anchor_hash("abc123")
    assert path.exists()
    data = json.loads(path.read_text())
    assert data[0]["data_hash"] == "abc123"
    os.environ.pop("LUKHAS_BLOCKCHAIN_ANCHOR")
