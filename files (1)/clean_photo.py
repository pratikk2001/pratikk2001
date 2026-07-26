"""
Prepares a source photo/illustration for ASCII conversion:
1. Cut the background (rembg) so only the subject remains.
2. Even out lighting with CLAHE so real detail comes out of flat areas.
3. Composite onto a plain white canvas so background reads as "empty"
   at the light end of the character ramp, not the dark end.

Usage: python tools/clean_photo.py <input-image>
Writes: assets/photo-ready.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "assets" / "photo-ready.png"


def remove_background(im: Image.Image) -> Image.Image:
    try:
        from rembg import remove
        return remove(im)
    except Exception as e:
        print(f"rembg unavailable or failed ({e}); using source as-is")
        return im.convert("RGBA")


def even_out_lighting(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGB"))
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    return Image.fromarray(rgb)


def composite_on_white(im: Image.Image) -> Image.Image:
    if im.mode != "RGBA":
        return im.convert("RGB")
    white = Image.new("RGB", im.size, (255, 255, 255))
    white.paste(im, mask=im.split()[3])
    return white


def main():
    src_path = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "assets" / "photo-original.png")
    im = Image.open(src_path)

    cut = remove_background(im)
    lit = even_out_lighting(composite_on_white(cut))
    final = composite_on_white(lit.convert("RGBA"))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    final.save(OUT_PATH)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
