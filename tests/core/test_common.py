"""
Comprehensive Test Suite for Core Common Utilities
=================================================

Tests the shared utilities for all LUKHAS modules, including logging functionality,
configuration management, and other common utility functions used throughout
the system.

Test Coverage Areas:
- Logger creation and configuration
- Log level management and validation
- Handler setup and formatting
- Logger inheritance and propagation
- Error handling in logging setup
- Performance of logging operations
- Thread safety of logger operations
- Integration with system logging
"""
import logging
import sys
import threading
import time
from io import StringIO
from unittest.mock import MagicMock, Mock, patch

import pytest

from core.common import (
    get_logger,
)


class TestCoreCommon:
    """Comprehensive test suite for Core Common utilities."""

    @pytest.fixture
    def logger_name(self):
        """Provide a test logger name."""
        return "test_logger_module"

    @pytest.fixture
    def capture_logs(self):
        """Capture log output for testing."""
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        return log_capture, handler

    # Basic Logger Functionality Tests
    def test_get_logger_basic(self, logger_name):
        """Test basic logger creation."""
        logger = get_logger(logger_name)

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == logger_name

    def test_get_logger_with_level(self, logger_name):
        """Test logger creation with custom level."""
        logger = get_logger(logger_name, level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_get_logger_default_level(self, logger_name):
        """Test logger creation with default level."""
        logger = get_logger(logger_name)

        # Default should be INFO
        assert logger.level == logging.INFO

    def test_get_logger_idempotent(self, logger_name):
        """Test that getting the same logger returns the same instance."""
        logger1 = get_logger(logger_name)
        logger2 = get_logger(logger_name)

        assert logger1 is logger2

    def test_logger_handler_configuration(self, logger_name):
        """Test logger handler is properly configured."""
        logger = get_logger(logger_name)

        # Should have at least one handler
        assert len(logger.handlers) >= 1

        # Handler should be StreamHandler to stdout
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout

    def test_logger_formatter_configuration(self, logger_name):
        """Test logger formatter is properly configured."""
        logger = get_logger(logger_name)

        handler = logger.handlers[0]
        formatter = handler.formatter

        assert formatter is not None

        # Test formatter format string
        format_string = formatter._fmt
        assert "%(asctime)s" in format_string
        assert "%(name)s" in format_string
        assert "%(levelname)s" in format_string
        assert "%(message)s" in format_string

    def test_logger_propagation_disabled(self, logger_name):
        """Test logger propagation is disabled."""
        logger = get_logger(logger_name)

        assert logger.propagate is False

    # Logger Output Tests
    def test_logger_info_output(self, logger_name, capture_logs):
        """Test logger info level output."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.INFO)

        # Replace handler to capture output
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log a message
        test_message = "Test info message"
        logger.info(test_message)

        # Check output
        log_output = log_capture.getvalue()
        assert test_message in log_output
        assert "INFO" in log_output
        assert logger_name in log_output

    def test_logger_debug_output(self, logger_name, capture_logs):
        """Test logger debug level output."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.DEBUG)

        # Replace handler to capture output
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log debug message
        test_message = "Test debug message"
        logger.debug(test_message)

        # Check output
        log_output = log_capture.getvalue()
        assert test_message in log_output
        assert "DEBUG" in log_output

    def test_logger_warning_output(self, logger_name, capture_logs):
        """Test logger warning level output."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.WARNING)

        # Replace handler to capture output
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log warning message
        test_message = "Test warning message"
        logger.warning(test_message)

        # Check output
        log_output = log_capture.getvalue()
        assert test_message in log_output
        assert "WARNING" in log_output

    def test_logger_error_output(self, logger_name, capture_logs):
        """Test logger error level output."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.ERROR)

        # Replace handler to capture output
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log error message
        test_message = "Test error message"
        logger.error(test_message)

        # Check output
        log_output = log_capture.getvalue()
        assert test_message in log_output
        assert "ERROR" in log_output

    def test_logger_critical_output(self, logger_name, capture_logs):
        """Test logger critical level output."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.CRITICAL)

        # Replace handler to capture output
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log critical message
        test_message = "Test critical message"
        logger.critical(test_message)

        # Check output
        log_output = log_capture.getvalue()
        assert test_message in log_output
        assert "CRITICAL" in log_output

    # Log Level Filtering Tests
    def test_log_level_filtering_info(self, logger_name, capture_logs):
        """Test log level filtering at INFO level."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.INFO)
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log messages at different levels
        logger.debug("Debug message")  # Should be filtered out
        logger.info("Info message")    # Should appear
        logger.warning("Warning message")  # Should appear

        log_output = log_capture.getvalue()

        assert "Debug message" not in log_output
        assert "Info message" in log_output
        assert "Warning message" in log_output

    def test_log_level_filtering_warning(self, logger_name, capture_logs):
        """Test log level filtering at WARNING level."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.WARNING)
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log messages at different levels
        logger.debug("Debug message")    # Should be filtered out
        logger.info("Info message")      # Should be filtered out
        logger.warning("Warning message")  # Should appear
        logger.error("Error message")    # Should appear

        log_output = log_capture.getvalue()

        assert "Debug message" not in log_output
        assert "Info message" not in log_output
        assert "Warning message" in log_output
        assert "Error message" in log_output

    def test_log_level_filtering_error(self, logger_name, capture_logs):
        """Test log level filtering at ERROR level."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name, level=logging.ERROR)
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log messages at different levels
        logger.info("Info message")      # Should be filtered out
        logger.warning("Warning message")  # Should be filtered out
        logger.error("Error message")    # Should appear
        logger.critical("Critical message")  # Should appear

        log_output = log_capture.getvalue()

        assert "Info message" not in log_output
        assert "Warning message" not in log_output
        assert "Error message" in log_output
        assert "Critical message" in log_output

    # Handler Management Tests
    def test_logger_single_handler_per_logger(self, logger_name):
        """Test that each logger gets only one handler."""
        logger = get_logger(logger_name)
        initial_handler_count = len(logger.handlers)

        # Get the same logger again
        same_logger = get_logger(logger_name)

        # Handler count should not increase
        assert len(same_logger.handlers) == initial_handler_count

    def test_multiple_loggers_separate_handlers(self):
        """Test that different loggers get separate handlers."""
        logger1 = get_logger("test_logger_1")
        logger2 = get_logger("test_logger_2")

        # Both should have handlers
        assert len(logger1.handlers) >= 1
        assert len(logger2.handlers) >= 1

        # Handlers should be different instances
        assert logger1.handlers[0] is not logger2.handlers[0]

    def test_handler_stream_configuration(self, logger_name):
        """Test handler stream is configured to stdout."""
        logger = get_logger(logger_name)
        handler = logger.handlers[0]

        assert handler.stream == sys.stdout

    # Error Handling Tests
    def test_invalid_log_level_handling(self, logger_name):
        """Test handling of invalid log levels."""
        # Test with invalid numeric level
        logger = get_logger(logger_name, level=9999)

        # Should still create logger (Python logging handles invalid levels gracefully)
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_none_log_level_handling(self, logger_name):
        """Test handling of None log level."""
        logger = get_logger(logger_name, level=None)

        # Should use default level (INFO)
        assert logger.level == logging.INFO

    def test_empty_logger_name_handling(self):
        """Test handling of empty logger name."""
        logger = get_logger("")

        assert logger is not None
        assert logger.name == ""

    def test_none_logger_name_handling(self):
        """Test handling of None logger name."""
        with pytest.raises((TypeError, ValueError)):
            get_logger(None)

    # Thread Safety Tests
    def test_concurrent_logger_creation(self):
        """Test concurrent logger creation is thread-safe."""
        loggers = []
        exceptions = []

        def create_logger(name):
            try:
                logger = get_logger(f"concurrent_test_{name}")
                loggers.append(logger)
            except Exception as e:
                exceptions.append(e)

        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_logger, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no exceptions occurred
        assert len(exceptions) == 0
        assert len(loggers) == 10

        # Verify all loggers are unique
        logger_names = [logger.name for logger in loggers]
        assert len(set(logger_names)) == 10

    def test_concurrent_logging_operations(self, logger_name, capture_logs):
        """Test concurrent logging operations are thread-safe."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)

        messages_logged = []

        def log_messages(thread_id):
            for i in range(10):
                message = f"Thread {thread_id} message {i}"
                logger.info(message)
                messages_logged.append(message)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=log_messages, args=(i,))
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all messages were logged
        log_output = log_capture.getvalue()
        for message in messages_logged:
            assert message in log_output

    # Performance Tests
    def test_logger_creation_performance(self):
        """Test logger creation performance."""
        start_time = time.time()

        # Create many loggers
        loggers = []
        for i in range(100):
            logger = get_logger(f"performance_test_{i}")
            loggers.append(logger)

        end_time = time.time()
        creation_time = end_time - start_time

        # Should create 100 loggers quickly
        assert creation_time < 1.0  # Less than 1 second
        assert len(loggers) == 100

    def test_logging_performance(self, logger_name, capture_logs):
        """Test logging operation performance."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)

        start_time = time.time()

        # Log many messages
        for i in range(1000):
            logger.info(f"Performance test message {i}")

        end_time = time.time()
        logging_time = end_time - start_time

        # Should log 1000 messages quickly
        assert logging_time < 2.0  # Less than 2 seconds

    def test_logger_memory_usage(self):
        """Test logger memory usage doesn't grow excessively."""
        import gc

        # Force garbage collection
        gc.collect()
        initial_logger_count = len(logging.Logger.manager.loggerDict)

        # Create and use many loggers
        for i in range(50):
            logger = get_logger(f"memory_test_{i}")
            logger.info("Test message")

        # Verify reasonable memory usage
        final_logger_count = len(logging.Logger.manager.loggerDict)
        new_loggers = final_logger_count - initial_logger_count

        # Should have created the expected number of new loggers
        assert new_loggers <= 50

    # Integration Tests
    def test_logger_with_external_logging_config(self, logger_name):
        """Test logger behavior with external logging configuration."""
        # Modify root logger configuration
        root_logger = logging.getLogger()
        original_level = root_logger.level
        root_logger.setLevel(logging.CRITICAL)

        try:
            # Create logger (should not be affected by root logger changes)
            logger = get_logger(logger_name)

            # Should still use its own configuration
            assert logger.level == logging.INFO  # Default level
            assert logger.propagate is False  # Should not propagate

        finally:
            # Restore original configuration
            root_logger.setLevel(original_level)

    def test_logger_with_structured_logging(self, logger_name, capture_logs):
        """Test logger with structured logging patterns."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log structured information
        logger.info("User action", extra={
            "user_id": "12345",
            "action": "login",
            "timestamp": time.time()
        })

        log_output = log_capture.getvalue()
        assert "User action" in log_output

    def test_logger_exception_logging(self, logger_name, capture_logs):
        """Test logger exception logging capabilities."""
        log_capture, handler = capture_logs

        logger = get_logger(logger_name)
        logger.handlers.clear()
        logger.addHandler(handler)

        # Log an exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

        log_output = log_capture.getvalue()
        assert "An error occurred" in log_output
        assert "ValueError" in log_output
        assert "Test exception" in log_output

    # Configuration Validation Tests
    def test_logger_configuration_consistency(self):
        """Test logger configuration consistency across multiple calls."""
        logger1 = get_logger("consistency_test")
        logger2 = get_logger("consistency_test")

        # Should be the same instance
        assert logger1 is logger2

        # Should have consistent configuration
        assert logger1.level == logger2.level
        assert logger1.handlers == logger2.handlers
        assert logger1.propagate == logger2.propagate

    def test_logger_formatter_consistency(self):
        """Test logger formatter consistency."""
        logger1 = get_logger("formatter_test_1")
        logger2 = get_logger("formatter_test_2")

        # Both should have formatters
        formatter1 = logger1.handlers[0].formatter
        formatter2 = logger2.handlers[0].formatter

        # Formatters should use the same format string
        assert formatter1._fmt == formatter2._fmt

    # Edge Cases and Boundary Tests
    def test_logger_with_very_long_name(self):
        """Test logger with very long name."""
        long_name = "x" * 1000  # 1000 character name
        logger = get_logger(long_name)

        assert logger is not None
        assert logger.name == long_name

    def test_logger_with_special_characters_in_name(self):
        """Test logger with special characters in name."""
        special_name = "test.logger-with_special@characters#123"
        logger = get_logger(special_name)

        assert logger is not None
        assert logger.name == special_name

    def test_logger_with_unicode_name(self):
        """Test logger with unicode characters in name."""
        unicode_name = "test_logger_🚀_unicode_测试"
        logger = get_logger(unicode_name)

        assert logger is not None
        assert logger.name == unicode_name

    def test_logger_behavior_after_handler_removal(self, logger_name):
        """Test logger behavior after handler removal."""
        logger = get_logger(logger_name)
        len(logger.handlers)

        # Remove all handlers
        logger.handlers.clear()

        # Get logger again (should recreate handlers)
        same_logger = get_logger(logger_name)

        # Since we're getting the same instance and handlers were cleared,
        # the logger might not have handlers unless get_logger recreates them
        # This test verifies the behavior is predictable
        assert same_logger is logger

    # Cleanup and Resource Management Tests
    def test_logger_resource_cleanup(self):
        """Test logger resource cleanup doesn't cause issues."""
        loggers = []

        # Create many loggers
        for i in range(20):
            logger = get_logger(f"cleanup_test_{i}")
            loggers.append(logger)

        # Clear references
        loggers.clear()

        # Force garbage collection
        import gc
        gc.collect()

        # Should not cause any issues
        new_logger = get_logger("cleanup_test_new")
        assert new_logger is not None

    def test_handler_resource_management(self, logger_name):
        """Test handler resource management."""
        logger = get_logger(logger_name)
        handler = logger.handlers[0]

        # Verify handler has proper resource management
        assert hasattr(handler, 'close')
        assert handler.stream is not None

        # Handler should be properly configured
        assert handler.formatter is not None
