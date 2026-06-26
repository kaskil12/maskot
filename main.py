# main.py — Entry point for MiniKasper
# Run with: python main.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from mascot import MascotWidget


def main():
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)

        mascot = MascotWidget()  # kept alive by Qt event loop
        sys.exit(app.exec())

    except Exception as e:
        print("main failed", e)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("main (entry) failed", e)