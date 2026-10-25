"""build.py: check the dump, unpack every text and graphics-text area, repack it, write build/bzd_en.sfc.

    python -X utf8 tools/build.py

Areas (docs/re/text.md, graphics.md):
  - dialogue block 0x1AA38-0x1BE33 (font-cell codes, tbl/jp.tbl), strings packed back to back, every script
    pointer ($83:BE33 VM) moved to its string's new address;
  - prologue, Shift-JIS inline in a bank-$82 sequence script at 0x10D0C (no pointer: must fit its slot);
  - G3/G4/G5 tile blocks (asset directory entries 13/11/9), lz codec; an unchanged block keeps its original bytes.
With no edits the output is byte-identical to the original (tests/test_build.py, the identity build).
"""
import re
import sys
from pathlib import Path

import bps
import check_rom
import lz
import script_vm
from dump_assets import entries
from tbl import Table

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
OUT = ROOT / "build" / "bzd_en.sfc"
TBL = ROOT / "tbl" / "jp.tbl"
TEXT_LO, TEXT_HI = 0x1AA38, 0x1BE33
PROLOGUE_LO = 0x10D0C
GFX = {"G5": 9, "G4": 11, "G3": 13}  # directory entry whose tile block holds Japanese lettering


def unpack_text(rom, t):
    """{CPU address in bank $83: text} for every string, in block order."""
    out, o = {}, TEXT_LO
    while o < TEXT_HI:
        text, used = t.decode(rom, o)
        out[o - script_vm.BANK] = text
        o += used
    return out


def pack_text(rom, texts, t):
    """Write the strings back to back from TEXT_LO and point every script op at its string's new address."""
    refs = script_vm.text_pointers(rom)
    block, new = bytearray(), {}
    for addr, text in texts.items():
        new[addr] = TEXT_LO + len(block) - script_vm.BANK
        block += t.encode(text)
    if len(block) > TEXT_HI - TEXT_LO:
        raise SystemExit(f"text block {len(block)} bytes, slot holds {TEXT_HI - TEXT_LO}")
    rom[TEXT_LO:TEXT_LO + len(block)] = block
    rom[TEXT_LO + len(block):TEXT_HI] = bytes(TEXT_HI - TEXT_LO - len(block))
    for addr, uses in refs.items():
        for _, at in uses:
            rom[script_vm.BANK + at + 1:script_vm.BANK + at + 3] = new[addr].to_bytes(2, "little")


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
    rom[PROLOGUE_LO:end] = out + bytes(end - PROLOGUE_LO - len(out))


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
        rom[start:start + len(blk)] = blk


def build(orig):
    t = Table.load(TBL)
    rom = bytearray(orig)
    texts, prologue = unpack_text(orig, t), unpack_prologue(orig)
    gfx = gfx_blocks(orig)
    tiles = {name: g[3] for name, g in gfx.items()}
    # phase 4+: texts / prologue / tiles come from script/ and the edited graphics instead of the ROM
    pack_text(rom, texts, t)
    pack_prologue(rom, prologue)
    pack_gfx(rom, gfx, tiles)
    return bps.snes_checksum(rom)[0]


def main():
    check_rom.check()
    orig = ROM.read_bytes()
    out = build(orig)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out)
    diff = sum(a != b for a, b in zip(orig, out))
    print(f"{OUT.relative_to(ROOT)}: {len(out)} bytes, {diff} bytes differ from the original")


if __name__ == "__main__":
    sys.exit(main())
