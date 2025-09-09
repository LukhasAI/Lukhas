import importlib
import pathlib

import pytest
import yaml

OPS = pathlib.Path("ops/matriz.yaml")
LANES = []
if OPS.exists():
    data = yaml.safe_load(OPS.read_text())
    for lane in data.get("lanes", []):
        root = lane.get("root", "").rstrip("/")
        if root and pathlib.Path(root).exists():
            pkg = root.strip("/").split("/")[0]
            LANES.append((lane["name"], pkg))


@pytest.mark.parametrize("lane,pkg", LANES)
def test_lane_imports_have_file(lane, pkg):
    mod = importlib.import_module(pkg)
    # Assertion that something real loaded
    assert hasattr(mod, "__file__"), f"{pkg} missing __file__"