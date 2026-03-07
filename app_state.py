"""
JARVIS WorkMode — Shared Application State
Thread-safe state machine with enum for the orchestrator lifecycle.
"""

from __future__ import annotations

import threading
import time
from enum import Enum, auto


class WorkmodeState(Enum):
    """All possible states of the JARVIS WorkMode lifecycle."""

    STARTUP = auto()
    IDLE = auto()
    DETECTING = auto()
    ACTIVATING = auto()
    ACTIVE = auto()
    COOLDOWN = auto()
    PAUSED = auto()
    EXITING = auto()


class AppState:
    """Thread-safe container for shared application state.

    Every read/write to mutable fields goes through ``_lock`` to ensure
    safe access from the 6+ concurrent threads.
    """

    def __init__(self) -> None:
        self._state: WorkmodeState = WorkmodeState.STARTUP
        self._lock: threading.Lock = threading.Lock()
        self.last_activation_time: float = 0.0
        self.consecutive_detections: int = 0
        self.activation_source: str = ""
        self.stop_event: threading.Event = threading.Event()

    # ── State property ───────────────────────────────────────────────

    @property
    def state(self) -> WorkmodeState:
        """Return the current state (thread-safe read)."""
        with self._lock:
            return self._state

    @state.setter
    def state(self, new_state: WorkmodeState) -> None:
        """Set a new state (thread-safe write)."""
        with self._lock:
            self._state = new_state

    # ── Helpers ──────────────────────────────────────────────────────

    def can_activate(self, cooldown_minutes: int) -> bool:
        """Return ``True`` if a new activation is allowed right now.

        Checks that we are not already activating/active/paused and that
        the cooldown period has elapsed since the last activation.
        """
        with self._lock:
            if self._state in (
                WorkmodeState.ACTIVATING,
                WorkmodeState.ACTIVE,
                WorkmodeState.PAUSED,
                WorkmodeState.EXITING,
            ):
                return False
            elapsed = time.time() - self.last_activation_time
            return elapsed >= cooldown_minutes * 60
