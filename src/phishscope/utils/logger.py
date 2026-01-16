"""
Logging utilities for PhishScope.
"""

import logging
import sys
from typing import Optional


def setup_logger(verbose: bool = False, name: str = "phishscope") -> logging.Logger:
    """
    Setup and configure logger for PhishScope.

    Args:
        verbose: Enable debug-level logging
        name: Logger name

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format based on verbosity
    if verbose:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "phishscope") -> logging.Logger:
    """
    Get an existing logger by name.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def configure_logging(verbose: bool = False) -> None:
    """
    Configure root logging for the application.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
