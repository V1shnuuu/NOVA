"""
JARVIS WorkMode v3 — Afternoon Mode (12:00 – 17:59)
Research layout: three equal columns — ChatGPT | Claude | Spotify.
"""

from __future__ import annotations

from modes.base_mode import BaseMode, WindowLayout


class AfternoonMode(BaseMode):
    @property
    def name(self) -> str:
        return "Afternoon"

    @property
    def description(self) -> str:
        return "Three-panel research layout for afternoon sessions"

    @property
    def apps_to_launch(self) -> list[str]:
        return ["chatgpt", "claude", "spotify"]

    @property
    def layout(self) -> list[WindowLayout]:
        return [
            WindowLayout("chatgpt", 0.0,  0.0, 0.33, 1.0),
            WindowLayout("claude",  0.33, 0.0, 0.34, 1.0),
            WindowLayout("spotify", 0.67, 0.0, 0.33, 1.0),
        ]

    @property
    def spotify_playlist_uri(self) -> str:
        return ""  # Set via config.afternoon_playlist

    @property
    def briefing_intro(self) -> str:
        return (
            "Good afternoon. Research configuration loaded. "
            "Three-panel layout is ready. All tools are at your disposal."
        )
