"""
JARVIS WorkMode v3 — Workspace Deactivator
Gracefully closes workspace apps when the user departs.
Browser tabs: WM_CLOSE on matching windows.
Spotify: terminate process.
"""

from __future__ import annotations

import psutil

from workspace.app_profiles import APP_PROFILES
from utils.logger import get_logger

logger = get_logger("jarvis.workspace.deactivator")

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WorkspaceDeactivator:
    """Gracefully shuts down workspace applications."""

    def close_all(self, apps: list[str]) -> None:
        for app in apps:
            if app == "spotify":
                self._close_spotify()
            else:
                self._close_browser_windows(app)

    def _close_browser_windows(self, app_name: str) -> None:
        if not WIN32_AVAILABLE:
            logger.warning("win32gui unavailable — cannot close browser windows.")
            return

        terms = APP_PROFILES.get(app_name, [])
        closed = 0

        def _enum_callback(hwnd: int, _: None) -> None:
            nonlocal closed
            title = win32gui.GetWindowText(hwnd)
            if any(t.lower() in title.lower() for t in terms):
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    closed += 1
                except Exception:
                    pass

        try:
            win32gui.EnumWindows(_enum_callback, None)
        except Exception as exc:
            logger.error(f"EnumWindows failed for '{app_name}': {exc}")

        if closed:
            logger.info(f"Closed {closed} window(s) for '{app_name}'.")
        else:
            logger.debug(f"No windows found for '{app_name}'.")

    @staticmethod
    def _close_spotify() -> None:
        for proc in psutil.process_iter(["name"]):
            try:
                if "spotify" in (proc.info["name"] or "").lower():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
                    logger.info("Spotify closed.")
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        logger.debug("Spotify was not running.")
