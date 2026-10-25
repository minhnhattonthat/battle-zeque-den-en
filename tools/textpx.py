"""textpx.py: x extent of the text pixels in a shot, per text row, to measure box widths from pixels.

    python -X utf8 tools/textpx.py SHOT.png Y0 [ROWS] [--pitch 16] [--min 200]

For each band Y0 + k*pitch .. +pitch: first and last x whose pixel has every RGB channel >= --min (the glyph
colour; the shadow and box are darker). Width = last - first + 1.
"""
import argparse

from PIL import Image


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("shot")
    ap.add_argument("y0", type=int)
    ap.add_argument("rows", type=int, nargs="?", default=3)
    ap.add_argument("--pitch", type=int, default=16)
    ap.add_argument("--min", type=int, default=200)
    ap.add_argument("--x", default="0,256", help="x range to search, X0,X1 (skip the box border and portrait)")
    a = ap.parse_args()
    im = Image.open(a.shot).convert("RGB")
    px = im.load()
    x0, x1 = map(int, a.x.split(","))
    for k in range(a.rows):
        y0 = a.y0 + k * a.pitch
        xs = [x for x in range(x0, min(x1, im.width)) if any(min(px[x, y]) >= a.min for y in range(y0, min(y0 + a.pitch, im.height)))]
        print(f"row {k} y{y0}: " + (f"x {xs[0]}..{xs[-1]} width {xs[-1] - xs[0] + 1}" if xs else "empty"))


if __name__ == "__main__":
    main()
