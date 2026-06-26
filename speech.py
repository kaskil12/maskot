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
        layout.setContentsMargins(14, 10, 14, 22)  # bottom margin leaves room for tail
        layout.addWidget(self._label)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    # ── Public API ────────────────────────────────────────────────────────────

    def show_text(self, text: str, mascot_x: int, mascot_y: int):
        """Display text above the mascot window at (mascot_x, mascot_y)."""
        self._label.setText(text)
        self.adjustSize()

        # Position bubble centred above the mascot
        bx = mascot_x + 48 - self.width() // 2
        by = mascot_y - self.height() - 4
        self.move(bx, by)
        self.show()
        self.raise_()

        self._hide_timer.stop()
        self._hide_timer.start(int(config.SHOW_SPEECH_TIME_SEC * 1000))

    def dismiss(self):
        self._hide_timer.stop()
        self.hide()

    # ── Painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        tail_h = 10
        body_h = h - tail_h
        r = 10  # corner radius

        # Bubble body
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, body_h, r, r)

        # Tail triangle pointing downward
        tail_cx = w // 2
        path.moveTo(tail_cx - 8, body_h)
        path.lineTo(tail_cx,     body_h + tail_h)
        path.lineTo(tail_cx + 8, body_h)
        path.closeSubpath()

        painter.setPen(QPen(QColor("#555555"), 1.5))
        painter.setBrush(QColor(255, 255, 240, 230))
        painter.drawPath(path)


class SpeechController:
    """Loads quotes.json and manages showing speech bubbles."""

    def __init__(self, mascot_widget):
        self._mascot = mascot_widget
        self._quotes: list[str] = []
        self._bubble = SpeechBubble()
        self._load_quotes()

    def _load_quotes(self):
        try:
            with open(config.QUOTES_FILE, encoding="utf-8") as f:
                self._quotes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._quotes = ["Hei! 👋"]

    def say(self, text: str):
        """Show a specific message in the speech bubble."""
        pos = self._mascot.pos()
        self._bubble.show_text(text, pos.x(), pos.y())

    def say_random(self):
        """Show a randomly chosen quote."""
        if self._quotes:
            self.say(random.choice(self._quotes))

    def dismiss(self):
        self._bubble.dismiss()