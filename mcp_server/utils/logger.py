"""
Logging utility using Loguru
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_file: str = "mcp_server.log",
    rotation: str = "10 MB",
    retention: str = "1 week"
) -> None:
    """
    Setup loguru logger with file and console output

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        log_file: Log file name
        rotation: When to rotate log file
        retention: How long to keep old logs
    """
    # Remove default handler
    logger.remove()

    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Console handler with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # File handler
    logger.add(
        log_path / log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation=rotation,
        retention=retention,
        compression="zip"
    )

    logger.info(f"Logger initialized with level {log_level}")
    logger.info(f"Logs will be saved to {log_path / log_file}")


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance

    Args:
        name: Optional name for the logger context

    Returns:
        Logger instance
    """
    if name:
        return logger.bind(context=name)
    return logger
