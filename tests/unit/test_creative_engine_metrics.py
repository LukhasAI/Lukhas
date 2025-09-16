from contextlib import ExitStack

from products.content.poetica.creativity_engines.creative_engine import (
    ACTIVE_GENERATORS,
    CREATIVE_REQUESTS_TOTAL,
    HAIKU_GENERATION_TIME,
)


def test_metrics_support_basic_operations() -> None:
    with ExitStack() as stack:
        stack.enter_context(HAIKU_GENERATION_TIME.time())

    CREATIVE_REQUESTS_TOTAL.labels(type="haiku", status="success").inc()
    ACTIVE_GENERATORS.set(1)
