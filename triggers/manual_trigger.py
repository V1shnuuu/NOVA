"""
JARVIS WorkMode — Manual Trigger
Global hotkey listener (default CTRL+ALT+W).
"""

from __future__ import annotations

from collections.abc import Callable

import keyboard

from utils.logger import get_logger

logger = get_logger("jarvis.triggers.manual")


class ManualTrigger:
    """Registers a global hotkey that fires a callback on press.

    Requires the ``keyboard`` library, which may need Administrator
    privileges on Windows for system-wide hotkeys.
    """

    def __init__(self, hotkey: str, callback: Callable[[], None]) -> None:
        self.hotkey = hotkey
        self.callback = callback
        self._registered = False

    def start(self) -> None:
        """Register the global hotkey."""
        try:
            keyboard.add_hotkey(self.hotkey, self._handle)
            self._registered = True
            logger.info(f"Manual trigger registered: {self.hotkey}")
        except Exception as exc:
            logger.error(f"Failed to register hotkey '{self.hotkey}': {exc}")

    def stop(self) -> None:
        """Unregister the global hotkey."""
        if self._registered:
            try:
                keyboard.remove_hotkey(self.hotkey)
                self._registered = False
                logger.info("Manual trigger unregistered.")
            except Exception as exc:
                logger.warning(f"Could not remove hotkey: {exc}")

    def _handle(self) -> None:
        """Internal handler invoked by the keyboard library."""
        logger.info(f"Hotkey [{self.hotkey}] pressed!")
        self.callback("hotkey")
