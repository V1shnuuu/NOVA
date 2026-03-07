"""
v3 Build Script — Compiles JARVIS WorkMode into a single .exe.
Run from project root: python build/build_exe.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build() -> None:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "JarvisWorkMode",
        "--add-data", f"{ROOT / 'voice' / 'assets'};voice/assets",
        "--add-data", f"{ROOT / 'hud' / 'assets'};hud/assets",
        "--hidden-import", "win32timezone",
        "--hidden-import", "vosk",
        "--hidden-import", "pyaudio",
        "--hidden-import", "pyttsx3.drivers",
        "--hidden-import", "pyttsx3.drivers.sapi5",
        "--collect-all", "vosk",
        "--collect-all", "spotipy",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "pandas",
        str(ROOT / "main.py"),
    ]

    icon = ROOT / "hud" / "assets" / "icon.ico"
    if icon.exists():
        cmd.insert(-1, "--icon")
        cmd.insert(-1, str(icon))

    vinfo = ROOT / "build" / "version_info.txt"
    if vinfo.exists():
        cmd.insert(-1, "--version-file")
        cmd.insert(-1, str(vinfo))

    print("=" * 50)
    print("Building JARVIS WorkMode v3 EXE…")
    print("=" * 50)
    result = subprocess.run(cmd, cwd=ROOT)

    if result.returncode == 0:
        exe = ROOT / "dist" / "JarvisWorkMode.exe"
        if exe.exists():
            print(f"\n✅ Success: {exe} ({exe.stat().st_size / 1024**2:.1f} MB)")
        else:
            print("\n✅ Build finished (check dist/).")
    else:
        print("\n❌ Build failed.")
        sys.exit(1)


if __name__ == "__main__":
    build()
