# mascot.py — Main mascot widget for MiniKasper

import time
import threading
from PySide6.QtWidgets import QWidget, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import QPixmap, QPainter

import config
import utils
import pranks
from animation import Animator, AnimState
from movement import MovementController
from sounds import SoundPlayer
from speech import SpeechController
from cursor_actions import CursorController
from scheduler import Scheduler
from menu import build_context_menu

_ANNOYANCE_THRESHOLD = 4
_ANNOYANCE_WINDOW_MS = 3000


class _ThreadSafeSpeechProxy:
    """
    Lightweight proxy that mimics the SpeechController interface 
    but safely redirects execution back to the Main UI Thread via Signals.
    """
    def __init__(self, signal: Signal):
        self._signal = signal

    def say(self, text: str):
        self._signal.emit(text)


class MascotWidget(QWidget):
    # ── Thread-safe Qt Signals ───────────────────────────────────────────────
    speech_signal = Signal(str)
    drag_signal = Signal(str)

    def __init__(self):
        try:
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

            self._sounds = SoundPlayer()
            self._animator = Animator(on_frame_changed=self._on_frame_changed)
            self._speech = SpeechController(mascot_widget=self)

            # Connect thread signals to their safe UI slots
            self.speech_signal.connect(self._speech.say)
            self.drag_signal.connect(self._handle_drag_anim)

            self._movement = MovementController(
                on_position=self._on_position,
                on_idle=self._on_arrived,
                on_facing=self._animator.set_facing,
                on_footstep=self._sounds.play_footstep,
                get_sprite_size=self._animator.sprite_size,
            )

            self._cursor_ctrl = CursorController(
                on_walk_to=self._movement.walk_to,
                on_position=lambda: (self._movement.x, self._movement.y),
                get_sprite_size=self._animator.sprite_size,
                on_eat_start=self._begin_eating,
                on_eat_done=self._finish_eating,
            )

            self._scheduler = Scheduler(
                on_google_search=self._prank_google,
                on_vscode_prank=self._prank_vscode,
                on_window_drag=self._prank_drag,
                on_almost_leaving=self._prank_almost_leaving,
            )

            self._idle_start: float | None = None
            self._sleeping = False
            self._follow_active = False
            self._dragging = False
            self._drag_offset = QPoint()

            self._click_times: list[float] = []

            self._wander_timer = QTimer(self)
            self._wander_timer.setSingleShot(True)
            self._wander_timer.timeout.connect(self._pick_wander)

            self._context_timer = QTimer(self)
            self._context_timer.setInterval(5000)
            self._context_timer.timeout.connect(self._check_context)
            self._context_timer.start()

            self.resize(16, 16)
            sw, sh = utils.screen_size()
            self.move(sw // 2 - 8, sh - 200)
            self.show()
            self._schedule_wander()

        except Exception as e:
            print("MascotWidget.__init__ failed", e)

    # ── animation ─────────────────────────────────────────────────────────────

    def _on_frame_changed(self, pixmap: QPixmap):
        try:
            self._img_label.setPixmap(pixmap)
            self._img_label.resize(pixmap.size())
            self.setFixedSize(pixmap.size())
        except Exception as e:
            print("MascotWidget._on_frame_changed failed", e)

    # ── movement ──────────────────────────────────────────────────────────────

    def _on_position(self, x: int, y: int):
        try:
            self.move(x, y)
        except Exception as e:
            print("MascotWidget._on_position failed", e)

    def _on_arrived(self):
        try:
            if self._sleeping or self._cursor_ctrl.is_active:
                return
            self._animator.set_state(AnimState.IDLE)
            self._idle_start = time.time()
            self._schedule_wander()
        except Exception as e:
            print("MascotWidget._on_arrived failed", e)

    def _schedule_wander(self):
        try:
            delay_ms = int(utils.rand_range(config.IDLE_MIN_SEC, config.IDLE_MAX_SEC) * 1000)
            self._wander_timer.start(delay_ms)
        except Exception as e:
            print("MascotWidget._schedule_wander failed", e)

    def _pick_wander(self):
        try:
            if self._sleeping or self._cursor_ctrl.is_active:
                return

            if (self._idle_start is not None
                and time.time() - self._idle_start > config.SLEEP_IDLE_THRESHOLD_SEC
                and utils.roll(config.SLEEP_CHANCE)):
                self._enter_sleep()
                return

            self._animator.set_state(AnimState.WALK)
            self._movement.pick_random_target()

        except Exception as e:
            print("MascotWidget._pick_wander failed", e)

    # ── sleep ────────────────────────────────────────────────────────────────

    def _enter_sleep(self):
        try:
            self._sleeping = True
            self._wander_timer.stop()
            self._movement.stop()
            self._animator.set_state(AnimState.SLEEP)
            self._sounds.play_loop("sleep")
        except Exception as e:
            print("MascotWidget._enter_sleep failed", e)

    def _wake_up(self):
        try:
            if not self._sleeping:
                return
            self._sleeping = False
            self._sounds.stop("sleep")
            self._animator.set_state(AnimState.IDLE)
            self._idle_start = time.time()
            self._schedule_wander()
        except Exception as e:
            print("MascotWidget._wake_up failed", e)

    # ── cursor eat ────────────────────────────────────────────────────────────

    def _begin_eating(self):
        try:
            self._animator.set_state(AnimState.EAT)
            self._sounds.play("nom")
        except Exception as e:
            print("MascotWidget._begin_eating failed", e)

    def _finish_eating(self):
        try:
            self._animator.set_state(AnimState.IDLE)
            self._speech.say("😋")
            self._schedule_wander()
        except Exception as e:
            print("MascotWidget._finish_eating failed", e)

    # ── annoyance ─────────────────────────────────────────────────────────────

    def _register_click_annoyance(self):
        try:
            now = time.time()
            cutoff = now - (_ANNOYANCE_WINDOW_MS / 1000.0)
            self._click_times = [t for t in self._click_times if t > cutoff]
            self._click_times.append(now)

            if len(self._click_times) >= _ANNOYANCE_THRESHOLD:
                self._click_times.clear()
                self._snap_and_eat()
        except Exception as e:
            print("MascotWidget._register_click_annoyance failed", e)

    def _snap_and_eat(self):
        try:
            if self._cursor_ctrl.is_active:
                return
            self._speech.say("Det var nok det! 😤")
            QTimer.singleShot(400, self._cursor_ctrl.start_eat)
        except Exception as e:
            print("MascotWidget._snap_and_eat failed", e)

    # ── context ───────────────────────────────────────────────────────────────

    def _check_context(self):
        try:
            from window_control import get_foreground_process_name
            fg = get_foreground_process_name()
            if "code" in fg and not self._sleeping:
                self._speech.say("Ser riktig ut 👍")
        except Exception as e:
            print("MascotWidget._check_context failed", e)

    # ── pranks ───────────────────────────────────────────────────────────────

    def _prank_google(self):
        try:
            if self._sleeping:
                return
            proxy_speech = _ThreadSafeSpeechProxy(self.speech_signal)
            threading.Thread(target=pranks.prank_google_search,
                             args=(proxy_speech,), daemon=True).start()
        except Exception as e:
            print("MascotWidget._prank_google failed", e)

    def _prank_vscode(self):
        try:
            if self._sleeping:
                return
            proxy_speech = _ThreadSafeSpeechProxy(self.speech_signal)
            threading.Thread(target=pranks.prank_vscode_type,
                             args=(proxy_speech,), daemon=True).start()
        except Exception as e:
            print("MascotWidget._prank_vscode failed", e)

    def _prank_drag(self):
        try:
            if self._sleeping:
                return
            proxy_speech = _ThreadSafeSpeechProxy(self.speech_signal)
            safe_drag_cb = lambda direction: self.drag_signal.emit(direction)

            threading.Thread(target=pranks.prank_drag_window,
                             args=(safe_drag_cb, proxy_speech),
                             daemon=True).start()
        except Exception as e:
            print("MascotWidget._prank_drag failed", e)

    def _handle_drag_anim(self, direction: str):
        try:
            state = AnimState.DRAG_LEFT if direction == "left" else AnimState.DRAG_RIGHT
            self._animator.set_state(state)
            self._sounds.play("yip")
            QTimer.singleShot(1500, lambda: self._animator.set_state(AnimState.IDLE))
        except Exception as e:
            print("MascotWidget._handle_drag_anim failed", e)

    def _prank_almost_leaving(self):
        try:
            if self._sleeping:
                return

            sx, sy, sw, sh = utils.screen_rect()
            sp_w, sp_h = self._animator.sprite_size()

            go_right = utils.roll(0.5)
            edge_x = (sx + sw - sp_w - 5) if go_right else (sx + 5)
            edge_y = self._movement.y

            self._animator.set_state(AnimState.WALK)
            self._movement.walk_to(edge_x, edge_y)

            def _come_back():
                try:
                    if self._sleeping:
                        return
                    self._speech.say(pranks.get_almost_leaving_quote())
                    centre_x = sw // 2 - sp_w // 2
                    QTimer.singleShot(2000, lambda: (
                        self._animator.set_state(AnimState.WALK),
                        self._movement.walk_to(centre_x, edge_y),
                    ))
                except Exception as e:
                    print("MascotWidget._come_back failed", e)

            QTimer.singleShot(5000, _come_back)

        except Exception as e:
            print("MascotWidget._prank_almost_leaving failed", e)

    # ── mouse ────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        try:
            if self._sleeping:
                self._wake_up()
                return

            if event.button() == Qt.MouseButton.LeftButton:
                self._sounds.play("click")
                self._register_click_annoyance()
                self._speech.say_random()
                self._dragging = True
                self._drag_offset = event.pos()

            elif event.button() == Qt.MouseButton.RightButton:
                menu = build_context_menu(
                    parent=self,
                    on_follow=self._toggle_follow,
                    on_quote=self._speech.say_random,
                    on_sleep=self._enter_sleep,
                    on_exit=QApplication.quit,
                )
                menu.exec(event.globalPosition().toPoint())

        except Exception as e:
            print("MascotWidget.mousePressEvent failed", e)

    def mouseDoubleClickEvent(self, event):
        try:
            if self._sleeping:
                return
            if event.button() == Qt.MouseButton.LeftButton:
                self._animator.set_state(AnimState.WALK)
                sw, sh = utils.screen_size()
                sp_w, sp_h = self._animator.sprite_size()
                flee_x = utils.rand_int_range(50, sw - sp_w - 50)
                self._movement.walk_to(flee_x, self._movement.y)
        except Exception as e:
            print("MascotWidget.mouseDoubleClickEvent failed", e)

    def mouseMoveEvent(self, event):
        try:
            if self._dragging:
                new_pos = event.globalPosition().toPoint() - self._drag_offset
                self.move(new_pos)
        except Exception as e:
            print("MascotWidget.mouseMoveEvent failed", e)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._dragging = False
        except Exception as e:
            print("MascotWidget.mouseReleaseEvent failed", e)

    # ── follow ───────────────────────────────────────────────────────────────

    def _toggle_follow(self, checked: bool):
        try:
            self._follow_active = not self._follow_active
            if self._follow_active:
                self._cursor_ctrl.start_follow()
                self._animator.set_state(AnimState.WALK)
            else:
                self._cursor_ctrl.stop_follow()
                self._animator.set_state(AnimState.IDLE)
        except Exception as e:
            print("MascotWidget._toggle_follow failed", e)

    # ── paint ────────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        except Exception as e:
            print("MascotWidget.paintEvent failed", e)