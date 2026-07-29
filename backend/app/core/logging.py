"""
FinPilot AI – Structured JSON Logging Configuration
Configures a production-ready logger for the entire application.
"""

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.core.config import get_settings


def setup_logging() -> None:
    """
    Configures the root logger to output structured JSON logs.
    In development, a human-readable format is used instead.
    """
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove all existing handlers to avoid duplicate output
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if settings.is_production:
        formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
