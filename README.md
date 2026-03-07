# 🤖 JARVIS WorkMode

An intelligent, automated desktop productivity assistant for **Windows 11**.

JARVIS detects when you arrive at your desk (via phone presence on WiFi or a keyboard shortcut), then automatically launches your productivity workspace — opening ChatGPT and Claude in the browser, launching Spotify, and tiling all windows into a clean layout.

**100% free · open-source · Python-based · Windows 11**

---

## ✨ Features

| Feature | Description |
|---|---|
| **Phone Presence Detection** | Detects your phone on WiFi via ARP or ICMP ping |
| **Bluetooth Detection** | Optional BLE-based detection (experimental) |
| **Global Hotkey** | Instantly activate with `CTRL+ALT+W` |
| **Browser Launcher** | Opens ChatGPT & Claude in separate windows |
| **Spotify Integration** | Launches Spotify + starts a playlist at set volume |
| **Window Tiling** | Automatically arranges all windows in a 3-column layout |
| **Cooldown Protection** | Prevents repeated triggers within 5 minutes |
| **Diagnostic Mode** | Dumps all processes, windows, ARP table on startup |
| **Colored Logging** | Timestamped console + file logging |

---

## 📁 Project Structure

```
jarvis_workmode/
├── main.py                         # Entry point / orchestrator
├── config.py                       # All user settings
├── requirements.txt                # pip dependencies
├── README.md
├── triggers/
│   ├── wifi_presence.py            # ARP/ping phone detection
│   ├── bluetooth_presence.py       # BLE detection (optional)
│   └── manual_trigger.py           # CTRL+ALT+W hotkey
├── automation/
│   ├── workspace_launcher.py       # Opens browsers + Spotify
│   ├── window_manager.py           # Positions/resizes windows
│   └── spotify_controller.py       # Spotify Web API control
└── utils/
    ├── logger.py                   # Colored console + file logging
    └── helpers.py                  # Retry, admin check, process utils
```

---

## 🚀 Setup

### 1. Prerequisites

- **Windows 11** (or 10)
- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **Spotify Desktop** (optional) — [spotify.com/download](https://www.spotify.com/download)

### 2. Clone & Install

```powershell
cd jarvis_workmode

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. pywin32 Post-Install

After installing, run the pywin32 post-install script:

```powershell
python venv\Scripts\pywin32_postinstall.py -install
```

### 4. Configure

Open **`config.py`** and update these values:

```python
# Your phone's IP address (find it in your router's admin page)
PHONE_IP = "192.168.1.42"

# Your phone's MAC address
PHONE_MAC = "AA:BB:CC:DD:EE:FF"

# Detection method: "ping", "arp", or "bluetooth"
PRESENCE_DETECTION_METHOD = "arp"
```

### 5. Spotify Setup (Optional)

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Create a new app (it's free)
3. Set Redirect URI to `http://localhost:8888/callback`
4. Copy your **Client ID** and **Client Secret** into `config.py`:

```python
SPOTIFY_CLIENT_ID = "your-client-id"
SPOTIFY_CLIENT_SECRET = "your-client-secret"
SPOTIFY_PLAYLIST_URI = "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M"  # example
```

> **Note:** On first run, a browser tab will open asking you to authorize the app. After that, a `.cache` file stores the token and you won't be asked again.

### 6. Run

```powershell
# Run as Administrator (recommended for global hotkeys)
python main.py
```

Or run silently without a console window:

```powershell
pythonw.exe main.py
```

---

## 📱 Finding Your Phone's MAC Address

| Device | Path |
|---|---|
| **Android** | Settings → About Phone → Status → Wi-Fi MAC Address |
| **iPhone** | Settings → Wi-Fi → tap ⓘ next to your network → Wi-Fi Address |

To find your phone's **IP address**, check your router's admin page (usually `192.168.1.1`) or run `arp -a` in PowerShell while your phone is connected.

---

## ⌨️ Usage

| Action | How |
|---|---|
| **Manual activate** | Press `CTRL+ALT+W` |
| **Auto activate** | Just walk in — your phone triggers it |
| **Stop** | Press `CTRL+C` in the console |
| **Diagnostics** | Set `DIAGNOSTIC_MODE = True` in `config.py` |

---

## 🖥️ Window Layout

The default layout tiles three apps across your screen:

```
┌──────────────┬──────────────┬──────────────┐
│              │              │              │
│   ChatGPT    │    Claude    │   Spotify    │
│   (33%)      │   (34%)      │   (33%)      │
│              │              │              │
└──────────────┴──────────────┴──────────────┘
```

Customize in `config.py` by editing the `LAYOUT` dict (values are fractions of screen size):

```python
LAYOUT = {
    "chatgpt": {"x": 0.0,  "y": 0.0, "w": 0.5, "h": 1.0},
    "claude":  {"x": 0.5,  "y": 0.0, "w": 0.5, "h": 0.5},
    "spotify": {"x": 0.5,  "y": 0.5, "w": 0.5, "h": 0.5},
}
```

---

## 🔧 Running at Windows Startup

Use **Task Scheduler** to run JARVIS at login:

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task → Name: "JARVIS WorkMode"
3. Trigger: "When I log on"
4. Action: "Start a program"
   - Program: `C:\path\to\venv\Scripts\pythonw.exe`
   - Arguments: `main.py`
   - Start in: `C:\path\to\jarvis_workmode`
5. Check "Run with highest privileges" (for global hotkeys)

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| Hotkey doesn't work | Run as Administrator |
| Phone not detected (ping) | Phone may block ICMP — switch to `"arp"` method |
| Phone not detected (ARP) | Ensure phone is on the same WiFi network; try pinging it first |
| Spotify won't play | Check Spotify is open and logged in; verify API credentials |
| Window not arranged | Enable `DIAGNOSTIC_MODE` to see all window titles |
| Wrong monitor | Set `MONITOR_INDEX` in config (currently primary only) |

---

## 🧩 Extension Ideas

These are **not implemented** but can be added later:

1. **System Tray Icon** — `pystray` + `PIL` for a right-click menu
2. **Voice Greeting** — `pyttsx3` to say "Welcome back"
3. **Deactivation Mode** — close apps when phone leaves WiFi
4. **Web Dashboard** — Flask localhost status page
5. **Multi-Profile** — different layouts for day/night
6. **Camera Detection** — OpenCV face detection trigger
7. **Toast Notifications** — `win10toast` for native Windows alerts
8. **Dynamic Playlists** — pick playlist by time of day
9. **GitHub Auto-Pull** — pull latest code on activation

---

## 📄 License

This project is free and open-source. Use it however you like.
