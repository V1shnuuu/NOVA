"""
JARVIS WorkMode — Bluetooth Presence Detection (Optional / Experimental)
Uses the ``bleak`` BLE library to detect nearby Bluetooth devices.

⚠ This module is **optional**. If ``bleak`` is not installed the class
gracefully disables itself and logs a warning.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Callable

from utils.logger import get_logger

logger = get_logger("jarvis.triggers.bluetooth")

try:
    from bleak import BleakScanner  # type: ignore[import-untyped]
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    logger.warning(
        "bleak is not installed — Bluetooth presence detection disabled. "
        "Install with: pip install bleak"
    )


class BluetoothPresenceDetector:
    """Scans for a specific Bluetooth device using BLE advertisements.

    Falls back gracefully if ``bleak`` is missing. The scanner runs in a
    dedicated thread with its own ``asyncio`` event loop.
    """

    def __init__(self, config, callback: Callable[[str], None]) -> None:
        self.config = config
        self.callback = callback
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    # ── Public API ───────────────────────────────────────────────────

    def start(self) -> None:
        """Begin scanning in a background thread."""
        if not BLEAK_AVAILABLE:
            logger.warning("Bluetooth scanner not started (bleak unavailable).")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            name="BluetoothPresenceScanner",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            f"Bluetooth presence scanner started "
            f"(looking for '{self.config.PHONE_BLUETOOTH_NAME}')."
        )

    def stop(self) -> None:
        """Signal the scanning thread to stop."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("Bluetooth presence scanner stopped.")

    # ── Private ──────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        """Create a fresh event loop and poll for BLE devices."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while not self._stop_event.is_set():
                found = loop.run_until_complete(self._scan())
                if found:
                    logger.info("Bluetooth device detected!")
                    self.callback("bluetooth")

                for _ in range(self.config.WIFI_SCAN_INTERVAL * 2):
                    if self._stop_event.is_set():
                        return
                    time.sleep(0.5)
        finally:
            loop.close()

    async def _scan(self) -> bool:
        """Perform a single BLE scan and check for our target device."""
        try:
            devices = await BleakScanner.discover(timeout=5.0)
            target_name = self.config.PHONE_BLUETOOTH_NAME.lower()
            target_mac = self.config.PHONE_MAC.lower().replace(":", "-")

            for device in devices:
                name = (device.name or "").lower()
                address = (device.address or "").lower().replace(":", "-")
                if target_name in name or target_mac == address:
                    logger.debug(f"Matched BLE device: {device.name} [{device.address}]")
                    return True

            logger.debug(f"BLE scan complete — {len(devices)} devices, no match.")
            return False
        except Exception as exc:
            logger.error(f"BLE scan error: {exc}")
            return False
