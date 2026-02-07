"""
Logging configuration
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> logging.Logger:
    """Setup application logging."""
    logger = logging.getLogger("pitchcube")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
