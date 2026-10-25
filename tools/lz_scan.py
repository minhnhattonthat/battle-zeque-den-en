"""Find chains of compressed blocks: blocks sit back to back, so a block's stream end is the next block's start.

    python -X utf8 tools/lz_scan.py [START_HEX ...] [--dump DIR]

With no START, tries every offset whose header looks plausible (size 1..0x10000, stride a small power of two)
and keeps chains of 2+ blocks. A chain stops at the first header that is implausible or fails to decode.
Seed (op 6/7 initial byte) is taken as 0; blocks that use it decode with wrong values but the right length.
"""
import argparse
import sys
from pathlib import Path

from lz import ROM, decompress

STRIDES = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x100, 0x200}


def plausible(rom, o):
    if o + 4 > len(rom):
        return False
    size = rom[o] | rom[o + 1] << 8
    stride = rom[o + 2] | rom[o + 3] << 8
    return 0 < size <= 0x8000 and size % 0x10 == 0 and stride in STRIDES


def chain(rom, o):
    out = []
    while plausible(rom, o):
        try:
            data, end = decompress(rom, o)
        except (IndexError, ValueError):
            break
        if end <= o + 4 or end - o > 0x10000:
            break
        out.append((o, end, data))
        o = end
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("starts", nargs="*")
    ap.add_argument("--dump")
    ap.add_argument("--lo", type=lambda s: int(s, 16), default=0)
    ap.add_argument("--hi", type=lambda s: int(s, 16))
    a = ap.parse_args()
    rom = ROM.read_bytes()
    chains = []
    if a.starts:
        chains = [chain(rom, int(s, 16)) for s in a.starts]
    else:
        o, hi = a.lo, a.hi or len(rom)
        while o < hi:
            c = chain(rom, o) if plausible(rom, o) else []
            if len(c) >= 2:
                chains.append(c)
                o = c[-1][1]
            else:
                o += 1
    for c in chains:
        if not c:
            continue
        print(f"chain {c[0][0]:06X}-{c[-1][1]:06X}: {len(c)} blocks")
        for o, end, data in c:
            print(f"  {o:06X}-{end:06X} -> {len(data):5d} bytes stride {rom[o + 2] | rom[o + 3] << 8:#x}")
            if a.dump:
                Path(a.dump).mkdir(parents=True, exist_ok=True)
                (Path(a.dump) / f"blk_{o:06X}.bin").write_bytes(data)


if __name__ == "__main__":
    sys.exit(main())
