"""
JARVIS WorkMode — Utility Functions
Retry decorator, admin check, process helpers.
"""

from __future__ import annotations

import ctypes
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def retry(
    times: int = 3,
    delay: float = 1.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable:
    """Decorator: retry a function *times* on failure.

    Args:
        times: Maximum number of attempts.
        delay: Seconds to wait between retries.
        exceptions: Exception types that trigger a retry.
    """
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


def is_admin() -> bool:
    """Return ``True`` if the script is running with Windows Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0  # type: ignore[union-attr]
    except AttributeError:
        return False


def wait_for_process(name: str, timeout: int = 10) -> bool:
    """Wait until a process with *name* appears in the process list.

    Args:
        name: Case-insensitive substring to match against process names.
        timeout: Maximum seconds to wait.

    Returns:
        ``True`` if the process was found within the timeout.
    """
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
    """Return a sorted list of unique running process names (diagnostic helper)."""
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
    """Return a list of all visible window titles (diagnostic helper)."""
    import pygetwindow as gw

    return [w.title for w in gw.getAllWindows() if w.title.strip()]
