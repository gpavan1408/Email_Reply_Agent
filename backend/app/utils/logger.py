"""
logger.py — Structured logging using Loguru.

What this does:
  Sets up logging for the whole app.
  In development: colorful logs in your VS Code terminal.
  In production:  logs saved to files, rotated daily.

Why Loguru instead of Python's built-in logging?
  Much simpler syntax and better formatting out of the box.

How to use anywhere in the project:
  from loguru import logger
  logger.info("Email received from sender@example.com")
  logger.error("Failed to connect to Gmail API")
"""

import sys
from loguru import logger
from app.utils.config import settings


def setup_logger():
    """Configure Loguru for the whole application."""

    # Remove the default Loguru handler
    logger.remove()

    # Log format — shows time, level, file, line, message
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console output (your VS Code terminal)
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.APP_ENV == "development" else "INFO",
        colorize=True,
    )

    # File output — only in production
    if settings.APP_ENV == "production":
        logger.add(
            "logs/email_agent_{time:YYYY-MM-DD}.log",
            format=log_format,
            level="INFO",
            rotation="00:00",       # New file every midnight
            retention="7 days",     # Keep 7 days of logs
            compression="zip",      # Compress old logs
        )

    logger.info(f"✅ Logger ready | Environment: {settings.APP_ENV}")