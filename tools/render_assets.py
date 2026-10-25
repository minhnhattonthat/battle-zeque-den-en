"""Render each dumped directory entry (tools/dump_assets.py output) as its tilemap drawn with its own tiles.

    python -X utf8 tools/render_assets.py work/gfx        # -> work/gfx/dirNN_{2bpp,4bpp}.png (greyscale)

The map's tile numbers are taken relative to the start of the entry's tile block; bpp is unknown per entry, so
both are drawn. Maps are 32 tiles wide (stride 0x40). Flips honoured; palettes ignored (grey by pixel value).
"""
import sys
from pathlib import Path

from PIL import Image


def tile(chr_, n, bpp):
    size = 8 * bpp
    t = chr_[n * size:(n + 1) * size]
    if len(t) < size:
        return None
    px = []
    for y in range(8):
        row = []
        for x in range(8):
            bit = 7 - x
            v = 0
            for p in range(bpp):
                plane = t[(p // 2) * 16 + 2 * y + (p & 1)]
                v |= (plane >> bit & 1) << p
            row.append(v)
        px.append(row)
    return px


def render(map_, chr_, bpp):
    w, h = 32, len(map_) // 64
    img = Image.new("L", (w * 8, h * 8), 40)
    scale = 255 // ((1 << bpp) - 1)
    for i in range(w * h):
        e = map_[2 * i] | map_[2 * i + 1] << 8
        t = tile(chr_, e & 0x3FF, bpp)
        if t is None:
            continue
        hf, vf = e >> 14 & 1, e >> 15 & 1
        for y in range(8):
            for x in range(8):
                v = t[7 - y if vf else y][7 - x if hf else x]
                img.putpixel(((i % w) * 8 + x, (i // w) * 8 + y), v * scale)
    return img


def main():
    d = Path(sys.argv[1])
    for m in sorted(d.glob("dir*_map.bin")):
        n = m.name[:5]
        c = next(d.glob(f"{n}_*_chr.bin"), None)
        if c is None:
            continue
        for bpp in (2, 4):
            render(m.read_bytes(), c.read_bytes(), bpp).save(d / f"{n}_{bpp}bpp.png")
        print(n)


if __name__ == "__main__":
    sys.exit(main())
