"""
JARVIS WorkMode v3 — Mode Controller
Time-based auto-selection of workspace mode with manual override.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum, auto

from modes.base_mode import BaseMode
from modes.deep_work import DeepWorkMode
from modes.afternoon import AfternoonMode
from modes.evening import EveningMode
from utils.logger import get_logger

logger = get_logger("jarvis.modes.controller")


class ModeType(Enum):
    DEEP_WORK = auto()  # 05:00 – 11:59
    AFTERNOON = auto()  # 12:00 – 17:59
    EVENING   = auto()  # 18:00 – 04:59


class ModeController:
    """Selects the appropriate mode based on time-of-day or manual override."""

    def __init__(self, config) -> None:
        self.config = config
        self._override: ModeType | None = None
        self._modes: dict[ModeType, BaseMode] = {
            ModeType.DEEP_WORK: DeepWorkMode(),
            ModeType.AFTERNOON: AfternoonMode(),
            ModeType.EVENING:   EveningMode(),
        }

    def get_current_mode(self) -> BaseMode:
        mode_type = self._override or self._detect_time_mode()
        mode = self._modes[mode_type]
        logger.debug(f"Mode selected: {mode.name} ({mode_type.name})")
        return mode

    def set_override(self, mode_type: ModeType) -> None:
        self._override = mode_type
        logger.info(f"Mode override set: {mode_type.name}")

    def clear_override(self) -> None:
        self._override = None
        logger.info("Mode override cleared — using time-based selection.")

    @staticmethod
    def _detect_time_mode() -> ModeType:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return ModeType.DEEP_WORK
        elif 12 <= hour < 18:
            return ModeType.AFTERNOON
        else:
            return ModeType.EVENING
