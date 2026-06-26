# movement.py — Walking, wandering, and pathing AI for MiniKasper

import random
from PySide6.QtCore import QTimer
import config
import utils

_TASKBAR_MARGIN = 48


class MovementController:
    def __init__(self, on_position, on_idle, on_facing, on_footstep, get_sprite_size):
        try:
            self._on_position = on_position
            self._on_idle = on_idle
            self._on_facing = on_facing
            self._on_footstep = on_footstep
            self._get_sprite_size = get_sprite_size

            sw, sh = utils.screen_size()
            self._x = sw // 2
            self._y = sh - 200

            self._target_x = self._x
            self._target_y = self._y
            self._is_walking = False
            self._step_counter = 0

            self._timer = QTimer()
            self._timer.setInterval(config.MOVEMENT_TICK_MS)
            self._timer.timeout.connect(self._tick)
            self._timer.start()

        except Exception as e:
            print("MovementController.__init__ failed", e)

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def x(self):
        try:
            return self._x
        except Exception as e:
            print("MovementController.x failed", e)

    @property
    def y(self):
        try:
            return self._y
        except Exception as e:
            print("MovementController.y failed", e)

    @property
    def is_walking(self):
        try:
            return self._is_walking
        except Exception as e:
            print("MovementController.is_walking failed", e)

    # ── movement API ──────────────────────────────────────────────────────────

    def walk_to(self, x: int, y: int):
        try:
            tx, ty = self._clamp(x, y)
            self._target_x = tx
            self._target_y = ty
            self._is_walking = True

            dx = self._target_x - self._x
            if dx != 0:
                self._on_facing(dx < 0)

        except Exception as e:
            print("MovementController.walk_to failed", e)

    def teleport(self, x: int, y: int):
        try:
            self._x, self._y = self._clamp(x, y)
            self._on_position(self._x, self._y)
        except Exception as e:
            print("MovementController.teleport failed", e)

    def pick_random_target(self):
        try:
            sx, sy, sw, sh = utils.screen_rect()
            sp_w, sp_h = self._get_sprite_size()
            margin = 16

            tx = random.randint(sx + margin, sx + sw - sp_w - margin)

            y_ceil = sy + sh - sp_h - _TASKBAR_MARGIN
            y_floor = sy + (sh // 2)

            if y_floor > y_ceil:
                y_floor = y_ceil

            ty = random.randint(y_floor, y_ceil)
            self.walk_to(tx, ty)

        except Exception as e:
            print("MovementController.pick_random_target failed", e)

    def stop(self):
        try:
            self._is_walking = False
        except Exception as e:
            print("MovementController.stop failed", e)

    # ── internal ──────────────────────────────────────────────────────────────

    def _clamp(self, x: int, y: int) -> tuple[int, int]:
        try:
            sx, sy, sw, sh = utils.screen_rect()
            sp_w, sp_h = self._get_sprite_size()

            cx = utils.clamp(x, sx, sx + sw - sp_w)
            cy = utils.clamp(y, sy, sy + sh - sp_h - _TASKBAR_MARGIN)

            return cx, cy

        except Exception as e:
            print("MovementController._clamp failed", e)
            return x, y

    def _tick(self):
        try:
            if not self._is_walking:
                return

            dx = self._target_x - self._x
            dy = self._target_y - self._y
            dist = (dx ** 2 + dy ** 2) ** 0.5

            if dist <= config.WALK_SPEED:
                self._x, self._y = self._clamp(self._target_x, self._target_y)
                self._is_walking = False
                self._on_position(self._x, self._y)
                self._on_idle()
                return

            step = config.WALK_SPEED / dist
            nx = self._x + int(dx * step)
            ny = self._y + int(dy * step)

            self._x, self._y = self._clamp(nx, ny)
            self._on_position(self._x, self._y)

            self._step_counter += 1
            if self._step_counter % 2 == 0:
                self._on_footstep()

        except Exception as e:
            print("MovementController._tick failed", e)