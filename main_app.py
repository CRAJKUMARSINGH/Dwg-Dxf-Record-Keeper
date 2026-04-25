"""
Bridge Engineering Software Suite — Launcher
===========================================
Entry point for the Phase 4 professional desktop application.
"""

import sys
import os
from pathlib import Path

# Add src to python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from ui.main_window import BridgeSuiteMainWindow

def main():
    # Setup application environment
    app = QApplication(sys.argv)
    app.setApplicationName("BridgeMaster Pro")
    app.setOrganizationName("BridgeMaster Software")
    app.setApplicationVersion("1.0.0")

    # Launch main window
    window = BridgeSuiteMainWindow()
    window.setWindowTitle("BridgeMaster Pro 2026 — Professional Bridge CAD")
    window.show()

    
    # Run loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
