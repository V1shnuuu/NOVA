"""
JARVIS WorkMode v3 — Workspace Launcher
Opens browser tabs and applications based on the active mode.
"""

from __future__ import annotations

import subprocess
import time
import webbrowser

import psutil

from utils.logger import get_logger

logger = get_logger("jarvis.workspace.launcher")

_APP_URLS: dict[str, str] = {
    "chatgpt": "https://chat.openai.com",
    "claude":  "https://claude.ai",
}


class WorkspaceLauncher:
    """Opens productivity apps defined by the current mode."""

    def __init__(self, config) -> None:
        self.config = config

    def launch_apps(self, apps: list[str]) -> None:
        for app in apps:
            if app in _APP_URLS:
                self._open_browser_tab(app, _APP_URLS[app])
            elif app == "spotify":
                self._launch_spotify()
            time.sleep(self.config.launch_delay_seconds)

    def _open_browser_tab(self, name: str, url: str) -> None:
        try:
            if self.config.browser_executable:
                subprocess.Popen(
                    [self.config.browser_executable, "--new-window", url],
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                webbrowser.open(url)
            logger.info(f"Opened {name}: {url}")
        except Exception as exc:
            logger.error(f"Failed to open {name}: {exc}")

    def _launch_spotify(self) -> None:
        if not self.config.spotify_enabled:
            logger.info("Spotify disabled — skipping.")
            return
        if self._is_running("spotify"):
            logger.info("Spotify already running.")
            return
        try:
            exe = self.config.spotify_executable or "spotify.exe"
            subprocess.Popen([exe], shell=True,
                              creationflags=subprocess.CREATE_NO_WINDOW)
            logger.info("Spotify launched.")
        except Exception as exc:
            logger.error(f"Spotify launch error: {exc}")

    @staticmethod
    def _is_running(name: str) -> bool:
        for proc in psutil.process_iter(["name"]):
            try:
                if name.lower() in (proc.info["name"] or "").lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
