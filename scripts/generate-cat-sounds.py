"""Generate three short, gentle and original cat-like vocal sounds."""

from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np


SAMPLE_RATE = 44_100
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "sounds"


def smooth_curve(points: list[tuple[float, float]], time: np.ndarray) -> np.ndarray:
    x = np.array([point[0] for point in points], dtype=np.float64)
    y = np.array([point[1] for point in points], dtype=np.float64)
    return np.interp(time, x, y)


def make_meow(
    filename: str,
    duration: float,
    pitch_points: list[tuple[float, float]],
    brightness: float,
    vibrato: float,
) -> None:
    count = int(duration * SAMPLE_RATE)
    time = np.arange(count, dtype=np.float64) / SAMPLE_RATE
    frequency = smooth_curve(pitch_points, time)
    frequency *= 1 + vibrato * np.sin(2 * np.pi * (5.2 + brightness) * time)
    phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE

    attack = np.minimum(1.0, time / 0.055)
    release = np.minimum(1.0, (duration - time) / 0.18)
    breath = np.sin(np.pi * np.clip(time / duration, 0, 1)) ** 0.55
    envelope = np.maximum(0.0, np.minimum(attack, release)) * breath

    voice = (
        np.sin(phase)
        + (0.50 + brightness * 0.06) * np.sin(phase * 2 + 0.18)
        + 0.22 * np.sin(phase * 3 + 0.35)
        + 0.08 * np.sin(phase * 5 + 0.2)
    )
    rng = np.random.default_rng(sum((index + 1) * ord(char) for index, char in enumerate(filename)))
    airy = rng.normal(0, 1, count)
    airy = np.convolve(airy, np.ones(7) / 7, mode="same")
    mono = (voice * 0.19 + airy * 0.012) * envelope

    delay = int(0.035 * SAMPLE_RATE)
    right = mono.copy()
    right[delay:] += mono[:-delay] * 0.12
    left = mono * 0.98
    stereo = np.column_stack((left, right))
    stereo /= max(1.0, np.max(np.abs(stereo)) / 0.72)
    pcm = (stereo * 32767).astype(np.int16)

    with wave.open(str(OUTPUT_DIR / filename), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(SAMPLE_RATE)
        audio.writeframes(pcm.tobytes())


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    make_meow(
        "cat-meow-soft.wav",
        0.92,
        [(0.0, 460), (0.18, 610), (0.48, 760), (0.72, 560), (0.92, 430)],
        0.7,
        0.012,
    )
    make_meow(
        "cat-meow-curious.wav",
        1.08,
        [(0.0, 390), (0.2, 520), (0.58, 690), (0.82, 720), (1.08, 470)],
        1.2,
        0.016,
    )
    make_meow(
        "cat-chirp.wav",
        0.58,
        [(0.0, 620), (0.12, 900), (0.25, 720), (0.38, 980), (0.58, 680)],
        1.6,
        0.022,
    )
    print(f"Created 3 cat sounds in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
