# cursor_actions.py — Cursor chasing, eating, and follow-mode for MiniKasper

from time import sleep
import time

import pyautogui
from PySide6.QtCore import QTimer
import utils

class CursorController:
    """
    Manages cursor-related interactions.

    Callbacks
    ---------
    on_walk_to(x, y)              — delegate to MovementController.walk_to
    on_position() -> (x, y)       — returns current mascot top-left
    get_sprite_size() -> (w, h)   — so we can compute the sprite centre
    on_eat_start()                — called when mascot reaches cursor
    on_eat_done()                 — called when eating animation ends
    """

    CHASE_TICK_MS   = 80    # how often we update the chase target
    EAT_DISTANCE_PX = 24    # distance from sprite CENTRE to cursor before eating

    def __init__(self, on_walk_to, on_position, get_sprite_size, on_eat_start, on_eat_done):
        self._on_walk_to      = on_walk_to
        self._on_position     = on_position
        self._get_sprite_size = get_sprite_size
        self._on_eat_start    = on_eat_start
        self._on_eat_done     = on_eat_done

        self._follow_mode = False
        self._eat_mode    = False

        self._chase_timer = QTimer()
        self._chase_timer.setInterval(self.CHASE_TICK_MS)
        self._chase_timer.timeout.connect(self._chase_tick)

        self._eat_done_timer = QTimer()
        self._eat_done_timer.setSingleShot(True)
        self._eat_done_timer.timeout.connect(self._finish_eating)

    # ── Public API ────────────────────────────────────────────────────────────

    def start_follow(self):
        self._follow_mode = True
        self._eat_mode = False
        self._chase_timer.start()

    def stop_follow(self):
        self._follow_mode = False
        if not self._eat_mode:
            self._chase_timer.stop()

    def start_eat(self):
        self._eat_mode = True
        self._chase_timer.start()

    @property
    def is_active(self) -> bool:
        return self._follow_mode or self._eat_mode

    # ── Internal ──────────────────────────────────────────────────────────────

    def _sprite_centre(self) -> tuple[int, int]:
        """Return the screen-space centre of the mascot sprite."""
        mx, my = self._on_position()
        sw, sh = self._get_sprite_size()
        return mx + sw // 2, my + sh // 2

    def _chase_tick(self):
        cx, cy = pyautogui.position()
        scx, scy = self._sprite_centre()
        dist = ((cx - scx) ** 2 + (cy - scy) ** 2) ** 0.5

        if self._eat_mode and dist < self.EAT_DISTANCE_PX:
            self._begin_eating()
            return

        # Walk sprite top-left so that the sprite centre chases the cursor
        sw, sh = self._get_sprite_size()
        self._on_walk_to(cx - sw // 2, cy - sh // 2)

    def _begin_eating(self):
        self._chase_timer.stop()
        self._eat_mode    = False
        self._follow_mode = False
        self._hide_cursor()
        self._on_eat_start()
        self._eat_done_timer.start(1500)

    def _finish_eating(self):
        self._show_cursor()
        self._on_eat_done()
        self._show_cursor()

    @staticmethod
    def _hide_cursor():
        try:
            import ctypes
            user32 = ctypes.windll.user32

            # Hide cursor (safe enough)
            for _ in range(5):
                user32.ShowCursor(False)

            # DO NOT clip cursor unless you really need it
            user32.ClipCursor(None)

        except Exception as e:
            print(f"Error hiding cursor: {e}")

    @staticmethod
    def _show_cursor():
        try:
            import ctypes
            user32 = ctypes.windll.user32

            # Restore cursor visibility
            for _ in range(5):
                user32.ShowCursor(True)

            # IMPORTANT: release clipping
            user32.ClipCursor(None)

        except Exception as e:
            print(f"Error showing cursor: {e}")