"""
Common utilities for LUKHAS PWM
===============================
Centralized utility functions to reduce code duplication.
"""

import asyncio
import json
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def load_config(config_path: Path, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load JSON configuration with defaults"""
    config = defaults or {}

    if config_path.exists():
        try:
            with open(config_path) as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            logger = get_logger(__name__)
            logger.error(f"Failed to load config from {config_path}: {e}")

    return config


def save_config(config: Dict[str, Any], config_path: Path) -> bool:
    """Save configuration to JSON file"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False


def async_error_handler(func):
    """Decorator for consistent async error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


def sync_error_handler(func):
    """Decorator for consistent sync error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


class SingletonMeta(type):
    """Metaclass for singleton pattern"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def ensure_path(path: Path) -> Path:
    """Ensure a path exists, creating directories if needed"""
    path = Path(path)
    if path.suffix:  # It's a file
        path.parent.mkdir(parents=True, exist_ok=True)
    else:  # It's a directory
        path.mkdir(parents=True, exist_ok=True)
    return path


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result
