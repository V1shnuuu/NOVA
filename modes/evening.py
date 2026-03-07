"""
JARVIS WorkMode v3 — Evening Mode (18:00 – 04:59)
Creative / wind-down: Claude 70%, Spotify 30%, no ChatGPT.
"""

from __future__ import annotations

from modes.base_mode import BaseMode, WindowLayout


class EveningMode(BaseMode):
    @property
    def name(self) -> str:
        return "Evening"

    @property
    def description(self) -> str:
        return "Centered creative layout for evening sessions"

    @property
    def apps_to_launch(self) -> list[str]:
        return ["claude", "spotify"]

    @property
    def layout(self) -> list[WindowLayout]:
        return [
            WindowLayout("claude",  0.0,  0.0, 0.70, 1.0),
            WindowLayout("spotify", 0.70, 0.0, 0.30, 1.0),
        ]

    @property
    def spotify_playlist_uri(self) -> str:
        return ""  # Set via config.evening_playlist

    @property
    def briefing_intro(self) -> str:
        return (
            "Good evening. Evening configuration is active. "
            "Claude is centered for focus. Spotify is on the right. "
            "Take it easy."
        )
