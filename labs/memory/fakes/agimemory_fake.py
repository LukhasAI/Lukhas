from typing import Any, Optional

from lukhas.memory.contracts import AGIMemoryProtocol
from lukhas.memory.folds.fold_engine import MemoryFold, MemoryPriority, MemoryType


class AGIMemoryFake(AGIMemoryProtocol):
    def __init__(self) -> None:
        self.kv = {}
        self.folds: dict = {}

    def put(self, key: str, value: Any) -> None:
        self.kv[key] = value

    def get(self, key: str) -> Any:
        return self.kv.get(key)

    def fold_open(self, *, parent_id: Optional[str] = None) -> str:
        fid = f"F{len(self.folds)+1:06d}"
        self.folds[fid] = []
        return fid

    def fold_append(self, fold_id: str, item: Any) -> None:
        self.folds[fold_id].append(item)

    def fold_close(self, fold_id: str) -> dict:
        items = self.folds.get(fold_id, [])
        lineage = hash(tuple(str(i) for i in items))
        return {"fold_id": fold_id, "count": len(items), "lineage": lineage}

    def add_fold(self, key: str, content: any, memory_type: MemoryType, priority: MemoryPriority, owner_id: str = None, tags: list = None) -> MemoryFold:
        if key in self.folds:
            raise ValueError(f"Fold with key '{key}' already exists.")
        fold = MemoryFold(key=key, content=content, memory_type=memory_type, priority=priority, owner_id=owner_id)
        if tags:
            for tag in tags:
                fold.add_tag(tag)
        self.folds[key] = fold
        return fold

    def get_fold(self, key: str) -> MemoryFold:
        return self.folds.get(key)

    async def search_folds(self, query: str, **kwargs) -> list:
        # A simple mock implementation for search
        return [k for k, v in self.folds.items() if query in str(v.content)]

    async def retrieve_by_emotion(self, emotion: str, **kwargs) -> list:
        # A simple mock implementation for emotion retrieval
        return [k for k, v in self.folds.items() if hasattr(v, 'emotional_context') and emotion in str(v.emotional_context)]

    async def consolidate_memories(self, **kwargs) -> dict:
        return {"status": "ok", "consolidated": len(self.folds)}

    async def optimize_storage(self, **kwargs) -> dict:
        return {"status": "ok", "optimized": len(self.folds)}
