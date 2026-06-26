# main.py — Entry point for MiniKasper
# Run with: python main.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# High-DPI support (must be set before QApplication is created)
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

from mascot import MascotWidget


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)   # keep running even if bubble closes

    mascot = MascotWidget()                # noqa: F841 — kept alive by event loop

    sys.exit(app.exec())


if __name__ == "__main__":
    main()