"""
JARVIS WorkMode v3 — App Window Title Profiles
Maps app names to their known window title keywords for detection.
"""

from __future__ import annotations

APP_PROFILES: dict[str, list[str]] = {
    "chatgpt": ["ChatGPT", "chat.openai.com", "OpenAI"],
    "claude":  ["Claude", "claude.ai", "Anthropic"],
    "spotify": ["Spotify"],
}

APP_PROCESS_NAMES: dict[str, list[str]] = {
    "chatgpt": ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"],
    "claude":  ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"],
    "spotify": ["spotify.exe"],
}
