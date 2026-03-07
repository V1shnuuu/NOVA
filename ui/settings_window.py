"""
JARVIS WorkMode — Settings Window (v2)
Tabbed Tkinter settings panel — re-openable from the system tray.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from config import Config
from version import __version__, __app_name__, __github_repo__
from utils.logger import get_logger

logger = get_logger("jarvis.ui.settings")

# ── Theme (matches wizard) ───────────────────────────────────────────
BG_DARK = "#0d0d1a"
BG_CARD = "#1a1a2e"
ACCENT = "#e94560"
TEXT_PRIMARY = "#ffffff"
TEXT_MUTED = "#888888"
BORDER = "#2a2a4e"
FONT_HEADING = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)

_INSTANCE: SettingsWindow | None = None


class SettingsWindow:
    """Singleton tabbed settings panel."""

    def __init__(self, config: Config, on_save: callable) -> None:
        self.config = config
        self.on_save = on_save
        self.root: tk.Toplevel | None = None

    def open(self) -> None:
        """Create or raise the settings window."""
        global _INSTANCE  # noqa: PLW0603
        if _INSTANCE and _INSTANCE.root and _INSTANCE.root.winfo_exists():
            _INSTANCE.root.lift()
            return
        _INSTANCE = self
        self._build()

    # ── Build ────────────────────────────────────────────────────────

    def _build(self) -> None:
        self.root = tk.Tk()
        self.root.title("JARVIS WorkMode — Settings")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)
        self._centre(640, 480)
        self._apply_styles()

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        nb.add(self._tab_detection(), text=" 📡 Detection ")
        nb.add(self._tab_apps(), text=" 🌐 Apps ")
        nb.add(self._tab_spotify(), text=" 🎵 Spotify ")
        nb.add(self._tab_layout(), text=" 🖥 Layout ")
        nb.add(self._tab_system(), text=" ⚙️ System ")
        nb.add(self._tab_about(), text=" ℹ️ About ")

        btn_f = tk.Frame(self.root, bg=BG_DARK)
        btn_f.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_f, text="Cancel", command=self.root.destroy,
                    style="Secondary.TButton").pack(side="right")
        ttk.Button(btn_f, text="Save & Close",
                    command=self._save_and_close).pack(side="right", padx=8)

        self.root.mainloop()

    def _apply_styles(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BG_DARK, foreground=TEXT_PRIMARY,
                         fieldbackground=BG_CARD, bordercolor=BORDER,
                         insertcolor=TEXT_PRIMARY)
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_CARD,
                         foreground=TEXT_PRIMARY, padding=(12, 6))
        style.map("TNotebook.Tab",
                   background=[("selected", ACCENT)])
        style.configure("TEntry", fieldbackground=BG_CARD,
                         foreground=TEXT_PRIMARY, padding=5)
        style.configure("TLabel", background=BG_DARK, foreground=TEXT_PRIMARY)
        style.configure("Card.TLabel", background=BG_CARD)
        style.configure("Muted.TLabel", foreground=TEXT_MUTED)
        style.configure("TButton", background=ACCENT, foreground=TEXT_PRIMARY,
                         padding=(14, 6))
        style.map("TButton", background=[("active", "#c73e55")])
        style.configure("Secondary.TButton", background=BG_CARD)
        style.configure("TCheckbutton", background=BG_DARK,
                         foreground=TEXT_PRIMARY)
        style.configure("TScale", background=BG_DARK, troughcolor=BG_CARD)

    def _centre(self, w: int, h: int) -> None:
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Helper ───────────────────────────────────────────────────────

    @staticmethod
    def _labelled_entry(
        parent: tk.Widget, label: str, var: tk.StringVar,
        hint: str = "", show: str = "",
    ) -> None:
        ttk.Label(parent, text=label, font=FONT_BODY).pack(
            anchor="w", pady=(8, 2))
        kw: dict = {"textvariable": var, "width": 40}
        if show:
            kw["show"] = show
        ttk.Entry(parent, **kw).pack(anchor="w")
        if hint:
            ttk.Label(parent, text=hint, style="Muted.TLabel",
                       font=FONT_SMALL).pack(anchor="w")

    # ── Tabs ─────────────────────────────────────────────────────────

    def _tab_detection(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="Phone Detection", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        self._ip_v = tk.StringVar(value=self.config.phone_ip)
        self._labelled_entry(tab, "Phone IP", self._ip_v)
        self._mac_v = tk.StringVar(value=self.config.phone_mac)
        self._labelled_entry(tab, "Phone MAC", self._mac_v)
        self._method_v = tk.StringVar(value=self.config.detection_method)
        f = tk.Frame(tab, bg=BG_DARK)
        f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Method:", font=FONT_BODY).pack(side="left")
        for val, lbl in [("arp", "ARP"), ("ping", "Ping"),
                          ("bluetooth", "Bluetooth")]:
            ttk.Radiobutton(f, text=lbl, variable=self._method_v,
                             value=val).pack(side="left", padx=6)
        self._interval_v = tk.IntVar(value=self.config.scan_interval_seconds)
        f2 = tk.Frame(tab, bg=BG_DARK)
        f2.pack(anchor="w", pady=4)
        ttk.Label(f2, text="Scan interval (seconds):",
                   font=FONT_BODY).pack(side="left")
        ttk.Spinbox(f2, from_=5, to=120, textvariable=self._interval_v,
                      width=5).pack(side="left", padx=6)
        return tab

    def _tab_apps(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="Applications", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        self._chatgpt_v = tk.StringVar(value=self.config.chatgpt_url)
        self._labelled_entry(tab, "ChatGPT URL", self._chatgpt_v)
        self._claude_v = tk.StringVar(value=self.config.claude_url)
        self._labelled_entry(tab, "Claude URL", self._claude_v)
        self._browser_v = tk.StringVar(value=self.config.browser_executable)
        self._labelled_entry(tab, "Browser executable (blank = default)",
                              self._browser_v)
        self._spotify_exe_v = tk.StringVar(
            value=self.config.spotify_executable)
        self._labelled_entry(tab, "Spotify executable (blank = auto-detect)",
                              self._spotify_exe_v)
        return tab

    def _tab_spotify(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="Spotify", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        self._sp_en_v = tk.BooleanVar(value=self.config.spotify_enabled)
        ttk.Checkbutton(tab, text="Enable Spotify control",
                         variable=self._sp_en_v).pack(anchor="w")
        self._sp_id_v = tk.StringVar(value=self.config.spotify_client_id)
        self._labelled_entry(tab, "Client ID", self._sp_id_v)
        self._sp_sec_v = tk.StringVar(value=self.config.spotify_client_secret)
        self._labelled_entry(tab, "Client Secret", self._sp_sec_v, show="•")
        self._sp_pl_v = tk.StringVar(value=self.config.spotify_playlist_uri)
        self._labelled_entry(tab, "Playlist URI", self._sp_pl_v)
        vol_f = tk.Frame(tab, bg=BG_DARK)
        vol_f.pack(anchor="w", pady=8)
        ttk.Label(vol_f, text="Volume:", font=FONT_BODY).pack(side="left")
        self._sp_vol_v = tk.IntVar(value=self.config.spotify_volume)
        ttk.Scale(vol_f, from_=0, to=100, variable=self._sp_vol_v,
                   orient="horizontal", length=180).pack(side="left", padx=8)
        return tab

    def _tab_layout(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="Window Layout", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        ttk.Label(
            tab,
            text="Values are fractions of screen (0.0 – 1.0).",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 8))

        self._layout_vars: dict[str, dict[str, tk.StringVar]] = {}
        for app_name in ("chatgpt", "claude", "spotify"):
            f = tk.LabelFrame(
                tab, text=f"  {app_name.title()}  ", bg=BG_CARD,
                fg=TEXT_PRIMARY, font=FONT_BODY,
            )
            f.pack(fill="x", pady=4)
            current = self.config.layout.get(
                app_name, {"x": 0, "y": 0, "w": 0.33, "h": 1.0})
            vars_: dict[str, tk.StringVar] = {}
            row = tk.Frame(f, bg=BG_CARD)
            row.pack(fill="x", padx=8, pady=4)
            for key in ("x", "y", "w", "h"):
                ttk.Label(row, text=f"{key}:", style="Card.TLabel",
                           font=FONT_SMALL).pack(side="left")
                v = tk.StringVar(value=str(current.get(key, 0)))
                ttk.Entry(row, textvariable=v, width=6).pack(
                    side="left", padx=(0, 10))
                vars_[key] = v
            self._layout_vars[app_name] = vars_
        return tab

    def _tab_system(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="System", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        self._startup_v = tk.BooleanVar(value=self.config.launch_on_startup)
        ttk.Checkbutton(tab, text="Launch on Windows startup",
                         variable=self._startup_v).pack(anchor="w", pady=3)
        self._notif_v = tk.BooleanVar(
            value=self.config.show_activation_notifications)
        ttk.Checkbutton(tab, text="Show activation notifications",
                         variable=self._notif_v).pack(anchor="w", pady=3)
        self._diag_v = tk.BooleanVar(value=self.config.diagnostic_mode)
        ttk.Checkbutton(tab, text="Diagnostic mode (verbose logging)",
                         variable=self._diag_v).pack(anchor="w", pady=3)
        f = tk.Frame(tab, bg=BG_DARK)
        f.pack(anchor="w", pady=8)
        ttk.Label(f, text="Hotkey:", font=FONT_BODY).pack(side="left")
        self._hk_v = tk.StringVar(value=self.config.hotkey)
        ttk.Entry(f, textvariable=self._hk_v, width=18).pack(
            side="left", padx=8)
        f2 = tk.Frame(tab, bg=BG_DARK)
        f2.pack(anchor="w", pady=4)
        ttk.Label(f2, text="Cooldown (minutes):",
                   font=FONT_BODY).pack(side="left")
        self._cd_v = tk.IntVar(
            value=self.config.activation_cooldown_minutes)
        ttk.Spinbox(f2, from_=1, to=60, textvariable=self._cd_v,
                      width=5).pack(side="left", padx=6)
        return tab

    def _tab_about(self) -> tk.Frame:
        tab = tk.Frame(bg=BG_DARK)
        ttk.Label(tab, text="About", font=FONT_HEADING).pack(
            anchor="w", pady=(10, 6))
        info = (
            f"{__app_name__}  v{__version__}\n\n"
            f"GitHub: github.com/{__github_repo__}\n\n"
            "An intelligent workspace assistant for Windows 11.\n"
            "100% free and open-source."
        )
        ttk.Label(tab, text=info, font=FONT_BODY, justify="left").pack(
            anchor="w", pady=10)
        return tab

    # ── Save ─────────────────────────────────────────────────────────

    def _save_and_close(self) -> None:
        self.config.phone_ip = self._ip_v.get().strip()
        self.config.phone_mac = self._mac_v.get().strip()
        self.config.detection_method = self._method_v.get()
        self.config.scan_interval_seconds = int(self._interval_v.get())
        self.config.chatgpt_url = self._chatgpt_v.get().strip()
        self.config.claude_url = self._claude_v.get().strip()
        self.config.browser_executable = self._browser_v.get().strip()
        self.config.spotify_executable = self._spotify_exe_v.get().strip()
        self.config.spotify_enabled = self._sp_en_v.get()
        self.config.spotify_client_id = self._sp_id_v.get().strip()
        self.config.spotify_client_secret = self._sp_sec_v.get().strip()
        self.config.spotify_playlist_uri = self._sp_pl_v.get().strip()
        self.config.spotify_volume = int(self._sp_vol_v.get())
        self.config.launch_on_startup = self._startup_v.get()
        self.config.show_activation_notifications = self._notif_v.get()
        self.config.diagnostic_mode = self._diag_v.get()
        self.config.hotkey = self._hk_v.get().strip()
        self.config.activation_cooldown_minutes = int(self._cd_v.get())

        # Layout
        for app_name, vars_ in self._layout_vars.items():
            self.config.layout[app_name] = {
                k: float(v.get()) for k, v in vars_.items()
            }

        self.config.save()
        logger.info("Settings saved via settings window.")
        self.on_save()
        self.root.destroy()
