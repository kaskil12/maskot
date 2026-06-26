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
            speech_controller.say("Åpner dokument 👀")

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


# ── Targeted Window Drag Prank ────────────────────────────────────────────────

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

        # Restore if dragged completely offscreen
        if left < -_OFFSCREEN_LIMIT or right > screen_w + _OFFSCREEN_LIMIT:
            safe_x = max(0, min(screen_w - win_w, left))
            safe_y = max(0, min(screen_h - win_h, top))

            if on_drag_anim:
                on_drag_anim("right" if left < 0 else "left")

            if speech_controller:
                speech_controller.say("Kom hit! 😤")

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
            on_drag_anim(direction)

        if speech_controller:
            speech_controller.say("*yip*")

        time.sleep(0.2)
        window_control.drag_window(hwnd, delta_x, 0)
        time.sleep(0.4)
        window_control.drag_window(hwnd, -delta_x, 0)

        return True

    except Exception as e:
        print("prank_drag_window failed", e)
        return False


# ── Random Chaos Window Drag Prank ────────────────────────────────────────────

def prank_drag_random_window(on_drag_anim=None, speech_controller=None):
    """
    Finds a completely random open visible window on the user's desktop 
    and gives it an unexpected shove.
    """
    try:
        visible_windows = []

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                # Filter out empty titles, taskbar elements, and desktop roots
                if title and title not in ["Program Manager", "Start", "Taskbar"]:
                    left, top, right, bottom = window_control.get_window_rect(hwnd)
                    # Ensure it has a physical presence on screen
                    if (right - left) > 150 and (bottom - top) > 150:
                        visible_windows.append(hwnd)

        win32gui.EnumWindows(enum_windows_callback, None)

        if not visible_windows:
            return False

        # Pick a window entirely at random
        random_hwnd = random.choice(visible_windows)
        
        # Decide direction
        direction = random.choice(["left", "right"])
        delta_x = -70 if direction == "left" else 70

        if on_drag_anim:
            on_drag_anim(direction)

        if speech_controller:
            speech_controller.say(random.choice([
                "Denne skal stå her! 🚚",
                "Flytter på ting! 📦",
                "Hoppsann! 😮",
                "Litt til venstre... nei høyre! 📐"
            ]))

        time.sleep(0.2)
        # Give it a shove, pause, and drop it
        window_control.drag_window(random_hwnd, delta_x, 20)
        time.sleep(0.3)
        window_control.drag_window(random_hwnd, int(delta_x * 0.5), -10)

        return True

    except Exception as e:
        print("prank_drag_random_window failed", e)
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