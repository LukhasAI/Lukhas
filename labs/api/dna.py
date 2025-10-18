from fastapi import APIRouter, Query

from dna.memory_inmem import InMemoryHelix
from migration.legacy_jsonl import LegacyJSONL

router = APIRouter(prefix="/dna", tags=["DNA"])

# Wire real instances via DI in the future; for now, simple statics for smoke
LEGACY = LegacyJSONL()
DNA = InMemoryHelix()


@router.get("/health")
def dna_health():
    return {"ok": True, "legacy_count": LEGACY.count(), "dna_keys": len(DNA._store)}


@router.get("/compare")
def dna_compare(key: str = Query(...)):
    return {"key": key, "legacy": LEGACY.read(key), "dna": DNA.read(key)}
