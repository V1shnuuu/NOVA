"""
JARVIS WorkMode v3 — Activation Chime Generator
Programmatically creates a short futuristic chime WAV file.
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("jarvis.voice.chime")

CHIME_PATH = Path(__file__).parent / "assets" / "chime.wav"


def ensure_chime() -> Path:
    """Generate the chime WAV if it doesn't exist. Returns the path."""
    if CHIME_PATH.exists():
        return CHIME_PATH

    CHIME_PATH.parent.mkdir(parents=True, exist_ok=True)
    _generate_chime(CHIME_PATH)
    logger.info(f"Activation chime generated: {CHIME_PATH}")
    return CHIME_PATH


def _generate_chime(path: Path) -> None:
    """Create a short futuristic two-tone ascending chime."""
    sample_rate = 44100
    duration = 0.35  # seconds per tone
    volume = 0.4

    # Two ascending tones for a sci-fi 'beep-boop' feel
    frequencies = [880, 1320]  # A5 → E6
    samples: list[int] = []

    for freq in frequencies:
        n_samples = int(sample_rate * duration)
        for i in range(n_samples):
            t = i / sample_rate
            # Envelope: quick attack, smooth decay
            envelope = max(0.0, 1.0 - (t / duration) ** 0.5)
            # Main tone + subtle harmonic
            val = (
                math.sin(2 * math.pi * freq * t)
                + 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            )
            sample = int(val * envelope * volume * 32767)
            sample = max(-32768, min(32767, sample))
            samples.append(sample)

        # Tiny gap between tones
        gap = int(sample_rate * 0.04)
        samples.extend([0] * gap)

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
