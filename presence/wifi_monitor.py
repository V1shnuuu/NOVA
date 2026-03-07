"""
JARVIS WorkMode v3 — WiFi Presence Monitor
ARP/ping scanner that sets app_state.phone_present and fires callback.
"""

from __future__ import annotations

import subprocess
import threading
import time
from collections import deque
from collections.abc import Callable

from app_state import AppState, WorkmodeState
from utils.logger import get_logger

logger = get_logger("jarvis.presence.wifi")


def _ping(ip: str, timeout_ms: int = 1000) -> bool:
    try:
        r = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout_ms), ip],
            capture_output=True, text=True, timeout=(timeout_ms / 1000) + 2,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return "TTL=" in r.stdout.upper()
    except Exception:
        return False


def _arp_check(mac: str) -> bool:
    normalised = mac.lower().replace(":", "-")
    try:
        r = subprocess.run(
            ["arp", "-a"], capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return normalised in r.stdout.lower()
    except Exception:
        return False


class WiFiMonitor:
    """Background daemon scanning for phone presence on local WiFi."""

    def __init__(
        self, config, app_state: AppState,
        on_present: Callable[[], None] | None = None,
    ) -> None:
        self.config = config
        self.state = app_state
        self.on_present = on_present
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WiFiMonitorThread",
        )
        self._thread.start()
        logger.info(f"WiFi monitor started ({self.config.detection_method}).")

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def is_phone_present(self) -> bool:
        """Single check — used by absence detector."""
        method = self.config.detection_method.lower()
        if method == "ping":
            return _ping(self.config.phone_ip, self.config.ping_timeout_ms)
        return _arp_check(self.config.phone_mac)

    def _loop(self) -> None:
        history: deque[bool] = deque(maxlen=self.config.presence_window)
        while not self._stop.is_set():
            if self.state.state == WorkmodeState.PAUSED:
                self._sleep(self.config.scan_interval_seconds)
                continue

            detected = self.is_phone_present()
            history.append(detected)
            self.state.phone_present = detected

            hits = sum(history)
            if hits >= self.config.confirmed_detections_required:
                if self.on_present and self.state.can_activate(
                    self.config.activation_cooldown_minutes
                ):
                    logger.info(f"Phone presence confirmed ({hits}/{len(history)}).")
                    self.on_present()
                    history.clear()

            self._sleep(self.config.scan_interval_seconds)

    def _sleep(self, seconds: int) -> None:
        for _ in range(seconds * 2):
            if self._stop.is_set():
                return
            time.sleep(0.5)
