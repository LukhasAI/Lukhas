# Prometheus Metrics Implementation

This document outlines how to use the Prometheus metrics implemented in the `lukhas/observability` module.

## Available Metrics

The following metrics are available for use throughout the LUKHAS application:

- `counter(name, documentation, labelnames=None)`: A counter metric that can be incremented.
- `gauge(name, documentation, labelnames=None)`: A gauge metric that can be set to a specific value.
- `histogram(name, documentation, labelnames=None)`: A histogram metric that can be used to observe the distribution of a set of values.
- `summary(name, documentation, labelnames=None)`: A summary metric that can be used to observe the distribution of a set of values, including quantiles.

All metrics are created using the functions from `observability.prometheus_registry`. This registry ensures that metrics are only created once, even if the module is imported multiple times.

## Usage

To use a metric, import the desired metric type from `observability.prometheus_registry` and create an instance of it.

### Example

```python
from observability.prometheus_registry import counter

# Create a counter metric
my_counter = counter("my_counter", "A counter for my awesome feature.")

# Increment the counter
my_counter.inc()

# Increment the counter by a specific value
my_counter.inc(5)
```

### Labels

All metric types support labels, which can be used to differentiate between different dimensions of the same metric.

```python
from observability.prometheus_registry import gauge

# Create a gauge metric with a "status" label
my_gauge = gauge("my_gauge", "A gauge for my awesome feature.", ["status"])

# Set the gauge for the "success" status
my_gauge.labels("success").set(1)

# Set the gauge for the "failure" status
my_gauge.labels("failure").set(0)
```
