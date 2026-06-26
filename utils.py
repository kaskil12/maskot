# utils.py — Shared helper utilities for MiniKasper

import random
from PySide6.QtWidgets import QApplication


def screen_size() -> tuple[int, int]:
    """Return (width, height) of the primary screen."""
    screen = QApplication.primaryScreen().availableGeometry()
    return screen.width(), screen.height()


def screen_rect() -> tuple[int, int, int, int]:
    """Return (x, y, width, height) of the available desktop area."""
    geo = QApplication.primaryScreen().availableGeometry()
    return geo.x(), geo.y(), geo.width(), geo.height()


def clamp(value: int, lo: int, hi: int) -> int:
    """Clamp value between lo and hi, inclusive."""
    return max(lo, min(hi, value))


def rand_range(lo: float, hi: float) -> float:
    """Uniform float in [lo, hi]."""
    return random.uniform(lo, hi)


def rand_int_range(lo: int, hi: int) -> int:
    """Uniform integer in [lo, hi]."""
    return random.randint(lo, hi)


def roll(probability: float) -> bool:
    """Return True with the given probability (0.0–1.0)."""
    return random.random() < probability


def sign(value: float) -> int:
    """Return 1, -1, or 0 depending on the sign of value."""
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0