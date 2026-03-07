"""
JARVIS WorkMode — WiFi Presence Detection (v2)
Detects phone on local network via ICMP ping or ARP table scan.
Integrates with AppState for state-aware scanning.
"""

from __future__ import annotations

import subprocess
import threading
import time
from collections import deque
from collections.abc import Callable

from app_state import AppState, WorkmodeState
from utils.logger import get_logger

logger = get_logger("jarvis.triggers.wifi")


def ping_device(ip: str, timeout_ms: int = 1000) -> bool:
    """Send a single ICMP ping and return ``True`` if the device responds."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout_ms), ip],
            capture_output=True, text=True, timeout=(timeout_ms / 1000) + 2,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return "TTL=" in result.stdout.upper()
    except subprocess.TimeoutExpired:
        logger.debug(f"Ping to {ip} timed out.")
        return False
    except FileNotFoundError:
        logger.error("ping command not found.")
        return False


def arp_scan(mac: str) -> bool:
    """Check the local ARP table for a given MAC address."""
    normalised = mac.lower().replace(":", "-")
    try:
        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return normalised in result.stdout.lower()
    except subprocess.TimeoutExpired:
        logger.debug("ARP scan timed out.")
        return False
    except FileNotFoundError:
        logger.error("arp command not found.")
        return False


class WiFiPresenceDetector:
    """Background thread that polls for phone presence on the local network.

    Uses a rolling-window confirmation: ``confirmed_detections_required``
    positive scans out of ``presence_window`` consecutive scans.
    """

    def __init__(
        self,
        config,
        app_state: AppState,
        callback: Callable[[str], None],
    ) -> None:
        self.config = config
        self.app_state = app_state
        self.callback = callback
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Spin up the background scanning thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._scan_loop, name="WiFiPresenceScanner", daemon=True,
        )
        self._thread.start()
        logger.info(
            f"WiFi presence scanner started "
            f"(method={self.config.detection_method}, "
            f"interval={self.config.scan_interval_seconds}s)."
        )

    def stop(self) -> None:
        """Signal the scanning thread to stop."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("WiFi presence scanner stopped.")

    def restart(self) -> threading.Thread | None:
        """Stop then start — returns the new thread (for watchdog)."""
        self.stop()
        self.start()
        return self._thread

    # ── Private ──────────────────────────────────────────────────────

    def _scan_loop(self) -> None:
        history: deque[bool] = deque(maxlen=self.config.presence_window)

        while not self._stop_event.is_set():
            # Skip scanning if paused
            if self.app_state.state == WorkmodeState.PAUSED:
                self._sleep(self.config.scan_interval_seconds)
                continue

            detected = self._detect()
            history.append(detected)
            logger.debug(
                f"Scan: {'FOUND' if detected else 'NOT FOUND'}  "
                f"history={list(history)}"
            )

            hits = sum(history)
            if hits >= self.config.confirmed_detections_required:
                logger.info(
                    f"Phone presence confirmed "
                    f"({hits}/{len(history)} positive)."
                )
                self.callback("wifi")
                history.clear()

            self._sleep(self.config.scan_interval_seconds)

    def _detect(self) -> bool:
        method = self.config.detection_method.lower()
        match method:
            case "ping":
                return ping_device(
                    self.config.phone_ip, self.config.ping_timeout_ms,
                )
            case "arp":
                return arp_scan(self.config.phone_mac)
            case _:
                logger.warning(
                    f"Unknown method '{method}' — falling back to ARP."
                )
                return arp_scan(self.config.phone_mac)

    def _sleep(self, seconds: int) -> None:
        for _ in range(seconds * 2):
            if self._stop_event.is_set():
                return
            time.sleep(0.5)
