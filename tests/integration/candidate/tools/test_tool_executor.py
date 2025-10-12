from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import docker
from labs.tools.tool_executor import ToolExecutor


@pytest.fixture
def executor():
    """Provides a ToolExecutor instance for tests."""
    return ToolExecutor(config={"rate_limit_seconds": 1})


@pytest.mark.asyncio
async def test_open_url_success(executor):
    """Tests successful URL opening and content extraction."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"<html><head><title>Test Page</title></head><body><p>Hello World</p></body></html>"

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        result = await executor._open_url({"url": "https://example.com"})
        assert "Successfully retrieved and parsed content" in result
        assert "Title: Test Page" in result
        assert "Hello World" in result
        assert "<html>" not in result


@pytest.mark.asyncio
async def test_open_url_rate_limiting(executor):
    """Tests if rate limiting is enforced for the same domain."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"<html><body>ok</body></html>"

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        # First call should succeed
        result1 = await executor._open_url({"url": "https://example.com"})
        assert "Successfully" in result1

        # Immediate second call should be rate limited
        result2 = await executor._open_url({"url": "https://example.com"})
        assert "Rate limit exceeded" in result2

        # Call to a different domain should succeed
        result3 = await executor._open_url({"url": "https://another.com"})
        assert "Successfully" in result3


@pytest.mark.asyncio
async def test_open_url_non_html(executor):
    """Tests handling of non-HTML content."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {"content-type": "application/json"}

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        result = await executor._open_url({"url": "https://example.com/data.json"})
        assert "Cannot parse content of type 'application/json'" in result


@pytest.mark.asyncio
async def test_open_url_too_large(executor):
    """Tests handling of oversized content."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"a" * (3 * 1024 * 1024)  # 3MB

    mock_async_client = AsyncMock()
    mock_async_client.__aenter__.return_value.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_async_client):
        result = await executor._open_url({"url": "https://example.com"})
        assert "Page content is too large" in result


@pytest.mark.asyncio
async def test_open_url_invalid_url(executor):
    """Tests handling of invalid URL formats."""
    result = await executor._open_url({"url": "ftp://example.com"})
    assert "Invalid URL format" in result


@pytest.mark.asyncio
async def test_open_url_browser_disabled(executor):
    """Tests behavior when the browser tool is disabled."""
    executor.browser_enabled = False
    result = await executor._open_url({"url": "https://example.com"})
    assert "Web browsing is disabled" in result


# --- Tests for _exec_code ---


@patch("labs.tools.tool_executor.docker")
def test_exec_code_python_success(mock_docker, executor):
    """Tests successful execution of a Python script."""
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"Hello from Python", b""]  # stdout, stderr

    mock_docker.from_env.return_value.images.build.return_value = (
        MagicMock(id="test-id"),
        "log",
    )
    mock_docker.from_env.return_value.containers.run.return_value = mock_container

    source = "print('Hello from Python')"
    result = executor._exec_code({"language": "python", "source": source})

    assert "Execution successful" in result
    assert "Hello from Python" in result


@patch("labs.tools.tool_executor.docker")
def test_exec_code_javascript_success(mock_docker, executor):
    """Tests successful execution of a JavaScript script."""
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"Hello from JS", b""]

    mock_docker.from_env.return_value.images.build.return_value = (
        MagicMock(id="test-id"),
        "log",
    )
    mock_docker.from_env.return_value.containers.run.return_value = mock_container

    source = "console.log('Hello from JS')"
    result = executor._exec_code({"language": "javascript", "source": source})

    assert "Execution successful" in result
    assert "Hello from JS" in result


@patch("labs.tools.tool_executor.docker")
def test_exec_code_bash_success(mock_docker, executor):
    """Tests successful execution of a Bash script."""
    mock_container = MagicMock()
    mock_container.wait.return_value = {"StatusCode": 0}
    mock_container.logs.side_effect = [b"Hello from Bash", b""]

    mock_docker.from_env.return_value.images.build.return_value = (
        MagicMock(id="test-id"),
        "log",
    )
    mock_docker.from_env.return_value.containers.run.return_value = mock_container

    source = "echo 'Hello from Bash'"
    result = executor._exec_code({"language": "bash", "source": source})

    assert "Execution successful" in result
    assert "Hello from Bash" in result


def test_exec_code_disabled(executor):
    """Tests behavior when code execution is disabled."""
    executor.code_exec_enabled = False
    result = executor._exec_code({"language": "python", "source": "print(1)"})
    assert "Code execution is disabled" in result


def test_exec_code_unsupported_language(executor):
    """Tests handling of unsupported programming languages."""
    result = executor._exec_code({"language": "ruby", "source": "puts 1"})
    assert "Language 'ruby' is not supported" in result


@patch("labs.tools.tool_executor.docker")
def test_exec_code_build_error(mock_docker, executor):
    """Tests handling of Docker build failures."""
    mock_docker.errors.BuildError = docker.errors.BuildError
    mock_docker.from_env.return_value.images.build.side_effect = docker.errors.BuildError("Build failed", "build_log")

    result = executor._exec_code({"language": "python", "source": "print(1)"})
    assert "Docker build failed" in result


def test_exec_code_security_violation(executor):
    """Tests that dangerous patterns are blocked."""
    result = executor._exec_code({"language": "python", "source": 'import os; os.system("ls")'})
    assert "Security violation: pattern 'os' is not allowed" in result
