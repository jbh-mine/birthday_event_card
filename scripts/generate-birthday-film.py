"""Render a photo-free 60-second 2.5D paper-cut birthday growth drama."""

from __future__ import annotations

import math
import os
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
    (0, 5, "PROLOGUE", "한 사람이\n세상에 왔습니다", "별 하나가 켜진 밤"),
    (5, 12, "1986 · THE FIRST SEASON", "아주 작은 숨결이\n세상을 따뜻하게 했어요", "첫 번째 계절"),
    (12, 20, "LITTLE STEPS", "작은 발걸음은\n수많은 계절을 건너", "웃고, 뛰고, 꿈꾸며"),
    (20, 28, "DREAMS & COURAGE", "꿈을 향해 달리고\n때로는 넘어지고", "그래도 다시 일어나"),
    (28, 38, "THE HEART OF HOME", "누군가의\n따뜻한 편이 되어", "평범한 하루를 특별하게 만들었어요"),
    (38, 47, "FORTY", "마흔, 여기까지\n참 잘 왔어요", "지나온 모든 당신이 빛나는 순간"),
    (47, 57, "THE NEXT SEASONS", "앞으로의 계절은\n더 눈부실 거예요", "천천히, 오래, 함께"),
    (57, 60, "FORTY & FOREVER", "태어나줘서 고마워요\n생일 축하해요", "나의 가장 아름다운 사람"),
]

PALETTES = [
    ((9, 7, 14), (64, 16, 43), (246, 196, 110)),
    ((25, 11, 24), (120, 42, 62), (255, 193, 111)),
    ((37, 17, 39), (145, 61, 82), (246, 190, 105)),
    ((25, 23, 55), (103, 53, 92), (225, 151, 106)),
    ((15, 28, 42), (94, 38, 56), (236, 177, 99)),
    ((21, 10, 25), (125, 29, 62), (250, 202, 112)),
    ((12, 35, 45), (34, 92, 98), (255, 207, 118)),
    ((12, 7, 15), (101, 24, 54), (251, 206, 120)),
]

IVORY = (248, 241, 231)
GOLD = (247, 199, 111)
WINE = (115, 27, 59)
INK = (17, 10, 18)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def smoothstep(value: float) -> float:
    value = clamp01(value)
    return value * value * (3 - 2 * value)


def ease_out(value: float) -> float:
    value = clamp01(value)
    return 1 - (1 - value) ** 3


def lerp(a: float, b: float, value: float) -> float:
    return a + (b - a) * value


def rgba(color: tuple[int, int, int], alpha: float | int = 255) -> tuple[int, int, int, int]:
    return (*color, int(clamp01(alpha / 255 if alpha > 1 else alpha) * 255))


@lru_cache(maxsize=None)
def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


@lru_cache(maxsize=None)
def paper_background(scene_index: int) -> Image.Image:
    dark, mid, accent = PALETTES[scene_index]
    y = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None, None]
    x = np.linspace(0, 1, WIDTH, dtype=np.float32)[None, :, None]
    dark_array = np.array(dark, dtype=np.float32)[None, None, :]
    mid_array = np.array(mid, dtype=np.float32)[None, None, :]
    accent_array = np.array(accent, dtype=np.float32)[None, None, :]
    vertical = dark_array * (1 - y * 0.58) + mid_array * (y * 0.58)
    vertical = np.broadcast_to(vertical, (HEIGHT, WIDTH, 3)).copy()
    radial = np.exp(-(((x - 0.66) / 0.48) ** 2 + ((y - 0.40) / 0.55) ** 2) * 2.1)
    base = vertical * (1 - radial * 0.13) + accent_array * (radial * 0.13)
    rng = np.random.default_rng(9301 + scene_index)
    noise = rng.normal(0, 3.3, (HEIGHT, WIDTH, 1))
    grain = np.sin(np.arange(HEIGHT, dtype=np.float32)[:, None, None] * 0.37) * 0.8
    base = np.clip(base + noise + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(base, "RGB").convert("RGBA")


@lru_cache(maxsize=None)
def vignette() -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((-170, -90, WIDTH + 170, HEIGHT + 120), fill=235)
    mask = mask.filter(ImageFilter.GaussianBlur(105))
    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 205))
    shade.putalpha(Image.eval(mask, lambda value: 225 - value))
    return shade


def draw_centered(draw: ImageDraw.ImageDraw, y: int, text: str, text_font, fill, spacing=8) -> None:
    box = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=spacing, align="center")
    width = box[2] - box[0]
    draw.multiline_text(((WIDTH - width) / 2, y), text, font=text_font, fill=fill, spacing=spacing, align="center")


def paper_polygon(draw: ImageDraw.ImageDraw, points, fill, outline=None, width=1) -> None:
    shifted = [(x + 4, y + 6) for x, y in points]
    shadow = (*INK, min(115, fill[3] if len(fill) == 4 else 115))
    draw.polygon(shifted, fill=shadow)
    draw.polygon(points, fill=fill, outline=outline)
    if outline:
        draw.line(points + [points[0]], fill=outline, width=width, joint="curve")


def scene_progress(time_s: float, index: int) -> float:
    start, end, *_ = SCENES[index]
    return clamp01((time_s - start) / (end - start))


def scene_opacity(local: float, scene_index: int) -> float:
    if scene_index == 0:
        return smoothstep(local / 0.15)
    if scene_index == len(SCENES) - 1:
        return smoothstep(local / 0.16)
    return min(smoothstep(local / 0.13), smoothstep((1 - local) / 0.1))


def bezier_path(y_offset=0, amplitude=70, phase=0.0) -> list[tuple[float, float]]:
    points = []
    for index in range(45):
        x = -35 + index * (610 / 44)
        p = index / 44
        y = 720 + y_offset + math.sin(p * math.pi * 1.35 + phase) * amplitude - p * 58
        points.append((x, y))
    return points


def draw_golden_path(layer: Image.Image, local: float, y_offset=0, amplitude=70, phase=0.0, reveal=True) -> None:
    draw = ImageDraw.Draw(layer)
    points = bezier_path(y_offset, amplitude, phase)
    if reveal:
        count = max(2, int(len(points) * ease_out(local)))
        points = points[:count]
    draw.line([(x + 5, y + 10) for x, y in points], fill=(5, 3, 7, 115), width=28, joint="curve")
    draw.line(points, fill=(151, 94, 45, 220), width=20, joint="curve")
    draw.line(points, fill=(248, 198, 105, 245), width=7, joint="curve")
    draw.line([(x, y - 2) for x, y in points], fill=(255, 231, 165, 150), width=2, joint="curve")


def draw_particles(layer: Image.Image, time_s: float, scene_index: int, amount=34) -> None:
    draw = ImageDraw.Draw(layer)
    for index in range(amount):
        seed_x = (index * 137 + scene_index * 73 + 31) % WIDTH
        seed_y = (index * 211 + scene_index * 47 + 61) % HEIGHT
        y = (seed_y - time_s * (3.4 + index % 6)) % (HEIGHT + 70) - 35
        x = seed_x + math.sin(time_s * 0.22 + index * 1.9) * (5 + index % 8)
        pulse = (math.sin(time_s * 1.1 + index * 1.73) + 1) / 2
        alpha = int(35 + pulse * 115)
        radius = 1 + (index % 3) * 0.45
        color = (248, 203, 122, alpha) if index % 4 else (222, 164, 192, alpha)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def draw_hills(layer: Image.Image, time_s: float, scene_index: int, dawn=False) -> None:
    draw = ImageDraw.Draw(layer)
    drift = math.sin(time_s * 0.12) * 7
    colors = [(18, 12, 25, 235), (31, 17, 34, 245), (47, 23, 42, 255)]
    if dawn:
        colors = [(12, 32, 42, 230), (19, 48, 55, 245), (29, 58, 59, 255)]
    for depth, color in enumerate(colors):
        base_y = 570 + depth * 86
        points = [(-40, HEIGHT), (-40, base_y)]
        for i in range(8):
            x = -60 + i * 100 + drift * (depth + 1)
            y = base_y - (i % 2) * (38 + depth * 8) - math.sin(i * 1.8 + scene_index) * 28
            points.append((x, y))
        points += [(WIDTH + 40, HEIGHT)]
        paper_polygon(draw, points, (*color[:3], color[3]), outline=(103, 57, 67, 65))


def draw_sunrise(layer: Image.Image, local: float) -> None:
    draw = ImageDraw.Draw(layer)
    rise = ease_out(local)
    cx, cy = 438, int(575 - rise * 105)
    for radius, alpha in ((150, 16), (105, 25), (68, 42)):
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(255, 208, 122, alpha))
    draw.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(255, 221, 147, 235))
    for angle in range(0, 360, 22):
        rad = math.radians(angle)
        draw.line((cx + math.cos(rad) * 48, cy + math.sin(rad) * 48, cx + math.cos(rad) * 110, cy + math.sin(rad) * 110), fill=(250, 207, 123, 55), width=2)


def draw_tree(layer: Image.Image, x: float, ground_y: float, scale: float, grow=1.0, future=False) -> None:
    draw = ImageDraw.Draw(layer)
    grow = smoothstep(grow)
    trunk_h = 155 * scale * grow
    trunk_w = max(4, int(15 * scale))
    draw.line((x + 4, ground_y + 6, x, ground_y - trunk_h), fill=(7, 5, 9, 125), width=trunk_w + 6)
    draw.line((x, ground_y, x, ground_y - trunk_h), fill=(103, 51, 46, 255), width=trunk_w)
    if grow < 0.2:
        return
    crown_y = ground_y - trunk_h
    leaf_color = (26, 77, 71, 240) if future else (91, 26, 55, 235)
    for index in range(11):
        angle = index * 2.4
        radius = (34 + index % 4 * 7) * scale * grow
        cx = x + math.sin(angle) * 46 * scale * grow
        cy = crown_y + math.cos(angle) * 30 * scale * grow
        draw.ellipse((cx - radius, cy - radius * 0.72, cx + radius, cy + radius * 0.72), fill=leaf_color, outline=(188, 105, 90, 60))


def draw_city(layer: Image.Image, horizon: int, local: float, future=False) -> None:
    draw = ImageDraw.Draw(layer)
    color = (16, 51, 60, 220) if future else (28, 20, 41, 220)
    for index in range(12):
        width = 24 + (index % 4) * 9
        height = 50 + (index * 37 % 145) * ease_out(local)
        x = 15 + index * 47
        draw.rectangle((x, horizon - height, x + width, horizon), fill=color, outline=(118, 74, 76, 75))
        for wy in range(int(horizon - height + 16), horizon - 9, 19):
            if (index + wy) % 3:
                draw.rectangle((x + 7, wy, x + 10, wy + 4), fill=(247, 195, 104, 100))


def draw_person(
    layer: Image.Image,
    x: float,
    ground_y: float,
    height: float,
    phase: float,
    color=(75, 24, 47),
    alpha=255,
    direction=1,
    age="adult",
    future=False,
    still=False,
) -> None:
    draw = ImageDraw.Draw(layer)
    head_r = height * (0.12 if age == "child" else 0.095)
    head_y = ground_y - height + head_r * 1.1
    shoulder_y = head_y + head_r * 1.55
    hip_y = ground_y - height * 0.39
    stride = 0 if still else math.sin(phase) * height * 0.12
    arm_stride = 0 if still else math.sin(phase + math.pi) * height * 0.085
    outline = (244, 181, 98, int(alpha * 0.62))
    body = (*color, alpha)
    shadow = (5, 4, 7, int(alpha * 0.42))

    # Paper shadow makes the character feel physically layered.
    draw.ellipse((x - head_r + 4, head_y - head_r + 6, x + head_r + 4, head_y + head_r + 6), fill=shadow)
    torso_top = shoulder_y
    if age in ("child", "youth"):
        torso_points = [(x - height * 0.11, torso_top), (x + height * 0.1, torso_top), (x + height * 0.13, hip_y), (x - height * 0.12, hip_y)]
    else:
        torso_points = [(x - height * 0.115, torso_top), (x + height * 0.11, torso_top), (x + height * 0.18, hip_y), (x - height * 0.16, hip_y)]
    paper_polygon(draw, torso_points, body, outline=outline)

    leg_width = max(4, int(height * 0.055))
    left_foot = (x - stride, ground_y)
    right_foot = (x + stride, ground_y)
    draw.line((x - height * 0.06 + 4, hip_y + 5, left_foot[0] + 4, left_foot[1] + 5), fill=shadow, width=leg_width + 5)
    draw.line((x + height * 0.06 + 4, hip_y + 5, right_foot[0] + 4, right_foot[1] + 5), fill=shadow, width=leg_width + 5)
    draw.line((x - height * 0.06, hip_y, *left_foot), fill=body, width=leg_width)
    draw.line((x + height * 0.06, hip_y, *right_foot), fill=body, width=leg_width)
    shoe = max(7, int(height * 0.065))
    draw.line((left_foot[0] - shoe * direction, ground_y, left_foot[0] + 2, ground_y), fill=(*INK, alpha), width=max(3, leg_width // 2))
    draw.line((right_foot[0] - shoe * direction, ground_y, right_foot[0] + 2, ground_y), fill=(*INK, alpha), width=max(3, leg_width // 2))

    hand_y = shoulder_y + height * 0.31
    arm_width = max(3, int(height * 0.043))
    draw.line((x - height * 0.08, shoulder_y + 8, x - arm_stride - height * 0.06, hand_y), fill=body, width=arm_width)
    draw.line((x + height * 0.08, shoulder_y + 8, x + arm_stride + height * 0.08, hand_y), fill=body, width=arm_width)
    draw.ellipse((x - head_r, head_y - head_r, x + head_r, head_y + head_r), fill=(198, 130, 105, alpha), outline=outline, width=max(1, int(height / 90)))

    hair = (40, 17, 31, alpha) if not future else (107, 83, 82, alpha)
    draw.pieslice((x - head_r * 1.14, head_y - head_r * 1.15, x + head_r * 1.15, head_y + head_r * 1.15), 176 if direction > 0 else -3, 355 if direction > 0 else 178, fill=hair)
    tail_x = x - direction * head_r * 0.75
    draw.polygon([(tail_x, head_y), (tail_x - direction * head_r * 1.7, head_y + head_r * 1.8), (tail_x + direction * head_r * 0.3, head_y + head_r * 1.45)], fill=hair)
    draw.line((x + direction * head_r * 0.78, head_y + 1, x + direction * head_r * 1.05, head_y + 2), fill=outline, width=1)

    if age == "youth":
        bag_x = x - direction * height * 0.14
        draw.rounded_rectangle((bag_x - height * 0.06, shoulder_y + 12, bag_x + height * 0.06, hip_y - 5), radius=5, fill=(65, 34, 47, alpha), outline=outline)


def draw_cradle(layer: Image.Image, local: float) -> None:
    draw = ImageDraw.Draw(layer)
    sway = math.sin(local * math.pi * 6) * 3
    x, y = 250, 635 + sway
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for radius, alpha in ((170, 18), (115, 30), (72, 45)):
        gdraw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 192, 105, alpha))
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    draw = ImageDraw.Draw(layer)
    draw.arc((x - 135, y + 90, x + 135, y + 200), 5, 175, fill=(233, 167, 89, 230), width=13)
    paper_polygon(draw, [(x - 105, y), (x + 105, y), (x + 83, y + 105), (x - 83, y + 105)], (103, 38, 55, 255), outline=(245, 190, 104, 180), width=2)
    for slat in range(-72, 73, 24):
        draw.line((x + slat, y + 16, x + slat * 0.82, y + 88), fill=(241, 177, 95, 145), width=3)
    # Baby silhouette and one reaching hand.
    draw.ellipse((x - 52, y + 28, x + 46, y + 82), fill=(246, 201, 156, 240))
    draw.ellipse((x - 45, y + 15, x - 4, y + 56), fill=(204, 137, 110, 255), outline=(255, 220, 168, 180))
    reach = smoothstep((local - 0.45) / 0.35)
    draw.line((x - 6, y + 50, x + 18 + reach * 23, y + 34 - reach * 18), fill=(205, 138, 111, 255), width=8)
    draw.ellipse((x + 35 + reach * 8, y + 8 - reach * 10, x + 45 + reach * 8, y + 18 - reach * 10), fill=(249, 204, 156, 255))

    # Mobile above the cradle.
    draw.line((x, y - 150, x, y - 72), fill=(246, 192, 102, 180), width=2)
    draw.arc((x - 70, y - 100, x + 70, y - 30), 188, 352, fill=(246, 192, 102, 210), width=3)
    for idx, dx in enumerate((-48, 0, 48)):
        star_y = y - 44 + (idx % 2) * 12
        draw.line((x + dx, y - 60, x + dx, star_y), fill=(246, 192, 102, 120), width=1)
        draw_regular_star(draw, x + dx, star_y + 11, 7, (250, 203, 113, 225))


def draw_regular_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, fill) -> None:
    points = []
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        r = radius if index % 2 == 0 else radius * 0.42
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(points, fill=fill)


def draw_paper_plane(draw: ImageDraw.ImageDraw, local: float) -> None:
    x = lerp(80, 480, ease_out(local))
    y = 340 + math.sin(local * math.pi * 2.3) * 72
    points = [(x - 25, y + 4), (x + 25, y - 8), (x - 5, y + 18), (x - 4, y + 4)]
    paper_polygon(draw, points, (248, 226, 190, 245), outline=(246, 190, 105, 180))
    tail = []
    for index in range(18):
        px = x - 24 - index * 10
        py = y + 3 + math.sin(index * 0.6 + local * 7) * 5
        tail.append((px, py))
    draw.line(tail, fill=(246, 193, 106, 80), width=2)


def draw_umbrella(layer: Image.Image, x: float, y: float, scale: float, local: float) -> None:
    draw = ImageDraw.Draw(layer)
    open_amount = smoothstep(local / 0.25)
    width = 138 * scale * open_amount
    draw.pieslice((x - width / 2, y - 34 * scale, x + width / 2, y + 47 * scale), 180, 360, fill=(99, 28, 55, 250), outline=(245, 183, 98, 175), width=2)
    draw.line((x, y + 5, x, y + 145 * scale), fill=(237, 178, 97, 220), width=max(2, int(4 * scale)))
    draw.arc((x - 4 * scale, y + 125 * scale, x + 28 * scale, y + 162 * scale), 45, 205, fill=(237, 178, 97, 220), width=max(2, int(4 * scale)))


def draw_rain(layer: Image.Image, time_s: float, opacity: float) -> None:
    draw = ImageDraw.Draw(layer)
    for index in range(52):
        x = (index * 83 + int(time_s * 190)) % (WIDTH + 120) - 60
        y = (index * 149 + int(time_s * 315)) % (HEIGHT + 120) - 60
        draw.line((x, y, x - 12, y + 31), fill=(173, 195, 207, int(90 * opacity)), width=1)


def draw_house(layer: Image.Image, x: float, ground_y: float, scale: float, glow=1.0) -> None:
    draw = ImageDraw.Draw(layer)
    w, h = 180 * scale, 150 * scale
    body = [(x - w / 2, ground_y - h), (x + w / 2, ground_y - h), (x + w / 2, ground_y), (x - w / 2, ground_y)]
    paper_polygon(draw, body, (45, 24, 38, 255), outline=(122, 70, 77, 110))
    roof = [(x - w * 0.62, ground_y - h), (x, ground_y - h - 78 * scale), (x + w * 0.62, ground_y - h)]
    paper_polygon(draw, roof, (76, 25, 47, 255), outline=(190, 103, 86, 100))
    for wx in (-42, 35):
        window = (x + wx * scale - 19 * scale, ground_y - h + 40 * scale, x + wx * scale + 19 * scale, ground_y - h + 82 * scale)
        draw.rectangle(window, fill=(250, 198, 105, int(215 * glow)), outline=(255, 229, 169, 150))
        draw.line(((window[0] + window[2]) / 2, window[1], (window[0] + window[2]) / 2, window[3]), fill=(92, 50, 51, 150), width=2)


def heart_points(count=40, scale=1.0, center=(270, 365)) -> list[tuple[float, float]]:
    points = []
    for index in range(count):
        angle = (index / count) * math.pi * 2
        x = center[0] + scale * 7.8 * 16 * math.sin(angle) ** 3
        y = center[1] - scale * 7.1 * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        points.append((x, y))
    return points


def draw_heart_constellation(layer: Image.Image, local: float, center=(270, 365), scale=1.0, complete=False) -> None:
    draw = ImageDraw.Draw(layer)
    points = heart_points(40, scale, center)
    lit = 40 if complete else min(40, int(ease_out(local) * 42))
    for index in range(max(0, lit - 1)):
        draw.line((points[index], points[index + 1]), fill=(247, 198, 108, 80), width=1)
    if lit == 40:
        draw.line((points[-1], points[0]), fill=(247, 198, 108, 80), width=1)
    for index, (x, y) in enumerate(points):
        if index >= lit:
            draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(104, 71, 75, 80))
            continue
        pulse = 1 + math.sin(index * 1.7 + local * 10) * 0.25
        radius = (2.2 + index % 3 * 0.55) * pulse
        draw.ellipse((x - radius * 2.6, y - radius * 2.6, x + radius * 2.6, y + radius * 2.6), fill=(247, 198, 108, 18))
        draw_regular_star(draw, x, y, radius, (255, 218, 139, 235))


def draw_candle(layer: Image.Image, x: float, base_y: float, scale: float, local: float) -> None:
    draw = ImageDraw.Draw(layer)
    w, h = 58 * scale, 105 * scale
    draw.rounded_rectangle((x - w / 2 + 5, base_y - h + 7, x + w / 2 + 5, base_y + 7), radius=8, fill=(5, 4, 7, 110))
    draw.rounded_rectangle((x - w / 2, base_y - h, x + w / 2, base_y), radius=8, fill=(128, 30, 62, 255), outline=(245, 186, 98, 190), width=2)
    number_font = font(FONT_BOLD, max(12, int(30 * scale)))
    box = draw.textbbox((0, 0), "40", font=number_font)
    draw.text((x - (box[2] - box[0]) / 2, base_y - h * 0.7), "40", font=number_font, fill=(251, 213, 139, 230))
    draw.line((x, base_y - h, x, base_y - h - 14 * scale), fill=(42, 23, 24, 255), width=max(1, int(3 * scale)))
    flame_y = base_y - h - 31 * scale
    sway = math.sin(local * 20) * 3 * scale
    draw.ellipse((x - 20 * scale + sway, flame_y - 29 * scale, x + 20 * scale + sway, flame_y + 27 * scale), fill=(255, 171, 70, 32))
    flame = [(x + sway, flame_y - 22 * scale), (x + 13 * scale + sway, flame_y + 10 * scale), (x + sway, flame_y + 21 * scale), (x - 13 * scale + sway, flame_y + 10 * scale)]
    draw.polygon(flame, fill=(255, 184, 74, 250))
    draw.ellipse((x - 4 * scale + sway, flame_y + 4 * scale, x + 4 * scale + sway, flame_y + 17 * scale), fill=(255, 249, 207, 255))


def draw_caption(layer: Image.Image, scene_index: int, local: float, low=False) -> None:
    _, _, kicker, title, subtitle = SCENES[scene_index]
    opacity = scene_opacity(local, scene_index)
    if opacity <= 0.02:
        return
    draw = ImageDraw.Draw(layer)
    rise = int((1 - ease_out(local / 0.24)) * 19)
    title_size = 39 if scene_index not in (1, 4) else 34
    if scene_index == 7:
        title_size = 42
    title_font = font(FONT_BOLD, title_size)
    kicker_font = font(FONT_REGULAR, 12)
    subtitle_font = font(FONT_REGULAR, 17)
    y = 665 if low else 116
    if scene_index in (0, 7):
        y = 605 if scene_index == 0 else 520
    alpha = int(opacity * 255)
    draw_centered(draw, y + rise, kicker, kicker_font, (247, 198, 110, int(alpha * 0.88)))
    draw_centered(draw, y + 39 + rise, title, title_font, (248, 241, 231, alpha), spacing=11)
    title_box = draw.multiline_textbbox((0, 0), title, font=title_font, spacing=11)
    title_h = title_box[3] - title_box[1]
    draw_centered(draw, y + 62 + title_h + rise, subtitle, subtitle_font, (219, 207, 209, int(alpha * 0.78)))
    line_y = y + 25 + rise
    draw.line((WIDTH / 2 - 23, line_y, WIDTH / 2 + 23, line_y), fill=(247, 198, 110, int(alpha * 0.6)), width=1)


def scene_prologue(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    beat = (math.sin(time_s * math.pi * 2.15) + 1) / 2
    radius = 8 + smoothstep(local) * 12
    cx, cy = WIDTH / 2, 400
    for ring in range(3):
        rr = radius + ring * 24 + beat * 8
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(247, 198, 110, max(0, 70 - ring * 20)), width=1)
    draw_regular_star(draw, cx, cy, radius * (0.7 + beat * 0.25), (255, 215, 136, 245))
    thread = smoothstep((local - 0.28) / 0.55)
    points = []
    for index in range(max(2, int(45 * thread))):
        p = index / 44
        points.append((cx + math.sin(p * 8) * 15, cy + p * 215))
    if len(points) > 1:
        draw.line(points, fill=(247, 198, 110, 190), width=2)
    draw_particles(layer, time_s, 0, 24)
    draw_caption(layer, 0, local)
    frame.alpha_composite(layer)


def scene_birth(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 1)
    draw_golden_path(layer, min(1, local * 1.25), y_offset=26, amplitude=34, phase=0.2)
    draw_cradle(layer, local)
    draw_particles(layer, time_s, 1, 28)
    draw_caption(layer, 1, local)
    frame.alpha_composite(layer)


def scene_childhood(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 2)
    draw_tree(layer, 92, 660, 0.8, 1, future=False)
    draw_tree(layer, 472, 625, 0.55, 1, future=False)
    draw_golden_path(layer, 1, y_offset=15, amplitude=58, phase=-0.25, reveal=False)
    x = lerp(95, 420, smoothstep(local))
    ground = 722 + math.sin(((x + 35) / 610) * math.pi * 1.35 - 0.25) * 58 - ((x + 35) / 610) * 58 + 15
    draw_person(layer, x, ground, 118, time_s * 5.7, color=(109, 35, 65), age="child")
    draw_paper_plane(ImageDraw.Draw(layer), local)
    draw_particles(layer, time_s, 2, 30)
    draw_caption(layer, 2, local)
    frame.alpha_composite(layer)


def scene_youth(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 3)
    draw_city(layer, 640, local * 1.3)
    draw_golden_path(layer, 1, y_offset=30, amplitude=50, phase=0.55, reveal=False)
    draw = ImageDraw.Draw(layer)
    # A fork in the road resolves back into one path.
    if local < 0.55:
        fork_alpha = int((1 - smoothstep(local / 0.55)) * 115)
        draw.arc((190, 615, 560, 870), 185, 294, fill=(244, 186, 98, fork_alpha), width=4)
    x = lerp(95, 438, smoothstep(local))
    p = (x + 35) / 610
    ground = 720 + 30 + math.sin(p * math.pi * 1.35 + 0.55) * 50 - p * 58
    if 0.45 < local < 0.57:
        crouch = math.sin((local - 0.45) / 0.12 * math.pi)
        height = 165 - crouch * 38
        ground += crouch * 5
    else:
        height = 165
    draw_person(layer, x, ground, height, time_s * 6.2, color=(55, 35, 79), age="youth")
    # A book opens into a small flock of dream-stars.
    book_x, book_y = x + 55, ground - 102
    draw.polygon([(book_x - 18, book_y), (book_x, book_y + 6), (book_x, book_y + 28), (book_x - 19, book_y + 19)], fill=(239, 213, 173, 220))
    draw.polygon([(book_x + 18, book_y), (book_x, book_y + 6), (book_x, book_y + 28), (book_x + 19, book_y + 19)], fill=(249, 228, 188, 220))
    for idx in range(7):
        star_x = book_x + math.sin(idx * 2.1 + local * 4) * (20 + idx * 6)
        star_y = book_y - 12 - idx * 18 - smoothstep(local) * 25
        draw_regular_star(draw, star_x, star_y, 3 + idx % 2, (247, 197, 108, 155))
    draw_particles(layer, time_s, 3, 24)
    draw_caption(layer, 3, local)
    frame.alpha_composite(layer)


def scene_adulthood(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 4)
    draw_city(layer, 655, 1)
    draw_house(layer, 425, 676, 0.68, glow=smoothstep((local - 0.55) / 0.25))
    draw_golden_path(layer, 1, y_offset=35, amplitude=36, phase=0.1, reveal=False)
    rain_opacity = smoothstep(local / 0.18) * (1 - smoothstep((local - 0.68) / 0.22))
    draw_rain(layer, time_s, rain_opacity)
    x = lerp(105, 375, smoothstep(local))
    p = (x + 35) / 610
    ground = 720 + 35 + math.sin(p * math.pi * 1.35 + 0.1) * 36 - p * 58
    draw_person(layer, x, ground, 190, time_s * 4.8, color=(79, 29, 53), age="adult")
    companion_x = x + 67
    draw_person(layer, companion_x, ground + 3, 176, time_s * 4.8 + 0.5, color=(35, 42, 58), age="adult", alpha=int(230 * smoothstep((local - 0.25) / 0.2)))
    draw_umbrella(layer, x + 35, ground - 175, 0.85, local)
    draw_particles(layer, time_s, 4, 18)
    draw_caption(layer, 4, local)
    frame.alpha_composite(layer)


def scene_forty(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 5)
    draw_golden_path(layer, 1, y_offset=45, amplitude=25, phase=0, reveal=False)
    ghost_alpha = int(86 * smoothstep(local / 0.3))
    draw_person(layer, 118, 748, 95, 0, color=(113, 48, 70), age="child", alpha=ghost_alpha, still=True)
    draw_person(layer, 190, 744, 143, 0, color=(84, 47, 87), age="youth", alpha=ghost_alpha, still=True)
    draw_person(layer, 270, 735, 212, 0, color=(105, 28, 59), age="adult", still=True)
    draw_person(layer, 356, 742, 170, 0, color=(58, 40, 66), age="adult", alpha=ghost_alpha, still=True)
    draw_heart_constellation(layer, smoothstep((local - 0.08) / 0.7), center=(270, 350), scale=0.72)
    if local > 0.72:
        draw_candle(layer, 270, 805, 0.67, time_s)
    draw_particles(layer, time_s, 5, 42)
    draw_caption(layer, 5, local)
    frame.alpha_composite(layer)


def scene_future(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_sunrise(layer, local)
    draw_hills(layer, time_s, 6, dawn=True)
    draw_tree(layer, 126, 678, 0.9, smoothstep(local / 0.65), future=True)
    draw_golden_path(layer, 1, y_offset=28, amplitude=42, phase=-0.12, reveal=False)
    x = lerp(120, 386, smoothstep(local))
    p = (x + 35) / 610
    ground = 720 + 28 + math.sin(p * math.pi * 1.35 - 0.12) * 42 - p * 58
    future_stage = smoothstep((local - 0.15) / 0.72)
    height = lerp(194, 188, future_stage)
    draw_person(layer, x, ground, height, time_s * 3.5, color=(54, 42, 56), age="adult", future=future_stage > 0.42)
    draw_person(layer, x - 62, ground + 5, height * 0.94, time_s * 3.5 + 0.4, color=(35, 54, 61), age="adult", future=future_stage > 0.42)
    # Their joined hands are the continuation of the golden path.
    hand_y = ground - height * 0.48
    draw = ImageDraw.Draw(layer)
    draw.line((x - 35, hand_y, x - 27, hand_y + 2), fill=(249, 202, 113, 210), width=3)
    draw_particles(layer, time_s, 6, 36)
    draw_caption(layer, 6, local)
    frame.alpha_composite(layer)


def scene_finale(frame: Image.Image, local: float, time_s: float) -> None:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw_hills(layer, time_s, 7)
    draw_golden_path(layer, 1, y_offset=50, amplitude=25, phase=0, reveal=False)
    silhouettes = [
        (90, 94, "child", (107, 38, 66)),
        (157, 129, "youth", (76, 42, 82)),
        (237, 168, "adult", (91, 29, 56)),
        (330, 202, "adult", (112, 29, 59)),
        (430, 188, "adult", (44, 58, 64)),
    ]
    for index, (x, h, age, color) in enumerate(silhouettes):
        opacity = int(215 * smoothstep((local - index * 0.07) / 0.25))
        draw_person(layer, x, 760 - index * 4, h, 0, color=color, age=age, alpha=opacity, future=index == 4, still=True)
    draw_heart_constellation(layer, 1, center=(270, 330), scale=0.63, complete=True)
    draw_candle(layer, 270, 820, 0.62, time_s)
    draw_particles(layer, time_s, 7, 48)
    draw_caption(layer, 7, local)
    frame.alpha_composite(layer)


SCENE_DRAWERS = [scene_prologue, scene_birth, scene_childhood, scene_youth, scene_adulthood, scene_forty, scene_future, scene_finale]


def render_scene(scene_index: int, local: float, time_s: float) -> Image.Image:
    frame = paper_background(scene_index).copy()
    SCENE_DRAWERS[scene_index](frame, local, time_s)
    frame.alpha_composite(vignette())
    return frame.convert("RGB")


def render_frame(time_s: float) -> Image.Image:
    scene_index = next((i for i, scene in enumerate(SCENES) if scene[0] <= time_s < scene[1]), len(SCENES) - 1)
    local = scene_progress(time_s, scene_index)
    current = render_scene(scene_index, local, time_s)
    start = SCENES[scene_index][0]
    if scene_index > 0 and time_s - start < 0.85:
        blend = smoothstep((time_s - start) / 0.85)
        previous = render_scene(scene_index - 1, 1.0, time_s)
        current = Image.blend(previous, current, blend)
    return current


def add_tone(track: np.ndarray, frequency: float, start: float, length: float, amplitude: float, bell=False, warmth=0.2) -> None:
    start_index = int(start * SAMPLE_RATE)
    count = min(int(length * SAMPLE_RATE), len(track) - start_index)
    if count <= 0:
        return
    t = np.arange(count, dtype=np.float64) / SAMPLE_RATE
    if bell:
        envelope = np.exp(-t * 1.25) * np.minimum(1.0, t * 55)
    else:
        attack = np.minimum(1.0, t / 1.6)
        release = np.minimum(1.0, (length - t) / 2.1)
        envelope = np.maximum(0.0, np.minimum(attack, release))
    tone = np.sin(2 * np.pi * frequency * t)
    tone += warmth * np.sin(2 * np.pi * frequency * 2.01 * t)
    if bell:
        tone += 0.18 * np.sin(2 * np.pi * frequency * 3.99 * t)
    track[start_index:start_index + count] += tone * envelope * amplitude


def add_heartbeat(track: np.ndarray, start: float, amplitude=0.22) -> None:
    start_index = int(start * SAMPLE_RATE)
    length = int(0.28 * SAMPLE_RATE)
    if start_index + length > len(track):
        return
    t = np.arange(length) / SAMPLE_RATE
    frequency = 58 - 18 * t
    phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE
    beat = np.sin(phase) * np.exp(-t * 17)
    track[start_index:start_index + length] += beat * amplitude
    second = start_index + int(0.22 * SAMPLE_RATE)
    remain = min(length, len(track) - second)
    track[second:second + remain] += beat[:remain] * amplitude * 0.62


def make_soundtrack(path: Path) -> None:
    total = DURATION * SAMPLE_RATE
    mono = np.zeros(total, dtype=np.float64)
    chords = [
        (130.81, 164.81, 196.00, 246.94),
        (110.00, 146.83, 174.61, 220.00),
        (98.00, 130.81, 164.81, 220.00),
        (87.31, 130.81, 164.81, 196.00),
        (82.41, 123.47, 164.81, 196.00),
        (98.00, 146.83, 196.00, 246.94),
        (110.00, 164.81, 220.00, 293.66),
        (130.81, 164.81, 196.00, 293.66),
    ]
    scene_lengths = [5, 7, 8, 8, 10, 9, 10, 3]
    cursor = 0.0
    for scene_index, duration in enumerate(scene_lengths):
        chord = chords[scene_index]
        for note_index, note in enumerate(chord):
            amplitude = 0.025 + scene_index * 0.002 + (0.012 if note_index == 0 else 0)
            add_tone(mono, note, cursor, duration + 1.2, amplitude, warmth=0.18)
        cursor += duration

    for beat_time in (0.55, 1.45, 2.35, 3.25, 4.15):
        add_heartbeat(mono, beat_time)

    melody = [261.63, 329.63, 392.00, 329.63, 293.66, 392.00, 440.00, 392.00, 329.63, 493.88, 440.00, 392.00, 523.25, 493.88, 440.00, 587.33]
    for index, note in enumerate(melody):
        start = 5.5 + index * 3.05
        amplitude = 0.065 if start < 38 else 0.105
        add_tone(mono, note, start, 3.8, amplitude, bell=True, warmth=0.28)

    # Soft rain texture during adulthood, tucked behind the score.
    rng = np.random.default_rng(1986)
    rain_start, rain_end = int(28 * SAMPLE_RATE), int(37 * SAMPLE_RATE)
    rain = rng.normal(0, 1, rain_end - rain_start)
    rain = np.convolve(rain, np.ones(7) / 7, mode="same")
    rain_env = np.sin(np.linspace(0, math.pi, len(rain))) ** 1.4
    mono[rain_start:rain_end] += rain * rain_env * 0.012

    for note in (523.25, 659.25, 783.99):
        add_tone(mono, note, 39.0 + (note - 523.25) / 170, 7.0, 0.09, bell=True, warmth=0.3)
    for note_index, note in enumerate((392.00, 493.88, 587.33, 783.99)):
        add_tone(mono, note, 52.0 + note_index * 1.15, 7.5, 0.11 + note_index * 0.012, bell=True, warmth=0.32)

    delay_left = int(0.27 * SAMPLE_RATE)
    delay_right = int(0.36 * SAMPLE_RATE)
    left = mono.copy()
    right = mono.copy()
    left[delay_left:] += mono[:-delay_left] * 0.22
    right[delay_right:] += mono[:-delay_right] * 0.25
    fade_in = np.minimum(1.0, np.arange(total) / (SAMPLE_RATE * 1.8))
    fade_out = np.minimum(1.0, np.arange(total)[::-1] / (SAMPLE_RATE * 2.5))
    stereo = np.column_stack((left, right)) * np.minimum(fade_in, fade_out)[:, None]
    stereo /= max(1.0, np.max(np.abs(stereo)) / 0.88)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())


def resolve_ffmpeg() -> Path:
    if len(sys.argv) == 2:
        return Path(sys.argv[1])
    try:
        import imageio_ffmpeg
        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError as exc:
        raise SystemExit("Pass an ffmpeg path or install imageio-ffmpeg") from exc


def generate(ffmpeg: Path) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="birthday-growth-film-") as temp_dir:
        temp_path = Path(temp_dir)
        audio_path = temp_path / "soundtrack.wav"
        video_path = temp_path / "birthday-film.mp4"
        make_soundtrack(audio_path)
        command = [
            str(ffmpeg), "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", str(DURATION),
            str(video_path),
        ]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        assert process.stdin is not None
        poster_saved = False
        for frame_number in range(DURATION * FPS):
            time_s = frame_number / FPS
            frame = render_frame(time_s)
            if not poster_saved and time_s >= 43.0:
                frame.save(POSTER, quality=94, optimize=True)
                poster_saved = True
            process.stdin.write(frame.tobytes())
            if frame_number % (FPS * 5) == 0:
                print(f"rendered {frame_number // FPS:02d}s / {DURATION}s", flush=True)
        process.stdin.close()
        return_code = process.wait()
        if return_code:
            raise SystemExit(return_code)
        os.replace(video_path, OUTPUT)
    print(f"created {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    generate(resolve_ffmpeg())
