"""
JARVIS WorkMode — Configuration Hub
All user-configurable parameters in one place.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Central configuration for JARVIS WorkMode."""

    # ── Phone Detection ──────────────────────────────────────────────
    PHONE_IP: str = "192.168.1.XXX"
    PHONE_MAC: str = "AA:BB:CC:DD:EE:FF"
    PHONE_BLUETOOTH_NAME: str = "MyPhone"
    WIFI_SCAN_INTERVAL: int = 30            # seconds between presence checks
    PHONE_PING_TIMEOUT: int = 1             # seconds before ping times out
    PRESENCE_DETECTION_METHOD: str = "arp"  # "ping", "arp", or "bluetooth"
    PRESENCE_CONFIRM_COUNT: int = 2         # detections out of 3 scans to trigger
    PRESENCE_WINDOW: int = 3                # rolling window size for confirmations

    # ── Activation Cooldown ──────────────────────────────────────────
    ACTIVATION_COOLDOWN: int = 300          # 5 minutes before re-triggering

    # ── Manual Hotkey ────────────────────────────────────────────────
    HOTKEY: str = "ctrl+alt+w"

    # ── Browser URLs ─────────────────────────────────────────────────
    CHATGPT_URL: str = "https://chat.openai.com"
    CLAUDE_URL: str = "https://claude.ai"
    BROWSER_PATH: str | None = None         # None = system default browser

    # ── Spotify ──────────────────────────────────────────────────────
    SPOTIFY_ENABLED: bool = True
    SPOTIFY_CLIENT_ID: str = ""
    SPOTIFY_CLIENT_SECRET: str = ""
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8888/callback"
    SPOTIFY_PLAYLIST_URI: str = ""          # e.g. "spotify:playlist:XXXX"
    SPOTIFY_VOLUME: int = 40                # 0–100

    # ── App Launch Delays (seconds) ──────────────────────────────────
    BROWSER_TAB_DELAY: float = 1.0          # delay between browser tabs
    BROWSER_SETTLE_DELAY: float = 2.0       # delay after browsers before next app
    SPOTIFY_LAUNCH_DELAY: float = 4.0       # wait for Spotify to fully load

    # ── Window Layout (fractions of screen) ──────────────────────────
    LAYOUT: dict = field(default_factory=lambda: {
        "chatgpt": {"x": 0.0,  "y": 0.0, "w": 0.33, "h": 1.0},
        "claude":  {"x": 0.33, "y": 0.0, "w": 0.34, "h": 1.0},
        "spotify": {"x": 0.67, "y": 0.0, "w": 0.33, "h": 1.0},
    })
    WINDOW_FIND_TIMEOUT: int = 15           # seconds to wait for a window to appear
    MONITOR_INDEX: int = 0                  # 0 = primary monitor

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "jarvis.log"

    # ── Diagnostics ──────────────────────────────────────────────────
    DIAGNOSTIC_MODE: bool = False
