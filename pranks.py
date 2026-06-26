# pranks.py — All random prank behaviors for MiniKasper

import random
import time
import webbrowser
import pyautogui
import win32gui
import window_control
from PySide6.QtCore import QTimer


def run_in_main_thread(func):
    try:
        QTimer.singleShot(0, func)
    except Exception as e:
        print("run_in_main_thread failed", e)


# ── Google Search Prank ───────────────────────────────────────────────────────

_GOOGLE_QUERIES = [
    "hvordan erstatte verdens beste lærling",
    "hvor mye kaffe er for mye",
    "hvorfor virker printere aldri",
    "kan man leve på energidrikk",
    "hvorfor er det alltid DNS",
    "hvordan late som man jobber",
    "hva gjør en IT-tekniker egentlig",
    "hvordan overleve uten lærling",
    "er det normalt å savne lærlingen sin",
    "gratis IT-support etter lærlingtid",
    "hva gjør jeg nå som lærlingen dro",
]


def prank_google_search(speech_controller=None):
    try:
        query = random.choice(_GOOGLE_QUERIES)
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open_new_tab(url)

        if speech_controller:
            speech_controller.say("Søker litt... 🔍")

    except Exception as e:
        print("prank_google_search failed", e)


# ── VS Code Typing Prank ──────────────────────────────────────────────────────

_VSCODE_MESSAGES = [
    'print("Hei, sjef! 😄")',
    '# TODO: finn en ny lærling',
    'print("Alt er DNS.")',
    '# Jeg var her. - Kasper',
    'print("Husk å lagre! 💾")',
]


def prank_vscode_type(speech_controller=None):
    try:
        fg = window_control.get_foreground_process_name().lower()

        if "code" not in fg:
            return False

        if speech_controller:
            run_in_main_thread(lambda: speech_controller.say("Åpner dokument 👀"))

        pyautogui.hotkey("ctrl", "n")
        time.sleep(0.3)

        message = random.choice(_VSCODE_MESSAGES)

        pyautogui.typewrite(message, interval=0.04)

        time.sleep(0.2)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")

        return True

    except Exception as e:
        print("prank_vscode_type failed", e)
        return False


# ── Window Drag Prank ─────────────────────────────────────────────────────────

_DRAG_TARGETS = ["explorer", "notepad", "mspaint", "calc", "wordpad"]

_DRAG_AMOUNT = 120
_OFFSCREEN_LIMIT = 40


def safe_drag(hwnd, dx, dy):
    try:
        window_control.drag_window(hwnd, dx, dy)
        return True
    except Exception as e:
        print("safe_drag failed", e)
        return False


def prank_drag_window(on_drag_anim=None, speech_controller=None):
    try:
        import ctypes

        SM_CXSCREEN = 0
        SM_CYSCREEN = 1

        screen_w = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
        screen_h = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

        hwnd = None

        for target in _DRAG_TARGETS:
            hwnd = window_control.find_window_by_process(target)
            if hwnd:
                break

        if not hwnd:
            return False

        left, top, right, bottom = window_control.get_window_rect(hwnd)

        win_w = right - left
        win_h = bottom - top

        # restore if offscreen
        if left < -_OFFSCREEN_LIMIT or right > screen_w + _OFFSCREEN_LIMIT:

            safe_x = max(0, min(screen_w - win_w, left))
            safe_y = max(0, min(screen_h - win_h, top))

            if on_drag_anim:
                run_in_main_thread(lambda: on_drag_anim("right" if left < 0 else "left"))

            if speech_controller:
                run_in_main_thread(lambda: speech_controller.say("Kom hit! 😤"))

            window_control.move_window(hwnd, safe_x, safe_y)
            return True

        dist_left = left
        dist_right = screen_w - right

        if dist_left < dist_right:
            direction = "left"
            delta_x = -min(_DRAG_AMOUNT, dist_left + _OFFSCREEN_LIMIT)
        else:
            direction = "right"
            delta_x = min(_DRAG_AMOUNT, dist_right + _OFFSCREEN_LIMIT)

        if on_drag_anim:
            run_in_main_thread(lambda: on_drag_anim(direction))

        if speech_controller:
            run_in_main_thread(lambda: speech_controller.say("*yip*"))

        time.sleep(0.2)

        window_control.drag_window(hwnd, delta_x, 0)
        time.sleep(0.4)
        window_control.drag_window(hwnd, -delta_x, 0)

        return True

    except Exception as e:
        print("prank_drag_window failed", e)
        return False


# ── Almost Leaving ────────────────────────────────────────────────────────────

ALMOST_LEAVING_QUOTES = [
    "...neh.",
    "Kanskje ikke.",
    "Egentlig ikke klar.",
    "Glemte noe.",
    "Hmm... nei.",
]


def get_almost_leaving_quote() -> str:
    try:
        return random.choice(ALMOST_LEAVING_QUOTES)
    except Exception as e:
        print("get_almost_leaving_quote failed", e)
        return "...neh."