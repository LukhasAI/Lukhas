from consciousness.dream.expand import sentinel


def test_detect_blocks_high_fear():
    snap = {"emotional_context": {"fear": 0.9}}
    assert sentinel.detect(snap)


def test_detect_allows_safe():
    snap = {"emotional_context": {"fear": 0.1}}
    assert not sentinel.detect(snap)
