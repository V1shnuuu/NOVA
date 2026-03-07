"""
JARVIS WorkMode v3 — Configuration Hub
JSON-persistent dataclass stored in %%APPDATA%%\\JarvisWorkMode.
Expanded for voice, HUD, time-based modes, and absence detection.
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
    # ── Setup ────────────────────────────────────────────────────────
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

    # ── Absence detection ────────────────────────────────────────────
    enable_deactivation: bool = True
    absence_confirmations_required: int = 4

    # ── Voice ────────────────────────────────────────────────────────
    wake_word: str = "jarvis"
    voice_rate: int = 175
    voice_volume: float = 0.95
    voice_command_timeout: float = 5.0

    # ── HUD ──────────────────────────────────────────────────────────
    hud_width: int = 400
    hud_height: int = 240
    hud_opacity: float = 0.92
    hud_position: str = "bottom-right"

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
    spotify_volume: int = 40

    # ── Mode playlists ───────────────────────────────────────────────
    deep_work_playlist: str = ""
    afternoon_playlist: str = ""
    evening_playlist: str = ""

    # ── System ───────────────────────────────────────────────────────
    launch_on_startup: bool = True
    show_notifications: bool = True
    diagnostic_mode: bool = False
    log_level: str = "INFO"

    # ── Auto-updater ─────────────────────────────────────────────────
    auto_check_updates: bool = True

    # ── Persistence ──────────────────────────────────────────────────

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(asdict(self), indent=2), encoding="utf-8",
        )

    @classmethod
    def load(cls) -> Config:
        if not CONFIG_FILE.exists():
            return cls()
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**known)
        except (json.JSONDecodeError, TypeError, KeyError):
            return cls()
