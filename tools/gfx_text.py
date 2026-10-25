"""gfx_text.py: English lettering for graphics text, drawn with the game's own 8x16 staff-roll font (docs/re/graphics.md).

    python -X utf8 tools/gfx_text.py "Chapter 1" OUT.png      # preview one line (zoom 4, grey by colour index)

The font is asset-directory entry 4: raw 2bpp tiles at file 0x25A5E (the staff roll copies them to VRAM as is),
ASCII 0x20-0x7F as 8x16 cells, top tile of character c at 32*((c-0x20)//16) + c%16, bottom tile 16 later.
Colour 3 = ink, 1 = shadow, 2 = edge.
Lines are drawn proportionally: each glyph trimmed to its inked columns, then GAP blank columns.
"""
import sys
from pathlib import Path

import font as vwf  # font() below is the 8x16 font

ROOT = Path(__file__).resolve().parent.parent
FONT_AT = 0x25A5E
GAP = 1
SPACE = 4


def tile_px(data, at, bpp=2):
    """One SNES planar tile -> 8 rows of 8 colour indices."""
    return [[sum((data[at + 16 * (p // 2) + 2 * y + (p & 1)] >> (7 - x) & 1) << p for p in range(bpp))
             for x in range(8)] for y in range(8)]


def tile_bytes(rows, bpp=2):
    out = bytearray(8 * bpp)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            for p in range(bpp):
                if c >> p & 1:
                    out[16 * (p // 2) + 2 * y + (p & 1)] |= 0x80 >> x
    return bytes(out)


def font(rom):
    """{char: 16 rows of trimmed colour indices} for printable ASCII."""
    out = {}
    for c in range(0x21, 0x7F):
        top = 32 * ((c - 0x20) // 16) + c % 16
        rows = tile_px(rom, FONT_AT + 16 * top) + tile_px(rom, FONT_AT + 16 * (top + 16))
        cols = [x for x in range(8) if any(r[x] for r in rows)]
        out[chr(c)] = [r[cols[0]:cols[-1] + 1] for r in rows] if cols else [[] for _ in rows]
    out[" "] = [[0] * SPACE for _ in range(16)]
    return out


def width(text, f):
    return sum(len(f[ch][0]) + GAP for ch in text) - GAP if text else 0


def line(text, f):
    """16 rows of colour indices, width(text) wide."""
    rows = [[] for _ in range(16)]
    for i, ch in enumerate(text):
        for y in range(16):
            rows[y] += f[ch][y] + ([0] * GAP if i < len(text) - 1 else [])
    return rows


def place(canvas, rows, x, y):
    for dy, r in enumerate(rows):
        canvas[y + dy][x:x + len(r)] = r


def to_tiles(canvas, bpp=2):
    """Canvas (rows of indices, multiple of 8 each way) -> {(tile row, tile col): tile bytes}."""
    out = {}
    for ty in range(len(canvas) // 8):
        for tx in range(len(canvas[0]) // 8):
            out[ty, tx] = tile_bytes([r[8 * tx:8 * tx + 8] for r in canvas[8 * ty:8 * ty + 8]], bpp)
    return out


def canvas(w, h):
    return [[0] * w for _ in range(h)]


def centred(c, text, f, cx, y):
    w = width(text, f)
    if w > len(c[0]):
        raise SystemExit(f"{text!r}: {w} px, room for {len(c[0])}")
    place(c, line(text, f), cx - w // 2, y)


def tilemap(cells, w=32, h=None):
    """{(row, col): tile bytes} -> (map bytes, w wide, plain tile numbers, identical tiles shared, tile 0 blank;
    chr bytes)."""
    h = h or max(r for r, _ in cells) + 1
    tiles, index, mp = [bytes(16)], {bytes(16): 0}, bytearray(2 * w * h)
    for (r, col), t in sorted(cells.items()):
        n = index.setdefault(t, len(tiles))
        if n == len(tiles):
            tiles.append(t)
        mp[2 * (r * w + col):2 * (r * w + col) + 2] = n.to_bytes(2, "little")
    return bytes(mp), b"".join(tiles)


def redraw(mp, chr_, cells, bpp, w=32):
    """Directory-entry map + tiles with the map cells in `cells` ({(row, col): tile bytes}) replaced. Tiles are
    renumbered in map order (identical tiles shared, tile 0 kept first); other cells keep their flip bits. Loaders
    decompress into $7F:0600+ (map) and the tiles after it; entry 13 fills it to $7F:5220 (lzlog.lua), so a
    tile block may grow up to that entry's 16416 bytes."""
    size = 8 * bpp
    old = [chr_[i:i + size] for i in range(0, len(chr_), size)]
    tiles, index, out = [old[0]], {old[0]: 0}, bytearray(mp)
    for k in range(len(mp) // 2):
        e = mp[2 * k] | mp[2 * k + 1] << 8
        t, flags = (cells[divmod(k, w)], 0) if divmod(k, w) in cells else (old[e & 0x3FF], e & 0xFC00)
        n = index.setdefault(t, len(tiles))
        if n == len(tiles):
            tiles.append(t)
        out[2 * k:2 * k + 2] = (n | flags).to_bytes(2, "little")
    assert len(tiles) * size <= 16416, f"{len(tiles)} tiles"
    return bytes(out), b"".join(tiles)


INK4 = {0: 0, 1: 1, 2: 7, 3: 15}  # font colour -> 4bpp sprite colour of the select-screen names (ink 15, edge 7)


def orb_names(rom, gfx, mp, chr_):
    """Directory entry 12 (select-screen sprite sheet, map cell = VRAM sprite tile): each heroine's name is a 64x32
    block at gfx["heroines"][i]["block"] (tile row, column), drawn centred at y 8."""
    f = font(rom)
    cells = {}
    for h in gfx["heroines"]:
        cv = canvas(64, 32)
        centred(cv, h["en"], f, 32, 8)
        cv = [[INK4[c] for c in row] for row in cv]
        r0, c0 = h["block"]
        for (r, col), t in to_tiles(cv, 4).items():
            cells[r0 + r, c0 + col] = t
    return redraw(mp, chr_, cells, 4)


def big_line(text, f):
    """line() at twice the size (each pixel doubled), glyphs 1 px apart: 32 rows."""
    rows = [[] for _ in range(32)]
    for i, ch in enumerate(text):
        for y in range(32):
            rows[y] += [c for c in f[ch][y // 2] for _ in (0, 1)] + ([0] if i < len(text) - 1 else [])
    return rows


INK_NAMES = {0: 0, 1: 0, 2: 13, 3: 15}  # font colour -> prologue name sprites (white 15, grey edge 13, no shadow)


def prologue_names(rom, gfx, mp, chr_):
    """Directory entry 9 (prologue name sprites, map cell = VRAM sprite tile, rows 0-7 x 16) and the sprite lists
    for gfx["prologue_names"]: each name drawn twice size into a box of "size" px at "at" (screen), turned to read
    top to bottom if "rotate". The box is cut into 16x16 sprites, one list entry (x, y, tile, attr) each."""
    f = font(rom)
    cells = {(r, c): bytes(32) for r in range(8) for c in range(16)}
    lists, slot = [], 0
    for h in gfx["prologue_names"]:
        (w, ht), (x0, y0) = h["size"], h["at"]
        rows = big_line(h["en"], f)
        if h.get("rotate"):
            rows = [[rows[len(rows) - 1 - x][y] for x in range(len(rows))] for y in range(len(rows[0]))]
        if len(rows[0]) > w or len(rows) > ht:
            raise SystemExit(f"{h['en']!r}: {len(rows[0])}x{len(rows)} px, box {w}x{ht}")
        cv = canvas(w, ht)
        place(cv, [[INK_NAMES[c] for c in r] for r in rows], (w - len(rows[0])) // 2, (ht - len(rows)) // 2)
        blocks = to_tiles(cv, 4)
        entries = bytearray()
        for by in range(ht // 16):
            for bx in range(w // 16):
                sr, sc = divmod(slot, 8)
                slot += 1
                for dy in (0, 1):
                    for dx in (0, 1):
                        cells[2 * sr + dy, 2 * sc + dx] = blocks[2 * by + dy, 2 * bx + dx]
                entries += bytes([x0 + 16 * bx, y0 + 16 * by, 32 * sr + 2 * sc, 0x30])
        lists.append(bytes(entries))
    return (*redraw(mp, chr_, cells, 4), lists)


PRO_W = 14  # 16x16 cells per row in the prologue drawer's horizontal mode (it pads rows to 14, $82:BED8)
PRO_CELLS = 127  # cells of 4 tiles in VRAM $A010-$BFFF, the BG3 tile area the vertical mode wraps in ($82:D000)
PRO_LISTS = ((0x15281, 0), (0x15315, 0x49), (0x153A7, 0x91))  # SJIS lookup lists: file offset, first glyph slot


def _pro_list(code):
    """Index into PRO_LISTS the drawer searches for an SJIS code ($82:D13F)."""
    big = code[0] << 8 | code[1]
    return 2 if code in (b"\x81\x75", b"\x81\x76", b"\x81\x58") or big >= 0x889F else 1 if big >= 0x8341 else 0


def prologue_slots(rom):
    """[(font slot, SJIS code)] of every glyph the prologue drawer finds by code: the entries of each lookup list
    whose code makes the drawer search that list."""
    out = []
    for i, (o, first) in enumerate(PRO_LISTS):
        while rom[o:o + 2] != b"\0\0":
            if _pro_list(rom[o:o + 2]) == i and all(c != rom[o:o + 2] for _, c in out):  # first match wins
                out.append((first + (o - PRO_LISTS[i][0]) // 2, rom[o:o + 2]))
            o += 2
    return out


def prologue(rom, text, glyphs):
    """English prologue for the horizontal mode of its drawer ($82:D039, docs/re/text.md §Prologue): each line drawn
    with the dialogue VWF font (no shadow), left-aligned in PRO_W 16x16 cells (every cell drawn, blank or not, takes
    4 VRAM tiles from $A010 and this mode never wraps them: PRO_CELLS in all; the build centres the block by
    hscroll). Each distinct inked cell takes a font slot (1bpp, 32 bytes: the left 8 px column top down, then the
    right one) and is written as that slot's SJIS code; blank cells are 8140, trailing ones dropped.
    Returns (script bytes: lines ending 0D, then 00; {slot: glyph bytes}; widest line in px)."""
    rows_of, adv = {ch: rows for ch, rows, _ in glyphs}, vwf.advance_map(glyphs)
    slots, cells, out, w, drawn, widest = prologue_slots(rom), {}, bytearray(), 16 * PRO_W, 0, 0
    for ln in text.split("\n"):
        tw = vwf.text_width(ln, adv)
        if tw > w:
            raise SystemExit(f"prologue {ln!r}: {tw} px, room for {w}")
        px, x, widest = [0] * 16, 0, max(widest, tw)
        for ch in ln:
            for y, r in enumerate(rows_of[ch]):
                px[y + 2] |= r << (w - 16 - x)  # r: 16 bits, MSB = pixel 0
            x += adv[ch]
        line = [bytes(px[y] >> (w - 8 - 16 * j - 8 * h) & 0xFF for h in (0, 1) for y in range(16))
                for j in range(PRO_W)]
        while line and not any(line[-1]):
            line.pop()
        drawn += len(line)
        for g in line:
            if g in cells or not any(g):
                out += cells[g][1] if any(g) else b"\x81\x40"
                continue
            if len(cells) == len(slots):
                raise SystemExit(f"prologue needs more than {len(slots)} glyph cells")
            cells[g] = slots[len(cells)]
            out += cells[g][1]
        out.append(0x0D)
    if drawn > PRO_CELLS:
        raise SystemExit(f"prologue draws {drawn} cells, BG3 holds {PRO_CELLS}")
    return bytes(out) + b"\0", {slot: g for g, (slot, _) in cells.items()}, widest


CARD_STRIP = 15  # tiles per row the card loader copies from the dir-11 map (VRAM tile columns 1-15)


def chapter_card(rom, gfx):
    """Directory entry 11 (map, chr) for the English chapter cards (docs/re/graphics.md §G4, asm/card.asm):
    map rows 0-1 "Chapter" (x 3, 8 tiles), rows 2-3 the digits 1-6 one tile each, rows 4+4c..7+4c chapter c's title
    centred, one line at y 8 or two at y 0/16."""
    f = font(rom)
    cells = {}
    head = canvas(8 * CARD_STRIP, 32)
    place(head, line(gfx["chapter"]["en"], f), 3, 0)
    assert width(gfx["chapter"]["en"], f) + 3 <= 64, "asm/card.asm draws 8 tiles of the header word"
    for d in range(6):
        place(head, line(str(d + 1), f), 8 * d, 16)
    for (r, col), t in to_tiles(head).items():
        cells[r, col] = t
    for c, title in enumerate(gfx["titles"]):
        cv = canvas(8 * CARD_STRIP, 32)
        lines = title["en"].split("\n")
        for n, text in enumerate(lines):
            centred(cv, text, f, len(cv[0]) // 2, 8 if len(lines) == 1 else 16 * n)
        for (r, col), t in to_tiles(cv).items():
            cells[4 + 4 * c + r, col] = t
    return tilemap(cells, h=28)


def main():
    from PIL import Image
    rom = (ROOT / "rom" / "Battle Zeque Den (Japan).sfc").read_bytes()
    f = font(rom)
    rows = line(sys.argv[1], f)
    img = Image.new("L", (len(rows[0]), 16))
    img.putdata([c * 85 for r in rows for c in r])
    img.resize((img.width * 4, 64), Image.NEAREST).save(sys.argv[2])
    print(f"{width(sys.argv[1], f)} px")


if __name__ == "__main__":
    sys.exit(main())
