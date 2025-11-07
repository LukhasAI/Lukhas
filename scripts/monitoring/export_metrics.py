import argparse

from datadog import statsd


class Metrics:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def increment(self, metric_name, tags=None):
        if self.dry_run:
            print(f"[DRY RUN] Incrementing metric: {metric_name}, tags: {tags}")
        else:
            statsd.increment(metric_name, tags=tags)

    def gauge(self, metric_name, value, tags=None):
        if self.dry_run:
            print(f"[DRY RUN] Setting gauge: {metric_name}, value: {value}, tags: {tags}")
        else:
            statsd.gauge(metric_name, value, tags=tags)

    def histogram(self, metric_name, value, tags=None):
        if self.dry_run:
            print(f"[DRY RUN] Recording histogram: {metric_name}, value: {value}, tags: {tags}")
        else:
            statsd.histogram(metric_name, value, tags=tags)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export metrics to Datadog.')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (do not send metrics to Datadog)')
    args = parser.parse_args()

    metrics = Metrics(dry_run=args.dry_run)

    # Example usage
    metrics.increment('lukhas.wavec.snapshot.count', tags=['env:dev'])
    metrics.gauge('lukhas.wavec.rollback.rate', 0.01, tags=['env:dev'])
    metrics.histogram('lukhas.wavec.snapshot.latency', 123, tags=['env:dev'])
    metrics.increment('lukhas.lane_guard.failures', tags=['env:dev'])
