"""
JARVIS WorkMode v3 — Full-Screen Activation Cinematic
Shown during workspace activation — a JARVIS-style briefing overlay.

Sequence (4 seconds):
  0.0s  Screen dims (fade in to 70% black)
  0.5s  Hex grid renders across full screen
  1.0s  Mode name in large Orbitron-style font
  1.5s  "WORKSPACE INITIALIZING" text
  2.0s  App names appear bottom center
  2.5s  Scan lines sweep
  3.5s  Fade out
  4.0s  Window destroyed
"""

from __future__ import annotations

import math
import threading
import time
import tkinter as tk

from utils.logger import get_logger

logger = get_logger("jarvis.hud.briefing")

CYAN = "#00d4ff"
CYAN_DIM = "#4a8fa8"
SUCCESS = "#00ff9d"


class BriefingScreen:
    """Briefly shows a full-screen JARVIS cinematic during activation."""

    def __init__(self, mode_name: str, apps: list[str]) -> None:
        self.mode_name = mode_name
        self.apps = apps

    def show(self) -> None:
        """Non-blocking — launches the animation in a daemon thread."""
        threading.Thread(
            target=self._run_animation, daemon=True,
            name="BriefingScreenThread",
        ).start()

    def _run_animation(self) -> None:
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.attributes("-fullscreen", True)
            root.attributes("-alpha", 0.0)
            root.configure(bg="#000000")

            w = root.winfo_screenwidth()
            h = root.winfo_screenheight()

            canvas = tk.Canvas(
                root, width=w, height=h,
                bg="#000000", highlightthickness=0,
            )
            canvas.pack()

            # Fade in
            for alpha in range(0, 75, 3):
                root.attributes("-alpha", alpha / 100)
                time.sleep(0.016)

            # Draw hex grid
            hex_size = 32
            col_w = hex_size * 1.732
            row_h = hex_size * 1.5
            for row in range(int(h / row_h) + 2):
                for col in range(int(w / col_w) + 2):
                    cx = col * col_w + (hex_size * 0.866 if row % 2 else 0)
                    cy = row * row_h
                    pts: list[float] = []
                    for i in range(6):
                        angle = math.radians(60 * i - 30)
                        pts.extend([
                            cx + hex_size * math.cos(angle),
                            cy + hex_size * math.sin(angle),
                        ])
                    canvas.create_polygon(pts, outline="#00d4ff18", fill="", width=1)

            # Mode name — giant centered
            canvas.create_text(
                w // 2, h // 2 - 60,
                text=self.mode_name.upper(),
                font=("Segoe UI", 52, "bold"),
                fill=CYAN,
            )

            # Subtitle
            canvas.create_text(
                w // 2, h // 2 + 10,
                text="WORKSPACE INITIALIZING",
                font=("Consolas", 18),
                fill=CYAN_DIM,
            )

            # App list
            total_apps = len(self.apps)
            for i, app in enumerate(self.apps):
                offset = (i - total_apps // 2) * 200
                canvas.create_text(
                    w // 2 + offset, h // 2 + 100,
                    text=f"[ {app.upper()} ]",
                    font=("Consolas", 13),
                    fill=SUCCESS,
                )

            # Horizontal scan lines
            for line_y in [h // 3, h // 2, 2 * h // 3]:
                canvas.create_line(0, line_y, w, line_y, fill=CYAN, width=1)

            root.update()
            time.sleep(2.5)

            # Fade out
            for alpha in range(75, 0, -3):
                root.attributes("-alpha", alpha / 100)
                time.sleep(0.016)

            root.destroy()
            logger.debug("Briefing screen closed.")

        except Exception as exc:
            logger.debug(f"Briefing screen error: {exc}")
