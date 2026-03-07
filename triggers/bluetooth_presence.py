"""
JARVIS WorkMode — Bluetooth Presence Detection (v2, Optional / Experimental)
Uses ``bleak`` BLE library. Gracefully disabled if bleak is not installed.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable

from app_state import AppState, WorkmodeState
from utils.logger import get_logger

logger = get_logger("jarvis.triggers.bluetooth")

try:
    from bleak import BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    logger.warning("bleak not installed — Bluetooth detection disabled.")


class BluetoothPresenceDetector:
    """BLE presence scanner running in a dedicated thread."""

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
        if not BLEAK_AVAILABLE:
            logger.warning("Bluetooth scanner not started (bleak unavailable).")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop, name="BluetoothPresenceScanner",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            f"Bluetooth scanner started "
            f"(looking for '{self.config.phone_bluetooth_name}')."
        )

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Bluetooth scanner stopped.")

    def restart(self) -> threading.Thread | None:
        self.stop()
        self.start()
        return self._thread

    def _run_loop(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while not self._stop_event.is_set():
                if self.app_state.state == WorkmodeState.PAUSED:
                    self._sleep(self.config.scan_interval_seconds)
                    continue
                found = loop.run_until_complete(self._scan())
                if found:
                    logger.info("Bluetooth device detected!")
                    self.callback("bluetooth")
                self._sleep(self.config.scan_interval_seconds)
        finally:
            loop.close()

    async def _scan(self) -> bool:
        try:
            devices = await BleakScanner.discover(timeout=5.0)
            target_name = self.config.phone_bluetooth_name.lower()
            target_mac = self.config.phone_mac.lower().replace(":", "-")
            for d in devices:
                name = (d.name or "").lower()
                addr = (d.address or "").lower().replace(":", "-")
                if target_name in name or target_mac == addr:
                    logger.debug(f"Matched BLE device: {d.name} [{d.address}]")
                    return True
            logger.debug(f"BLE scan: {len(devices)} devices, no match.")
            return False
        except Exception as exc:
            logger.error(f"BLE scan error: {exc}")
            return False

    def _sleep(self, seconds: int) -> None:
        for _ in range(seconds * 2):
            if self._stop_event.is_set():
                return
            time.sleep(0.5)
