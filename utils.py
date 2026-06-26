# utils.py — Shared helper utilities for MiniKasper

import os
import random
import sys
from PySide6.QtWidgets import QApplication


def screen_size() -> tuple[int, int]:
    try:
        """Return (width, height) of the primary screen."""
        screen = QApplication.primaryScreen().availableGeometry()
        return screen.width(), screen.height()
    except:
        print("screen_size failed")


def screen_rect() -> tuple[int, int, int, int]:
    try:
        """Return (x, y, width, height) of the available desktop area."""
        geo = QApplication.primaryScreen().availableGeometry()
        return geo.x(), geo.y(), geo.width(), geo.height()
    except:
        print("screen_rect failed")

def clamp(value: int, lo: int, hi: int) -> int:
    try:
        """Clamp value between lo and hi, inclusive."""
        return max(lo, min(hi, value))
    except:
        print("clamp failed")

def rand_range(lo: float, hi: float) -> float:
    try:
        """Uniform float in [lo, hi]."""
        return random.uniform(lo, hi)
    except:
        print("rand_range failed")

def rand_int_range(lo: int, hi: int) -> int:
    try:
        """Uniform integer in [lo, hi]."""
        return random.randint(lo, hi)
    except:
        print("rand_int_range failed")


def roll(probability: float) -> bool:
    try:
        """Return True with the given probability (0.0–1.0)."""
        return random.random() < probability
    except:
        print("roll failed")
def get_asset_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for local dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores its path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
        # If utils.py is in the root, base_path points to root.

    return os.path.join(base_path, relative_path)
def sign(value: float) -> int:
    try:
        """Return 1, -1, or 0 depending on the sign of value."""
        if value > 0:
            return 1
        if value < 0:
            return -1
        return 0
    except:
        print("sign failed")