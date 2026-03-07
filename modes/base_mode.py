"""
JARVIS WorkMode v3 — Abstract Base Mode
Defines the interface that all workspace modes must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class WindowLayout:
    """Position and size of one app window (fractions of screen)."""
    app_name: str
    x_pct: float  # 0.0 – 1.0
    y_pct: float
    w_pct: float
    h_pct: float


class BaseMode(ABC):
    """Every workspace mode (Deep Work, Afternoon, Evening) extends this."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        ...

    @property
    @abstractmethod
    def apps_to_launch(self) -> list[str]:
        ...

    @property
    @abstractmethod
    def layout(self) -> list[WindowLayout]:
        ...

    @property
    @abstractmethod
    def spotify_playlist_uri(self) -> str:
        ...

    @property
    @abstractmethod
    def briefing_intro(self) -> str:
        ...
