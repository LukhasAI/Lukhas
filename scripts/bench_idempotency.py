import time

import numpy as np
import redis


def run_benchmark(client, num_operations=1000):
    """Measures p95 latency for Redis GET and SET operations."""

    set_latencies = []
    get_latencies = []

    for i in range(num_operations):
        key = f"bench_key_{i}"
        value = f"bench_value_{i}"

        # Benchmark SET
        start_time = time.perf_counter()
        client.set(key, value)
        end_time = time.perf_counter()
        set_latencies.append((end_time - start_time) * 1000) # in ms

        # Benchmark GET
        start_time = time.perf_counter()
        client.get(key)
        end_time = time.perf_counter()
        get_latencies.append((end_time - start_time) * 1000) # in ms

    p95_set = np.percentile(set_latencies, 95)
    p95_get = np.percentile(get_latencies, 95)

    print(f"Benchmark Results ({num_operations} operations):")
    print(f"  SET p95 latency: {p95_set:.4f} ms")
    print(f"  GET p95 latency: {p95_get:.4f} ms")

    if p95_set <= 2.0 and p95_get <= 2.0:
        print("\nSLO PASSED: p95 get/put latency is within 2ms.")
    else:
        print("\nSLO FAILED: p95 get/put latency exceeds 2ms.")


if __name__ == "__main__":
    # This requires a running Redis instance on localhost
    try:
        redis_client = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
        redis_client.ping() # Check connection
        run_benchmark(redis_client)
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        print("Please ensure Redis is running on redis://localhost:6379/0")
