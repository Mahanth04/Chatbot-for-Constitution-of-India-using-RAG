"""
Centralized logging configuration for the backend.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str = "coi_chatbot", level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with console output.
    
    Args:
        name: Logger name.
        level: Logging level.
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers on re-init
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Console handler with formatted output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Pre-configured logger instance
logger = setup_logger()
