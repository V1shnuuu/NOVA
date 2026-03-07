"""
JARVIS WorkMode v3 — Absence Detector
Fires deactivation callback after N consecutive missed presence scans.
Uses stricter threshold than arrival detection.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from app_state import AppState, WorkmodeState
from utils.logger import get_logger

logger = get_logger("jarvis.presence.absence")


class AbsenceDetector:
    """Monitors for the user's departure and triggers workspace shutdown."""

    def __init__(
        self,
        config,
        wifi_monitor,
        app_state: AppState,
        on_absent: Callable[[], None],
    ) -> None:
        self.config = config
        self.wifi_monitor = wifi_monitor
        self.state = app_state
        self.on_absent = on_absent
        self._miss_count = 0
        self._required = config.absence_confirmations_required
        self._running = False
        self._stop = threading.Event()

    def start(self) -> None:
        if not self.config.enable_deactivation:
            logger.info("Absence detection disabled in config.")
            return
        self._running = True
        self._miss_count = 0
        self._stop.clear()
        threading.Thread(
            target=self._watch_loop, daemon=True,
            name="AbsenceDetectorThread",
        ).start()
        logger.info(
            f"Absence detector started (need {self._required} misses)."
        )

    def stop(self) -> None:
        self._running = False
        self._stop.set()

    def _watch_loop(self) -> None:
        while self._running and not self._stop.is_set():
            self._sleep(self.config.scan_interval_seconds)
            if self._stop.is_set():
                return

            if self.wifi_monitor.is_phone_present():
                self._miss_count = 0
                self.state.phone_present = True
            else:
                self._miss_count += 1
                self.state.phone_present = False
                logger.debug(
                    f"Absence scan: miss {self._miss_count}/{self._required}"
                )
                if self._miss_count >= self._required:
                    logger.info("Departure confirmed — triggering deactivation.")
                    self._miss_count = 0
                    self._running = False
                    self.on_absent()

    def _sleep(self, seconds: int) -> None:
        for _ in range(seconds * 2):
            if self._stop.is_set():
                return
            time.sleep(0.5)
