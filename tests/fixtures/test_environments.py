import os
import subprocess
import time
import pytest

# Attempt to import lukhas modules and mock them if they are not found.
try:
    import lukhas.config
    import lukhas.logging
except ImportError:
    from unittest.mock import MagicMock
    import sys
    sys.modules['lukhas'] = MagicMock()
    sys.modules['lukhas.config'] = MagicMock()
    sys.modules['lukhas.logging'] = MagicMock()


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """Get the path to the docker-compose.yml file."""
    return os.path.join(pytestconfig.rootpath, "docker-compose.yml")


def _wait_for_redis(timeout=30):
    """Waits for the Redis service to be ready."""
    try:
        import redis
    except ImportError:
        pytest.skip("redis-py is not installed, cannot perform Redis health check.")

    start_time = time.time()
    while True:
        try:
            client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True, socket_connect_timeout=1)
            if client.ping():
                return
        except redis.exceptions.ConnectionError:
            pass
        if time.time() - start_time > timeout:
            pytest.fail("Timeout waiting for Redis service to start.")
        time.sleep(1)


def _wait_for_postgres(timeout=30):
    """Waits for the PostgreSQL service to be ready."""
    try:
        import psycopg2
    except ImportError:
        pytest.skip("psycopg2 is not installed, cannot perform PostgreSQL health check.")

    start_time = time.time()
    while True:
        try:
            psycopg2.connect(
                host="localhost",
                port=5432,
                user="testuser",
                password="testpass",
                dbname="testdb",
                connect_timeout=1
            )
            return
        except psycopg2.OperationalError:
            pass
        if time.time() - start_time > timeout:
            pytest.fail("Timeout waiting for PostgreSQL service to start.")
        time.sleep(1)


def _wait_for_services(timeout=30):
    """Waits for all Docker services to be ready."""
    # Add a small initial delay to allow containers to initialize
    time.sleep(2)
    _wait_for_redis(timeout)
    _wait_for_postgres(timeout)


@pytest.fixture(scope="session")
def test_services(docker_compose_file):
    """
    Start and stop test services using Docker Compose.

    This fixture starts the services defined in the docker-compose.yml
    file before the test session begins and tears them down after the
    session ends.
    """
    if not os.path.exists(docker_compose_file):
        pytest.skip("docker-compose.yml not found, skipping integration tests that require it.")

    try:
        # Start the services
        subprocess.run(
            ["docker-compose", "-f", docker_compose_file, "up", "-d"],
            check=True,
            capture_output=True,
            text=True
        )
        _wait_for_services()  # Wait for services to be ready
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.fail(f"Failed to start docker-compose services. Is docker-compose installed and is docker running? Error: {e}")

    yield

    # Stop the services
    subprocess.run(
        ["docker-compose", "-f", docker_compose_file, "down"],
        check=False,
        capture_output=True,
        text=True
    )

@pytest.fixture(scope="session")
def redis_client(test_services):
    """A fixture for a Redis client connected to the test Redis service."""
    try:
        import redis
        client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        client.ping()
        return client
    except ImportError:
        pytest.skip("redis-py is not installed, skipping redis tests.")
    except redis.exceptions.ConnectionError as e:
        pytest.fail(f"Failed to connect to Redis: {e}")


@pytest.fixture(scope="session")
def postgres_conn(test_services):
    """A fixture for a PostgreSQL connection to the test database."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="testuser",
            password="testpass",
            dbname="testdb",
        )
        yield conn
        conn.close()
    except ImportError:
        pytest.skip("psycopg2 is not installed, skipping postgres tests.")
    except Exception as e:
        pytest.fail(f"Failed to connect to PostgreSQL: {e}")


@pytest.fixture(scope="session")
def mock_api_url(test_services):
    """A fixture for the URL of the mock API service."""
    return "http://localhost:8080"
