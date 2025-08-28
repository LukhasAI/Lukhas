# LUKHAS AI Enterprise Observability

This directory contains the full observability stack for the LUKHAS AI platform, designed for enterprise-grade monitoring, tracing, and logging.

## Overview

The observability solution for LUKHAS AI is built on a combination of Datadog and Prometheus, leveraging the strengths of both platforms:

-   **Datadog**: Used for centralized logging, distributed tracing (APM), and sophisticated dashboards for business intelligence.
-   **Prometheus**: Used for collecting high-frequency, detailed metrics from application components and infrastructure.

The core of this integration is the `T4ObservabilityStack` class in `t4_observability_stack.py`, which configures and initializes all observability components.

## Configuration

To enable the observability stack, you need to configure your Datadog API keys.

1.  **Create a `.env` file** in the root of the repository by copying `.env.example`.

2.  **Add your Datadog API keys** to the `.env` file. You can find your keys in your Datadog account settings.

    ```dotenv
    # .env
    DATADOG_API_KEY=your_datadog_api_key
    DATADOG_APP_KEY=your_datadog_app_key
    DATADOG_SITE=us5.datadoghq.com # Or your datadog site
    DATADOG_ENV=development # Or production, staging, etc.
    DATADOG_SERVICE=lukhas-ai
    DATADOG_VERSION=1.0.0
    ```

## Features

### 1. Distributed Tracing (APM)

Distributed tracing is implemented using OpenTelemetry and is automatically configured for all FastAPI endpoints. This provides end-to-end visibility into requests as they travel through the system.

**Usage:**

For more granular tracing of specific functions, you can use the `@obs_stack.trace()` decorator.

```python
# serve/routes.py
from .main import obs_stack

@router.post("/generate-dream/")
@obs_stack.trace(name="generate_dream_endpoint")
async def generate_dream(req: DreamRequest):
    # Your code here
    pass
```

### 2. Centralized Logging

All application logs are automatically forwarded to Datadog. The logs are formatted as JSON and include trace and span IDs, which allows for seamless correlation between logs and traces in the Datadog UI.

**Usage:**

Simply use the standard Python `logging` module as you normally would.

```python
import logging

logger = logging.getLogger(__name__)

def my_function():
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.", extra={"user_id": 123})
```

Any extra information passed to the logger will be included in the JSON payload sent to Datadog.

### 3. Metrics

Metrics are collected from two sources:

-   **Prometheus:** The application exposes detailed metrics at various endpoints (e.g., `/metrics`, `/api/guardian/metrics`). The Datadog Agent is configured to scrape these endpoints, bringing all Prometheus metrics into Datadog. The agent configuration can be found in `enterprise/monitoring/datadog-agent-config.yml`.

-   **Custom Metrics:** You can send custom metrics directly to Datadog from the application code using the `submit_metric` method of the `T4ObservabilityStack` instance.

**Usage:**

```python
# a_file_in_the_application.py
from serve.main import obs_stack

def process_payment(amount):
    # ... payment processing logic ...
    obs_stack.submit_metric(
        'gauge',
        'lukhas.business.revenue',
        amount,
        tags=['payment_type:credit_card']
    )
```

## How It's Integrated

The `T4ObservabilityStack` is instantiated in `serve/main.py` when the application starts. This single instance is then used throughout the application to provide observability services. The FastAPI application is automatically instrumented, so no further setup is required to get basic tracing and logging.
