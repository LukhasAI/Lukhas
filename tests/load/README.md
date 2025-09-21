# Load Testing

This directory contains scripts for load testing the LUKHAS AI system.

## Tool

We use [k6](https://k6.io/) for load testing. Please make sure you have it installed before running the tests.

## Running the Tests

To run the load test, use the following command from the root of the repository:

```bash
k6 run tests/load/api_load_test.js
```

This will execute the scenarios defined in the `api_load_test.js` script.

## Scenarios

The `api_load_test.js` script includes two scenarios:

1.  **Sustained Load**: This scenario runs with a constant number of 20 virtual users for 5 minutes. It's designed to test the system's stability under a moderate, continuous load.

2.  **Spike Load**: This scenario starts after the sustained load test. It ramps up from 0 to 100 virtual users in 10 seconds, stays at 100 VUs for 30 seconds, and then ramps down to 0. This tests the system's ability to handle sudden spikes in traffic.

## Analyzing Results

The script includes thresholds for the test to pass:
-   The rate of failed HTTP requests should be less than 1%.
-   The 95th percentile of request duration should be below 500ms.

k6 will provide a summary of the test results in the console after the test is complete. You can also use k6's output options to send the results to other tools for more detailed analysis. For example, to output to a JSON file:

```bash
k6 run --out json=test_results.json tests/load/api_load_test.js
```

This will create a `test_results.json` file with detailed metrics from the test run.
