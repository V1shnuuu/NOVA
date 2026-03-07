"""
JARVIS WorkMode — Auto-Update Checker (v2)
Queries the GitHub Releases API (no auth needed for public repos).
"""

from __future__ import annotations

import json
import urllib.request
import webbrowser

from packaging.version import Version

from version import __version__, __github_repo__
from utils.logger import get_logger

logger = get_logger("jarvis.services.updater")


class AutoUpdater:
    """Checks for new releases on GitHub and offers to download them."""

    RELEASES_URL = (
        f"https://api.github.com/repos/{__github_repo__}/releases/latest"
    )

    def check_for_updates(self) -> tuple[bool, str, str]:
        """Query GitHub for the latest release.

        Returns:
            ``(update_available, latest_version, download_url)``
            Falls back to ``(False, "", "")`` on any network failure.
        """
        try:
            req = urllib.request.Request(
                self.RELEASES_URL,
                headers={"User-Agent": "JARVIS-WorkMode-Updater"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())

            latest = data["tag_name"].lstrip("v")
            download_url = next(
                (
                    a["browser_download_url"]
                    for a in data.get("assets", [])
                    if a["name"].endswith(".exe")
                ),
                data.get("html_url", ""),
            )
            update_available = Version(latest) > Version(__version__)
            if update_available:
                logger.info(f"Update available: v{latest} (current: v{__version__})")
            return update_available, latest, download_url
        except Exception as exc:
            logger.debug(f"Update check failed: {exc}")
            return False, "", ""

    @staticmethod
    def open_download_page(url: str) -> None:
        """Open the download URL in the default browser."""
        if url:
            webbrowser.open(url)
