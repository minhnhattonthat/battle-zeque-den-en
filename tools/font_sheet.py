"""Render the 16x11 1bpp dialogue font ($84:808C, 22 bytes/glyph) as a labelled sheet.

    python -X utf8 tools/font_sheet.py OUT.png [--zoom 3] [--from 0 --to 388]

Row label = glyph index of the row's first cell (hex); column = low nibble. Code for index i:
i < 0x70 -> byte i+0x10; else the two bytes 0x80|(i>>8), i&0xFF.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
FONT_OFF, GLYPH_BYTES, GLYPHS, W, H = 0x2008C, 22, 388, 16, 11


def glyph(rom, i):
    """Rows of the glyph as 16-bit ints (bit 15 = leftmost pixel)."""
    o = FONT_OFF + i * GLYPH_BYTES
    return [rom[o + 2 * r] << 8 | rom[o + 2 * r + 1] for r in range(H)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--from", dest="lo", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--to", dest="hi", type=lambda s: int(s, 0), default=GLYPHS)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    first = a.lo & ~15
    rows = (a.hi - first + 15) // 16
    cw, ch, lw, th = W + 4, H + 4, 28, 10
    img = Image.new("RGB", (lw + 16 * cw, th + rows * ch), "white")
    d = ImageDraw.Draw(img)
    for c in range(16):
        d.text((lw + c * cw + 4, 0), "%X" % c, fill="red")
    for r in range(rows):
        d.text((0, th + r * ch + 2), "%03X" % (first + r * 16), fill="blue")
        for c in range(16):
            i = first + r * 16 + c
            if not a.lo <= i < a.hi:
                continue
            x0, y0 = lw + c * cw + 2, th + r * ch + 2
            d.rectangle((x0 - 1, y0 - 1, x0 + W, y0 + H), fill=(230, 230, 255))
            for y, bits in enumerate(glyph(rom, i)):
                for x in range(W):
                    if bits >> (15 - x) & 1:
                        img.putpixel((x0 + x, y0 + y), (0, 0, 0))
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    img.save(a.out)
    print(a.out, img.size)


if __name__ == "__main__":
    sys.exit(main())
