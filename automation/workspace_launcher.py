"""
JARVIS WorkMode — Workspace Launcher
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
        time.sleep(self.config.BROWSER_SETTLE_DELAY)
        results.append(self._launch_spotify())
        return results

    # ── Browser ──────────────────────────────────────────────────────

    def _open_browser_tabs(self) -> list[LaunchResult]:
        """Open ChatGPT and Claude in the default (or configured) browser."""
        results: list[LaunchResult] = []

        urls = [
            ("ChatGPT", self.config.CHATGPT_URL),
            ("Claude", self.config.CLAUDE_URL),
        ]

        for name, url in urls:
            try:
                if self.config.BROWSER_PATH:
                    subprocess.Popen(
                        [self.config.BROWSER_PATH, "--new-window", url],
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                else:
                    webbrowser.open(url)
                logger.info(f"Opened {name}: {url}")
                results.append(LaunchResult(name, True, url))
            except Exception as exc:
                logger.error(f"Failed to open {name}: {exc}")
                results.append(LaunchResult(name, False, str(exc)))

            time.sleep(self.config.BROWSER_TAB_DELAY)

        return results

    # ── Spotify ──────────────────────────────────────────────────────

    def _launch_spotify(self) -> LaunchResult:
        """Launch the Spotify desktop app if it is not already running."""
        if not self.config.SPOTIFY_ENABLED:
            msg = "Spotify is disabled in config — skipping."
            logger.info(msg)
            return LaunchResult("Spotify", True, msg)

        if self._is_spotify_running():
            msg = "Spotify is already running."
            logger.info(msg)
            return LaunchResult("Spotify", True, msg)

        try:
            # Try common install paths on Windows
            subprocess.Popen(
                ["spotify.exe"],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            logger.info("Spotify launched. Waiting for it to load…")
            time.sleep(self.config.SPOTIFY_LAUNCH_DELAY)
            return LaunchResult("Spotify", True, "Launched")
        except FileNotFoundError:
            msg = "Spotify executable not found — is it installed?"
            logger.warning(msg)
            return LaunchResult("Spotify", False, msg)
        except Exception as exc:
            msg = f"Spotify launch error: {exc}"
            logger.error(msg)
            return LaunchResult("Spotify", False, msg)

    @staticmethod
    def _is_spotify_running() -> bool:
        """Return ``True`` if a Spotify process is already alive."""
        import psutil

        for proc in psutil.process_iter(["name"]):
            try:
                if "spotify" in (proc.info["name"] or "").lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
