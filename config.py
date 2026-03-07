"""
JARVIS WorkMode — Configuration Hub (v2)
Persistent JSON-backed dataclass stored in %%APPDATA%%\\JarvisWorkMode.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import platformdirs

CONFIG_DIR: Path = Path(
    platformdirs.user_data_dir("JarvisWorkMode", "JarvisWorkMode")
)
CONFIG_FILE: Path = CONFIG_DIR / "config.json"


@dataclass
class Config:
    """Central configuration — every field is JSON-serialisable."""

    # ── Setup state ──────────────────────────────────────────────────
    first_run: bool = True
    setup_complete: bool = False

    # ── Phone detection ──────────────────────────────────────────────
    phone_ip: str = ""
    phone_mac: str = ""
    detection_method: str = "arp"
    scan_interval_seconds: int = 30
    ping_timeout_ms: int = 1000
    confirmed_detections_required: int = 2
    presence_window: int = 3
    phone_bluetooth_name: str = ""

    # ── Hotkey ───────────────────────────────────────────────────────
    hotkey: str = "ctrl+alt+w"

    # ── Activation ───────────────────────────────────────────────────
    activation_cooldown_minutes: int = 5
    launch_delay_seconds: float = 1.5

    # ── Browser / Apps ───────────────────────────────────────────────
    chatgpt_url: str = "https://chat.openai.com"
    claude_url: str = "https://claude.ai"
    browser_executable: str = ""
    spotify_executable: str = ""

    # ── Spotify ──────────────────────────────────────────────────────
    spotify_enabled: bool = True
    spotify_client_id: str = ""
    spotify_client_secret: str = ""
    spotify_redirect_uri: str = "http://localhost:8888/callback"
    spotify_playlist_uri: str = ""
    spotify_volume: int = 40

    # ── Window layout (fractions of screen) ──────────────────────────
    layout: dict = field(default_factory=lambda: {
        "chatgpt": {"x": 0.0, "y": 0.0, "w": 0.33, "h": 1.0},
        "claude":  {"x": 0.33, "y": 0.0, "w": 0.34, "h": 1.0},
        "spotify": {"x": 0.67, "y": 0.0, "w": 0.33, "h": 1.0},
    })
    monitor_index: int = 0
    window_find_timeout: int = 15

    # ── System ───────────────────────────────────────────────────────
    launch_on_startup: bool = True
    minimize_to_tray_on_close: bool = True
    show_activation_notifications: bool = True
    diagnostic_mode: bool = False
    log_level: str = "INFO"

    # ── Auto-updater ─────────────────────────────────────────────────
    auto_check_updates: bool = True
    last_update_check: str = ""

    # ── Persistence ──────────────────────────────────────────────────

    def save(self) -> None:
        """Serialise to ``%APPDATA%\\JarvisWorkMode\\config.json``."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2),
            encoding="utf-8",
        )

    @classmethod
    def load(cls) -> Config:
        """Load from disk, falling back to defaults on any error."""
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**known)
        except (json.JSONDecodeError, TypeError, KeyError):
            return cls()
