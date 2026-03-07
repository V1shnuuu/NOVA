"""
JARVIS WorkMode — Window Layout Engine
Finds, restores, and positions windows into a tiled layout.
Uses ``pygetwindow`` with ``win32gui`` fallback for stubborn windows.
"""

from __future__ import annotations

import ctypes
import time

import pygetwindow as gw

from utils.logger import get_logger

logger = get_logger("jarvis.automation.windows")

# Try importing win32gui for the fallback path
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning(
        "pywin32 not available — window management will rely on pygetwindow only."
    )


# ── Search keywords per app ─────────────────────────────────────────
_WINDOW_KEYWORDS: dict[str, list[str]] = {
    "chatgpt": ["ChatGPT", "chat.openai.com", "OpenAI"],
    "claude":  ["Claude", "claude.ai", "Anthropic"],
    "spotify": ["Spotify"],
}


class WindowManager:
    """Discovers and arranges application windows according to the configured layout."""

    def __init__(self, config) -> None:
        self.config = config
        self.screen_width, self.screen_height = self._get_screen_size()
        logger.debug(
            f"Primary screen: {self.screen_width}×{self.screen_height}"
        )

    # ── Public ───────────────────────────────────────────────────────

    def arrange_workspace(self) -> None:
        """Position all configured applications."""
        for app_name in self.config.LAYOUT:
            self._wait_and_arrange(app_name)

    # ── Private ──────────────────────────────────────────────────────

    @staticmethod
    def _get_screen_size() -> tuple[int, int]:
        """Return (width, height) of the primary monitor."""
        user32 = ctypes.windll.user32  # type: ignore[union-attr]
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def _wait_and_arrange(self, app_name: str) -> None:
        """Find a window for *app_name* and move it to the configured rectangle."""
        layout = self.config.LAYOUT.get(app_name)
        if layout is None:
            logger.warning(f"No layout entry for '{app_name}' — skipping.")
            return

        window = self._find_window(
            app_name,
            timeout=self.config.WINDOW_FIND_TIMEOUT,
        )
        if window is None:
            logger.warning(f"Window for '{app_name}' not found within timeout.")
            return

        x = int(layout["x"] * self.screen_width)
        y = int(layout["y"] * self.screen_height)
        w = int(layout["w"] * self.screen_width)
        h = int(layout["h"] * self.screen_height)
        self._move_window(window, x, y, w, h, app_name)

    def _find_window(
        self,
        app_name: str,
        timeout: int = 15,
    ) -> gw.Win32Window | None:
        """Poll for a window whose title matches known keywords."""
        search_terms = _WINDOW_KEYWORDS.get(app_name, [app_name])
        deadline = time.time() + timeout

        while time.time() < deadline:
            for win in gw.getAllWindows():
                title = win.title.lower()
                if any(term.lower() in title for term in search_terms):
                    logger.debug(
                        f"Matched '{app_name}' → window '{win.title}'"
                    )
                    return win
            time.sleep(0.5)

        # Fallback: brute-force via win32gui.EnumWindows
        if WIN32_AVAILABLE:
            return self._find_window_win32(search_terms)
        return None

    def _find_window_win32(
        self,
        search_terms: list[str],
    ) -> gw.Win32Window | None:
        """Fallback search using ``win32gui.EnumWindows``."""
        matched_hwnd: int | None = None

        def _enum_callback(hwnd: int, _extra: None) -> None:
            nonlocal matched_hwnd
            if matched_hwnd is not None:
                return
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).lower()
            if any(term.lower() in title for term in search_terms):
                matched_hwnd = hwnd

        win32gui.EnumWindows(_enum_callback, None)

        if matched_hwnd is not None:
            # Wrap the HWND back into a pygetwindow object for consistency
            for win in gw.getAllWindows():
                try:
                    if win._hWnd == matched_hwnd:
                        return win
                except AttributeError:
                    continue
        return None

    def _move_window(
        self,
        window: gw.Win32Window,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str = "",
    ) -> None:
        """Restore and reposition a window, falling back to win32gui if needed."""
        try:
            window.restore()
            time.sleep(0.3)
            window.moveTo(x, y)
            window.resizeTo(w, h)
            logger.info(
                f"Arranged '{label}' → ({x}, {y}, {w}×{h})"
            )
        except Exception as exc:
            logger.warning(
                f"pygetwindow move failed for '{label}': {exc}. "
                f"Trying win32gui fallback…"
            )
            self._force_move_window(window, x, y, w, h, label)

    def _force_move_window(
        self,
        window: gw.Win32Window,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str = "",
    ) -> None:
        """Use raw win32gui calls to position a stubborn window."""
        if not WIN32_AVAILABLE:
            logger.error("win32gui unavailable — cannot force move window.")
            return
        try:
            hwnd = window._hWnd
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOP,
                x, y, w, h,
                win32con.SWP_SHOWWINDOW,
            )
            logger.info(
                f"Arranged '{label}' via win32gui → ({x}, {y}, {w}×{h})"
            )
        except Exception as exc:
            logger.error(f"win32gui fallback failed for '{label}': {exc}")
