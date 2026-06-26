# pranks.py — All random prank behaviors for MiniKasper

import random
import time
import webbrowser
import pyautogui
import win32gui
import window_control


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
    query = random.choice(_GOOGLE_QUERIES)
    url   = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open_new_tab(url)
    if speech_controller:
        speech_controller.say("Søker litt... 🔍")


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

        # mer robust sjekk
        if "code" not in fg and "vscode" not in fg:
            return False

        if speech_controller:
            speech_controller.say("Åpner nytt dokument 👀")

        # 🔥 sikrer editor fokus
        pyautogui.hotkey("ctrl", "n")
        time.sleep(0.5)

        message = random.choice(_VSCODE_MESSAGES)

        pyautogui.typewrite(message, interval=0.04)

        time.sleep(0.5)

        # cleanup (mer stabil enn home+shift+end)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")

        return True

    except Exception as e:
        print(f"Feil med vscode prank: {e}")
        return False


# ── Window Drag Prank ─────────────────────────────────────────────────────────

_DRAG_TARGETS = ["explorer", "notepad", "mspaint", "calc", "wordpad"]

# How many pixels to drag the window, and how far off-screen before we pull it back
_DRAG_AMOUNT     = 120
_OFFSCREEN_LIMIT = 40   # window edge must be at least this many px on screen


def prank_drag_window(on_drag_anim=None, speech_controller=None):
    """
    Find an open window and drag it toward the nearest screen edge, then
    drag it back. If the window is already partially off-screen, we pull
    it back into view instead.
    """
    import ctypes
    SM_CXSCREEN = 0
    SM_CYSCREEN = 1
    screen_w = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
    screen_h = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)

    for target in _DRAG_TARGETS:
        hwnd = window_control.find_window_by_process(target)
        if not hwnd:
            continue

        left, top, right, bottom = window_control.get_window_rect(hwnd)
        win_w = right  - left
        win_h = bottom - top

        # Is the window already hanging off a screen edge? Pull it back.
        if left < -_OFFSCREEN_LIMIT or right > screen_w + _OFFSCREEN_LIMIT:
            safe_x = max(0, min(screen_w - win_w, left))
            safe_y = max(0, min(screen_h - win_h, top))
            if on_drag_anim:
                direction = "right" if left < 0 else "left"
                on_drag_anim(direction)
            if speech_controller:
                speech_controller.say("Kom hit! 😤")
            time.sleep(0.3)
            window_control.move_window(hwnd, safe_x, safe_y)
            return True

        # Pick the closer horizontal edge and drag toward it
        dist_left  = left
        dist_right = screen_w - right
        if dist_left < dist_right:
            direction = "left"
            delta_x   = -min(_DRAG_AMOUNT, dist_left + _OFFSCREEN_LIMIT)
        else:
            direction = "right"
            delta_x   = min(_DRAG_AMOUNT, dist_right + _OFFSCREEN_LIMIT)

        if on_drag_anim:
            on_drag_anim(direction)
        if speech_controller:
            speech_controller.say("*yip*")

        time.sleep(0.4)
        window_control.drag_window(hwnd, delta_x, 0)
        time.sleep(1.0)
        # Drag back to original position
        window_control.drag_window(hwnd, -delta_x, 0)
        return True

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
    return random.choice(ALMOST_LEAVING_QUOTES)