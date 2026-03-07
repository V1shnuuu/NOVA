"""
JARVIS WorkMode — Watchdog Service (v2)
Monitors registered background threads and auto-restarts dead ones.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from app_state import AppState
from utils.logger import get_logger

logger = get_logger("jarvis.services.watchdog")


class Watchdog:
    """Periodically checks that monitored threads are still alive.

    If a registered thread has died, the watchdog invokes its restart
    callback and stores the new thread reference.
    """

    def __init__(
        self, app_state: AppState, check_interval: int = 60,
    ) -> None:
        self.app_state = app_state
        self.check_interval = check_interval
        self._monitored: dict[str, tuple[threading.Thread, Callable]] = {}
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        thread: threading.Thread | None,
        restart_fn: Callable[[], threading.Thread | None],
    ) -> None:
        """Register a thread with a restart function.

        Args:
            name: Human-readable label for logging.
            thread: The thread to monitor (may be ``None`` if not started yet).
            restart_fn: Called when the thread dies. Must return the new thread.
        """
        with self._lock:
            self._monitored[name] = (thread, restart_fn)  # type: ignore[arg-type]
            logger.debug(f"Watchdog monitoring: {name}")

    def start(self) -> None:
        """Launch the watchdog loop in a daemon thread."""
        threading.Thread(
            target=self._watch_loop, daemon=True, name="WatchdogThread",
        ).start()
        logger.info(
            f"Watchdog started (check every {self.check_interval}s)."
        )

    def _watch_loop(self) -> None:
        while not self.app_state.stop_event.is_set():
            with self._lock:
                for name, (thread, restart_fn) in list(self._monitored.items()):
                    if thread is not None and not thread.is_alive():
                        logger.warning(
                            f"[Watchdog] Thread '{name}' died — restarting…"
                        )
                        try:
                            new_thread = restart_fn()
                            self._monitored[name] = (new_thread, restart_fn)
                        except Exception as exc:
                            logger.error(
                                f"[Watchdog] Failed to restart '{name}': {exc}"
                            )

            # Sleep in small increments so stop_event is responsive
            for _ in range(self.check_interval * 2):
                if self.app_state.stop_event.is_set():
                    return
                time.sleep(0.5)
