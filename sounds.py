# sounds.py — Sound effect loading and playback for MiniKasper

import os
import random
import pygame.mixer as mixer
import config


class SoundPlayer:
    """Loads all .mp3 assets and exposes simple play() methods."""

    def __init__(self):
        mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        mixer.init()

        self._sounds: dict[str, mixer.Sound] = {}
        self._load_all()

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_all(self):
        files = {
            "click":      "click.mp3",
            "footstep1":  "footstep1.mp3",
            "footstep2":  "footstep2.mp3",
            "footstep3":  "footstep3.mp3",
            "nom":        "nom.mp3",
            "yip":        "yip.mp3",
            "sleep":      "sleep.mp3",
        }
        for key, fname in files.items():
            path = os.path.join(config.SOUNDS_DIR, fname)
            if os.path.isfile(path):
                snd = mixer.Sound(path)
                snd.set_volume(config.MASTER_VOLUME)
                self._sounds[key] = snd
            # Silently skip missing files so the app still runs without assets

    # ── Public API ────────────────────────────────────────────────────────────

    def play(self, name: str, volume_multiplier: float = 1.0):
        """Play a named sound effect (non-blocking)."""
        snd = self._sounds.get(name)
        if snd is None:
            return
        vol = config.MASTER_VOLUME * volume_multiplier
        snd.set_volume(min(1.0, max(0.0, vol)))
        snd.play()

    def play_footstep(self):
        """Play a random footstep sound at the configured footstep volume."""
        choices = ["footstep1", "footstep2", "footstep3"]
        available = [c for c in choices if c in self._sounds]
        if available:
            self.play(random.choice(available), config.FOOTSTEP_VOLUME)

    def play_loop(self, name: str):
        """Play a sound on infinite loop (e.g. snoring)."""
        snd = self._sounds.get(name)
        if snd:
            snd.set_volume(config.MASTER_VOLUME)
            snd.play(loops=-1)

    def stop(self, name: str):
        """Stop a specific looping sound."""
        snd = self._sounds.get(name)
        if snd:
            snd.stop()

    def stop_all(self):
        mixer.stop()