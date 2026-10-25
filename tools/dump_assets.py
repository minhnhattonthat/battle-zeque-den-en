"""Decompress every entry of the asset directory at $84:8000 into a folder (docs/re/compression.md).

    python -X utf8 tools/dump_assets.py OUTDIR

Directory: 35 entries of (u24 CPU address, u8 type). Type 01 = raw data (fonts); others are compressed, and
the type byte is the decompressor's initial "last byte" (it sits in $43 when the loader passes the address).
"""
import sys
from pathlib import Path

from lz import ROM, decompress

DIR_OFF, DIR_ENTRIES = 0x20000, 35


def lorom(a):
    return (a & 0x7F0000) >> 1 | a & 0x7FFF


def entries(rom):
    for i in range(DIR_ENTRIES):
        o = DIR_OFF + 4 * i
        yield i, lorom(rom[o] | rom[o + 1] << 8 | rom[o + 2] << 16), rom[o + 3]


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    rom = ROM.read_bytes()
    for i, off, t in entries(rom):
        if t == 1:
            print(f"{i:2d} {off:06X} raw")
            continue
        data, end = decompress(rom, off, t)
        (out / f"dir{i:02d}_{off:06X}_map.bin").write_bytes(data)
        tiles, tend = decompress(rom, end, t) if data else (b"", end)  # tile block follows the map stream
        if tiles:
            (out / f"dir{i:02d}_{end:06X}_chr.bin").write_bytes(tiles)
        print(f"{i:2d} {off:06X} type {t:02X} map {len(data)} bytes, chr at {end:06X} {len(tiles)} bytes"
              f" (ends {tend:06X})")


if __name__ == "__main__":
    sys.exit(main())
