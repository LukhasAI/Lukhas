"""
Test-Compatible Logger Wrapper
==============================
Provides a logger that accepts keyword arguments in tests,
matching the production logger interface.
"""

import logging
from typing import Any, Optional


class StructuredLogger:
    """Logger wrapper that accepts keyword arguments for structured logging."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def _format_message(self, msg: str, **kwargs) -> str:
        """Format message with keyword arguments."""
        if not kwargs:
            return msg
        
        # Append key-value pairs to the message
        extras = " | ".join(f"{k}={v}" for k, v in kwargs.items())
        return f"{msg} | {extras}"
    
    def debug(self, msg: str, *args, **kwargs):
        """Debug level logging with keyword argument support."""
        formatted = self._format_message(msg, **kwargs)
        self.logger.debug(formatted, *args)
    
    def info(self, msg: str, *args, **kwargs):
        """Info level logging with keyword argument support."""
        formatted = self._format_message(msg, **kwargs)
        self.logger.info(formatted, *args)
    
    def warning(self, msg: str, *args, **kwargs):
        """Warning level logging with keyword argument support."""
        formatted = self._format_message(msg, **kwargs)
        self.logger.warning(formatted, *args)
    
    def error(self, msg: str, *args, **kwargs):
        """Error level logging with keyword argument support."""
        formatted = self._format_message(msg, **kwargs)
        self.logger.error(formatted, *args)
    
    def critical(self, msg: str, *args, **kwargs):
        """Critical level logging with keyword argument support."""
        formatted = self._format_message(msg, **kwargs)
        self.logger.critical(formatted, *args)


def get_test_logger(name: str) -> StructuredLogger:
    """
    Get a test-compatible logger that accepts keyword arguments.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        StructuredLogger instance that handles keyword arguments
    """
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger)


# Monkey-patch for test environments
def patch_logger_for_tests():
    """
    Monkey-patch the logger module to use StructuredLogger in tests.
    Call this in your test setup or conftest.py.
    """
    import candidate.core.common.logger as logger_module
    
    # Replace the get_logger function
    original_get_logger = logger_module.get_logger
    
    def wrapped_get_logger(name: str, module_name: Optional[str] = None):
        # Return our test-compatible logger
        return get_test_logger(name)
    
    logger_module.get_logger = wrapped_get_logger
    logger_module.get_module_logger = wrapped_get_logger
    
    return original_get_logger  # Return original for cleanup if needed