
import unittest

from observability.prometheus_registry import LUKHAS_REGISTRY, counter, gauge, histogram, summary


class TestPrometheusMetrics(unittest.TestCase):
    def setUp(self):
        # Clear the cache and registry before each test to ensure isolation
        from observability import prometheus_registry
        prometheus_registry._CACHE.clear()

        # Unregister all collectors from the registry
        for collector in list(LUKHAS_REGISTRY._collector_to_names.keys()):
            LUKHAS_REGISTRY.unregister(collector)


    def test_counter_creation(self):
        test_counter = counter("test_counter", "A counter for testing.")
        self.assertIsNotNone(test_counter)
        metric_names = [m.name for m in LUKHAS_REGISTRY.collect()]
        self.assertIn("test_counter", metric_names)

    def test_gauge_creation(self):
        test_gauge = gauge("test_gauge", "A gauge for testing.")
        self.assertIsNotNone(test_gauge)
        metric_names = [m.name for m in LUKHAS_REGISTRY.collect()]
        self.assertIn("test_gauge", metric_names)

    def test_counter_increment(self):
        test_counter = counter("test_inc_counter", "A counter for testing increment.")
        test_counter.inc()

        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertIn("test_inc_counter", metrics)
        self.assertEqual(metrics["test_inc_counter"].samples[0].value, 1.0)

        test_counter.inc(5)
        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertEqual(metrics["test_inc_counter"].samples[0].value, 6.0)

    def test_gauge_set(self):
        test_gauge = gauge("test_set_gauge", "A gauge for testing set.")
        test_gauge.set(42)

        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertIn("test_set_gauge", metrics)
        self.assertEqual(metrics["test_set_gauge"].samples[0].value, 42.0)

        test_gauge.set(123)
        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertEqual(metrics["test_set_gauge"].samples[0].value, 123.0)

    def test_duplicate_metric_noop(self):
        # The registry's _get_or_create has a try-except ValueError that returns a noop
        # To trigger this, we have to bypass the cache. We can't do that easily,
        # so we'll simulate a different kind of registration clash.

        # First, create a metric.
        c1 = counter("duplicate_counter", "First counter.")
        c1.inc()

        # Now, try to create another metric of a DIFFERENT type but SAME name,
        # which prometheus_client will raise a ValueError for.
        # Our registry should catch this and return a no-op metric.
        g1 = gauge("duplicate_counter", "A gauge with a clashing name.")

        # The original counter should still be registered and have its value.
        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertIn("duplicate_counter", metrics)
        self.assertEqual(metrics["duplicate_counter"].type, "counter")
        self.assertEqual(metrics["duplicate_counter"].samples[0].value, 1.0)

        # The new metric 'g1' should be a no-op, so calling its methods should do nothing.
        g1.set(100)
        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertEqual(metrics["duplicate_counter"].samples[0].value, 1.0) # Unchanged

    def test_histogram_observe(self):
        test_histogram = histogram("test_histogram", "A histogram for testing.")
        test_histogram.observe(0.5)

        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertIn("test_histogram", metrics)

        samples = {s.name: s.value for s in metrics["test_histogram"].samples}
        self.assertEqual(samples["test_histogram_sum"], 0.5)
        self.assertEqual(samples["test_histogram_count"], 1.0)

    def test_summary_observe(self):
        test_summary = summary("test_summary", "A summary for testing.")
        test_summary.observe(1.5)

        metrics = {m.name: m for m in LUKHAS_REGISTRY.collect()}
        self.assertIn("test_summary", metrics)

        samples = {s.name: s.value for s in metrics["test_summary"].samples}
        self.assertEqual(samples["test_summary_sum"], 1.5)
        self.assertEqual(samples["test_summary_count"], 1.0)

if __name__ == '__main__':
    unittest.main()
