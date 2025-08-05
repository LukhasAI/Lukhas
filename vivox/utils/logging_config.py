"""
VIVOX Logging Configuration
Provides performance-optimized logging with configurable levels
"""

import os
import logging
from typing import Optional

# Environment-based logging level
VIVOX_LOG_LEVEL = os.getenv('VIVOX_LOG_LEVEL', 'INFO').upper()

# Production mode detection
VIVOX_PRODUCTION = os.getenv('VIVOX_PRODUCTION', 'false').lower() == 'true'

# Performance mode - disables debug logging entirely
VIVOX_PERFORMANCE_MODE = os.getenv('VIVOX_PERFORMANCE_MODE', 'false').lower() == 'true'


def get_vivox_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for VIVOX components
    
    Args:
        name: Logger name (e.g., 'VIVOX.ME', 'VIVOX.MAE')
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if already configured
    if logger.handlers:
        return logger
    
    # Set level based on environment
    if VIVOX_PERFORMANCE_MODE:
        # In performance mode, only log warnings and above
        logger.setLevel(logging.WARNING)
    elif VIVOX_PRODUCTION:
        # In production, default to INFO
        logger.setLevel(logging.INFO)
    else:
        # Development mode
        level = getattr(logging, VIVOX_LOG_LEVEL, logging.INFO)
        logger.setLevel(level)
    
    # Create console handler with formatting
    handler = logging.StreamHandler()
    
    if VIVOX_PRODUCTION:
        # Minimal format for production
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        # Detailed format for development
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def log_performance(logger: logging.Logger, operation: str, elapsed: float, 
                   count: Optional[int] = None):
    """
    Log performance metrics at appropriate level
    
    Args:
        logger: Logger instance
        operation: Operation name
        elapsed: Time elapsed in seconds
        count: Number of operations (optional)
    """
    if VIVOX_PERFORMANCE_MODE:
        # Skip performance logging in performance mode
        return
        
    if count:
        rate = count / elapsed if elapsed > 0 else 0
        logger.info(f"{operation}: {count} ops in {elapsed:.3f}s ({rate:.0f} ops/s)")
    else:
        logger.info(f"{operation}: completed in {elapsed:.3f}s")


def debug_trace(logger: logging.Logger, message: str, **kwargs):
    """
    Log debug trace only in development mode
    
    Args:
        logger: Logger instance
        message: Debug message
        **kwargs: Additional context to log
    """
    if not VIVOX_PRODUCTION and not VIVOX_PERFORMANCE_MODE:
        if kwargs:
            logger.debug(f"{message} | {kwargs}")
        else:
            logger.debug(message)


# Component loggers
class VIVOXLoggers:
    """Centralized logger access for VIVOX components"""
    
    ME = get_vivox_logger('VIVOX.ME')
    MAE = get_vivox_logger('VIVOX.MAE')
    CIL = get_vivox_logger('VIVOX.CIL')
    SRM = get_vivox_logger('VIVOX.SRM')
    INTEGRATION = get_vivox_logger('VIVOX.INTEGRATION')
    
    @classmethod
    def set_global_level(cls, level: str):
        """Set logging level for all VIVOX loggers"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        for logger_name in ['ME', 'MAE', 'CIL', 'SRM', 'INTEGRATION']:
            logger = getattr(cls, logger_name)
            logger.setLevel(log_level)