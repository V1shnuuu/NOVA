# 🤖 JARVIS WorkMode

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Windows 11](https://img.shields.io/badge/Windows-11-0078D6.svg)](https://www.microsoft.com/windows)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-V1shnuuu%2FNOVA-181717.svg)](https://github.com/V1shnuuu/NOVA)

An intelligent, automated desktop productivity assistant for **Windows 11** — inspired by JARVIS from Iron Man.

JARVIS detects when you arrive at your desk (via phone presence on WiFi or a keyboard shortcut), then automatically launches ChatGPT, Claude, and Spotify, and tiles every window into a clean productivity layout. It lives in the system tray, ships as a single `.exe`, and includes a first-run setup wizard.

![Demo](docs/demo.gif)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Phone Presence Detection** | ARP/ping/Bluetooth detection of your phone on WiFi |
| **Global Hotkey** | `CTRL+ALT+W` to manually activate |
| **Setup Wizard** | Dark-themed 5-page wizard — zero config file editing |
| **System Tray** | Colour-coded icon with full right-click menu |
| **Browser Launcher** | Opens ChatGPT & Claude in separate windows |
| **Spotify Integration** | Launches Spotify + starts playlist + sets volume |
| **Window Tiling** | 3-column auto-layout via pygetwindow + win32gui |
| **Cooldown** | Prevents repeated triggers (configurable) |
| **Auto-Updater** | Checks GitHub Releases for new versions |
| **Windows Startup** | Registers in startup via the registry |
| **Toast Notifications** | Native Windows 11 toasts on activation |
| **Watchdog** | Auto-restarts dead background threads |
| **Diagnostic Mode** | Dumps processes, windows, ARP table |
| **Single-File EXE** | PyInstaller build — no Python needed |
| **NSIS Installer** | Professional setup.exe with shortcuts + uninstaller |

---

## 🚀 Quick Start (3 Steps)

1. **Download** `JarvisWorkMode_Setup_v1.0.0.exe` from [Releases](https://github.com/V1shnuuu/NOVA/releases)
2. **Install** and launch — the setup wizard guides you through everything
3. **Done** — JARVIS monitors for your phone and activates your workspace automatically

---

## 🔧 Build from Source

### Prerequisites

- **Windows 11** (or 10)
- **Python 3.11+** — [python.org/downloads](https://www.python.org/downloads/)
- **Spotify Desktop** (optional) — [spotify.com/download](https://www.spotify.com/download)

### Setup

```powershell
git clone https://github.com/V1shnuuu/NOVA.git
cd NOVA

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# pywin32 post-install
python venv\Scripts\pywin32_postinstall.py -install
```

### Run

```powershell
# As Administrator (recommended for global hotkeys)
python main.py

# Or silent (no console):
pythonw.exe main.py
```

### Build EXE

```powershell
python build\build_exe.py
# Output: dist\JarvisWorkMode.exe
```

### Build Installer

Install [NSIS](https://nsis.sourceforge.io) first, then:

```powershell
python build\build_installer.py
# Output: build\JarvisWorkMode_Setup_v1.0.0.exe
```

---

## 🎵 Spotify Setup

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App** (free)
3. Set **Redirect URI** to `http://localhost:8888/callback`
4. Copy **Client ID** and **Client Secret** into the wizard or settings
5. To get a playlist URI: right-click a playlist in Spotify → **Share** → **Copy Spotify URI**

> On first run, a browser tab opens for OAuth. After authorizing, a `.spotify_cache` token file is saved in `%APPDATA%\JarvisWorkMode` and you won't be asked again.

---

## 📱 Finding Your Phone's Network Info

| Device | MAC Address |
|---|---|
| **Android** | Settings → About Phone → Status → Wi-Fi MAC Address |
| **iPhone** | Settings → Wi-Fi → tap ⓘ → Wi-Fi Address |

**IP Address**: Check your router's admin page (usually `192.168.1.1`) or run `arp -a` in PowerShell while your phone is connected.

---

## 🖥️ Window Layout

Default 3-column layout (customizable in Settings):

```
┌──────────────┬──────────────┬──────────────┐
│   ChatGPT    │    Claude    │   Spotify    │
│    (33%)     │    (34%)     │    (33%)     │
└──────────────┴──────────────┴──────────────┘
```

---

## ⌨️ Usage

| Action | How |
|---|---|
| Manual activate | `CTRL+ALT+W` or tray → "Activate Workspace Now" |
| Pause monitoring | Tray → "Pause Monitoring" |
| Open settings | Tray → "Settings" |
| View logs | Tray → "View Logs" (opens `%APPDATA%\JarvisWorkMode\logs`) |
| Exit | Tray → "Exit" |

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| Hotkey doesn't work | Run as Administrator |
| Phone not detected (ping) | Switch to ARP method in settings |
| Phone not detected (ARP) | Ensure phone is on same WiFi; try pinging it first |
| Spotify won't play | Verify Spotify is open + logged in; check API credentials |
| Windows not arranging | Enable diagnostic mode to see all window titles |
| Multiple monitors | Uses primary monitor; `monitor_index` config planned |
| "Already running" error | Kill existing `JarvisWorkMode.exe` in Task Manager |

---

## 📁 Project Structure

```
jarvis_workmode/
├── main.py                     # Orchestrator + entry point
├── config.py                   # JSON-persistent dataclass
├── app_state.py                # Thread-safe state machine
├── version.py                  # Version metadata
├── requirements.txt
├── ui/
│   ├── tray_icon.py            # pystray system tray
│   ├── wizard.py               # 5-page setup wizard
│   ├── settings_window.py      # Tabbed settings panel
│   └── notification.py         # Toast notifications
├── triggers/
│   ├── wifi_presence.py        # ARP/ping detection
│   ├── bluetooth_presence.py   # BLE detection (optional)
│   └── manual_trigger.py       # CTRL+ALT+W hotkey
├── automation/
│   ├── workspace_launcher.py   # Opens browsers + Spotify
│   ├── window_manager.py       # Window tiling engine
│   └── spotify_controller.py   # Spotify Web API
├── services/
│   ├── startup_manager.py      # Windows startup registry
│   ├── updater.py              # GitHub auto-update checker
│   └── watchdog.py             # Thread health monitor
├── build/
│   ├── build_exe.py            # PyInstaller script
│   ├── build_installer.py      # Full build pipeline
│   ├── jarvis_installer.nsi    # NSIS installer script
│   └── version_info.txt        # EXE metadata
└── tests/
    ├── test_config.py
    ├── test_wifi_detection.py
    └── test_window_manager.py
```

---

## 🧩 Future Extensions

- **System Tray Icon** with animated states
- **Voice Greeting** via `pyttsx3`
- **Deactivation Mode** — close apps when phone leaves WiFi
- **Web Dashboard** — Flask localhost status page
- **Multi-Profile** — different layouts for day/night
- **Camera Detection** — OpenCV face detection trigger
- **Dynamic Playlists** — pick by time of day
- **GitHub Auto-Pull** — pull latest code on activation

---

## 📄 License

MIT License — free to use, modify, and distribute.
