# scheduler.py — Random event scheduler for MiniKasper

from PySide6.QtCore import QTimer
import config
import utils
import pranks


class Scheduler:
    """
    Fires random prank events at a configurable interval.

    Each tick rolls probability dice against every configured event.
    At most one prank fires per tick to avoid chaos.

    Callbacks supplied by the mascot
    ---------------------------------
    on_google_search()      — trigger the Google search prank
    on_vscode_prank()       — trigger the VS Code typing prank
    on_window_drag()        — trigger the window drag prank
    on_almost_leaving()     — trigger the "almost leaving" edge walk
    """

    def __init__(self, on_google_search, on_vscode_prank,
                 on_window_drag, on_almost_leaving):
        self._on_google_search   = on_google_search
        self._on_vscode_prank    = on_vscode_prank
        self._on_window_drag     = on_window_drag
        self._on_almost_leaving  = on_almost_leaving

        self._timer = QTimer()
        self._timer.setInterval(int(config.SCHEDULER_TICK_SEC * 1000))
        self._timer.timeout.connect(self._tick)
        self._timer.start()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _tick(self):
        """Roll for each possible event. Fire at most one per tick."""

        # Build a weighted list of (probability, callback) pairs and shuffle so
        # no single prank always wins when multiple dice would succeed.
        events = [
            (config.GOOGLE_SEARCH_CHANCE,  self._on_google_search),
            (config.VSCODE_PRANK_CHANCE,   self._on_vscode_prank),
            (config.WINDOW_DRAG_CHANCE,    self._on_window_drag),
            (config.ALMOST_LEAVING_CHANCE, self._on_almost_leaving),
        ]

        import random
        random.shuffle(events)

        for probability, callback in events:
            if utils.roll(probability):
                callback()
                return   # only one prank per tick