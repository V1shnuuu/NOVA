"""
JARVIS WorkMode — Utility Functions (v2)
Retry decorator, admin check, process helpers, single-instance mutex.
"""

from __future__ import annotations

import ctypes
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


# ── Retry Decorator ──────────────────────────────────────────────────

def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable:
    """Decorator: retry a function *times* on failure."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator


# ── Admin Check ──────────────────────────────────────────────────────

def is_admin() -> bool:
    """Return ``True`` if running with Windows Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[union-attr]
    except AttributeError:
        return False


# ── Single Instance Mutex ────────────────────────────────────────────

_MUTEX_HANDLE = None


def ensure_single_instance(app_name: str = "JarvisWorkMode") -> bool:
    """Ensure only one instance of the app is running.

    Creates a Windows named mutex. Returns ``True`` if this is the first
    instance, ``False`` if another instance already holds the mutex.
    """
    global _MUTEX_HANDLE  # noqa: PLW0603
    try:
        kernel32 = ctypes.windll.kernel32  # type: ignore[union-attr]
        _MUTEX_HANDLE = kernel32.CreateMutexW(None, True, f"Global\\{app_name}")
        last_error = kernel32.GetLastError()
        # ERROR_ALREADY_EXISTS = 183
        if last_error == 183:
            kernel32.CloseHandle(_MUTEX_HANDLE)
            _MUTEX_HANDLE = None
            return False
        return True
    except Exception:
        return True  # Non-Windows or error — allow running


# ── Process Helpers ──────────────────────────────────────────────────

def wait_for_process(name: str, timeout: int = 10) -> bool:
    """Wait until a process with *name* appears in the process list."""
    import psutil

    deadline = time.time() + timeout
    while time.time() < deadline:
        for proc in psutil.process_iter(["name"]):
            try:
                if name.lower() in (proc.info["name"] or "").lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(0.5)
    return False


def get_running_processes() -> list[str]:
    """Return a sorted list of unique running process names."""
    import psutil

    names: set[str] = set()
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"]:
                names.add(proc.info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(names)


def get_all_window_titles() -> list[str]:
    """Return a list of all visible window titles."""
    import pygetwindow as gw

    return [w.title for w in gw.getAllWindows() if w.title.strip()]
