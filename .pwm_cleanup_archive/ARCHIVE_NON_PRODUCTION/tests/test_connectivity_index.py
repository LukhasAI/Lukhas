import os

from scripts.connectivity import generate_connectivity_index


def test_connectivity_index(tmp_path):
    fixture_dir = os.path.join(os.path.dirname(__file__), "connectivity", "fixtures")
    index = generate_connectivity_index(fixture_dir, repo_root=os.getcwd())
    files = {f["path"]: f for f in index["files"]}
    module_a = files[
        os.path.relpath(os.path.join(fixture_dir, "module_a.py"), os.getcwd())
    ]
    module_b = files[
        os.path.relpath(os.path.join(fixture_dir, "module_b.py"), os.getcwd())
    ]

    symbols_a = {s["name"]: s for s in module_a["symbols"]}
    assert symbols_a["A"]["used"] is True
    assert symbols_a["foo"]["used"] is False
    assert symbols_a["A"]["used_by"] != []

    symbols_b = {s["name"]: s for s in module_b["symbols"]}
    assert symbols_b["B"]["used"] is False
