"""
JARVIS WorkMode — Production Logging (v2)
Rotating file logs in %%APPDATA%% + colored console output.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

import colorlog
import platformdirs

LOG_DIR: Path = (
    Path(platformdirs.user_data_dir("JarvisWorkMode", "JarvisWorkMode")) / "logs"
)


def get_logger(name: str) -> logging.Logger:
    """Create and return a logger with colored console + daily rotating file.

    Logs are stored in ``%APPDATA%\\JarvisWorkMode\\logs\\jarvis.log`` and
    rotate at midnight, keeping the last 7 days.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # ── Console (colored) ────────────────────────────────────────────
    console = colorlog.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(colorlog.ColoredFormatter(
        "%(log_color)s[%(asctime)s] %(levelname)-8s%(reset)s "
        "%(name)s — %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    ))
    logger.addHandler(console)

    # ── Rotating file (midnight, keep 7 days) ────────────────────────
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_DIR / "jarvis.log",
        when="midnight",
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
    ))
    logger.addHandler(file_handler)

    return logger
