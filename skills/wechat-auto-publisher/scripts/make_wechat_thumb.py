#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a WeChat-safe 2.35:1 thumbnail JPG.")
    parser.add_argument("--cover", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=383)
    args = parser.parse_args()

    image = Image.open(args.cover).convert("RGB")
    image.thumbnail((args.width, args.height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (args.width, args.height), (5, 9, 15))
    canvas.paste(image, ((args.width - image.width) // 2, (args.height - image.height) // 2))

    out = Path(args.out)
    quality = 90
    while True:
        canvas.save(out, "JPEG", quality=quality, optimize=True)
        if out.stat().st_size < 1900 * 1024 or quality <= 60:
            break
        quality -= 5


if __name__ == "__main__":
    main()
