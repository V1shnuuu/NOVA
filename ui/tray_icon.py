"""
JARVIS WorkMode — System Tray Icon (v2)
Live system tray with state-driven colour, full right-click menu.
"""

from __future__ import annotations

import subprocess
import threading
from pathlib import Path
from typing import TYPE_CHECKING

import platformdirs
import pystray
from PIL import Image, ImageDraw, ImageFont

from app_state import AppState, WorkmodeState
from config import Config
from utils.logger import get_logger

if TYPE_CHECKING:
    from main import JarvisWorkMode

logger = get_logger("jarvis.ui.tray")

# ── Colour map per state ─────────────────────────────────────────────
_STATE_COLOURS: dict[WorkmodeState, str] = {
    WorkmodeState.STARTUP:    "#e94560",
    WorkmodeState.IDLE:       "#e94560",
    WorkmodeState.DETECTING:  "#e94560",
    WorkmodeState.ACTIVATING: "#ffaa00",
    WorkmodeState.ACTIVE:     "#00ff88",
    WorkmodeState.COOLDOWN:   "#ffaa00",
    WorkmodeState.PAUSED:     "#888888",
    WorkmodeState.EXITING:    "#888888",
}

_STATE_LABELS: dict[WorkmodeState, str] = {
    WorkmodeState.STARTUP:    "⏳ Starting up…",
    WorkmodeState.IDLE:       "● Monitoring active",
    WorkmodeState.DETECTING:  "◌ Scanning for phone…",
    WorkmodeState.ACTIVATING: "⚡ Activating workspace…",
    WorkmodeState.ACTIVE:     "✅ Workspace is active",
    WorkmodeState.COOLDOWN:   "⏳ Cooldown in progress",
    WorkmodeState.PAUSED:     "⏸ Monitoring paused",
    WorkmodeState.EXITING:    "Shutting down…",
}


class TrayIcon:
    """System tray icon powered by pystray + Pillow.

    The icon colour updates dynamically to reflect the current
    ``WorkmodeState`` and the right-click menu exposes all user actions.
    """

    def __init__(
        self,
        config: Config,
        app_state: AppState,
        orchestrator: JarvisWorkMode,
    ) -> None:
        self.config = config
        self.state = app_state
        self.orchestrator = orchestrator
        self.icon: pystray.Icon | None = None

    # ── Icon generation ──────────────────────────────────────────────

    @staticmethod
    def _create_icon_image(colour: str = "#e94560", size: int = 64) -> Image.Image:
        """Draw a JARVIS-themed **J** icon programmatically.

        * Dark circle background
        * Bold **J** in the given accent colour
        """
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background circle
        draw.ellipse(
            [2, 2, size - 2, size - 2],
            fill="#1a1a2e",
            outline=colour,
            width=2,
        )

        # Letter J
        try:
            font = ImageFont.truetype("segoeuib.ttf", int(size * 0.55))
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), "J", font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (size - tw) // 2 - bbox[0]
        ty = (size - th) // 2 - bbox[1]
        draw.text((tx, ty), "J", fill=colour, font=font)

        return img

    # ── Menu ─────────────────────────────────────────────────────────

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem("JARVIS WorkMode", None, enabled=False),
            pystray.MenuItem(
                self._get_status_text, None, enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⚡ Activate Workspace Now", self._on_manual_activate,
            ),
            pystray.MenuItem(
                "⏸  Pause Monitoring",
                self._on_pause_toggle,
                checked=lambda _: self.state.state == WorkmodeState.PAUSED,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("⚙️  Settings", self._on_open_settings),
            pystray.MenuItem("📋  View Logs", self._on_open_logs),
            pystray.MenuItem("🔄  Check for Updates", self._on_check_updates),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("❌  Exit", self._on_exit),
        )

    def _get_status_text(self, _item: pystray.MenuItem) -> str:
        return _STATE_LABELS.get(self.state.state, "Unknown")

    # ── Icon state updates ───────────────────────────────────────────

    def update_icon(self, new_state: WorkmodeState) -> None:
        """Swap the tray icon image to reflect *new_state*."""
        if self.icon is None:
            return
        colour = _STATE_COLOURS.get(new_state, "#e94560")
        self.icon.icon = self._create_icon_image(colour)

    # ── Callbacks ────────────────────────────────────────────────────

    def _on_manual_activate(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        threading.Thread(
            target=self.orchestrator.activate,
            args=("manual_tray",),
            daemon=True,
        ).start()

    def _on_pause_toggle(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        if self.state.state == WorkmodeState.PAUSED:
            self.state.state = WorkmodeState.IDLE
            logger.info("Monitoring resumed.")
        else:
            self.state.state = WorkmodeState.PAUSED
            logger.info("Monitoring paused.")
        self.update_icon(self.state.state)

    def _on_open_settings(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        threading.Thread(
            target=self._launch_settings_window, daemon=True,
        ).start()

    def _launch_settings_window(self) -> None:
        try:
            from ui.settings_window import SettingsWindow
            win = SettingsWindow(
                self.config,
                on_save=lambda: logger.info("Settings saved."),
            )
            win.open()
        except Exception as exc:
            logger.error(f"Could not open settings: {exc}")

    def _on_open_logs(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        log_dir = (
            Path(platformdirs.user_data_dir("JarvisWorkMode", "JarvisWorkMode"))
            / "logs"
        )
        log_dir.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.Popen(["explorer", str(log_dir)])
        except Exception as exc:
            logger.error(f"Could not open log directory: {exc}")

    def _on_check_updates(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        threading.Thread(
            target=self.orchestrator.check_updates_and_notify,
            daemon=True,
        ).start()

    def _on_exit(
        self, _icon: pystray.Icon, _item: pystray.MenuItem,
    ) -> None:
        logger.info("Exit requested from tray menu.")
        self.state.state = WorkmodeState.EXITING
        self.state.stop_event.set()
        if self.icon:
            self.icon.stop()

    # ── Run ──────────────────────────────────────────────────────────

    def run(self) -> None:
        """Blocking — start the tray icon event loop on the calling thread."""
        self.icon = pystray.Icon(
            "JARVIS WorkMode",
            self._create_icon_image("#e94560"),
            "JARVIS WorkMode",
            self._build_menu(),
        )
        logger.info("System tray icon visible.")
        self.icon.run()
