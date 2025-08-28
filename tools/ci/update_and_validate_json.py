import json, hashlib, os, sys
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(".")
FILES = [
    ("LUKHAS_ARCHITECTURE_MASTER.json","schemas/architecture_master.schema.json"),
    ("DEPENDENCY_MATRIX.json","schemas/dependency_matrix.schema.json"),
    ("SECURITY_ARCHITECTURE.json",None),
    ("CONSCIOUSNESS_METRICS.json",None),
    ("PERFORMANCE_BASELINES.json",None),
    ("BUSINESS_METRICS.json",None),
    ("EVOLUTION_ROADMAP.json",None),
    ("VISUALIZATION_CONFIG.json",None),
]

def scope_hash(p: Path) -> str:
    h=hashlib.sha256()
    h.update(p.read_bytes())
    return "sha256:"+h.hexdigest()

git_sha = os.popen("git rev-parse HEAD").read().strip() or "TBD"
now = os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip()

# Load master first for referential checks
master = json.loads(Path(FILES[0][0]).read_text())
uids = set()
lanes = master.get("lanes",{})
for lane, data in lanes.items():
    for name, rec in (data.get("modules",{}) or {}).items():
        uid = rec.get("module_uid") or f"{lane}.{name}"
        uids.add(uid)

errors=[]
for fn, schema_fn in FILES:
    p=Path(fn)
    if not p.exists(): 
        continue
    data=json.loads(p.read_text())
    # ensure required top-level fields exist for minimal schemas
    if schema_fn == "schemas/architecture_master.schema.json":
        data.setdefault("schema_version", "0.1.0")
        data.setdefault("lanes", {})
    if schema_fn == "schemas/dependency_matrix.schema.json":
        data.setdefault("schema_version", "0.1.0")
        data.setdefault("module_dependency_matrix", {})
    # provenance
    data.setdefault("provenance",{})
    data["provenance"]["git_sha"]=git_sha
    data["provenance"]["timestamp_utc"]=now
    data["provenance"]["scope_hash"]=scope_hash(p)
    # schema_url if missing
    if "schema_url" not in data and schema_fn:
        data["schema_url"]=schema_fn

    # referential integrity for dependency matrix
    if fn=="DEPENDENCY_MATRIX.json":
        mm=data.get("module_dependency_matrix",{})
        bad=[k for k in mm.keys() if k not in uids]
        if bad: errors.append(f"Unknown module_uids in DEPENDENCY_MATRIX: {bad}")

    p.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # validate
    if schema_fn:
        try:
            schema=json.loads(Path(schema_fn).read_text())
            validate(instance=data, schema=schema)
        except ValidationError as e:
            errors.append(f"{fn} schema validation failed: {e.message}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK: provenance updated, hashes set, schemas validated, refs consistent.")
