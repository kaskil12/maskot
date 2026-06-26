# window_control.py — Win32 window detection and interaction for MiniKasper
# Uses pywin32 (win32gui, win32process) and psutil.

from __future__ import annotations
import time
import win32gui
import win32process
import win32con
import psutil


def _get_pid(hwnd: int) -> int:
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    except:
        print("_get_pid failed")


def _process_name(pid: int) -> str:
    try:
        return psutil.Process(pid).name().lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return ""


def find_window_by_process(process_name: str) -> int | None:
    try:
        """
        Return the HWND of the first visible window whose owning process matches
        *process_name* (case-insensitive, partial match allowed).
        Returns None if not found.
        """
        result: list[int] = []

        def callback(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            name = _process_name(_get_pid(hwnd))
            if process_name.lower() in name:
                result.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return result[0] if result else None
    except:
        print("Find_window_by_process failed")


def get_window_rect(hwnd: int) -> tuple[int, int, int, int]:
    try:
        """Return (left, top, right, bottom) for the given window."""
        return win32gui.GetWindowRect(hwnd)
    except:
        print("get_window_rect failed")

def move_window(hwnd: int, x: int, y: int, width: int | None = None, height: int | None = None):
    try:
        """Move a window to (x, y), optionally resizing it."""
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        w = width  if width  is not None else right  - left
        h = height if height is not None else bottom - top
        win32gui.MoveWindow(hwnd, x, y, w, h, True)
    except:
        print("move_window failed")
    


def drag_window(hwnd: int, delta_x: int, delta_y: int):
    try:
        """Shift a window by delta_x, delta_y pixels."""
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        move_window(hwnd, left + delta_x, top + delta_y)
    except:
        print("drag_window failed")


def is_process_running(process_name: str) -> bool:
    """Return True if any process whose name contains *process_name* is running."""
    name_lower = process_name.lower()
    for proc in psutil.process_iter(["name"]):
        try:
            if name_lower in proc.info["name"].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def get_foreground_process_name() -> str:
    try:
        """Return the process name of the currently focused window."""
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return ""
        return _process_name(_get_pid(hwnd))
    except:
        print("get_foreground_process_name failed")


def focus_window(hwnd: int):
    """Bring a window to the foreground."""
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        print("focus_window failed")