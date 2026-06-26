# config.py — All tunable constants for MiniKasper
# Change values here to tune behavior without touching other code.

import os
import utils
# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR  = utils.get_asset_path("assets")
SOUNDS_DIR  = utils.get_asset_path("sounds")
QUOTES_FILE = utils.get_asset_path("quotes.json")

# ── Movement ─────────────────────────────────────────────────────────────────
WALK_SPEED       = 3          # pixels moved per movement tick
MOVEMENT_TICK_MS = 16         # ms between movement updates (~60 fps)

# Idle: how long before the mascot picks a new destination
IDLE_MIN_SEC = 2.0
IDLE_MAX_SEC = 6.0

# ── Animation ────────────────────────────────────────────────────────────────
ANIMATION_SPEED_MS = 150      # ms per animation frame

# ── Sleep ────────────────────────────────────────────────────────────────────
SLEEP_IDLE_THRESHOLD_SEC = 300   # seconds idle before sleep is considered
SLEEP_CHANCE             = 0.25  # probability per check of falling asleep

# ── Speech Bubbles ───────────────────────────────────────────────────────────
SHOW_SPEECH_TIME_SEC = 4.0    # seconds a speech bubble stays visible

# ── Sound ────────────────────────────────────────────────────────────────────
MASTER_VOLUME    = 0.8        # 0.0 – 1.0
FOOTSTEP_VOLUME  = 0.4        # relative to master
PITCH_VARIANCE   = 0.08       # max ±fraction applied to playback speed

# ── Scheduler ────────────────────────────────────────────────────────────────
SCHEDULER_TICK_SEC  = 30      # how often the scheduler checks for pranks

# Probability per scheduler tick that each prank fires
VSCODE_PRANK_CHANCE    = 0.15
GOOGLE_SEARCH_CHANCE   = 0.20
WINDOW_DRAG_CHANCE     = 0.12
ALMOST_LEAVING_CHANCE  = 0.017  # ~1 % per minute at 30-s ticks

# ── Sprite size (pixels) ─────────────────────────────────────────────────────
SPRITE_SCALE = 0.4            # multiply raw sprite pixels by this factor