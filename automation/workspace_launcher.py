"""
JARVIS WorkMode — Workspace Launcher (v2)
Opens browser tabs (ChatGPT, Claude) and launches Spotify.
"""

from __future__ import annotations

import subprocess
import time
import webbrowser
from typing import NamedTuple

from utils.logger import get_logger

logger = get_logger("jarvis.automation.launcher")


class LaunchResult(NamedTuple):
    """Outcome of an individual app launch."""
    app: str
    success: bool
    message: str


class WorkspaceLauncher:
    """Opens productivity apps as defined in the configuration."""

    def __init__(self, config) -> None:
        self.config = config

    def launch_all(self) -> list[LaunchResult]:
        """Launch all configured applications and return results."""
        results: list[LaunchResult] = []
        results.extend(self._open_browser_tabs())
        time.sleep(self.config.launch_delay_seconds)
        results.append(self._launch_spotify())
        return results

    def _open_browser_tabs(self) -> list[LaunchResult]:
        results: list[LaunchResult] = []
        urls = [
            ("ChatGPT", self.config.chatgpt_url),
            ("Claude", self.config.claude_url),
        ]
        for name, url in urls:
            try:
                if self.config.browser_executable:
                    subprocess.Popen(
                        [self.config.browser_executable, "--new-window", url],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    webbrowser.open(url)
                logger.info(f"Opened {name}: {url}")
                results.append(LaunchResult(name, True, url))
            except Exception as exc:
                logger.error(f"Failed to open {name}: {exc}")
                results.append(LaunchResult(name, False, str(exc)))
            time.sleep(self.config.launch_delay_seconds)
        return results

    def _launch_spotify(self) -> LaunchResult:
        if not self.config.spotify_enabled:
            msg = "Spotify disabled — skipping."
            logger.info(msg)
            return LaunchResult("Spotify", True, msg)

        if self._is_spotify_running():
            msg = "Spotify already running."
            logger.info(msg)
            return LaunchResult("Spotify", True, msg)

        try:
            exe = self.config.spotify_executable or "spotify.exe"
            subprocess.Popen(
                [exe], shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.info("Spotify launched — waiting for it to load…")
            time.sleep(self.config.launch_delay_seconds * 2)
            return LaunchResult("Spotify", True, "Launched")
        except FileNotFoundError:
            msg = "Spotify executable not found."
            logger.warning(msg)
            return LaunchResult("Spotify", False, msg)
        except Exception as exc:
            msg = f"Spotify launch error: {exc}"
            logger.error(msg)
            return LaunchResult("Spotify", False, msg)

    @staticmethod
    def _is_spotify_running() -> bool:
        import psutil
        for proc in psutil.process_iter(["name"]):
            try:
                if "spotify" in (proc.info["name"] or "").lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
