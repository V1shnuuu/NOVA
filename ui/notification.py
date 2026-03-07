"""
JARVIS WorkMode — Windows 11 Toast Notifications (v2)
Wraps win10toast for activation, update, and detection toasts.
"""

from __future__ import annotations

from config import Config
from utils.logger import get_logger

logger = get_logger("jarvis.ui.notification")

try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    logger.warning("win10toast not installed — notifications disabled.")


class NotificationService:
    """Sends native Windows 11 toast notifications."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._toaster: ToastNotifier | None = None
        if TOAST_AVAILABLE:
            try:
                self._toaster = ToastNotifier()
            except Exception as exc:
                logger.warning(f"ToastNotifier init failed: {exc}")

    # ── Public API ───────────────────────────────────────────────────

    def notify_activation(self) -> None:
        """Toast shown after workspace has fully activated."""
        if not self.config.show_activation_notifications:
            return
        self._show(
            "JARVIS WorkMode",
            "Workspace activated. Welcome back. 🚀",
            duration=4,
        )

    def notify_phone_detected(self) -> None:
        """Toast shown when the phone is detected on the network."""
        if not self.config.show_activation_notifications:
            return
        self._show(
            "JARVIS WorkMode",
            "Phone detected on network. Activating workspace…",
            duration=3,
        )

    def notify_update_available(self, version: str) -> None:
        """Toast shown when a newer version is available on GitHub."""
        self._show(
            "JARVIS WorkMode — Update Available",
            f"Version {version} is ready. Right-click tray icon to update.",
            duration=8,
        )

    # ── Private ──────────────────────────────────────────────────────

    def _show(self, title: str, msg: str, duration: int = 5) -> None:
        if self._toaster is None:
            return
        try:
            self._toaster.show_toast(
                title,
                msg,
                duration=duration,
                threaded=True,
            )
        except Exception as exc:
            logger.debug(f"Toast failed: {exc}")
