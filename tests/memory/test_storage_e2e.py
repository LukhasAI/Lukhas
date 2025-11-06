import time

import pytest

from memory.backends.pgvector_store import PgVectorStore
from memory.indexer import Indexer
from memory.memory_orchestrator import MemoryOrchestrator


class DummyConn: ...  # TODO: mock/fixture

@pytest.fixture
def orch():
    store = PgVectorStore(DummyConn(), dim=8)  # small dim for tests
    return MemoryOrchestrator(Indexer(store))

@pytest.mark.asyncio
async def test_upsert_and_query_roundtrip(orch):
    doc_id = await orch.add_event("hello world", {"lane": "labs"})
    assert isinstance(doc_id, str)
    res = orch.query("hello", k=3)
    assert isinstance(res, list)

@pytest.mark.slow
def test_search_p95_under_100ms(orch):
    # TODO: create N docs first
    lat = []
    for _ in range(200):
        t0 = time.perf_counter_ns()
        orch.query("hello", k=5)
        lat.append(time.perf_counter_ns() - t0)
    lat.sort()
    p95 = lat[int(0.95 * len(lat))] / 1_000_000
    assert p95 < 100.0
