# scheduler.py — Random event scheduler for MiniKasper

from PySide6.QtCore import QTimer
import config
import utils
import pranks


class Scheduler:
    """
    Fires random prank events at a configurable interval.
    """

    def __init__(self, on_google_search, on_vscode_prank,
                 on_window_drag, on_almost_leaving):
        try:
            self._on_google_search = on_google_search
            self._on_vscode_prank = on_vscode_prank
            self._on_window_drag = on_window_drag
            self._on_almost_leaving = on_almost_leaving

            self._timer = QTimer()
            self._timer.setInterval(int(config.SCHEDULER_TICK_SEC * 1000))
            self._timer.timeout.connect(self._tick)
            self._timer.start()

        except Exception as e:
            print("Scheduler.__init__ failed", e)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _tick(self):
        """Roll for each possible event. Fire at most one per tick."""
        try:
            import random

            events = [
                (config.GOOGLE_SEARCH_CHANCE, self._on_google_search),
                (config.VSCODE_PRANK_CHANCE, self._on_vscode_prank),
                (config.WINDOW_DRAG_CHANCE, self._on_window_drag),
                (config.ALMOST_LEAVING_CHANCE, self._on_almost_leaving),
            ]

            random.shuffle(events)

            for probability, callback in events:
                try:
                    if utils.roll(probability):
                        callback()
                        return
                except Exception as e:
                    print("_tick callback execution failed", e)

        except Exception as e:
            print("Scheduler._tick failed", e)