"""
JARVIS WorkMode v3 — Application State
Thread-safe state machine with voice/HUD/presence awareness.
"""

from __future__ import annotations

import threading
import time
from enum import Enum, auto


class WorkmodeState(Enum):
    STARTUP      = auto()
    IDLE         = auto()
    LISTENING    = auto()
    DETECTING    = auto()
    ACTIVATING   = auto()
    ACTIVE       = auto()
    DEACTIVATING = auto()
    COOLDOWN     = auto()
    PAUSED       = auto()
    EXITING      = auto()


class AppState:
    """Thread-safe shared state for the entire v3 system."""

    def __init__(self) -> None:
        self._state: WorkmodeState = WorkmodeState.STARTUP
        self._lock: threading.Lock = threading.Lock()
        self.last_activation_time: float = 0.0
        self.activation_source: str = ""
        self.stop_event: threading.Event = threading.Event()

        # Voice
        self.is_listening: bool = False

        # Presence
        self.phone_present: bool = False

        # Mode
        self.current_mode_name: str = "Standby"

    @property
    def state(self) -> WorkmodeState:
        with self._lock:
            return self._state

    @state.setter
    def state(self, new_state: WorkmodeState) -> None:
        with self._lock:
            self._state = new_state

    def can_activate(self, cooldown_minutes: int) -> bool:
        with self._lock:
            if self._state in (
                WorkmodeState.ACTIVATING,
                WorkmodeState.ACTIVE,
                WorkmodeState.DEACTIVATING,
                WorkmodeState.PAUSED,
                WorkmodeState.EXITING,
            ):
                return False
            elapsed = time.time() - self.last_activation_time
            return elapsed >= cooldown_minutes * 60
