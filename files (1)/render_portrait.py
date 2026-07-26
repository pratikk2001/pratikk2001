"""
Maps the cleaned portrait to a character grid, one glyph per cell based
on brightness, and animates each row drawing in left-to-right, staggered
top-to-bottom. Single accent color only -- multi-color ASCII reads as
noise, not a portrait.

Reads:  assets/photo-ready.png
Writes: portrait.svg
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = ROOT / "assets" / "photo-ready.png"
OUT_PATH = ROOT / "portrait.svg"

GLYPHS = " '.,:;~+*xXO#"   # light/empty -> dense/dark
COLS = 90
CHAR_W = 6.2
CHAR_H = 11
ACCENT = "#5fc4ff"
ROW_STAGGER_MS = 40
ROW_DRAW_MS = 260


def to_char_grid(im: Image.Image):
    im = im.convert("L")
    w, h = im.size
    # characters are taller than wide, so compress rows to keep proportions
    rows = max(1, round(COLS * (h / w) * (CHAR_W / CHAR_H) * 0.55))
    small = im.resize((COLS, rows), Image.LANCZOS)
    arr = np.array(small).astype(float)

    # normalize contrast so the full glyph ramp gets used
    lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
    arr = np.clip((arr - lo) / max(hi - lo, 1e-6), 0, 1)

    n = len(GLYPHS) - 1
    idx = ((1 - arr) * n).round().astype(int)  # dark pixel -> dense glyph
    grid = [[GLYPHS[i] for i in row] for row in idx]
    return grid


def escape(ch: str) -> str:
    return {"<": "&lt;", ">": "&gt;", "&": "&amp;"}.get(ch, ch)


def render():
    im = Image.open(SRC_PATH)
    grid = to_char_grid(im)
    rows = len(grid)
    cols = len(grid[0])

    width = cols * CHAR_W + 20
    height = rows * CHAR_H + 20

    lines = []
    for r, row in enumerate(grid):
        text = "".join(escape(c) for c in row)
        y = 14 + r * CHAR_H
        delay = r * ROW_STAGGER_MS
        row_width = cols * CHAR_W
        lines.append(f'''
    <g>
      <clipPath id="clip{r}">
        <rect x="10" y="{y - CHAR_H}" width="0" height="{CHAR_H + 2}">
          <animate attributeName="width" from="0" to="{row_width}"
            begin="{delay}ms" dur="{ROW_DRAW_MS}ms" fill="freeze" />
        </rect>
      </clipPath>
      <text x="10" y="{y}" class="glyph" clip-path="url(#clip{r})" xml:space="preserve">{text}</text>
    </g>''')

    svg = f'''<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace">
  <style>
    .glyph {{ font-size: {CHAR_H - 1}px; fill: {ACCENT}; letter-spacing: 0.5px; }}
  </style>
  <rect width="100%" height="100%" fill="transparent" />
  {"".join(lines)}
</svg>'''

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH} ({cols}x{rows} grid)")


if __name__ == "__main__":
    render()
