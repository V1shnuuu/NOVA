"""
JARVIS WorkMode v3 — Voice Command Parser
Maps raw transcribed text to a Command enum via keyword matching.
No NLP library needed — keeps it offline and fast.
"""

from __future__ import annotations

from enum import Enum, auto


class Command(Enum):
    ACTIVATE     = auto()
    DEACTIVATE   = auto()
    PAUSE        = auto()
    RESUME       = auto()
    STATUS       = auto()
    VOLUME_UP    = auto()
    VOLUME_DOWN  = auto()
    OPEN_SPOTIFY = auto()
    CLOSE_ALL    = auto()
    SWITCH_MODE  = auto()
    UNKNOWN      = auto()


_COMMAND_MAP: dict[Command, list[str]] = {
    Command.ACTIVATE:     ["activate", "start", "begin", "wake up", "launch", "let's go"],
    Command.DEACTIVATE:   ["deactivate", "shutdown", "stop", "goodbye", "shut down"],
    Command.PAUSE:        ["pause", "hold on", "wait", "stop monitoring"],
    Command.RESUME:       ["resume", "continue", "keep watching"],
    Command.STATUS:       ["status", "report", "how are you", "what's happening"],
    Command.VOLUME_UP:    ["volume up", "louder", "turn it up"],
    Command.VOLUME_DOWN:  ["volume down", "quieter", "turn it down"],
    Command.OPEN_SPOTIFY: ["spotify", "music", "play music"],
    Command.CLOSE_ALL:    ["close everything", "close all", "clear workspace"],
    Command.SWITCH_MODE:  ["switch mode", "change mode", "work mode", "evening mode", "focus mode"],
}


def parse_command(text: str) -> Command:
    """Return the best-matching ``Command`` for *text*, or ``UNKNOWN``."""
    text = text.lower().strip()
    for command, keywords in _COMMAND_MAP.items():
        if any(kw in text for kw in keywords):
            return command
    return Command.UNKNOWN
