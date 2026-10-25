"""build.py: check the dump, unpack every text and graphics-text area, repack it, write build/bzd_en.sfc.

    python -X utf8 tools/build.py

Text comes from script/dialogue.json and script/prologue.json (tools/extract.py), field LANG, else jp.
Areas (docs/re/text.md, graphics.md):
  - dialogue block 0x1AA38-0x1BE33 (font-cell codes, tbl/jp.tbl), strings packed back to back, every script
    pointer ($83:BE33 VM) moved to its string's new address;
  - prologue, Shift-JIS inline in a bank-$82 sequence script at 0x10D0C (no pointer: must fit its slot);
  - G3/G4/G5 tile blocks (asset directory entries 13/11/9), lz codec; an unchanged block keeps its original bytes.
build(orig, identity=True) (tests/test_build.py): jp text, no engine patch -> byte-identical to the original.
The real build: the VWF (asm/vwf.asm, fonts/vwf.txt via tools/font.py, assembled with tools/asar/asar.exe) and
tbl/en.tbl; a dialogue entry with no LANG text gets a marker line "[id] p.l The quick brown fox..." per line of its
jp text (the marker build), so every box shows which string it is.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import bps
import check_rom
import font
import lz
import script_vm
from dump_assets import entries
from tbl import Table

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
OUT = ROOT / "build" / "bzd_en.sfc"
TBL = ROOT / "tbl" / "jp.tbl"
SCRIPT = ROOT / "script"
ASAR = ROOT / "tools" / "asar" / "asar.exe"  # asar 1.91, github.com/RPGHacker/asar/releases (gitignored)
ASM = ROOT / "asm" / "vwf.asm"
LANG = "en"  # text field read from script/*.json; empty -> the jp text
TEXT_LO, TEXT_HI = 0x1AA38, 0x1BE33
TEXT_FREE = (0x1DB7A, 0x20000)  # bank $83 free space, trap-tested (docs/re/rom.md); text must stay in bank $83
PROLOGUE_LO = 0x10D0C
CHECKSUM = 0x7FDC  # LoROM header checksum complement + checksum
GFX = {"G5": 9, "G4": 11, "G3": 13}  # directory entry whose tile block holds Japanese lettering
BUF_PX = {"profile": 128}  # text buffer row width in px (asm/vwf.asm); others 23 tiles
FILLER = "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs. "
# glyph torture line (every printable ASCII + double spaces), shown instead of the marker of entry AA38 (ch1_h0)
TORTURE = {"AA38": "!\"#$%&'()*+,-./0123456789:;<=>?@{n}ABCDEFGHIJKLMNOPQRSTUVWXYZ{n}"
                   "[\\]^_` abcdefghijklmnopq{n}rstuvwxyz{|}~  x  y  z{end}"}


WRITES = []  # (offset, original bytes, new bytes, writer) of the last build(): build/writes.txt for romdiff.py
_ORIG = b""  # the clean original of the current build()


def put(rom, off, data, by):
    """Every write of the build goes through here, so romdiff.py --writes can check it (docs/re/rom.md)."""
    data = bytes(data)
    WRITES.append((off, _ORIG[off:off + len(data)], data, by))
    rom[off:off + len(data)] = data


def load(name):
    """Entries of script/<name>.json (written by tools/extract.py)."""
    return json.loads((SCRIPT / f"{name}.json").read_text(encoding="utf-8"))


def unpack_text(rom, t):
    """{CPU address in bank $83: text} for every string, in block order."""
    out, o = {}, TEXT_LO
    while o < TEXT_HI:
        text, used = t.decode(rom, o)
        out[o - script_vm.BANK] = text
        o += used
    return out


def pack_text(rom, texts, t, regions=((TEXT_LO, TEXT_HI),)):
    """Write the strings back to back, filling each region (file ranges in bank $83) in turn, and point every
    script op at its string's new address. Unused bytes of each region become 00."""
    refs = script_vm.text_pointers(rom)
    bufs = [bytearray() for _ in regions]
    new, ri = {}, 0
    for addr, text in texts.items():
        b = t.encode(text)
        while regions[ri][0] + len(bufs[ri]) + len(b) > regions[ri][1]:
            ri += 1
            if ri == len(regions):
                raise SystemExit(f"text does not fit: {sum(len(t.encode(x)) for x in texts.values())} bytes, "
                                 f"regions hold {sum(hi - lo for lo, hi in regions)}")
        new[addr] = regions[ri][0] + len(bufs[ri]) - script_vm.BANK
        bufs[ri] += b
    for i, ((lo, hi), buf) in enumerate(zip(regions, bufs)):
        if buf or not i:  # the original slot is always rewritten whole; free space only as far as it is used
            put(rom, lo, buf + bytes(hi - lo - len(buf) if not i else 0), f"text region {i}")
    for addr, uses in refs.items():
        for _, at in uses:
            put(rom, script_vm.BANK + at + 1, new[addr].to_bytes(2, "little"), f"text pointer {addr:04X}")


def prologue_end(rom):
    """One past the prologue's 00 terminator (SJIS lead bytes are >= 0x81, so the first 00 is the end)."""
    o = PROLOGUE_LO
    while rom[o]:
        o += 2 if rom[o] >= 0x81 else 1
    return o + 1


def unpack_prologue(rom):
    """Prologue text: SJIS characters, 0D as a newline, other control bytes as [XX]; the 00 end is implied."""
    data, out, o = rom[PROLOGUE_LO:prologue_end(rom) - 1], [], 0
    while o < len(data):
        if data[o] >= 0x81:
            out.append(data[o:o + 2].decode("cp932"))
            o += 2
        else:
            out.append("\n" if data[o] == 0x0D else f"[{data[o]:02X}]")
            o += 1
    return "".join(out)


def pack_prologue(rom, text):
    out = bytearray()
    for hexcode, ch in re.findall(r"\[([0-9A-F]{2})\]|(.)", text, re.S):
        out += bytes([int(hexcode, 16)]) if hexcode else b"\x0d" if ch == "\n" else ch.encode("cp932")
    out.append(0)
    end = prologue_end(rom)
    if len(out) > end - PROLOGUE_LO:
        raise SystemExit(f"prologue {len(out)} bytes, slot holds {end - PROLOGUE_LO}")
    put(rom, PROLOGUE_LO, out + bytes(end - PROLOGUE_LO - len(out)), "prologue")


def gfx_blocks(rom):
    """{name: (file offset, end, stride, decompressed tiles)} for the graphics-text tile blocks."""
    ents = {i: (off, typ) for i, off, typ in entries(rom)}
    out = {}
    for name, i in GFX.items():
        off, typ = ents[i]
        _, start = lz.decompress(rom, off, typ)  # tile block follows the map stream
        tiles, end = lz.decompress(rom, start, typ)
        out[name] = (start, end, rom[start + 2] | rom[start + 3] << 8, tiles)
    return out


def pack_gfx(rom, orig, tiles):
    for name, data in tiles.items():
        start, end, stride, old = orig[name]
        if data == old:
            continue
        blk = lz.compress(data, stride)
        if len(blk) > end - start:
            raise SystemExit(f"{name}: compressed {len(blk)} bytes, slot holds {end - start}")
        put(rom, start, blk, f"{name} tiles")


def marker(e, adv, full):
    """Marker text for an untranslated entry: one line per jp line, "[id] page.line" + filler, keeping the
    jp page/line breaks and effect codes. full: fill each line to the buffer width (box-width measuring),
    else a short filler (all 401 lines at full width would not fit the text space)."""
    width = BUF_PX.get(e["box"], 184)
    pages = []
    for p, page in enumerate(e["jp"].removesuffix("{end}").split("{page}"), 1):
        lines = []
        for n, line in enumerate(page.split("{n}"), 1):
            codes = "".join(re.findall(r"\{c\w+\}|\{wait\}", line))
            s = f"[{e['id']}] {p}.{n} "
            for ch in FILLER if full else FILLER[:20]:
                if font.text_width(s + ch, adv) > width:
                    break
                s += ch
            lines.append(codes + s.rstrip())
        pages.append("{n}".join(lines))
    return "{page}".join(pages) + "{end}"


def full_markers(dialogue):
    """Ids whose markers fill the whole line: the first two entries of each box type."""
    seen, out = {}, set()
    for e in dialogue:
        if seen.setdefault(e["box"], 0) < 2:
            seen[e["box"]] += 1
            out.add(e["id"])
    return out


def assemble(rom, glyphs):
    """Write the font/width binaries, run asar on asm/vwf.asm over the ROM, return the patched bytes."""
    if not ASAR.is_file():
        raise SystemExit(f"{ASAR} missing: unzip asar.exe from github.com/RPGHacker/asar/releases (v1.91)")
    tmp = OUT.parent / "_asar.sfc"
    OUT.parent.mkdir(exist_ok=True)
    (OUT.parent / "vwf_font.bin").write_bytes(font.glyph_bytes(glyphs))
    (OUT.parent / "vwf_widths.bin").write_bytes(font.widths(glyphs))
    tmp.write_bytes(rom)
    r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ASM), str(tmp)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"asar failed:\n{r.stdout}{r.stderr}")
    out = tmp.read_bytes()
    tmp.unlink()
    diff = [i for i in range(len(out)) if out[i] != rom[i]]
    while diff:  # log asar's changes as one write per span (changed runs less than 32 bytes apart)
        j = 1
        while j < len(diff) and diff[j] - diff[j - 1] < 32:
            j += 1
        lo, hi = diff[0], diff[j - 1] + 1
        WRITES.append((lo, _ORIG[lo:hi], out[lo:hi], "asm/vwf.asm"))
        del diff[:j]
    return bytearray(out)


def build(orig, identity=False):
    """identity: jp text and table, no engine patch (must equal the original). Else the English build.
    Fills WRITES with every write made."""
    global _ORIG
    _ORIG = bytes(orig)
    WRITES.clear()
    rom = bytearray(orig)
    dialogue = load("dialogue")
    prologue = load("prologue")[0]
    gfx = gfx_blocks(orig)
    tiles = {name: g[3] for name, g in gfx.items()}
    # phase 7: tiles come from the edited graphics instead of the ROM
    if identity:
        pack_text(rom, {int(e["id"], 16): e["jp"] for e in dialogue}, Table.load(TBL))
        pack_prologue(rom, prologue["jp"])
    else:
        glyphs = font.load()
        adv = font.advance_map(glyphs)
        full = full_markers(dialogue)
        texts = {int(e["id"], 16): e[LANG] or TORTURE.get(e["id"]) or marker(e, adv, e["id"] in full)
                 for e in dialogue}
        pack_text(rom, texts, Table.load(font.EN_TBL), ((TEXT_LO, TEXT_HI), TEXT_FREE))
        pack_prologue(rom, prologue["jp"])  # phase 7: the English prologue needs its own renderer (text.md)
        rom = assemble(rom, glyphs)
    pack_gfx(rom, gfx, tiles)
    put(rom, CHECKSUM, bps.snes_checksum(rom)[0][CHECKSUM:CHECKSUM + 4], "header checksum")
    return bytes(rom)


def main():
    check_rom.check()
    orig = ROM.read_bytes()
    out = build(orig)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    (OUT.parent / "writes.txt").write_text("".join(f"{o:X} {a.hex()} {b.hex()} {by}\n" for o, a, b, by in WRITES),
                                           encoding="utf-8", newline="\n")
    diff = sum(a != b for a, b in zip(orig, out))
    print(f"{OUT.relative_to(ROOT)}: {len(out)} bytes, {diff} bytes differ from the original")


if __name__ == "__main__":
    sys.exit(main())
