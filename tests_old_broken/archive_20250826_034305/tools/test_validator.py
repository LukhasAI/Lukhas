import json, time, uuid, importlib.util, pathlib
root = pathlib.Path(".").resolve()
val_path = root/"MATRIZ/utils/matriz_validate.py"
spec = importlib.util.spec_from_file_location("matriz_validate", val_path)
mv = importlib.util.module_from_spec(spec); spec.loader.exec_module(mv)

def node(schema_ref):
    return {
      "version": 1,
      "id": f"LT-{uuid.uuid4()}",
      "type": "HYPOTHESIS",
      "state": {"confidence": 0.5, "salience": 0.5},
      "timestamps": {"created_ts": int(time.time()*1000)},
      "provenance": {
        "producer": "smoke.test",
        "capabilities": ["test"],
        "tenant": "demo",
        "trace_id": "LT-TEST",
        "consent_scopes": ["demo:ok"]
      },
      "schema_ref": schema_ref
    }

nodes = [
  node("lukhas://schemas/matriz_node_v1.json"),   # new
  node("lukhas://schemas/matada_node_v1.json"),   # legacy alias
]
mv.validate_nodes(nodes)
print("Validator accepts new and legacy schema_ref ✅")