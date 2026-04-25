"""
Build Script - Nuitka
=====================
Compiles the Bridge Suite into a standalone Windows .EXE.
Run this from a terminal with: py build_exe.py
"""

import os
import subprocess
import sys

def build():
    print("🚀 Starting Build Process...")
    
    # Ensure Nuitka is installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka", "zstandard"])

    command = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-disable-console",
        "--enable-plugin=pyside6",
        "--enable-plugin=matplotlib",
        "--include-data-dir=src/ui=ui",
        "--include-data-dir=config=config",
        "--include-data-dir=assets=assets",
        "--output-dir=dist",
        "--output-filename=BridgeSuitePro",
        "main_app.py"
    ]

    print(f"Executing: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print("✅ Build Successful! Check the 'dist' folder.")
    except Exception as e:
        print(f"❌ Build Failed: {e}")

if __name__ == "__main__":
    build()
