"""LUKHAS Creative Market Prototype.

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Exports generated art and literature with glyph tagging.
Tracks symbolic reputation for each creative item.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

try:  # ΛTAG: logger_fallback
    import structlog

    logger = structlog.get_logger(__name__).bind(module="creative_market")
except ModuleNotFoundError:  # pragma: no cover - structlog optional
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("creative_market")

from ..symbolic.glyph_engine import evaluate_resonance, generate_glyph
from ..symbolic_core.symbolic_glyph_hash import compute_glyph_hash
from ..tagging.tagging_system import DeduplicationCache, SimpleTagResolver, Tag


@dataclass
class CreativeItem:
    """Represents a piece of creative content."""

    item_id: str
    content: str
    item_type: str
    tag: Tag
    glyph: str
    symbolic_value: float
    reputation: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CreativeMarket:
    """Manage export of creative works with symbolic reputation."""

    def __init__(self, export_path: Path, resolver: SimpleTagResolver | None = None) -> None:
        self.export_path = Path(export_path)
        self.export_path.parent.mkdir(parents=True, exist_ok=True)
        self.resolver = resolver or SimpleTagResolver()
        self.cache = DeduplicationCache()
        self.reputation_store: dict[str, float] = {}
        logger.info("market_initialized", export=str(self.export_path))

    # ΛTAG: tag_generation

    def _create_tag(self, content: str) -> Tag:
        tag = self.resolver.resolve_tag(content)
        return self.cache.store(tag)

    # ΛTAG: glyph_attachment

    def _generate_glyph(self) -> str:
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tier_level": 0,
        }
        return generate_glyph(state)

    # ΛTAG: symbolic_value_computation

    def _compute_value(self, tag: Tag) -> float:
        return evaluate_resonance(tag.vector)

    # ΛTAG: symbolic_reputation

    def update_reputation(self, item_id: str, delta: float) -> None:
        self.reputation_store[item_id] = max(0.0, self.reputation_store.get(item_id, 1.0) + delta)
        logger.info(
            "reputation_updated",
            item=item_id,
            reputation=self.reputation_store[item_id],
        )

    # ΛTAG: export_logic

    def export_item(self, content: str, item_type: str) -> CreativeItem:
        tag = self._create_tag(content)
        glyph = self._generate_glyph()
        value = self._compute_value(tag)
        item_id = compute_glyph_hash(glyph)[:12]
        reputation = self.reputation_store.get(item_id, 1.0)
        item = CreativeItem(item_id, content, item_type, tag, glyph, value, reputation)
        # Store initial reputation
        self.reputation_store[item_id] = reputation

        with self.export_path.open("a", encoding="utf-8") as f:
            json.dump(
                {
                    "item_id": item.item_id,
                    "content": item.content,
                    "item_type": item.item_type,
                    "tag_id": item.tag.id,
                    "glyph": item.glyph,
                    "symbolic_value": item.symbolic_value,
                    "reputation": item.reputation,
                    "created_at": item.created_at,
                },
                f,
            )
            f.write("\n")

        logger.info("item_exported", item=item.item_id)
        return item

    # ΛTAG: market_replay
    def import_items(self) -> list[CreativeItem]:
        """Import previously exported items for replay analysis."""
        items: list[CreativeItem] = []
        if not self.export_path.exists():
            return items
        with self.export_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("replay_import_failed", line=line)
                    continue
                tag = self._create_tag(data["content"])
                item = CreativeItem(
                    data["item_id"],
                    data["content"],
                    data.get("item_type", "unknown"),
                    tag,
                    data.get("glyph", ""),
                    data.get("symbolic_value", 0.0),
                    data.get("reputation", 1.0),
                    data.get("created_at", datetime.now(timezone.utc).isoformat()),
                )
                items.append(item)
                self.reputation_store[item.item_id] = item.reputation
        logger.info("market_replay_imported", count=len(items))
        return items


__all__ = ["CreativeItem", "CreativeMarket"]
