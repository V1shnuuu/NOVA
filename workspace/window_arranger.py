"""
JARVIS WorkMode v3 — Window Arranger
Positions and resizes windows per a mode's layout specification.
"""

from __future__ import annotations

import ctypes
import time

import pygetwindow as gw

from modes.base_mode import WindowLayout
from workspace.app_profiles import APP_PROFILES
from utils.logger import get_logger

logger = get_logger("jarvis.workspace.arranger")

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowArranger:
    """Arranges application windows according to a list of WindowLayout specs."""

    def __init__(self, config) -> None:
        self.config = config
        self.screen_w, self.screen_h = self._get_screen_size()

    def arrange(self, layouts: list[WindowLayout]) -> None:
        for spec in layouts:
            window = self._find_window(spec.app_name, timeout=15)
            if window is None:
                logger.warning(f"Window for '{spec.app_name}' not found.")
                continue
            x = int(spec.x_pct * self.screen_w)
            y = int(spec.y_pct * self.screen_h)
            w = int(spec.w_pct * self.screen_w)
            h = int(spec.h_pct * self.screen_h)
            self._move(window, x, y, w, h, spec.app_name)

    @staticmethod
    def _get_screen_size() -> tuple[int, int]:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def _find_window(
        self, app_name: str, timeout: int = 15,
    ) -> gw.Win32Window | None:
        terms = APP_PROFILES.get(app_name, [app_name])
        deadline = time.time() + timeout
        while time.time() < deadline:
            for win in gw.getAllWindows():
                title = win.title.lower()
                if any(t.lower() in title for t in terms):
                    return win
            time.sleep(0.5)

        if WIN32_AVAILABLE:
            return self._find_win32(terms)
        return None

    def _find_win32(self, terms: list[str]) -> gw.Win32Window | None:
        matched_hwnd: int | None = None

        def _cb(hwnd: int, _: None) -> None:
            nonlocal matched_hwnd
            if matched_hwnd is not None:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).lower()
            if any(t.lower() in title for t in terms):
                matched_hwnd = hwnd

        win32gui.EnumWindows(_cb, None)
        if matched_hwnd is not None:
            for win in gw.getAllWindows():
                try:
                    if win._hWnd == matched_hwnd:
                        return win
                except AttributeError:
                    continue
        return None

    def _move(
        self, window: gw.Win32Window, x: int, y: int, w: int, h: int,
        label: str,
    ) -> None:
        try:
            window.restore()
            time.sleep(0.3)
            window.moveTo(x, y)
            window.resizeTo(w, h)
            logger.info(f"Arranged '{label}' → ({x},{y} {w}x{h})")
        except Exception:
            if WIN32_AVAILABLE:
                try:
                    hwnd = window._hWnd
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetWindowPos(
                        hwnd, win32con.HWND_TOP, x, y, w, h,
                        win32con.SWP_SHOWWINDOW,
                    )
                    logger.info(f"Arranged '{label}' via win32gui.")
                except Exception as exc:
                    logger.error(f"win32gui failed for '{label}': {exc}")
