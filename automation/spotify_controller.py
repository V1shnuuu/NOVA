"""
JARVIS WorkMode — Spotify Playback Controller (v2)
Authenticates via Spotipy OAuth and controls playback.
Token cache stored in %%APPDATA%%\\JarvisWorkMode\\.spotify_cache.
"""

from __future__ import annotations

from pathlib import Path

import platformdirs

from utils.logger import get_logger

logger = get_logger("jarvis.automation.spotify")

CACHE_PATH = (
    Path(platformdirs.user_data_dir("JarvisWorkMode", "JarvisWorkMode"))
    / ".spotify_cache"
)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    logger.warning("spotipy not installed — Spotify control disabled.")


class SpotifyController:
    """Manages Spotify playback via the Web API."""

    def __init__(self, config) -> None:
        self.config = config
        self.sp: spotipy.Spotify | None = None

        if not config.spotify_enabled:
            logger.info("Spotify control disabled in config.")
            return
        if not SPOTIPY_AVAILABLE:
            return
        self._authenticate()

    def start_playlist(self) -> None:
        if self.sp is None:
            logger.info("Spotify client unavailable — skipping.")
            return
        try:
            devices = self.sp.devices()
            if not devices or not devices.get("devices"):
                logger.warning("No active Spotify device found.")
                return

            device_id: str = devices["devices"][0]["id"]
            device_name: str = devices["devices"][0].get("name", "unknown")
            logger.info(f"Using Spotify device: {device_name}")

            if self.config.spotify_playlist_uri:
                self.sp.start_playback(
                    device_id=device_id,
                    context_uri=self.config.spotify_playlist_uri,
                )
                logger.info(f"Playing: {self.config.spotify_playlist_uri}")
            else:
                self.sp.start_playback(device_id=device_id)
                logger.info("Resumed Spotify playback.")

            self.sp.volume(self.config.spotify_volume, device_id=device_id)
            logger.info(f"Volume set to {self.config.spotify_volume}%.")
        except Exception as exc:
            logger.error(f"Spotify playback error: {exc}")

    def _authenticate(self) -> None:
        if not self.config.spotify_client_id:
            logger.warning("Spotify client ID not set — skipping auth.")
            return
        try:
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            auth_manager = SpotifyOAuth(
                client_id=self.config.spotify_client_id,
                client_secret=self.config.spotify_client_secret,
                redirect_uri=self.config.spotify_redirect_uri,
                scope="user-read-playback-state user-modify-playback-state",
                open_browser=True,
                cache_path=str(CACHE_PATH),
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify authenticated.")
        except Exception as exc:
            logger.error(f"Spotify auth failed: {exc}")
            self.sp = None
