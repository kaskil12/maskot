# pranks.py — All random prank behaviors for MiniKasper

import random
import time
import webbrowser
import pyautogui
import win32gui
import win32con
import winsound
import window_control

# ── Helper for Smooth Dragging ────────────────────────────────────────────────

def _force_move_window(hwnd, x, y):
    """Bypasses window_control and forces the OS to move and redraw the window."""
    win32gui.SetWindowPos(
        hwnd, 0, x, y, 0, 0, 
        win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_SHOWWINDOW
    )

def _smooth_sweep(hwnd, start_x, start_y, delta_x, delta_y, duration=1.5, set_mascot_pos_cb=None, mascot_offset_x=0, mascot_offset_y=0):
    """
    Gradually moves a window over a set duration to create a smooth dragging effect.
    If a mascot position callback is provided, the mascot runs alongside the window.
    """
    steps = 60
    sleep_time = duration / steps
    
    for i in range(1, steps + 1):
        curr_x = int(start_x + (delta_x * (i / steps)))
        curr_y = int(start_y + (delta_y * (i / steps)))
        
        _force_move_window(hwnd, curr_x, curr_y)
        
        if set_mascot_pos_cb:
            set_mascot_pos_cb(curr_x + mascot_offset_x, curr_y + mascot_offset_y)
            
        time.sleep(sleep_time)


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
]

def prank_google_search(speech_controller=None, **kwargs):
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
]

def prank_vscode_type(speech_controller=None, **kwargs):
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
_DRAG_AMOUNT = 450  
_OFFSCREEN_LIMIT = 40

def prank_drag_window(on_drag_anim=None, speech_controller=None, **kwargs):
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
        
        # Check for mascot callbacks to walk to the window
        walk_cb = kwargs.get("walk_cb")
        get_pos_cb = kwargs.get("get_pos_cb")
        set_pos_cb = kwargs.get("set_pos_cb")

        dist_left = left
        dist_right = screen_w - right

        if dist_left < dist_right:
            direction = "left"
            delta_x = -min(_DRAG_AMOUNT, dist_left + _OFFSCREEN_LIMIT)
            target_mascot_x = right
        else:
            direction = "right"
            delta_x = min(_DRAG_AMOUNT, dist_right + _OFFSCREEN_LIMIT)
            target_mascot_x = left - 30  # Stand slightly to the left of the window

        # Walk to the window if callbacks are provided
        if walk_cb and get_pos_cb:
            walk_cb(target_mascot_x, top + 20)
            if speech_controller:
                speech_controller.say("Skal bare låne denne... 🏃‍♂️")
            
            # Wait for mascot to arrive (timeout after 6 seconds)
            start_wait = time.time()
            while time.time() - start_wait < 6.0:
                mx, my = get_pos_cb()
                if abs(mx - target_mascot_x) < 30 and abs(my - (top + 20)) < 30:
                    break
                time.sleep(0.2)

        if on_drag_anim:
            on_drag_anim(direction)

        if speech_controller:
            speech_controller.say("*yip*")

        time.sleep(0.1)
        
        # Offset to keep the mascot glued to the window edge during the sweep
        offset_x = (target_mascot_x - left)
        offset_y = 20

        _smooth_sweep(hwnd, left, top, delta_x, 0, duration=1.5, 
                      set_mascot_pos_cb=set_pos_cb, 
                      mascot_offset_x=offset_x, mascot_offset_y=offset_y)

        return True

    except Exception as e:
        print("prank_drag_window failed", e)
        return False


# ── Random Chaos Window Drag Prank ────────────────────────────────────────────

def prank_drag_random_window(on_drag_anim=None, speech_controller=None, **kwargs):
    """
    Finds a random open visible window, walks up to its edge, and runs across the screen with it.
    """
    try:
        visible_windows = []

        def enum_windows_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title not in ["Program Manager", "Start", "Taskbar"]:
                    left, top, right, bottom = window_control.get_window_rect(hwnd)
                    if (right - left) > 150 and (bottom - top) > 150:
                        visible_windows.append(hwnd)

        win32gui.EnumWindows(enum_windows_callback, None)

        if not visible_windows:
            return False

        random_hwnd = random.choice(visible_windows)
        left, top, right, bottom = window_control.get_window_rect(random_hwnd)
        
        direction = random.choice(["left", "right"])
        delta_x = -400 if direction == "left" else 400
        delta_y = random.choice([-50, 0, 50])

        target_mascot_x = right if direction == "left" else (left - 30)

        walk_cb = kwargs.get("walk_cb")
        get_pos_cb = kwargs.get("get_pos_cb")
        set_pos_cb = kwargs.get("set_pos_cb")

        # Mascot runs to the edge of the chosen window
        if walk_cb and get_pos_cb:
            walk_cb(target_mascot_x, top + 20)
            if speech_controller:
                speech_controller.say("Denne står i veien! 🚚")
            
            start_wait = time.time()
            while time.time() - start_wait < 6.0:
                mx, my = get_pos_cb()
                if abs(mx - target_mascot_x) < 30 and abs(my - (top + 20)) < 30:
                    break
                time.sleep(0.2)

        if on_drag_anim:
            on_drag_anim(direction)

        if speech_controller:
            speech_controller.say(random.choice([
                "Flytter på ting! 📦",
                "Hoppsann! 😮",
                "Ryddetid! 🧹"
            ]))

        time.sleep(0.1)
        
        offset_x = (target_mascot_x - left)
        offset_y = 20

        _smooth_sweep(random_hwnd, left, top, delta_x, delta_y, duration=1.5,
                      set_mascot_pos_cb=set_pos_cb,
                      mascot_offset_x=offset_x, mascot_offset_y=offset_y)

        return True

    except Exception as e:
        print("prank_drag_random_window failed", e)
        return False


# ── Pause and Minimize All Prank (NEW) ────────────────────────────────────────

def prank_pause_and_minimize(speech_controller=None, **kwargs):
    """
    Yells "PAUSE!" and instantly minimizes every application on the desktop.
    """
    try:
        if speech_controller:
            speech_controller.say("PAUSE! 🛑")
            
        time.sleep(1.2) # Give them a second to read the bubble and panic
        pyautogui.hotkey('win', 'm')
        
        return True
    except Exception as e:
        print("prank_pause_and_minimize failed", e)
        return False


# ── Ghost Scroll Prank (NEW) ──────────────────────────────────────────────────

def prank_ghost_scroll(speech_controller=None, **kwargs):
    """
    Unexpectedly scrolls the user's mouse wheel down.
    """
    try:
        if speech_controller:
            speech_controller.say("Litt lenger ned... 📜")
            
        time.sleep(0.8)
        pyautogui.scroll(-600) # Negative is scrolling down
        
        return True
    except Exception as e:
        print("prank_ghost_scroll failed", e)
        return False


# ── Caps Lock Prank (NEW) ─────────────────────────────────────────────────────

def prank_caps_lock(speech_controller=None, **kwargs):
    """
    Turns on Caps Lock when the user least expects it.
    """
    try:
        pyautogui.press('capslock')
        
        if speech_controller:
            speech_controller.say("SÅNN, MYE BEDRE! 🔠")
            
        return True
    except Exception as e:
        print("prank_caps_lock failed", e)
        return False


# ── Fake Error Sound Prank ────────────────────────────────────────────────────

def prank_fake_error_sound(speech_controller=None, **kwargs):
    """
    Plays the standard Windows critical error sound.
    """
    try:
        winsound.MessageBeep(winsound.MB_ICONHAND)
        if speech_controller:
            speech_controller.say("Det der hørtes ikke bra ut... 😬")
        return True
    except Exception as e:
        print("prank_fake_error_sound failed", e)
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