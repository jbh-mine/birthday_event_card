"""Crop a generated 3x2 cat sheet into optimized decorative web photos."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps


NAMES = [
    "orange-tabby", "tuxedo", "ragdoll",
    "british-shorthair", "calico", "black-kitten",
]


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: prepare-cat-moments.py <cat-sheet>")

    sheet = Image.open(sys.argv[1]).convert("RGB")
    width, height = sheet.size
    output_dir = Path(__file__).resolve().parents[1] / "public" / "cats"
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, name in enumerate(NAMES):
        row, column = divmod(index, 3)
        left = round(column * width / 3) + 2
        right = round((column + 1) * width / 3) - 2
        top = round(row * height / 2) + 2
        bottom = round((row + 1) * height / 2) - 2
        photo = sheet.crop((left, top, right, bottom))
        photo = ImageOps.fit(
            photo,
            (640, 640),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.46),
        )
        photo.save(
            output_dir / f"cat-{index + 1:02d}-{name}.webp",
            "WEBP",
            quality=84,
            method=6,
        )

    print(f"Created {len(NAMES)} cat photos in {output_dir}")


if __name__ == "__main__":
    main()
