"""
JARVIS WorkMode v3 — Spoken Response Lines
All words JARVIS speaks, centralised for easy personality tuning.

Tone: Calm, precise, slightly formal.
No 'okay' or 'sure' — uses 'Understood', 'Initiating', 'Confirmed'.
"""

from __future__ import annotations

from datetime import datetime


def get_greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning. Systems are online. Initiating morning workspace."
    elif hour < 18:
        return "Good afternoon. Productivity systems standing by."
    else:
        return "Good evening. Activating evening workspace configuration."


RESPONSES: dict[str, str] = {
    # Activation
    "wake":              "Yes?",
    "activating":        "Initiating workspace. Stand by.",
    "workspace_ready":   "Workspace is ready. All systems nominal.",
    "already_active":    "Workspace is already active.",

    # Modes
    "deep_work_mode":    "Deep work mode activated. Minimizing distractions.",
    "afternoon_mode":    "Afternoon configuration loaded. Research layout active.",
    "evening_mode":      "Evening mode. Winding down productivity systems.",

    # Deactivation
    "departure_detected": "Presence no longer detected. Initiating shutdown sequence.",
    "deactivating":       "Closing workspace. Goodbye.",
    "deactivated":        "All systems offline. Have a good one.",

    # Voice commands
    "cmd_unknown":       "I didn't catch that. Could you repeat?",
    "cmd_pause":         "Monitoring paused. I'll be standing by.",
    "cmd_resume":        "Monitoring resumed. Watching for your return.",
    "cmd_volume_up":     "Increasing volume.",
    "cmd_volume_down":   "Reducing volume.",
    "cmd_spotify":       "Opening Spotify.",
    "cmd_status":        "All systems are operational. No anomalies detected.",
    "cmd_close_all":     "Closing all workspace applications.",

    # Update
    "update_available":  "An update is available. I recommend installing it at your convenience.",

    # Errors
    "error_spotify":     "I was unable to connect to Spotify. Proceeding without music.",
    "error_browser":     "Browser launch encountered an issue. Attempting recovery.",
}


def briefing(mode_name: str, time_str: str) -> str:
    """Generate a spoken briefing for workspace activation."""
    return (
        f"It is {time_str}. {get_greeting()} "
        f"Loading {mode_name} configuration. "
        f"All applications are standing by."
    )
