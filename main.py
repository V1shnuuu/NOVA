"""
JARVIS WorkMode v3 — Main Orchestrator
═══════════════════════════════════════
Voice-first HUD system. Wires all components together.

Boot sequence → wake word → command → mode selection →
briefing cinematic → activation/deactivation → HUD event loop.
"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
import winsound
from datetime import datetime

from version import __version__, __app_name__
from config import Config
from app_state import AppState, WorkmodeState

from voice.speaker import JarvisSpeaker
from voice.recognizer import CommandRecognizer
from voice.wake_word import WakeWordDetector
from voice.command_parser import parse_command, Command
from voice.responses import RESPONSES, briefing, get_greeting
from voice.chime import ensure_chime

from hud.hud_window import HUDWindow
from hud.briefing_screen import BriefingScreen
from hud.voice_ring import VoiceRing

from modes.mode_controller import ModeController

from workspace.launcher import WorkspaceLauncher
from workspace.window_arranger import WindowArranger
from workspace.deactivator import WorkspaceDeactivator

from presence.wifi_monitor import WiFiMonitor
from presence.absence_detector import AbsenceDetector

from services.startup_manager import StartupManager
from services.updater import AutoUpdater

from utils.logger import get_logger
from utils.helpers import is_admin, ensure_single_instance

logger = get_logger("jarvis.main")


class JarvisV3:
    """Top-level orchestrator for the v3 Voice-First HUD System."""

    def __init__(self) -> None:
        self.config = Config.load()
        self.state = AppState()

        # Voice
        self.speaker = JarvisSpeaker(self.config)
        self.recognizer = CommandRecognizer()
        self.wake_detector = WakeWordDetector(
            on_wake=self._on_wake_word,
            wake_word=self.config.wake_word,
        )

        # HUD
        self.hud = HUDWindow(self.config, self.state)
        self.voice_ring = VoiceRing()

        # Modes
        self.mode_ctrl = ModeController(self.config)

        # Workspace
        self.launcher = WorkspaceLauncher(self.config)
        self.arranger = WindowArranger(self.config)
        self.deactivator = WorkspaceDeactivator()

        # Presence
        self.wifi_monitor = WiFiMonitor(
            self.config, self.state,
            on_present=self._on_presence_detected,
        )
        self.absence_det = AbsenceDetector(
            self.config, self.wifi_monitor, self.state,
            on_absent=self._on_absence_detected,
        )

        # Services
        self.startup_mgr = StartupManager()
        self.updater = AutoUpdater()

        # Chime
        self._chime_path = ensure_chime()

    # ─────────────────────────────────────────────
    # STARTUP
    # ─────────────────────────────────────────────

    def start(self) -> None:
        logger.info(f"{'=' * 50}")
        logger.info(f" {__app_name__} v{__version__} — Voice-First HUD")
        logger.info(f"{'=' * 50}")

        if not ensure_single_instance():
            logger.error("Another instance running. Exiting.")
            sys.exit(1)

        if not is_admin():
            logger.warning("Not Administrator — global hotkeys may fail.")

        # First-run setup
        if not self.config.setup_complete:
            logger.info("First run — launching setup wizard…")
            from ui.wizard import SetupWizard
            wizard = SetupWizard(
                self.config, on_complete=lambda: None,
            )
            if not wizard.run():
                logger.info("Wizard cancelled. Exiting.")
                sys.exit(0)
            self.config = Config.load()

        # Startup registration
        if self.config.launch_on_startup:
            self.startup_mgr.enable()

        # Boot sequence — runs BEFORE HUD mainloop
        threading.Thread(
            target=self._boot_sequence, daemon=True,
        ).start()

        # Start background services
        self.wake_detector.start()
        self.wifi_monitor.start()
        self.absence_det.start()

        # Manual hotkey
        try:
            import keyboard
            keyboard.add_hotkey(
                self.config.hotkey,
                lambda: self._on_wake_word(),
            )
            logger.info(f"Hotkey registered: {self.config.hotkey}")
        except Exception as exc:
            logger.warning(f"Hotkey failed: {exc}")

        self.state.state = WorkmodeState.IDLE
        logger.info("JARVIS v3 online. HUD visible. Listening for wake word.")

        # Blocking — HUD event loop on main thread
        self.hud.run()

        # Shutdown
        logger.info("Shutting down…")
        self.wake_detector.stop()
        self.wifi_monitor.stop()
        self.absence_det.stop()
        logger.info("Goodbye! 👋")

    def _boot_sequence(self) -> None:
        """Typewriter boot lines on the HUD + greeting speech."""
        time.sleep(0.5)  # Let HUD initialize
        boot_lines = [
            "SYSTEM BOOT SEQUENCE INITIATED",
            "VOICE ENGINE..........ONLINE",
            "PRESENCE MONITOR......ONLINE",
            "HUD RENDERER..........ONLINE",
            "ALL SYSTEMS NOMINAL",
        ]
        for line in boot_lines:
            self.hud.set_speech_text(line)
            time.sleep(0.6)

        greeting = get_greeting()
        self.hud.set_speech_text(greeting)
        self.speaker.speak(greeting)

    # ─────────────────────────────────────────────
    # VOICE INTERACTION
    # ─────────────────────────────────────────────

    def _on_wake_word(self) -> None:
        if self.state.state == WorkmodeState.LISTENING:
            return

        self.state.state = WorkmodeState.LISTENING
        self.state.is_listening = True

        # Chime + ring
        self._play_chime()
        self.voice_ring.show(duration=self.config.voice_command_timeout)
        self.speaker.speak(RESPONSES["wake"], blocking=True)

        # Listen in background
        threading.Thread(
            target=self._process_voice_command, daemon=True,
        ).start()

    def _process_voice_command(self) -> None:
        raw_text = self.recognizer.listen_for_command(
            duration_seconds=self.config.voice_command_timeout,
        )
        self.state.is_listening = False
        self.state.state = WorkmodeState.IDLE

        logger.info(f"Voice: '{raw_text}'")
        self.hud.set_speech_text(f"Heard: {raw_text}" if raw_text else "…")

        if not raw_text:
            self.speaker.speak(RESPONSES["cmd_unknown"])
            return

        command = parse_command(raw_text)
        self._execute_command(command)

    def _execute_command(self, cmd: Command) -> None:
        handlers = {
            Command.ACTIVATE:     lambda: self._activate_workspace("voice"),
            Command.DEACTIVATE:   lambda: self._deactivate_workspace("voice"),
            Command.PAUSE:        self._pause,
            Command.RESUME:       self._resume,
            Command.STATUS:       self._report_status,
            Command.VOLUME_UP:    lambda: self.speaker.speak(RESPONSES["cmd_volume_up"]),
            Command.VOLUME_DOWN:  lambda: self.speaker.speak(RESPONSES["cmd_volume_down"]),
            Command.OPEN_SPOTIFY: lambda: self.speaker.speak(RESPONSES["cmd_spotify"]),
            Command.CLOSE_ALL:    lambda: self._deactivate_workspace("voice"),
            Command.UNKNOWN:      lambda: self.speaker.speak(RESPONSES["cmd_unknown"]),
        }
        handler = handlers.get(cmd, handlers[Command.UNKNOWN])
        handler()

    # ─────────────────────────────────────────────
    # ACTIVATION
    # ─────────────────────────────────────────────

    def _on_presence_detected(self) -> None:
        if self.state.can_activate(self.config.activation_cooldown_minutes):
            self._activate_workspace("presence")

    def _activate_workspace(self, source: str = "voice") -> None:
        if not self.state.can_activate(self.config.activation_cooldown_minutes):
            self.speaker.speak(RESPONSES["already_active"])
            return

        self.state.state = WorkmodeState.ACTIVATING
        threading.Thread(
            target=self._run_activation, args=(source,),
            daemon=True, name="ActivationThread",
        ).start()

    def _run_activation(self, source: str) -> None:
        mode = self.mode_ctrl.get_current_mode()
        self.state.current_mode_name = mode.name

        # Briefing
        time_str = datetime.now().strftime("%I:%M %p")
        brief = briefing(mode.name, time_str)
        self.hud.set_speech_text(brief)
        self.speaker.speak(brief)

        # Cinematic
        screen = BriefingScreen(mode.name, mode.apps_to_launch)
        screen.show()
        time.sleep(1.0)

        # Launch + arrange
        self.launcher.launch_apps(mode.apps_to_launch)
        time.sleep(2.5)
        self.arranger.arrange(mode.layout)

        # Spotify
        if "spotify" in mode.apps_to_launch and self.config.spotify_enabled:
            self._start_spotify(mode)

        self.state.state = WorkmodeState.ACTIVE
        self.state.last_activation_time = time.time()
        self.hud.set_speech_text(RESPONSES["workspace_ready"])
        self.speaker.speak(RESPONSES["workspace_ready"])
        logger.info(f"Workspace active — mode: {mode.name}, source: {source}")

    # ─────────────────────────────────────────────
    # DEACTIVATION
    # ─────────────────────────────────────────────

    def _on_absence_detected(self) -> None:
        if self.state.state != WorkmodeState.ACTIVE:
            return
        logger.info("Departure detected.")
        self.hud.set_speech_text(RESPONSES["departure_detected"])
        self.speaker.speak(RESPONSES["departure_detected"])
        self._deactivate_workspace("absence")

    def _deactivate_workspace(self, source: str = "voice") -> None:
        if self.state.state in (WorkmodeState.IDLE, WorkmodeState.DEACTIVATING):
            return

        self.state.state = WorkmodeState.DEACTIVATING
        threading.Thread(
            target=self._run_deactivation, args=(source,),
            daemon=True, name="DeactivationThread",
        ).start()

    def _run_deactivation(self, source: str) -> None:
        self.speaker.speak(RESPONSES["deactivating"], blocking=True)

        mode = self.mode_ctrl.get_current_mode()
        self.deactivator.close_all(mode.apps_to_launch)

        self.state.state = WorkmodeState.IDLE
        self.state.current_mode_name = "Standby"
        self.hud.set_speech_text(RESPONSES["deactivated"])
        self.speaker.speak(RESPONSES["deactivated"])
        logger.info(f"Workspace deactivated (source: {source}).")

        # Re-arm absence detector
        self.absence_det.start()

    # ─────────────────────────────────────────────
    # MISC
    # ─────────────────────────────────────────────

    def _pause(self) -> None:
        self.state.state = WorkmodeState.PAUSED
        self.speaker.speak(RESPONSES["cmd_pause"])
        self.hud.set_speech_text(RESPONSES["cmd_pause"])

    def _resume(self) -> None:
        self.state.state = WorkmodeState.IDLE
        self.speaker.speak(RESPONSES["cmd_resume"])
        self.hud.set_speech_text(RESPONSES["cmd_resume"])

    def _report_status(self) -> None:
        status = (
            f"Current mode is {self.state.current_mode_name}. "
            f"System is {self.state.state.name.lower()}. "
            f"Phone is {'detected' if self.state.phone_present else 'not detected'}."
        )
        self.speaker.speak(status)
        self.hud.set_speech_text(status)

    def _play_chime(self) -> None:
        try:
            winsound.PlaySound(
                str(self._chime_path),
                winsound.SND_FILENAME | winsound.SND_ASYNC,
            )
        except Exception:
            pass

    def _start_spotify(self, mode) -> None:
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth

            auth = SpotifyOAuth(
                client_id=self.config.spotify_client_id,
                client_secret=self.config.spotify_client_secret,
                redirect_uri=self.config.spotify_redirect_uri,
                scope="user-modify-playback-state user-read-playback-state",
            )
            sp = spotipy.Spotify(auth_manager=auth)
            devices = sp.devices().get("devices", [])
            playlist = (
                mode.spotify_playlist_uri
                or getattr(self.config, f"{mode.name.lower().replace(' ', '_')}_playlist", "")
            )
            if devices:
                device_id = devices[0]["id"]
                if playlist:
                    sp.start_playback(device_id=device_id, context_uri=playlist)
                else:
                    sp.start_playback(device_id=device_id)
                sp.volume(self.config.spotify_volume, device_id=device_id)
                logger.info("Spotify playback started.")
        except Exception as exc:
            self.speaker.speak(RESPONSES["error_spotify"])
            logger.error(f"Spotify error: {exc}")


def main() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass
    JarvisV3().start()


if __name__ == "__main__":
    main()
