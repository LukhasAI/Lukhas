# Test Environment Setup

This document outlines how to set up and use the test environment for integration testing. The test environment is managed using Docker Compose and provides services like a test database, Redis, and mock APIs.

## Prerequisites

- Docker
- Docker Compose

## Docker Compose Configuration

The test environment is defined in the `docker-compose.yml` file in the root of the repository. This file is not provided by the test environment system and must be created manually. Here is an example `docker-compose.yml` that sets up a Redis, Postgres, and a mock API service:

```yaml
version: '3.8'
services:
  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"
  postgres:
    image: postgres:13-alpine
    environment:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
  mock-api:
    image: kennethreitz/httpbin
    ports:
      - "8080:80"
```

## Pytest Fixtures

The test environment is managed through a set of pytest fixtures defined in `tests/fixtures/test_environments.py`. These fixtures handle the lifecycle of the Docker containers and provide clients for the services.

### `test_services`

This is a session-scoped fixture that starts the Docker Compose services before any tests run and tears them down after the tests are complete. It's designed to be used by other fixtures and not directly in tests.

### `redis_client`

This session-scoped fixture provides a Redis client connected to the test Redis service.

**Usage:**

```python
def test_redis_functionality(redis_client):
    redis_client.set("foo", "bar")
    assert redis_client.get("foo") == "bar"
```

### `postgres_conn`

This session-scoped fixture provides a connection to the test PostgreSQL database.

**Usage:**

```python
def test_postgres_functionality(postgres_conn):
    with postgres_conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    assert result[0] == 1
```

### `mock_api_url`

This session-scoped fixture provides the base URL for the mock API service.

**Usage:**

```python
import requests

def test_mock_api_functionality(mock_api_url):
    response = requests.get(f"{mock_api_url}/get")
    assert response.status_code == 200
```

## Running Tests

To run tests that use these fixtures, simply run pytest from the root of the repository. The fixtures will automatically be discovered and used.

```bash
pytest
```
