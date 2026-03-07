"""
JARVIS WorkMode v3 — Wake Word Detector
Continuously listens for 'JARVIS' in the mic stream using vosk.
Fires a callback when the wake word is detected.
"""

from __future__ import annotations

import json
import threading

from utils.logger import get_logger

logger = get_logger("jarvis.voice.wake_word")

SAMPLE_RATE = 16000

try:
    import pyaudio
    from vosk import KaldiRecognizer, Model
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("vosk/pyaudio not installed — wake word detection disabled.")


class WakeWordDetector:
    """Background thread that continuously listens for the wake word."""

    def __init__(
        self,
        on_wake: callable,
        wake_word: str = "jarvis",
        model_path: str = "assets/vosk-model",
    ) -> None:
        self.on_wake = on_wake
        self.wake_word = wake_word.lower()
        self._running = False
        self._thread: threading.Thread | None = None
        self.model = None

        if VOSK_AVAILABLE:
            try:
                self.model = Model(model_path)
                logger.info("Vosk model loaded for wake word detection.")
            except Exception as exc:
                logger.error(f"Vosk model load failed: {exc}")

    def start(self) -> None:
        if self.model is None:
            logger.warning("Wake word detector cannot start — no model.")
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="WakeWordThread",
        )
        self._thread.start()
        logger.info(f"Wake word detector started (word='{self.wake_word}').")

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        logger.info("Wake word detector stopped.")

    def _listen_loop(self) -> None:
        try:
            rec = KaldiRecognizer(self.model, SAMPLE_RATE)
            mic = pyaudio.PyAudio()
            stream = mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=8192,
            )
            stream.start_stream()

            while self._running:
                data = stream.read(4096, exception_on_overflow=False)
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").lower()
                    if self.wake_word in text:
                        logger.info("🎤 Wake word detected!")
                        self.on_wake()

                # Also check partial results for faster response
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "").lower()
                if self.wake_word in partial_text:
                    logger.info("🎤 Wake word detected (partial)!")
                    rec.Reset()
                    self.on_wake()

            stream.stop_stream()
            stream.close()
            mic.terminate()

        except Exception as exc:
            logger.error(f"Wake word listener error: {exc}")
            self._running = False
