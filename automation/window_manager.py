"""
JARVIS WorkMode — Window Layout Engine (v2)
Finds windows by fuzzy title match, tiles them using pygetwindow + win32gui fallback.
"""

from __future__ import annotations

import ctypes
import time

import pygetwindow as gw

from utils.logger import get_logger

logger = get_logger("jarvis.automation.windows")

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32 unavailable — limited window control.")

_WINDOW_KEYWORDS: dict[str, list[str]] = {
    "chatgpt": ["ChatGPT", "chat.openai.com", "OpenAI"],
    "claude":  ["Claude", "claude.ai", "Anthropic"],
    "spotify": ["Spotify"],
}


class WindowManager:
    """Discovers and arranges windows per the configured layout."""

    def __init__(self, config) -> None:
        self.config = config
        self.screen_width, self.screen_height = self._get_screen_size()
        logger.debug(f"Screen: {self.screen_width}×{self.screen_height}")

    def arrange_workspace(self) -> None:
        """Position every app listed in ``config.layout``."""
        for app_name in self.config.layout:
            self._wait_and_arrange(app_name)

    @staticmethod
    def _get_screen_size() -> tuple[int, int]:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def _wait_and_arrange(self, app_name: str) -> None:
        layout = self.config.layout.get(app_name)
        if layout is None:
            logger.warning(f"No layout for '{app_name}'.")
            return

        window = self._find_window(
            app_name, timeout=self.config.window_find_timeout,
        )
        if window is None:
            logger.warning(f"Window for '{app_name}' not found.")
            return

        x = int(layout["x"] * self.screen_width)
        y = int(layout["y"] * self.screen_height)
        w = int(layout["w"] * self.screen_width)
        h = int(layout["h"] * self.screen_height)
        self._move_window(window, x, y, w, h, app_name)

    def _find_window(
        self, app_name: str, timeout: int = 15,
    ) -> gw.Win32Window | None:
        search_terms = _WINDOW_KEYWORDS.get(app_name, [app_name])
        deadline = time.time() + timeout
        while time.time() < deadline:
            for win in gw.getAllWindows():
                title = win.title.lower()
                if any(t.lower() in title for t in search_terms):
                    logger.debug(f"Matched '{app_name}' → '{win.title}'")
                    return win
            time.sleep(0.5)

        if WIN32_AVAILABLE:
            return self._find_window_win32(search_terms)
        return None

    def _find_window_win32(
        self, search_terms: list[str],
    ) -> gw.Win32Window | None:
        matched_hwnd: int | None = None

        def _callback(hwnd: int, _: None) -> None:
            nonlocal matched_hwnd
            if matched_hwnd is not None:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).lower()
            if any(t.lower() in title for t in search_terms):
                matched_hwnd = hwnd

        win32gui.EnumWindows(_callback, None)
        if matched_hwnd is not None:
            for win in gw.getAllWindows():
                try:
                    if win._hWnd == matched_hwnd:
                        return win
                except AttributeError:
                    continue
        return None

    def _move_window(
        self, window: gw.Win32Window, x: int, y: int, w: int, h: int,
        label: str = "",
    ) -> None:
        try:
            window.restore()
            time.sleep(0.3)
            window.moveTo(x, y)
            window.resizeTo(w, h)
            logger.info(f"Arranged '{label}' → ({x}, {y}, {w}×{h})")
        except Exception as exc:
            logger.warning(
                f"pygetwindow failed for '{label}': {exc} — trying win32gui…"
            )
            self._force_move(window, x, y, w, h, label)

    def _force_move(
        self, window: gw.Win32Window, x: int, y: int, w: int, h: int,
        label: str = "",
    ) -> None:
        if not WIN32_AVAILABLE:
            logger.error("win32gui unavailable — cannot force-move window.")
            return
        try:
            hwnd = window._hWnd
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(
                hwnd, win32con.HWND_TOP, x, y, w, h,
                win32con.SWP_SHOWWINDOW,
            )
            logger.info(f"Arranged '{label}' via win32gui → ({x}, {y}, {w}×{h})")
        except Exception as exc:
            logger.error(f"win32gui failed for '{label}': {exc}")
