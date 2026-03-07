"""
JARVIS WorkMode v3 — Main HUD Overlay Window
Transparent, always-on-top tkinter Canvas with:
  - Hexagonal grid background
  - Sweeping scan line animation (20 FPS)
  - Corner bracket decorations
  - Clock, mode, presence status
  - Typewriter text reveal for speech lines
  - Draggable via click-and-drag
"""

from __future__ import annotations

import math
import time
import tkinter as tk
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("jarvis.hud.window")

# ── Design tokens ────────────────────────────────────────────────────
TRANSPARENT_KEY = "#000001"
CYAN           = "#00d4ff"
CYAN_DIM       = "#0a4f6e"
CYAN_GRID      = "#0a2a3a"
ICE_WHITE      = "#e0f7ff"
SUCCESS        = "#00ff9d"
DANGER         = "#ff3c3c"
PANEL_BG       = "#040d12"

FONT_TITLE = ("Segoe UI", 11, "bold")
FONT_CLOCK = ("Segoe UI", 22, "bold")
FONT_MONO  = ("Consolas", 10)
FONT_SMALL = ("Consolas", 9)

# Try loading custom fonts if available — fall back gracefully
try:
    import ctypes
    _fonts_dir = __import__("pathlib").Path(__file__).parent / "assets" / "fonts"
    for _ttf in _fonts_dir.glob("*.ttf"):
        ctypes.windll.gdi32.AddFontResourceW(str(_ttf))
    FONT_TITLE = ("Orbitron", 11, "bold")
    FONT_CLOCK = ("Orbitron", 22, "bold")
    FONT_MONO  = ("Share Tech Mono", 10)
    FONT_SMALL = ("Share Tech Mono", 9)
except Exception:
    pass  # System fonts used as fallback


class HUDWindow:
    """Transparent always-on-top overlay — the JARVIS visual centerpiece."""

    def __init__(self, config, app_state) -> None:
        self.config = config
        self.state = app_state

        self.root: tk.Tk | None = None
        self.canvas: tk.Canvas | None = None

        self._hud_w = config.hud_width
        self._hud_h = config.hud_height

        # Animation state
        self._scan_y = 0
        self._scan_dir = 1
        self._last_speech = "JARVIS WORKMODE v3.0 — STANDING BY"
        self._boot_chars = 0
        self._drag_x = 0
        self._drag_y = 0

    # ── Setup ────────────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        self.root.attributes("-alpha", self.config.hud_opacity)
        self.root.configure(bg=TRANSPARENT_KEY)

        # Position: bottom-right above taskbar
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - self._hud_w - 20
        y = sh - self._hud_h - 60
        self.root.geometry(f"{self._hud_w}x{self._hud_h}+{x}+{y}")

        # Draggable
        self.root.bind("<Button-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_motion)

    def _setup_canvas(self) -> None:
        self.canvas = tk.Canvas(
            self.root,
            width=self._hud_w,
            height=self._hud_h,
            bg=TRANSPARENT_KEY,
            highlightthickness=0,
        )
        self.canvas.pack()

    # ── Drawing ──────────────────────────────────────────────────────

    def _draw_frame(self) -> None:
        c = self.canvas
        W, H = self._hud_w, self._hud_h
        c.delete("all")

        # Background panel
        c.create_rectangle(0, 0, W, H, fill=PANEL_BG, outline="")

        # Hexagonal grid
        self._draw_hex_grid(c, W, H)

        # Scan line
        c.create_line(0, self._scan_y, W, self._scan_y, fill=CYAN, width=1)
        for offset in (1, 2, 3):
            c.create_line(
                0, self._scan_y - offset, W, self._scan_y - offset,
                fill="#001f2e", width=1,
            )
            c.create_line(
                0, self._scan_y + offset, W, self._scan_y + offset,
                fill="#001f2e", width=1,
            )

        # Corner brackets
        self._draw_corner_brackets(c, W, H)

        # Top label
        c.create_text(14, 14, text="J.A.R.V.I.S", anchor="nw",
                       fill=CYAN, font=FONT_TITLE)

        # Mode badge
        mode_text = self.state.current_mode_name.upper()
        c.create_text(W - 14, 14, text=f"[ {mode_text} ]",
                       anchor="ne", fill=CYAN_DIM, font=FONT_MONO)

        # Divider
        c.create_line(14, 34, W - 14, 34, fill=CYAN_DIM, width=1)

        # Clock
        now = datetime.now()
        c.create_text(14, 46, text=now.strftime("%H:%M:%S"),
                       anchor="nw", fill=ICE_WHITE, font=FONT_CLOCK)
        c.create_text(14, 76, text=now.strftime("%A  %d %b %Y"),
                       anchor="nw", fill=CYAN_DIM, font=FONT_MONO)

        # Presence
        if self.state.phone_present:
            pres_color, pres_text = SUCCESS, "● PRESENT"
        else:
            pres_color, pres_text = DANGER, "○ ABSENT"
        c.create_text(14, 100, text=f"PRESENCE   {pres_text}",
                       anchor="nw", fill=pres_color, font=FONT_MONO)

        # System state
        c.create_text(14, 118, text=f"STATUS     {self.state.state.name}",
                       anchor="nw", fill=CYAN_DIM, font=FONT_MONO)

        # Divider
        c.create_line(14, 142, W - 14, 142, fill=CYAN_DIM, width=1)

        # Last speech (typewriter)
        displayed = self._last_speech[: self._boot_chars]
        c.create_text(14, 154, text=f"> {displayed}_",
                       anchor="nw", fill=CYAN, font=FONT_MONO,
                       width=W - 28)

        # Bottom bar
        if self.state.is_listening:
            self._draw_listening_dots(c, W, H)
        else:
            c.create_text(W // 2, H - 14,
                           text='SAY  "JARVIS"  TO  ACTIVATE',
                           anchor="center", fill=CYAN_DIM, font=FONT_SMALL)

    def _draw_hex_grid(self, c: tk.Canvas, W: int, H: int) -> None:
        hex_size = 20
        col_w = hex_size * 1.732
        row_h = hex_size * 1.5
        for row in range(int(H / row_h) + 2):
            for col in range(int(W / col_w) + 2):
                cx = col * col_w + (hex_size * 0.866 if row % 2 else 0)
                cy = row * row_h
                points: list[float] = []
                for i in range(6):
                    angle = math.radians(60 * i - 30)
                    points.extend([
                        cx + hex_size * math.cos(angle),
                        cy + hex_size * math.sin(angle),
                    ])
                c.create_polygon(points, outline=CYAN_GRID, fill="", width=1)

    def _draw_corner_brackets(
        self, c: tk.Canvas, W: int, H: int,
    ) -> None:
        size, pad, w = 14, 4, 2
        col = CYAN
        # Top-left
        c.create_line(pad, pad + size, pad, pad, pad + size, pad,
                       fill=col, width=w)
        # Top-right
        c.create_line(W - pad, pad + size, W - pad, pad,
                       W - pad - size, pad, fill=col, width=w)
        # Bottom-left
        c.create_line(pad, H - pad - size, pad, H - pad,
                       pad + size, H - pad, fill=col, width=w)
        # Bottom-right
        c.create_line(W - pad, H - pad - size, W - pad, H - pad,
                       W - pad - size, H - pad, fill=col, width=w)

    def _draw_listening_dots(
        self, c: tk.Canvas, W: int, H: int,
    ) -> None:
        t = time.time()
        for i, dot_x in enumerate([W // 2 - 20, W // 2, W // 2 + 20]):
            phase = math.sin(t * 4 + i * 1.2)
            brightness = int(((phase + 1) / 2) * 200 + 55)
            color = f"#{brightness:02x}{brightness:02x}ff"
            r = 3 + int(phase * 2)
            c.create_oval(
                dot_x - r, H - 20 - r, dot_x + r, H - 20 + r,
                fill=color, outline="",
            )

    # ── Animation loop ───────────────────────────────────────────────

    def _advance_scan_line(self) -> None:
        self._scan_y += 2 * self._scan_dir
        if self._scan_y >= self._hud_h:
            self._scan_dir = -1
        elif self._scan_y <= 0:
            self._scan_dir = 1

    def _animation_loop(self) -> None:
        if self.root is None:
            return
        self._advance_scan_line()
        if self._boot_chars < len(self._last_speech):
            self._boot_chars += 1
        self._draw_frame()
        self.root.after(50, self._animation_loop)  # 20 FPS

    # ── Public API ───────────────────────────────────────────────────

    def set_speech_text(self, text: str) -> None:
        """Set the typewriter text on the HUD. Restarts animation."""
        self._last_speech = text
        self._boot_chars = 0

    # ── Drag ─────────────────────────────────────────────────────────

    def _on_drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag_motion(self, event: tk.Event) -> None:
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    # ── Run ──────────────────────────────────────────────────────────

    def run(self) -> None:
        """Blocking — creates the window and enters the Tk event loop."""
        self._setup_window()
        self._setup_canvas()
        self.root.after(100, self._animation_loop)
        logger.info("HUD overlay visible.")
        self.root.mainloop()

    def destroy(self) -> None:
        if self.root:
            self.root.destroy()
