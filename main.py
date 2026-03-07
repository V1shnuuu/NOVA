"""
JARVIS WorkMode — Main Orchestrator
═══════════════════════════════════
Starts all trigger listeners and responds to activation events by
launching apps, arranging windows, and controlling Spotify.

Usage:
    python main.py          (as Administrator for global hotkeys)
    pythonw.exe main.py     (no console window — silent mode)
"""

from __future__ import annotations

import subprocess
import threading
import time

from config import Config
from triggers.wifi_presence import WiFiPresenceDetector
from triggers.manual_trigger import ManualTrigger
from automation.workspace_launcher import WorkspaceLauncher
from automation.window_manager import WindowManager
from automation.spotify_controller import SpotifyController
from utils.logger import get_logger
from utils.helpers import is_admin, get_running_processes, get_all_window_titles

logger = get_logger("jarvis.main")


# ── State Machine ────────────────────────────────────────────────────
# IDLE → DETECTING → ACTIVATING → ACTIVE → IDLE (cooldown)

class AppState:
    """Thread-safe shared state for the application."""

    def __init__(self) -> None:
        self.is_active: bool = False
        self.lock: threading.Lock = threading.Lock()
        self.last_activation: float = 0.0


class JarvisWorkMode:
    """Top-level orchestrator that wires triggers to automation modules."""

    def __init__(self) -> None:
        self.config = Config()
        self.state = AppState()

        # ── Automation layer ─────────────────────────────────────────
        self.launcher = WorkspaceLauncher(self.config)
        self.window_manager = WindowManager(self.config)
        self.spotify = SpotifyController(self.config)

        # ── Trigger layer ────────────────────────────────────────────
        self.wifi_detector = WiFiPresenceDetector(
            self.config, self._on_triggered,
        )
        self.manual_trigger = ManualTrigger(
            self.config.HOTKEY, self._on_triggered,
        )

        # Optional bluetooth trigger
        self._bluetooth_detector = None
        if self.config.PRESENCE_DETECTION_METHOD == "bluetooth":
            try:
                from triggers.bluetooth_presence import BluetoothPresenceDetector
                self._bluetooth_detector = BluetoothPresenceDetector(
                    self.config, self._on_triggered,
                )
            except ImportError:
                logger.warning("Bluetooth trigger unavailable.")

    # ── Event Handling ───────────────────────────────────────────────

    def _on_triggered(self, source: str = "unknown") -> None:
        """Central callback invoked by any trigger source."""
        with self.state.lock:
            now = time.time()

            if self.state.is_active:
                logger.info(
                    f"Trigger from [{source}] ignored — "
                    f"workspace already active."
                )
                return

            elapsed = now - self.state.last_activation
            if elapsed < self.config.ACTIVATION_COOLDOWN:
                remaining = int(self.config.ACTIVATION_COOLDOWN - elapsed)
                logger.info(
                    f"Trigger from [{source}] ignored — "
                    f"cooldown active ({remaining}s remaining)."
                )
                return

            self.state.is_active = True
            self.state.last_activation = now

        logger.info(f"🚀 JARVIS WorkMode ACTIVATED (source: {source})")
        threading.Thread(
            target=self._activate_workspace,
            name="WorkspaceActivation",
            daemon=True,
        ).start()

    def _activate_workspace(self) -> None:
        """Run the full activation sequence in a background thread."""
        try:
            logger.info("Phase 1/3 — Launching applications…")
            results = self.launcher.launch_all()
            for r in results:
                status = "✅" if r.success else "❌"
                logger.info(f"  {status} {r.app}: {r.message}")

            logger.info("Phase 2/3 — Arranging windows…")
            self.window_manager.arrange_workspace()

            if self.config.SPOTIFY_ENABLED:
                logger.info("Phase 3/3 — Starting Spotify playback…")
                self.spotify.start_playlist()
            else:
                logger.info("Phase 3/3 — Spotify disabled, skipping.")

            logger.info("✅ Workspace fully activated!")

        except Exception as exc:
            logger.error(f"Workspace activation failed: {exc}", exc_info=True)

        finally:
            with self.state.lock:
                self.state.is_active = False

    # ── Diagnostics ──────────────────────────────────────────────────

    def _run_diagnostics(self) -> None:
        """Print extensive system info when DIAGNOSTIC_MODE is enabled."""
        logger.info("═══ DIAGNOSTIC MODE ═══")

        logger.info("Running processes:")
        for name in get_running_processes():
            logger.debug(f"  • {name}")

        logger.info("Visible window titles:")
        for title in get_all_window_titles():
            logger.debug(f"  • {title}")

        logger.info("ARP table:")
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in result.stdout.strip().splitlines():
                logger.debug(f"  {line}")
        except Exception as exc:
            logger.warning(f"  Could not read ARP table: {exc}")

        logger.info("Network interfaces:")
        try:
            result = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in result.stdout.strip().splitlines():
                if line.strip():
                    logger.debug(f"  {line}")
        except Exception as exc:
            logger.warning(f"  Could not read network interfaces: {exc}")

        logger.info("═══ END DIAGNOSTICS ═══")

    # ── Run ──────────────────────────────────────────────────────────

    def run(self) -> None:
        """Start JARVIS WorkMode and block until CTRL+C."""
        logger.info("🤖 JARVIS WorkMode is starting…")
        logger.info(f"   Python event-driven orchestrator on Windows")

        if not is_admin():
            logger.warning(
                "Not running as Administrator. "
                "Global hotkeys may not work in all apps."
            )

        if self.config.DIAGNOSTIC_MODE:
            self._run_diagnostics()

        # Start triggers
        if self.config.PRESENCE_DETECTION_METHOD in ("ping", "arp"):
            self.wifi_detector.start()
        elif self._bluetooth_detector:
            self._bluetooth_detector.start()

        self.manual_trigger.start()

        logger.info(
            f"📡 Monitoring for phone [{self.config.PHONE_IP}] "
            f"via {self.config.PRESENCE_DETECTION_METHOD.upper()}"
        )
        logger.info(f"⌨️  Hotkey: {self.config.HOTKEY}")
        logger.info("Press CTRL+C to exit.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down JARVIS WorkMode…")
            self.wifi_detector.stop()
            self.manual_trigger.stop()
            if self._bluetooth_detector:
                self._bluetooth_detector.stop()
            logger.info("Goodbye! 👋")


if __name__ == "__main__":
    JarvisWorkMode().run()
