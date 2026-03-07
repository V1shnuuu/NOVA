"""
JARVIS WorkMode v3 — Text-to-Speech Engine
Offline TTS via pyttsx3 with JARVIS personality voice.
Prefers 'Microsoft David' (male, authoritative).
"""

from __future__ import annotations

import threading

import pyttsx3

from utils.logger import get_logger

logger = get_logger("jarvis.voice.speaker")


class JarvisSpeaker:
    """Thread-safe offline text-to-speech engine."""

    def __init__(self, config) -> None:
        self.config = config
        self.engine = pyttsx3.init()
        self._lock = threading.Lock()
        self._configure_voice()

    def _configure_voice(self) -> None:
        voices = self.engine.getProperty("voices")
        # Prefer male voice for JARVIS feel
        for voice in voices:
            name_lower = voice.name.lower()
            if "david" in name_lower or "male" in name_lower:
                self.engine.setProperty("voice", voice.id)
                logger.info(f"Voice selected: {voice.name}")
                break
        else:
            if voices:
                self.engine.setProperty("voice", voices[0].id)
                logger.info(f"Voice fallback: {voices[0].name}")

        self.engine.setProperty("rate", self.config.voice_rate)
        self.engine.setProperty("volume", self.config.voice_volume)

    def speak(self, text: str, blocking: bool = False) -> None:
        """Speak *text*. Non-blocking by default (runs in daemon thread)."""

        def _say() -> None:
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()

        logger.debug(f'Speaking: "{text}"')
        if blocking:
            _say()
        else:
            threading.Thread(target=_say, daemon=True).start()

    def stop(self) -> None:
        try:
            self.engine.stop()
        except Exception:
            pass
