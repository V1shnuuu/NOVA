"""
JARVIS WorkMode v3 — Voice Ring Overlay
Pulsing concentric cyan rings displayed center-screen while JARVIS listens.
Auto-hides after the specified duration.
"""

from __future__ import annotations

import math
import time
import tkinter as tk
import threading

from utils.logger import get_logger

logger = get_logger("jarvis.hud.voice_ring")

RING_SIZE = 180
TRANSPARENT_KEY = "#000001"
CYAN = "#00d4ff"


class VoiceRing:
    """Transparent overlay showing pulsing rings during voice listening."""

    def __init__(self) -> None:
        self._active = False

    def show(self, duration: float = 5.0) -> None:
        """Display the ring for *duration* seconds (non-blocking)."""
        threading.Thread(
            target=self._display, args=(duration,),
            daemon=True, name="VoiceRingThread",
        ).start()

    def _display(self, duration: float) -> None:
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.attributes("-transparentcolor", TRANSPARENT_KEY)
            root.configure(bg=TRANSPARENT_KEY)

            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            x = sw // 2 - RING_SIZE // 2
            y = sh // 2 - RING_SIZE // 2
            root.geometry(f"{RING_SIZE}x{RING_SIZE}+{x}+{y}")

            canvas = tk.Canvas(
                root, width=RING_SIZE, height=RING_SIZE,
                bg=TRANSPARENT_KEY, highlightthickness=0,
            )
            canvas.pack()

            start_time = time.time()

            def animate() -> None:
                elapsed = time.time() - start_time
                if elapsed > duration:
                    root.destroy()
                    return

                canvas.delete("all")
                cx = cy = RING_SIZE // 2

                # 3 expanding rings with phase offset
                for i in range(3):
                    phase = (elapsed * 0.8 + i * 0.33) % 1.0
                    radius = 20 + phase * 60
                    width = max(1, int((1 - phase) * 3))
                    canvas.create_oval(
                        cx - radius, cy - radius,
                        cx + radius, cy + radius,
                        outline=CYAN, width=width, fill="",
                    )

                # Center dot
                canvas.create_oval(
                    cx - 6, cy - 6, cx + 6, cy + 6,
                    fill=CYAN, outline="",
                )

                # "LISTENING" text below
                canvas.create_text(
                    cx, cy + 72, text="LISTENING",
                    font=("Consolas", 9), fill=CYAN,
                )

                root.after(33, animate)  # ~30 FPS

            root.after(0, animate)
            root.mainloop()

        except Exception as exc:
            logger.debug(f"Voice ring display error: {exc}")
