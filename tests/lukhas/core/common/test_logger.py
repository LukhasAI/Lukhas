
import json
import logging
import os
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# This is a hack to get the import to work.
# The test runner's working directory might not be the project root.
# This assumes the test is run from the project root.
# A better solution would be to configure the test runner properly.
# For now, this will have to do.
sys.path.insert(0, os.path.abspath("./lukhas_website"))

from lukhas.core.common import logger as logger_module
from lukhas.core.common.logger import (
    JSONFormatter,
    LukhasFormatter,
    configure_logging,
    get_logger,
    get_module_logger,
)

TEST_LOG_FILE = "test_logger.log"


class TestLogger(unittest.TestCase):
    def setUp(self):
        # Redirect stdout to capture console logs
        self.stdout_capture = StringIO()
        self.stdout_patch = patch("sys.stdout", self.stdout_capture)
        self.stdout_patch.start()

        # Keep a copy of the original state
        self.original_loggers = logger_module._loggers.copy()
        self.original_config = logger_module._logging_config.copy()

        # Reset logger state before each test
        logger_module._loggers.clear()
        logger_module._logging_config = {
            "level": logging.INFO,
            "format": "standard",
            "handlers": ["console"],
            "propagate": False,
        }
        # Remove any existing root handlers to avoid duplicate logs
        logging.getLogger().handlers = []


    def tearDown(self):
        self.stdout_patch.stop()

        # Restore original state
        logger_module._loggers = self.original_loggers
        logger_module._logging_config = self.original_config

        if os.path.exists(TEST_LOG_FILE):
            os.remove(TEST_LOG_FILE)

    def test_lukhas_formatter_symbols(self):
        formatter = LukhasFormatter()
        self.assertEqual(formatter.SYMBOLS[logging.DEBUG], "🔍")
        self.assertEqual(formatter.SYMBOLS[logging.INFO], "i")
        self.assertEqual(formatter.SYMBOLS[logging.WARNING], "⚠️")
        self.assertEqual(formatter.SYMBOLS[logging.ERROR], "❌")
        self.assertEqual(formatter.SYMBOLS[logging.CRITICAL], "🚨")

    def test_lukhas_formatter_format(self):
        configure_logging(level="DEBUG")
        logger = get_logger("test_formatter")
        logger.debug("test debug")
        log_output = self.stdout_capture.getvalue()
        self.assertIn("🔍", log_output)
        self.assertIn("test_formatter - DEBUG - test debug", log_output)

    def test_lukhas_formatter_module_context(self):
        configure_logging(level="INFO")
        logger = get_module_logger("consciousness.unified.auto_consciousness")
        logger.info("test message")
        log_output = self.stdout_capture.getvalue()
        self.assertIn("[CONSCIOUSNESS]", log_output)

    def test_json_formatter(self):
        configure_logging(level="INFO", json_output=True)
        logger = get_logger("test_json")
        logger.warning("json test", extra={"request_id": "123"})
        log_output = self.stdout_capture.getvalue()
        log_data = json.loads(log_output)

        self.assertEqual(log_data["level"], "WARNING")
        self.assertEqual(log_data["module"], "test_logger")
        self.assertEqual(log_data["message"], "json test")
        self.assertEqual(log_data["request_id"], "123")

    def test_configure_logging_level(self):
        configure_logging(level="WARNING")
        logger = get_logger("test_level")
        logger.info("should not appear")
        logger.warning("should appear")
        log_output = self.stdout_capture.getvalue()
        self.assertNotIn("should not appear", log_output)
        self.assertIn("should appear", log_output)

    def test_configure_logging_format_type(self):
        configure_logging(level="INFO", format_type="minimal")
        logger = get_logger("test_format_type")
        logger.info("minimal format")
        log_output = self.stdout_capture.getvalue()
        self.assertNotIn("test_format_type", log_output) # minimal format doesn't include logger name
        self.assertIn("i INFO - minimal format", log_output)

    def test_configure_logging_file(self):
        self.assertFalse(os.path.exists(TEST_LOG_FILE))
        configure_logging(level="INFO", log_file=TEST_LOG_FILE)
        logger = get_logger("test_file_log")
        logger.info("log to file")

        # Force file handler to write
        for handler in logging.getLogger("test_file_log").handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()

        self.assertTrue(os.path.exists(TEST_LOG_FILE))
        with open(TEST_LOG_FILE) as f:
            file_content = f.read()
        self.assertIn("log to file", file_content)

    def test_get_logger_caching(self):
        logger1 = get_logger("cached_logger")
        logger2 = get_logger("cached_logger")
        self.assertIs(logger1, logger2)

    def test_get_logger_new_logger(self):
        logger1 = get_logger("new_logger_1")
        logger2 = get_logger("new_logger_2")
        self.assertIsNot(logger1, logger2)

    def test_get_module_logger_known_module(self):
        logger = get_module_logger("core.common.config")
        # It's an adapter
        self.assertIn("module_name", logger.extra)
        self.assertEqual(logger.extra["module_name"], "CORE")

    def test_get_module_logger_unknown_module(self):
        logger = get_module_logger("some.other.module")
        self.assertIn("module_name", logger.extra)
        self.assertEqual(logger.extra["module_name"], "LUKHAS")

    def test_log_levels(self):
        configure_logging(level="DEBUG")
        logger = get_logger("test_all_levels")

        levels = {
            "debug": logger.debug,
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "critical": logger.critical,
        }

        for level, log_func in levels.items():
            self.stdout_capture.truncate(0)
            self.stdout_capture.seek(0)
            log_func(f"testing {level}")
            log_output = self.stdout_capture.getvalue()
            self.assertIn(f"testing {level}", log_output)
            self.assertIn(level.upper(), log_output)

    def test_log_extra_data(self):
        configure_logging(level="INFO", json_output=True)
        logger = get_logger("test_extra")
        extra_data = {"user_id": "test_user", "tenant_id": "test_tenant"}
        logger.info("log with extra data", extra=extra_data)
        log_data = json.loads(self.stdout_capture.getvalue())
        self.assertEqual(log_data["user_id"], "test_user")
        self.assertEqual(log_data["tenant_id"], "test_tenant")

    def test_detailed_format(self):
        configure_logging(level="INFO", format_type="detailed")
        logger = get_logger("test_detailed")
        logger.info("detailed message")
        log_output = self.stdout_capture.getvalue()
        self.assertIn("test_detailed:test_detailed_format", log_output)

    def test_reconfigure_logging(self):
        # Configure once
        configure_logging(level="INFO")
        logger = get_logger("reconfig_test")
        logger.debug("should not show")
        self.assertNotIn("should not show", self.stdout_capture.getvalue())

        # Reconfigure
        configure_logging(level="DEBUG")
        logger.debug("should show now")
        self.assertIn("should show now", self.stdout_capture.getvalue())


if __name__ == "__main__":
    unittest.main()
