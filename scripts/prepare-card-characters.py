"""Crop four generated 5x2 character sheets into optimized card artwork."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps


GROUPS = {
    "playmobil": [
        "explorer", "bride", "groom", "chef", "doctor",
        "astronaut", "firefighter", "gardener", "musician", "princess",
    ],
    "demon-slayer": [
        "tanjiro", "nezuko", "zenitsu", "inosuke", "rengoku",
        "shinobu", "giyu", "mitsuri", "muichiro", "tengen",
    ],
    "jujutsu-kaisen": [
        "gojo", "yuji", "megumi", "nobara", "yuta",
        "maki", "panda", "inumaki", "nanami", "sukuna",
    ],
    "my-hero-academia": [
        "deku", "bakugo", "todoroki", "uraraka", "all-might",
        "tsuyu", "iida", "kirishima", "aizawa", "hawks",
    ],
}


def crop_sheet(sheet_path: Path, group: str, output_dir: Path) -> None:
    sheet = Image.open(sheet_path).convert("RGB")
    width, height = sheet.size

    for index, character in enumerate(GROUPS[group]):
        row, column = divmod(index, 5)
        left = round(column * width / 5) + 2
        right = round((column + 1) * width / 5) - 2
        top = round(row * height / 2) + 2
        bottom = round((row + 1) * height / 2) - 2
        crop = sheet.crop((left, top, right, bottom))
        crop = ImageOps.fit(
            crop,
            (360, 600),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.46),
        )
        crop.save(
            output_dir / f"{group}-{index + 1:02d}-{character}.webp",
            "WEBP",
            quality=84,
            method=6,
        )


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: prepare-card-characters.py <playmobil> <demon-slayer> "
            "<jujutsu-kaisen> <my-hero-academia>"
        )

    output_dir = Path(__file__).resolve().parents[1] / "public" / "characters"
    output_dir.mkdir(parents=True, exist_ok=True)
    for group, sheet in zip(GROUPS, sys.argv[1:], strict=True):
        crop_sheet(Path(sheet), group, output_dir)

    files = sorted(output_dir.glob("*.webp"))
    print(f"Created {len(files)} character assets in {output_dir}")


if __name__ == "__main__":
    main()
