import json, pathlib
from MATRIZ.utils.matriz_validate import validate_node

def test_examples_validate():
    root = pathlib.Path(__file__).resolve().parents[1]
    for f in (root / "MATRIZ" / "examples").glob("*.json"):
        node = json.loads(f.read_text())
        validate_node(node)