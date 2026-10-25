"""Phase-2 debug tool: the event-script addresses in tools/debug/scenes.lua point where docs/re/debug.md says."""
import re
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"
SCENES = (ROOT / "tools" / "debug" / "scenes.lua").read_text(encoding="utf-8")
needs_rom = pytest.mark.skipif(not ROM.is_file(), reason="ROM absent")


def off(a):
    return ((a & 0x7F0000) >> 1) | (a & 0x7FFF)


def test_scene_list_parses():
    assert re.search(r"^return S$", SCENES, re.M)
    assert len(re.findall(r"jump = 0x96[0-9A-F]{4}", SCENES)) >= 6


@needs_rom
def test_area_table_and_jumps():
    rom = ROM.read_bytes()
    w = lambda a: struct.unpack_from("<H", rom, off(a))[0]  # noqa: E731
    starts = {w(0x960000 | w(0x96A5DE + 2 * c) + 2 * a) for c in range(6) for a in range(3)}
    assert 0xA5F6 in starts and 0xC2AE in starts  # chapter 1 area 0, chapter 6 area 1
    # plain jumps land on "03 01" (cutscene on) followed, within 8 bytes, by an op 05 dialogue call
    for line in SCENES.splitlines():
        m = re.search(r"jump = (0x96[0-9A-F]{4})", line)
        if not m or "arena" in line:
            continue
        a = int(m.group(1), 16)
        b = rom[off(a):off(a) + 10]
        assert b[:2] == b"\x03\x01" and 0x05 in b[2:], f"{a:06X}: {b.hex(' ')}"
    # boss arenas: {scene, chapter, area, jump, rect x}: a "08" rect op with that x1 within 40 bytes, then
    # "05 <scene>" later in the same script
    bosses = re.findall(r"\{ (\d+), (\d), (\d), (0x96[0-9A-F]{4}), (\d+) \}", SCENES)
    assert len(bosses) == 6
    for scene, _, _, jump, x in bosses:
        o = off(int(jump, 16))
        seg = rom[o:o + 40]
        assert b"\x08" + struct.pack("<H", int(x)) in seg, jump
        assert bytes([5, int(scene), 6]) in rom[o:o + 120], jump
