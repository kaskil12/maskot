# animation.py — Sprite animation state machine for MiniKasper

import os
from enum import Enum, auto
from PySide6.QtGui import QPixmap, QTransform, QColor
from PySide6.QtCore import QTimer, Qt
import config


class AnimState(Enum):
    IDLE = auto()
    WALK = auto()
    EAT = auto()
    SLEEP = auto()
    DRAG_LEFT = auto()
    DRAG_RIGHT = auto()


_STATE_FRAMES: dict[AnimState, list[str]] = {
    AnimState.IDLE: ["idle.png", "idle2.png"],
    AnimState.WALK: ["walk1.png", "walk2.png", "walk3.png", "walk4.png"],
    AnimState.EAT: ["eat1.png", "eat2.png", "eat3.png"],
    AnimState.SLEEP: ["sleep1.png", "sleep2.png"],
    AnimState.DRAG_LEFT: ["dragleft.png"],
    AnimState.DRAG_RIGHT: ["dragright.png"],
}

_PLACEHOLDER_SIZE = 16


class Animator:

    def __init__(self, on_frame_changed):
        try:
            self._on_frame_changed = on_frame_changed
            self._state = AnimState.IDLE
            self._index = 0
            self._facing_left = False
            self._sleep_rotate = False
            self._frames: dict[AnimState, list[QPixmap]] = {}

            self._load_all_sprites()

            self._timer = QTimer()
            self._timer.setInterval(config.ANIMATION_SPEED_MS)
            self._timer.timeout.connect(self._advance)
            self._timer.start()

        except Exception as e:
            print("Animator.__init__ failed", e)

    # ── loading ───────────────────────────────────────────────────────────────

    def _load_all_sprites(self):
        try:
            for state, filenames in _STATE_FRAMES.items():
                pixmaps = []

                for fname in filenames:
                    path = os.path.join(config.ASSETS_DIR, fname)
                    pm = QPixmap(path)

                    if pm.isNull():
                        pm = QPixmap(_PLACEHOLDER_SIZE, _PLACEHOLDER_SIZE)

                        colours = {
                            AnimState.IDLE: "#7ecfff",
                            AnimState.WALK: "#a3f0a3",
                            AnimState.EAT: "#ffb347",
                            AnimState.SLEEP: "#c9a0dc",
                            AnimState.DRAG_LEFT: "#ff7f7f",
                            AnimState.DRAG_RIGHT: "#ff7f7f",
                        }

                        pm.fill(QColor(colours.get(state, "#ffffff")))
                    else:
                        pm = pm.scaled(
                            pm.width() * config.SPRITE_SCALE,
                            pm.height() * config.SPRITE_SCALE,
                        )

                    pixmaps.append(pm)

                self._frames[state] = pixmaps

        except Exception as e:
            print("Animator._load_all_sprites failed", e)

    # ── public API ────────────────────────────────────────────────────────────

    def set_state(self, state: AnimState, facing_left: bool | None = None):
        try:
            if facing_left is not None:
                self._facing_left = facing_left

            self._sleep_rotate = (state == AnimState.SLEEP)

            if state != self._state:
                self._state = state
                self._index = 0
                self._emit()

        except Exception as e:
            print("Animator.set_state failed", e)

    def set_facing(self, facing_left: bool):
        try:
            if facing_left != self._facing_left:
                self._facing_left = facing_left
                self._emit()
        except Exception as e:
            print("Animator.set_facing failed", e)

    @property
    def state(self) -> AnimState:
        try:
            return self._state
        except Exception as e:
            print("Animator.state failed", e)

    @property
    def frame_index(self) -> int:
        try:
            return self._index
        except Exception as e:
            print("Animator.frame_index failed", e)

    def current_pixmap(self) -> QPixmap:
        try:
            return self._get_frame(self._state, self._index)
        except Exception as e:
            print("Animator.current_pixmap failed", e)

    def sprite_size(self) -> tuple[int, int]:
        try:
            pm = self.current_pixmap()
            return pm.width(), pm.height()
        except Exception as e:
            print("Animator.sprite_size failed", e)
            return (0, 0)

    # ── internal ──────────────────────────────────────────────────────────────

    def _advance(self):
        try:
            frames = self._frames[self._state]
            self._index = (self._index + 1) % len(frames)
            self._emit()
        except Exception as e:
            print("Animator._advance failed", e)

    def _emit(self):
        try:
            self._on_frame_changed(self._get_frame(self._state, self._index))
        except Exception as e:
            print("Animator._emit failed", e)

    def _get_frame(self, state: AnimState, index: int) -> QPixmap:
        try:
            frames = self._frames[state]
            pm = frames[index % len(frames)]

            transform = QTransform()

            if self._facing_left and not self._sleep_rotate:
                transform = transform.scale(-1, 1)

            if self._sleep_rotate:
                transform = transform.rotate(90)

            if not transform.isIdentity():
                pm = pm.transformed(
                    transform,
                    Qt.TransformationMode.SmoothTransformation
                )

            return pm

        except Exception as e:
            print("Animator._get_frame failed", e)
            return QPixmap()