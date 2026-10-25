"""Static graphics sweep: render every 32 KB bank of the ROM as raw tiles (one PNG per bank) for reviewers.

    python -X utf8 tools/sweep_sheets.py OUTDIR [--bpp 4] [--skip LO-HI ...]

Each PNG is 32x32 tiles (one bank), zoom 2, labelled by file offset of its first tile in the name. Ranges given
with --skip (file offsets, hex, e.g. 1AA38-1BE33 for text) are drawn grey and listed, never dropped silently.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

from lz import ROM
from render_assets import tile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bpp", type=int, default=4)
    ap.add_argument("--skip", nargs="*", default=[])
    a = ap.parse_args()
    rom = ROM.read_bytes()
    skips = [tuple(int(x, 16) for x in s.split("-")) for s in a.skip]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tb = 8 * a.bpp
    scale = 255 // ((1 << a.bpp) - 1)
    for bank in range(len(rom) // 0x8000):
        base = bank * 0x8000
        img = Image.new("L", (256, 8 * (0x8000 // tb // 32)), 0)
        skipped = 0
        for n in range(0x8000 // tb):
            o = base + n * tb
            x0, y0 = (n % 32) * 8, (n // 32) * 8
            if any(lo <= o < hi for lo, hi in skips):
                img.paste(90, (x0, y0, x0 + 8, y0 + 8))
                skipped += 1
                continue
            px = tile(rom[o:o + tb], 0, a.bpp)
            for y in range(8):
                for x in range(8):
                    img.putpixel((x0 + x, y0 + y), px[y][x] * scale)
        img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
        name = f"bank{bank:02X}_{base:06X}_{a.bpp}bpp.png"
        img.save(out / name)
        print(name, f"skipped {skipped} tiles" if skipped else "")


if __name__ == "__main__":
    sys.exit(main())
