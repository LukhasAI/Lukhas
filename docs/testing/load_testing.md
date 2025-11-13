# Load Testing Guide

This document provides instructions on how to run the Locust load tests for the LUKHAS API.

## Prerequisites

- Python 3.11 or higher
- `pip` for installing dependencies

## Setup

1.  **Install Dependencies:**

    Install all the required dependencies from `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

    You will also need to install `locust`:

    ```bash
    pip install locust
    ```

2.  **Start the API Server:**

    To run the load test, you need to have the API server running. You can start the server with the following command:

    ```bash
    CACHE_ENABLED=false LUKHAS_LOAD_TESTING_MODE=1 python3 -m serve.main
    ```

    -   `CACHE_ENABLED=false`: Disables the Redis cache.
    -   `LUKHAS_LOAD_TESTING_MODE=1`: Disables authentication middleware and overrides authentication dependencies.

## Running the Load Test

Once the server is running, you can start the load test using the following command:

```bash
locust -f tests/load/locustfile_api.py --host http://localhost:8000
```

This will start the Locust web interface at `http://localhost:8089`. You can then specify the number of users and spawn rate to start the test.

### Headless Mode

To run the test in headless mode, use the following command:

```bash
locust -f tests/load/locustfile_api.py --host http://localhost:8000 --headless -u <users> -r <spawn-rate> -t <run-time>
```

-   `<users>`: The number of concurrent users.
-   `<spawn-rate>`: The rate at which to spawn users.
-   `<run-time>`: The duration of the test (e.g., `60s`, `10m`).
