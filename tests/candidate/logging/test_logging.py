import logging
import json
import io
import pytest
from unittest.mock import patch

from candidate.logging.structured_logger import setup_logging, get_logger, LogLevel

@pytest.fixture
def log_capture():
    """Fixture to capture log output."""
    stream = io.StringIO()
    with patch('sys.stdout', new=stream):
        yield stream

class TestStructuredLogger:
    def test_setup_logging_text_format(self, log_capture):
        setup_logging(log_level="INFO", log_format="text")
        log = get_logger(__name__)

        log.info("test message", key="value")

        output = log_capture.getvalue()
        assert "INFO" in output
        assert "test message" in output
        assert "key=value" in output
        assert "test_logging" in output # logger name

    def test_setup_logging_json_format(self, log_capture):
        setup_logging(log_level="INFO", log_format="json")
        log = get_logger(__name__)

        log.info("test message", key="value")

        output = log_capture.getvalue().strip()
        log_data = json.loads(output)

        assert log_data["level"] == "info"
        assert log_data["event"] == "test message"
        assert log_data["key"] == "value"
        assert log_data["logger"] == "tests.candidate.logging.test_logging"

    def test_log_level_filtering(self, log_capture):
        setup_logging(log_level="WARNING", log_format="text")
        log = get_logger(__name__)

        log.info("info message")
        log.warning("warning message")

        output = log_capture.getvalue()
        assert "info message" not in output
        assert "warning message" in output

    def test_get_logger(self):
        setup_logging()
        logger1 = get_logger("my_logger")
        logger2 = get_logger("my_logger")
        assert logger1 is logger2

        logger3 = get_logger("another_logger")
        assert logger1 is not logger3
