# sounds.py — Sound effect loading and playback for MiniKasper

import os
import random
import pygame.mixer as mixer
import config


class SoundPlayer:
    """Loads all .mp3 assets and exposes simple play() methods."""

    def __init__(self):
        try:
            mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            mixer.init()

            self._sounds: dict[str, mixer.Sound] = {}
            self._load_all()
        except Exception as e:
            print("SoundPlayer.__init__ failed", e)

    # ── Loading ───────────────────────────────────────────────────────────────

    def _load_all(self):
        try:
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

        except Exception as e:
            print("SoundPlayer._load_all failed", e)

    # ── Public API ────────────────────────────────────────────────────────────

    def play(self, name: str, volume_multiplier: float = 1.0):
        """Play a named sound effect (non-blocking)."""
        try:
            snd = self._sounds.get(name)
            if snd is None:
                return
            vol = config.MASTER_VOLUME * volume_multiplier
            snd.set_volume(min(1.0, max(0.0, vol)))
            snd.play()
        except Exception as e:
            print("SoundPlayer.play failed", e)

    def play_footstep(self):
        """Play a random footstep sound at the configured footstep volume."""
        try:
            choices = ["footstep1", "footstep2", "footstep3"]
            available = [c for c in choices if c in self._sounds]
            if available:
                self.play(random.choice(available), config.FOOTSTEP_VOLUME)
        except Exception as e:
            print("SoundPlayer.play_footstep failed", e)

    def play_loop(self, name: str):
        """Play a sound on infinite loop (e.g. snoring)."""
        try:
            snd = self._sounds.get(name)
            if snd:
                snd.set_volume(config.MASTER_VOLUME)
                snd.play(loops=-1)
        except Exception as e:
            print("SoundPlayer.play_loop failed", e)

    def stop(self, name: str):
        """Stop a specific looping sound."""
        try:
            snd = self._sounds.get(name)
            if snd:
                snd.stop()
        except Exception as e:
            print("SoundPlayer.stop failed", e)

    def stop_all(self):
        try:
            mixer.stop()
        except Exception as e:
            print("SoundPlayer.stop_all failed", e)