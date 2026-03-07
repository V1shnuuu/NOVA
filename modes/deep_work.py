"""
JARVIS WorkMode v3 — Deep Work Mode (05:00 – 11:59)
Maximum focus: Claude 60% left, ChatGPT 40% right, Spotify minimized.
"""

from __future__ import annotations

from modes.base_mode import BaseMode, WindowLayout


class DeepWorkMode(BaseMode):
    @property
    def name(self) -> str:
        return "Deep Work"

    @property
    def description(self) -> str:
        return "Maximum focus configuration for morning productivity"

    @property
    def apps_to_launch(self) -> list[str]:
        return ["claude", "chatgpt", "spotify"]

    @property
    def layout(self) -> list[WindowLayout]:
        return [
            WindowLayout("claude",  0.0,  0.0, 0.60, 1.0),
            WindowLayout("chatgpt", 0.60, 0.0, 0.40, 1.0),
        ]

    @property
    def spotify_playlist_uri(self) -> str:
        return ""  # Set via config.deep_work_playlist

    @property
    def briefing_intro(self) -> str:
        return (
            "Good morning. Deep work mode is active. "
            "Claude is your primary workspace. ChatGPT on the right for reference. "
            "Spotify is running in the background. Let's get to work."
        )
