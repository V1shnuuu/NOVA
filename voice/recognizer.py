"""
JARVIS WorkMode v3 — Command Recognizer
After wake word fires, records a short audio clip and transcribes it
using vosk (fully offline). Returns the recognized text string.
"""

from __future__ import annotations

import json

from utils.logger import get_logger

logger = get_logger("jarvis.voice.recognizer")

SAMPLE_RATE = 16000

try:
    import pyaudio
    from vosk import KaldiRecognizer, Model
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("vosk/pyaudio not installed — voice recognition disabled.")


class CommandRecognizer:
    """Records from mic for N seconds and returns transcribed text."""

    def __init__(self, model_path: str = "assets/vosk-model") -> None:
        self.model = None
        if VOSK_AVAILABLE:
            try:
                self.model = Model(model_path)
                logger.info("Vosk model loaded for command recognition.")
            except Exception as exc:
                logger.error(f"Vosk model load failed: {exc}")

    def listen_for_command(self, duration_seconds: float = 5.0) -> str:
        """Blocking: record *duration_seconds* of audio and return text."""
        if self.model is None:
            return ""

        try:
            rec = KaldiRecognizer(self.model, SAMPLE_RATE)
            mic = pyaudio.PyAudio()
            stream = mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=4096,
            )
            stream.start_stream()

            frames_needed = int(SAMPLE_RATE * duration_seconds / 4096) + 1
            for _ in range(frames_needed):
                data = stream.read(4096, exception_on_overflow=False)
                rec.AcceptWaveform(data)

            stream.stop_stream()
            stream.close()
            mic.terminate()

            result = json.loads(rec.FinalResult())
            text = result.get("text", "").lower().strip()
            logger.info(f"Recognized command: '{text}'")
            return text

        except Exception as exc:
            logger.error(f"Command recognition error: {exc}")
            return ""
