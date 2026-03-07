"""
JARVIS WorkMode — Windows Startup Manager (v2)
Manages the HKCU\\...\\Run registry key so the app launches at login.
"""

from __future__ import annotations

import sys
import winreg
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("jarvis.services.startup")

REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REGISTRY_NAME = "JarvisWorkMode"


class StartupManager:
    """Add / remove the application from Windows startup via the registry."""

    def enable(self) -> bool:
        """Register the app to start at Windows login. Returns ``True`` on success."""
        exe_path = self._get_exe_path()
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0,
                winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(
                key, APP_REGISTRY_NAME, 0, winreg.REG_SZ,
                f'"{exe_path}"',
            )
            winreg.CloseKey(key)
            logger.info(f"Startup enabled: {exe_path}")
            return True
        except OSError as exc:
            logger.error(f"Could not enable startup: {exc}")
            return False

    def disable(self) -> bool:
        """Remove the app from Windows startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, REGISTRY_KEY, 0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, APP_REGISTRY_NAME)
            winreg.CloseKey(key)
            logger.info("Startup disabled.")
            return True
        except FileNotFoundError:
            return True  # Already absent
        except OSError as exc:
            logger.error(f"Could not disable startup: {exc}")
            return False

    def is_enabled(self) -> bool:
        """Check whether the app is registered for startup."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_KEY)
            winreg.QueryValueEx(key, APP_REGISTRY_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def _get_exe_path() -> str:
        """Return the correct executable path whether running as .exe or .py."""
        if getattr(sys, "frozen", False):
            return sys.executable
        main_py = Path(__file__).resolve().parent.parent / "main.py"
        return f"{sys.executable} {main_py}"
