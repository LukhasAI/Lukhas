from tagging import DeduplicationCache, SimpleTagResolver


def test_deduplication_cache():
    resolver = SimpleTagResolver()
    cache = DeduplicationCache()
    tag1 = cache.store(resolver.resolve_tag("hello"))
    tag2 = cache.store(resolver.resolve_tag("hello"))
    assert tag1 is tag2
    assert len(cache) == 1
