# mascot.py — Main mascot widget for MiniKasper

import time
import threading
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore    import Qt, QTimer, QPoint
from PySide6.QtGui     import QPixmap, QPainter

import config
import utils
import pranks
from animation      import Animator, AnimState
from movement       import MovementController
from sounds         import SoundPlayer
from speech         import SpeechController
from cursor_actions import CursorController
from scheduler      import Scheduler
from menu           import build_context_menu

# How many rapid clicks before Kasper snaps and eats the cursor
_ANNOYANCE_THRESHOLD = 4
# Window to count clicks within (ms)
_ANNOYANCE_WINDOW_MS = 3000


class MascotWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._img_label = QLabel(self)
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Sub-systems ───────────────────────────────────────────────────────
        self._sounds   = SoundPlayer()
        self._animator = Animator(on_frame_changed=self._on_frame_changed)
        self._speech   = SpeechController(mascot_widget=self)

        self._movement = MovementController(
            on_position     = self._on_position,
            on_idle         = self._on_arrived,
            on_facing       = self._animator.set_facing,
            on_footstep     = self._sounds.play_footstep,
            get_sprite_size = self._animator.sprite_size,
        )
        self._cursor_ctrl = CursorController(
            on_walk_to      = self._movement.walk_to,
            on_position     = lambda: (self._movement.x, self._movement.y),
            get_sprite_size = self._animator.sprite_size,
            on_eat_start    = self._begin_eating,
            on_eat_done     = self._finish_eating,
        )
        self._scheduler = Scheduler(
            on_google_search  = self._prank_google,
            on_vscode_prank   = self._prank_vscode,
            on_window_drag    = self._prank_drag,
            on_almost_leaving = self._prank_almost_leaving,
        )

        # ── State ─────────────────────────────────────────────────────────────
        self._idle_start     : float | None = None
        self._sleeping       = False
        self._follow_active  = False
        self._dragging       = False
        self._drag_offset    = QPoint()

        # Annoyance tracking
        self._click_times: list[float] = []

        # ── Timers ────────────────────────────────────────────────────────────
        self._wander_timer = QTimer(self)
        self._wander_timer.setSingleShot(True)
        self._wander_timer.timeout.connect(self._pick_wander)

        self._context_timer = QTimer(self)
        self._context_timer.setInterval(5000)
        self._context_timer.timeout.connect(self._check_context)
        self._context_timer.start()

        # ── Initial size and position ─────────────────────────────────────────
        # Start at 16×16; will resize automatically after first frame is emitted
        self.resize(16, 16)
        sw, sh = utils.screen_size()
        self.move(sw // 2 - 8, sh - 200)
        self.show()
        self._schedule_wander()

    # ── Animation callback ────────────────────────────────────────────────────

    def _on_frame_changed(self, pixmap: QPixmap):
        self._img_label.setPixmap(pixmap)
        self._img_label.resize(pixmap.size())
        self.setFixedSize(pixmap.size())

    # ── Movement callbacks ────────────────────────────────────────────────────

    def _on_position(self, x: int, y: int):
        self.move(x, y)

    def _on_arrived(self):
        if self._sleeping or self._cursor_ctrl.is_active:
            return
        self._animator.set_state(AnimState.IDLE)
        self._idle_start = time.time()
        self._schedule_wander()

    def _schedule_wander(self):
        delay_ms = int(utils.rand_range(config.IDLE_MIN_SEC, config.IDLE_MAX_SEC) * 1000)
        self._wander_timer.start(delay_ms)

    def _pick_wander(self):
        if self._sleeping or self._cursor_ctrl.is_active:
            return
        if (self._idle_start is not None
                and time.time() - self._idle_start > config.SLEEP_IDLE_THRESHOLD_SEC
                and utils.roll(config.SLEEP_CHANCE)):
            self._enter_sleep()
            return
        self._animator.set_state(AnimState.WALK)
        self._movement.pick_random_target()

    # ── Sleep ─────────────────────────────────────────────────────────────────

    def _enter_sleep(self):
        self._sleeping = True
        self._wander_timer.stop()
        self._movement.stop()
        self._animator.set_state(AnimState.SLEEP)
        self._sounds.play_loop("sleep")

    def _wake_up(self):
        if not self._sleeping:
            return
        self._sleeping = False
        self._sounds.stop("sleep")
        self._animator.set_state(AnimState.IDLE)
        self._idle_start = time.time()
        self._schedule_wander()

    # ── Cursor eating ─────────────────────────────────────────────────────────

    def _begin_eating(self):
        self._animator.set_state(AnimState.EAT)
        self._sounds.play("nom")

    def _finish_eating(self):
        self._animator.set_state(AnimState.IDLE)
        self._speech.say("😋")
        self._schedule_wander()

    # ── Annoyance system ──────────────────────────────────────────────────────

    def _register_click_annoyance(self):
        """Track rapid clicks. If annoyed enough, Kasper eats the cursor."""
        now = time.time()
        cutoff = now - (_ANNOYANCE_WINDOW_MS / 1000.0)
        self._click_times = [t for t in self._click_times if t > cutoff]
        self._click_times.append(now)

        if len(self._click_times) >= _ANNOYANCE_THRESHOLD:
            self._click_times.clear()
            self._snap_and_eat()

    def _snap_and_eat(self):
        """Kasper has had enough — he snaps and eats the cursor immediately."""
        if self._cursor_ctrl.is_active:
            return
        # Show an annoyed reaction before chasing
        self._speech.say("Det var nok det! 😤")
        # Short delay then immediately start eating (skip the chase, go straight to eat)
        QTimer.singleShot(400, self._cursor_ctrl.start_eat)

    # ── Context detection ─────────────────────────────────────────────────────

    def _check_context(self):
        from window_control import get_foreground_process_name
        fg = get_foreground_process_name()
        if "code" in fg and not self._sleeping:
            self._speech.say("Ser riktig ut 👍")

    # ── Pranks ────────────────────────────────────────────────────────────────

    def _prank_google(self):
        if self._sleeping: return
        threading.Thread(target=pranks.prank_google_search,
                         args=(self._speech,), daemon=True).start()

    def _prank_vscode(self):
        if self._sleeping: return
        threading.Thread(target=pranks.prank_vscode_type,
                         args=(self._speech,), daemon=True).start()

    def _prank_drag(self):
        if self._sleeping: return
        threading.Thread(target=pranks.prank_drag_window,
                         args=(self._handle_drag_anim, self._speech),
                         daemon=True).start()

    def _handle_drag_anim(self, direction: str):
        state = AnimState.DRAG_LEFT if direction == "left" else AnimState.DRAG_RIGHT
        self._animator.set_state(state)
        self._sounds.play("yip")
        QTimer.singleShot(1500, lambda: self._animator.set_state(AnimState.IDLE))

    def _prank_almost_leaving(self):
        if self._sleeping: return
        sx, sy, sw, sh = utils.screen_rect()
        sp_w, sp_h = self._animator.sprite_size()
        go_right = utils.roll(0.5)
        edge_x   = (sx + sw - sp_w - 5) if go_right else (sx + 5)
        edge_y   = self._movement.y
        self._animator.set_state(AnimState.WALK)
        self._movement.walk_to(edge_x, edge_y)

        def _come_back():
            if self._sleeping: return
            self._speech.say(pranks.get_almost_leaving_quote())
            centre_x = sw // 2 - sp_w // 2
            QTimer.singleShot(2000, lambda: (
                self._animator.set_state(AnimState.WALK),
                self._movement.walk_to(centre_x, edge_y),
            ))
        QTimer.singleShot(5000, _come_back)

    # ── Mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if self._sleeping:
            self._wake_up()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self._sounds.play("click")
            self._register_click_annoyance()
            self._speech.say_random()
            self._dragging    = True
            self._drag_offset = event.pos()

        elif event.button() == Qt.MouseButton.RightButton:
            menu = build_context_menu(
                parent    = self,
                on_follow = self._toggle_follow,
                on_quote  = self._speech.say_random,
                on_sleep  = self._enter_sleep,
                on_exit   = QApplication.quit,
            )
            menu.exec(event.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, event):
        if self._sleeping: return
        if event.button() == Qt.MouseButton.LeftButton:
            self._animator.set_state(AnimState.WALK)
            sw, sh = utils.screen_size()
            sp_w, sp_h = self._animator.sprite_size()
            flee_x = utils.rand_int_range(50, sw - sp_w - 50)
            self._movement.walk_to(flee_x, self._movement.y)

    def mouseMoveEvent(self, event):
        if self._dragging:
            new_pos = event.globalPosition().toPoint() - self._drag_offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    # ── Follow mode ───────────────────────────────────────────────────────────

    def _toggle_follow(self, checked: bool):
        self._follow_active = not self._follow_active
        if self._follow_active:
            self._cursor_ctrl.start_follow()
            self._animator.set_state(AnimState.WALK)
        else:
            self._cursor_ctrl.stop_follow()
            self._animator.set_state(AnimState.IDLE)

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)