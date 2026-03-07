"""
Full Build Pipeline — EXE + Installer in one command.
Run from project root: python build/build_installer.py

Prerequisites:
  - PyInstaller: pip install pyinstaller
  - NSIS: https://nsis.sourceforge.io (free, optional — EXE still builds without it)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def build_all() -> None:
    root = Path(__file__).resolve().parent.parent

    print("=" * 50)
    print("Step 1/2 — Building EXE…")
    print("=" * 50)
    result = subprocess.run(
        [sys.executable, str(root / "build" / "build_exe.py")],
        cwd=root,
    )
    if result.returncode != 0:
        print("❌ EXE build failed. Aborting.")
        sys.exit(1)

    print()
    print("=" * 50)
    print("Step 2/2 — Building Installer…")
    print("=" * 50)

    nsis_paths = [
        Path("C:/Program Files (x86)/NSIS/makensis.exe"),
        Path("C:/Program Files/NSIS/makensis.exe"),
    ]
    makensis = next((p for p in nsis_paths if p.exists()), None)

    if not makensis:
        print("⚠️  NSIS not found — skipping installer.")
        print("   Install NSIS from: https://nsis.sourceforge.io")
        exe = root / "dist" / "JarvisWorkMode.exe"
        print(f"   Standalone EXE: {exe}")
        return

    result = subprocess.run(
        [str(makensis), str(root / "build" / "jarvis_installer.nsi")],
        cwd=root / "build",
    )

    if result.returncode == 0:
        print("\n✅ Installer built successfully!")
        print("   Output: build/JarvisWorkMode_Setup_v1.0.0.exe")
    else:
        print("\n❌ Installer build failed.")


if __name__ == "__main__":
    build_all()
