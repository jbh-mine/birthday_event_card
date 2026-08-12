"""Generate the photo-free 60-second birthday film and its original soundtrack."""

from __future__ import annotations

import math
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 540, 960
FPS = 24
DURATION = 60
SAMPLE_RATE = 44_100

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "birthday-film.mp4"
POSTER = ROOT / "public" / "birthday-film-poster.jpg"
FONT_REGULAR = Path(r"C:\Windows\Fonts\malgun.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\malgunbd.ttf")

SCENES = [
    (0, 7, "FORTY YEARS AGO", ["한 사람이", "세상에 태어났습니다"], "그날부터 세상은 조금 더 따뜻해졌어요"),
    (7, 15, "FORTY SEASONS", ["그리고 마흔 번의", "계절을 지나"], "웃고, 울고, 사랑하며 여기까지 온 당신"),
    (15, 24, "THE HEART OF HOME", ["누군가의 가장 다정한 사람", "한 가족의 따뜻한 중심"], "당신이 있는 곳은 언제나 집이 되었습니다"),
    (24, 33, "EVERY ORDINARY DAY", ["평범한 하루를", "특별하게 만들고"], "작은 순간마다 오래 남을 온기를 건네주었어요"),
    (33, 42, "ALWAYS ON MY SIDE", ["수많은 순간에", "내 편이 되어준 당신"], "기쁜 날에도, 힘든 날에도 가장 가까운 곳에서"),
    (42, 51, "A BEAUTIFUL NEXT CHAPTER", ["이제 당신의", "가장 아름다운 다음 장이", "시작됩니다"], "마흔은 끝이 아니라 더 눈부신 계절의 시작이니까"),
    (51, 60, "FORTY & FOREVER", ["태어나줘서 고마워요", "생일 축하해요"], "나의 가장 아름다운 사람"),
]

PALETTES = [
    ((92, 25, 61), (201, 132, 88)),
    ((80, 32, 100), (236, 178, 91)),
    ((29, 65, 83), (193, 111, 106)),
    ((90, 38, 52), (222, 156, 87)),
    ((43, 46, 104), (198, 92, 120)),
    ((39, 69, 82), (226, 164, 90)),
    ((110, 31, 67), (248, 194, 104)),
]


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep(value: float) -> float:
    value = clamp01(value)
    return value * value * (3 - 2 * value)


def scene_opacity(time_s: float, start: float, end: float) -> float:
    fade_in = smoothstep((time_s - start) / 1.35)
    fade_out = smoothstep((end - time_s) / 1.2)
    return min(fade_in, fade_out)


@lru_cache(maxsize=None)
def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


@lru_cache(maxsize=1)
def vignette_shade() -> Image.Image:
    vignette = Image.new("L", (WIDTH, HEIGHT), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.ellipse((-210, -120, WIDTH + 210, HEIGHT + 150), fill=210)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120))
    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 110))
    shade.putalpha(Image.eval(vignette, lambda value: 210 - value))
    return shade


def centered_text(draw: ImageDraw.ImageDraw, xy_y: int, text: str, text_font, fill, spacing=4):
    box = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=spacing, align="center")
    width = box[2] - box[0]
    draw.multiline_text(((WIDTH - width) / 2, xy_y), text, font=text_font, fill=fill, spacing=spacing, align="center")


def make_background(time_s: float, palette_index: int) -> Image.Image:
    small_w, small_h = 180, 320
    base = Image.new("RGB", (small_w, small_h), (9, 7, 14))
    glows = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glows)
    primary, secondary = PALETTES[palette_index]

    drift_x = math.sin(time_s * 0.15 + palette_index) * 34
    drift_y = math.cos(time_s * 0.12 + palette_index * 0.8) * 45
    x1 = 38 + drift_x
    y1 = 92 + drift_y
    x2 = 145 - drift_x * 0.55
    y2 = 245 - drift_y * 0.45

    draw.ellipse((x1 - 88, y1 - 110, x1 + 88, y1 + 110), fill=(*primary, 125))
    draw.ellipse((x2 - 92, y2 - 120, x2 + 92, y2 + 120), fill=(*secondary, 75))
    glows = glows.filter(ImageFilter.GaussianBlur(45))
    base = Image.alpha_composite(base.convert("RGBA"), glows)
    return base.resize((WIDTH, HEIGHT), Image.Resampling.BICUBIC)


def draw_particles(frame: Image.Image, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for index in range(44):
        x0 = (index * 127 + 43) % WIDTH
        y0 = (index * 211 + 79) % HEIGHT
        speed = 4.5 + (index % 7) * 0.9
        y = (y0 - time_s * speed) % (HEIGHT + 90) - 45
        x = x0 + math.sin(time_s * (0.2 + index % 4 * 0.035) + index) * (6 + index % 9)
        pulse = (math.sin(time_s * 1.2 + index * 1.71) + 1) / 2
        alpha = int(30 + pulse * 120)
        radius = 1 + (index % 3) * 0.55
        color = (248, 203, 125, alpha) if index % 3 else (234, 198, 219, alpha)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

    frame.alpha_composite(layer)


def draw_orbits(frame: Image.Image, time_s: float, opacity: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    alpha = int(38 * opacity)
    phase = (time_s * 6) % 360
    for inset in (62, 86, 114):
        box = (inset - 85, 235 + inset, WIDTH - inset + 85, 770 - inset)
        draw.arc(box, start=phase + inset, end=phase + inset + 132, fill=(247, 203, 127, alpha), width=1)
    frame.alpha_composite(layer)


def draw_scene(frame: Image.Image, time_s: float, scene_index: int) -> None:
    start, end, kicker, lines, subtitle = SCENES[scene_index]
    opacity = scene_opacity(time_s, start, end)
    if opacity <= 0:
        return

    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    local = clamp01((time_s - start) / (end - start))
    rise = int((1 - smoothstep(min(local / 0.25, 1))) * 22)

    kicker_font = font(FONT_REGULAR, 15)
    title_size = 50 if scene_index not in (2, 5) else 40
    if scene_index == 6:
        title_size = 48
    title_font = font(FONT_BOLD, title_size)
    subtitle_font = font(FONT_REGULAR, 20)

    title_text = "\n".join(lines)
    title_box = draw.multiline_textbbox((0, 0), title_text, font=title_font, spacing=15, align="center")
    title_height = title_box[3] - title_box[1]
    title_y = int(HEIGHT * 0.42 - title_height / 2 + rise)

    gold = (247, 202, 124, int(230 * opacity))
    ivory = (248, 241, 231, int(255 * opacity))
    soft = (221, 209, 210, int(205 * opacity))

    centered_text(draw, title_y - 92, kicker, kicker_font, gold)
    centered_text(draw, title_y, title_text, title_font, ivory, spacing=15)
    centered_text(draw, title_y + title_height + 60, subtitle, subtitle_font, soft)

    line_y = title_y - 56
    draw.line((WIDTH / 2 - 25, line_y, WIDTH / 2 + 25, line_y), fill=gold, width=1)

    if scene_index == 1:
        forty_font = font(FONT_BOLD, 280)
        forty_box = draw.textbbox((0, 0), "40", font=forty_font)
        forty_w = forty_box[2] - forty_box[0]
        draw.text(((WIDTH - forty_w) / 2, 540), "40", font=forty_font, fill=(255, 222, 153, int(18 * opacity)))

    if scene_index == 6:
        ring_alpha = int(85 * opacity)
        draw.ellipse((WIDTH / 2 - 128, 188, WIDTH / 2 + 128, 444), outline=(247, 202, 124, ring_alpha), width=1)
        draw.ellipse((WIDTH / 2 - 150, 166, WIDTH / 2 + 150, 466), outline=(247, 202, 124, int(ring_alpha * 0.4)), width=1)

    frame.alpha_composite(layer)


def render_frame(time_s: float) -> Image.Image:
    scene_index = min(len(SCENES) - 1, next((i for i, scene in enumerate(SCENES) if scene[0] <= time_s < scene[1]), len(SCENES) - 1))
    frame = make_background(time_s, scene_index)
    draw_particles(frame, time_s)
    draw_orbits(frame, time_s, 0.9)

    # Draw adjacent scenes too, which creates a soft cinematic cross-fade.
    for index in range(max(0, scene_index - 1), min(len(SCENES), scene_index + 2)):
        draw_scene(frame, time_s, index)

    frame.alpha_composite(vignette_shade())
    return frame.convert("RGB")


def add_tone(track: np.ndarray, frequency: float, start: float, length: float, amplitude: float, bell=False) -> None:
    start_index = int(start * SAMPLE_RATE)
    count = min(int(length * SAMPLE_RATE), len(track) - start_index)
    if count <= 0:
        return
    t = np.arange(count, dtype=np.float64) / SAMPLE_RATE
    if bell:
        envelope = np.exp(-t * 1.45) * np.minimum(1.0, t * 45)
        tone = (
            np.sin(2 * np.pi * frequency * t)
            + 0.38 * np.sin(2 * np.pi * frequency * 2.01 * t)
            + 0.18 * np.sin(2 * np.pi * frequency * 3.98 * t)
        )
    else:
        attack = np.minimum(1.0, t / 2.2)
        release = np.minimum(1.0, (length - t) / 2.7)
        envelope = np.maximum(0.0, np.minimum(attack, release))
        tone = np.sin(2 * np.pi * frequency * t) + 0.18 * np.sin(2 * np.pi * frequency * 2 * t)
    track[start_index:start_index + count] += tone * envelope * amplitude


def make_soundtrack(path: Path) -> None:
    total = DURATION * SAMPLE_RATE
    mono = np.zeros(total, dtype=np.float64)
    chords = [
        (130.81, 164.81, 196.00, 246.94),
        (110.00, 130.81, 164.81, 196.00),
        (87.31, 130.81, 164.81, 196.00),
        (98.00, 146.83, 196.00, 261.63),
        (82.41, 130.81, 164.81, 196.00),
        (87.31, 130.81, 174.61, 220.00),
        (98.00, 146.83, 196.00, 246.94),
        (130.81, 164.81, 196.00, 293.66),
    ]
    chord_length = 7.5
    for chord_index, chord in enumerate(chords):
        start = chord_index * chord_length
        for note_index, note in enumerate(chord):
            add_tone(mono, note, start, chord_length + 1.4, 0.033 if note_index else 0.045)

    melody_steps = [0, 2, 1, 3, 2, 1, 3, 0, 2, 3, 1, 2, 0, 3, 2, 1, 3, 2, 0, 3, 1, 2, 3, 0]
    for index, step in enumerate(melody_steps):
        start = 1.1 + index * 2.42
        chord = chords[min(int(start // chord_length), len(chords) - 1)]
        note = chord[step] * (2 if index % 5 else 1)
        add_tone(mono, note, start, 3.8, 0.11 if index < 20 else 0.14, bell=True)

    # Gentle sub pulse and a final pair of chimes.
    for start in np.arange(0, DURATION, 3.75):
        chord = chords[min(int(start // chord_length), len(chords) - 1)]
        add_tone(mono, chord[0] / 2, float(start), 3.2, 0.035)
    add_tone(mono, 523.25, 51.3, 6.0, 0.16, bell=True)
    add_tone(mono, 659.25, 54.0, 5.2, 0.13, bell=True)
    add_tone(mono, 783.99, 56.7, 3.1, 0.12, bell=True)

    # A light stereo echo gives the synthesized tones an intimate room feel.
    delay = int(0.31 * SAMPLE_RATE)
    left = mono.copy()
    right = mono.copy()
    left[delay:] += mono[:-delay] * 0.22
    right[int(delay * 1.23):] += mono[:-int(delay * 1.23)] * 0.25

    fade_in = np.minimum(1.0, np.arange(total) / (SAMPLE_RATE * 2.2))
    fade_out = np.minimum(1.0, np.arange(total)[::-1] / (SAMPLE_RATE * 3.0))
    stereo = np.column_stack((left, right)) * np.minimum(fade_in, fade_out)[:, None]
    stereo /= max(1.0, np.max(np.abs(stereo)) / 0.86)
    pcm = (stereo * 32767).astype(np.int16)

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())


def generate(ffmpeg: Path) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="birthday-film-") as temp_dir:
        audio_path = Path(temp_dir) / "soundtrack.wav"
        make_soundtrack(audio_path)

        command = [
            str(ffmpeg), "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", str(DURATION),
            str(OUTPUT),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        assert process.stdin is not None
        for frame_number in range(DURATION * FPS):
            frame = render_frame(frame_number / FPS)
            if frame_number == 0:
                render_frame(2.6).save(POSTER, quality=93, optimize=True)
            process.stdin.write(frame.tobytes())
            if frame_number % (FPS * 5) == 0:
                print(f"rendered {frame_number // FPS:02d}s / {DURATION}s", flush=True)
        process.stdin.close()
        return_code = process.wait()
        if return_code:
            raise SystemExit(return_code)

    print(f"created {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: generate-birthday-film.py <ffmpeg-path>")
    generate(Path(sys.argv[1]))
