# cursor_actions.py — Cursor chasing, eating, and follow-mode for MiniKasper

from time import sleep
import time

import pyautogui
from PySide6.QtCore import QTimer
import utils


class CursorController:
    """
    Manages cursor-related interactions.
    """

    CHASE_TICK_MS = 80
    EAT_DISTANCE_PX = 24

    def __init__(self, on_walk_to, on_position, get_sprite_size, on_eat_start, on_eat_done):
        try:
            self._on_walk_to = on_walk_to
            self._on_position = on_position
            self._get_sprite_size = get_sprite_size
            self._on_eat_start = on_eat_start
            self._on_eat_done = on_eat_done

            self._follow_mode = False
            self._eat_mode = False

            self._chase_timer = QTimer()
            self._chase_timer.setInterval(self.CHASE_TICK_MS)
            self._chase_timer.timeout.connect(self._chase_tick)

            self._eat_done_timer = QTimer()
            self._eat_done_timer.setSingleShot(True)
            self._eat_done_timer.timeout.connect(self._finish_eating)

        except Exception as e:
            print("CursorController.__init__ failed", e)

    # ── Public API ────────────────────────────────────────────────────────────

    def start_follow(self):
        try:
            self._follow_mode = True
            self._eat_mode = False
            self._chase_timer.start()
        except Exception as e:
            print("CursorController.start_follow failed", e)

    def stop_follow(self):
        try:
            self._follow_mode = False
            if not self._eat_mode:
                self._chase_timer.stop()
        except Exception as e:
            print("CursorController.stop_follow failed", e)

    def start_eat(self):
        try:
            self._eat_mode = True
            self._chase_timer.start()
        except Exception as e:
            print("CursorController.start_eat failed", e)

    @property
    def is_active(self) -> bool:
        try:
            return self._follow_mode or self._eat_mode
        except Exception as e:
            print("CursorController.is_active failed", e)
            return False

    # ── Internal ──────────────────────────────────────────────────────────────

    def _sprite_centre(self) -> tuple[int, int]:
        try:
            mx, my = self._on_position()
            sw, sh = self._get_sprite_size()
            return mx + sw // 2, my + sh // 2
        except Exception as e:
            print("CursorController._sprite_centre failed", e)
            return 0, 0

    def _chase_tick(self):
        try:
            cx, cy = pyautogui.position()
            scx, scy = self._sprite_centre()

            dist = ((cx - scx) ** 2 + (cy - scy) ** 2) ** 0.5

            if self._eat_mode and dist < self.EAT_DISTANCE_PX:
                self._begin_eating()
                return

            sw, sh = self._get_sprite_size()
            self._on_walk_to(cx - sw // 2, cy - sh // 2)

        except Exception as e:
            print("CursorController._chase_tick failed", e)

    def _begin_eating(self):
        try:
            self._chase_timer.stop()
            self._eat_mode = False
            self._follow_mode = False
            self._hide_cursor()
            self._on_eat_start()
            self._eat_done_timer.start(1500)
        except Exception as e:
            print("CursorController._begin_eating failed", e)

    def _finish_eating(self):
        try:
            self._show_cursor()
            self._on_eat_done()
            self._show_cursor()
        except Exception as e:
            print("CursorController._finish_eating failed", e)

    # ── cursor visibility ─────────────────────────────────────────────────────

    @staticmethod
    def _hide_cursor():
        try:
            import ctypes
            user32 = ctypes.windll.user32

            for _ in range(100):
                pyautogui.moveTo(0, 0) 
                user32.ShowCursor(False)
                sleep(0.1)

            user32.ClipCursor(None)

        except Exception as e:
            print("CursorController._hide_cursor failed", e)

    @staticmethod
    def _show_cursor():
        try:
            import ctypes
            user32 = ctypes.windll.user32

            for _ in range(5):
                user32.ShowCursor(True)
                pyautogui.moveTo(500, 500) 

            user32.ClipCursor(None)

        except Exception as e:
            print("CursorController._show_cursor failed", e)