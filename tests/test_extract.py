"""Phase-4 extract: script/*.json matches the ROM, re-encodes to the original bytes and covers the text ranges."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import extract  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not build.ROM.is_file(), reason="ROM absent")


def strip(entries):
    return [{k: v for k, v in e.items() if k != build.LANG} for e in entries]


@needs_rom
@pytest.mark.parametrize("name", ["dialogue", "prologue"])
def test_json_matches_rom(name):
    """Every field but the translation equals a fresh dump: no stale jp, ids or script uses."""
    rom = build.ROM.read_bytes()
    assert strip(build.load(name)) == strip(getattr(extract, name)(rom))


@needs_rom
def test_dialogue_reencodes_to_the_whole_block():
    rom = build.ROM.read_bytes()
    t = Table.load(build.TBL)
    entries = build.load("dialogue")
    assert len({e["id"] for e in entries}) == len(entries) == 143
    o = build.TEXT_LO
    for e in entries:
        assert int(e["id"], 16) + 0x18000 - 0x8000 == o, e["id"]
        b = t.encode(e["jp"])
        assert b == rom[o:o + len(b)], e["id"]
        o += len(b)
    assert o == build.TEXT_HI  # no gap, no overlap


@needs_rom
def test_prologue_reencodes_to_its_slot():
    rom = build.ROM.read_bytes()
    out = bytearray(rom)
    build.pack_prologue(out, build.load("prologue")[0]["jp"])
    assert out == rom
