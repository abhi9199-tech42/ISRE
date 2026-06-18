"""Structured logging for the ISRE system."""

import logging
import sys
from typing import Optional

_LOG: Optional[logging.Logger] = None


def get_logger(name: str = "isre", level: Optional[int] = None) -> logging.Logger:
    """Get or create the ISRE logger.

    Args:
        name: Logger name (default: "isre")
        level: Optional override for logging level

    Returns:
        Configured logging.Logger instance
    """
    global _LOG
    if _LOG is not None:
        return _LOG

    logger = logging.getLogger(name)

    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.WARNING)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)

    _LOG = logger
    return logger


def set_level(level: int):
    """Set the logging level for the ISRE logger.

    Args:
        level: One of logging.DEBUG, logging.INFO, logging.WARNING, etc.
    """
    get_logger().setLevel(level)
