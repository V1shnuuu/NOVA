"""
JARVIS WorkMode — Logging Utility
Colored console output + file logging with timestamps.
"""

import logging
from pathlib import Path

import colorlog


def get_logger(name: str, log_file: str = "jarvis.log") -> logging.Logger:
    """Create and return a logger with colored console + file output.

    Args:
        name: Logger name (usually the module path).
        log_file: Path to the log file.

    Returns:
        Configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if called more than once
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── Console handler (colored) ────────────────────────────────────
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] %(levelname)s%(reset)s — %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    ))
    logger.addHandler(console_handler)

    # ── File handler ─────────────────────────────────────────────────
    log_path = Path(log_file)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s — %(name)s — %(message)s",
    ))
    logger.addHandler(file_handler)

    return logger
