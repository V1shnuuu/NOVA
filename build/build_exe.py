"""
Build Script — Compiles JARVIS WorkMode into a single .exe via PyInstaller.
Run from project root: python build/build_exe.py
Output: dist/JarvisWorkMode.exe
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def build() -> None:
    """Run PyInstaller with all required options."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "JarvisWorkMode",
        "--add-data", f"{PROJECT_ROOT / 'version.py'};.",
        "--hidden-import", "win32timezone",
        "--hidden-import", "pystray._win32",
        "--hidden-import", "pkg_resources.py2_warn",
        "--collect-all", "spotipy",
        "--collect-all", "pystray",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        str(PROJECT_ROOT / "main.py"),
    ]

    # Optionally add icon if it exists
    icon_path = PROJECT_ROOT / "ui" / "assets" / "icon.ico"
    if icon_path.exists():
        cmd.insert(-1, "--icon")
        cmd.insert(-1, str(icon_path))

    version_file = PROJECT_ROOT / "build" / "version_info.txt"
    if version_file.exists():
        cmd.insert(-1, "--version-file")
        cmd.insert(-1, str(version_file))

    print("=" * 50)
    print("Building JARVIS WorkMode EXE…")
    print("=" * 50)
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        exe = PROJECT_ROOT / "dist" / "JarvisWorkMode.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / (1024 * 1024)
            print(f"\n✅ Build successful!")
            print(f"   Output: {exe}")
            print(f"   Size:   {size_mb:.1f} MB")
        else:
            print("\n✅ Build finished (check dist/ for output).")
    else:
        print("\n❌ Build failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    build()
