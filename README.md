# 🤖 JARVIS WorkMode v3 — Voice-First HUD System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Windows 11](https://img.shields.io/badge/Windows-11-0078D6.svg)](https://www.microsoft.com/windows)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-V1shnuuu%2FNOVA-181717.svg)](https://github.com/V1shnuuu/NOVA)

A **voice-driven, AI-style desktop intelligence system** for Windows 11 — inspired by JARVIS from Iron Man.

Not a tray icon app. Not a background script. A **living HUD overlay** that hovers above your desktop, listens for your voice, speaks back, and auto-manages your workspace.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎤 **Voice Control** | Say "JARVIS" → hear a chime → give commands (offline via vosk) |
| 🖥️ **HUD Overlay** | Transparent always-on-top panel with hex grid, scan line, clock |
| 🎬 **Briefing Cinematic** | Full-screen activation animation with mode name + app list |
| ⏰ **Time-Based Modes** | Deep Work (morning) ∙ Afternoon (research) ∙ Evening (creative) |
| 📱 **Phone Detection** | ARP/ping WiFi scanner triggers workspace automatically |
| 👋 **Auto-Deactivation** | Detects departure → speaks farewell → closes apps |
| 🔊 **JARVIS Voice** | pyttsx3 offline TTS with JARVIS personality |
| 🎵 **Spotify** | Auto-plays playlists per mode, sets volume |
| ⌨️ **Hotkey** | CTRL+ALT+W as fallback trigger |
| 🪟 **Window Tiling** | Arranges apps per mode layout via pygetwindow + win32gui |
| 📦 **Single-File EXE** | PyInstaller build with all assets bundled |

---

## 🗣️ Voice Commands

| Say | Action |
|---|---|
| "JARVIS" | Wake word — activates listening |
| "Activate" / "Start" | Launch workspace |
| "Deactivate" / "Shut down" | Close workspace |
| "Pause" | Pause monitoring |
| "Resume" | Resume monitoring |
| "Status" / "Report" | Speak current system state |
| "Spotify" / "Music" | Open Spotify |
| "Close all" | Close all workspace apps |

---

## ⏰ Workspace Modes

| Mode | Time | Layout |
|---|---|---|
| **Deep Work** | 05:00 – 11:59 | Claude 60% ∙ ChatGPT 40% ∙ Spotify minimized |
| **Afternoon** | 12:00 – 17:59 | ChatGPT ∙ Claude ∙ Spotify (3 equal columns) |
| **Evening** | 18:00 – 04:59 | Claude 70% ∙ Spotify 30% ∙ no ChatGPT |

---

## 🚀 Quick Start

### From Source

```powershell
git clone https://github.com/V1shnuuu/NOVA.git
cd NOVA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Download Vosk Model (40MB, one-time)

```powershell
# Download from: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
# Extract to: assets/vosk-model/
```

### Run

```powershell
python main.py
```

### Build EXE

```powershell
python build\build_exe.py
```

---

## 📁 Project Structure

```
jarvis_workmode/
├── main.py                        # v3 orchestrator
├── config.py                      # JSON-persistent config
├── app_state.py                   # Thread-safe state machine
├── version.py
├── voice/
│   ├── wake_word.py               # Vosk wake word detector
│   ├── recognizer.py              # Vosk command recognizer
│   ├── speaker.py                 # pyttsx3 TTS
│   ├── command_parser.py          # Keyword → Command enum
│   ├── responses.py               # All JARVIS spoken lines
│   └── chime.py                   # Programmatic chime generator
├── hud/
│   ├── hud_window.py              # Transparent HUD overlay
│   ├── voice_ring.py              # Pulsing listening animation
│   └── briefing_screen.py         # Full-screen activation cinematic
├── modes/
│   ├── base_mode.py               # Abstract mode + WindowLayout
│   ├── mode_controller.py         # Time-based mode selection
│   ├── deep_work.py               # Morning focus mode
│   ├── afternoon.py               # Research mode
│   └── evening.py                 # Creative/wind-down mode
├── workspace/
│   ├── launcher.py                # App launcher
│   ├── window_arranger.py         # Window tiling engine
│   ├── deactivator.py             # Graceful app closer
│   └── app_profiles.py            # Window title patterns
├── presence/
│   ├── wifi_monitor.py            # ARP/ping scanner
│   └── absence_detector.py        # Departure trigger
├── services/
│   ├── startup_manager.py         # Windows startup registry
│   └── updater.py                 # GitHub update checker
├── utils/
│   ├── logger.py                  # Rotating file + color console
│   └── helpers.py                 # Retry, admin, mutex
└── build/
    ├── build_exe.py               # PyInstaller build
    ├── build_installer.py         # Full build pipeline
    ├── jarvis_installer.nsi       # NSIS installer
    └── version_info.txt           # EXE metadata
```

---

## 📄 License

MIT License — free to use, modify, and distribute.
