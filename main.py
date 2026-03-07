"""
JARVIS WorkMode v2 — Main Orchestrator
══════════════════════════════════════
Production entry point: setup wizard → tray icon → event-driven automation.

Usage:
    python main.py          (as Administrator for global hotkeys)
    pythonw.exe main.py     (silent — no console window)
"""

from __future__ import annotations

import ctypes
import subprocess
import sys
import threading
import time

from version import __version__, __app_name__
from config import Config
from app_state import AppState, WorkmodeState
from ui.tray_icon import TrayIcon
from ui.wizard import SetupWizard
from ui.notification import NotificationService
from triggers.wifi_presence import WiFiPresenceDetector
from triggers.manual_trigger import ManualTrigger
from automation.workspace_launcher import WorkspaceLauncher
from automation.window_manager import WindowManager
from automation.spotify_controller import SpotifyController
from services.updater import AutoUpdater
from services.startup_manager import StartupManager
from services.watchdog import Watchdog
from utils.logger import get_logger
from utils.helpers import is_admin, ensure_single_instance, get_running_processes, get_all_window_titles

logger = get_logger("jarvis.main")


class JarvisWorkMode:
    """Top-level orchestrator wiring triggers → automation → UI."""

    def __init__(self) -> None:
        self.config = Config.load()
        self.state = AppState()

        # ── Automation ───────────────────────────────────────────────
        self.launcher = WorkspaceLauncher(self.config)
        self.window_mgr = WindowManager(self.config)
        self.spotify = SpotifyController(self.config)

        # ── Services ─────────────────────────────────────────────────
        self.notifier = NotificationService(self.config)
        self.updater = AutoUpdater()
        self.startup_mgr = StartupManager()
        self.watchdog = Watchdog(self.state)

        # ── Triggers ─────────────────────────────────────────────────
        self.wifi_detector = WiFiPresenceDetector(
            self.config, self.state, self._on_triggered,
        )
        self.manual_trigger = ManualTrigger(
            self.config.hotkey,
            lambda: self._on_triggered("hotkey"),
        )

        # Optional Bluetooth
        self._bt_detector = None
        if self.config.detection_method == "bluetooth":
            try:
                from triggers.bluetooth_presence import BluetoothPresenceDetector
                self._bt_detector = BluetoothPresenceDetector(
                    self.config, self.state, self._on_triggered,
                )
            except ImportError:
                logger.warning("Bluetooth trigger unavailable.")

        # ── Tray (created last — references self) ────────────────────
        self.tray = TrayIcon(self.config, self.state, self)

    # ── Event handling ───────────────────────────────────────────────

    def _on_triggered(self, source: str = "unknown") -> None:
        """Callback invoked by any trigger source."""
        if not self.state.can_activate(self.config.activation_cooldown_minutes):
            logger.info(
                f"Trigger [{source}] skipped — state: {self.state.state.name}"
            )
            return

        logger.info(f"🚀 Activation triggered by [{source}]")
        self.state.state = WorkmodeState.ACTIVATING
        self.state.activation_source = source
        self.state.last_activation_time = time.time()
        self.tray.update_icon(WorkmodeState.ACTIVATING)
        self.notifier.notify_phone_detected()

        threading.Thread(
            target=self.activate, args=(source,),
            daemon=True, name="ActivationThread",
        ).start()

    def activate(self, source: str = "manual") -> None:
        """Run the full workspace activation sequence."""
        try:
            logger.info("Step 1/3 — Launching applications…")
            results = self.launcher.launch_all()
            for r in results:
                icon = "✅" if r.success else "❌"
                logger.info(f"  {icon} {r.app}: {r.message}")

            logger.info("Step 2/3 — Arranging windows…")
            self.window_mgr.arrange_workspace()

            if self.config.spotify_enabled:
                logger.info("Step 3/3 — Starting Spotify playback…")
                self.spotify.start_playlist()
            else:
                logger.info("Step 3/3 — Spotify disabled, skipping.")

            self.state.state = WorkmodeState.ACTIVE
            self.tray.update_icon(WorkmodeState.ACTIVE)
            self.notifier.notify_activation()
            logger.info("✅ Workspace fully activated!")

        except Exception as exc:
            logger.error(f"Activation failed: {exc}", exc_info=True)

        finally:
            self.state.state = WorkmodeState.COOLDOWN
            self.tray.update_icon(WorkmodeState.COOLDOWN)

    # ── Updates ──────────────────────────────────────────────────────

    def check_updates_and_notify(self) -> None:
        """Check GitHub for a newer release and toast if available."""
        logger.info("Checking for updates…")
        available, version, url = self.updater.check_for_updates()
        if available:
            logger.info(f"Update available: v{version}")
            self.notifier.notify_update_available(version)
        else:
            logger.info("Already on latest version.")

    # ── Diagnostics ──────────────────────────────────────────────────

    def _run_diagnostics(self) -> None:
        logger.info("═══ DIAGNOSTIC MODE ═══")
        logger.info("Running processes:")
        for name in get_running_processes():
            logger.debug(f"  • {name}")
        logger.info("Visible windows:")
        for title in get_all_window_titles():
            logger.debug(f"  • {title}")
        logger.info("ARP table:")
        try:
            r = subprocess.run(
                ["arp", "-a"], capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in r.stdout.strip().splitlines():
                logger.debug(f"  {line}")
        except Exception as exc:
            logger.warning(f"  ARP failed: {exc}")
        logger.info("═══ END DIAGNOSTICS ═══")

    # ── Start ────────────────────────────────────────────────────────

    def start(self) -> None:
        """Entry point — wizard gate → services → tray icon (blocking)."""
        logger.info(f"{'=' * 50}")
        logger.info(f" {__app_name__} v{__version__} starting up")
        logger.info(f"{'=' * 50}")

        # Single instance
        if not ensure_single_instance():
            logger.error("Another instance is already running. Exiting.")
            sys.exit(1)

        # Admin check
        if not is_admin():
            logger.warning(
                "Not running as Administrator — global hotkeys may be limited."
            )

        # First-run wizard
        if not self.config.setup_complete:
            logger.info("First run — launching setup wizard…")
            wizard = SetupWizard(
                self.config,
                on_complete=lambda: self.activate("wizard_test"),
            )
            completed = wizard.run()
            if not completed:
                logger.info("Wizard cancelled. Exiting.")
                sys.exit(0)
            # Reload config in case wizard saved new values
            self.config = Config.load()

        # Post-setup
        if self.config.launch_on_startup:
            self.startup_mgr.enable()
        else:
            self.startup_mgr.disable()

        # Diagnostics
        if self.config.diagnostic_mode:
            self._run_diagnostics()

        # Start services
        self.watchdog.start()

        if self.config.detection_method in ("ping", "arp"):
            self.wifi_detector.start()
            self.watchdog.register(
                "WiFiDetector", self.wifi_detector._thread,
                self.wifi_detector.restart,
            )
        elif self._bt_detector:
            self._bt_detector.start()
            self.watchdog.register(
                "BluetoothDetector", self._bt_detector._thread,
                self._bt_detector.restart,
            )

        self.manual_trigger.start()

        # Update check
        if self.config.auto_check_updates:
            threading.Thread(
                target=self.check_updates_and_notify,
                daemon=True, name="UpdaterThread",
            ).start()

        self.state.state = WorkmodeState.IDLE
        logger.info(
            f"📡 Monitoring for phone [{self.config.phone_ip}] "
            f"via {self.config.detection_method.upper()}"
        )
        logger.info(f"⌨️  Hotkey: {self.config.hotkey}")
        logger.info("System tray icon active. Right-click for options.")

        # Blocking — runs tray event loop
        self.tray.run()

        # After tray exits
        logger.info("Shutting down…")
        self.wifi_detector.stop()
        self.manual_trigger.stop()
        if self._bt_detector:
            self._bt_detector.stop()
        logger.info("Goodbye! 👋")


def main() -> None:
    """Module entry point."""
    # DPI awareness for crisp UI
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

    JarvisWorkMode().start()


if __name__ == "__main__":
    main()
