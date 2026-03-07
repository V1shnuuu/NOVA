"""
JARVIS WorkMode — First-Run Setup Wizard (v2)
5-page dark-themed Tkinter wizard: Welcome → Phone → Spotify → Preferences → Done.
"""

from __future__ import annotations

import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from config import Config
from utils.logger import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("jarvis.ui.wizard")

# ── Theme colours ────────────────────────────────────────────────────
BG_DARK = "#0d0d1a"
BG_CARD = "#1a1a2e"
BG_HOVER = "#16213e"
ACCENT = "#e94560"
ACCENT_GREEN = "#00ff88"
ACCENT_AMBER = "#ffaa00"
TEXT_PRIMARY = "#ffffff"
TEXT_MUTED = "#888888"
BORDER = "#2a2a4e"

WINDOW_W, WINDOW_H = 620, 500
FONT_HEADING = ("Segoe UI", 18, "bold")
FONT_SUBHEADING = ("Segoe UI", 12)
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)


class SetupWizard:
    """Multi-page first-run wizard. Blocks until the user finishes or cancels."""

    def __init__(self, config: Config, on_complete: callable) -> None:
        self.config = config
        self.on_complete = on_complete
        self._completed = False

        # ── Root window ──────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("JARVIS WorkMode — Setup")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)
        self._centre_window(WINDOW_W, WINDOW_H)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._apply_styles()

        # ── Progress bar ─────────────────────────────────────────────
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(
            self.root, variable=self.progress_var,
            maximum=100, length=WINDOW_W - 40,
            style="Accent.Horizontal.TProgressbar",
        )
        self.progress.pack(pady=(15, 0))

        # ── Page container ───────────────────────────────────────────
        self.container = tk.Frame(self.root, bg=BG_DARK)
        self.container.pack(fill="both", expand=True, padx=20, pady=10)

        # ── Pages ────────────────────────────────────────────────────
        self.pages: list[tk.Frame] = []
        self.current_page = 0
        self._build_pages()
        self._show_page(0)

    # ── Public ───────────────────────────────────────────────────────

    def run(self) -> bool:
        """Block until wizard finishes; returns ``True`` if completed."""
        self.root.mainloop()
        return self._completed

    # ── Style ────────────────────────────────────────────────────────

    def _apply_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG_DARK, foreground=TEXT_PRIMARY,
                         fieldbackground=BG_CARD, bordercolor=BORDER,
                         insertcolor=TEXT_PRIMARY)
        style.configure("TEntry", fieldbackground=BG_CARD,
                         foreground=TEXT_PRIMARY, padding=6)
        style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY)
        style.configure("Muted.TLabel", foreground=TEXT_MUTED)
        style.configure("Heading.TLabel", font=FONT_HEADING)
        style.configure("Sub.TLabel", font=FONT_SUBHEADING)
        style.configure("TButton", background=ACCENT, foreground=TEXT_PRIMARY,
                         padding=(16, 8), font=FONT_BODY)
        style.map("TButton",
                   background=[("active", "#c73e55"), ("disabled", "#555")])
        style.configure("Secondary.TButton", background=BG_CARD)
        style.map("Secondary.TButton",
                   background=[("active", BG_HOVER)])
        style.configure("TCheckbutton", background=BG_DARK,
                         foreground=TEXT_PRIMARY)
        style.configure("TRadiobutton", background=BG_DARK,
                         foreground=TEXT_PRIMARY)
        style.configure("Accent.Horizontal.TProgressbar",
                         troughcolor=BG_CARD, background=ACCENT)
        style.configure("TScale", background=BG_DARK, troughcolor=BG_CARD)

    def _centre_window(self, w: int, h: int) -> None:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── Page management ──────────────────────────────────────────────

    def _build_pages(self) -> None:
        self.pages = [
            self._page_welcome(),
            self._page_phone(),
            self._page_spotify(),
            self._page_preferences(),
            self._page_done(),
        ]

    def _show_page(self, index: int) -> None:
        for p in self.pages:
            p.pack_forget()
        self.pages[index].pack(fill="both", expand=True)
        self.current_page = index
        self.progress_var.set((index / (len(self.pages) - 1)) * 100)

    def _next(self) -> None:
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)

    def _back(self) -> None:
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    # ── Navigation buttons helper ────────────────────────────────────

    def _nav_frame(
        self,
        parent: tk.Frame,
        show_back: bool = True,
        next_text: str = "Next →",
        next_cmd: callable | None = None,
    ) -> tk.Frame:
        f = tk.Frame(parent, bg=BG_DARK)
        f.pack(side="bottom", fill="x", pady=(10, 0))
        if show_back:
            ttk.Button(
                f, text="← Back", command=self._back,
                style="Secondary.TButton",
            ).pack(side="left")
        ttk.Button(
            f, text=next_text, command=next_cmd or self._next,
        ).pack(side="right")
        return f

    # ── PAGE 1: Welcome ──────────────────────────────────────────────

    def _page_welcome(self) -> tk.Frame:
        page = tk.Frame(self.container, bg=BG_DARK)

        ttk.Label(
            page, text="🤖", font=("Segoe UI Emoji", 48),
            style="Heading.TLabel",
        ).pack(pady=(20, 5))
        ttk.Label(
            page, text="JARVIS WorkMode", style="Heading.TLabel",
        ).pack()
        ttk.Label(
            page,
            text="Your intelligent workspace assistant for Windows 11",
            style="Sub.TLabel",
        ).pack(pady=(5, 20))

        info = (
            "JARVIS detects when you arrive at your desk and\n"
            "automatically opens ChatGPT, Claude, and Spotify —\n"
            "arranging everything into a clean workspace layout.\n\n"
            "Let's get you set up in 2 minutes."
        )
        ttk.Label(page, text=info, font=FONT_BODY,
                   justify="center").pack(pady=10)

        self._nav_frame(page, show_back=False, next_text="Let's Go →")
        return page

    # ── PAGE 2: Phone Detection ──────────────────────────────────────

    def _page_phone(self) -> tk.Frame:
        page = tk.Frame(self.container, bg=BG_DARK)

        ttk.Label(page, text="📱 Detect Your Phone",
                   style="Heading.TLabel").pack(anchor="w")
        ttk.Label(
            page,
            text="JARVIS watches for your phone on WiFi to know you're here.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 12))

        # Method selection
        self._method_var = tk.StringVar(value=self.config.detection_method)
        methods_f = tk.Frame(page, bg=BG_DARK)
        methods_f.pack(anchor="w", pady=(0, 10))
        ttk.Radiobutton(methods_f, text="WiFi / ARP (recommended)",
                         variable=self._method_var,
                         value="arp").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(methods_f, text="Ping",
                         variable=self._method_var,
                         value="ping").pack(side="left", padx=(0, 20))
        ttk.Radiobutton(methods_f, text="Bluetooth (optional)",
                         variable=self._method_var,
                         value="bluetooth").pack(side="left")

        # IP
        ttk.Label(page, text="Phone IP Address", font=FONT_BODY).pack(
            anchor="w", pady=(8, 2))
        self._ip_var = tk.StringVar(value=self.config.phone_ip)
        ttk.Entry(page, textvariable=self._ip_var, width=30).pack(
            anchor="w")
        ttk.Label(
            page,
            text="Find this in your router's device list or phone WiFi settings",
            style="Muted.TLabel", font=FONT_SMALL,
        ).pack(anchor="w")

        # MAC
        ttk.Label(page, text="Phone MAC Address", font=FONT_BODY).pack(
            anchor="w", pady=(10, 2))
        self._mac_var = tk.StringVar(value=self.config.phone_mac)
        ttk.Entry(page, textvariable=self._mac_var, width=30).pack(
            anchor="w")
        ttk.Label(
            page,
            text="Android: Settings → About → WiFi MAC  |  "
                 "iPhone: Settings → Wi-Fi → ⓘ",
            style="Muted.TLabel", font=FONT_SMALL,
        ).pack(anchor="w")

        # Test button + result
        test_f = tk.Frame(page, bg=BG_DARK)
        test_f.pack(anchor="w", pady=(14, 0))
        self._test_label = ttk.Label(test_f, text="", font=FONT_BODY)
        ttk.Button(
            test_f, text="🔍 Test Connection",
            command=self._test_connection, style="Secondary.TButton",
        ).pack(side="left")
        self._test_label.pack(side="left", padx=12)

        def _save_phone() -> None:
            self.config.phone_ip = self._ip_var.get().strip()
            self.config.phone_mac = self._mac_var.get().strip()
            self.config.detection_method = self._method_var.get()
            self._next()

        self._nav_frame(page, next_cmd=_save_phone)
        return page

    def _test_connection(self) -> None:
        self._test_label.configure(text="⏳ Testing…", foreground=ACCENT_AMBER)

        def _run() -> None:
            ip = self._ip_var.get().strip()
            mac = self._mac_var.get().strip()
            method = self._method_var.get()
            ok = False
            try:
                if method == "ping" and ip:
                    r = subprocess.run(
                        ["ping", "-n", "1", "-w", "1000", ip],
                        capture_output=True, text=True, timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    ok = "TTL=" in r.stdout.upper()
                elif mac:
                    normalised = mac.lower().replace(":", "-")
                    r = subprocess.run(
                        ["arp", "-a"], capture_output=True, text=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                    ok = normalised in r.stdout.lower()
            except Exception:
                ok = False

            if ok:
                self._test_label.configure(
                    text="✅ Device found!", foreground=ACCENT_GREEN)
            else:
                self._test_label.configure(
                    text="❌ Not found — check IP/MAC", foreground=ACCENT)

        threading.Thread(target=_run, daemon=True).start()

    # ── PAGE 3: Spotify ──────────────────────────────────────────────

    def _page_spotify(self) -> tk.Frame:
        page = tk.Frame(self.container, bg=BG_DARK)

        ttk.Label(page, text="🎵 Spotify Integration",
                   style="Heading.TLabel").pack(anchor="w")
        ttk.Label(page, text="Optional — control Spotify playback on activation.",
                   style="Muted.TLabel").pack(anchor="w", pady=(2, 12))

        self._spotify_var = tk.BooleanVar(value=self.config.spotify_enabled)
        ttk.Checkbutton(page, text="Enable Spotify control",
                         variable=self._spotify_var).pack(anchor="w")

        ttk.Label(page, text="Client ID", font=FONT_BODY).pack(
            anchor="w", pady=(10, 2))
        self._sp_id_var = tk.StringVar(value=self.config.spotify_client_id)
        ttk.Entry(page, textvariable=self._sp_id_var, width=45).pack(anchor="w")
        ttk.Label(
            page,
            text="Get yours free at developer.spotify.com/dashboard →",
            style="Muted.TLabel", font=FONT_SMALL,
        ).pack(anchor="w")

        ttk.Label(page, text="Client Secret", font=FONT_BODY).pack(
            anchor="w", pady=(8, 2))
        self._sp_secret_var = tk.StringVar(
            value=self.config.spotify_client_secret)
        ttk.Entry(page, textvariable=self._sp_secret_var,
                   width=45, show="•").pack(anchor="w")

        ttk.Label(page, text="Playlist URI", font=FONT_BODY).pack(
            anchor="w", pady=(8, 2))
        self._sp_playlist_var = tk.StringVar(
            value=self.config.spotify_playlist_uri)
        ttk.Entry(page, textvariable=self._sp_playlist_var,
                   width=45).pack(anchor="w")
        ttk.Label(
            page,
            text="Right-click playlist → Share → Copy Spotify URI",
            style="Muted.TLabel", font=FONT_SMALL,
        ).pack(anchor="w")

        # Volume slider
        vol_f = tk.Frame(page, bg=BG_DARK)
        vol_f.pack(anchor="w", pady=(10, 0), fill="x")
        ttk.Label(vol_f, text="Volume:", font=FONT_BODY).pack(side="left")
        self._vol_var = tk.IntVar(value=self.config.spotify_volume)
        ttk.Scale(vol_f, from_=0, to=100, variable=self._vol_var,
                   orient="horizontal", length=200).pack(
            side="left", padx=8)
        self._vol_label = ttk.Label(vol_f, text=f"{self._vol_var.get()}%",
                                     font=FONT_BODY)
        self._vol_label.pack(side="left")
        self._vol_var.trace_add(
            "write",
            lambda *_: self._vol_label.configure(
                text=f"{int(self._vol_var.get())}%"),
        )

        def _save_spotify() -> None:
            self.config.spotify_enabled = self._spotify_var.get()
            self.config.spotify_client_id = self._sp_id_var.get().strip()
            self.config.spotify_client_secret = self._sp_secret_var.get().strip()
            self.config.spotify_playlist_uri = self._sp_playlist_var.get().strip()
            self.config.spotify_volume = int(self._vol_var.get())
            self._next()

        nav = self._nav_frame(page, next_cmd=_save_spotify)
        ttk.Button(
            nav, text="Skip Spotify →", command=self._next,
            style="Secondary.TButton",
        ).pack(side="right", padx=(0, 8))
        return page

    # ── PAGE 4: Preferences ──────────────────────────────────────────

    def _page_preferences(self) -> tk.Frame:
        page = tk.Frame(self.container, bg=BG_DARK)

        ttk.Label(page, text="⚙️ Preferences",
                   style="Heading.TLabel").pack(anchor="w")
        ttk.Label(page, text="Fine-tune how JARVIS behaves.",
                   style="Muted.TLabel").pack(anchor="w", pady=(2, 16))

        self._startup_var = tk.BooleanVar(
            value=self.config.launch_on_startup)
        ttk.Checkbutton(
            page, text="Launch JARVIS WorkMode when Windows starts",
            variable=self._startup_var,
        ).pack(anchor="w", pady=3)

        self._notif_var = tk.BooleanVar(
            value=self.config.show_activation_notifications)
        ttk.Checkbutton(
            page, text="Show notification when workspace activates",
            variable=self._notif_var,
        ).pack(anchor="w", pady=3)

        # Hotkey
        hk_f = tk.Frame(page, bg=BG_DARK)
        hk_f.pack(anchor="w", pady=(14, 0))
        ttk.Label(hk_f, text="Manual hotkey:", font=FONT_BODY).pack(
            side="left")
        self._hk_var = tk.StringVar(value=self.config.hotkey)
        ttk.Entry(hk_f, textvariable=self._hk_var, width=18).pack(
            side="left", padx=8)

        # Cooldown
        cd_f = tk.Frame(page, bg=BG_DARK)
        cd_f.pack(anchor="w", pady=(10, 0))
        ttk.Label(cd_f, text="Cooldown between activations (minutes):",
                   font=FONT_BODY).pack(side="left")
        self._cd_var = tk.IntVar(
            value=self.config.activation_cooldown_minutes)
        ttk.Spinbox(cd_f, from_=1, to=60, textvariable=self._cd_var,
                      width=5).pack(side="left", padx=8)

        def _save_prefs() -> None:
            self.config.launch_on_startup = self._startup_var.get()
            self.config.show_activation_notifications = self._notif_var.get()
            self.config.hotkey = self._hk_var.get().strip()
            self.config.activation_cooldown_minutes = int(self._cd_var.get())
            self._next()

        self._nav_frame(page, next_cmd=_save_prefs)
        return page

    # ── PAGE 5: Done ─────────────────────────────────────────────────

    def _page_done(self) -> tk.Frame:
        page = tk.Frame(self.container, bg=BG_DARK)

        ttk.Label(page, text="✅", font=("Segoe UI Emoji", 40),
                   style="Heading.TLabel").pack(pady=(20, 5))
        ttk.Label(page, text="JARVIS WorkMode is Ready!",
                   style="Heading.TLabel").pack()

        summary = (
            f"Detection: {self.config.detection_method.upper()}\n"
            f"Phone IP: {self.config.phone_ip or '(not set)'}\n"
            f"Hotkey: {self.config.hotkey}\n"
            f"Spotify: {'Enabled' if self.config.spotify_enabled else 'Disabled'}\n"
            f"Start with Windows: "
            f"{'Yes' if self.config.launch_on_startup else 'No'}"
        )
        ttk.Label(page, text=summary, font=FONT_MONO,
                   justify="left", background=BG_CARD,
                   padding=12).pack(pady=15, fill="x")

        ttk.Label(
            page,
            text="JARVIS will now watch for your phone on WiFi\n"
                 "and activate your workspace automatically.",
            font=FONT_BODY, justify="center",
        ).pack(pady=(0, 10))

        self._test_activate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            page, text="Activate workspace now to test it",
            variable=self._test_activate_var,
        ).pack(anchor="w")

        self._nav_frame(
            page, show_back=True, next_text="🚀 Finish",
            next_cmd=self._finish,
        )
        return page

    # ── Finish / Close ───────────────────────────────────────────────

    def _finish(self) -> None:
        self.config.first_run = False
        self.config.setup_complete = True
        self.config.save()
        self._completed = True
        logger.info("Setup wizard completed successfully.")

        if self._test_activate_var.get():
            self.on_complete()

        self.root.destroy()

    def _on_close(self) -> None:
        self.config.save()
        self.root.destroy()
