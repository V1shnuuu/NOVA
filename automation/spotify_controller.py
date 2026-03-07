"""
JARVIS WorkMode — Spotify Playback Controller
Authenticates via Spotipy and starts a playlist on the active device.
"""

from __future__ import annotations

from utils.logger import get_logger

logger = get_logger("jarvis.automation.spotify")

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    logger.warning(
        "spotipy is not installed — Spotify control disabled. "
        "Install with: pip install spotipy"
    )


class SpotifyController:
    """Manages Spotify playback via the Spotify Web API (Spotipy).

    On first run the OAuth flow opens a browser tab for the user to
    authorise the app. A ``.cache`` token file is saved so subsequent
    runs authenticate silently.
    """

    def __init__(self, config) -> None:
        self.config = config
        self.sp: spotipy.Spotify | None = None  # type: ignore[name-defined]

        if not config.SPOTIFY_ENABLED:
            logger.info("Spotify control is disabled in config.")
            return

        if not SPOTIPY_AVAILABLE:
            return

        self._authenticate()

    # ── Public ───────────────────────────────────────────────────────

    def start_playlist(self) -> None:
        """Begin playback of the configured playlist on the first active device."""
        if self.sp is None:
            logger.info("Spotify client not available — skipping playback.")
            return

        try:
            devices = self.sp.devices()
            if not devices or not devices.get("devices"):
                logger.warning(
                    "No active Spotify device found. "
                    "Make sure Spotify desktop is open and logged in."
                )
                return

            device_id: str = devices["devices"][0]["id"]
            device_name: str = devices["devices"][0].get("name", "unknown")
            logger.info(f"Using Spotify device: {device_name} ({device_id})")

            if self.config.SPOTIFY_PLAYLIST_URI:
                self.sp.start_playback(
                    device_id=device_id,
                    context_uri=self.config.SPOTIFY_PLAYLIST_URI,
                )
                logger.info(
                    f"Playback started: {self.config.SPOTIFY_PLAYLIST_URI}"
                )
            else:
                # Resume whatever was playing last
                self.sp.start_playback(device_id=device_id)
                logger.info("Resumed Spotify playback (no playlist URI set).")

            self.sp.volume(self.config.SPOTIFY_VOLUME, device_id=device_id)
            logger.info(f"Spotify volume set to {self.config.SPOTIFY_VOLUME}%.")

        except Exception as exc:
            logger.error(f"Spotify playback error: {exc}")

    # ── Private ──────────────────────────────────────────────────────

    def _authenticate(self) -> None:
        """Set up Spotipy OAuth and create the client."""
        if not self.config.SPOTIFY_CLIENT_ID:
            logger.warning(
                "Spotify client ID not configured — Spotify control disabled."
            )
            return

        try:
            auth_manager = SpotifyOAuth(
                client_id=self.config.SPOTIFY_CLIENT_ID,
                client_secret=self.config.SPOTIFY_CLIENT_SECRET,
                redirect_uri=self.config.SPOTIFY_REDIRECT_URI,
                scope="user-read-playback-state user-modify-playback-state",
                open_browser=True,
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify authenticated successfully.")
        except Exception as exc:
            logger.error(f"Spotify authentication failed: {exc}")
            self.sp = None
