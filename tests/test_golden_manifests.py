import json, glob
from jsonschema import Draft7Validator

def test_golden_manifests_validate():
    schema = json.load(open("schemas/matriz_module_compliance.schema.json"))
    v = Draft7Validator(schema)
    for f in glob.glob("tests/manifests/golden/*.json"):
        data = json.load(open(f))
        errs = list(v.iter_errors(data))
        assert not errs, f"{f} invalid: {errs[:2]}"
