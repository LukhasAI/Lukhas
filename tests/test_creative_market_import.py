from pathlib import Path

from labs.core.symbolic.creative_market import CreativeMarket


def test_import_items_round_trip(tmp_path: Path) -> None:
    # ΛTAG: market_replay_test
    market_file = tmp_path / "market.jsonl"
    market = CreativeMarket(market_file)
    market.export_item("hello", "text")
    items = market.import_items()
    assert items and items[0].content == "hello"
