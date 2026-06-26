# speech.py — Speech bubbles and Norwegian quotes for MiniKasper

import json
import random
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPainterPath, QPen
import config


class SpeechBubble(QWidget):
    """A frameless, transparent speech bubble widget that floats above the mascot."""

    def __init__(self, parent=None):
        try:
            super().__init__(parent, Qt.WindowType.Tool
                             | Qt.WindowType.FramelessWindowHint
                             | Qt.WindowType.WindowStaysOnTopHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)

            self._label = QLabel()
            self._label.setWordWrap(True)
            self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            self._label.setFont(font)
            self._label.setStyleSheet("color: #1a1a1a; padding: 6px 10px;")

            layout = QVBoxLayout(self)
            layout.setContentsMargins(14, 10, 14, 22)
            layout.addWidget(self._label)

            self._hide_timer = QTimer(self)
            self._hide_timer.setSingleShot(True)
            self._hide_timer.timeout.connect(self.hide)

        except Exception as e:
            print("SpeechBubble.__init__ failed", e)

    def show_text(self, text: str, mascot_x: int, mascot_y: int):
        """Display text above the mascot window at (mascot_x, mascot_y)."""
        try:
            self._label.setText(text)
            self.adjustSize()

            bx = mascot_x + 48 - self.width() // 2
            by = mascot_y - self.height() - 4
            self.move(bx, by)
            self.show()
            self.raise_()

            self._hide_timer.stop()
            self._hide_timer.start(int(config.SHOW_SPEECH_TIME_SEC * 1000))
        except Exception as e:
            print("SpeechBubble.show_text failed", e)

    def dismiss(self):
        try:
            self._hide_timer.stop()
            self.hide()
        except Exception as e:
            print("SpeechBubble.dismiss failed", e)

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            w, h = self.width(), self.height()
            tail_h = 10
            body_h = h - tail_h
            r = 10

            path = QPainterPath()
            path.addRoundedRect(0, 0, w, body_h, r, r)

            tail_cx = w // 2
            path.moveTo(tail_cx - 8, body_h)
            path.lineTo(tail_cx, body_h + tail_h)
            path.lineTo(tail_cx + 8, body_h)
            path.closeSubpath()

            painter.setPen(QPen(QColor("#555555"), 1.5))
            painter.setBrush(QColor(255, 255, 240, 230))
            painter.drawPath(path)

        except Exception as e:
            print("SpeechBubble.paintEvent failed", e)


class SpeechController:
    """Loads quotes.json and manages showing speech bubbles."""

    def __init__(self, mascot_widget):
        try:
            self._mascot = mascot_widget
            self._quotes: list[str] = []
            self._bubble = SpeechBubble()
            self._load_quotes()
        except Exception as e:
            print("SpeechController.__init__ failed", e)

    def _load_quotes(self):
        try:
            with open(config.QUOTES_FILE, encoding="utf-8") as f:
                self._quotes = json.load(f)
        except Exception as e:
            print("SpeechController._load_quotes failed", e)
            self._quotes = ["Hei! 👋"]

    def say(self, text: str):
        """Show a specific message in the speech bubble."""
        try:
            pos = self._mascot.pos()
            self._bubble.show_text(text, pos.x(), pos.y())
        except Exception as e:
            print("SpeechController.say failed", e)

    def say_random(self):
        """Show a randomly chosen quote."""
        try:
            if self._quotes:
                self.say(random.choice(self._quotes))
        except Exception as e:
            print("SpeechController.say_random failed", e)

    def dismiss(self):
        try:
            self._bubble.dismiss()
        except Exception as e:
            print("SpeechController.dismiss failed", e)