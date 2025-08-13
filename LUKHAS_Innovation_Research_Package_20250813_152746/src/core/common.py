"""
Common utilities for LUKHAS Innovation System
Provides logging and basic utilities needed by test modules.
"""

import logging
import sys
from datetime import datetime
from typing import Optional

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or "lukhas")
    
    # Ensure logger has handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

# Guardian System Constants
GUARDIAN_DRIFT_THRESHOLD = 0.15
HALLUCINATION_THRESHOLD = 0.1

# System Configuration
class Config:
    """System configuration container"""
    
    def __init__(self):
        self.guardian_threshold = GUARDIAN_DRIFT_THRESHOLD
        self.hallucination_threshold = HALLUCINATION_THRESHOLD
        self.api_timeout = 30
        self.max_retries = 3
        self.enable_fallback = True
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        import os
        config = cls()
        
        config.guardian_threshold = float(
            os.getenv('GUARDIAN_DRIFT_THRESHOLD', str(GUARDIAN_DRIFT_THRESHOLD))
        )
        config.api_timeout = int(os.getenv('API_TIMEOUT_SECONDS', '30'))
        config.max_retries = int(os.getenv('RETRY_ATTEMPTS', '3'))
        config.enable_fallback = os.getenv('ENABLE_API_FALLBACK', 'true').lower() == 'true'
        
        return config