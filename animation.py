# animation.py — Sprite animation state machine for MiniKasper

import os
from enum import Enum, auto
from PySide6.QtGui import QPixmap, QTransform, QColor
from PySide6.QtCore import QTimer, Qt
import config


class AnimState(Enum):
    IDLE       = auto()
    WALK       = auto()
    EAT        = auto()
    SLEEP      = auto()
    DRAG_LEFT  = auto()
    DRAG_RIGHT = auto()


_STATE_FRAMES: dict[AnimState, list[str]] = {
    AnimState.IDLE:       ["idle.png", "idle2.png"],
    AnimState.WALK:       ["walk1.png", "walk2.png", "walk3.png", "walk4.png"],
    AnimState.EAT:        ["eat1.png", "eat2.png", "eat3.png"],
    AnimState.SLEEP:      ["sleep1.png", "sleep2.png"],
    AnimState.DRAG_LEFT:  ["dragleft.png"],
    AnimState.DRAG_RIGHT: ["dragright.png"],
}

# Placeholder size when no real sprites are present
_PLACEHOLDER_SIZE = 16


class Animator:
    """Loads sprites and cycles animation frames on a timer."""

    def __init__(self, on_frame_changed):
        self._on_frame_changed = on_frame_changed
        self._state        = AnimState.IDLE
        self._index        = 0
        self._facing_left  = False
        self._sleep_rotate = False   # True → rotate 90° clockwise (lying down)
        self._frames: dict[AnimState, list[QPixmap]] = {}

        self._load_all_sprites()

        self._timer = QTimer()
        self._timer.setInterval(config.ANIMATION_SPEED_MS)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_all_sprites(self):
        for state, filenames in _STATE_FRAMES.items():
            pixmaps = []
            for fname in filenames:
                path = os.path.join(config.ASSETS_DIR, fname)
                pm = QPixmap(path)
                if pm.isNull():
                    pm = QPixmap(_PLACEHOLDER_SIZE, _PLACEHOLDER_SIZE)
                    # Different colours per state for easy debugging
                    colours = {
                        AnimState.IDLE:       "#7ecfff",
                        AnimState.WALK:       "#a3f0a3",
                        AnimState.EAT:        "#ffb347",
                        AnimState.SLEEP:      "#c9a0dc",
                        AnimState.DRAG_LEFT:  "#ff7f7f",
                        AnimState.DRAG_RIGHT: "#ff7f7f",
                    }
                    pm.fill(QColor(colours.get(state, "#ffffff")))
                else:
                    pm = pm.scaled(
                        pm.width()  * config.SPRITE_SCALE,
                        pm.height() * config.SPRITE_SCALE,
                    )
                pixmaps.append(pm)
            self._frames[state] = pixmaps

    # ── Public API ────────────────────────────────────────────────────────────

    def set_state(self, state: AnimState, facing_left: bool | None = None):
        if facing_left is not None:
            self._facing_left = facing_left
        # Enable 90° rotation only during sleep
        self._sleep_rotate = (state == AnimState.SLEEP)
        if state != self._state:
            self._state = state
            self._index = 0
            self._emit()

    def set_facing(self, facing_left: bool):
        if facing_left != self._facing_left:
            self._facing_left = facing_left
            self._emit()

    @property
    def state(self) -> AnimState:
        return self._state

    @property
    def frame_index(self) -> int:
        return self._index

    def current_pixmap(self) -> QPixmap:
        return self._get_frame(self._state, self._index)

    def sprite_size(self) -> tuple[int, int]:
        pm = self.current_pixmap()
        return pm.width(), pm.height()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _advance(self):
        frames = self._frames[self._state]
        self._index = (self._index + 1) % len(frames)
        self._emit()

    def _emit(self):
        self._on_frame_changed(self._get_frame(self._state, self._index))

    def _get_frame(self, state: AnimState, index: int) -> QPixmap:
        frames = self._frames[state]
        pm = frames[index % len(frames)]

        transform = QTransform()
        if self._facing_left and not self._sleep_rotate:
            transform = transform.scale(-1, 1)
        if self._sleep_rotate:
            # Rotate 90° clockwise so the sprite appears to lie on its right side
            transform = transform.rotate(90)

        if not transform.isIdentity():
            pm = pm.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        return pm