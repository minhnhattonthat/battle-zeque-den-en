"""Print every dialogue string (address + decoded text) from the bank-$83 block, for reading and review.

    python -X utf8 tools/dump_text.py > work/strings.txt
"""
import sys
from pathlib import Path

from tbl import Table

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
TEXT_LO, TEXT_HI = 0x1AA38, 0x1BE33


def strings(rom, t):
    o = TEXT_LO
    while o < TEXT_HI:
        text, used = t.decode(rom, o)
        yield o, text
        o += used


if __name__ == "__main__":
    t = Table.load(ROOT / "tbl" / "jp.tbl")
    for o, text in strings(ROM.read_bytes(), t):
        print(f"$83:{(o & 0x7FFF) | 0x8000:04X} {text}")
